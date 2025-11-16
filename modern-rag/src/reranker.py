"""Reranking implementation using sentence-transformers cross-encoder (Python 3.12 compatible)."""

from sentence_transformers import CrossEncoder
from langchain_core.documents import Document

from .config import settings


class Reranker:
    """Reranks search results using cross-encoder models."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """Initialize reranker.

        Args:
            model_name: Name of the cross-encoder model
                       Default: cross-encoder/ms-marco-MiniLM-L-6-v2 (lightweight, good performance)
                       Alternatives:
                       - cross-encoder/ms-marco-MiniLM-L-12-v2 (larger, better quality)
                       - cross-encoder/ms-marco-TinyBERT-L-2-v2 (tiny, fastest)
        """
        self.model = CrossEncoder(model_name)
        self.model_name = model_name
        print(f"Initialized cross-encoder reranker: {model_name}")

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = None,
    ) -> list[tuple[Document, float]]:
        """Rerank documents based on query relevance.

        Args:
            query: Search query
            documents: List of documents to rerank
            top_k: Number of top results to return

        Returns:
            List of (document, score) tuples sorted by relevance
        """
        if not documents:
            return []

        top_k = top_k or settings.top_k_rerank

        # Prepare query-document pairs for cross-encoder
        pairs = [[query, doc.page_content] for doc in documents]

        # Get relevance scores
        scores = self.model.predict(pairs)

        # Combine documents with scores and sort by score (descending)
        doc_scores = list(zip(documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top_k results
        return doc_scores[:top_k]


class HybridSearchWithReranking:
    """Combines hybrid search with reranking."""

    def __init__(self, hybrid_searcher, reranker: Reranker = None):
        """Initialize hybrid search with reranking.

        Args:
            hybrid_searcher: HybridSearcher instance
            reranker: Reranker instance (optional)
        """
        self.hybrid_searcher = hybrid_searcher
        self.reranker = reranker or (Reranker() if settings.rerank_enabled else None)

    def search(
        self,
        query: str,
        search_type: str = None,
        top_k_retrieval: int = None,
        top_k_final: int = None,
        rerank: bool = None,
        **kwargs,
    ) -> list[tuple[Document, float]]:
        """Search with optional reranking.

        Args:
            query: Search query
            search_type: Type of search ('vector', 'bm25', 'hybrid')
            top_k_retrieval: Number of documents to retrieve initially
            top_k_final: Number of final results after reranking
            rerank: Whether to apply reranking
            **kwargs: Additional search arguments

        Returns:
            List of (document, score) tuples
        """
        rerank = rerank if rerank is not None else settings.rerank_enabled
        top_k_retrieval = top_k_retrieval or settings.top_k_retrieval
        top_k_final = top_k_final or settings.top_k_final

        # Initial retrieval
        results = self.hybrid_searcher.search(
            query=query,
            search_type=search_type,
            top_k=top_k_retrieval,
            **kwargs,
        )

        # Extract documents
        documents = [doc for doc, _ in results]

        # Apply reranking if enabled
        if rerank and self.reranker and documents:
            results = self.reranker.rerank(
                query=query,
                documents=documents,
                top_k=top_k_final,
            )
        else:
            results = results[:top_k_final]

        return results
