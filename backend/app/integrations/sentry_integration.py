"""Optional Sentry integration for error tracking."""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from ..services.feature_service import get_feature_service, FeatureFlagError

logger = logging.getLogger(__name__)

# Global flag to track if Sentry is initialized
_sentry_initialized = False


def initialize_sentry(db: Session) -> bool:
    """
    Initialize Sentry if the feature is enabled and dependencies are met.

    This is called during app startup. It will only initialize Sentry if:
    1. The 'sentry' feature flag is enabled
    2. The sentry_sdk package is installed
    3. Valid configuration is provided

    Args:
        db: Database session

    Returns:
        True if Sentry was successfully initialized, False otherwise
    """
    global _sentry_initialized

    try:
        service = get_feature_service(db)

        # Check if feature is enabled
        if not service.is_enabled("sentry"):
            logger.info("Sentry integration is disabled")
            return False

        # Validate dependencies
        try:
            service.validate_feature("sentry", raise_on_error=True)
        except FeatureFlagError as e:
            logger.error(f"Cannot initialize Sentry: {e}")
            return False

        # Import Sentry SDK (only if enabled and deps are met)
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
        except ImportError as e:
            logger.error(f"Sentry SDK not installed: {e}")
            logger.error("Install with: pip install sentry-sdk")
            return False

        # Get configuration
        config = service.get_feature_config("sentry")
        dsn = config.get("dsn")

        if not dsn:
            logger.error("Sentry DSN not configured")
            return False

        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn,
            environment=config.get("environment", "production"),
            traces_sample_rate=config.get("traces_sample_rate", 0.1),
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,        # Capture info and above as breadcrumbs
                    event_level=logging.ERROR  # Send errors as events
                )
            ],
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
            # We recommend adjusting this value in production.
        )

        _sentry_initialized = True
        logger.info(f"Sentry initialized successfully (environment: {config.get('environment')})")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def is_sentry_enabled() -> bool:
    """Check if Sentry is currently initialized and active."""
    return _sentry_initialized


def capture_exception(error: Exception, context: Optional[dict] = None):
    """
    Capture an exception in Sentry if it's enabled.

    This is a safe wrapper that does nothing if Sentry is not initialized.

    Args:
        error: The exception to capture
        context: Optional context dictionary to attach to the event
    """
    if not _sentry_initialized:
        return

    try:
        import sentry_sdk

        if context:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_extra(key, value)
                sentry_sdk.capture_exception(error)
        else:
            sentry_sdk.capture_exception(error)

    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {e}")


def capture_message(message: str, level: str = "info", context: Optional[dict] = None):
    """
    Capture a message in Sentry if it's enabled.

    Args:
        message: The message to capture
        level: Log level (debug, info, warning, error, fatal)
        context: Optional context dictionary
    """
    if not _sentry_initialized:
        return

    try:
        import sentry_sdk

        if context:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_extra(key, value)
                sentry_sdk.capture_message(message, level=level)
        else:
            sentry_sdk.capture_message(message, level=level)

    except Exception as e:
        logger.error(f"Failed to capture message in Sentry: {e}")


def set_user_context(user_id: str, email: Optional[str] = None):
    """
    Set user context in Sentry for better error tracking.

    Args:
        user_id: User ID
        email: Optional user email
    """
    if not _sentry_initialized:
        return

    try:
        import sentry_sdk

        sentry_sdk.set_user({"id": user_id, "email": email})

    except Exception as e:
        logger.error(f"Failed to set user context in Sentry: {e}")
