from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import MLModel, Mood, Dataset
from ..schemas import MLModelResponse, TrainModelRequest
from ..services.training_service import train_models_task

router = APIRouter()


@router.post("/{mood_id}/train", status_code=status.HTTP_202_ACCEPTED)
def train_models(
    mood_id: str,
    train_request: TrainModelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger model training for a mood."""
    # Check if mood exists
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Mood {mood_id} not found"
        )

    # Check if dataset exists and is completed
    dataset = db.query(Dataset).filter(Dataset.id == train_request.dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {train_request.dataset_id} not found",
        )

    if dataset.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset must be completed before training. Current status: {dataset.status}",
        )

    # Trigger background task
    background_tasks.add_task(train_models_task, mood_id, train_request.dataset_id)

    return {"message": "Training started", "mood_id": mood_id}


@router.get("/{model_id}", response_model=MLModelResponse)
def get_model(model_id: str, db: Session = Depends(get_db)):
    """Get a model by ID."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Model {model_id} not found"
        )
    return model


@router.get("/mood/{mood_id}", response_model=List[MLModelResponse])
def list_mood_models(mood_id: str, db: Session = Depends(get_db)):
    """List all models for a mood."""
    models = db.query(MLModel).filter(MLModel.mood_id == mood_id).all()
    return models


@router.post("/{model_id}/select", response_model=MLModelResponse)
def select_model(model_id: str, db: Session = Depends(get_db)):
    """Select a model as the active model for its mood."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Model {model_id} not found"
        )

    # Unselect all other models for this mood
    db.query(MLModel).filter(
        MLModel.mood_id == model.mood_id, MLModel.id != model_id
    ).update({"is_selected": False})

    # Select this model
    model.is_selected = True
    db.commit()
    db.refresh(model)

    return model
