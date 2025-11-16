from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..database import Base


class ModelType(str, enum.Enum):
    """ML model types."""

    NUMERICAL_REGRESSION = "numerical_regression"
    BINARY_CLASSIFICATION = "binary_classification"
    ORDINAL_REGRESSION = "ordinal_regression"


class MLModel(Base):
    """Trained ML model metadata."""

    __tablename__ = "ml_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mood_id = Column(String, ForeignKey("moods.id", ondelete="CASCADE"), nullable=False)
    model_type = Column(Enum(ModelType), nullable=False)
    metrics = Column(JSON, nullable=True)  # {"spearman": 0.85, "f1": 0.92, etc.}
    file_path = Column(String(500), nullable=False)
    is_selected = Column(Boolean, default=False)
    trained_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mood = relationship("Mood", back_populates="models")
    analyses = relationship("Analysis", back_populates="model")
