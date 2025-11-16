from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..database import Base


class DatasetStatus(str, enum.Enum):
    """Dataset generation status."""

    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Dataset(Base):
    """Training dataset model."""

    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mood_id = Column(String, ForeignKey("moods.id", ondelete="CASCADE"), nullable=False)
    num_examples = Column(Integer, nullable=False, default=0)
    openai_model_used = Column(String(100), nullable=True)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.PENDING)
    error_message = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mood = relationship("Mood", back_populates="datasets")
    examples = relationship("DatasetExample", back_populates="dataset", cascade="all, delete-orphan")


class DatasetExample(Base):
    """Individual training example in a dataset."""

    __tablename__ = "dataset_examples"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="examples")
