from fastapi import APIRouter, Query
from app.services.vector_store import vector_store_service
from app.models.vector import BenchmarkSlideQuery, BenchmarkSearchResponse

router = APIRouter()


@router.post(
    "/search",
    response_model=BenchmarkSearchResponse,
    summary="Search Similar Benchmark Pitch Slides",
    tags=["Vector Search"],
)
async def search_benchmark_slides(payload: BenchmarkSlideQuery):
    """Retrieves top-k benchmark slides from AlloyDB / pgvector using Vertex AI embeddings

    and HNSW index cosine distance similarity.
    """
    results = await vector_store_service.search_similar_slides(
        query_text=payload.query_text,
        slide_type=payload.slide_type,
        top_k=payload.top_k,
    )
    return results


@router.get(
    "/search",
    response_model=BenchmarkSearchResponse,
    summary="Quick Search Benchmark Slides via Query String",
    tags=["Vector Search"],
)
async def search_benchmark_slides_get(
    q: str = Query(..., description="Query phrase or slide topic"),
    slide_type: str = Query(None, description="Optional slide category filter"),
    top_k: int = Query(3, ge=1, le=10, description="Top matches to retrieve"),
):
    """Convenience GET endpoint for similarity search."""
    results = await vector_store_service.search_similar_slides(
        query_text=q,
        slide_type=slide_type,
        top_k=top_k,
    )
    return results
