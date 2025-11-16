from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UsageQuotaResponse(BaseModel):
    """Schema for usage quota response."""

    id: str
    user_id: str

    # Limits
    analyses_limit: int
    datasets_limit: int
    model_trainings_limit: int

    # Current usage
    analyses_used: int
    datasets_used: int
    model_trainings_used: int

    # Remaining
    analyses_remaining: int
    datasets_remaining: int
    model_trainings_remaining: int

    # Period
    current_period_start: datetime
    current_period_end: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsageQuotaUpdate(BaseModel):
    """Schema for updating usage quota limits (admin only)."""

    analyses_limit: Optional[int] = None
    datasets_limit: Optional[int] = None
    model_trainings_limit: Optional[int] = None
