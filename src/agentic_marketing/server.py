"""FastAPI backend — production API server."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agentic_marketing.api import run_pipeline as _run_pipeline
from agentic_marketing.multi_tenant import Workspace, WorkspaceMember
from agentic_marketing.config import settings


# ── Pydantic models ─────────────────────────────────────────────────────────

class PipelineRunRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500, description="Content topic/keyword")
    platform: str = Field(default="twitter", description="Primary target platform")
    workspace_id: str | None = Field(default=None, description="Multi-tenant workspace")


class PipelineRunResponse(BaseModel):
    execution_id: str
    status: str
    topic: str
    platform: str
    timestamp: str
    artifacts: dict[str, Any]
    stage_status: dict[str, str]
    total_cost_estimate: float
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    demo_mode: bool


# ── Lifespan ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = structlog.get_logger(__name__)
    logger.info("server_startup", version="0.1.0", demo_mode=settings.DEMO_MODE)
    yield
    logger.info("server_shutdown")


# ── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agentic Marketing API",
    description="LLM-driven full-funnel marketing content pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        demo_mode=settings.DEMO_MODE,
    )


@app.post("/api/v1/pipeline/run", response_model=PipelineRunResponse, tags=["pipeline"])
async def run_pipeline(req: PipelineRunRequest) -> PipelineRunResponse:
    """
    Trigger the marketing pipeline for a topic + platform.
    In demo mode, returns mock artifacts.
    In production, runs the full LangGraph pipeline.
    """
    result = _run_pipeline(topic=req.topic, platform=req.platform)
    return PipelineRunResponse(**result)


@app.get("/api/v1/workspace/{workspace_id}", tags=["multi-tenant"])
async def get_workspace(workspace_id: str) -> dict[str, Any]:
    """Get workspace details and member count."""
    workspace = Workspace.get_by_id(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    members = WorkspaceMember.get_by_workspace(workspace_id)
    return {
        "id": workspace.id,
        "name": workspace.name,
        "plan": workspace.plan,
        "created_at": workspace.created_at.isoformat(),
        "member_count": len(members),
    }


@app.get("/api/v1/analytics/summary", tags=["analytics"])
async def analytics_summary(workspace_id: str | None = None) -> dict[str, Any]:
    """Return analytics summary — mock data in demo mode."""
    return {
        "total_campaigns": 0,
        "total_posts": 0,
        "avg_engagement": 0.0,
        "top_platform": "twitter",
        "period": "last_30_days",
    }


# ── Uvicorn entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agentic_marketing.server:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEMO_MODE,
        workers=1,
    )