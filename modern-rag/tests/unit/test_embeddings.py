"""Tests for embeddings module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.embeddings import EmbeddingManager, SentenceTransformerEmbeddings


@pytest.mark.unit
def test_embedding_manager_init_local(mock_sentence_transformer, mock_settings):
    """Test EmbeddingManager initialization with local model."""
    with patch("src.embeddings.settings", mock_settings):
        manager = EmbeddingManager(use_openai=False)

        assert manager.use_openai is False
        assert manager.dimension == 384
        assert hasattr(manager, "embeddings")


@pytest.mark.unit
def test_embedding_manager_init_openai(mock_openai_embeddings, mock_settings):
    """Test EmbeddingManager initialization with OpenAI."""
    with patch("src.embeddings.settings", mock_settings):
        manager = EmbeddingManager(use_openai=True)

        assert manager.use_openai is True
        assert manager.dimension == 1536


@pytest.mark.unit
def test_embed_documents(mock_sentence_transformer, mock_settings):
    """Test embedding multiple documents."""
    with patch("src.embeddings.settings", mock_settings):
        manager = EmbeddingManager(use_openai=False)

        texts = ["Document 1", "Document 2", "Document 3"]
        embeddings = manager.embed_documents(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) > 0


@pytest.mark.unit
def test_embed_query(mock_sentence_transformer, mock_settings):
    """Test embedding a single query."""
    with patch("src.embeddings.settings", mock_settings):
        manager = EmbeddingManager(use_openai=False)

        query = "What is machine learning?"
        embedding = manager.embed_query(query)

        assert isinstance(embedding, list)
        assert len(embedding) > 0


@pytest.mark.unit
def test_sentence_transformer_wrapper():
    """Test SentenceTransformer wrapper."""
    mock_model = MagicMock()
    # Return numpy arrays (what sentence-transformers actually returns)
    mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

    wrapper = SentenceTransformerEmbeddings(mock_model)

    # Test embed_documents
    docs = ["doc1", "doc2"]
    embeddings = wrapper.embed_documents(docs)
    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert all(isinstance(emb, list) for emb in embeddings)

    # Test embed_query
    mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
    query = "test query"
    embedding = wrapper.embed_query(query)
    assert isinstance(embedding, list)
    assert len(embedding) == 3
