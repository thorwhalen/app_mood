from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class AnalysisCreate(BaseModel):
    """Schema for creating a single analysis."""

    mood_id: str
    text: str = Field(..., min_length=1, description="Text to analyze")


class AnalysisBatchCreate(BaseModel):
    """Schema for batch analysis."""

    mood_id: str
    texts: List[str] = Field(..., min_items=1, max_items=1000, description="Texts to analyze")


class AnalysisResponse(BaseModel):
    """Schema for analysis response."""

    id: str
    mood_id: str
    model_id: Optional[str] = None
    user_id: Optional[str] = None
    input_text: str
    score: float
    analyzed_at: datetime

    class Config:
        from_attributes = True


class HeadlineAnalysisResponse(BaseModel):
    """Schema for financial headline analysis response."""

    headline: str
    sentiment_score: float
    source: Optional[str] = None
