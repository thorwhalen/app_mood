"""Admin endpoints for system management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import User, Mood, Dataset, MLModel, Analysis, UsageQuota
from ..schemas import UsageQuotaUpdate
from ..utils.dependencies import get_current_user
from pydantic import BaseModel


router = APIRouter()


# Helper function to check if user is admin
def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify that the current user is an admin."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required.",
        )
    return current_user


class SystemStats(BaseModel):
    """System-wide statistics."""
    total_users: int
    total_moods: int
    total_datasets: int
    total_models: int
    total_analyses: int
    analyses_today: int
    analyses_this_month: int


class UserInfo(BaseModel):
    """User information for admin dashboard."""
    id: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    moods_count: int
    analyses_count: int

    # Usage quota info
    analyses_used: int
    analyses_limit: int
    datasets_used: int
    datasets_limit: int

    class Config:
        from_attributes = True


@router.get("/stats", response_model=SystemStats)
def get_system_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics (admin only)."""
    from datetime import datetime, timedelta

    # Count totals
    total_users = db.query(func.count(User.id)).scalar()
    total_moods = db.query(func.count(Mood.id)).scalar()
    total_datasets = db.query(func.count(Dataset.id)).scalar()
    total_models = db.query(func.count(MLModel.id)).scalar()
    total_analyses = db.query(func.count(Analysis.id)).scalar()

    # Analyses today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    analyses_today = db.query(func.count(Analysis.id)).filter(
        Analysis.analyzed_at >= today_start
    ).scalar()

    # Analyses this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    analyses_this_month = db.query(func.count(Analysis.id)).filter(
        Analysis.analyzed_at >= month_start
    ).scalar()

    return SystemStats(
        total_users=total_users,
        total_moods=total_moods,
        total_datasets=total_datasets,
        total_models=total_models,
        total_analyses=total_analyses,
        analyses_today=analyses_today,
        analyses_this_month=analyses_this_month,
    )


@router.get("/users", response_model=List[UserInfo])
def list_all_users(
    current_admin: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users with their statistics (admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()

    user_infos = []
    for user in users:
        # Count user's resources
        moods_count = db.query(func.count(Mood.id)).filter(Mood.user_id == user.id).scalar()
        analyses_count = db.query(func.count(Analysis.id)).filter(Analysis.user_id == user.id).scalar()

        # Get usage quota
        quota = db.query(UsageQuota).filter(UsageQuota.user_id == user.id).first()

        user_infos.append(UserInfo(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            moods_count=moods_count,
            analyses_count=analyses_count,
            analyses_used=quota.analyses_used if quota else 0,
            analyses_limit=quota.analyses_limit if quota else 0,
            datasets_used=quota.datasets_used if quota else 0,
            datasets_limit=quota.datasets_limit if quota else 0,
        ))

    return user_infos


@router.patch("/users/{user_id}/quota", response_model=dict)
def update_user_quota(
    user_id: str,
    quota_update: UsageQuotaUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a user's usage quota limits (admin only)."""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    # Get or create quota
    quota = db.query(UsageQuota).filter(UsageQuota.user_id == user_id).first()
    if not quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usage quota not found for user {user_id}"
        )

    # Update quota limits
    if quota_update.analyses_limit is not None:
        quota.analyses_limit = quota_update.analyses_limit
    if quota_update.datasets_limit is not None:
        quota.datasets_limit = quota_update.datasets_limit
    if quota_update.model_trainings_limit is not None:
        quota.model_trainings_limit = quota_update.model_trainings_limit

    quota.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Quota updated for user {user.email}"}


@router.patch("/users/{user_id}/activate", response_model=dict)
def toggle_user_active(
    user_id: str,
    active: bool,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Activate or deactivate a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    user.is_active = active
    user.updated_at = datetime.utcnow()
    db.commit()

    status_text = "activated" if active else "deactivated"
    return {"message": f"User {user.email} {status_text}"}
