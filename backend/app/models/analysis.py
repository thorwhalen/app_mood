from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


class Analysis(Base):
    """Sentiment analysis result model."""

    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mood_id = Column(String, ForeignKey("moods.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String, ForeignKey("ml_models.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    input_text = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mood = relationship("Mood", back_populates="analyses")
    model = relationship("MLModel", back_populates="analyses")
    user = relationship("User", back_populates="analyses")
