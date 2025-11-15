# Modern RAG System 🚀

A production-ready **Retrieval-Augmented Generation (RAG)** system implementing cutting-edge search technologies for 2024/2025.

## ✨ Features

### Core Capabilities
- **🔍 Hybrid Search**: Combines BM25 (keyword) + Dense Vector (semantic) search
- **🎯 Neural Reranking**: Cross-encoder reranking with FlashRank
- **🗄️ Modern Vector DB**: Qdrant integration with HNSW indexing
- **🤖 Multi-LLM Support**: OpenAI, Anthropic Claude, Ollama (local LLMs)
- **📊 Evaluation Framework**: RAGAS metrics + custom retrieval metrics
- **👁️ Observability**: LangSmith integration ready
- **🔄 Contextual Retrieval**: Anthropic-style chunk contextualization
- **⚡ Production API**: FastAPI with async support

### Advanced Features
- Conversational RAG with chat history
- Batch query processing
- Document upload and indexing
- Multiple file format support (PDF, DOCX, TXT, MD)
- Configurable chunking strategies
- Metadata filtering
- Real-time collection statistics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Query                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Hybrid Retrieval                            │
│  ┌─────────────┐        ┌──────────────┐                   │
│  │   BM25      │        │ Dense Vector │                    │
│  │  (Keyword)  │   +    │  (Semantic)  │                    │
│  └─────────────┘        └──────────────┘                    │
│         │                       │                            │
│         └───────────┬───────────┘                            │
│                     ▼                                        │
│         ┌──────────────────────┐                            │
│         │  Score Normalization │                            │
│         │   & Combination      │                            │
│         └──────────┬───────────┘                            │
└────────────────────┼────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Neural Reranking                                │
│         (Cross-Encoder: ms-marco-MiniLM)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 LLM Generation                               │
│      (GPT-4, Claude, or Llama via Ollama)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              Final Answer + Sources
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- OpenAI API key (or local LLM with Ollama)

### Installation

1. **Clone the repository**
```bash
cd boost-search/modern-rag
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Start Qdrant (Vector Database)**
```bash
# Option 1: Docker Compose
docker-compose up qdrant -d

# Option 2: Docker standalone
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### Basic Usage

```python
from src import (
    EmbeddingManager,
    QdrantVectorStore,
    HybridSearcher,
    DocumentProcessor,
    RAGPipeline,
)
from langchain_core.documents import Document

# Initialize components
embedding_manager = EmbeddingManager()
vector_store = QdrantVectorStore(
    collection_name="my_docs",
    embedding_manager=embedding_manager,
)

# Process documents
doc_processor = DocumentProcessor()
documents = [
    Document(
        page_content="Your document text here...",
        metadata={"source": "doc1.txt"},
    )
]

chunks = doc_processor.chunk_documents(documents)
vector_store.add_documents(chunks)

# Create RAG pipeline
hybrid_searcher = HybridSearcher(
    vector_store=vector_store,
    documents=chunks,
)

rag_pipeline = RAGPipeline(
    vector_store=vector_store,
    hybrid_searcher=hybrid_searcher,
)

# Ask questions
result = rag_pipeline.query(
    question="What is this document about?",
    search_type="hybrid",  # or "vector", "bm25"
    rerank=True,
)

print(result["answer"])
```

### Run Examples

```bash
# Basic example
python examples/basic_usage.py

# Advanced example with evaluation
python examples/advanced_usage.py
```

## 🔧 Configuration

Edit `.env` file or set environment variables:

```bash
# LLM Configuration
OPENAI_API_KEY=your-key-here
LLM_PROVIDER=openai  # openai, ollama, anthropic
LLM_MODEL=gpt-4-turbo-preview

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Embeddings
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# Search Settings
SEARCH_TYPE=hybrid  # vector, bm25, hybrid
RERANK_ENABLED=true
TOP_K_RETRIEVAL=20
TOP_K_FINAL=3

# Observability (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
```

## 🌐 API Server

### Start the API

```bash
# Development
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production with Docker
docker-compose --profile api up
```

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Query the RAG system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is hybrid search?",
    "search_type": "hybrid",
    "top_k": 3,
    "rerank": true
  }'

# Index new documents
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Document 1 content...", "Document 2 content..."],
    "metadatas": [{"source": "doc1.txt"}, {"source": "doc2.txt"}]
  }'

# Upload files
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"

# Search only (no generation)
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "search_type": "hybrid",
    "top_k": 5
  }'
```

## 📊 Evaluation

The system includes comprehensive evaluation capabilities:

### RAGAS Metrics
- **Faithfulness**: LLM answer grounded in retrieved context
- **Answer Relevancy**: Answer relevance to the question
- **Context Precision**: Relevant chunks ranked higher
- **Context Recall**: Coverage of ground truth in retrieved context

### Retrieval Metrics
- **MRR** (Mean Reciprocal Rank)
- **Precision@K**
- **NDCG@K** (Normalized Discounted Cumulative Gain)

```python
from src.evaluation import RAGEvaluator, RetrievalEvaluator, EvaluationExample

# RAG evaluation
evaluator = RAGEvaluator()
examples = [
    EvaluationExample(
        question="What is Python?",
        ground_truth="Python is a programming language...",
    )
]

results = evaluator.evaluate(examples, rag_pipeline)
print(results)

# Retrieval evaluation
retrieval_eval = RetrievalEvaluator()
mrr = retrieval_eval.calculate_mrr(search_results, relevant_docs)
```

## 🎯 Search Strategies

### 1. Vector Search (Semantic)
Best for: Conceptual queries, paraphrased questions
```python
result = rag_pipeline.query(question, search_type="vector")
```

### 2. BM25 Search (Keyword)
Best for: Exact terms, technical jargon, entity names
```python
result = rag_pipeline.query(question, search_type="bm25")
```

### 3. Hybrid Search (Recommended)
Best for: General use, combines strengths of both
```python
result = rag_pipeline.query(
    question,
    search_type="hybrid",
    rerank=True,  # Add neural reranking
)
```

## 🔬 Advanced Features

### Contextual Retrieval
```python
chunks = doc_processor.chunk_documents(
    documents,
    add_context=True,  # Anthropic-style contextualization
)
```

### Conversational RAG
```python
chat_history = []
result = rag_pipeline.query_with_chat_history(
    question="What are its benefits?",
    chat_history=chat_history,
)
```

### Metadata Filtering
```python
results = vector_store.vector_search(
    query="machine learning",
    filter_dict={"topic": "AI", "year": 2024},
)
```

### Batch Processing
```python
questions = ["Q1?", "Q2?", "Q3?"]
results = rag_pipeline.batch_query(questions)
```

## 🐳 Docker Deployment

### Full Stack
```bash
# Start all services
docker-compose --profile api up

# Services:
# - Qdrant: http://localhost:6333
# - RAG API: http://localhost:8000
# - Ollama (optional): http://localhost:11434
```

### Qdrant Only
```bash
docker-compose up qdrant
```

### With Local LLM (Ollama)
```bash
docker-compose --profile local-llm up
# Set LLM_PROVIDER=ollama in .env
```

## 📈 Performance Tips

1. **Embedding Model**: Use `BAAI/bge-large-en-v1.5` for best quality, `all-MiniLM-L6-v2` for speed
2. **Chunk Size**: 300-500 tokens for technical docs, 500-1000 for general content
3. **Reranking**: Enable for top-3 final results (too expensive for >10)
4. **Alpha Parameter**: Adjust hybrid search weight (0.5 = equal, >0.5 favors vector)
5. **Top-K Retrieval**: Retrieve 20-50, rerank to 3-5 for best results

## 🛠️ Development

### Project Structure
```
modern-rag/
├── src/
│   ├── config.py              # Configuration management
│   ├── embeddings.py          # Embedding models
│   ├── vector_store.py        # Qdrant integration
│   ├── hybrid_search.py       # Hybrid search logic
│   ├── reranker.py            # Neural reranking
│   ├── document_processor.py  # Document loading & chunking
│   ├── rag_pipeline.py        # Main RAG pipeline
│   └── evaluation.py          # Evaluation metrics
├── api/
│   └── main.py                # FastAPI application
├── examples/
│   ├── basic_usage.py
│   └── advanced_usage.py
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

### Running Tests
```bash
pytest tests/
```

## 🔮 Roadmap

- [ ] Multi-modal support (images + text with CLIP)
- [ ] Graph RAG integration
- [ ] Streaming responses
- [ ] Query caching
- [ ] Auto-optimization of retrieval parameters
- [ ] Support for more vector DBs (Weaviate, Pinecone)
- [ ] Distributed indexing
- [ ] Web UI

## 📚 References

- [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [LangChain Documentation](https://python.langchain.com/)
- [Qdrant Vector Database](https://qdrant.tech/)
- [RAGAS Evaluation](https://docs.ragas.io/)
- [FlashRank Reranking](https://github.com/PrithivirajDamodaran/FlashRank)

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with ❤️ for the boost-search project**
