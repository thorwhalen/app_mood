from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


class User(Base):
    """User model for authentication and multi-tenancy."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    moods = relationship("Mood", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    usage_quota = relationship("UsageQuota", back_populates="user", uselist=False, cascade="all, delete-orphan")
