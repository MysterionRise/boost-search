"""Embedding models management."""


from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer

from .config import settings


class EmbeddingManager:
    """Manages embedding models for vector search."""

    def __init__(self, model_name: str = None, use_openai: bool = False):
        """Initialize embedding model.

        Args:
            model_name: Name of the embedding model
            use_openai: Whether to use OpenAI embeddings
        """
        self.model_name = model_name or settings.embedding_model
        self.use_openai = use_openai

        if use_openai:
            self.embeddings: Embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small", openai_api_key=settings.openai_api_key
            )
            self.dimension = 1536  # text-embedding-3-small dimension
        else:
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            # Wrap SentenceTransformer for LangChain compatibility
            self.embeddings = SentenceTransformerEmbeddings(self.model)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)


class SentenceTransformerEmbeddings(Embeddings):
    """Wrapper for SentenceTransformer to work with LangChain."""

    def __init__(self, model: SentenceTransformer):
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents."""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Embed a query."""
        embedding = self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()
