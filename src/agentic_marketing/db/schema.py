"""PostgreSQL database schema — production ready, no mocks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, Float, ForeignKey,
    Integer, String, Text, JSON, Index, UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

import enum
import uuid


Base = declarative_base()


# ── Enums ───────────────────────────────────────────────────────────────────

class PipelineStage(str, enum.Enum):
    RESEARCH = "research"
    STRATEGY = "strategy"
    BRIEF = "brief"
    COPY = "copy"
    CREATIVE = "creative"
    REPURPOSE = "repurpose"
    REVIEW = "review"
    PUBLISH = "publish"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    FAILED = "failed"


class Platform(str, enum.Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    BLOG = "blog"
    YOUTUBE = "youtube"
    THREADS = "threads"


class WorkspacePlan(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


# ── Workspace / Multi-tenant ─────────────────────────────────────────────────

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    plan = Column(SQLEnum(WorkspacePlan), default=WorkspacePlan.FREE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Usage limits
    monthly_campaigns = Column(Integer, default=3)
    monthly_posts = Column(Integer, default=50)
    api_calls_used = Column(Integer, default=0)
    api_calls_limit = Column(Integer, default=1000)

    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)

    # Settings — JSON blob for flexibility
    settings = Column(JSONB, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_workspaces_name", "name"),
        Index("ix_workspaces_stripe_customer_id", "stripe_customer_id"),
    )

    def __repr__(self) -> str:
        return f"<Workspace {self.name} ({self.plan})>"

    @property
    def is_usage_limit_reached(self) -> bool:
        return self.api_calls_used >= self.api_calls_limit


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False, default="member")  # owner, admin, editor, member, viewer
    invited_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member_user"),
        Index("ix_workspace_members_workspace_id", "workspace_id"),
        Index("ix_workspace_members_user_id", "user_id"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # OAuth
    oauth_provider = Column(String(50), nullable=True)
    oauth_provider_id = Column(String(255), nullable=True)

    last_login_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("email != ''", name="chk_user_email_not_empty"),
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False)  # SHA-256 hash of the actual key
    key_prefix = Column(String(10), nullable=False)  # First 8 chars for identification
    scopes = Column(ARRAY(String), default=list, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_api_keys_workspace_id", "workspace_id"),
        Index("ix_api_keys_key_hash", "key_hash"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    event_metadata = Column("audit_metadata", JSONB, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    __table_args__ = (
        Index("ix_audit_logs_workspace_id_created_at", "workspace_id", "created_at"),
    )


# ── Campaign & Content ────────────────────────────────────────────────────────

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False)
    topic = Column(String(500), nullable=False)  # The main topic/keyword
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False, index=True)

    # Goals
    target_platforms = Column(ARRAY(String), default=list, nullable=False)
    target_audience = Column(String(255), nullable=True)
    campaign_goal = Column(String(255), nullable=True)

    # Budget
    monthly_budget_usd = Column(Float, default=0.0, nullable=False)

    # Stats
    total_posts = Column(Integer, default=0, nullable=False)
    published_posts = Column(Integer, default=0, nullable=False)
    total_engagement = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_campaigns_workspace_id_status", "workspace_id", "status"),
        Index("ix_campaigns_workspace_id_created_at", "workspace_id", "created_at"),
    )


class PipelineExecution(Base):
    __tablename__ = "pipeline_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)

    topic = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False)

    # Stage tracking
    current_stage = Column(SQLEnum(PipelineStage), default=PipelineStage.RESEARCH, nullable=False)
    stage_status = Column(JSONB, default=dict, nullable=False)  # {"research": "completed", "copy": "in_progress", ...}

    # Overall status
    status = Column(String(50), default="running", nullable=False, index=True)  # running, completed, failed, cancelled
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Cost tracking
    llm_calls = Column(Integer, default=0, nullable=False)
    total_cost_usd = Column(Float, default=0.0, nullable=False)

    # Metadata
    triggered_by = Column(String(50), nullable=True)  # "api", "scheduler", "manual"
    execution_metadata = Column("execution_metadata", JSONB, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_pipeline_executions_workspace_id_status", "workspace_id", "status"),
        Index("ix_pipeline_executions_campaign_id", "campaign_id"),
        Index("ix_pipeline_executions_created_at", "created_at"),
    )


class ContentVariant(Base):
    """One version of copy for a platform."""
    __tablename__ = "content_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_executions.id"), nullable=False)

    approach = Column(String(50), nullable=False)  # problem_led, stat_led, outcome_led, etc.
    platform = Column(String(50), nullable=False)

    hook = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    cta = Column(Text, nullable=True)  # Call to action

    # Quality scores from review
    engagement_score = Column(Float, nullable=True)  # predicted 1-10
    quality_score = Column(Float, nullable=True)  # reviewed 1-10
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT, nullable=False)

    char_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)

    # Review notes
    review_notes = Column(Text, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_content_variants_execution_id", "execution_id"),
        Index("ix_content_variants_status", "status"),
    )


class ContentAsset(Base):
    """Images, video thumbnails, etc."""
    __tablename__ = "content_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_executions.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("content_variants.id"), nullable=True)

    asset_type = Column(String(50), nullable=False)  # image, video_thumbnail, banner
    platform = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=True)  # The prompt used to generate

    # Storage
    storage_url = Column(String(500), nullable=True)  # S3 or local path
    storage_key = Column(String(255), nullable=True)  # S3 key

    dimensions = Column(JSONB, default=dict, nullable=False)  # {"width": 1600, "height": 900}
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    # Generation metadata
    generation_method = Column(String(50), nullable=False)  # flux, dalle, upload
    model_used = Column(String(100), nullable=True)

    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_content_assets_execution_id", "execution_id"),
        Index("ix_content_assets_variant_id", "variant_id"),
    )


class PublishedPost(Base):
    """Content that has been published to a social platform."""
    __tablename__ = "published_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_executions.id"), nullable=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("content_variants.id"), nullable=True)

    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    content_text = Column(Text, nullable=True)
    media_urls = Column(ARRAY(String), default=list, nullable=False)

    # Platform post ID (for tracking)
    platform_post_id = Column(String(255), nullable=True, index=True)
    platform_post_url = Column(String(500), nullable=True)

    # Timing
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Engagement stats (fetched from platform API)
    impressions = Column(Integer, default=0, nullable=False)
    engagements = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    reach = Column(Integer, default=0, nullable=False)

    engagement_rate = Column(Float, nullable=True)
    last_stats_fetched_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(50), default="published", nullable=False)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_published_posts_workspace_id_platform", "workspace_id", "platform"),
        Index("ix_published_posts_campaign_id", "campaign_id"),
        Index("ix_published_posts_published_at", "published_at"),
    )


class AnalyticsEvent(Base):
    """Raw analytics events for time-series analysis."""
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("published_posts.id"), nullable=True)

    event_type = Column(String(100), nullable=False, index=True)  # impression, click, like, etc.
    event_value = Column(Integer, default=1, nullable=False)
    event_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Dimensions
    platform = Column(String(50), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), nullable=True)
    content_type = Column(String(50), nullable=True)

    analytics_metadata = Column("analytics_metadata", JSONB, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_analytics_events_workspace_timestamp", "workspace_id", "event_timestamp"),
        Index("ix_analytics_events_post_id", "post_id"),
    )


# ── Qdrant metadata (mirror for easy joins) ───────────────────────────────────

class VectorCollection(Base):
    """Tracks Qdrant collections linked to workspaces."""
    __tablename__ = "vector_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    collection_name = Column(String(255), nullable=False)
    vector_dim = Column(Integer, default=384, nullable=False)
    description = Column(Text, nullable=True)

    # Usage stats
    point_count = Column(Integer, default=0, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("workspace_id", "collection_name", name="uq_vector_collection_name"),
        Index("ix_vector_collections_workspace_id", "workspace_id"),
    )


# ── Database init ────────────────────────────────────────────────────────────

def init_db(engine):
    """Create all tables."""
    Base.metadata.create_all(engine)


def drop_db(engine):
    """Drop all tables (use with caution!)."""
    Base.metadata.drop_all(engine)