import pytest
from app.models.pitch import (
    SlideType,
    Slide,
    InvestorCritique,
    MetricCallout,
    PitchDeck,
)


def test_investor_critique_creation():
    critique = InvestorCritique(
        strengths=["Defensible IP and deep customer lock-in."],
        red_flags=["Sales cycle is 9+ months with high enterprise CAC."],
        hard_questions=["How will you scale without linear headcount growth?"],
    )
    assert len(critique.strengths) == 1
    assert len(critique.red_flags) == 1
    assert len(critique.hard_questions) == 1


def test_pitch_deck_validation():
    slides = []
    slide_types = [
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

    for idx, st in enumerate(slide_types, start=1):
        slides.append(
            Slide(
                slide_number=idx,
                slide_type=st,
                headline=f"Slide {idx} Headline",
                key_points=["Validated point 1", "Validated point 2"],
                metrics=[MetricCallout(label="Metric", value="100k")],
                investor_critique=InvestorCritique(
                    strengths=["Strong thesis"],
                    red_flags=["Potential market risk"],
                    hard_questions=["What is your moat?"],
                ),
            )
        )

    deck = PitchDeck(
        company_name="ApexAI",
        one_liner="Autonomous compliance infrastructure for enterprise fintech.",
        target_round="Seed",
        target_amount="$2,500,000",
        slides=slides,
    )

    assert deck.company_name == "ApexAI"
    assert len(deck.slides) == 10
    assert deck.slides[0].slide_type == SlideType.PROBLEM
    assert deck.slides[9].slide_type == SlideType.ASK
