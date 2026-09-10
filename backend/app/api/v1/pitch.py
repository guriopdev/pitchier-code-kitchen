from fastapi import APIRouter, HTTPException, Response
from app.models.pitch import (
    DeckGenerationRequest,
    DeckGenerationResponse,
    PitchDeck,
)
from app.services.generator import deck_generator_service
from app.services.pptx_exporter import pptx_exporter_service

router = APIRouter()


@router.post(
    "/generate",
    response_model=DeckGenerationResponse,
    summary="Generate 10-Slide Pitch Deck with Gemini 2.5",
    tags=["Pitch Generation"],
)
async def generate_pitch_deck_endpoint(payload: DeckGenerationRequest):
    """Synthesizes founder notes into a canonical 10-slide deck

    with venture partner critique and quantitative metric anchors.
    """
    try:
        response = await deck_generator_service.generate_pitch_deck(payload)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Deck generation failed: {str(e)}"
        )


@router.post(
    "/export/pptx",
    summary="Export Pitch Deck to PowerPoint (.pptx)",
    tags=["Export"],
)
async def export_pitch_deck_pptx(deck: PitchDeck):
    """Exports a validated 10-slide pitch deck to a 16:9 widescreen PowerPoint file."""
    try:
        pptx_bytes = pptx_exporter_service.export_deck_to_bytes(deck)
        filename = f"{deck.company_name.lower().replace(' ', '_')}_pitch_deck.pptx"

        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"PPTX export failed: {str(e)}"
        )
