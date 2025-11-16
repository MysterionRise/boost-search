# Dependency Management

This document explains how dependencies are managed in the Modern RAG system.

## Files

### `requirements.txt` (Flexible)
- Uses version ranges (e.g., `>=0.1.20,<0.3.0`)
- Allows pip to resolve compatible versions
- Use for development and when you want latest compatible versions
- **Recommended for most users**

```bash
pip install -r requirements.txt
```

### `requirements-lock.txt` (Locked)
- Exact pinned versions (e.g., `==0.1.20`)
- Tested and verified to work together
- Use for reproducible builds and production deployments
- **Recommended for CI/CD and production**

```bash
pip install -r requirements-lock.txt
```

### `requirements-dev.txt`
- Development dependencies (testing, linting, formatting)
- Install for development work

```bash
pip install -r requirements-dev.txt
```

## Installation Methods

### Method 1: Flexible (Development)
```bash
# Install with version ranges
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt
```

### Method 2: Locked (Production)
```bash
# Install exact versions
pip install -r requirements-lock.txt
```

### Method 3: Editable Install (Contributors)
```bash
# Install in editable mode for development
pip install -e .
pip install -r requirements-dev.txt
```

## Key Dependencies

### LLM Framework
- **langchain**: Core LLM framework
- **langchain-community**: Community integrations
- **langchain-openai**: OpenAI integration
- **langchain-core**: Core abstractions

### Vector Database
- **qdrant-client**: Qdrant vector database client

### Embeddings
- **sentence-transformers**: Local embedding models
- **openai**: OpenAI API (including embeddings)

### Search Components
- **rank-bm25**: BM25 algorithm for keyword search
- **flashrank**: Neural reranking

### API
- **fastapi**: Modern web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation

## Dependency Conflicts

If you encounter dependency conflicts:

1. **Try requirements-lock.txt first**:
   ```bash
   pip install -r requirements-lock.txt
   ```

2. **Use virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Update to latest compatible versions**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Check for conflicts**:
   ```bash
   pip check
   ```

## Updating Dependencies

### Update all to latest compatible versions:
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements-lock.txt  # Update lock file
```

### Update specific package:
```bash
pip install --upgrade langchain
```

### Generate new lock file:
```bash
# Install from flexible requirements
pip install -r requirements.txt

# Freeze exact versions
pip freeze > requirements-lock.txt

# Test the lock file
pip install -r requirements-lock.txt
make test
```

## Known Compatibility Issues

### LangChain Ecosystem
- `langchain` requires `langchain-community>=0.0.21`
- `langchain-openai` has specific OpenAI version requirements
- Always install these together: `langchain`, `langchain-core`, `langchain-community`

### Python Version
- **Minimum**: Python 3.11
- **Recommended**: Python 3.11 or 3.12
- **Tested on**: Python 3.11, 3.12

### Optional Dependencies

#### Unstructured with PDF support:
```bash
pip install "unstructured[pdf]"
```

#### Ollama for local LLMs:
```bash
pip install ollama
```

#### vLLM for high-performance serving:
```bash
pip install vllm
```

## Security

### Check for vulnerabilities:
```bash
# Using safety (included in requirements-dev.txt)
safety check

# Using pip audit
pip install pip-audit
pip-audit
```

### Update security patches:
```bash
pip install --upgrade $(pip list --outdated --format=json | jq -r '.[] | .name')
```

## Troubleshooting

### "Cannot install... conflicting dependencies"

**Solution 1**: Use requirements-lock.txt
```bash
pip install -r requirements-lock.txt
```

**Solution 2**: Create fresh virtual environment
```bash
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Solution 3**: Install in order
```bash
# Install core dependencies first
pip install langchain langchain-core langchain-community langchain-openai

# Then install the rest
pip install -r requirements.txt
```

### "No module named..."

Ensure you've activated your virtual environment:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Slow pip install

Use pip cache or try binary wheels:
```bash
pip install --prefer-binary -r requirements.txt
```

## CI/CD Usage

In GitHub Actions, we use requirements-lock.txt for consistency:

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements-lock.txt
    pip install -r requirements-dev.txt
```

This ensures tests run with known-good versions.

## Contributing

When adding new dependencies:

1. Add to `requirements.txt` with version range
2. Test thoroughly
3. Update `requirements-lock.txt`:
   ```bash
   pip freeze > requirements-lock.txt
   ```
4. Run tests: `make test`
5. Update this documentation if needed

## Best Practices

1. ✅ **Use virtual environments** - Always isolate dependencies
2. ✅ **Pin major versions** - Avoid breaking changes
3. ✅ **Test after updates** - Run full test suite
4. ✅ **Document conflicts** - Help others avoid issues
5. ✅ **Lock for production** - Use requirements-lock.txt
6. ✅ **Regular updates** - Check for security patches monthly

## Support

If you encounter dependency issues:

1. Check this documentation
2. Try requirements-lock.txt
3. Open an issue on GitHub with:
   - Your Python version (`python --version`)
   - OS and version
   - Full error message
   - Output of `pip list`
