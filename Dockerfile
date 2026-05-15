# ── Stage 1: Backend — Python 3.12 slim ──────────────────────────────────────
FROM python:3.12-slim AS backend

WORKDIR /app

# Install deps (no langchain — we call OpenAI direct)
COPY pyproject.toml .env.example ./
RUN pip install --no-cache-dir -e ".[server]" httpx structlog python-dotenv pydantic pydantic-settings

# Copy source
COPY src/ ./src/
COPY schemas/ ./schemas/
COPY skills/ ./skills/
COPY pipeline_defs/ ./pipeline_defs/

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "agentic_marketing.server:app", "--host", "0.0.0.0", "--port", "8000"]


# ── Stage 2: Frontend — Node 22 Alpine ───────────────────────────────────────
FROM node:22-alpine AS frontend

WORKDIR /app

# Install deps
COPY frontend/package*.json ./
RUN npm ci --quiet

# Build (Next.js needs this to compile API routes)
COPY frontend/ ./
RUN npm run build

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

CMD ["node", "_modules/.bin/next", "start", "-p", "3000"]