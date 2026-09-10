import pytest
from app.services.embeddings import embeddings_service
from app.services.vector_store import vector_store_service


def test_embedding_generation():
    text = "Instant payment settlement infrastructure for global banking."
    vec = embeddings_service.get_embedding(text)
    assert len(vec) == 768
    # Test batch embedding
    batch = embeddings_service.get_embeddings_batch([text, "Another slide headline."])
    assert len(batch) == 2
    assert len(batch[0]) == 768


@pytest.mark.asyncio
async def test_vector_similarity_search():
    query = "Developer API for payments and checkout"
    response = await vector_store_service.search_similar_slides(query_text=query, top_k=2)
    assert response.results_count >= 1
    top_match = response.matches[0]
    assert top_match.company_name in ["Stripe", "Airbnb", "Uber", "Coinbase"]
    assert top_match.similarity_score > 0.0
