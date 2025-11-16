from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


class Mood(Base):
    """Mood (semantic attribute) definition model."""

    __tablename__ = "moods"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    attribute_definition = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="moods")
    datasets = relationship("Dataset", back_populates="mood", cascade="all, delete-orphan")
    models = relationship("MLModel", back_populates="mood", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="mood", cascade="all, delete-orphan")
