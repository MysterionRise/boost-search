"""Tests for document processor module."""


import pytest
from langchain_core.documents import Document

from src.document_processor import DocumentProcessor


@pytest.mark.unit
def test_document_processor_init(mock_settings):
    """Test DocumentProcessor initialization."""
    processor = DocumentProcessor(chunk_size=300, chunk_overlap=50)

    assert processor.chunk_size == 300
    assert processor.chunk_overlap == 50
    assert processor.text_splitter is not None


@pytest.mark.unit
def test_chunk_documents(sample_documents):
    """Test document chunking."""
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)

    chunks = processor.chunk_documents(sample_documents)

    assert isinstance(chunks, list)
    assert len(chunks) >= len(sample_documents)  # May create multiple chunks
    assert all(isinstance(chunk, Document) for chunk in chunks)


@pytest.mark.unit
def test_chunk_documents_with_context(sample_documents):
    """Test document chunking with contextual information."""
    processor = DocumentProcessor()

    chunks = processor.chunk_documents(sample_documents, add_context=True)

    assert len(chunks) > 0
    # Check that context was added
    for chunk in chunks:
        assert "Document:" in chunk.page_content
        assert chunk.metadata.get("contextualized") is True


@pytest.mark.unit
def test_chunk_preserves_metadata(sample_documents):
    """Test that chunking preserves metadata."""
    processor = DocumentProcessor(chunk_size=100)

    chunks = processor.chunk_documents(sample_documents)

    # Check metadata is preserved
    for chunk in chunks:
        assert "source" in chunk.metadata


@pytest.mark.unit
def test_process_files_empty():
    """Test processing with no files raises error."""
    processor = DocumentProcessor()

    with pytest.raises(ValueError, match="No documents loaded"):
        processor.process_files()


@pytest.mark.unit
def test_load_file_unsupported_type(tmp_path):
    """Test loading unsupported file type."""
    processor = DocumentProcessor()

    # Create unsupported file
    unsupported_file = tmp_path / "test.xyz"
    unsupported_file.write_text("test content")

    with pytest.raises(ValueError, match="Unsupported file type"):
        processor.load_file(str(unsupported_file))
