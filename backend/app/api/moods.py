from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Mood
from ..schemas import MoodCreate, MoodUpdate, MoodResponse

router = APIRouter()


@router.post("/", response_model=MoodResponse, status_code=status.HTTP_201_CREATED)
def create_mood(mood_data: MoodCreate, db: Session = Depends(get_db)):
    """Create a new mood definition."""
    mood = Mood(
        name=mood_data.name,
        description=mood_data.description,
        attribute_definition=mood_data.attribute_definition,
    )
    db.add(mood)
    db.commit()
    db.refresh(mood)
    return mood


@router.get("/", response_model=List[MoodResponse])
def list_moods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all mood definitions."""
    moods = db.query(Mood).offset(skip).limit(limit).all()
    return moods


@router.get("/{mood_id}", response_model=MoodResponse)
def get_mood(mood_id: str, db: Session = Depends(get_db)):
    """Get a specific mood by ID."""
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Mood {mood_id} not found"
        )
    return mood


@router.put("/{mood_id}", response_model=MoodResponse)
def update_mood(mood_id: str, mood_data: MoodUpdate, db: Session = Depends(get_db)):
    """Update a mood definition."""
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Mood {mood_id} not found"
        )

    update_data = mood_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mood, field, value)

    db.commit()
    db.refresh(mood)
    return mood


@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mood(mood_id: str, db: Session = Depends(get_db)):
    """Delete a mood definition."""
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Mood {mood_id} not found"
        )

    db.delete(mood)
    db.commit()
    return None
