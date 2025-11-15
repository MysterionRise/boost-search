## Different cutting-edge approaches to traditional information retrieval projects

What's inside:

### 🔥 Modern (2024/2025) Implementations
- **[modern-rag](modern-rag/README.md)** - Production-ready RAG system with:
  - Hybrid Search (BM25 + Dense Vectors + Neural Reranking)
  - Qdrant vector database with HNSW indexing
  - LangChain integration with multi-LLM support (OpenAI, Anthropic, Ollama)
  - RAGAS evaluation framework
  - FastAPI server with comprehensive endpoints
  - Contextual retrieval (Anthropic approach)
  - Docker deployment ready

### Legacy Implementations (2020-2021)
- Docker compose files with Elastic and Kibana nodes (both Elastic and Open Distro)
- Dense vectors usage in Elastic for PDF documents similarity
- *farm-haystack* docker-compose ready project with Q&A app (https://github.com/deepset-ai/haystack)
- *jina-ai* plays with image and text similarity (https://github.com/jina-ai/jina)
- *nboost* (https://github.com/koursaros-ai/nboost)
- *Milvus* (https://milvus.io/)
- [Permissions search](permissions-search/README.md) in Elastic

## 🚀 Quick Start with Modern RAG

```bash
cd modern-rag
./quick_start.sh
# Follow the instructions to set up and run
```

See [modern-rag/README.md](modern-rag/README.md) for complete documentation.
