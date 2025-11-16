"""Basic usage example for Modern RAG system."""

import os
import sys

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


def main():
    """Run basic RAG example."""
    print("=== Modern RAG System - Basic Usage ===\n")

    # Step 1: Initialize components
    print("1. Initializing components...")
    embedding_manager = EmbeddingManager()
    vector_store = QdrantVectorStore(
        collection_name="demo_collection",
        embedding_manager=embedding_manager,
    )

    # Step 2: Process and load documents
    print("\n2. Processing documents...")
    doc_processor = DocumentProcessor()

    # Create sample documents (in practice, load from files)
    from langchain_core.documents import Document

    sample_docs = [
        Document(
            page_content="Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            metadata={"source": "python_intro.txt", "topic": "programming"},
        ),
        Document(
            page_content="Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn.",
            metadata={"source": "ml_intro.txt", "topic": "AI"},
        ),
        Document(
            page_content="Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They use algorithms like HNSW or IVF to perform approximate nearest neighbor search.",
            metadata={"source": "vector_db.txt", "topic": "databases"},
        ),
        Document(
            page_content="RAG (Retrieval-Augmented Generation) combines information retrieval with text generation. It retrieves relevant documents and uses them as context for generating accurate, grounded responses.",
            metadata={"source": "rag_overview.txt", "topic": "AI"},
        ),
    ]

    # Chunk documents
    chunks = doc_processor.chunk_documents(sample_docs)
    print(f"Created {len(chunks)} chunks")

    # Step 3: Add documents to vector store
    print("\n3. Indexing documents...")
    vector_store.add_documents(chunks)
    info = vector_store.get_collection_info()
    print(f"Collection info: {info}")

    # Step 4: Initialize hybrid search
    print("\n4. Initializing hybrid search...")
    hybrid_searcher = HybridSearcher(
        vector_store=vector_store,
        documents=chunks,
    )

    # Step 5: Create RAG pipeline
    print("\n5. Creating RAG pipeline...")
    rag_pipeline = RAGPipeline(
        vector_store=vector_store,
        hybrid_searcher=hybrid_searcher,
    )

    # Step 6: Ask questions
    print("\n6. Querying the system...\n")

    questions = [
        "What is Python?",
        "How does RAG work?",
        "What are vector databases used for?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        print("-" * 80)

        result = rag_pipeline.query(
            question=question,
            search_type="hybrid",
            rerank=True,
            return_sources=True,
        )

        print(f"Answer: {result['answer']}\n")
        print(f"Sources ({result['num_sources']}):")
        for i, source in enumerate(result["sources"], 1):
            print(
                f"  [{i}] {source['metadata']['source']} (score: {source['relevance_score']:.3f})"
            )
        print()

    # Step 7: Cleanup (optional)
    print("\n7. Cleanup...")
    # Uncomment to delete collection
    # vector_store.delete_collection()

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Make sure to set OPENAI_API_KEY in environment or .env file
    if not settings.openai_api_key and settings.llm_provider == "openai":
        print("Warning: OPENAI_API_KEY not set. Please set it in .env file or environment.")
        print("Alternatively, use Ollama by setting LLM_PROVIDER=ollama")
        sys.exit(1)

    main()
