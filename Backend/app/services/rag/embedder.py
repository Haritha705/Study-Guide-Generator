"""RAG embedder — generates vector embeddings for text chunks."""

import logging
from typing import List

from langsmith import traceable

from app.core.exceptions import RAGRetrievalError

logger = logging.getLogger(__name__)


@traceable(name="generate_embeddings")
def generate_embeddings(chunks: List[str], embeddings_model=None) -> List[List[float]]:
    """
    Generate vector embeddings for a list of text chunks.

    Uses MistralAIEmbeddings by default for cost-efficient embedding generation.

    Args:
        chunks: List of text strings to embed.
        embeddings_model: Optional pre-configured embeddings model.
                          If None, uses MistralAIEmbeddings.

    Returns:
        List of embedding vectors (each is a list of floats).

    Raises:
        RAGRetrievalError: If embedding generation fails.
    """
    if not chunks:
        logger.warning("No chunks provided for embedding.")
        return []

    try:
        if embeddings_model is None:
            from app.services.ai_pipeline import get_embeddings_model
            embeddings_model = get_embeddings_model()

        vectors = embeddings_model.embed_documents(chunks)
        logger.info(f"Generated {len(vectors)} embeddings (dim={len(vectors[0]) if vectors else 0})")
        return vectors

    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise RAGRetrievalError(f"Failed to generate embeddings: {str(e)}")


@traceable(name="embed_query")
def embed_query(query: str, embeddings_model=None) -> List[float]:
    """
    Generate an embedding vector for a single query string.

    Args:
        query: The query text to embed.
        embeddings_model: Optional pre-configured embeddings model.

    Returns:
        Embedding vector as a list of floats.
    """
    try:
        if embeddings_model is None:
            from app.services.ai_pipeline import get_embeddings_model
            embeddings_model = get_embeddings_model()

        vector = embeddings_model.embed_query(query)
        return vector

    except Exception as e:
        logger.error(f"Query embedding failed: {e}")
        raise RAGRetrievalError(f"Failed to embed query: {str(e)}")
