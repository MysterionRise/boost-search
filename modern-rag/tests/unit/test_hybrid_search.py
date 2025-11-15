"""Tests for hybrid search module."""

import pytest
from unittest.mock import MagicMock, patch
from src.hybrid_search import HybridSearcher
from langchain_core.documents import Document


@pytest.mark.unit
def test_hybrid_searcher_init(sample_documents):
    """Test HybridSearcher initialization."""
    mock_vector_store = MagicMock()

    searcher = HybridSearcher(
        vector_store=mock_vector_store,
        documents=sample_documents,
    )

    assert searcher.vector_store == mock_vector_store
    assert len(searcher.documents) == len(sample_documents)
    assert searcher.bm25 is not None


@pytest.mark.unit
def test_bm25_search(sample_documents):
    """Test BM25 search."""
    mock_vector_store = MagicMock()

    searcher = HybridSearcher(
        vector_store=mock_vector_store,
        documents=sample_documents,
    )

    results = searcher.bm25_search("Python programming", top_k=2)

    assert isinstance(results, list)
    assert len(results) <= 2
    # Each result should be (Document, score) tuple
    for doc, score in results:
        assert isinstance(doc, Document)
        assert isinstance(score, float)
        assert score >= 0


@pytest.mark.unit
def test_update_documents(sample_documents):
    """Test updating documents in searcher."""
    mock_vector_store = MagicMock()

    searcher = HybridSearcher(
        vector_store=mock_vector_store,
        documents=[],
    )

    assert searcher.bm25 is None

    # Update with new documents
    searcher.update_documents(sample_documents)

    assert len(searcher.documents) == len(sample_documents)
    assert searcher.bm25 is not None


@pytest.mark.unit
def test_search_dispatch(sample_documents):
    """Test unified search interface."""
    mock_vector_store = MagicMock()
    mock_vector_store.vector_search_with_score.return_value = [
        (sample_documents[0], 0.9),
    ]

    searcher = HybridSearcher(
        vector_store=mock_vector_store,
        documents=sample_documents,
    )

    # Test vector search
    with patch("src.hybrid_search.settings") as mock_settings:
        mock_settings.top_k_retrieval = 5
        results = searcher.search("test query", search_type="vector", top_k=5)
        assert isinstance(results, list)

    # Test BM25 search
    results = searcher.search("test query", search_type="bm25", top_k=5)
    assert isinstance(results, list)

    # Test hybrid search
    results = searcher.search("test query", search_type="hybrid", top_k=5)
    assert isinstance(results, list)

    # Test invalid search type
    with pytest.raises(ValueError, match="Unknown search type"):
        searcher.search("test query", search_type="invalid")


@pytest.mark.unit
def test_combine_scores(sample_documents):
    """Test score combination logic."""
    mock_vector_store = MagicMock()

    searcher = HybridSearcher(
        vector_store=mock_vector_store,
        documents=sample_documents,
    )

    vector_results = [(sample_documents[0], 0.8), (sample_documents[1], 0.6)]
    bm25_results = [(sample_documents[0], 5.0), (sample_documents[2], 3.0)]

    combined = searcher._combine_scores(
        vector_results=vector_results,
        bm25_results=bm25_results,
        alpha=0.5,
    )

    assert isinstance(combined, dict)
    assert len(combined) > 0
    # Scores should be normalized between 0 and 1
    for score in combined.values():
        assert 0 <= score <= 1
