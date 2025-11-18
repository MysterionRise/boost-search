"""Test configuration and fixtures."""

import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("src.config.settings") as mock:
        mock.openai_api_key = "test-key"
        mock.opensearch_host = "localhost"
        mock.opensearch_port = 9200
        mock.opensearch_user = "admin"
        mock.opensearch_password = "admin"
        mock.opensearch_index_name = "test_index"
        mock.opensearch_use_ssl = False
        mock.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        mock.llm_provider = "openai"
        mock.llm_model = "gpt-3.5-turbo"
        mock.llm_temperature = 0.0
        mock.search_type = "hybrid"
        mock.rerank_enabled = True
        mock.top_k_retrieval = 20
        mock.top_k_rerank = 5
        mock.top_k_final = 3
        mock.chunk_size = 500
        mock.chunk_overlap = 50
        yield mock


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    from langchain_core.documents import Document

    return [
        Document(
            page_content="Python is a high-level programming language.",
            metadata={"id": "doc1", "source": "python.txt", "topic": "programming"},
        ),
        Document(
            page_content="Machine learning is a subset of artificial intelligence.",
            metadata={"id": "doc2", "source": "ml.txt", "topic": "AI"},
        ),
        Document(
            page_content="Vector databases store high-dimensional embeddings.",
            metadata={"id": "doc3", "source": "vectors.txt", "topic": "databases"},
        ),
    ]


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model."""
    mock = MagicMock()
    # Return numpy array (what sentence-transformers actually returns)
    mock.encode.return_value = np.array([[0.1] * 384])
    mock.get_sentence_embedding_dimension.return_value = 384
    return mock


@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client."""
    with patch("src.vector_store.OpenSearch") as mock:
        client = MagicMock()
        client.indices.exists.return_value = True
        client.indices.stats.return_value = {
            "indices": {
                "test_index": {
                    "total": {
                        "docs": {"count": 0},
                        "store": {"size_in_bytes": 0},
                    }
                }
            }
        }
        client.cluster.health.return_value = {"status": "green"}
        mock.return_value = client
        yield mock


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings."""
    with patch("src.embeddings.OpenAIEmbeddings") as mock:
        embeddings = MagicMock()
        embeddings.embed_documents.return_value = [[0.1] * 1536]
        embeddings.embed_query.return_value = [0.1] * 1536
        mock.return_value = embeddings
        yield mock


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer."""
    with patch("src.embeddings.SentenceTransformer") as mock:
        model = MagicMock()
        # Return numpy array (what sentence-transformers actually returns)
        model.encode.return_value = np.array([[0.1] * 384])
        model.get_sentence_embedding_dimension.return_value = 384
        mock.return_value = model
        yield mock


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    with patch("src.rag_pipeline.ChatOpenAI") as mock:
        llm = MagicMock()
        llm.invoke.return_value.content = "This is a test answer."
        mock.return_value = llm
        yield mock


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
