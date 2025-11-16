"""Celery tasks for quota management."""
from datetime import datetime
from dateutil.relativedelta import relativedelta
from celery import shared_task
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import UsageQuota


@shared_task
def reset_monthly_quotas():
    """
    Reset all usage quotas at the end of each billing period.
    This task should be run daily to check for expired periods.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()

        # Find all quotas where the period has ended
        expired_quotas = db.query(UsageQuota).filter(
            UsageQuota.current_period_end <= now
        ).all()

        reset_count = 0
        for quota in expired_quotas:
            # Reset usage counters
            quota.analyses_used = 0
            quota.datasets_used = 0
            quota.model_trainings_used = 0

            # Update period dates
            quota.current_period_start = now
            quota.current_period_end = now + relativedelta(months=1)
            quota.updated_at = now

            reset_count += 1

        db.commit()

        return {
            "status": "success",
            "reset_count": reset_count,
            "timestamp": now.isoformat()
        }

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@shared_task
def check_quota_warnings():
    """
    Check all users' quota usage and send warnings for those approaching limits.
    This task should be run daily.
    """
    db: Session = SessionLocal()
    try:
        all_quotas = db.query(UsageQuota).all()

        warnings_sent = 0
        critical_warnings = 0

        for quota in all_quotas:
            # Check analyses quota
            analyses_percent = (quota.analyses_used / quota.analyses_limit * 100) if quota.analyses_limit > 0 else 0

            # 90% threshold - critical warning
            if 90 <= analyses_percent < 100 and not hasattr(quota, '_warned_90'):
                send_quota_warning(quota, 'analyses', 90, critical=True)
                critical_warnings += 1

            # 80% threshold - warning
            elif 80 <= analyses_percent < 90 and not hasattr(quota, '_warned_80'):
                send_quota_warning(quota, 'analyses', 80, critical=False)
                warnings_sent += 1

            # Check datasets quota
            datasets_percent = (quota.datasets_used / quota.datasets_limit * 100) if quota.datasets_limit > 0 else 0
            if 80 <= datasets_percent < 100:
                send_quota_warning(quota, 'datasets', int(datasets_percent), critical=datasets_percent >= 90)
                warnings_sent += 1

            # Check model trainings quota
            trainings_percent = (quota.model_trainings_used / quota.model_trainings_limit * 100) if quota.model_trainings_limit > 0 else 0
            if 80 <= trainings_percent < 100:
                send_quota_warning(quota, 'model_trainings', int(trainings_percent), critical=trainings_percent >= 90)
                warnings_sent += 1

        return {
            "status": "success",
            "warnings_sent": warnings_sent,
            "critical_warnings": critical_warnings,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def send_quota_warning(quota: UsageQuota, resource: str, percent: int, critical: bool = False):
    """
    Send quota warning notification to user.
    In a real implementation, this would send an email or push notification.
    For now, we'll just log it.
    """
    from ..utils.logger import logger

    severity = "CRITICAL" if critical else "WARNING"
    message = (
        f"{severity}: User {quota.user_id} has used {percent}% of their {resource} quota "
        f"({getattr(quota, f'{resource}_used')}/{getattr(quota, f'{resource}_limit')})"
    )

    logger.warning(message)

    # TODO: Implement actual email/notification sending
    # Example:
    # from ..services.email_service import send_email
    # send_email(
    #     to=quota.user.email,
    #     subject=f"Quota Warning: {percent}% of {resource} used",
    #     body=message
    # )
