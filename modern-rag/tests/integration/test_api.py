"""Integration tests for FastAPI application."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create test client for API."""
    # Import here to avoid issues with startup
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

    with (
        patch("api.main.EmbeddingManager"),
        patch("api.main.QdrantVectorStore"),
        patch("api.main.HybridSearcher"),
        patch("api.main.RAGPipeline"),
    ):

        from api.main import app

        client = TestClient(app)
        yield client


@pytest.mark.integration
@pytest.mark.requires_docker
def test_api_root(test_client):
    """Test API root endpoint."""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.integration
@pytest.mark.requires_docker
def test_api_health_check(test_client):
    """Test health check endpoint."""
    with patch("api.main.vector_store") as mock_vs:
        mock_vs.get_collection_info.return_value = {
            "name": "test",
            "points_count": 0,
            "vectors_count": 0,
            "status": "green",
        }

        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.integration
@pytest.mark.requires_docker
def test_api_query(test_client):
    """Test query endpoint."""
    with patch("api.main.rag_pipeline") as mock_pipeline:
        mock_pipeline.query.return_value = {
            "question": "Test question?",
            "answer": "Test answer.",
            "sources": [],
            "num_sources": 0,
        }

        response = test_client.post(
            "/query",
            json={
                "question": "Test question?",
                "search_type": "hybrid",
                "top_k": 3,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "question" in data


@pytest.mark.integration
@pytest.mark.requires_docker
def test_api_index(test_client):
    """Test index endpoint."""
    from langchain_core.documents import Document

    with (
        patch("api.main.vector_store") as mock_vs,
        patch("api.main.doc_processor") as mock_dp,
        patch("api.main.rag_pipeline") as mock_pipeline,
    ):

        mock_dp.chunk_documents.return_value = [
            Document(page_content="Test", metadata={"id": "1"}),
        ]
        mock_vs.add_documents.return_value = ["id1"]
        mock_pipeline.hybrid_searcher.documents = []

        response = test_client.post(
            "/index",
            json={
                "texts": ["Test document 1", "Test document 2"],
                "metadatas": [{"source": "test1"}, {"source": "test2"}],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "num_documents" in data
        assert data["num_documents"] == 2


@pytest.mark.integration
@pytest.mark.requires_docker
def test_api_stats(test_client):
    """Test stats endpoint."""
    with patch("api.main.vector_store") as mock_vs, patch("api.main.settings") as mock_settings:

        mock_vs.get_collection_info.return_value = {
            "name": "test_collection",
            "points_count": 100,
            "vectors_count": 100,
            "status": "green",
        }

        mock_settings.embedding_model = "test-model"
        mock_settings.llm_provider = "openai"
        mock_settings.llm_model = "gpt-4"
        mock_settings.search_type = "hybrid"
        mock_settings.rerank_enabled = True

        response = test_client.get("/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "collection_name" in data
