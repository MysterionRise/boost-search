"""Hybrid search combining BM25 and dense vector search."""

from __future__ import annotations

from typing import Any

import numpy as np
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from .config import settings
from .vector_store import QdrantVectorStore


class HybridSearcher:
    """Implements hybrid search using BM25 + Dense Vector + Reranking."""

    def __init__(
        self,
        vector_store: QdrantVectorStore,
        documents: list[Document] = None,
    ):
        """Initialize hybrid searcher.

        Args:
            vector_store: Qdrant vector store instance
            documents: List of documents for BM25 indexing
        """
        self.vector_store = vector_store
        self.documents = documents or []
        self.bm25 = None

        if self.documents:
            self._init_bm25()

    def _init_bm25(self):
        """Initialize BM25 index."""
        # Tokenize documents for BM25
        tokenized_docs = [doc.page_content.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        print(f"Initialized BM25 with {len(self.documents)} documents")

    def update_documents(self, documents: list[Document]):
        """Update the document corpus and rebuild BM25 index.

        Args:
            documents: New list of documents
        """
        self.documents = documents
        self._init_bm25()

    def bm25_search(self, query: str, top_k: int = 10) -> list[tuple[Document, float]]:
        """Perform BM25 keyword search.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (document, score) tuples
        """
        if not self.bm25:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        # Get top k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with positive scores
                results.append((self.documents[idx], float(scores[idx])))

        return results

    def hybrid_search(
        self,
        query: str,
        top_k: int = None,
        alpha: float = 0.5,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[tuple[Document, float]]:
        """Perform hybrid search combining BM25 and vector search.

        Args:
            query: Search query
            top_k: Number of final results (default from settings)
            alpha: Weight for vector search (1-alpha for BM25). Range [0, 1]
            filter_dict: Optional metadata filters for vector search

        Returns:
            List of (document, score) tuples sorted by hybrid score
        """
        top_k = top_k or settings.top_k_retrieval

        # Get vector search results
        vector_results = self.vector_store.vector_search_with_score(
            query=query,
            top_k=top_k,
            filter_dict=filter_dict,
        )

        # Get BM25 results
        bm25_results = self.bm25_search(query=query, top_k=top_k)

        # Normalize scores and combine
        combined_scores = self._combine_scores(
            vector_results=vector_results,
            bm25_results=bm25_results,
            alpha=alpha,
        )

        # Sort by combined score (value is (doc, score) tuple)
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        # Return as list of (document, score) tuples
        return sorted_results

    def _combine_scores(
        self,
        vector_results: list[tuple[Document, float]],
        bm25_results: list[tuple[Document, float]],
        alpha: float,
    ) -> dict[str, tuple[Document, float]]:
        """Combine and normalize scores from different search methods.

        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            alpha: Weight for vector search

        Returns:
            Dictionary mapping content strings to (document, score) tuples
        """
        # Normalize vector scores (Qdrant returns distance, lower is better for cosine)
        vector_scores = {}
        if vector_results:
            max_vec_score = max(score for _, score in vector_results) if vector_results else 1.0
            min_vec_score = min(score for _, score in vector_results) if vector_results else 0.0
            score_range = max_vec_score - min_vec_score if max_vec_score != min_vec_score else 1.0

            for doc, score in vector_results:
                # Normalize to [0, 1], higher is better
                normalized = (max_vec_score - score) / score_range
                vector_scores[doc.page_content] = normalized

        # Normalize BM25 scores
        bm25_scores = {}
        if bm25_results:
            max_bm25 = max(score for _, score in bm25_results) if bm25_results else 1.0
            for doc, score in bm25_results:
                normalized = score / max_bm25 if max_bm25 > 0 else 0
                bm25_scores[doc.page_content] = normalized

        # Combine scores
        all_docs = {}
        combined_scores = {}

        # Add vector results
        for doc, _ in vector_results:
            all_docs[doc.page_content] = doc

        # Add BM25 results
        for doc, _ in bm25_results:
            all_docs[doc.page_content] = doc

        # Calculate hybrid scores
        for content, doc in all_docs.items():
            vec_score = vector_scores.get(content, 0.0)
            bm25_score = bm25_scores.get(content, 0.0)
            hybrid_score = alpha * vec_score + (1 - alpha) * bm25_score
            # Use content as key (hashable), store (doc, score) as value
            combined_scores[content] = (doc, hybrid_score)

        return combined_scores

    def search(
        self,
        query: str,
        search_type: str = None,
        top_k: int = None,
        **kwargs,
    ) -> list[tuple[Document, float]]:
        """Unified search interface.

        Args:
            query: Search query
            search_type: Type of search ('vector', 'bm25', 'hybrid')
            top_k: Number of results
            **kwargs: Additional arguments for specific search types

        Returns:
            List of (document, score) tuples
        """
        search_type = search_type or settings.search_type
        top_k = top_k or settings.top_k_retrieval

        if search_type == "vector":
            return self.vector_store.vector_search_with_score(query, top_k)
        elif search_type == "bm25":
            return self.bm25_search(query, top_k)
        elif search_type == "hybrid":
            return self.hybrid_search(query, top_k, **kwargs)
        else:
            raise ValueError(f"Unknown search type: {search_type}")
