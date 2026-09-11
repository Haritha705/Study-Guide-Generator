"""RAG retriever — top-k similarity search for tutor grounding."""

import logging
from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from app.services.rag.chunker import chunk_text
from app.services.rag.vector_store import vector_store_manager
from app.core.exceptions import RAGRetrievalError

logger = logging.getLogger(__name__)

# Number of context chunks to retrieve per query
DEFAULT_TOP_K = 4


@traceable(name="rag_index_document")
def index_document(text: str) -> int:
    """
    Chunk and index a document into the vector store for later retrieval.

    Args:
        text: Full document text to index.

    Returns:
        Number of chunks indexed.
    """
    chunks = chunk_text(text)
    if not chunks:
        logger.warning("No chunks produced from document.")
        return 0

    vector_store_manager.build_from_chunks(chunks)
    return len(chunks)


@traceable(name="rag_retrieve_context")
def retrieve_context(query: str, top_k: int = DEFAULT_TOP_K) -> str:
    """
    Retrieve relevant context from the vector store for a given query.

    Performs a top-k cosine similarity search and concatenates the
    most relevant chunks into a single context string.

    Args:
        query: The user's question to find context for.
        top_k: Number of chunks to retrieve.

    Returns:
        Concatenated context string from the top-k most relevant chunks.

    Raises:
        RAGRetrievalError: If retrieval fails.
    """
    if not vector_store_manager.is_initialized:
        logger.warning("Vector store not initialized. Returning empty context.")
        return ""

    try:
        results = vector_store_manager.similarity_search(query, k=top_k)

        if not results:
            return ""

        # Concatenate chunks with separators
        context_parts = []
        for i, (chunk_text_content, score) in enumerate(results):
            context_parts.append(
                f"[Source {i + 1} (relevance: {score:.3f})]\n{chunk_text_content}"
            )

        context = "\n\n---\n\n".join(context_parts)
        logger.info(f"Retrieved {len(results)} context chunks for query: '{query[:50]}...'")
        return context

    except RAGRetrievalError:
        raise
    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        raise RAGRetrievalError(f"Retrieval failed: {str(e)}")


def retrieve_context_with_scores(
    query: str, top_k: int = DEFAULT_TOP_K
) -> List[dict]:
    """
    Retrieve context chunks with their relevance scores.

    Args:
        query: The user's question.
        top_k: Number of chunks to retrieve.

    Returns:
        List of dicts with 'text' and 'relevance_score' keys.
    """
    if not vector_store_manager.is_initialized:
        return []

    try:
        results = vector_store_manager.similarity_search(query, k=top_k)
        return [
            {"text": chunk, "relevance_score": round(score, 4)}
            for chunk, score in results
        ]
    except Exception as e:
        logger.error(f"Scored retrieval failed: {e}")
        return []
