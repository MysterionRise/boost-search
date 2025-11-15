# Testing Guide for Modern RAG

This document describes the testing infrastructure and best practices for the Modern RAG system.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (fast, no external dependencies)
│   ├── test_config.py
│   ├── test_embeddings.py
│   ├── test_document_processor.py
│   ├── test_hybrid_search.py
│   ├── test_reranker.py
│   └── test_evaluation.py
└── integration/             # Integration tests (require services)
    ├── test_end_to_end.py
    └── test_api.py
```

## Running Tests

### Quick Start

```bash
# Install dev dependencies
make install-dev

# Run all tests
make test

# Run only unit tests (fast)
make test-unit

# Run integration tests
make test-integration

# Run with coverage report
make test-cov
```

### Using pytest directly

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# Run specific test file
pytest tests/unit/test_embeddings.py -v

# Run specific test function
pytest tests/unit/test_embeddings.py::test_embedding_manager_init_local -v

# Run tests matching a pattern
pytest -k "test_hybrid" -v

# Run with markers
pytest -m "unit and not requires_api_key"
pytest -m "integration"
pytest -m "slow"
```

## Test Markers

Tests are marked with the following markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (require services)
- `@pytest.mark.slow` - Slow tests (>1 second)
- `@pytest.mark.requires_api_key` - Tests requiring API keys (OpenAI, etc.)
- `@pytest.mark.requires_docker` - Tests requiring Docker services

### Running specific marker combinations

```bash
# Only unit tests, exclude those needing API keys
pytest -m "unit and not requires_api_key"

# All integration tests
pytest -m "integration"

# Skip slow tests
pytest -m "not slow"
```

## Code Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=src --cov-report=xml

# All formats
make test-cov
```

### Coverage Requirements

- Minimum coverage: 80%
- Critical modules (config, embeddings, vector_store): 90%+
- Integration tests: Cover main user flows

## Code Quality

### Linting

```bash
# Run ruff linter
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/

# Using make
make lint
```

### Formatting

```bash
# Check formatting
black --check src/ tests/

# Auto-format
black src/ tests/

# Using make
make format
make format-check
```

### Type Checking

```bash
# Run mypy
mypy src/

# With auto-install of types
mypy src/ --install-types --non-interactive
```

### Security Scanning

```bash
# Check for known vulnerabilities
safety check

# Security linting
bandit -r src/

# Using make
make security
```

## Pre-commit Hooks

Set up pre-commit hooks to run checks automatically:

```bash
# Install hooks
make pre-commit

# Or manually
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

Pre-commit will run:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Black formatting
- Ruff linting
- MyPy type checking

## CI/CD Pipeline

### GitHub Actions Workflows

1. **Modern RAG CI** (`.github/workflows/modern-rag-ci.yml`)
   - Runs on: Push to main/develop, PRs, changes to modern-rag/
   - Jobs:
     - Test (Python 3.11, 3.12)
     - Lint (Black, Ruff, MyPy)
     - Integration (with Qdrant service)
     - Docker Build
     - Security Scan
     - Coverage Report

2. **Dependency Review** (`.github/workflows/dependency-review.yml`)
   - Runs on: PRs with dependency changes
   - Checks for known vulnerabilities in dependencies

3. **CodeQL Analysis** (`.github/workflows/codeql-analysis.yml`)
   - Runs on: Push to main, PRs, weekly schedule
   - Security and quality analysis

### Viewing CI Results

- Check the "Actions" tab on GitHub
- Coverage reports are uploaded as artifacts
- Codecov integration for coverage trends

## Writing Tests

### Unit Test Example

```python
import pytest
from src.embeddings import EmbeddingManager

@pytest.mark.unit
def test_embedding_manager_init(mock_sentence_transformer, mock_settings):
    """Test EmbeddingManager initialization."""
    with patch("src.embeddings.settings", mock_settings):
        manager = EmbeddingManager(use_openai=False)

        assert manager.use_openai is False
        assert manager.dimension == 384
```

### Integration Test Example

```python
import pytest
from src import RAGPipeline, QdrantVectorStore

@pytest.mark.integration
@pytest.mark.requires_docker
def test_full_rag_pipeline():
    """Test complete RAG pipeline."""
    # Setup
    vector_store = QdrantVectorStore(collection_name="test")
    rag = RAGPipeline(vector_store=vector_store)

    # Test
    result = rag.query("What is Python?")

    # Assert
    assert "answer" in result
```

### Using Fixtures

```python
def test_with_sample_docs(sample_documents):
    """Use the sample_documents fixture from conftest.py"""
    assert len(sample_documents) == 3
    assert all(hasattr(doc, "page_content") for doc in sample_documents)
```

## Testing Best Practices

### DO:
- ✅ Write tests before fixing bugs (TDD)
- ✅ Use descriptive test names
- ✅ Mock external dependencies (APIs, databases)
- ✅ Test edge cases and error conditions
- ✅ Keep tests independent and isolated
- ✅ Use fixtures for common setup
- ✅ Add docstrings to test functions

### DON'T:
- ❌ Test implementation details
- ❌ Write tests that depend on external services in unit tests
- ❌ Share state between tests
- ❌ Use sleep() in tests (use mocks/timeouts)
- ❌ Commit code that breaks tests
- ❌ Skip tests without good reason

## Troubleshooting

### Tests Fail Locally But Pass in CI

- Check Python version (CI uses 3.11, 3.12)
- Ensure all dependencies installed: `make install-dev`
- Clear cache: `make clean`

### Integration Tests Timeout

- Ensure Docker is running
- Check Qdrant is accessible: `curl http://localhost:6333/health`
- Increase timeout: `pytest --timeout=120`

### Coverage Too Low

- Run with `--cov-report=term-missing` to see missing lines
- Focus on critical paths first
- Add integration tests for main flows

### Import Errors

- Check PYTHONPATH is set correctly
- Ensure you're in the right directory
- Try: `python -m pytest` instead of `pytest`

## Performance Testing

For performance testing (not in CI):

```python
import time

@pytest.mark.slow
def test_search_performance():
    start = time.time()
    # ... test code ...
    duration = time.time() - start
    assert duration < 1.0  # Should complete in < 1 second
```

## Continuous Improvement

- Monitor coverage trends in Codecov
- Review failed tests in CI regularly
- Update tests when adding features
- Refactor tests when they become flaky
- Keep test runtime under 5 minutes

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Black code formatter](https://black.readthedocs.io/)
- [Ruff linter](https://docs.astral.sh/ruff/)
- [MyPy type checker](https://mypy.readthedocs.io/)
