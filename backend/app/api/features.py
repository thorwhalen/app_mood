"""Feature flags admin endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import User, FeatureFlag
from ..schemas import (
    FeatureFlagResponse,
    FeatureEnableRequest,
    FeatureConfigUpdate,
    FeatureDependencyStatus,
)
from ..services.feature_service import (
    get_feature_service,
    FeatureFlagError,
)
from ..utils.dependencies import get_current_user

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


@router.get("/", response_model=List[FeatureFlagResponse])
def list_features(
    category: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all feature flags (admin only).

    Optionally filter by category: monitoring, notifications, storage, compliance
    """
    service = get_feature_service(db)
    features = service.list_features(category=category)

    # Add dependency status to each feature
    response = []
    for feature in features:
        dep_status = service.check_dependencies(feature.name)

        response.append(FeatureFlagResponse(
            id=feature.id,
            name=feature.name,
            display_name=feature.display_name,
            description=feature.description,
            category=feature.category,
            enabled=feature.enabled,
            config=feature.config,
            required_dependencies=feature.required_dependencies,
            dependencies_met=dep_status,
            enabled_at=feature.enabled_at,
            enabled_by=feature.enabled_by,
            created_at=feature.created_at,
            updated_at=feature.updated_at,
        ))

    return response


@router.get("/{feature_name}", response_model=FeatureFlagResponse)
def get_feature(
    feature_name: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get a specific feature flag (admin only)."""
    service = get_feature_service(db)
    feature = service.get_feature(feature_name)

    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature '{feature_name}' not found"
        )

    dep_status = service.check_dependencies(feature_name)

    return FeatureFlagResponse(
        id=feature.id,
        name=feature.name,
        display_name=feature.display_name,
        description=feature.description,
        category=feature.category,
        enabled=feature.enabled,
        config=feature.config,
        required_dependencies=feature.required_dependencies,
        dependencies_met=dep_status,
        enabled_at=feature.enabled_at,
        enabled_by=feature.enabled_by,
        created_at=feature.created_at,
        updated_at=feature.updated_at,
    )


@router.get("/{feature_name}/dependencies", response_model=FeatureDependencyStatus)
def check_dependencies(
    feature_name: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Check dependency status for a feature (admin only).

    Returns which dependencies are installed and which are missing.
    """
    service = get_feature_service(db)
    feature = service.get_feature(feature_name)

    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature '{feature_name}' not found"
        )

    dep_status = service.check_dependencies(feature_name)
    missing = [dep for dep, installed in dep_status.items() if not installed]
    all_met = len(missing) == 0

    install_cmd = None
    if missing:
        install_cmd = f"pip install {' '.join(missing)}"

    return FeatureDependencyStatus(
        feature_name=feature.name,
        display_name=feature.display_name,
        dependencies=dep_status,
        all_met=all_met,
        missing=missing,
        install_command=install_cmd,
    )


@router.post("/{feature_name}/enable", response_model=FeatureFlagResponse)
def enable_feature(
    feature_name: str,
    request: FeatureEnableRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Enable a feature with configuration (admin only).

    This will:
    1. Check that all required dependencies are installed
    2. Validate the configuration
    3. Enable the feature

    Raises 400 if dependencies are missing or config is invalid.
    """
    service = get_feature_service(db)

    try:
        feature = service.enable_feature(
            feature_name,
            config=request.config,
            user_id=current_admin.id
        )
    except FeatureFlagError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    dep_status = service.check_dependencies(feature_name)

    return FeatureFlagResponse(
        id=feature.id,
        name=feature.name,
        display_name=feature.display_name,
        description=feature.description,
        category=feature.category,
        enabled=feature.enabled,
        config=feature.config,
        required_dependencies=feature.required_dependencies,
        dependencies_met=dep_status,
        enabled_at=feature.enabled_at,
        enabled_by=feature.enabled_by,
        created_at=feature.created_at,
        updated_at=feature.updated_at,
    )


@router.post("/{feature_name}/disable", response_model=FeatureFlagResponse)
def disable_feature(
    feature_name: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Disable a feature (admin only)."""
    service = get_feature_service(db)

    try:
        feature = service.disable_feature(feature_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    dep_status = service.check_dependencies(feature_name)

    return FeatureFlagResponse(
        id=feature.id,
        name=feature.name,
        display_name=feature.display_name,
        description=feature.description,
        category=feature.category,
        enabled=feature.enabled,
        config=feature.config,
        required_dependencies=feature.required_dependencies,
        dependencies_met=dep_status,
        enabled_at=feature.enabled_at,
        enabled_by=feature.enabled_by,
        created_at=feature.created_at,
        updated_at=feature.updated_at,
    )


@router.put("/{feature_name}/config", response_model=FeatureFlagResponse)
def update_feature_config(
    feature_name: str,
    request: FeatureConfigUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update feature configuration (admin only)."""
    service = get_feature_service(db)

    try:
        feature = service.update_config(feature_name, request.config)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    dep_status = service.check_dependencies(feature_name)

    return FeatureFlagResponse(
        id=feature.id,
        name=feature.name,
        display_name=feature.display_name,
        description=feature.description,
        category=feature.category,
        enabled=feature.enabled,
        config=feature.config,
        required_dependencies=feature.required_dependencies,
        dependencies_met=dep_status,
        enabled_at=feature.enabled_at,
        enabled_by=feature.enabled_by,
        created_at=feature.created_at,
        updated_at=feature.updated_at,
    )


@router.post("/initialize", response_model=dict)
def initialize_features(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Initialize default feature flags (admin only).

    This creates all predefined features in the database if they don't exist.
    Safe to call multiple times.
    """
    service = get_feature_service(db)
    service.initialize_defaults()

    return {
        "message": "Feature flags initialized",
        "features": len(service.DEFAULT_FEATURES)
    }
