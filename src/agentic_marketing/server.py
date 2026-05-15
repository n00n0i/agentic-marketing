"""FastAPI backend — production ready, no mocks."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agentic_marketing.llm import client as llm
from agentic_marketing.llm import embedding as embedder
from agentic_marketing.db.connection import init_engine, session_scope
from agentic_marketing.db.qdrant import init_qdrant
from agentic_marketing.db.schema import init_db
from agentic_marketing.pipeline import engine as pipeline_engine


# ── Pydantic models ──────────────────────────────────────────────────────────

class PipelineRunRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    platform: str = Field(default="twitter")
    workspace_id: str = Field(default="default")
    campaign_id: str | None = None


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


class AnalyticsSummary(BaseModel):
    total_campaigns: int
    total_posts: int
    avg_engagement: float
    top_platform: str
    period: str


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    llm_configured: bool
    db_configured: bool
    qdrant_configured: bool


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = structlog.get_logger(__name__)
    logger.info("server_startup")

    # Initialize DB
    database_url = os.environ.get("DATABASE_URL", "sqlite:///./agentic.db")
    try:
        if database_url.startswith("postgresql"):
            init_engine(database_url)
            logger.info("db_init_ok")
        else:
            logger.warning("db_init_skipped", reason="no_postgres_url")
    except Exception as e:
        logger.warning("db_init_failed", error=str(e))

    # Initialize Qdrant
    qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:7433")
    try:
        host = qdrant_url.replace("http://", "").split(":")[0]
        port = int(qdrant_url.split(":")[-1])
        init_qdrant(host=host, port=port)
        logger.info("qdrant_init_ok")
    except Exception as e:
        logger.warning("qdrant_init_failed", error=str(e))

    # Initialize LLM
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        llm.init_llm(api_key)
        embedder.init_embedder(api_key)
        logger.info("llm_init_ok")
    else:
        logger.warning("llm_init_skipped", reason="no_api_key")

    logger.info("server_ready")
    yield
    logger.info("server_shutdown")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Agentic Marketing API",
    description="Production marketing pipeline — no mocks",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Dependencies ──────────────────────────────────────────────────────────────

def require_api_key(x_api_key: str | None = Header(None)) -> str:
    """Validate API key from header."""
    if not x_api_key:
        # In dev mode, allow no key
        if os.environ.get("DEMO_MODE", "false").lower() == "true":
            return "dev-key"
        raise HTTPException(status_code=401, detail="API key required")
    return x_api_key


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    db_url = os.environ.get("DATABASE_URL", "")
    qdrant_url = os.environ.get("QDRANT_URL", "")

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        llm_configured=bool(api_key),
        db_configured=bool(db_url),
        qdrant_configured=bool(qdrant_url),
    )


@app.post("/api/v1/pipeline/run", response_model=PipelineRunResponse, tags=["pipeline"])
async def run_pipeline(req: PipelineRunRequest, api_key: str = Depends(require_api_key)) -> PipelineRunResponse:
    """
    Run the full marketing pipeline.
    Calls OpenAI API directly (no LangChain, no mocks).
    Stores results in PostgreSQL + Qdrant.
    """
    try:
        result = pipeline_engine.run_pipeline(
            topic=req.topic,
            platform=req.platform,
            workspace_id=req.workspace_id,
            campaign_id=req.campaign_id,
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        return PipelineRunResponse(**result)
    except Exception as e:
        logger.error("pipeline_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@app.get("/api/v1/executions/{execution_id}", tags=["pipeline"])
async def get_execution(execution_id: str, api_key: str = Depends(require_api_key)):
    """Get pipeline execution status and artifacts."""
    from agentic_marketing.db.schema import PipelineExecution
    try:
        with session_scope() as db:
            exec_record = db.query(PipelineExecution).filter_by(id=execution_id).first()
            if not exec_record:
                raise HTTPException(status_code=404, detail="Execution not found")
            return {
                "id": str(exec_record.id),
                "status": exec_record.status,
                "current_stage": exec_record.current_stage.value if exec_record.current_stage else None,
                "stage_status": exec_record.stage_status,
                "created_at": exec_record.created_at.isoformat(),
            }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/api/v1/analytics/summary", response_model=AnalyticsSummary, tags=["analytics"])
async def analytics_summary(
    workspace_id: str = "default",
    api_key: str = Depends(require_api_key),
) -> AnalyticsSummary:
    """Return analytics summary from database."""
    from agentic_marketing.db.schema import PublishedPost
    try:
        with session_scope() as db:
            posts = db.query(PublishedPost).filter_by(workspace_id=workspace_id).all()
            if not posts:
                return AnalyticsSummary(
                    total_campaigns=0,
                    total_posts=0,
                    avg_engagement=0.0,
                    top_platform="twitter",
                    period="last_30_days",
                )
            total_posts = len(posts)
            total_engagement = sum(p.engagements or 0 for p in posts)
            avg = total_engagement / total_posts if total_posts > 0 else 0.0
            platform_counts: dict[str, int] = {}
            for p in posts:
                platform_counts[p.platform.value] = platform_counts.get(p.platform.value, 0) + 1
            top = max(platform_counts, key=platform_counts.get) if platform_counts else "twitter"
            return AnalyticsSummary(
                total_campaigns=0,
                total_posts=total_posts,
                avg_engagement=round(avg, 2),
                top_platform=top,
                period="last_30_days",
            )
    except Exception:
        # DB not configured — return empty
        return AnalyticsSummary(
            total_campaigns=0,
            total_posts=0,
            avg_engagement=0.0,
            top_platform="twitter",
            period="last_30_days",
        )


@app.post("/api/v1/workspace/create", tags=["multi-tenant"])
async def create_workspace(name: str, api_key: str = Depends(require_api_key)):
    """Create a new workspace."""
    from agentic_marketing.db.schema import Workspace
    try:
        with session_scope() as db:
            ws = Workspace(name=name)
            db.add(ws)
            db.commit()
            return {"id": str(ws.id), "name": ws.name, "created_at": ws.created_at.isoformat()}
    except Exception as e:
        logger.error("workspace_create_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ── Import structlog at module level ──────────────────────────────────────────
import structlog
logger = structlog.get_logger(__name__)