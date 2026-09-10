-- Initialize pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Benchmark Pitch Decks vector table
CREATE TABLE IF NOT EXISTS pitch_reference_embeddings (
    id SERIAL PRIMARY KEY,
    deck_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    industry_sector VARCHAR(100),
    slide_number INT NOT NULL,
    slide_type VARCHAR(50) NOT NULL,
    headline TEXT NOT NULL,
    extracted_text TEXT NOT NULL,
    -- Vertex AI text-embedding-004 produces 768-dimensional embeddings
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create HNSW index with cosine distance for sub-10ms vector similarity lookup
CREATE INDEX IF NOT EXISTS idx_pitch_embeddings_hnsw_cosine
ON pitch_reference_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
