"""Tests for evaluation module."""

import pytest
from langchain_core.documents import Document

from src.evaluation import EvaluationExample, RetrievalEvaluator


@pytest.mark.unit
def test_evaluation_example():
    """Test EvaluationExample dataclass."""
    example = EvaluationExample(
        question="What is Python?",
        ground_truth="Python is a programming language.",
        answer="Python is a high-level language.",
        contexts=["Python context"],
    )

    assert example.question == "What is Python?"
    assert example.answer is not None
    assert example.contexts is not None


@pytest.mark.unit
def test_calculate_mrr():
    """Test Mean Reciprocal Rank calculation."""
    evaluator = RetrievalEvaluator()

    # Create mock results
    doc1 = Document(page_content="Doc 1", metadata={"id": "1"})
    doc2 = Document(page_content="Doc 2", metadata={"id": "2"})
    doc3 = Document(page_content="Doc 3", metadata={"id": "3"})

    results = [
        [(doc1, 0.9), (doc2, 0.8), (doc3, 0.7)],  # Query 1: relevant is rank 1
        [(doc3, 0.9), (doc1, 0.8), (doc2, 0.7)],  # Query 2: relevant is rank 2
    ]

    relevant_docs = [
        {"1"},  # Doc 1 is relevant for query 1
        {"2"},  # Doc 2 is relevant for query 2
    ]

    mrr = evaluator.calculate_mrr(results, relevant_docs)

    # MRR = (1/1 + 1/3) / 2 = 0.667
    assert 0.6 < mrr < 0.7


@pytest.mark.unit
def test_calculate_precision_at_k():
    """Test Precision@K calculation."""
    evaluator = RetrievalEvaluator()

    doc1 = Document(page_content="Doc 1", metadata={"id": "1"})
    doc2 = Document(page_content="Doc 2", metadata={"id": "2"})
    doc3 = Document(page_content="Doc 3", metadata={"id": "3"})

    results = [
        [(doc1, 0.9), (doc2, 0.8), (doc3, 0.7)],  # 2 relevant in top 3
    ]

    relevant_docs = [
        {"1", "2"},  # Docs 1 and 2 are relevant
    ]

    precision = evaluator.calculate_precision_at_k(results, relevant_docs, k=3)

    # Precision@3 = 2/3 = 0.667
    assert abs(precision - 0.667) < 0.01


@pytest.mark.unit
def test_calculate_ndcg():
    """Test NDCG calculation."""
    evaluator = RetrievalEvaluator()

    doc1 = Document(page_content="Doc 1", metadata={"id": "1"})
    doc2 = Document(page_content="Doc 2", metadata={"id": "2"})
    doc3 = Document(page_content="Doc 3", metadata={"id": "3"})

    results = [
        [(doc1, 0.9), (doc2, 0.8), (doc3, 0.7)],
    ]

    relevance_scores = [
        {"1": 3.0, "2": 2.0, "3": 1.0},  # Graded relevance
    ]

    ndcg = evaluator.calculate_ndcg(results, relevance_scores, k=3)

    # NDCG should be between 0 and 1
    assert 0 <= ndcg <= 1


@pytest.mark.unit
def test_mrr_no_relevant():
    """Test MRR when no relevant documents found."""
    evaluator = RetrievalEvaluator()

    doc1 = Document(page_content="Doc 1", metadata={"id": "1"})
    doc2 = Document(page_content="Doc 2", metadata={"id": "2"})

    results = [
        [(doc1, 0.9), (doc2, 0.8)],
    ]

    relevant_docs = [
        {"999"},  # No relevant docs
    ]

    mrr = evaluator.calculate_mrr(results, relevant_docs)

    assert mrr == 0.0


@pytest.mark.unit
def test_precision_empty_results():
    """Test Precision@K with empty results."""
    evaluator = RetrievalEvaluator()

    results = [[]]
    relevant_docs = [{"1"}]

    precision = evaluator.calculate_precision_at_k(results, relevant_docs, k=5)

    assert precision == 0.0
