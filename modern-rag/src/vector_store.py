"""OpenSearch vector store integration."""

from __future__ import annotations

from typing import Any

from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.documents import Document
from opensearchpy import OpenSearch

from .config import settings
from .embeddings import EmbeddingManager


class OpenSearchVectorStore:
    """Manages OpenSearch vector database operations."""

    def __init__(
        self,
        index_name: str = None,
        embedding_manager: EmbeddingManager = None,
    ):
        """Initialize OpenSearch vector store.

        Args:
            index_name: Name of the OpenSearch index
            embedding_manager: Embedding model manager
        """
        self.index_name = index_name or settings.opensearch_index_name
        self.embedding_manager = embedding_manager or EmbeddingManager()

        # Build OpenSearch connection URL
        self.opensearch_url = f"http{'s' if settings.opensearch_use_ssl else ''}://{settings.opensearch_host}:{settings.opensearch_port}"

        # Initialize OpenSearch client
        self.client = OpenSearch(
            hosts=[{"host": settings.opensearch_host, "port": settings.opensearch_port}],
            http_auth=(settings.opensearch_user, settings.opensearch_password),
            use_ssl=settings.opensearch_use_ssl,
            verify_certs=False,  # For development; set to True in production
            ssl_show_warn=False,
        )

        # Initialize index if it doesn't exist
        self._init_index()

        # LangChain OpenSearch wrapper
        self.langchain_vectorstore = OpenSearchVectorSearch(
            index_name=self.index_name,
            embedding_function=self.embedding_manager.embeddings,
            opensearch_url=self.opensearch_url,
            http_auth=(settings.opensearch_user, settings.opensearch_password),
            use_ssl=settings.opensearch_use_ssl,
            verify_certs=False,
            ssl_show_warn=False,
        )

    def _init_index(self):
        """Initialize OpenSearch index if it doesn't exist."""
        if not self.client.indices.exists(index=self.index_name):
            # Create index with k-NN settings for vector search
            index_body = {
                "settings": {
                    "index": {
                        "knn": True,  # Enable k-NN plugin
                        "knn.algo_param.ef_search": 100,
                    }
                },
                "mappings": {
                    "properties": {
                        "vector_field": {
                            "type": "knn_vector",
                            "dimension": self.embedding_manager.dimension,
                            "method": {
                                "name": "hnsw",
                                "space_type": "cosinesimil",
                                "engine": "nmslib",
                                "parameters": {"ef_construction": 128, "m": 24},
                            },
                        },
                        "text": {"type": "text"},
                        "metadata": {"type": "object"},
                    }
                },
            }
            self.client.indices.create(index=self.index_name, body=index_body)
            print(f"Created index: {self.index_name}")

    def add_documents(
        self,
        documents: list[Document],
        batch_size: int = 100,
    ) -> list[str]:
        """Add documents to the vector store.

        Args:
            documents: List of LangChain Document objects
            batch_size: Batch size for insertion

        Returns:
            List of document IDs
        """
        return self.langchain_vectorstore.add_documents(documents=documents)

    def vector_search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[Document]:
        """Perform vector similarity search.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of relevant documents
        """
        return self.langchain_vectorstore.similarity_search(
            query=query,
            k=top_k,
        )

    def vector_search_with_score(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[tuple[Document, float]]:
        """Perform vector search with relevance scores.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of (document, score) tuples
        """
        return self.langchain_vectorstore.similarity_search_with_score(
            query=query,
            k=top_k,
        )

    def delete_index(self):
        """Delete the entire index."""
        self.client.indices.delete(index=self.index_name)
        print(f"Deleted index: {self.index_name}")

    def get_index_info(self) -> dict[str, Any]:
        """Get information about the index.

        Returns:
            Index metadata and statistics
        """
        stats = self.client.indices.stats(index=self.index_name)
        index_stats = stats["indices"][self.index_name]

        return {
            "name": self.index_name,
            "docs_count": index_stats["total"]["docs"]["count"],
            "size_in_bytes": index_stats["total"]["store"]["size_in_bytes"],
            "status": "green" if self.client.cluster.health()["status"] == "green" else "yellow",
        }
