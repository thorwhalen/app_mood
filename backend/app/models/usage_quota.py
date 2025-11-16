from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


class UsageQuota(Base):
    """Usage quota tracking for users."""

    __tablename__ = "usage_quotas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Quota limits (per month)
    analyses_limit = Column(Integer, default=1000)
    datasets_limit = Column(Integer, default=10)
    model_trainings_limit = Column(Integer, default=5)

    # Current usage (resets monthly)
    analyses_used = Column(Integer, default=0)
    datasets_used = Column(Integer, default=0)
    model_trainings_used = Column(Integer, default=0)

    # Timestamps
    current_period_start = Column(DateTime, default=datetime.utcnow)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage_quota")

    def is_within_limit(self, resource: str) -> bool:
        """Check if usage is within limit for a resource."""
        if resource == "analyses":
            return self.analyses_used < self.analyses_limit
        elif resource == "datasets":
            return self.datasets_used < self.datasets_limit
        elif resource == "model_trainings":
            return self.model_trainings_used < self.model_trainings_limit
        return False

    def increment_usage(self, resource: str):
        """Increment usage for a resource."""
        if resource == "analyses":
            self.analyses_used += 1
        elif resource == "datasets":
            self.datasets_used += 1
        elif resource == "model_trainings":
            self.model_trainings_used += 1
        self.updated_at = datetime.utcnow()

    def get_remaining(self, resource: str) -> int:
        """Get remaining quota for a resource."""
        if resource == "analyses":
            return max(0, self.analyses_limit - self.analyses_used)
        elif resource == "datasets":
            return max(0, self.datasets_limit - self.datasets_used)
        elif resource == "model_trainings":
            return max(0, self.model_trainings_limit - self.model_trainings_used)
        return 0
