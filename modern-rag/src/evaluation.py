"""Evaluation framework using RAGAS."""

from dataclasses import dataclass

import pandas as pd
from datasets import Dataset

try:
    from ragas import evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    print("RAGAS not available. Install with: pip install ragas")


@dataclass
class EvaluationExample:
    """Single evaluation example."""

    question: str
    ground_truth: str
    answer: str | None = None
    contexts: list[str] | None = None


class RAGEvaluator:
    """Evaluates RAG system performance using RAGAS."""

    def __init__(self):
        """Initialize evaluator."""
        if not RAGAS_AVAILABLE:
            raise ImportError("RAGAS is not installed. Install with: pip install ragas")

        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]

    def evaluate(
        self,
        examples: list[EvaluationExample],
        rag_pipeline=None,
    ) -> dict[str, float]:
        """Evaluate RAG system.

        Args:
            examples: List of evaluation examples
            rag_pipeline: RAG pipeline instance (if answers not provided)

        Returns:
            Dictionary of metric scores
        """
        # Generate answers if not provided
        if rag_pipeline:
            for example in examples:
                if not example.answer:
                    result = rag_pipeline.query(example.question, return_sources=True)
                    example.answer = result["answer"]
                    example.contexts = [src["content"] for src in result["sources"]]

        # Prepare dataset
        data = {
            "question": [ex.question for ex in examples],
            "answer": [ex.answer for ex in examples],
            "contexts": [ex.contexts for ex in examples],
            "ground_truth": [ex.ground_truth for ex in examples],
        }

        dataset = Dataset.from_dict(data)

        # Evaluate
        result = evaluate(
            dataset,
            metrics=self.metrics,
        )

        return result

    def create_evaluation_report(
        self,
        results: dict[str, float],
        output_path: str | None = None,
    ) -> pd.DataFrame:
        """Create detailed evaluation report.

        Args:
            results: Evaluation results
            output_path: Optional path to save report

        Returns:
            DataFrame with results
        """
        df = pd.DataFrame([results])

        if output_path:
            df.to_csv(output_path, index=False)
            print(f"Evaluation report saved to: {output_path}")

        return df


class RetrievalEvaluator:
    """Evaluates retrieval performance."""

    @staticmethod
    def calculate_mrr(results: list[list[tuple]], relevant_docs: list[set]) -> float:
        """Calculate Mean Reciprocal Rank.

        Args:
            results: List of ranked results per query
            relevant_docs: List of relevant document sets per query

        Returns:
            MRR score
        """
        reciprocal_ranks = []
        for query_results, relevant_set in zip(results, relevant_docs):
            for rank, (doc, _) in enumerate(query_results, 1):
                doc_id = doc.metadata.get("id", doc.page_content)
                if doc_id in relevant_set:
                    reciprocal_ranks.append(1.0 / rank)
                    break
            else:
                reciprocal_ranks.append(0.0)

        return sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0

    @staticmethod
    def calculate_precision_at_k(
        results: list[list[tuple]],
        relevant_docs: list[set],
        k: int = 5,
    ) -> float:
        """Calculate Precision@K.

        Args:
            results: List of ranked results per query
            relevant_docs: List of relevant document sets per query
            k: Cutoff rank

        Returns:
            Precision@K score
        """
        precisions = []
        for query_results, relevant_set in zip(results, relevant_docs):
            top_k = query_results[:k]
            relevant_retrieved = sum(
                1 for doc, _ in top_k if doc.metadata.get("id", doc.page_content) in relevant_set
            )
            precisions.append(relevant_retrieved / k)

        return sum(precisions) / len(precisions) if precisions else 0.0

    @staticmethod
    def calculate_ndcg(
        results: list[list[tuple]],
        relevance_scores: list[dict[str, float]],
        k: int = 10,
    ) -> float:
        """Calculate Normalized Discounted Cumulative Gain.

        Args:
            results: List of ranked results per query
            relevance_scores: List of dicts mapping doc IDs to relevance scores
            k: Cutoff rank

        Returns:
            NDCG@K score
        """
        import numpy as np

        def dcg_at_k(scores, k):
            scores = np.array(scores[:k])
            return np.sum(scores / np.log2(np.arange(2, scores.size + 2)))

        ndcg_scores = []
        for query_results, relevance_dict in zip(results, relevance_scores):
            # Get relevance scores for retrieved docs
            retrieved_scores = []
            for doc, _ in query_results[:k]:
                doc_id = doc.metadata.get("id", doc.page_content)
                score = relevance_dict.get(doc_id, 0.0)
                retrieved_scores.append(score)

            # Calculate ideal DCG
            ideal_scores = sorted(relevance_dict.values(), reverse=True)[:k]

            dcg = dcg_at_k(retrieved_scores, k)
            idcg = dcg_at_k(ideal_scores, k)

            ndcg = dcg / idcg if idcg > 0 else 0.0
            ndcg_scores.append(ndcg)

        return sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0
