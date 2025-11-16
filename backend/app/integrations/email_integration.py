"""Optional email notifications integration."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Union
from sqlalchemy.orm import Session

from ..services.feature_service import get_feature_service, FeatureFlagError

logger = logging.getLogger(__name__)

# Global flag
_email_enabled = False
_email_config = {}


def initialize_email(db: Session) -> bool:
    """
    Initialize email notifications if enabled.

    Returns:
        True if email was successfully configured, False otherwise
    """
    global _email_enabled, _email_config

    try:
        service = get_feature_service(db)

        # Check if feature is enabled
        if not service.is_enabled("email_notifications"):
            logger.info("Email notifications are disabled")
            return False

        # Get configuration
        config = service.get_feature_config("email_notifications")

        required_fields = ["smtp_host", "smtp_user", "smtp_password", "from_email"]
        for field in required_fields:
            if not config.get(field):
                logger.error(f"Email configuration missing required field: {field}")
                return False

        _email_config = config
        _email_enabled = True
        logger.info(f"Email notifications initialized (SMTP: {config.get('smtp_host')})")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize email notifications: {e}")
        return False


def is_email_enabled() -> bool:
    """Check if email notifications are enabled."""
    return _email_enabled


def send_email(
    to: Union[str, List[str]],
    subject: str,
    body: str,
    html: bool = False
) -> bool:
    """
    Send an email if email notifications are enabled.

    Args:
        to: Recipient email(s)
        subject: Email subject
        body: Email body
        html: If True, send as HTML email

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not _email_enabled:
        logger.debug("Email not sent - feature disabled")
        return False

    try:
        # Convert single recipient to list
        recipients = [to] if isinstance(to, str) else to

        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = _email_config['from_email']
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject

        # Attach body
        mime_type = 'html' if html else 'plain'
        msg.attach(MIMEText(body, mime_type))

        # Connect to SMTP server
        smtp_host = _email_config['smtp_host']
        smtp_port = _email_config.get('smtp_port', 587)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(
                _email_config['smtp_user'],
                _email_config['smtp_password']
            )
            server.send_message(msg)

        logger.info(f"Email sent successfully to {recipients}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def send_quota_warning_email(user_email: str, resource: str, percent: int, used: int, limit: int) -> bool:
    """
    Send a quota warning email to a user.

    Args:
        user_email: User's email address
        resource: Resource type (analyses, datasets, etc.)
        percent: Percentage used
        used: Amount used
        limit: Quota limit

    Returns:
        True if email was sent
    """
    if not _email_enabled:
        return False

    severity = "Critical" if percent >= 90 else "Warning"
    subject = f"[Mood App] {severity}: {percent}% of {resource} quota used"

    body = f"""
Hello,

This is a quota usage notification for your Mood application account.

You have used {percent}% of your {resource} quota:
- Used: {used}
- Limit: {limit}
- Remaining: {limit - used}

{'⚠️ CRITICAL: Please reduce usage or contact support to increase your quota.' if percent >= 90 else 'Please monitor your usage to avoid service interruption.'}

Current Period: Until quota reset

Thank you,
Mood App Team
"""

    return send_email(user_email, subject, body)


def send_analysis_complete_email(user_email: str, mood_name: str, text: str, score: float) -> bool:
    """Send email notification when analysis is complete."""
    if not _email_enabled:
        return False

    subject = f"[Mood App] Analysis Complete: {mood_name}"
    body = f"""
Hello,

Your sentiment analysis has been completed.

Mood: {mood_name}
Text: {text[:100]}{'...' if len(text) > 100 else ''}
Score: {score:.3f}

View your results at: [Dashboard URL]

Thank you,
Mood App Team
"""

    return send_email(user_email, subject, body)
