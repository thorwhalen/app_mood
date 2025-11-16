"""Authentication endpoints for user registration and login."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from ..database import get_db
from ..models import User, UsageQuota
from ..schemas import UserCreate, UserResponse, Token, UsageQuotaResponse
from ..utils.auth import verify_password, get_password_hash, create_access_token
from ..utils.dependencies import get_current_user
from ..services.quota_service import get_or_create_quota
from ..config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_superuser=False,
    )

    db.add(user)
    db.flush()  # Flush to get the user ID

    # Create usage quota for the user
    now = datetime.utcnow()
    period_end = now + relativedelta(months=1)
    usage_quota = UsageQuota(
        user_id=user.id,
        analyses_limit=1000,
        datasets_limit=10,
        model_trainings_limit=5,
        current_period_start=now,
        current_period_end=period_end,
    )

    db.add(usage_quota)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("/usage", response_model=UsageQuotaResponse)
def get_usage_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage quota and statistics."""
    quota = get_or_create_quota(current_user, db)

    return UsageQuotaResponse(
        id=quota.id,
        user_id=quota.user_id,
        analyses_limit=quota.analyses_limit,
        datasets_limit=quota.datasets_limit,
        model_trainings_limit=quota.model_trainings_limit,
        analyses_used=quota.analyses_used,
        datasets_used=quota.datasets_used,
        model_trainings_used=quota.model_trainings_used,
        analyses_remaining=quota.get_remaining("analyses"),
        datasets_remaining=quota.get_remaining("datasets"),
        model_trainings_remaining=quota.get_remaining("model_trainings"),
        current_period_start=quota.current_period_start,
        current_period_end=quota.current_period_end,
    )
