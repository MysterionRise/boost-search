"""Tests for configuration module."""

import pytest
from src.config import Settings


@pytest.mark.unit
def test_settings_defaults():
    """Test default settings."""
    settings = Settings()

    assert settings.qdrant_host == "localhost"
    assert settings.qdrant_port == 6333
    assert settings.embedding_model == "BAAI/bge-large-en-v1.5"
    assert settings.llm_provider == "openai"
    assert settings.search_type == "hybrid"
    assert settings.rerank_enabled is True


@pytest.mark.unit
def test_settings_from_env(monkeypatch):
    """Test settings loaded from environment."""
    monkeypatch.setenv("QDRANT_HOST", "test-host")
    monkeypatch.setenv("QDRANT_PORT", "7777")
    monkeypatch.setenv("LLM_MODEL", "gpt-4")
    monkeypatch.setenv("SEARCH_TYPE", "vector")

    settings = Settings()

    assert settings.qdrant_host == "test-host"
    assert settings.qdrant_port == 7777
    assert settings.llm_model == "gpt-4"
    assert settings.search_type == "vector"


@pytest.mark.unit
def test_settings_validation():
    """Test settings validation."""
    # Valid settings
    settings = Settings(
        llm_provider="openai",
        search_type="hybrid",
    )
    assert settings.llm_provider == "openai"

    # Invalid provider should raise validation error
    with pytest.raises(Exception):  # Pydantic validation error
        Settings(llm_provider="invalid_provider")
