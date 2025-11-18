"""Configuration management for Modern RAG system."""

from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")

    # LangSmith
    langchain_tracing_v2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    langchain_api_key: str = Field(default="", env="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="modern-rag", env="LANGCHAIN_PROJECT")

    # OpenSearch
    opensearch_host: str = Field(default="localhost", env="OPENSEARCH_HOST")
    opensearch_port: int = Field(default=9200, env="OPENSEARCH_PORT")
    opensearch_user: str = Field(default="admin", env="OPENSEARCH_USER")
    opensearch_password: str = Field(default="admin", env="OPENSEARCH_PASSWORD")
    opensearch_index_name: str = Field(default="documents", env="OPENSEARCH_INDEX_NAME")
    opensearch_use_ssl: bool = Field(default=False, env="OPENSEARCH_USE_SSL")

    # Embeddings
    embedding_model: str = Field(default="BAAI/bge-large-en-v1.5", env="EMBEDDING_MODEL")

    # LLM Configuration
    llm_provider: Literal["openai", "ollama", "anthropic"] = Field(
        default="openai", env="LLM_PROVIDER"
    )
    llm_model: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.0, env="LLM_TEMPERATURE")

    # Search Configuration
    search_type: Literal["vector", "bm25", "hybrid"] = Field(default="hybrid", env="SEARCH_TYPE")
    rerank_enabled: bool = Field(default=True, env="RERANK_ENABLED")
    top_k_retrieval: int = Field(default=20, env="TOP_K_RETRIEVAL")
    top_k_rerank: int = Field(default=5, env="TOP_K_RERANK")
    top_k_final: int = Field(default=3, env="TOP_K_FINAL")

    # Chunking
    chunk_size: int = Field(default=500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
