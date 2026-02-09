Issues I Faced & How I Fixed Them (Short)

Wrong Python version

LlamaIndex required Python ≥3.10

Fixed by upgrading to Python 3.11 and recreating .venv

Virtual environment mismatch

Upgrading Python didn’t fix errors

Deleted and recreated .venv correctly

Module import failures (app not found)

Running scripts directly broke imports

Used python -m to run from project root

FastAPI couldn’t find app

app = FastAPI() missing or misplaced

Fixed file structure and __init__.py

Environment variables not loading

.env not detected reliably

Explicitly loaded .env path

OpenAI API quota exhausted

API returned 500 errors

Switched to local Ollama LLM (no API dependency)

Ingestion succeeded but retrieval returned empty

Vectors existed but were not retrievable

Debugged ingestion, persistence, and index loading separately

Implicit ingestion caused silent failures

Documents ingested but nodes not retrievable

Switched to explicit chunking and node creation

embedding not set error

Embeddings computed but not attached to nodes

Fixed by assigning embeddings directly to nodes

Collection mismatch in Chroma

Ingest and query used different collection logic

Unified collection name and access method

Broken imports due to partial edits

Functions missing despite file existing

Rewrote files cleanly instead of patching

Irrelevant chunks in answers

Low-score chunks polluted context

Added similarity score filtering

No source transparency

Answers couldn’t be audited

Added sources derived from retrieved metadata
