"""Feature flags model for optional integrations."""
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from datetime import datetime
import uuid
from ..database import Base


class FeatureFlag(Base):
    """Feature flag configuration for optional integrations."""

    __tablename__ = "feature_flags"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    description = Column(String)

    # Feature state
    enabled = Column(Boolean, default=False)

    # Configuration (JSON for flexibility)
    config = Column(JSON, default=dict)

    # Metadata
    required_dependencies = Column(JSON, default=list)  # List of Python packages
    category = Column(String, default="general")  # monitoring, notifications, storage, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    enabled_at = Column(DateTime, nullable=True)
    enabled_by = Column(String, nullable=True)  # User ID who enabled it

    def __repr__(self):
        return f"<FeatureFlag {self.name} enabled={self.enabled}>"
