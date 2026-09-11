"""User ORM model."""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.base import Base, IDMixin, TimestampMixin


class User(Base, IDMixin, TimestampMixin):
    """Represents a registered user of StudyPack AI."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)

    # Relationships
    studypacks = relationship("StudyPack", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
