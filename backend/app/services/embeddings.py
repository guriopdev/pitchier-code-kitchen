import math
import hashlib
from typing import List
from app.core.config import settings
from app.core.logger import logger


class EmbeddingsService:
    """Service client for Google Cloud Vertex AI text-embedding-004."""

    EMBEDDING_DIM = 768

    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.location = settings.VERTEX_AI_LOCATION
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.mock_mode = settings.MOCK_GCP_SERVICES

        if not self.mock_mode:
            try:
                import vertexai
                from vertexai.language_models import TextEmbeddingModel

                vertexai.init(project=self.project_id, location=self.location)
                self.model = TextEmbeddingModel.from_pretrained(self.model_name)
                logger.info(
                    f"Vertex AI Embeddings initialized with model '{self.model_name}' (dim: {self.EMBEDDING_DIM})"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize live Vertex AI Embeddings: {e}. Falling back to deterministic mock embeddings."
                )
                self.mock_mode = True
        else:
            logger.info("Embeddings Service initialized in MOCK / LOCAL mode.")

    def get_embedding(self, text: str) -> List[float]:
        """Generates a 768-dimensional normalized embedding vector for a single text."""
        if not text or not text.strip():
            return [0.0] * self.EMBEDDING_DIM

        if self.mock_mode:
            return self._mock_embed_text(text)

        try:
            embeddings = self.model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
            logger.error(f"Error calling Vertex AI Embeddings API: {e}")
            logger.info("Falling back to deterministic mock embedding.")
            return self._mock_embed_text(text)

    def get_embeddings_batch(
        self, texts: List[str], batch_size: int = 5
    ) -> List[List[float]]:
        """Generates embeddings for a batch of text strings."""
        if not texts:
            return []

        if self.mock_mode:
            return [self._mock_embed_text(t) for t in texts]

        results: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            try:
                response = self.model.get_embeddings(chunk)
                for item in response:
                    results.append(item.values)
            except Exception as e:
                logger.error(f"Batch embedding error on chunk {i}: {e}")
                for text in chunk:
                    results.append(self._mock_embed_text(text))

        return results

    def _mock_embed_text(self, text: str) -> List[float]:
        """Generates a deterministic, unit-normalized 768-dimensional vector

        using SHA-256 hash seeds for offline testing.
        """
        # Create a deterministic seed from the text
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(self.EMBEDDING_DIM):
            # Deterministic pseudo-random generation based on byte stream
            byte_val = h[i % len(h)]
            multiplier = ((i * 31) % 100) / 50.0 - 1.0
            vector.append(float(byte_val * multiplier))

        # Normalize vector to unit length (for cosine similarity)
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]
        else:
            vector = [0.0] * self.EMBEDDING_DIM

        return vector


embeddings_service = EmbeddingsService()
