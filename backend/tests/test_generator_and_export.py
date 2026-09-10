import pytest
from app.models.pitch import DeckGenerationRequest, PitchDeck
from app.services.generator import deck_generator_service
from app.services.pptx_exporter import pptx_exporter_service


@pytest.mark.asyncio
async def test_deck_generator_service():
    req = DeckGenerationRequest(
        company_name="ApexAI",
        raw_notes="Autonomous financial compliance engine for real-time payments.",
        target_round="Seed",
        target_amount="$2,000,000",
    )
    res = await deck_generator_service.generate_pitch_deck(req)
    assert res.deck_id.startswith("deck_")
    assert res.deck.company_name == "ApexAI"
    assert len(res.deck.slides) == 10
    assert res.deck.slides[0].slide_type.value == "problem"
    assert len(res.deck.slides[0].investor_critique.strengths) >= 1


def test_pptx_export_service():
    from app.services.generator import deck_generator_service
    req = DeckGenerationRequest(
        company_name="ApexAI",
        raw_notes="Sample notes for PPTX testing.",
    )
    deck = deck_generator_service._generate_mock_deck(req)
    pptx_bytes = pptx_exporter_service.export_deck_to_bytes(deck)
    assert len(pptx_bytes) > 5000  # Non-trivial presentation generated
    # PPTX files start with PK zip header bytes
    assert pptx_bytes[:2] == b"PK"
