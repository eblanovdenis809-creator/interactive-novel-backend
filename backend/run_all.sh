#!/usr/bin/env bash
set -euo pipefail

# Combined API + Bot in one process (fits Render free tier)
# DB is initialized automatically on startup via FastAPI lifespan
echo "Starting combined API + Bot server on port ${PORT:-8000}..."
uvicorn backend.api:app --host 0.0.0.0 --port "${PORT:-8000}"
