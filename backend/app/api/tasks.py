from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Task
from ..schemas import TaskResponse

router = APIRouter()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """Get the status of a background task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found"
        )
    return task
