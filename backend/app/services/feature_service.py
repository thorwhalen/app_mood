"""Service for managing feature flags and optional integrations."""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from importlib import import_module
import logging

from ..models import FeatureFlag

logger = logging.getLogger(__name__)


class FeatureFlagError(Exception):
    """Raised when a feature is enabled but dependencies are missing."""
    pass


class FeatureService:
    """Service for managing feature flags."""

    # Default feature definitions
    DEFAULT_FEATURES = {
        "sentry": {
            "display_name": "Sentry Error Tracking",
            "description": "Capture and track errors in real-time with Sentry",
            "required_dependencies": ["sentry_sdk"],
            "category": "monitoring",
            "config_schema": {
                "dsn": {"type": "string", "required": True, "description": "Sentry DSN"},
                "environment": {"type": "string", "default": "production"},
                "traces_sample_rate": {"type": "float", "default": 0.1},
            }
        },
        "email_notifications": {
            "display_name": "Email Notifications",
            "description": "Send email notifications for quota warnings and alerts",
            "required_dependencies": [],  # Using built-in smtplib
            "category": "notifications",
            "config_schema": {
                "smtp_host": {"type": "string", "required": True},
                "smtp_port": {"type": "integer", "default": 587},
                "smtp_user": {"type": "string", "required": True},
                "smtp_password": {"type": "string", "required": True, "secret": True},
                "from_email": {"type": "string", "required": True},
            }
        },
        "webhooks": {
            "display_name": "Webhook Notifications",
            "description": "Send HTTP webhooks for events (analysis complete, quota exceeded)",
            "required_dependencies": ["httpx"],  # Already installed
            "category": "notifications",
            "config_schema": {
                "webhook_url": {"type": "string", "required": True},
                "secret": {"type": "string", "required": False, "secret": True},
                "events": {"type": "array", "default": ["quota_exceeded", "analysis_complete"]},
            }
        },
        "s3_storage": {
            "display_name": "S3 Model Storage",
            "description": "Store ML models in AWS S3 instead of local filesystem",
            "required_dependencies": ["boto3"],
            "category": "storage",
            "config_schema": {
                "bucket_name": {"type": "string", "required": True},
                "region": {"type": "string", "default": "us-east-1"},
                "access_key_id": {"type": "string", "required": True, "secret": True},
                "secret_access_key": {"type": "string", "required": True, "secret": True},
            }
        },
        "audit_logging": {
            "display_name": "Advanced Audit Logging",
            "description": "Detailed audit logs for all admin actions and data changes",
            "required_dependencies": [],
            "category": "compliance",
            "config_schema": {
                "log_level": {"type": "string", "default": "INFO"},
                "retention_days": {"type": "integer", "default": 90},
            }
        },
    }

    def __init__(self, db: Session):
        self.db = db

    def initialize_defaults(self):
        """Initialize default feature flags if they don't exist."""
        for name, config in self.DEFAULT_FEATURES.items():
            existing = self.db.query(FeatureFlag).filter(FeatureFlag.name == name).first()
            if not existing:
                feature = FeatureFlag(
                    name=name,
                    display_name=config["display_name"],
                    description=config["description"],
                    required_dependencies=config["required_dependencies"],
                    category=config["category"],
                    enabled=False,
                    config={}
                )
                self.db.add(feature)
        self.db.commit()

    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        feature = self.db.query(FeatureFlag).filter(FeatureFlag.name == feature_name).first()
        return feature.enabled if feature else False

    def get_feature(self, feature_name: str) -> Optional[FeatureFlag]:
        """Get feature flag by name."""
        return self.db.query(FeatureFlag).filter(FeatureFlag.name == feature_name).first()

    def check_dependencies(self, feature_name: str) -> Dict[str, bool]:
        """
        Check if all required dependencies are installed for a feature.

        Returns:
            Dict mapping dependency names to installation status
        """
        feature = self.get_feature(feature_name)
        if not feature:
            return {}

        results = {}
        for dep in feature.required_dependencies:
            try:
                import_module(dep)
                results[dep] = True
            except ImportError:
                results[dep] = False

        return results

    def validate_feature(self, feature_name: str, raise_on_error: bool = True) -> bool:
        """
        Validate that a feature's dependencies are met.

        Args:
            feature_name: Name of the feature to validate
            raise_on_error: If True, raise FeatureFlagError on missing dependencies

        Returns:
            True if all dependencies are met

        Raises:
            FeatureFlagError: If feature is enabled but dependencies are missing
        """
        feature = self.get_feature(feature_name)
        if not feature:
            return False

        if not feature.enabled:
            return True  # Disabled features don't need validation

        # Check dependencies
        dep_status = self.check_dependencies(feature_name)
        missing_deps = [dep for dep, installed in dep_status.items() if not installed]

        if missing_deps:
            error_msg = (
                f"Feature '{feature.display_name}' is enabled but missing required dependencies: "
                f"{', '.join(missing_deps)}. Please install them with: "
                f"pip install {' '.join(missing_deps)}"
            )
            logger.error(error_msg)

            if raise_on_error:
                raise FeatureFlagError(error_msg)
            return False

        return True

    def enable_feature(self, feature_name: str, config: Dict[str, Any], user_id: Optional[str] = None) -> FeatureFlag:
        """
        Enable a feature with configuration.

        Args:
            feature_name: Name of the feature
            config: Configuration dict
            user_id: ID of user enabling the feature

        Returns:
            Updated FeatureFlag

        Raises:
            FeatureFlagError: If dependencies are not met
        """
        feature = self.get_feature(feature_name)
        if not feature:
            raise ValueError(f"Feature '{feature_name}' not found")

        # Validate dependencies BEFORE enabling
        dep_status = self.check_dependencies(feature_name)
        missing_deps = [dep for dep, installed in dep_status.items() if not installed]

        if missing_deps:
            raise FeatureFlagError(
                f"Cannot enable '{feature.display_name}'. Missing dependencies: {', '.join(missing_deps)}. "
                f"Install with: pip install {' '.join(missing_deps)}"
            )

        # Validate configuration
        self._validate_config(feature_name, config)

        # Enable feature
        feature.enabled = True
        feature.config = config
        feature.enabled_at = datetime.utcnow()
        feature.enabled_by = user_id
        self.db.commit()
        self.db.refresh(feature)

        logger.info(f"Feature '{feature.display_name}' enabled by user {user_id}")
        return feature

    def disable_feature(self, feature_name: str) -> FeatureFlag:
        """Disable a feature."""
        feature = self.get_feature(feature_name)
        if not feature:
            raise ValueError(f"Feature '{feature_name}' not found")

        feature.enabled = False
        self.db.commit()
        self.db.refresh(feature)

        logger.info(f"Feature '{feature.display_name}' disabled")
        return feature

    def update_config(self, feature_name: str, config: Dict[str, Any]) -> FeatureFlag:
        """Update feature configuration."""
        feature = self.get_feature(feature_name)
        if not feature:
            raise ValueError(f"Feature '{feature_name}' not found")

        self._validate_config(feature_name, config)

        feature.config = config
        self.db.commit()
        self.db.refresh(feature)

        return feature

    def _validate_config(self, feature_name: str, config: Dict[str, Any]):
        """Validate configuration against schema."""
        schema = self.DEFAULT_FEATURES.get(feature_name, {}).get("config_schema", {})

        for key, rules in schema.items():
            if rules.get("required") and key not in config:
                raise ValueError(f"Missing required config key: {key}")

        # Could add more detailed type validation here
        return True

    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """Get feature configuration."""
        feature = self.get_feature(feature_name)
        return feature.config if feature else {}

    def list_features(self, category: Optional[str] = None) -> List[FeatureFlag]:
        """List all features, optionally filtered by category."""
        query = self.db.query(FeatureFlag)
        if category:
            query = query.filter(FeatureFlag.category == category)
        return query.all()


# Global instance - will be initialized on app startup
from datetime import datetime

_feature_service: Optional[FeatureService] = None


def get_feature_service(db: Session) -> FeatureService:
    """Get or create feature service instance."""
    return FeatureService(db)


def is_feature_enabled(feature_name: str, db: Session) -> bool:
    """Quick check if a feature is enabled."""
    service = get_feature_service(db)
    return service.is_enabled(feature_name)
