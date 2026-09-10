#!/usr/bin/env python3
"""CLI pipeline script to ingest reference pitch deck PDFs using Document AI

and prepare them for vector indexing into AlloyDB.
"""

import os
import sys
import argparse
from pathlib import Path

# Add backend directory to sys.path so app modules can be imported
current_dir = Path(__file__).resolve().parent
repo_root = current_dir.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.services.document_ai import document_ai_service
from app.core.logger import logger


def ingest_pitch_deck(pdf_path: str):
    path = Path(pdf_path)
    if not path.exists() or not path.is_file():
        logger.error(f"Error: File not found at {pdf_path}")
        sys.exit(1)

    logger.info(f"Ingesting reference pitch deck: {path.name} ({path.stat().st_size} bytes)")

    with open(path, "rb") as f:
        pdf_bytes = f.read()

    parsed_deck = document_ai_service.parse_pdf_bytes(pdf_bytes, filename=path.name)

    logger.info(f"Successfully parsed {parsed_deck.total_slides} slides from {parsed_deck.deck_name}")
    for slide in parsed_deck.slides:
        print(f"  [Slide {slide.slide_number:02d}] ({slide.slide_type_guess or 'general'}): {slide.headline}")

    return parsed_deck


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a pitch deck PDF with Document AI")
    parser.add_argument("pdf_path", help="Path to the PDF file to ingest")
    args = parser.parse_args()

    ingest_pitch_deck(args.pdf_path)
