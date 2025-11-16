"""Qdrant vector store integration."""

from typing import Any

from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)

from .config import settings
from .embeddings import EmbeddingManager


class QdrantVectorStore:
    """Manages Qdrant vector database operations."""

    def __init__(
        self,
        collection_name: str = None,
        embedding_manager: EmbeddingManager = None,
    ):
        """Initialize Qdrant vector store.

        Args:
            collection_name: Name of the Qdrant collection
            embedding_manager: Embedding model manager
        """
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.embedding_manager = embedding_manager or EmbeddingManager()

        # Initialize Qdrant client
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None,
        )

        # Initialize collection if it doesn't exist
        self._init_collection()

        # LangChain Qdrant wrapper
        self.langchain_vectorstore = Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embedding_manager.embeddings,
        )

    def _init_collection(self):
        """Initialize Qdrant collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_manager.dimension,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Created collection: {self.collection_name}")

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
        return self.langchain_vectorstore.add_documents(
            documents=documents,
            batch_size=batch_size,
        )

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
            filter=filter_dict,
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
            filter=filter_dict,
        )

    def delete_collection(self):
        """Delete the entire collection."""
        self.client.delete_collection(collection_name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")

    def get_collection_info(self) -> dict[str, Any]:
        """Get information about the collection.

        Returns:
            Collection metadata and statistics
        """
        info = self.client.get_collection(collection_name=self.collection_name)
        return {
            "name": self.collection_name,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status,
        }
