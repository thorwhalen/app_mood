"""Optional webhook notifications integration."""
import logging
import hashlib
import hmac
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import httpx

from ..services.feature_service import get_feature_service

logger = logging.getLogger(__name__)

# Global state
_webhook_enabled = False
_webhook_config = {}


def initialize_webhooks(db: Session) -> bool:
    """Initialize webhook notifications if enabled."""
    global _webhook_enabled, _webhook_config

    try:
        service = get_feature_service(db)

        if not service.is_enabled("webhooks"):
            logger.info("Webhook notifications are disabled")
            return False

        config = service.get_feature_config("webhooks")

        if not config.get("webhook_url"):
            logger.error("Webhook URL not configured")
            return False

        _webhook_config = config
        _webhook_enabled = True
        logger.info(f"Webhook notifications initialized (URL: {config.get('webhook_url')})")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize webhooks: {e}")
        return False


def is_webhook_enabled() -> bool:
    """Check if webhooks are enabled."""
    return _webhook_enabled


async def send_webhook(event: str, data: Dict[str, Any]) -> bool:
    """
    Send a webhook notification if enabled and event is subscribed.

    Args:
        event: Event name (e.g., 'quota_exceeded', 'analysis_complete')
        data: Event data payload

    Returns:
        True if webhook was sent successfully
    """
    if not _webhook_enabled:
        return False

    # Check if this event is subscribed
    subscribed_events = _webhook_config.get("events", [])
    if event not in subscribed_events:
        logger.debug(f"Event '{event}' not subscribed, skipping webhook")
        return False

    try:
        url = _webhook_config["webhook_url"]
        secret = _webhook_config.get("secret")

        payload = {
            "event": event,
            "data": data
        }

        headers = {"Content-Type": "application/json"}

        # Add signature if secret is configured
        if secret:
            signature = _generate_signature(payload, secret)
            headers["X-Webhook-Signature"] = signature

        # Send webhook with timeout
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=10.0  # 10 second timeout
            )
            response.raise_for_status()

        logger.info(f"Webhook sent successfully for event '{event}'")
        return True

    except httpx.TimeoutException:
        logger.error(f"Webhook timeout for event '{event}'")
        return False
    except httpx.HTTPError as e:
        logger.error(f"Webhook HTTP error for event '{event}': {e}")
        return False
    except Exception as e:
        logger.error(f"Webhook failed for event '{event}': {e}")
        return False


def _generate_signature(payload: Dict[str, Any], secret: str) -> str:
    """Generate HMAC signature for webhook payload."""
    import json
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


async def send_quota_exceeded_webhook(user_id: str, resource: str, used: int, limit: int) -> bool:
    """Send webhook for quota exceeded event."""
    return await send_webhook("quota_exceeded", {
        "user_id": user_id,
        "resource": resource,
        "used": used,
        "limit": limit,
        "timestamp": datetime.utcnow().isoformat()
    })


async def send_analysis_complete_webhook(user_id: str, mood_id: str, analysis_id: str, score: float) -> bool:
    """Send webhook for analysis complete event."""
    return await send_webhook("analysis_complete", {
        "user_id": user_id,
        "mood_id": mood_id,
        "analysis_id": analysis_id,
        "score": score,
        "timestamp": datetime.utcnow().isoformat()
    })
