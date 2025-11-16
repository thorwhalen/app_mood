"""Pydantic schemas for feature flags."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class FeatureFlagBase(BaseModel):
    """Base schema for feature flags."""
    name: str
    display_name: str
    description: Optional[str] = None
    category: str = "general"


class FeatureFlagResponse(FeatureFlagBase):
    """Response schema for feature flags."""
    id: str
    enabled: bool
    config: Dict[str, Any] = {}
    required_dependencies: List[str] = []
    dependencies_met: Optional[Dict[str, bool]] = None
    enabled_at: Optional[datetime] = None
    enabled_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeatureFlagUpdate(BaseModel):
    """Schema for updating feature flag configuration."""
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class FeatureConfigUpdate(BaseModel):
    """Schema for updating just the configuration."""
    config: Dict[str, Any]


class FeatureEnableRequest(BaseModel):
    """Schema for enabling a feature."""
    config: Dict[str, Any] = Field(..., description="Feature configuration")


class FeatureDependencyStatus(BaseModel):
    """Schema for dependency check response."""
    feature_name: str
    display_name: str
    dependencies: Dict[str, bool]
    all_met: bool
    missing: List[str]
    install_command: Optional[str] = None
