"""Database package."""

from agentic_marketing.db.connection import init_engine, get_engine, session_scope, get_session
from agentic_marketing.db.qdrant import init_qdrant, get_client, ensure_collection, upsert_points, search
from agentic_marketing.db.schema import (
    init_db, drop_db,
    Workspace, WorkspaceMember, User, APIKey, AuditLog,
    Campaign, PipelineExecution, ContentVariant, ContentAsset,
    PublishedPost, AnalyticsEvent, VectorCollection,
    PipelineStage, ContentStatus, Platform, WorkspacePlan,
)

__all__ = [
    "init_engine", "get_engine", "session_scope", "get_session",
    "init_qdrant", "get_client", "ensure_collection", "upsert_points", "search",
    "init_db", "drop_db",
    "Workspace", "WorkspaceMember", "User", "APIKey", "AuditLog",
    "Campaign", "PipelineExecution", "ContentVariant", "ContentAsset",
    "PublishedPost", "AnalyticsEvent", "VectorCollection",
    "PipelineStage", "ContentStatus", "Platform", "WorkspacePlan",
]