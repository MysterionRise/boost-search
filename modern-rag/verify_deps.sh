#!/bin/bash
# Quick dependency verification script
# Tests that key packages can be resolved without conflicts

set -e

echo "=== Dependency Verification for Modern RAG ==="
echo ""
echo "Python version:"
python3 --version
echo ""

echo "Testing core LLM framework dependencies..."
python3 -m pip install --dry-run \
    langchain==0.1.20 \
    langchain-community==0.0.38 \
    langchain-core==0.1.52 \
    langchain-openai==0.1.7 \
    openai==1.30.0 \
    2>&1 | grep -E "(Would install|Successfully|ERROR)" | tail -3

echo ""
echo "Testing vector database dependencies..."
python3 -m pip install --dry-run \
    qdrant-client==1.9.1 \
    sentence-transformers==2.6.1 \
    2>&1 | grep -E "(Would install|Successfully|ERROR)" | tail -3

echo ""
echo "Testing hybrid search dependencies..."
python3 -m pip install --dry-run \
    rank-bm25==0.2.2 \
    flashrank==0.2.8 \
    2>&1 | grep -E "(Would install|Successfully|ERROR)" | tail -3

echo ""
echo "Testing document processing dependencies..."
python3 -m pip install --dry-run \
    "unstructured[pdf]==0.11.8" \
    pypdf==4.1.0 \
    python-docx==1.1.0 \
    2>&1 | grep -E "(Would install|Successfully|ERROR)" | tail -3

echo ""
echo "Testing API dependencies..."
python3 -m pip install --dry-run \
    fastapi==0.110.2 \
    "uvicorn[standard]==0.29.0" \
    pydantic==2.7.0 \
    pydantic-settings==2.2.1 \
    2>&1 | grep -E "(Would install|Successfully|ERROR)" | tail -3

echo ""
echo "=== Verification Complete ==="
echo "If no ERROR messages appeared above, all dependencies are compatible!"
