"""PostgreSQL models — SQLAlchemy ORM for agentic marketing core tables."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from psycopg2 import sql
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.pool import QueuePool

from ..config import DatabaseSettings

Base = declarative_base()


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------


class Timestamped:
    """Adds created_at / updated_at timestamps to a model."""

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class User(Base, Timestamped):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    external_id = Column(String(255), unique=True, nullable=True)  # SSO / external system ID
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="user")  # user | admin | reviewer
    is_active = Column(Boolean, nullable=False, default=True)
    metadata_ = Column("metadata", JSON, nullable=False, default=dict)

    # Relations
    campaigns = relationship("Campaign", back_populates="owner", cascade="all, delete-orphan")
    decision_logs = relationship("DecisionLog", back_populates="user", cascade="all, delete-orphan")


class Campaign(Base, Timestamped):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="draft")  # draft | active | paused | completed | archived
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Pipeline context
    execution_id = Column(String(100), nullable=True, index=True)  # Links to EP_STATE execution
    pipeline_manifest = Column(String(255), nullable=True)  # e.g. "agentic-marketing"
    enabled_channels = Column(ARRAY(String), nullable=False, default=list)  # [organic, paid, email]

    # Budget
    total_budget_usd = Column(Float, nullable=False, default=5.0)
    spent_usd = Column(Float, nullable=False, default=0.0)

    # Brand guidelines snapshot (JSON)
    brand_guidelines = Column(JSON, nullable=False, default=dict)

    # Result artifacts (JSON blob, small; large artifacts go to MongoDB)
    result_artifacts = Column(JSON, nullable=False, default=dict)
    result_artifacts_ref = Column(String(500), nullable=True)  # MongoDB collection/ref for large data

    # Relations
    owner = relationship("User", back_populates="campaigns")
    artifacts = relationship("Artifact", back_populates="campaign", cascade="all, delete-orphan")
    decision_logs = relationship("DecisionLog", back_populates="campaign", cascade="all, delete-orphan")
    stage_attempts = relationship("StageAttempt", back_populates="campaign", cascade="all, delete-orphan")


class Artifact(Base, Timestamped):
    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)

    artifact_type = Column(String(100), nullable=False, index=True)  # market_brief, copy_variants, etc.
    artifact_id = Column(String(100), nullable=False, index=True)  # e.g. "mb-001", "cv-001"
    version = Column(Integer, nullable=False, default=1)

    # Content can be stored inline (small) or as a ref (large)
    content = Column(JSON, nullable=True)  # Inline for small artifacts
    content_ref = Column(String(500), nullable=True)  # MongoDB ref for large artifacts

    # Stage provenance
    stage_name = Column(String(100), nullable=False, index=True)
    director_skill = Column(String(255), nullable=True)

    # Review
    review_status = Column(String(50), nullable=False, default="pending")  # pending | approved | revise | pass_with_warnings
    review_round = Column(Integer, nullable=False, default=0)
    chai_score = Column(JSON, nullable=True)  # {"C": 8, "H": 9, "A": 8, "I": 7, "C": 8}

    # Validation
    schema_valid = Column(Boolean, nullable=False, default=True)
    validation_errors = Column(JSON, nullable=False, default=list)

    # Relations
    campaign = relationship("Campaign", back_populates="artifacts")
    decision_logs = relationship("DecisionLog", back_populates="artifact")


class StageAttempt(Base, Timestamped):
    __tablename__ = "stage_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    execution_id = Column(String(100), nullable=True, index=True)

    stage_name = Column(String(100), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False, default=1)

    status = Column(String(50), nullable=False, default="pending")  # pending | in_progress | approved | revision | pass_with_warnings | failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Cost tracking
    estimated_cost_usd = Column(Float, nullable=True)
    actual_cost_usd = Column(Float, nullable=True)

    # Artifacts produced (ref only, full content in MongoDB)
    artifacts_ref = Column(JSON, nullable=False, default=list)  # [{artifact_id, artifact_type}, ...]

    # Errors
    errors = Column(ARRAY(String), nullable=False, default=list)

    # Relations
    campaign = relationship("Campaign", back_populates="stage_attempts")


class DecisionLog(Base, Timestamped):
    __tablename__ = "decision_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    artifact_id = Column(UUID(as_uuid=True), ForeignKey("artifacts.id"), nullable=True)

    execution_id = Column(String(100), nullable=True, index=True)
    decision_id = Column(String(100), nullable=False, unique=True, index=True)  # dec-xxxxxxxx

    stage = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # channel_selection, budget_allocation, etc.
    subject = Column(Text, nullable=False)

    options_considered = Column(JSON, nullable=False, default=list)
    selected = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)

    confidence = Column(Float, nullable=True)
    user_visible = Column(Boolean, nullable=False, default=True)
    user_approved = Column(Boolean, nullable=False, default=False)

    # Relations
    campaign = relationship("Campaign", back_populates="decision_logs")
    user = relationship("User", back_populates="decision_logs")
    artifact = relationship("Artifact", back_populates="decision_logs")


# ---------------------------------------------------------------------------
# Engine / session helpers
# ---------------------------------------------------------------------------


def create_engine_and_session(settings: DatabaseSettings) -> tuple[Any, Session]:
    """
    Create a SQLAlchemy engine and session maker.

    Caller is responsible for closing the session.
    """
    engine = create_engine(
        settings.url,
        poolclass=QueuePool,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_pre_ping=True,
        echo=False,
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, SessionLocal


def init_db(engine: Any) -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    # Create UUID extension for UUID generation
    with engine.connect() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")


def get_session(settings: DatabaseSettings) -> Session:
    """Get a new DB session (caller must close)."""
    _, SessionLocal = create_engine_and_session(settings)
    return SessionLocal()