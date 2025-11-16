"""Main FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging
import time

from .config import settings
from .database import init_db, engine
from .api import api_router
from .utils.metrics import PrometheusMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    # Startup
    logger.info("Starting Mood API...")
    init_db()
    logger.info("Database initialized")

    # Initialize optional integrations
    from .database import SessionLocal
    from .services.feature_service import get_feature_service
    from .integrations import sentry_integration, email_integration, webhook_integration

    db = SessionLocal()
    try:
        # Initialize default feature flags
        service = get_feature_service(db)
        service.initialize_defaults()
        logger.info("Feature flags initialized")

        # Initialize optional integrations (only if enabled)
        sentry_integration.initialize_sentry(db)
        email_integration.initialize_email(db)
        webhook_integration.initialize_webhooks(db)

        logger.info("Optional integrations initialized")
    except Exception as e:
        logger.error(f"Error initializing integrations: {e}")
    finally:
        db.close()

    yield
    # Shutdown
    logger.info("Shutting down Mood API...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for mood-based financial sentiment analysis",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure in production

# Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
@limiter.limit("100/minute")
def root(request: Request):
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}


@app.get("/health/ready")
def readiness_check():
    """
    Readiness probe for Kubernetes.

    Checks if the application is ready to serve traffic.
    """
    try:
        # Check database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")

        return {
            "status": "ready",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/health/live")
def liveness_check():
    """
    Liveness probe for Kubernetes.

    Checks if the application is alive and should not be restarted.
    """
    return {"status": "alive"}


@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    metrics_data = generate_latest()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
