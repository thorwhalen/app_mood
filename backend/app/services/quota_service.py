"""Service for managing usage quotas."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import UsageQuota, User


def get_or_create_quota(user: User, db: Session) -> UsageQuota:
    """Get or create usage quota for a user."""
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

    return quota


def check_quota(user: User, resource: str, db: Session):
    """
    Check if user has quota remaining for a resource.

    Raises HTTPException if quota exceeded.
    """
    quota = get_or_create_quota(user, db)

    if not quota.is_within_limit(resource):
        limit = getattr(quota, f"{resource}_limit")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Usage quota exceeded for {resource}. Limit: {limit} per month.",
        )


def increment_usage(user: User, resource: str, db: Session):
    """Increment usage counter for a resource."""
    quota = get_or_create_quota(user, db)
    quota.increment_usage(resource)
    db.commit()
