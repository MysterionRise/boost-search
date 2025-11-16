"""FastAPI application for Modern RAG system."""

import os
import sys
from typing import Any

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (
    DocumentProcessor,
    EmbeddingManager,
    HybridSearcher,
    QdrantVectorStore,
    RAGPipeline,
    settings,
)

# Initialize FastAPI app
app = FastAPI(
    title="Modern RAG API",
    description="Advanced RAG system with hybrid search and reranking",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
rag_pipeline: RAGPipeline | None = None
vector_store: QdrantVectorStore | None = None
doc_processor: DocumentProcessor | None = None


# Request/Response models
class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask")
    search_type: str | None = Field("hybrid", description="Search type: vector, bm25, or hybrid")
    top_k: int | None = Field(3, description="Number of results")
    rerank: bool | None = Field(True, description="Apply reranking")
    return_sources: bool | None = Field(True, description="Include source documents")


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict[str, Any]] | None = None
    num_sources: int | None = None


class IndexRequest(BaseModel):
    texts: list[str] = Field(..., description="Texts to index")
    metadatas: list[dict[str, Any]] | None = Field(None, description="Metadata for each text")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    search_type: str | None = Field("hybrid", description="Search type")
    top_k: int | None = Field(5, description="Number of results")


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup."""
    global rag_pipeline, vector_store, doc_processor

    print("Initializing Modern RAG system...")

    # Initialize components
    embedding_manager = EmbeddingManager()
    vector_store = QdrantVectorStore(
        collection_name=settings.qdrant_collection_name,
        embedding_manager=embedding_manager,
    )
    doc_processor = DocumentProcessor()

    # Initialize with empty documents (will be populated via API)
    hybrid_searcher = HybridSearcher(
        vector_store=vector_store,
        documents=[],
    )

    rag_pipeline = RAGPipeline(
        vector_store=vector_store,
        hybrid_searcher=hybrid_searcher,
    )

    print("Modern RAG system initialized successfully!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Modern RAG API",
        "version": "1.0.0",
        "endpoints": [
            "/query - Ask questions",
            "/search - Search documents",
            "/index - Index new documents",
            "/upload - Upload files",
            "/health - Health check",
            "/stats - Get statistics",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    return {
        "status": "healthy",
        "qdrant_connected": True,
        "collection_info": vector_store.get_collection_info(),
    }


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="System not initialized")

    info = vector_store.get_collection_info()
    return {
        "collection_name": info["name"],
        "total_documents": info["points_count"],
        "settings": {
            "embedding_model": settings.embedding_model,
            "llm_provider": settings.llm_provider,
            "llm_model": settings.llm_model,
            "search_type": settings.search_type,
            "rerank_enabled": settings.rerank_enabled,
        },
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system."""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        result = rag_pipeline.query(
            question=request.question,
            search_type=request.search_type,
            top_k=request.top_k,
            rerank=request.rerank,
            return_sources=request.return_sources,
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/search")
async def search(request: SearchRequest):
    """Search for relevant documents."""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        results = rag_pipeline.search_with_reranking.search(
            query=request.query,
            search_type=request.search_type,
            top_k_final=request.top_k,
        )

        return {
            "query": request.query,
            "results": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                }
                for doc, score in results
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/index")
async def index_documents(request: IndexRequest):
    """Index new documents."""
    if vector_store is None or doc_processor is None:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        from langchain_core.documents import Document

        # Create documents
        documents = []
        for i, text in enumerate(request.texts):
            metadata = request.metadatas[i] if request.metadatas else {}
            documents.append(Document(page_content=text, metadata=metadata))

        # Chunk and add to vector store
        chunks = doc_processor.chunk_documents(documents)
        ids = vector_store.add_documents(chunks)

        # Update hybrid searcher
        current_docs = rag_pipeline.hybrid_searcher.documents
        rag_pipeline.hybrid_searcher.update_documents(current_docs + chunks)

        return {
            "message": "Documents indexed successfully",
            "num_documents": len(request.texts),
            "num_chunks": len(chunks),
            "document_ids": ids[:5],  # Return first 5 IDs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and index a document file."""
    if doc_processor is None or vector_store is None:
        raise HTTPException(status_code=503, detail="System not initialized")

    # Save uploaded file temporarily
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Process file
        chunks = doc_processor.process_files(file_paths=[tmp_path])

        # Add to vector store
        vector_store.add_documents(chunks)

        # Update hybrid searcher
        current_docs = rag_pipeline.hybrid_searcher.documents
        rag_pipeline.hybrid_searcher.update_documents(current_docs + chunks)

        # Clean up
        os.unlink(tmp_path)

        return {
            "message": "File uploaded and indexed successfully",
            "filename": file.filename,
            "num_chunks": len(chunks),
        }
    except Exception as e:
        # Clean up on error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
