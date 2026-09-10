# Pitchier — Institutional Startup Pitch Builder 🚀

> **Transform raw founder thoughts, chaotic notes, and napkin unit economics into an investor-ready 10-slide pitch deck — complete with native charts, strategic moat analysis, and harsh venture partner critiques.**

---

## 🌟 Key Features

- **Strict 10-Slide Institutional Blueprint**: Generates Problem, Solution, Market Sizing, Product, Traction, Business Model / Waterfall, Go-To-Market, Competitive Moat, Team, and The Ask.
- **Native SVG Visualizations**: Interactive Donut/Pie charts for waterfall revenue splits and proportional Bar charts for market sizing & sales velocity.
- **Venture Partner Critique & Diligence Simulator**: Dual-mode canvas showing strengths, red flags, and ruthless diligence grilling questions for every slide.
- **Institutional Strategic Analysis**: Automated moat ratings (`High`, `Defensible`, `Developing`), margin defense evaluations, and unit economics verdicts.
- **16:9 Widescreen PowerPoint Export**: Download real `.pptx` presentations with embedded presenter notes — works seamlessly via backend or instant browser synthesis.
- **Hallmark Editorial Design**: Built with warm oat/beige paper tones (`#f9f7f2`), high typographic contrast, and hairline borders — zero AI buzzwords or generic templates.

---

## 🏛️ System Architecture

```
                    ┌─────────────────────────┐
                    │     Frontend UI         │
                    │ Next.js 16 + React 19   │
                    │ Tailwind + pptxgenjs    │
                    └────────────┬────────────┘
                                 │ HTTP / REST
                    ┌────────────▼────────────┐
                    │    FastAPI Backend      │
                    │      Port: 8000         │
                    └──────┬───────────┬──────┘
                           │           │
           ┌───────────────▼┐         ┌▼─────────────────────────┐
           │ Vertex AI      │         │ PostgreSQL + pgvector     │
           │ Gemini 2.5     │         │ (AlloyDB / Docker pg16)   │
           │ Embeddings 004 │         │ 768-dim HNSW Vector Index │
           └────────────────┘         └──────────────────────────┘
```

---

## 🚀 Getting Started

You can run Pitchier either using **Docker Compose** (recommended for full-stack with vector database) or **Locally** for instant frontend preview.

### Option 1: Quickstart with Docker Compose (Full Stack)

This launches the FastAPI backend and the PostgreSQL `pgvector` container with pre-configured HNSW vector indices.

#### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

#### 2. Clone the repository
```bash
git clone https://github.com/guriopdev/pitchier-code-kitchen.git
cd pitchier-code-kitchen
```

#### 3. Configure Environment Variables
```bash
cp .env.example .env
```
*(For offline/local development without GCP credentials, set `MOCK_GCP_SERVICES=true` in `.env`)*.

#### 4. Spin up Containers
```bash
docker compose up --build
```
- **Backend API**: `http://localhost:8000`
- **Swagger API Docs**: `http://localhost:8000/docs`
- **Vector Database (PostgreSQL)**: `localhost:5432`

#### 5. Run Frontend
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

### Option 2: Running Locally Without Docker

If you just want to run and test the frontend and presentation builder immediately:

#### 1. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
- Access the web interface at **`http://localhost:3000`**.
- The presentation canvas and **"Export 16:9 Deck (.pptx)"** features are 100% operational in the browser using client-side synthesis even when the backend is offline.

#### 2. Start the Backend (Optional)
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 📥 Presentation & Export Guide

### How to Generate a Pitch Deck:
1. Open `http://localhost:3000`.
2. Click on the **"Slide Synthesis Studio"** tab.
3. Enter your **Company Name**, **Target Round**, **Target Amount**, and paste your raw notes (e.g. *Your revenue split, business model, customer numbers*).
4. Click **"Compile Structured Deck"**.
5. Browse slides 1 through 10 using the bottom dock or navigation arrows.

### How to Download PowerPoint (.pptx):
- Click the **"Export 16:9 Deck (.pptx)"** button in the top right navigation bar.
- The presentation will immediately download to your computer as `[company_name]_pitch_deck.pptx`.
- Open it in **Microsoft PowerPoint**, **Google Slides**, or **Keynote**. Speaker notes are automatically included in presenter view.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16.3 (Turbopack), React 19, Tailwind CSS, Framer Motion, Lucide Icons |
| **Presentation Export** | `pptxgenjs` (Client-side) & `python-pptx` (Backend Cloud Run) |
| **Backend API** | FastAPI, Pydantic v2, Python 3.11+ |
| **LLM & AI Engine** | Google Gemini 2.5 Flash on Vertex AI |
| **Ingestion & OCR** | Google Document AI (for PDF pitch deck parsing) |
| **Vector Search** | PostgreSQL 16 + `pgvector` (Cosine distance with HNSW index) / Google AlloyDB |
| **Infrastructure** | Terraform, Docker, Google Cloud Run |

---

## 📁 Repository Structure

```
pitchier-code-kitchen/
├── backend/               # FastAPI backend service
│   ├── app/
│   │   ├── api/v1/        # Endpoints for pitch generation, ingest, vector search, export
│   │   ├── core/          # GCP config & logging
│   │   ├── models/        # Pydantic data schemas
│   │   └── services/      # Gemini 2.5 generator, embeddings, pptx builder
│   ├── tests/             # Backend test suites
│   ├── Dockerfile         # Multi-stage production container
│   └── requirements.txt
├── frontend/              # Next.js web application
│   ├── src/
│   │   ├── app/           # App router & global styles
│   │   ├── components/    # PitchBuilderApp & SlideChartVisualizer
│   │   ├── lib/           # Client deck synthesizer & pptx-client-exporter
│   │   └── types/         # TypeScript deck interfaces
│   └── package.json
├── infra/                 # Terraform scripts for GCP (Cloud Run, AlloyDB, DocAI)
├── pipelines/             # Reference deck ingestion scripts
├── docker-compose.yml     # Local orchestration (FastAPI + pgvector)
├── .env.example           # Environment template
└── README.md
```

---

## 📄 License
MIT License. Built for hackathons and early-stage founders.
