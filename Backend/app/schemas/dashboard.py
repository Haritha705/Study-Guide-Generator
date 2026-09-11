"""Dashboard and analytics schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ActivityItem(BaseModel):
    """Single activity entry for the dashboard feed."""
    action: str = Field(..., description="Action type, e.g. 'quiz_completed', 'pack_generated'.")
    title: str = Field(..., description="Human-readable description.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[float] = Field(None, description="Score if action is quiz-related.")


class WeakTopicSummary(BaseModel):
    """Aggregated weak topic across all quiz attempts."""
    topic: str
    occurrences: int = Field(..., ge=1, description="How many times this appeared as weak.")
    average_accuracy: float = Field(..., ge=0.0, le=100.0)


class DashboardStats(BaseModel):
    """Overall dashboard statistics for a user."""
    total_packs: int = Field(0, ge=0, description="Total study packs generated.")
    total_quizzes: int = Field(0, ge=0, description="Total quizzes attempted.")
    average_score: float = Field(0.0, ge=0.0, le=100.0, description="Average quiz score.")
    best_score: float = Field(0.0, ge=0.0, le=100.0, description="Highest quiz score.")
    weak_topics: List[WeakTopicSummary] = Field(
        default_factory=list,
        description="Persistent weak topics across attempts."
    )
    recent_activity: List[ActivityItem] = Field(
        default_factory=list,
        description="Recent user activity feed."
    )
