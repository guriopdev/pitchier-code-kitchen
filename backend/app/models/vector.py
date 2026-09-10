from typing import List, Optional
from pydantic import BaseModel, Field


class BenchmarkSlideQuery(BaseModel):
    """Query payload to find similar reference pitch deck slides."""

    query_text: str = Field(
        ...,
        description="Founder note snippet or slide topic to benchmark against winning decks.",
    )
    slide_type: Optional[str] = Field(
        None,
        description="Optional filter by slide type (e.g. 'problem', 'solution', 'traction').",
    )
    top_k: int = Field(
        default=3, ge=1, le=10, description="Number of top similar slides to retrieve"
    )


class BenchmarkSlideResult(BaseModel):
    """A matched reference slide from AlloyDB vector storage."""

    id: int = Field(..., description="Unique reference record ID")
    deck_name: str = Field(..., description="Reference deck title (e.g., 'Airbnb', 'Uber', 'Stripe')")
    company_name: str = Field(..., description="Company name")
    slide_number: int = Field(..., description="Slide page index")
    slide_type: str = Field(..., description="Slide classification")
    headline: str = Field(..., description="Reference slide headline")
    extracted_text: str = Field(..., description="Full reference slide content")
    similarity_score: float = Field(
        ..., description="Cosine similarity score (0.0 to 1.0)"
    )


class BenchmarkSearchResponse(BaseModel):
    """Response containing retrieved reference slides."""

    query: str = Field(..., description="Original search query")
    results_count: int = Field(..., description="Total retrieved matches")
    matches: List[BenchmarkSlideResult] = Field(
        default_factory=list, description="Top-k matching benchmark slides"
    )
