from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Dataset, DatasetExample, Mood
from ..schemas import DatasetCreate, DatasetResponse, DatasetExampleResponse
from ..services.dataset_service import generate_dataset_task

router = APIRouter()


@router.post("/{mood_id}/generate", response_model=DatasetResponse, status_code=status.HTTP_202_ACCEPTED)
def generate_dataset(
    mood_id: str,
    dataset_data: DatasetCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Generate a training dataset for a mood."""
    # Check if mood exists
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Mood {mood_id} not found"
        )

    # Create dataset record
    dataset = Dataset(
        mood_id=mood_id,
        num_examples=dataset_data.num_examples,
        openai_model_used=dataset_data.openai_model,
        status="pending",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Trigger background task
    background_tasks.add_task(generate_dataset_task, dataset.id, mood.attribute_definition)

    return dataset


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get a dataset by ID."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {dataset_id} not found"
        )
    return dataset


@router.get("/{dataset_id}/examples", response_model=List[DatasetExampleResponse])
def get_dataset_examples(
    dataset_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get examples from a dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {dataset_id} not found"
        )

    examples = (
        db.query(DatasetExample)
        .filter(DatasetExample.dataset_id == dataset_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return examples


@router.get("/mood/{mood_id}", response_model=List[DatasetResponse])
def list_mood_datasets(mood_id: str, db: Session = Depends(get_db)):
    """List all datasets for a mood."""
    datasets = db.query(Dataset).filter(Dataset.mood_id == mood_id).all()
    return datasets
