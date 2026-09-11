"""RAG AI Tutor request and response schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional


class TutorRequest(BaseModel):
    """Schema for asking the AI tutor a question."""
    question: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="The student's question."
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID to maintain conversation context."
    )
    context_id: Optional[str] = Field(
        None,
        description="ID of the study pack to ground answers against."
    )


class SourceChunk(BaseModel):
    """A retrieved context chunk used to ground the answer."""
    text: str = Field(..., description="The retrieved text snippet.")
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score."
    )


class TutorResponse(BaseModel):
    """Response from the AI tutor."""
    answer: str = Field(..., description="The tutor's grounded answer.")
    sources: List[SourceChunk] = Field(
        default_factory=list,
        description="Context chunks used to generate the answer."
    )
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the answer."
    )
    follow_up_suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up questions."
    )
