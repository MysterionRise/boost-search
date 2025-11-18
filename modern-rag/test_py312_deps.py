#!/usr/bin/env python3
"""Test Python 3.12+ compatible dependencies can be imported."""

import sys

print(f"Python version: {sys.version}")
print(f"Python version info: {sys.version_info}")
print()

# Test core imports
try:
    print("Testing imports...")

    # LangChain
    from langchain.schema import Document as LCDocument
    print("✓ langchain")

    # Sentence Transformers (includes CrossEncoder for reranking)
    from sentence_transformers import CrossEncoder, SentenceTransformer
    print("✓ sentence-transformers (with CrossEncoder)")

    # Qdrant
    from qdrant_client import QdrantClient
    print("✓ qdrant-client")

    # BM25
    from rank_bm25 import BM25Okapi
    print("✓ rank-bm25")

    # FastAPI
    from fastapi import FastAPI
    print("✓ fastapi")

    # Pydantic
    from pydantic import BaseModel
    print("✓ pydantic")

    # Document loaders
    from pypdf import PdfReader
    print("✓ pypdf")

    from docx import Document as DocxDocument
    print("✓ python-docx")

    print()
    print("=" * 50)
    print("✅ All Python 3.12+ compatible dependencies work!")
    print("=" * 50)
    print()
    print("Removed incompatible packages:")
    print("  ✗ flashrank (onnxruntime incompatible with Python 3.12)")
    print("  ✗ unstructured (onnxruntime incompatible with Python 3.12)")
    print("  ✗ ragas (complex dependencies)")
    print()
    print("Alternatives used:")
    print("  ✓ sentence-transformers.CrossEncoder (replaces flashrank)")
    print("  ✓ pypdf + python-docx (replaces unstructured)")

except ImportError as e:
    print(f"❌ Import failed: {e}")
    print()
    print("Run: pip install -r requirements-lock.txt")
    sys.exit(1)
