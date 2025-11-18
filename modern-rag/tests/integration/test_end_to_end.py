"""End-to-end integration tests."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from langchain_core.documents import Document


@pytest.mark.integration
@pytest.mark.slow
def test_full_rag_pipeline():
    """Test complete RAG pipeline end-to-end."""
    from src import (
        DocumentProcessor,
        EmbeddingManager,
        HybridSearcher,
        QdrantVectorStore,
        RAGPipeline,
    )

    # Mock external dependencies
    with patch("src.vector_store.QdrantClient") as mock_qdrant:
        with patch("src.embeddings.SentenceTransformer") as mock_st:
            with patch("src.rag_pipeline.ChatOpenAI") as mock_llm:
                # Setup mocks
                mock_client = MagicMock()
                mock_client.get_collections.return_value.collections = []
                mock_qdrant.return_value = mock_client

                mock_model = MagicMock()
                # Return numpy array (what sentence-transformers actually returns)
                mock_model.encode.return_value = np.array([[0.1] * 384])
                mock_model.get_sentence_embedding_dimension.return_value = 384
                mock_st.return_value = mock_model

                mock_llm_instance = MagicMock()
                mock_llm_instance.invoke.return_value.content = "Test answer"
                mock_llm.return_value = mock_llm_instance

                # Mock Qdrant vectorstore operations
                with patch("src.vector_store.Qdrant") as mock_langchain_qdrant:
                    mock_vs = MagicMock()
                    mock_vs.similarity_search_with_score.return_value = [
                        (Document(page_content="Test doc", metadata={"id": "1"}), 0.9)
                    ]
                    mock_langchain_qdrant.return_value = mock_vs

                    # Initialize components
                    embedding_manager = EmbeddingManager(use_openai=False)
                    vector_store = QdrantVectorStore(
                        collection_name="test_e2e",
                        embedding_manager=embedding_manager,
                    )

                    doc_processor = DocumentProcessor()

                    # Create sample documents
                    documents = [
                        Document(
                            page_content="Python is a programming language.",
                            metadata={"source": "test.txt"},
                        ),
                    ]

                    chunks = doc_processor.chunk_documents(documents)

                    # Mock add_documents
                    mock_vs.add_documents.return_value = ["id1"]

                    # Add to vector store
                    vector_store.add_documents(chunks)

                    # Create RAG pipeline
                    hybrid_searcher = HybridSearcher(
                        vector_store=vector_store,
                        documents=chunks,
                    )

                    rag_pipeline = RAGPipeline(
                        vector_store=vector_store,
                        hybrid_searcher=hybrid_searcher,
                    )

                    # Query the system
                    result = rag_pipeline.query(
                        question="What is Python?",
                        search_type="hybrid",
                        rerank=False,
                    )

                    # Assertions
                    assert "answer" in result
                    assert "question" in result
                    assert result["question"] == "What is Python?"


@pytest.mark.integration
def test_document_processing_pipeline():
    """Test document processing from file to chunks."""
    import tempfile
    from pathlib import Path

    from src.document_processor import DocumentProcessor

    processor = DocumentProcessor(chunk_size=200, chunk_overlap=20)

    # Create temporary test file
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("This is a test document. " * 50)  # Create a longer document

        # Process file
        chunks = processor.process_files(file_paths=[str(test_file)])

        # Assertions
        assert len(chunks) > 0
        assert all(hasattr(chunk, "page_content") for chunk in chunks)
        assert all(hasattr(chunk, "metadata") for chunk in chunks)
        assert all("source" in chunk.metadata for chunk in chunks)


@pytest.mark.integration
def test_hybrid_search_integration(sample_documents):
    """Test hybrid search with mocked components."""
    from src.hybrid_search import HybridSearcher

    mock_vector_store = MagicMock()
    mock_vector_store.vector_search_with_score.return_value = [
        (sample_documents[0], 0.9),
        (sample_documents[1], 0.8),
    ]

    searcher = HybridSearcher(
        vector_store=mock_vector_store,
        documents=sample_documents,
    )

    # Test hybrid search
    results = searcher.hybrid_search(
        query="Python programming language",
        top_k=2,
        alpha=0.5,
    )

    assert len(results) <= 2
    assert all(isinstance(doc, Document) for doc, _ in results)
    assert all(isinstance(score, float) for _, score in results)
