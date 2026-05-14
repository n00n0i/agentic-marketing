"""Pipeline loader — parses YAML manifest into executable Python structures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog
import yaml
from pydantic import BaseModel, Field, field_validator

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Pydantic models for YAML manifest
# ---------------------------------------------------------------------------


class ChannelConfig(BaseModel):
    platforms: list[str] = Field(default_factory=list)
    media_spend: float | str = 0
    tools: list[str] = Field(default_factory=list)


class StageSubStage(BaseModel):
    name: str
    condition: str = ""
    tools_available: list[str] = Field(default_factory=list)


class BudgetPolicy(BaseModel):
    enforcement: str = "warn"
    reserve_holdback_pct: float = 0.10
    single_action_approval_threshold_usd: float = 0.50
    new_paid_tool_approval_required: bool = True
    allocation: dict[str, float] = Field(default_factory=lambda: {"organic": 0.15, "paid": 0.80, "email": 0.05})


class StageConfig(BaseModel):
    name: str
    skill: str
    produces: list[str] = Field(default_factory=list)
    checkpoint_required: bool = False
    human_approval_default: bool = False
    tools_available: list[str] = Field(default_factory=list)
    review_focus: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    stage_enabled: str = ""
    sub_stages: list[StageSubStage] = Field(default_factory=list)

    @field_validator("produces", mode="before")
    @classmethod
    def _ensure_list(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [v]
        return v


class PipelineManifest(BaseModel):
    """Validated view of the agentic-marketing.yaml pipeline manifest."""

    name: str
    version: str = "1.0"
    category: str = ""
    stability: str = ""
    description: str = ""
    default_checkpoint_policy: str = "guided"
    orchestration: dict[str, Any] = Field(default_factory=dict)
    extensions: dict[str, bool] = Field(default_factory=dict)
    required_skills: list[str] = Field(default_factory=list)
    channels: dict[str, ChannelConfig] = Field(default_factory=dict)
    stages: list[StageConfig] = Field(default_factory=list)
    budget_policies: BudgetPolicy = Field(default_factory=BudgetPolicy)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_pipeline_manifest(yaml_path: Path | str) -> PipelineManifest:
    """
    Load and validate a pipeline YAML manifest.

    Raises:
        FileNotFoundError: if the YAML file doesn't exist
        ValueError: if validation fails
    """
    path = Path(yaml_path)
    if not path.exists():
        raise FileNotFoundError(f"Pipeline manifest not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not raw:
        raise ValueError(f"Empty pipeline manifest: {path}")

    manifest = PipelineManifest.model_validate(raw)
    logger.info("pipeline_manifest_loaded", name=manifest.name, version=manifest.version, stages=len(manifest.stages))
    return manifest


def get_stage_by_name(manifest: PipelineManifest, stage_name: str) -> StageConfig | None:
    for stage in manifest.stages:
        if stage.name == stage_name:
            return stage
    return None


def stage_order(manifest: PipelineManifest) -> list[str]:
    """Return ordered list of stage names."""
    return [s.name for s in manifest.stages]


def enabled_stages(manifest: PipelineManifest, context: dict[str, Any] | None = None) -> list[StageConfig]:
    """
    Return stages that are enabled given the current context.

    A stage is filtered out if it has a `stage_enabled` condition that
    evaluates to False in the context dict.
    """
    ctx = context or {}
    result = []
    for stage in manifest.stages:
        if not stage.stage_enabled:
            result.append(stage)
            continue
        # Simple condition evaluation: "channel_organic_enabled" -> ctx.get("channel_organic_enabled")
        cond = stage.stage_enabled
        if ctx.get(cond, True):
            result.append(stage)
    return result


def build_execution_plan(manifest: PipelineManifest, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """
    Build a sequential execution plan from the manifest.

    Returns a list of {"stage": StageConfig, "sub_stages": [StageSubStage, ...]} dicts.
    Sub-stages are expanded inline.
    """
    plan = []
    for stage in enabled_stages(manifest, context):
        entry: dict[str, Any] = {"stage": stage, "sub_stages": []}
        if stage.sub_stages:
            for sub in stage.sub_stages:
                # Evaluate sub-stage condition
                if sub.condition and not context.get(sub.condition, False):
                    continue
                entry["sub_stages"].append(sub)
        plan.append(entry)
    return plan


# ---------------------------------------------------------------------------
# Schema export (for canonical artifact validation)
# ---------------------------------------------------------------------------


MANIFEST_JSON_SCHEMA_PATH = Path(__file__).parent.parent.parent / "schemas" / "pipelines" / "agentic-marketing.schema.json"


def export_manifest_json_schema(output_path: Path | None = None) -> dict[str, Any]:
    """Export PipelineManifest as JSON Schema for artifact validation."""
    import inspect

    schema = PipelineManifest.model_json_schema()
    output = output_path or MANIFEST_JSON_SCHEMA_PATH
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    logger.info("manifest_json_schema_exported", path=str(output))
    return schema