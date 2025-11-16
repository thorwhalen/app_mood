from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Analysis, MLModel, Mood
from ..schemas import AnalysisCreate, AnalysisResponse, AnalysisBatchCreate, HeadlineAnalysisResponse
from ..services.analysis_service import analyze_text, analyze_batch_task, get_financial_headlines

router = APIRouter()


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def create_analysis(analysis_data: AnalysisCreate, db: Session = Depends(get_db)):
    """Analyze a single text with a mood."""
    # Check if mood exists
    mood = db.query(Mood).filter(Mood.id == analysis_data.mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood {analysis_data.mood_id} not found",
        )

    # Get selected model
    model = (
        db.query(MLModel)
        .filter(MLModel.mood_id == analysis_data.mood_id, MLModel.is_selected == True)
        .first()
    )

    if not model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No model selected for mood {analysis_data.mood_id}. Please train and select a model first.",
        )

    # Perform analysis
    try:
        score = analyze_text(model.file_path, analysis_data.text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )

    # Save analysis
    analysis = Analysis(
        mood_id=analysis_data.mood_id,
        model_id=model.id,
        input_text=analysis_data.text,
        score=score,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


@router.post("/batch", status_code=status.HTTP_202_ACCEPTED)
def create_batch_analysis(
    batch_data: AnalysisBatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Analyze multiple texts in batch."""
    # Check if mood exists
    mood = db.query(Mood).filter(Mood.id == batch_data.mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood {batch_data.mood_id} not found",
        )

    # Get selected model
    model = (
        db.query(MLModel)
        .filter(MLModel.mood_id == batch_data.mood_id, MLModel.is_selected == True)
        .first()
    )

    if not model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No model selected for mood {batch_data.mood_id}",
        )

    # Trigger background task
    background_tasks.add_task(
        analyze_batch_task, batch_data.mood_id, model.id, batch_data.texts
    )

    return {"message": "Batch analysis started", "num_texts": len(batch_data.texts)}


@router.get("/", response_model=List[AnalysisResponse])
def list_analyses(
    mood_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """List analysis history."""
    query = db.query(Analysis)

    if mood_id:
        query = query.filter(Analysis.mood_id == mood_id)

    analyses = query.order_by(Analysis.analyzed_at.desc()).offset(skip).limit(limit).all()
    return analyses


@router.get("/headlines", response_model=List[HeadlineAnalysisResponse])
def analyze_headlines(db: Session = Depends(get_db)):
    """Analyze current financial headlines (quick-start feature)."""
    try:
        results = get_financial_headlines()
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze headlines: {str(e)}",
        )
