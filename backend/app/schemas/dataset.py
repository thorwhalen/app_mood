from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from ..models.dataset import DatasetStatus


class DatasetCreate(BaseModel):
    """Schema for creating/generating a dataset."""

    num_examples: int = Field(
        default=20, ge=5, le=100, description="Number of examples to generate"
    )
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")


class DatasetExampleResponse(BaseModel):
    """Schema for dataset example response."""

    id: str
    text: str
    score: float
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetResponse(BaseModel):
    """Schema for dataset response."""

    id: str
    mood_id: str
    num_examples: int
    openai_model_used: Optional[str] = None
    status: DatasetStatus
    error_message: Optional[str] = None
    generated_at: datetime
    examples: Optional[List[DatasetExampleResponse]] = None

    class Config:
        from_attributes = True
