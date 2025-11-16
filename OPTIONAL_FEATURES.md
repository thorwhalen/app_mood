# Optional Features Guide

This document describes the optional integrations available in the Mood application and how to configure them.

## Overview

The Mood application includes a flexible feature flag system that allows administrators to opt-in to various optional integrations. All features are **disabled by default** and only activate when explicitly enabled through the admin interface.

**Key principles:**
- Features are disabled by default (not in the computational path)
- Features can only be enabled if all dependencies are installed
- Missing dependencies result in clear error messages with installation instructions
- Features can be enabled/disabled without application restart
- Configuration is managed through the admin UI

## Accessing Feature Management

1. Log in as an admin user (superuser)
2. Navigate to **Admin** → **Manage Features** (or go directly to `/admin/features`)
3. View all available features with their dependency status
4. Enable features by toggling the switch and providing required configuration

## Available Features

### 1. Sentry Error Tracking

**Category:** Monitoring
**Dependencies:** `sentry-sdk`

Captures and tracks errors in real-time with Sentry for better debugging and monitoring.

**Installation:**
```bash
pip install sentry-sdk
```

**Configuration:**
- **DSN** (required): Your Sentry project DSN (format: `https://xxx@sentry.io/xxx`)
- **Environment** (optional): Environment name (default: `production`)
- **Traces Sample Rate** (optional): Performance monitoring sample rate (default: `0.1`)

**Example:**
```json
{
  "dsn": "https://your-key@sentry.io/your-project",
  "environment": "production",
  "traces_sample_rate": 0.1
}
```

**Features:**
- Automatic error capture
- Performance monitoring
- Release tracking
- User context in error reports

### 2. Email Notifications

**Category:** Notifications
**Dependencies:** None (uses built-in `smtplib`)

Send email notifications for quota warnings and system alerts.

**Configuration:**
- **SMTP Host** (required): SMTP server hostname (e.g., `smtp.gmail.com`)
- **SMTP Port** (optional): SMTP port (default: `587`)
- **SMTP User** (required): Username for SMTP authentication
- **SMTP Password** (required): Password for SMTP authentication
- **From Email** (required): Email address to send from

**Example:**
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your-email@gmail.com",
  "smtp_password": "your-app-password",
  "from_email": "noreply@mood-app.com"
}
```

**Features:**
- Quota warning emails (80%, 90% thresholds)
- Quota exceeded alerts
- Custom email templates
- Automatic retry on failure

**Note:** For Gmail, you'll need to use an [App Password](https://support.google.com/accounts/answer/185833).

### 3. Webhook Notifications

**Category:** Notifications
**Dependencies:** `httpx` (already installed)

Send HTTP webhooks for events like analysis completion and quota exceeded.

**Configuration:**
- **Webhook URL** (required): HTTPS endpoint to receive notifications
- **Secret** (optional): Secret key for HMAC signature verification
- **Events** (optional): Array of events to subscribe to (default: `["quota_exceeded", "analysis_complete"]`)

**Example:**
```json
{
  "webhook_url": "https://your-app.com/webhooks/mood",
  "secret": "your-webhook-secret",
  "events": ["quota_exceeded", "analysis_complete"]
}
```

**Available Events:**
- `quota_exceeded`: Fired when a user exceeds their quota
- `analysis_complete`: Fired when an analysis completes successfully

**Webhook Payload:**
```json
{
  "event": "analysis_complete",
  "data": {
    "user_id": "user-uuid",
    "mood_id": "mood-uuid",
    "analysis_id": "analysis-uuid",
    "score": 0.85,
    "timestamp": "2025-11-16T10:30:00Z"
  }
}
```

**Security:**
If a secret is configured, webhooks include an `X-Webhook-Signature` header with HMAC-SHA256 signature:
```
X-Webhook-Signature: sha256=<hex-digest>
```

To verify:
```python
import hmac
import hashlib
import json

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        json.dumps(payload, sort_keys=True).encode(),
        hashlib.sha256
    ).hexdigest()
    return signature == f"sha256={expected}"
```

### 4. S3 Model Storage

**Category:** Storage
**Dependencies:** `boto3`
**Status:** Defined but not yet implemented

Store ML models in AWS S3 instead of local filesystem for better scalability.

**Installation:**
```bash
pip install boto3
```

**Configuration (planned):**
- **Bucket Name** (required): S3 bucket name
- **Region** (optional): AWS region (default: `us-east-1`)
- **Access Key ID** (required): AWS access key
- **Secret Access Key** (required): AWS secret key

### 5. Advanced Audit Logging

**Category:** Compliance
**Dependencies:** None
**Status:** Defined but not yet implemented

Detailed audit logs for all admin actions and data changes.

**Configuration (planned):**
- **Log Level** (optional): Logging level (default: `INFO`)
- **Retention Days** (optional): How long to keep audit logs (default: `90`)

## Dependency Management

### Checking Dependencies

The Features page automatically checks if required dependencies are installed:
- ✅ **Green checkmark**: All dependencies are met
- ❌ **Red error**: Dependencies are missing

### Installing Dependencies

If dependencies are missing, you'll see a message like:
```
Missing: sentry_sdk
Install with: pip install sentry_sdk
```

**Docker Deployment:**
Add dependencies to `backend/requirements.txt`:
```txt
# Optional integrations
sentry-sdk>=1.30.0  # For Sentry error tracking
boto3>=1.26.0       # For S3 storage
```

Then rebuild:
```bash
docker-compose build backend
docker-compose up -d
```

**Local Development:**
```bash
cd backend
pip install sentry-sdk boto3
```

## Feature Lifecycle

### Enabling a Feature

1. Navigate to Features page
2. Ensure dependencies are installed (green checkmark)
3. Click the toggle switch
4. Fill in required configuration
5. Click "Enable Feature"

The feature is now active and will be initialized on the next request.

### Disabling a Feature

1. Navigate to Features page
2. Click the toggle switch for an enabled feature
3. Confirm the disable action

The feature is immediately disabled and will not process any new requests.

### Updating Configuration

1. Navigate to Features page
2. Expand the "Configuration" accordion for an enabled feature
3. View current configuration (secrets are masked)
4. To update: Disable the feature, then re-enable with new configuration

## Error Handling

### Graceful Degradation

If a feature is enabled but dependencies are missing or configuration is invalid:
- The feature will **not crash the application**
- An error is logged: `Feature 'X' is enabled but missing required dependencies: Y`
- The feature silently fails (returns `False` or `None`)
- Application continues to function normally

### Logs

Feature-related logs are written to the application logs:
```
INFO: Sentry integration initialized
ERROR: Cannot initialize Sentry: Missing dependencies: sentry_sdk. Install with: pip install sentry_sdk
INFO: Webhook notifications initialized (URL: https://...)
```

Check logs:
```bash
docker-compose logs -f backend
```

## Security Considerations

### Secrets Management

**Current Implementation:**
- Secrets are stored in the database (PostgreSQL) in JSON columns
- Secrets are masked in the UI (displayed as `••••••••`)
- API responses include full config (admin-only endpoint)

**Production Recommendations:**
1. Use environment variables for sensitive values
2. Integrate with secrets management (AWS Secrets Manager, HashiCorp Vault)
3. Enable database encryption at rest
4. Restrict admin access with role-based access control

### API Security

- Feature management endpoints require **superuser** privileges
- Non-admin users cannot view or modify feature configurations
- Invalid configurations are rejected before enabling

## Extending the System

### Adding a New Feature

1. **Define the feature** in `backend/app/services/feature_service.py`:
```python
"my_feature": {
    "display_name": "My Feature",
    "description": "Description of what this feature does",
    "required_dependencies": ["some_package"],
    "category": "monitoring",  # or notifications, storage, compliance
    "config_schema": {
        "api_key": {"type": "string", "required": True, "secret": True},
        "enabled": {"type": "boolean", "default": True},
    }
}
```

2. **Create integration module** in `backend/app/integrations/my_integration.py`:
```python
import logging
from sqlalchemy.orm import Session
from ..services.feature_service import get_feature_service

logger = logging.getLogger(__name__)
_my_feature_enabled = False
_my_feature_config = {}

def initialize_my_feature(db: Session) -> bool:
    global _my_feature_enabled, _my_feature_config

    service = get_feature_service(db)
    if not service.is_enabled("my_feature"):
        logger.info("My feature is disabled")
        return False

    try:
        service.validate_feature("my_feature", raise_on_error=True)
    except FeatureFlagError as e:
        logger.error(f"Cannot initialize my feature: {e}")
        return False

    config = service.get_feature_config("my_feature")
    _my_feature_config = config
    _my_feature_enabled = True

    logger.info("My feature initialized")
    return True

def is_my_feature_enabled() -> bool:
    return _my_feature_enabled

def do_something():
    if not _my_feature_enabled:
        return None
    # Implementation here
```

3. **Initialize in** `backend/app/main.py`:
```python
from .integrations import my_integration

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ...
    my_integration.initialize_my_feature(db)
    # ...
```

4. **Add UI configuration** in `frontend/src/pages/FeaturesPage.tsx`:
```tsx
{selectedFeature?.name === 'my_feature' && (
  <TextField
    fullWidth
    label="API Key"
    margin="normal"
    required
    type="password"
    onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
  />
)}
```

## Troubleshooting

### Feature Won't Enable

**Problem:** Toggle switch is disabled
**Solution:** Install missing dependencies first

**Problem:** "Missing required config key" error
**Solution:** Fill in all required configuration fields

### Feature Not Working After Enable

**Problem:** Feature enabled but not functioning
**Solution:**
1. Check application logs for errors
2. Verify configuration is correct
3. Restart the backend service: `docker-compose restart backend`

### Secrets Not Working

**Problem:** Email/webhook authentication failing
**Solution:**
1. Verify credentials in a test environment
2. Check for special characters in passwords (may need escaping)
3. For Gmail: Use App Password, not account password

## Architecture

### Database Schema

Features are stored in the `feature_flags` table:
```sql
CREATE TABLE feature_flags (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    display_name VARCHAR NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT FALSE,
    config JSON DEFAULT '{}',
    required_dependencies JSON DEFAULT '[]',
    category VARCHAR DEFAULT 'general',
    enabled_at TIMESTAMP,
    enabled_by VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Service Layer

`backend/app/services/feature_service.py`:
- `is_enabled(feature_name)`: Check if feature is enabled
- `check_dependencies(feature_name)`: Validate dependencies
- `enable_feature(feature_name, config)`: Enable with validation
- `disable_feature(feature_name)`: Disable feature
- `validate_feature(feature_name)`: Raise error if dependencies missing

### Integration Pattern

Each integration follows the pattern:
```python
# Global state (module level)
_feature_enabled = False
_feature_config = {}

# Initialize on app startup
def initialize_feature(db: Session) -> bool:
    # Check if enabled
    # Validate dependencies
    # Store config
    # Return success status

# Check before use
def use_feature():
    if not _feature_enabled:
        return None
    # Use feature
```

## Future Enhancements

- [ ] Secrets encryption in database
- [ ] Feature usage metrics
- [ ] A/B testing framework
- [ ] Gradual rollout (percentage-based enabling)
- [ ] Feature dependency graph
- [ ] Auto-disable on repeated failures
- [ ] Feature usage analytics
- [ ] Webhook retry mechanism with exponential backoff
- [ ] Email template customization
- [ ] Multi-environment configuration

## Support

For issues or questions:
1. Check application logs: `docker-compose logs -f backend`
2. Review this documentation
3. Check feature status in admin UI
4. Verify configuration is correct

## References

- [Sentry Documentation](https://docs.sentry.io/)
- [SMTP Configuration Guide](https://support.google.com/mail/answer/7126229)
- [Webhook Best Practices](https://webhooks.fyi/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
