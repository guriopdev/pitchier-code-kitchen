import math
from typing import List, Optional
from app.core.config import settings
from app.core.logger import logger
from app.services.embeddings import embeddings_service
from app.models.vector import BenchmarkSlideResult, BenchmarkSearchResponse


# Pre-seeded benchmark winning pitch deck slides for offline / bootstrap mode
BENCHMARK_SEED_DECKS = [
    {
        "id": 1,
        "deck_name": "Stripe Seed Deck",
        "company_name": "Stripe",
        "slide_number": 1,
        "slide_type": "problem",
        "headline": "Accepting Payments Online Is Broken for Developers",
        "extracted_text": "Setting up merchant accounts takes weeks, requires faxing paperwork, and legacy gateways have archaic APIs with 0 developer ergonomics.",
    },
    {
        "id": 2,
        "deck_name": "Stripe Seed Deck",
        "company_name": "Stripe",
        "slide_number": 2,
        "slide_type": "solution",
        "headline": "7 Lines of Code to Accept Payments Globally",
        "extracted_text": "Simple REST API, instant developer onboarding, zero merchant account setup friction, and programmable webhooks for automated reconciliation.",
    },
    {
        "id": 3,
        "deck_name": "Airbnb Pitch Deck",
        "company_name": "Airbnb",
        "slide_number": 1,
        "slide_type": "problem",
        "headline": "Hotels Leave You Disconnected From Local Culture & Cost Too Much",
        "extracted_text": "Hotels are impersonal and expensive. No easy way for homeowners to monetize spare rooms or for travelers to book authentic local stays.",
    },
    {
        "id": 4,
        "deck_name": "Airbnb Pitch Deck",
        "company_name": "Airbnb",
        "slide_number": 3,
        "slide_type": "market",
        "headline": "2 Billion+ Trips Booked Annually Worldwide",
        "extracted_text": "TAM: 2 Billion+ trips booked worldwide. SAM: 560M budget and online travel bookings. SOM: 10.6M trips targeted for $200M revenue potential.",
    },
    {
        "id": 5,
        "deck_name": "Uber Cab Pitch Deck",
        "company_name": "Uber",
        "slide_number": 6,
        "slide_type": "business_model",
        "headline": "Digital Metering With Automated 20% Fee Per Ride",
        "extracted_text": "No physical meter equipment required. GPS calculates distance and time; credit cards are billed automatically with Uber collecting a 20% margin.",
    },
    {
        "id": 6,
        "deck_name": "Coinbase Seed Deck",
        "company_name": "Coinbase",
        "slide_number": 5,
        "slide_type": "traction",
        "headline": "Wallet Growth Compounding at 24% Month-Over-Month",
        "extracted_text": "Consumer wallets crossed 130,000 active accounts. Merchant integration volume expanding 4x quarter-over-quarter.",
    },
]


class VectorStoreService:
    """Client for AlloyDB / PostgreSQL pgvector vector similarity retrieval."""

    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.vector_db_type = settings.VECTOR_DB_TYPE
        self.mock_mode = settings.MOCK_GCP_SERVICES
        self.is_connected = False

        # In-memory vector store cache for offline/mock development
        self.in_memory_index = []
        self._initialize_in_memory_index()

    def _initialize_in_memory_index(self):
        """Pre-computes embeddings for benchmark seed decks."""
        for item in BENCHMARK_SEED_DECKS:
            text_to_embed = f"{item['headline']} {item['extracted_text']}"
            embedding = embeddings_service.get_embedding(text_to_embed)
            self.in_memory_index.append(
                {
                    **item,
                    "embedding": embedding,
                }
            )
        logger.info(
            f"Pre-seeded in-memory vector index with {len(self.in_memory_index)} benchmark deck slides."
        )

    async def search_similar_slides(
        self,
        query_text: str,
        slide_type: Optional[str] = None,
        top_k: int = 3,
    ) -> BenchmarkSearchResponse:
        """Retrieves the top-k most relevant benchmark slides using cosine distance."""
        query_vector = embeddings_service.get_embedding(query_text)

        # Try live AlloyDB / PostgreSQL vector search if connection string is configured
        if not self.mock_mode and self.vector_db_type in ["alloydb", "local"]:
            try:
                matches = await self._search_postgres_pgvector(
                    query_vector=query_vector,
                    slide_type=slide_type,
                    top_k=top_k,
                )
                if matches:
                    return BenchmarkSearchResponse(
                        query=query_text,
                        results_count=len(matches),
                        matches=matches,
                    )
            except Exception as e:
                logger.warning(
                    f"Live pgvector search failed ({e}). Falling back to in-memory vector index."
                )

        # Fallback: In-memory cosine similarity search
        return self._search_in_memory(
            query_vector=query_vector,
            query_text=query_text,
            slide_type=slide_type,
            top_k=top_k,
        )

    async def _search_postgres_pgvector(
        self,
        query_vector: List[float],
        slide_type: Optional[str],
        top_k: int,
    ) -> List[BenchmarkSlideResult]:
        """Executes native PostgreSQL pgvector HNSW index search using cosine distance (<=>)."""
        import asyncpg

        # Parse asyncpg DSN from SQLAlchemy URL
        dsn = self.db_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(dsn, timeout=5)

        try:
            vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

            if slide_type:
                query = """
                    SELECT id, deck_name, company_name, slide_number, slide_type,
                           headline, extracted_text,
                           1 - (embedding <=> $1::vector) AS similarity_score
                    FROM pitch_reference_embeddings
                    WHERE slide_type = $2
                    ORDER BY embedding <=> $1::vector
                    LIMIT $3;
                """
                rows = await conn.fetch(query, vector_str, slide_type, top_k)
            else:
                query = """
                    SELECT id, deck_name, company_name, slide_number, slide_type,
                           headline, extracted_text,
                           1 - (embedding <=> $1::vector) AS similarity_score
                    FROM pitch_reference_embeddings
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2;
                """
                rows = await conn.fetch(query, vector_str, top_k)

            results = []
            for r in rows:
                results.append(
                    BenchmarkSlideResult(
                        id=r["id"],
                        deck_name=r["deck_name"],
                        company_name=r["company_name"],
                        slide_number=r["slide_number"],
                        slide_type=r["slide_type"],
                        headline=r["headline"],
                        extracted_text=r["extracted_text"],
                        similarity_score=round(float(r["similarity_score"]), 4),
                    )
                )
            return results
        finally:
            await conn.close()

    def _search_in_memory(
        self,
        query_vector: List[float],
        query_text: str,
        slide_type: Optional[str],
        top_k: int,
    ) -> BenchmarkSearchResponse:
        """Calculates cosine similarity in Python over seeded benchmark decks."""
        scored = []

        for item in self.in_memory_index:
            if slide_type and item["slide_type"] != slide_type:
                continue

            # Compute cosine similarity: (A · B) / (||A|| * ||B||)
            item_vector = item["embedding"]
            dot_product = sum(a * b for a, b in zip(query_vector, item_vector))
            norm_a = math.sqrt(sum(a * a for a in query_vector))
            norm_b = math.sqrt(sum(b * b for b in item_vector))

            score = (
                (dot_product / (norm_a * norm_b))
                if (norm_a > 0 and norm_b > 0)
                else 0.0
            )

            scored.append((score, item))

        # Sort descending by similarity score
        scored.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored[:top_k]

        results = [
            BenchmarkSlideResult(
                id=item["id"],
                deck_name=item["deck_name"],
                company_name=item["company_name"],
                slide_number=item["slide_number"],
                slide_type=item["slide_type"],
                headline=item["headline"],
                extracted_text=item["extracted_text"],
                similarity_score=round(float(score), 4),
            )
            for score, item in top_matches
        ]

        return BenchmarkSearchResponse(
            query=query_text,
            results_count=len(results),
            matches=results,
        )


vector_store_service = VectorStoreService()
