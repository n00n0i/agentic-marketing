"""Multi-tenant models — Workspace, API key, audit log."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

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
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from . import Base


# ---------------------------------------------------------------------------
# Timestamped is imported from the models module to avoid circular imports
# ---------------------------------------------------------------------------


class Timestamped:
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Workspace(Base, Timestamped):
    """
    Top-level tenant container.

    Hierarchy: Workspace → User (member) → Campaign
    """
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)  # URL-safe identifier
    plan = Column(String(50), nullable=False, default="free")  # free | starter | pro | enterprise
    is_active = Column(Boolean, nullable=False, default=True)

    # Limits
    max_campaigns = Column(Integer, nullable=False, default=3)
    max_users = Column(Integer, nullable=False, default=1)
    max_budget_usd = Column(Float, nullable=False, default=100.0)

    # Features
    enabled_channels = Column(JSON, nullable=False, default=list)  # ["organic", "paid", "email"]
    settings = Column(JSON, nullable=False, default=dict)

    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    billing_email = Column(String(255), nullable=True)

    # Relations
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="workspace", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="workspace", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="workspace", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_workspaces_plan", "plan"),
    )


class WorkspaceMember(Base, Timestamped):
    """
    User membership in a workspace with role-based access control.

    Roles:
    - owner: full access, can delete workspace
    - admin: manage users, campaigns, settings
    - editor: create/edit campaigns
    - viewer: read-only access
    """
    __tablename__ = "workspace_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    role = Column(String(50), nullable=False, default="editor")  # owner | admin | editor | viewer
    is_active = Column(Boolean, nullable=False, default=True)

    # Relations
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")

    __table_args__ = (
        Index("ix_workspace_members_unique", "workspace_id", "user_id", unique=True),
    )


class APIKey(Base, Timestamped):
    """
    Long-lived API key for programmatic workspace access.

    Stored in plaintext only at creation time — only the hash is kept after.
    """
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)

    name = Column(String(255), nullable=False)  # "Production Key", "CI/CD Key"
    key_prefix = Column(String(16), nullable=False)  # First 8 chars shown in UI (e.g. "amk_live_")
    key_hash = Column(String(255), nullable=False, unique=True)  # SHA-256 hash

    scopes = Column(JSON, nullable=False, default=list)  # ["campaigns:read", "campaigns:write", "analytics:read"]
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Rate limit customisation
    rate_limit_per_minute = Column(Integer, nullable=True)  # None = workspace default

    # Relations
    workspace = relationship("Workspace", back_populates="api_keys")

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired


class AuditLog(Base, Timestamped):
    """
    Immutable audit trail for workspace actions.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)

    actor_id = Column(UUID(as_uuid=True), nullable=True)  # None for system actions
    actor_type = Column(String(50), nullable=False, default="user")  # user | api_key | system

    action = Column(String(100), nullable=False, index=True)  # campaign.created, user.invited, api_key.rotated
    resource_type = Column(String(100), nullable=False)  # campaign, workspace_member, api_key
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # Change details (immutable JSON)
    metadata = Column(JSON, nullable=False, default=dict)  # {ip: "...", user_agent: "...", changes: {...}}

    # Relations
    workspace = relationship("Workspace", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_workspace_created", "workspace_id", "created_at"),
        Index("ix_audit_logs_action", "action", "created_at"),
    )


class Campaign(Base, Timestamped):
    """
    Marketing campaign — already defined in models.py but extended here for workspace.
    """
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    execution_id = Column(String(100), nullable=True, index=True)
    pipeline_manifest = Column(String(255), nullable=True)
    enabled_channels = Column(JSON, nullable=False, default=list)
    total_budget_usd = Column(Float, nullable=False, default=5.0)
    spent_usd = Column(Float, nullable=False, default=0.0)
    brand_guidelines = Column(JSON, nullable=False, default=dict)
    result_artifacts = Column(JSON, nullable=False, default=dict)
    result_artifacts_ref = Column(String(500), nullable=True)

    # Relations
    workspace = relationship("Workspace", back_populates="campaigns")
    owner = relationship("User")
    artifacts = relationship("Artifact", back_populates="campaign", cascade="all, delete-orphan")
    decision_logs = relationship("DecisionLog", back_populates="campaign", cascade="all, delete-orphan")
    stage_attempts = relationship("StageAttempt", back_populates="campaign", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key and its hash.

    Returns (plaintext_key, hash) — plaintext_key is only available at creation time.
    """
    import hashlib
    import secrets

    raw = f"amk_{secrets.token_urlsafe(32)}"
    hash_ = hashlib.sha256(raw.encode()).hexdigest()
    prefix = raw[:12]  # "amk_live_xxxx"
    return raw, hash_, prefix


def seed_demo_workspace(session) -> Workspace:
    """Create a demo workspace with one editor user for testing."""
    from .models import User

    # Create demo user if not exists
    demo_user = session.query(User).filter(User.email == "demo@agentic.local").first()
    if not demo_user:
        demo_user = User(
            email="demo@agentic.local",
            full_name="Demo User",
            role="admin",
        )
        session.add(demo_user)
        session.flush()

    # Create workspace
    workspace = Workspace(
        name="Demo Workspace",
        slug="demo",
        plan="pro",
        max_campaigns=10,
        max_users=5,
        max_budget_usd=1000.0,
        enabled_channels=["organic", "paid"],
        settings={"default_platform": "twitter", "auto_review": True},
    )
    session.add(workspace)
    session.flush()

    # Add member
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=demo_user.id,
        role="owner",
    )
    session.add(member)
    session.commit()

    return workspace