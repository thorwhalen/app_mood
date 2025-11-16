from sqlalchemy import Column, String, Integer, Text, DateTime, Enum, JSON
from datetime import datetime
import uuid
import enum
from ..database import Base


class TaskStatus(str, enum.Enum):
    """Background task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, enum.Enum):
    """Background task types."""

    GENERATE_DATASET = "generate_dataset"
    TRAIN_MODEL = "train_model"
    BATCH_ANALYSIS = "batch_analysis"


class Task(Base):
    """Background task tracking model."""

    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
