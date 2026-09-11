"""RAG vector store — manages in-memory vector storage and similarity search."""

import logging
from typing import List, Optional, Tuple

from langchain_community.vectorstores import InMemoryVectorStore
from langsmith import traceable

from app.core.exceptions import RAGRetrievalError

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages an in-memory vector store for RAG retrieval.

    Supports adding documents, searching by similarity, and clearing the store.
    Uses LangChain's InMemoryVectorStore backed by MistralAI embeddings.
    """

    def __init__(self):
        self._store: Optional[InMemoryVectorStore] = None
        self._chunks: List[str] = []

    @property
    def is_initialized(self) -> bool:
        return self._store is not None

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    @traceable(name="vector_store_build")
    def build_from_chunks(self, chunks: List[str], embeddings_model=None) -> None:
        """
        Build the vector store from a list of text chunks.

        Args:
            chunks: List of text chunks to store.
            embeddings_model: Optional embeddings model. If None, uses default.

        Raises:
            RAGRetrievalError: If store creation fails.
        """
        if not chunks:
            logger.warning("No chunks provided to build vector store.")
            return

        try:
            if embeddings_model is None:
                from app.services.ai_pipeline import get_embeddings_model
                embeddings_model = get_embeddings_model()

            self._store = InMemoryVectorStore.from_texts(chunks, embeddings_model)
            self._chunks = chunks
            logger.info(f"Vector store built with {len(chunks)} chunks.")

        except Exception as e:
            logger.error(f"Failed to build vector store: {e}")
            raise RAGRetrievalError(f"Vector store creation failed: {str(e)}")

    @traceable(name="vector_store_search")
    def similarity_search(self, query: str, k: int = 4) -> List[Tuple[str, float]]:
        """
        Search for the top-k most similar chunks to the query.

        Args:
            query: The search query.
            k: Number of results to return.

        Returns:
            List of (chunk_text, relevance_score) tuples.

        Raises:
            RAGRetrievalError: If search fails or store is not initialized.
        """
        if not self.is_initialized:
            raise RAGRetrievalError("Vector store is not initialized. Upload a document first.")

        try:
            results = self._store.similarity_search_with_score(query, k=k)
            scored = [(doc.page_content, score) for doc, score in results]
            logger.info(f"Similarity search: query='{query[:50]}...' → {len(scored)} results")
            return scored

        except RAGRetrievalError:
            raise
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise RAGRetrievalError(f"Search failed: {str(e)}")

    def get_retriever(self, k: int = 4):
        """
        Return a LangChain retriever interface for the vector store.

        Args:
            k: Number of documents to retrieve per query.

        Returns:
            A LangChain retriever object.
        """
        if not self.is_initialized:
            raise RAGRetrievalError("Vector store is not initialized.")
        return self._store.as_retriever(search_kwargs={"k": k})

    def clear(self) -> None:
        """Clear the vector store and reset state."""
        self._store = None
        self._chunks = []
        logger.info("Vector store cleared.")


# Global singleton instance
vector_store_manager = VectorStoreManager()
