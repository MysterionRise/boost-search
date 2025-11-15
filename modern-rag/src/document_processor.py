"""Document processing and chunking utilities."""

from typing import List, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .config import settings


class DocumentProcessor:
    """Handles document loading, processing, and chunking."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        """Initialize document processor.

        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def load_file(self, file_path: str) -> List[Document]:
        """Load a single file.

        Args:
            file_path: Path to the file

        Returns:
            List of Document objects
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        loaders = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".md": UnstructuredMarkdownLoader,
            ".docx": Docx2txtLoader,
        }

        loader_class = loaders.get(suffix)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {suffix}")

        loader = loader_class(file_path)
        documents = loader.load()

        # Add source metadata
        for doc in documents:
            doc.metadata["source"] = file_path
            doc.metadata["file_type"] = suffix[1:]  # Remove the dot

        return documents

    def load_directory(
        self,
        directory_path: str,
        glob_pattern: str = "**/*",
        file_types: Optional[List[str]] = None,
    ) -> List[Document]:
        """Load all supported files from a directory.

        Args:
            directory_path: Path to directory
            glob_pattern: Glob pattern for file matching
            file_types: List of file extensions to include (e.g., ['.pdf', '.txt'])

        Returns:
            List of Document objects
        """
        directory = Path(directory_path)
        file_types = file_types or [".pdf", ".txt", ".md", ".docx"]

        all_documents = []
        for file_path in directory.glob(glob_pattern):
            if file_path.is_file() and file_path.suffix.lower() in file_types:
                try:
                    documents = self.load_file(str(file_path))
                    all_documents.extend(documents)
                    print(f"Loaded: {file_path.name}")
                except Exception as e:
                    print(f"Error loading {file_path.name}: {e}")

        return all_documents

    def chunk_documents(
        self,
        documents: List[Document],
        add_context: bool = False,
    ) -> List[Document]:
        """Split documents into chunks.

        Args:
            documents: List of documents to chunk
            add_context: Whether to add document context to each chunk

        Returns:
            List of chunked documents
        """
        chunks = self.text_splitter.split_documents(documents)

        # Optionally add context (Anthropic's contextual retrieval approach)
        if add_context:
            chunks = self._add_contextual_info(chunks)

        return chunks

    def _add_contextual_info(self, chunks: List[Document]) -> List[Document]:
        """Add contextual information to chunks.

        This implements a simplified version of Anthropic's contextual retrieval,
        where each chunk is prepended with document-level context.

        Args:
            chunks: List of document chunks

        Returns:
            Chunks with added context
        """
        # Group chunks by source
        chunks_by_source = {}
        for chunk in chunks:
            source = chunk.metadata.get("source", "unknown")
            if source not in chunks_by_source:
                chunks_by_source[source] = []
            chunks_by_source[source].append(chunk)

        # Add context to each chunk
        contextualized_chunks = []
        for source, source_chunks in chunks_by_source.items():
            # Create a simple context (in production, use LLM to generate better context)
            doc_context = f"Document: {Path(source).name}\n"

            for chunk in source_chunks:
                # Prepend context to chunk
                chunk.page_content = doc_context + chunk.page_content
                chunk.metadata["contextualized"] = True
                contextualized_chunks.append(chunk)

        return contextualized_chunks

    def process_files(
        self,
        file_paths: List[str] = None,
        directory_path: str = None,
        add_context: bool = False,
    ) -> List[Document]:
        """Process files and return chunked documents.

        Args:
            file_paths: List of file paths to process
            directory_path: Directory path to process
            add_context: Whether to add contextual information

        Returns:
            List of processed and chunked documents
        """
        documents = []

        if file_paths:
            for file_path in file_paths:
                docs = self.load_file(file_path)
                documents.extend(docs)

        if directory_path:
            docs = self.load_directory(directory_path)
            documents.extend(docs)

        if not documents:
            raise ValueError("No documents loaded")

        print(f"Loaded {len(documents)} documents")

        # Chunk documents
        chunks = self.chunk_documents(documents, add_context=add_context)
        print(f"Created {len(chunks)} chunks")

        return chunks
