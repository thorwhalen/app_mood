"""Service for managing usage quotas with Redis caching."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import UsageQuota, User
from .cache_service import (
    get_cached_user_quota,
    cache_user_quota,
    invalidate_user_quota
)


def get_or_create_quota(user: User, db: Session, use_cache: bool = True) -> UsageQuota:
    """
    Get or create usage quota for a user with Redis caching.

    Args:
        user: User object
        db: Database session
        use_cache: Whether to use Redis cache (default: True)
    """
    # Try cache first
    if use_cache:
        cached = get_cached_user_quota(user.id)
        if cached:
            # Reconstruct quota object from cache
            quota = UsageQuota(**cached)
            quota.user_id = user.id  # Ensure user_id is set
            return quota

    # Cache miss or cache disabled - query database
    quota = db.query(UsageQuota).filter(UsageQuota.user_id == user.id).first()

    if not quota:
        # Create default quota for user
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        now = datetime.utcnow()
        period_end = now + relativedelta(months=1)
        quota = UsageQuota(
            user_id=user.id,
            analyses_limit=1000,
            datasets_limit=10,
            model_trainings_limit=5,
            current_period_start=now,
            current_period_end=period_end,
        )
        db.add(quota)
        db.commit()
        db.refresh(quota)

    # Cache the quota (60 second TTL since it changes frequently)
    if use_cache:
        quota_dict = {
            "id": quota.id,
            "analyses_limit": quota.analyses_limit,
            "datasets_limit": quota.datasets_limit,
            "model_trainings_limit": quota.model_trainings_limit,
            "analyses_used": quota.analyses_used,
            "datasets_used": quota.datasets_used,
            "model_trainings_used": quota.model_trainings_used,
            "current_period_start": quota.current_period_start.isoformat() if quota.current_period_start else None,
            "current_period_end": quota.current_period_end.isoformat() if quota.current_period_end else None,
        }
        cache_user_quota(user.id, quota_dict, ttl=60)

    return quota


def check_quota(user: User, resource: str, db: Session):
    """
    Check if user has quota remaining for a resource.

    Raises HTTPException if quota exceeded.
    Uses Redis cache for faster checks.
    """
    quota = get_or_create_quota(user, db, use_cache=True)

    if not quota.is_within_limit(resource):
        limit = getattr(quota, f"{resource}_limit")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Usage quota exceeded for {resource}. Limit: {limit} per month.",
        )


def increment_usage(user: User, resource: str, db: Session):
    """
    Increment usage counter for a resource and invalidate cache.
    """
    quota = get_or_create_quota(user, db, use_cache=False)  # Don't use cache for writes
    quota.increment_usage(resource)
    db.commit()

    # Invalidate cache so next read gets fresh data
    invalidate_user_quota(user.id)
