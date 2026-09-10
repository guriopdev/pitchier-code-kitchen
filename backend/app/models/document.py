from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedSlideData(BaseModel):
    """Structured data extracted from a single pitch deck slide via Document AI."""

    slide_number: int = Field(..., description="Slide page number (1-indexed)")
    headline: str = Field(..., description="Inferred or extracted headline")
    raw_text: str = Field(..., description="Full text content extracted from the slide")
    detected_tables: List[List[List[str]]] = Field(
        default_factory=list, description="Extracted table cell matrices"
    )
    slide_type_guess: Optional[str] = Field(
        None, description="Heuristic classification: problem, solution, traction, etc."
    )


class DocumentAIParsedDeck(BaseModel):
    """Container for the entire parsed pitch deck document."""

    deck_name: str = Field(..., description="Deck filename or title")
    total_slides: int = Field(..., description="Total pages/slides processed")
    slides: List[ExtractedSlideData] = Field(
        default_factory=list, description="Extracted slides"
    )
    raw_full_text: str = Field(
        ..., description="Concatenated textual content of the entire document"
    )
