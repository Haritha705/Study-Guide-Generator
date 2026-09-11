"""RAG text chunker — splits documents into overlapping semantic chunks."""

import logging
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 200
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Split source text into overlapping chunks for embedding and retrieval.

    Uses RecursiveCharacterTextSplitter with semantic-aware separators
    (paragraph breaks > line breaks > sentences > words).

    Args:
        text: The full source text to chunk.
        chunk_size: Target size of each chunk in characters (500–1000 recommended).
        chunk_overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to chunker.")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=SEPARATORS,
        is_separator_regex=False,
    )

    chunks = splitter.split_text(text)
    logger.info(f"Text chunked: {len(text)} chars → {len(chunks)} chunks "
                f"(size={chunk_size}, overlap={chunk_overlap})")
    return chunks
