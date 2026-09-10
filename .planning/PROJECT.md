# PROJECT.md — Startup Pitch Builder

## 1. Project Overview & Mission
**Startup Pitch Builder** is a production-ready, open-source AI platform designed to transform messy, unstructured founder inputs (raw thoughts, markdown notes, audio transcripts, competitor links) into an investor-grade 10-slide pitch deck. 

It features an intelligent backend on Google Cloud Platform that stress-tests founder claims, compares patterns with historical winning decks via vector retrieval, and outputs strict, validated 10-slide JSON payloads. The frontend delivers a dark-mode fintech aesthetic with live deck rendering, interactive critique inspection, and native export to PowerPoint (`.pptx`) and presentation web slides.

---

## 2. System Architecture & Tech Stack

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14+)                   │
│   Tailwind CSS • shadcn/ui • Framer Motion • Lucide Icons   │
│   (Slate Fintech Theme, Real-Time Deck Canvas, PPTX Export) │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / SSE / REST
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI on Cloud Run)            │
│   Pydantic V2 • Structured Schemas • Async Tasks & Streaming│
└──────────────┬───────────────┬────────────────┬─────────────┘
               │               │                │
               ▼               ▼                ▼
     ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐
     │  Document AI   │ │  Vertex AI   │ │ AlloyDB for PG   │
     │  (PDF Deck     │ │  Gemini 2.5  │ │  (pgvector HNSW  │
     │   Ingestion)   │ │  Embeddings  │ │   Similarity)    │
     └────────────────┘ └──────────────┘ └──────────────────┘
```

### Core Technology Stack

#### **Backend (`/backend`)**
- **Framework**: Python 3.11+, FastAPI, Uvicorn, Pydantic V2.
- **Compute**: Google Cloud Run (containerized, serverless autoscaling, HTTP/2, SSE enabled).
- **LLM Engine**: Vertex AI Gemini 2.5 (`gemini-2.5-pro` / `gemini-2.5-flash`) for note synthesis, critical stress-testing, and strict JSON schema generation.
- **Embeddings**: Vertex AI `text-embedding-004` (768-dim embeddings).
- **Vector Database**: AlloyDB for PostgreSQL with `pgvector` extension utilizing **HNSW** (Hierarchical Navigable Small World) index for low-latency sub-10ms similarity searches.
- **Document Processing**: Google Cloud Document AI (Form/Document Parser) for digitizing reference pitch decks (PDFs).
- **Slide Generator**: `python-pptx` for generating high-definition `.pptx` decks natively.

#### **Frontend (`/frontend`)**
- **Framework**: Next.js (App Router), React, TypeScript.
- **Styling**: Tailwind CSS, PostCSS, Lucide-react.
- **Component Primitives**: shadcn/ui (Radix UI primitives).
- **Aesthetics & Motion**: Monochrome slate dark-mode palette (`slate-950`/`slate-900`/`slate-800`), subtle glassmorphism borders (`border-white/10`, `backdrop-blur-md`), fluid Framer Motion micro-interactions.
- **Deck Rendering & Export**: Native SVG/Canvas preview + Client-side/Server-side PowerPoint export.

#### **Pipelines & Infrastructure (`/pipelines`, `/infra`)**
- **Pipelines**: Python ingestion scripts for parsing benchmark decks, computing embeddings, and batch indexing into AlloyDB.
- **IaC**: Terraform configurations for GCP (Artifact Registry, Cloud Run, Document AI Processor, Secret Manager, AlloyDB cluster & instances).
- **Containers**: Multi-stage production `Dockerfile`s for backend and frontend.

---

## 3. Strict Non-Negotiables & Rules of the Deck

1. **Zero AI Buzzwords**:
   - The LLM generation prompt strictly bans generic filler words: "revolutionary", "game-changing", "disruptive", "paradigm shift", "leverage", "uniquely positioned", "next-generation".
   - Claims must be concrete, metric-anchored, and operationalized.

2. **Strict 10-Slide Canonical Deck Format**:
   Every generated deck adheres strictly to the canonical 10-slide sequence:
   1. **Problem**: Clear, painful, validated problem statement with quantifiable impact.
   2. **Solution**: Precise value proposition, mechanism of action, unfair advantage.
   3. **Market Opportunity**: TAM / SAM / SOM with bottom-up derivation.
   4. **Product**: Key capabilities, architecture, and current status (MVP/Beta/GA).
   5. **Traction & Milestones**: Actual metrics, cohort retention, MOM growth, or pilot validation.
   6. **Business Model**: Unit economics, pricing strategy, ACV, CAC/LTV dynamics.
   7. **Go-to-Market (GTM)**: Acquisition flywheels, sales motion, distribution channels.
   8. **Competitive Landscape**: Defensibility matrix, why incumbents can't copy.
   9. **Team**: Founders, operational track record, domain authority.
   10. **The Ask & Use of Funds**: Target funding amount, runway extension, milestone objectives.

3. **Investor-Grade Critique Tags**:
   - Each slide payload includes an `investor_critique` object containing:
     - `strengths`: What an institutional Tier-1 investor likes.
     - `red_flags`: What partners will grill the founder on in Partner Meeting.
     - `hard_questions`: 2-3 specific questions the founder must prepare for.

4. **Architecture Isolation**:
   - No spaghetti code: Strict separation of `/frontend`, `/backend`, `/pipelines`, and `/infra`.
   - All AI interactions run through abstracted service layers with typed Pydantic models.
   - Comprehensive error handling and fallbacks for mock/local offline development mode.

---

## 4. Directory Structure Standard

```
Startup-Pitch-Builder/
├── .planning/             # GSD Workflow Roadmap, State, and Specs
│   ├── PROJECT.md
│   ├── ROADMAP.md
│   └── STATE.md
├── backend/               # FastAPI Application
│   ├── app/
│   │   ├── api/           # API routes (v1)
│   │   ├── core/          # Config, logging, security
│   │   ├── models/        # Pydantic schemas (10-slide spec, critique spec)
│   │   ├── services/      # Vertex AI, Document AI, AlloyDB vector client, PPTX engine
│   │   └── main.py        # Entrypoint
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # Next.js Application
│   ├── src/
│   │   ├── app/           # App router pages & layouts
│   │   ├── components/    # UI components (Deck Canvas, Slide Preview, Critique Panel)
│   │   ├── lib/           # API client, utility functions
│   │   └── types/         # TypeScript deck definitions
│   ├── public/
│   ├── package.json
│   └── tailwind.config.ts
├── pipelines/             # Ingestion & Benchmark Datasets
│   ├── scripts/           # Ingest PDF pitch decks to AlloyDB
│   ├── sample_decks/      # Curated reference pitch deck samples
│   └── requirements.txt
├── infra/                 # Terraform GCP Infrastructure
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── docker-compose.yml     # Local orchestration
└── README.md              # Complete setup and architecture documentation
```
