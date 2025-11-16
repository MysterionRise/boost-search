"""Advanced usage example with document loading and evaluation."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (
    DocumentProcessor,
    EmbeddingManager,
    HybridSearcher,
    QdrantVectorStore,
    RAGPipeline,
    settings,
)
from src.evaluation import RetrievalEvaluator


def main():
    """Run advanced RAG example."""
    print("=== Modern RAG System - Advanced Usage ===\n")

    # Initialize components
    embedding_manager = EmbeddingManager()
    vector_store = QdrantVectorStore(
        collection_name="advanced_demo",
        embedding_manager=embedding_manager,
    )

    # Process documents from a directory
    doc_processor = DocumentProcessor(
        chunk_size=300,  # Smaller chunks
        chunk_overlap=50,
    )

    # Option 1: Load from directory
    # documents = doc_processor.process_files(directory_path="./data/documents")

    # Option 2: Load specific files
    # documents = doc_processor.process_files(
    #     file_paths=["./data/doc1.pdf", "./data/doc2.txt"]
    # )

    # For demo, use sample documents
    from langchain_core.documents import Document

    docs = [
        Document(
            page_content="Hybrid search combines sparse retrieval methods like BM25 with dense vector search. BM25 excels at exact keyword matching, while dense vectors capture semantic meaning. By combining both approaches, hybrid search achieves better accuracy than either method alone.",
            metadata={"id": "doc1", "source": "search_methods.txt"},
        ),
        Document(
            page_content="Cross-encoder reranking improves search results by scoring query-document pairs directly. Unlike bi-encoders that create separate embeddings, cross-encoders process both inputs together, yielding more accurate relevance scores at the cost of higher computational requirements.",
            metadata={"id": "doc2", "source": "reranking.txt"},
        ),
        Document(
            page_content="Contextual retrieval prepends document context to each chunk before embedding. This technique, introduced by Anthropic, helps preserve semantic meaning by providing broader context. It can significantly improve retrieval accuracy, especially for technical documents.",
            metadata={"id": "doc3", "source": "contextual_retrieval.txt"},
        ),
    ]

    chunks = doc_processor.chunk_documents(docs, add_context=True)
    print(f"Processed {len(chunks)} chunks with contextual information\n")

    # Index documents
    vector_store.add_documents(chunks)

    # Initialize search with reranking
    hybrid_searcher = HybridSearcher(vector_store=vector_store, documents=chunks)
    rag_pipeline = RAGPipeline(vector_store=vector_store, hybrid_searcher=hybrid_searcher)

    # Compare search methods
    print("=== Comparing Search Methods ===\n")
    query = "How does hybrid search work?"

    search_types = ["vector", "bm25", "hybrid"]
    for search_type in search_types:
        print(f"\n{search_type.upper()} Search:")
        result = rag_pipeline.query(
            question=query,
            search_type=search_type,
            top_k=2,
            rerank=False,
            return_sources=True,
        )

        for i, source in enumerate(result["sources"], 1):
            print(
                f"  [{i}] Score: {source['relevance_score']:.3f} - {source['metadata']['source']}"
            )

    # Test with reranking
    print("\n\nHYBRID + RERANKING:")
    result = rag_pipeline.query(
        question=query,
        search_type="hybrid",
        rerank=True,
        return_sources=True,
    )

    for i, source in enumerate(result["sources"], 1):
        print(f"  [{i}] Score: {source['relevance_score']:.3f} - {source['metadata']['source']}")

    # Conversational RAG
    print("\n\n=== Conversational RAG ===\n")

    chat_history = []
    questions_sequence = [
        "What is hybrid search?",
        "What are its benefits?",
        "How does it compare to traditional search?",
    ]

    for question in questions_sequence:
        result = rag_pipeline.query_with_chat_history(
            question=question,
            chat_history=chat_history,
            return_sources=False,
        )

        print(f"Q: {question}")
        print(f"A: {result['answer']}\n")

        chat_history.append(
            {
                "question": question,
                "answer": result["answer"],
            }
        )

    # Evaluate retrieval
    print("=== Retrieval Evaluation ===\n")

    test_queries = [
        "How does hybrid search work?",
        "What is cross-encoder reranking?",
        "Explain contextual retrieval",
    ]

    # Define relevant docs for each query
    relevant_docs = [
        {"doc1"},  # Query 1
        {"doc2"},  # Query 2
        {"doc3"},  # Query 3
    ]

    results = []
    for query in test_queries:
        search_results = hybrid_searcher.search(query, top_k=3)
        results.append(search_results)

    evaluator = RetrievalEvaluator()

    mrr = evaluator.calculate_mrr(results, relevant_docs)
    precision_at_3 = evaluator.calculate_precision_at_k(results, relevant_docs, k=3)

    print(f"Mean Reciprocal Rank (MRR): {mrr:.3f}")
    print(f"Precision@3: {precision_at_3:.3f}")

    print("\n=== Advanced Demo Complete ===")


if __name__ == "__main__":
    if not settings.openai_api_key and settings.llm_provider == "openai":
        print("Warning: OPENAI_API_KEY not set.")
        sys.exit(1)

    main()
