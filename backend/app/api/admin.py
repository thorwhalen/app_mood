"""Admin endpoints for system management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List, Dict
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User, Mood, Dataset, MLModel, Analysis, UsageQuota
from ..schemas import UsageQuotaUpdate
from ..utils.dependencies import get_current_user
from ..services.cache_service import get_cached_admin_stats, cache_admin_stats, invalidate_admin_stats
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
    """Get system-wide statistics with Redis caching (admin only)."""
    from datetime import datetime, timedelta

    # Try to get from cache first (5 minute TTL)
    cached = get_cached_admin_stats()
    if cached:
        return SystemStats(**cached)

    # Cache miss - compute stats
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

    stats = {
        "total_users": total_users,
        "total_moods": total_moods,
        "total_datasets": total_datasets,
        "total_models": total_models,
        "total_analyses": total_analyses,
        "analyses_today": analyses_today,
        "analyses_this_month": analyses_this_month,
    }

    # Cache the stats (5 minutes)
    cache_admin_stats(stats, ttl=300)

    return SystemStats(**stats)


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


@router.get("/analytics/analyses-over-time", response_model=Dict)
def get_analyses_over_time(
    days: int = 30,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get analyses count over time for the past N days (admin only)."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query analyses grouped by date
    results = db.query(
        cast(Analysis.analyzed_at, Date).label('date'),
        func.count(Analysis.id).label('count')
    ).filter(
        Analysis.analyzed_at >= start_date
    ).group_by(
        cast(Analysis.analyzed_at, Date)
    ).order_by(
        cast(Analysis.analyzed_at, Date)
    ).all()

    # Convert to dict with all dates (fill missing dates with 0)
    data = {}
    current_date = start_date.date()
    while current_date <= end_date.date():
        data[current_date.isoformat()] = 0
        current_date += timedelta(days=1)

    # Fill in actual counts
    for result in results:
        data[result.date.isoformat()] = result.count

    return {
        "labels": list(data.keys()),
        "values": list(data.values()),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }


@router.get("/analytics/user-growth", response_model=Dict)
def get_user_growth(
    days: int = 30,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user registration growth over time (admin only)."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Query user registrations grouped by date
    results = db.query(
        cast(User.created_at, Date).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date
    ).group_by(
        cast(User.created_at, Date)
    ).order_by(
        cast(User.created_at, Date)
    ).all()

    # Convert to cumulative count
    data = {}
    current_date = start_date.date()
    cumulative = 0

    # Get count before start date
    previous_count = db.query(func.count(User.id)).filter(
        User.created_at < start_date
    ).scalar()
    cumulative = previous_count

    while current_date <= end_date.date():
        # Find count for this date
        day_count = next((r.count for r in results if r.date == current_date), 0)
        cumulative += day_count
        data[current_date.isoformat()] = cumulative
        current_date += timedelta(days=1)

    return {
        "labels": list(data.keys()),
        "values": list(data.values()),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }


@router.get("/analytics/top-moods", response_model=Dict)
def get_top_moods(
    limit: int = 10,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get most popular moods by analysis count (admin only)."""
    results = db.query(
        Mood.name,
        func.count(Analysis.id).label('count')
    ).join(
        Analysis, Analysis.mood_id == Mood.id
    ).group_by(
        Mood.id, Mood.name
    ).order_by(
        func.count(Analysis.id).desc()
    ).limit(limit).all()

    return {
        "labels": [r.name for r in results],
        "values": [r.count for r in results]
    }
