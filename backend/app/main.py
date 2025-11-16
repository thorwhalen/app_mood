"""Main FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time

from .config import settings
from .database import init_db, engine
from .api import api_router

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
    Basic metrics endpoint for monitoring.

    Returns application metrics in a simple format.
    """
    from sqlalchemy import func
    from .database import SessionLocal
    from .models import Mood, Dataset, Analysis

    db = SessionLocal()
    try:
        mood_count = db.query(func.count(Mood.id)).scalar()
        dataset_count = db.query(func.count(Dataset.id)).scalar()
        analysis_count = db.query(func.count(Analysis.id)).scalar()

        return {
            "moods_total": mood_count,
            "datasets_total": dataset_count,
            "analyses_total": analysis_count,
            "version": settings.app_version,
        }
    finally:
        db.close()
