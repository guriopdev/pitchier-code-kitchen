from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_ai import document_ai_service
from app.models.document import DocumentAIParsedDeck

router = APIRouter()


@router.post(
    "/parse-pdf",
    response_model=DocumentAIParsedDeck,
    summary="Parse PDF Pitch Deck with Document AI",
    tags=["Ingestion"],
)
async def parse_pitch_deck_pdf(file: UploadFile = File(...)):
    """Accepts a pitch deck PDF, processes it with Google Cloud Document AI,

    and returns slide-by-slide extracted structured content.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF pitch decks are supported.",
        )

    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        parsed_deck = document_ai_service.parse_pdf_bytes(
            pdf_bytes=content, filename=file.filename
        )
        return parsed_deck

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process pitch deck PDF: {str(e)}"
        )
