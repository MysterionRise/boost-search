#!/usr/bin/env python3
"""Verify that all required dependencies are installed and importable."""

import sys
from typing import List, Tuple

def test_imports() -> List[Tuple[str, bool, str]]:
    """Test importing all required packages."""
    results = []
    
    # Core LangChain
    packages = [
        ("langchain", "langchain"),
        ("langchain_core", "langchain_core"),
        ("langchain_community", "langchain_community"),
        ("langchain_openai", "langchain_openai.ChatOpenAI"),
        
        # Vector DB
        ("qdrant_client", "qdrant_client.QdrantClient"),
        
        # Embeddings
        ("sentence_transformers", "sentence_transformers.SentenceTransformer"),
        
        # Search
        ("rank_bm25", "rank_bm25.BM25Okapi"),
        ("flashrank", "flashrank.Ranker"),
        
        # Document processing
        ("pypdf", "pypdf.PdfReader"),
        
        # API
        ("fastapi", "fastapi.FastAPI"),
        ("pydantic", "pydantic.BaseModel"),
        
        # Utilities
        ("numpy", "numpy"),
        ("pandas", "pandas"),
    ]
    
    for name, import_path in packages:
        try:
            parts = import_path.split(".")
            module = __import__(parts[0])
            for part in parts[1:]:
                module = getattr(module, part)
            
            version = getattr(__import__(parts[0]), "__version__", "unknown")
            results.append((name, True, version))
        except ImportError as e:
            results.append((name, False, str(e)))
    
    return results

def main():
    """Run verification."""
    print("=" * 60)
    print("Modern RAG - Dependency Verification")
    print("=" * 60)
    print()
    
    results = test_imports()
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    print(f"Package Status ({success_count}/{total_count} successful):")
    print("-" * 60)
    
    for name, success, info in results:
        status = "✓" if success else "✗"
        print(f"{status} {name:25s} {info}")
    
    print()
    
    if success_count == total_count:
        print("✅ All dependencies verified successfully!")
        return 0
    else:
        print(f"❌ {total_count - success_count} dependencies failed to import")
        print("\nTry:")
        print("  pip install -r requirements-lock.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
