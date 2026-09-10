from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """Service health and environment status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "vector_db_type": settings.VECTOR_DB_TYPE,
        "mock_mode": settings.MOCK_GCP_SERVICES,
        "gemini_model": settings.GEMINI_MODEL_NAME,
    }
