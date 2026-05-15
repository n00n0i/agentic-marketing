# ── Stage 1: Backend — Python 3.12 slim ──────────────────────────────────────
FROM python:3.12-slim AS backend

WORKDIR /app

# Install Python deps directly (avoid hatchling editable install issues)
RUN pip install --no-cache-dir \
    fastapi uvicorn httpx structlog python-dotenv pydantic pydantic-settings \
    sqlalchemy asyncpg psycopg2-binary qdrant-client tenacity certifi

# Copy source
COPY src/ ./src/
COPY schemas/ ./schemas/
COPY skills/ ./skills/
COPY pipeline_defs/ ./pipeline_defs/

ENV PYTHONPATH=/app/src

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "agentic_marketing.server:app", "--host", "0.0.0.0", "--port", "8000"]


# ── Stage 2: Frontend — Node 22 Alpine ───────────────────────────────────────
FROM node:22-alpine AS frontend

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci --quiet

COPY frontend/ ./
RUN npm run build

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["node", "/app/node_modules/next/dist/bin/next", "start", "-p", "3000"]