# Startup Pitch Builder 🚀

> Production-ready, open-source AI platform to transform raw founder notes, audio transcripts, and competitor links into investor-grade 10-slide pitch decks with institutional critique tags and PowerPoint export.

---

## 🏛️ Architecture Overview

- **Backend (`/backend`)**: FastAPI on Google Cloud Run, Vertex AI Gemini 2.5, Vertex AI Embeddings (`text-embedding-004`), AlloyDB for PostgreSQL with `pgvector` HNSW index, Document AI for pitch PDF ingestion, `python-pptx` exporter.
- **Frontend (`/frontend`)**: Next.js 14+ (App Router), Tailwind CSS, shadcn/ui, Framer Motion (monochrome slate fintech dark-mode theme, live deck preview, interactive critique inspector).
- **Pipelines (`/pipelines`)**: Benchmark dataset loaders and Document AI ingestion pipelines.
- **Infrastructure (`/infra`)**: Terraform configurations for GCP resources.

---

## 📂 Repository Structure

```
Startup-Pitch-Builder/
├── .planning/             # GSD workflow roadmap, project specs, and state tracker
├── backend/               # FastAPI application & GCP service integrations
├── frontend/              # Next.js 14+ fintech web application
├── pipelines/             # Reference deck ingestion & vector indexing pipelines
├── infra/                 # Terraform GCP deployment scripts
├── docker-compose.yml     # Local orchestration (FastAPI + pgvector)
├── .env.example           # Environment template
└── README.md              # Project documentation
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and `npm`
- Docker and Docker Compose
- Google Cloud SDK (`gcloud`) with active billing (or use `MOCK_GCP_SERVICES=true`)

### 2. Setup Environment
```bash
cp .env.example .env
```

### 3. Running Services
Refer to `/backend/README.md` and `/frontend/README.md` for specific service startup instructions.
