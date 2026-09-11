"""QuizAttempt ORM model."""

from sqlalchemy import Column, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base, IDMixin, TimestampMixin


class QuizAttempt(Base, IDMixin, TimestampMixin):
    """
    Records a single quiz attempt by a user on a specific study pack.
    Stores the submitted answers, computed score, and identified weak topics.
    """

    __tablename__ = "quiz_attempts"

    studypack_id = Column(Integer, ForeignKey("studypacks.id"), nullable=False, index=True)
    score = Column(Float, nullable=False, default=0.0)
    correct = Column(Integer, nullable=False, default=0)
    wrong = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=20)

    # JSON columns for flexible storage
    answers = Column(JSON, nullable=False, comment="Map of question_id -> selected_answer")
    weak_topics = Column(JSON, nullable=True, comment="List of weak topic strings")
    difficulty_breakdown = Column(JSON, nullable=True, comment="Dict of difficulty -> accuracy")
    missed_question_ids = Column(JSON, nullable=True, comment="List of incorrectly answered question IDs")

    # Relationships
    studypack = relationship("StudyPack", back_populates="attempts")

    def __repr__(self) -> str:
        return f"<QuizAttempt(id={self.id}, score={self.score}, studypack_id={self.studypack_id})>"
