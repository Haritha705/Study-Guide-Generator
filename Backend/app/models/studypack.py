"""StudyPack ORM model."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base, IDMixin, TimestampMixin


class StudyPack(Base, IDMixin, TimestampMixin):
    """
    Represents a generated study pack.
    Stores the source text and the full AI-generated output as JSON.
    """

    __tablename__ = "studypacks"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(200), nullable=True, default="Untitled Study Pack")
    source_text = Column(Text, nullable=False)
    source_hash = Column(String(64), nullable=True, index=True, comment="SHA-256 of source_text for deduplication")
    page_count = Column(Integer, nullable=True)

    # The full generated output (notes, mcqs, glossary, saqs, study order)
    generated_output = Column(JSON, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="studypacks")
    attempts = relationship("QuizAttempt", back_populates="studypack", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StudyPack(id={self.id}, title='{self.title}')>"
