"""RAG pipeline implementation using LangChain."""

from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .config import settings
from .hybrid_search import HybridSearcher
from .reranker import HybridSearchWithReranking
from .vector_store import QdrantVectorStore


class RAGPipeline:
    """Complete RAG pipeline with hybrid search and reranking."""

    def __init__(
        self,
        vector_store: QdrantVectorStore,
        hybrid_searcher: HybridSearcher,
        llm_provider: str = None,
        llm_model: str = None,
    ):
        """Initialize RAG pipeline.

        Args:
            vector_store: Qdrant vector store
            hybrid_searcher: Hybrid search instance
            llm_provider: LLM provider ('openai', 'ollama', 'anthropic')
            llm_model: Model name
        """
        self.vector_store = vector_store
        self.hybrid_searcher = hybrid_searcher
        self.search_with_reranking = HybridSearchWithReranking(hybrid_searcher)

        # Initialize LLM
        self.llm_provider = llm_provider or settings.llm_provider
        self.llm_model = llm_model or settings.llm_model
        self.llm = self._init_llm()

        # Create RAG chain
        self.chain = self._create_chain()

    def _init_llm(self):
        """Initialize LLM based on provider."""
        if self.llm_provider == "openai":
            return ChatOpenAI(
                model=self.llm_model,
                temperature=settings.llm_temperature,
                openai_api_key=settings.openai_api_key,
            )
        elif self.llm_provider == "ollama":
            from langchain_community.llms import Ollama

            return Ollama(
                model=self.llm_model,
                temperature=settings.llm_temperature,
            )
        elif self.llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=self.llm_model,
                temperature=settings.llm_temperature,
                anthropic_api_key=settings.anthropic_api_key,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _create_chain(self):
        """Create the RAG chain."""
        # Define prompt template
        template = """You are a helpful AI assistant. Answer the question based on the following context.
If you cannot answer the question based on the context, say so.

Context:
{context}

Question: {question}

Answer:"""

        prompt = ChatPromptTemplate.from_template(template)

        # Create chain
        chain = (
            {
                "context": lambda x: self._format_docs(x["documents"]),
                "question": lambda x: x["question"],
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain

    def _format_docs(self, docs: list[Document]) -> str:
        """Format documents for context.

        Args:
            docs: List of documents

        Returns:
            Formatted context string
        """
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            formatted.append(f"[Document {i}] (Source: {source})\n{doc.page_content}")

        return "\n\n".join(formatted)

    def query(
        self,
        question: str,
        search_type: str = None,
        top_k: int = None,
        rerank: bool = None,
        return_sources: bool = True,
    ) -> dict[str, Any]:
        """Query the RAG system.

        Args:
            question: User question
            search_type: Type of search to use
            top_k: Number of documents to retrieve
            rerank: Whether to apply reranking
            return_sources: Whether to return source documents

        Returns:
            Dictionary with answer and optional sources
        """
        # Retrieve relevant documents
        results = self.search_with_reranking.search(
            query=question,
            search_type=search_type,
            top_k_final=top_k or settings.top_k_final,
            rerank=rerank,
        )

        # Extract documents and scores
        documents = [doc for doc, _ in results]
        scores = [score for _, score in results]

        # Generate answer
        answer = self.chain.invoke(
            {
                "question": question,
                "documents": documents,
            }
        )

        # Prepare response
        response = {
            "question": question,
            "answer": answer,
        }

        if return_sources:
            response["sources"] = [
                {
                    "content": doc.page_content[:200] + "...",  # Truncate for display
                    "metadata": doc.metadata,
                    "relevance_score": float(score),
                }
                for doc, score in zip(documents, scores)
            ]
            response["num_sources"] = len(documents)

        return response

    def query_with_chat_history(
        self,
        question: str,
        chat_history: list[dict[str, str]],
        **kwargs,
    ) -> dict[str, Any]:
        """Query with chat history for conversational RAG.

        Args:
            question: User question
            chat_history: List of previous messages
            **kwargs: Additional arguments for query

        Returns:
            Response dictionary
        """
        # Create a contextualized question using chat history
        if chat_history:
            history_context = "\n".join(
                [
                    f"User: {msg['question']}\nAssistant: {msg['answer']}"
                    for msg in chat_history[-3:]  # Last 3 turns
                ]
            )
            contextualized_question = (
                f"Previous conversation:\n{history_context}\n\nCurrent question: {question}"
            )
        else:
            contextualized_question = question

        # Use the contextualized question for retrieval but original for display
        response = self.query(contextualized_question, **kwargs)
        response["question"] = question  # Replace with original question

        return response

    def batch_query(
        self,
        questions: list[str],
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Process multiple questions in batch.

        Args:
            questions: List of questions
            **kwargs: Additional arguments for query

        Returns:
            List of response dictionaries
        """
        return [self.query(q, **kwargs) for q in questions]
