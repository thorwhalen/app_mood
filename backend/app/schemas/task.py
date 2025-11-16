from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any
from ..models.task import TaskStatus, TaskType


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: str
    task_type: TaskType
    status: TaskStatus
    progress: int
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
