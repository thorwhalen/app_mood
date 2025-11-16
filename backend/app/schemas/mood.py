from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MoodBase(BaseModel):
    """Base mood schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the mood")
    description: str = Field(..., min_length=1, description="Description of the mood")
    attribute_definition: str = Field(
        ..., min_length=1, description="Semantic attribute definition for the mood"
    )


class MoodCreate(MoodBase):
    """Schema for creating a mood."""

    pass


class MoodUpdate(BaseModel):
    """Schema for updating a mood."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    attribute_definition: Optional[str] = Field(None, min_length=1)


class MoodResponse(MoodBase):
    """Schema for mood response."""

    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
