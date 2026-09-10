from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General & App Server
    PROJECT_NAME: str = "Startup Pitch Builder API"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Google Cloud Platform
    GCP_PROJECT_ID: str = "startup-pitch-builder-dev"
    GCP_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # Vertex AI
    VERTEX_AI_LOCATION: str = "us-central1"
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    EMBEDDING_MODEL_NAME: str = "text-embedding-004"

    # Document AI
    DOCUMENT_AI_PROCESSOR_ID: str = ""
    DOCUMENT_AI_LOCATION: str = "us"

    # Vector Storage (AlloyDB / PostgreSQL)
    VECTOR_DB_TYPE: str = "local"  # 'alloydb' or 'local'
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/pitchbuilder"
    )

    # Offline / Mock Mode
    MOCK_GCP_SERVICES: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return [str(v)]


settings = Settings()
