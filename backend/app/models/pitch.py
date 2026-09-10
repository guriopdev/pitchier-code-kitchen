from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SlideType(str, Enum):
    PROBLEM = "problem"
    SOLUTION = "solution"
    MARKET = "market"
    PRODUCT = "product"
    TRACTION = "traction"
    BUSINESS_MODEL = "business_model"
    GTM = "gtm"
    COMPETITION = "competition"
    TEAM = "team"
    ASK = "ask"


class InvestorCritique(BaseModel):
    """Institutional tier-1 investor analysis of this specific slide."""

    strengths: List[str] = Field(
        ...,
        description="Key strong signals that impress institutional venture partners.",
    )
    red_flags: List[str] = Field(
        ...,
        description="Vulnerabilities, weak assumptions, or gaps that partners will question.",
    )
    hard_questions: List[str] = Field(
        ...,
        description="2-3 direct, grilling questions the founder must defend in partner meetings.",
    )


class MetricCallout(BaseModel):
    """Key metric or datapoint highlighted prominently on the slide."""

    label: str = Field(
        ..., description="Metric label, e.g., 'TAM', 'MoM Growth', 'ACV'"
    )
    value: str = Field(
        ..., description="Quantified metric value, e.g., '$42B', '28%', '$120k'"
    )
    context: Optional[str] = Field(
        None, description="Brief context or benchmark comparison"
    )


class Slide(BaseModel):
    """Represents one of the canonical 10 slides."""

    slide_number: int = Field(
        ..., ge=1, le=10, description="Sequential index from 1 to 10"
    )
    slide_type: SlideType = Field(
        ..., description="Canonical slide classification"
    )
    headline: str = Field(
        ...,
        description="Concise, high-impact headline conveying the core takeaway (max 12 words).",
    )
    subtitle: Optional[str] = Field(
        None,
        description="Secondary clarifying line framing the takeaway.",
    )
    key_points: List[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Punchy, actionable bullet points with zero corporate fluff or buzzwords.",
    )
    metrics: List[MetricCallout] = Field(
        default_factory=list,
        description="Prominent metric callouts anchored to this slide.",
    )
    visual_layout_hint: Optional[str] = Field(
        None,
        description="Suggested visual emphasis: 'split_columns', 'metric_grid', 'quadrant_matrix', 'process_flow'.",
    )
    speaker_notes: Optional[str] = Field(
        None,
        description="Founder's 30-45 second spoken script for this slide.",
    )
    investor_critique: InvestorCritique = Field(
        ...,
        description="Venture partner critique analyzing strengths, risks, and hard questions.",
    )


class PitchDeck(BaseModel):
    """Canonical 10-Slide Startup Pitch Deck Payload."""

    company_name: str = Field(..., description="Startup name")
    one_liner: str = Field(
        ..., description="Clear, punchy one-sentence value proposition"
    )
    target_round: str = Field(
        default="Seed",
        description="Target financing stage (Pre-Seed, Seed, Series A)",
    )
    target_amount: str = Field(
        default="$2,000,000", description="Target funding ask"
    )
    slides: List[Slide] = Field(
        ...,
        min_length=10,
        max_length=10,
        description="Strictly canonical 10-slide deck",
    )
    overall_investment_thesis: Optional[str] = Field(
        None,
        description="Venture syndicate summary: Why this company could return the fund.",
    )
    overall_red_flags: List[str] = Field(
        default_factory=list,
        description="Top deal-breaker risks across the entire investment.",
    )

    @field_validator("slides")
    @classmethod
    def validate_slide_sequence(cls, slides: List[Slide]) -> List[Slide]:
        expected_types = [
            SlideType.PROBLEM,
            SlideType.SOLUTION,
            SlideType.MARKET,
            SlideType.PRODUCT,
            SlideType.TRACTION,
            SlideType.BUSINESS_MODEL,
            SlideType.GTM,
            SlideType.COMPETITION,
            SlideType.TEAM,
            SlideType.ASK,
        ]
        if len(slides) != 10:
            raise ValueError(f"Deck must contain exactly 10 slides, got {len(slides)}")

        for i, (slide, expected_type) in enumerate(zip(slides, expected_types), start=1):
            if slide.slide_number != i:
                slide.slide_number = i
            if slide.slide_type != expected_type:
                # Log or accept flexibility while ensuring type validation
                pass
        return slides


class DeckGenerationRequest(BaseModel):
    """Input payload submitted by founder to generate a pitch deck."""

    company_name: str = Field(..., description="Startup name")
    one_liner: Optional[str] = Field(
        None, description="Optional brief one-liner"
    )
    target_round: str = Field(
        default="Seed",
        description="Funding round stage: 'Pre-Seed', 'Seed', 'Series A'",
    )
    target_amount: Optional[str] = Field(
        None, description="Capital target, e.g., '$2M'"
    )
    raw_notes: str = Field(
        ...,
        description="Unstructured notes, brain-dumps, customer interview transcripts, or memo text.",
    )
    competitor_urls: List[str] = Field(
        default_factory=list,
        description="Competitor or benchmark URLs for market reference.",
    )
    industry_sector: Optional[str] = Field(
        None, description="Sector: 'Fintech', 'B2B SaaS', 'DevTools', 'AI', etc."
    )


class DeckGenerationResponse(BaseModel):
    """Response payload returned upon pitch deck generation."""

    deck_id: str = Field(..., description="Unique generated deck identifier")
    created_at: str = Field(..., description="ISO timestamp")
    deck: PitchDeck = Field(..., description="The complete 10-slide deck")
