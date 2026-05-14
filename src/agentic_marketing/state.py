"""EP_STATE — Marketing Director state management."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REVISION = "revision"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAILED = "failed"


class Channel(str, Enum):
    ORGANIC = "organic"
    PAID = "paid"
    EMAIL = "email"


# ---------------------------------------------------------------------------
# Nested Pydantic models for EP_STATE
# ---------------------------------------------------------------------------


class BrandVoice(BaseModel):
    tone: str = ""
    vocabulary_use: list[str] = Field(default_factory=list, alias="vocabulary_use")
    vocabulary_avoid: list[str] = Field(default_factory=list)
    formatting: list[str] = Field(default_factory=list)
    storytelling_style: str = ""


class VisualGuidelines(BaseModel):
    color_palette: list[str] = Field(default_factory=list)
    typography: str = ""
    logo_usage: str = ""
    image_style: str = ""


class AudienceSegment(BaseModel):
    segment_id: str = Field(default_factory=lambda: f"seg-{uuid.uuid4().hex[:8]}")
    name: str
    demographics: dict[str, Any] = Field(default_factory=dict)
    psychographics: dict[str, Any] = Field(default_factory=dict)
    behavioral: dict[str, Any] = Field(default_factory=dict)


class StrategicAngle(BaseModel):
    angle_id: str = Field(default_factory=lambda: f"angle-{uuid.uuid4().hex[:8]}")
    name: str
    description: str = ""
    data_points: list[dict[str, Any]] = Field(default_factory=list)


class Competitor(BaseModel):
    competitor_id: str = Field(default_factory=lambda: f"comp-{uuid.uuid4().hex[:8]}")
    name: str
    content_examples: list[dict[str, Any]] = Field(default_factory=list)


class CopyVariant(BaseModel):
    variant_id: str = Field(default_factory=lambda: f"var-{uuid.uuid4().hex[:8]}")
    content_id: str
    body: str
    cta: str = ""
    angle: str = ""
    engagement_score: float = 0.0
    platform: str = ""


class CreativeAsset(BaseModel):
    asset_id: str = Field(default_factory=lambda: f"asset-{uuid.uuid4().hex[:8]}")
    content_id: str
    asset_type: str = ""  # image, video, carousel
    url: str = ""
    color_palette: list[str] = Field(default_factory=list)
    format_specs: dict[str, Any] = Field(default_factory=dict)


class ChannelCredentials(BaseModel):
    platform: str
    credentials: dict[str, Any] = Field(default_factory=dict)
    status: str = "active"


class OrganicState(BaseModel):
    published: list[str] = Field(default_factory=list)
    scheduled: list[str] = Field(default_factory=list)
    platform_credentials: dict[str, ChannelCredentials] = Field(default_factory=dict)


class BudgetAllocation(BaseModel):
    channel: str
    allocated: float = 0.0
    spent: float = 0.0
    reserved: float = 0.0


class TargetingProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"tgt-{uuid.uuid4().hex[:8]}")
    segments: list[str] = Field(default_factory=list)
    demographics: dict[str, Any] = Field(default_factory=dict)
    interests: list[str] = Field(default_factory=list)
    lookalike_source: str = ""
    bid_strategy: str = ""


class AdCreative(BaseModel):
    ad_id: str = Field(default_factory=lambda: f"ad-{uuid.uuid4().hex[:8]}")
    targeting_profile_id: str = ""
    headline_variations: list[str] = Field(default_factory=list)
    body_variations: list[str] = Field(default_factory=list)
    formats: list[str] = Field(default_factory=list)


class EmailSequence(BaseModel):
    sequence_id: str = Field(default_factory=lambda: f"seq-{uuid.uuid4().hex[:8]}")
    emails: list[dict[str, Any]] = Field(default_factory=list)
    personalization_segments: list[str] = Field(default_factory=list)


class PaidState(BaseModel):
    campaigns: list[str] = Field(default_factory=list)
    targeting_profiles: dict[str, TargetingProfile] = Field(default_factory=dict)
    ad_creatives: dict[str, AdCreative] = Field(default_factory=dict)
    budget_allocated: dict[str, float] = Field(default_factory=dict)
    budget_spent: dict[str, float] = Field(default_factory=dict)


class EmailState(BaseModel):
    sequences: list[str] = Field(default_factory=list)
    subscribers: list[str] = Field(default_factory=list)
    personalization_rules: dict[str, Any] = Field(default_factory=dict)


class StageAttempt(BaseModel):
    stage_name: str
    attempt_number: int = 1
    status: StageStatus = StageStatus.PENDING
    started_at: str | None = None
    completed_at: str | None = None
    artifacts: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class SendBack(BaseModel):
    from_stage: str
    to_stage: str
    reason: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DecisionLogEntry(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec-{uuid.uuid4().hex[:8]}")
    stage: str
    category: str
    subject: str
    options_considered: list[dict[str, Any]] = Field(default_factory=list)
    selected: str = ""
    reason: str = ""
    confidence: float = 1.0
    user_visible: bool = True
    user_approved: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReviewRecord(BaseModel):
    review_id: str
    artifact_type: str
    stage: str
    decision: str  # APPROVE | REVISE | APPROVE_WITH_WARNINGS | PASS_WITH_WARNINGS
    chai_score: dict[str, float] | None = None
    feedback: list[dict[str, Any]] = Field(default_factory=list)
    round: int = 1


# ---------------------------------------------------------------------------
# EP_STATE — the main state container
# ---------------------------------------------------------------------------


class EPState(BaseModel):
    """
    Marketing Director state carried through the entire pipeline.

    Mirrors the marketing-director skill definition but as a Pydantic model
    for validation and serialization.
    """

    model_prefix: str = "ep_state"

    # Identity
    execution_id: str = Field(default_factory=lambda: f"exec-{uuid.uuid4().hex[:12]}")
    campaign_id: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Brand consistency
    brand_voice: BrandVoice = Field(default_factory=BrandVoice)
    visual_guidelines: VisualGuidelines = Field(default_factory=VisualGuidelines)

    # Research output (populated after research stage)
    audience_segments: list[AudienceSegment] = Field(default_factory=list)
    strategic_angles: list[StrategicAngle] = Field(default_factory=list)
    competitors: list[Competitor] = Field(default_factory=list)

    # Content produced (keyed by content_id)
    content_briefs: dict[str, dict[str, Any]] = Field(default_factory=dict)
    copy_variants: dict[str, list[CopyVariant]] = Field(default_factory=dict)
    creative_assets: dict[str, list[CreativeAsset]] = Field(default_factory=dict)

    # Channel state
    organic: OrganicState = Field(default_factory=OrganicState)
    paid: PaidState = Field(default_factory=PaidState)
    email: EmailState = Field(default_factory=EmailState)

    # Pipeline tracking
    revision_counts: dict[str, int] = Field(default_factory=dict)
    send_back_history: list[SendBack] = Field(default_factory=list)
    decision_log: list[DecisionLogEntry] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    stage_history: list[StageAttempt] = Field(default_factory=list)

    # Active execution
    current_stage: str = ""
    current_channel: Channel | None = None
    enabled_channels: list[Channel] = Field(default_factory=list)

    # Budget
    total_budget_usd: float = 5.0

    # Methods
    def start_stage(self, stage_name: str) -> None:
        self.current_stage = stage_name
        self.stage_history.append(
            StageAttempt(stage_name=stage_name, status=StageStatus.IN_PROGRESS, started_at=datetime.now(timezone.utc).isoformat())
        )

    def complete_stage(self, stage_name: str, status: StageStatus, artifacts: dict[str, Any] | None = None) -> None:
        for attempt in reversed(self.stage_history):
            if attempt.stage_name == stage_name and attempt.status == StageStatus.IN_PROGRESS:
                attempt.status = status
                attempt.completed_at = datetime.now(timezone.utc).isoformat()
                if artifacts:
                    attempt.artifacts.update(artifacts)
                break
        self.current_stage = ""

    def log_decision(self, entry: DecisionLogEntry) -> None:
        self.decision_log.append(entry)

    def emit_warning(self, message: str) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        self.warnings.append(f"[{ts}] {message}")

    def increment_revision(self, stage_name: str) -> int:
        count = self.revision_counts.get(stage_name, 0) + 1
        self.revision_counts[stage_name] = count
        return count

    def record_send_back(self, from_stage: str, to_stage: str, reason: str) -> None:
        self.send_back_history.append(SendBack(from_stage=from_stage, to_stage=to_stage, reason=reason))

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EPState:
        return cls.model_validate(data)