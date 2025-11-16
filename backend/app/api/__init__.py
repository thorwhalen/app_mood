from fastapi import APIRouter
from .auth import router as auth_router
from .moods import router as moods_router
from .datasets import router as datasets_router
from .models import router as models_router
from .analysis import router as analysis_router
from .tasks import router as tasks_router

api_router = APIRouter()

# Public routes (no auth required)
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Protected routes (auth required)
api_router.include_router(moods_router, prefix="/moods", tags=["moods"])
api_router.include_router(datasets_router, prefix="/datasets", tags=["datasets"])
api_router.include_router(models_router, prefix="/models", tags=["models"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
