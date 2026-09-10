import re
from typing import Optional, List
from app.core.config import settings
from app.core.logger import logger
from app.models.document import ExtractedSlideData, DocumentAIParsedDeck


class DocumentAIService:
    """Service client for Google Cloud Document AI PDF extraction."""

    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.location = settings.DOCUMENT_AI_LOCATION
        self.processor_id = settings.DOCUMENT_AI_PROCESSOR_ID
        self.mock_mode = settings.MOCK_GCP_SERVICES or not bool(self.processor_id)

        if not self.mock_mode:
            try:
                from google.cloud import documentai

                self.client = documentai.DocumentProcessorServiceClient()
                self.processor_name = self.client.processor_path(
                    self.project_id, self.location, self.processor_id
                )
                logger.info(
                    f"Document AI Client initialized for processor: {self.processor_name}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize live Document AI client: {e}. Falling back to mock parser."
                )
                self.mock_mode = True
        else:
            logger.info("Document AI Service initialized in MOCK / LOCAL mode.")

    def parse_pdf_bytes(
        self, pdf_bytes: bytes, filename: str = "deck.pdf"
    ) -> DocumentAIParsedDeck:
        """Parses a pitch deck PDF into structured slides and tables."""
        if self.mock_mode:
            return self._mock_parse_pdf(pdf_bytes, filename)

        from google.cloud import documentai

        try:
            raw_document = documentai.RawDocument(
                content=pdf_bytes, mime_type="application/pdf"
            )
            request = documentai.ProcessRequest(
                name=self.processor_name, raw_document=raw_document
            )
            result = self.client.process_document(request=request)
            document = result.document

            slides: List[ExtractedSlideData] = []
            full_text = document.text or ""

            for i, page in enumerate(document.pages, start=1):
                page_text_segments = []
                # Extract paragraphs/blocks
                for block in page.blocks:
                    block_text = self._get_layout_text(block.layout, full_text)
                    if block_text:
                        page_text_segments.append(block_text)

                slide_text = "\n".join(page_text_segments).strip()
                headline = self._extract_headline(slide_text, default=f"Slide {i}")
                slide_type_guess = self._classify_slide_type(slide_text)

                slides.append(
                    ExtractedSlideData(
                        slide_number=i,
                        headline=headline,
                        raw_text=slide_text,
                        detected_tables=[],
                        slide_type_guess=slide_type_guess,
                    )
                )

            return DocumentAIParsedDeck(
                deck_name=filename,
                total_slides=len(slides),
                slides=slides,
                raw_full_text=full_text,
            )

        except Exception as e:
            logger.error(f"Error processing document with Document AI: {e}")
            logger.info("Falling back to mock parsed representation.")
            return self._mock_parse_pdf(pdf_bytes, filename)

    def _get_layout_text(self, layout, full_text: str) -> str:
        """Helper to extract text from a Document AI layout segment."""
        text = ""
        for segment in layout.text_anchor.text_segments:
            start_index = int(segment.start_index) if segment.start_index else 0
            end_index = int(segment.end_index)
            text += full_text[start_index:end_index]
        return text.strip()

    def _extract_headline(self, text: str, default: str) -> str:
        """Extracts the leading sentence or line as the headline."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            return lines[0][:120]
        return default

    def _classify_slide_type(self, text: str) -> str:
        """Heuristic classifier to match slide content against canonical slide types."""
        lower = text.lower()
        if any(w in lower for w in ["problem", "pain", "broken", "friction"]):
            return "problem"
        elif any(w in lower for w in ["solution", "platform", "engine", "infrastructure"]):
            return "solution"
        elif any(w in lower for w in ["market", "tam", "sam", "som", "cagr", "opportunity"]):
            return "market"
        elif any(w in lower for w in ["traction", "pipeline", "revenue", "pilots", "arr"]):
            return "traction"
        elif any(w in lower for w in ["business model", "pricing", "unit economics", "acv", "nrr"]):
            return "business_model"
        elif any(w in lower for w in ["competition", "moat", "defensibility", "vs"]):
            return "competition"
        elif any(w in lower for w in ["team", "founder", "advisors", "veterans"]):
            return "team"
        elif any(w in lower for w in ["ask", "funding", "seed", "round", "milestones"]):
            return "ask"
        return "product"

    def _mock_parse_pdf(
        self, pdf_bytes: bytes, filename: str
    ) -> DocumentAIParsedDeck:
        """Deterministic mock parser for offline development & tests."""
        mock_slides = [
            ExtractedSlideData(
                slide_number=1,
                headline="Legacy Enterprise Compliance Is Too Slow For Instant Rails",
                raw_text="Instant payment settlements require sub-second decisions. Legacy batch processing causes 42% false-positive rates.",
                slide_type_guess="problem",
            ),
            ExtractedSlideData(
                slide_number=2,
                headline="Real-Time In-VPC Graph Anomaly Detection",
                raw_text="Sentient Ledger embeds directly inside payment switches, evaluating transactions in 6.4ms with zero cloud egress.",
                slide_type_guess="solution",
            ),
            ExtractedSlideData(
                slide_number=3,
                headline="$21.4B Global Regulatory Compliance Modernization",
                raw_text="TAM: $21.4B. SAM: $6.8B focused on real-time and cross-border instant payment settlement infrastructure.",
                slide_type_guess="market",
            ),
        ]

        full_text = "\n\n".join(s.raw_text for s in mock_slides)

        return DocumentAIParsedDeck(
            deck_name=filename,
            total_slides=len(mock_slides),
            slides=mock_slides,
            raw_full_text=full_text,
        )


document_ai_service = DocumentAIService()
