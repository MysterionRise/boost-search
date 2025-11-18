"""Tests for reranker module (Python 3.12+ compatible)."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from langchain_core.documents import Document

from src.reranker import HybridSearchWithReranking, Reranker


@pytest.mark.unit
def test_reranker_init():
    """Test Reranker initialization."""
    with patch("src.reranker.CrossEncoder"):
        reranker = Reranker(model_name="test-model")
        assert reranker.model is not None
        assert reranker.model_name == "test-model"


@pytest.mark.unit
def test_rerank_documents():
    """Test document reranking."""
    with patch("src.reranker.CrossEncoder") as mock_cross_encoder_class:
        # Mock the cross-encoder
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0.95, 0.85])
        mock_cross_encoder_class.return_value = mock_model

        reranker = Reranker()

        documents = [
            Document(page_content="Doc 1", metadata={"id": "1"}),
            Document(page_content="Doc 2", metadata={"id": "2"}),
        ]

        results = reranker.rerank(
            query="test query",
            documents=documents,
            top_k=2,
        )

        assert len(results) == 2
        assert all(isinstance(doc, Document) for doc, _ in results)
        assert all(isinstance(score, (int, float, np.floating)) for _, score in results)
        # Results should be sorted by score (descending)
        assert results[0][1] >= results[1][1]


@pytest.mark.unit
def test_rerank_empty_documents():
    """Test reranking with empty document list."""
    with patch("src.reranker.CrossEncoder"):
        reranker = Reranker()

        results = reranker.rerank(
            query="test query",
            documents=[],
            top_k=5,
        )

        assert results == []


@pytest.mark.unit
def test_hybrid_search_with_reranking_init():
    """Test HybridSearchWithReranking initialization."""
    mock_hybrid_searcher = MagicMock()

    with patch("src.reranker.Reranker"):
        with patch("src.reranker.settings") as mock_settings:
            mock_settings.rerank_enabled = True

            search = HybridSearchWithReranking(
                hybrid_searcher=mock_hybrid_searcher,
            )

            assert search.hybrid_searcher == mock_hybrid_searcher
            assert search.reranker is not None


@pytest.mark.unit
def test_search_with_reranking():
    """Test search with reranking enabled."""
    mock_hybrid_searcher = MagicMock()
    mock_documents = [Document(page_content=f"Doc {i}", metadata={"id": str(i)}) for i in range(5)]
    mock_hybrid_searcher.search.return_value = [(doc, 0.5) for doc in mock_documents]

    with patch("src.reranker.CrossEncoder") as mock_cross_encoder_class:
        with patch("src.reranker.settings") as mock_settings:
            mock_settings.rerank_enabled = True
            mock_settings.top_k_retrieval = 10
            mock_settings.top_k_final = 3

            # Mock cross-encoder
            mock_model = MagicMock()
            mock_model.predict.return_value = np.array([0.9, 0.8, 0.7, 0.6, 0.5])
            mock_cross_encoder_class.return_value = mock_model

            search = HybridSearchWithReranking(
                hybrid_searcher=mock_hybrid_searcher,
            )

            results = search.search(
                query="test query",
                rerank=True,
            )

            assert len(results) <= 3
            assert all(isinstance(doc, Document) for doc, _ in results)


@pytest.mark.unit
def test_search_without_reranking():
    """Test search with reranking disabled."""
    mock_hybrid_searcher = MagicMock()
    mock_documents = [Document(page_content=f"Doc {i}", metadata={"id": str(i)}) for i in range(5)]
    mock_hybrid_searcher.search.return_value = [(doc, 0.5) for doc in mock_documents]

    with patch("src.reranker.settings") as mock_settings:
        mock_settings.rerank_enabled = False
        mock_settings.top_k_retrieval = 10
        mock_settings.top_k_final = 3

        search = HybridSearchWithReranking(
            hybrid_searcher=mock_hybrid_searcher,
            reranker=None,
        )

        results = search.search(
            query="test query",
            rerank=False,
        )

        # Should return top_k_final results without reranking
        assert len(results) <= 3
