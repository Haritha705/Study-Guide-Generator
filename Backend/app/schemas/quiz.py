"""Quiz submission and evaluation schemas."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class QuizSubmission(BaseModel):
    """Schema for submitting quiz answers."""
    studypack_id: Optional[str] = Field(
        None,
        description="ID of the study pack this quiz belongs to."
    )
    answers: Dict[int, str] = Field(
        ...,
        description="Map of question ID to selected answer string."
    )
    mcqs: Optional[List[dict]] = Field(
        None,
        description="The original MCQ items for server-side grading. "
                    "Each dict should match MCQItem schema."
    )
    current_difficulty: str = Field(
        "Medium",
        pattern="^(Easy|Medium|Hard)$",
        description="Difficulty of the quiz being submitted.",
    )


class TopicPerformance(BaseModel):
    """Performance breakdown for a single topic."""
    topic: str
    score: float = Field(..., ge=0.0, le=100.0)
    total_questions: int
    correct_answers: int


class DifficultyBreakdown(BaseModel):
    """Score breakdown by difficulty level."""
    easy: float = Field(0.0, ge=0.0, le=100.0)
    medium: float = Field(0.0, ge=0.0, le=100.0)
    hard: float = Field(0.0, ge=0.0, le=100.0)


class QuizResult(BaseModel):
    """Graded quiz result with analytics."""
    score: float = Field(..., ge=0.0, le=100.0, description="Overall percentage score.")
    weak_topics: List[str] = Field(
        default_factory=list,
        description="Topics where accuracy is below 60%."
    )
    topic_performance: Dict[str, TopicPerformance] = Field(
        default_factory=dict,
        description="Per-topic accuracy breakdown."
    )
    difficulty_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Accuracy percentage per difficulty level."
    )
    missed_question_ids: List[int] = Field(
        default_factory=list,
        description="IDs of incorrectly answered questions."
    )
    next_difficulty: str = Field(
        ...,
        pattern="^(Easy|Medium|Hard)$",
        description="Difficulty to use for the next quiz.",
    )
