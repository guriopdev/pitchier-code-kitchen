from fastapi import APIRouter
from app.api.v1 import health, ingest, vector, pitch

api_router = APIRouter()
api_router.include_router(health.router, prefix="", tags=["Health"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
api_router.include_router(vector.router, prefix="/vector", tags=["Vector Search"])
api_router.include_router(pitch.router, prefix="/pitch", tags=["Pitch Generation & Export"])
