# ROADMAP.md — Startup Pitch Builder

This roadmap defines the 4 atomic, sequential phases to deliver a production-ready, open-source Startup Pitch Builder.

---

## Phase 1: Backend Boilerplate, Models & GCP Pipelines Setup
**Objective**: Establish the repository foundation, directory segregation, typed schemas, and containerization.

- [ ] **Task 1.1: Directory & Repository Layout Setup**
  - Create `/backend`, `/frontend`, `/pipelines`, `/infra`.
  - Set up root configuration, `.gitignore`, and base `.env.example`.
- [ ] **Task 1.2: FastAPI Application Core & Pydantic V2 Schemas**
  - Initialize FastAPI backend with CORS, middleware, structured logging, and configuration via `pydantic-settings`.
  - Define strict Pydantic schemas for the canonical 10-slide deck model:
    - `SlideType` enum (Problem, Solution, Market, Product, Traction, BusinessModel, GTM, Competition, Team, Ask).
    - `SlideContent`, `InvestorCritique` (strengths, red flags, hard questions), and complete `PitchDeck` container schema.
- [ ] **Task 1.3: GCP Infrastructure As Code (Terraform) & Dockerization**
  - Define `backend/Dockerfile` with production multi-stage build.
  - Create Terraform definitions in `/infra` for GCP services: Cloud Run, Artifact Registry, Document AI processor, AlloyDB instance, Vertex AI permissions.
  - Create `docker-compose.yml` for unified local development (FastAPI + local Postgres with pgvector).

---

## Phase 2: Ingestion & Vector Retrieval Engine
**Objective**: Enable Document AI pitch parsing and AlloyDB pgvector HNSW similarity search to power grounded deck generation.

- [ ] **Task 2.1: Document AI PDF Pitch Ingestion Service**
  - Implement `backend/app/services/document_ai.py` to ingest PDF pitch decks.
  - Extract text blocks, tables, and slide-by-slide structure.
  - Create ingestion pipeline CLI script in `pipelines/scripts/ingest_deck.py`.
- [ ] **Task 2.2: Vertex AI Embeddings Service**
  - Implement `backend/app/services/embeddings.py` using `text-embedding-004` (768 dimensions).
  - Batch embedding generator with caching and retries.
- [ ] **Task 2.3: AlloyDB pgvector Client with HNSW Indexing**
  - Implement `backend/app/services/vector_store.py` using SQLAlchemy / `asyncpg` + `pgvector`.
  - Configure HNSW index creation (`m = 16`, `ef_construction = 64`) on embedding column for ultra-fast cosine similarity retrieval.
  - Provide fallback support for local PostgreSQL + pgvector container.
  - Implement similarity search endpoint to retrieve top-k matching reference slides/sections.

---

## Phase 3: Gemini 2.5 10-Slide Deck Generation & PPTX Export
**Objective**: Transform raw notes into investor-grade 10-slide JSON payloads with critique tags and export to PowerPoint.

- [ ] **Task 3.1: Vertex AI Gemini 2.5 Generation Service**
  - Implement `backend/app/services/generator.py` using Vertex AI Gemini 2.5 (`gemini-2.5-pro` / `gemini-2.5-flash`).
  - Strict system prompt enforcing "Zero AI Buzzwords", quantitative metrics, bottom-up market sizing, and tier-1 venture partner critique criteria.
  - Native structured output enforcement using Gemini's JSON schema mode mapped to `PitchDeck` Pydantic model.
- [ ] **Task 3.2: FastAPI Pitch Generation & Stream Endpoints**
  - Implement `POST /api/v1/pitch/generate`: Accepts raw text notes, competitor URLs, target stage, and funding goals.
  - Implement Server-Sent Events (SSE) or status polling for real-time generation progress (e.g., "Analyzing notes...", "Retrieving benchmarks...", "Synthesizing 10 slides...", "Generating investor critique...").
- [ ] **Task 3.3: Native PowerPoint (.pptx) Export Engine**
  - Implement `backend/app/services/pptx_exporter.py` utilizing `python-pptx`.
  - Design premium 16:9 widescreen slide layouts with dark fintech aesthetics (dark backgrounds, high-contrast typography, metrics callouts, critique summary cards).
  - Expose `POST /api/v1/pitch/export/pptx` returning ready-to-download `.pptx` file.

---

## Phase 4: Fintech Dark-Mode Frontend with Framer Motion
**Objective**: Sleek Next.js interface with real-time deck preview, critique inspector, and interactive presentation slides.

- [ ] **Task 4.1: Next.js Boilerplate, Design System & Tailwind Configuration**
  - Initialize `/frontend` with Next.js (App Router), TypeScript, and Tailwind CSS.
  - Configure slate fintech color system (`slate-950`, `slate-900`, `slate-800`, subtle borders, cyan/emerald accents).
  - Install and configure shadcn/ui components (tabs, dialogs, buttons, badges, tooltips, cards).
- [ ] **Task 4.2: Founder Input Canvas & Generation Workflow**
  - Build interactive input dashboard: raw notes editor, voice/audio memo upload simulation, URL inputs, and target stage selector.
  - Streaming/progress tracker with Framer Motion animated states.
- [ ] **Task 4.3: Real-Time 10-Slide Deck Viewer & Critique Inspector**
  - 16:9 responsive slide preview canvas with thumbnail strip.
  - Slide-level toggles: View Slide vs. View Investor Critique (Strengths, Red Flags, Hard Questions).
  - Framer Motion transitions between slides and smooth layout animations.
- [ ] **Task 4.4: Export Suite & End-to-End Polish**
  - PowerPoint (`.pptx`) one-click download trigger.
  - Fullscreen Presentation Mode for web pitching.
  - End-to-end integration tests, README documentation, and demo verification.
