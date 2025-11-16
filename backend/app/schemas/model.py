from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from ..models.model import ModelType


class TrainModelRequest(BaseModel):
    """Schema for triggering model training."""

    dataset_id: str


class MLModelResponse(BaseModel):
    """Schema for ML model response."""

    id: str
    mood_id: str
    model_type: ModelType
    metrics: Optional[Dict[str, Any]] = None
    is_selected: bool
    trained_at: datetime

    class Config:
        from_attributes = True
