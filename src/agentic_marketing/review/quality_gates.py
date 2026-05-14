"""Quality gates — per-artifact-type gate definitions and evaluation."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import structlog

from .chai_reviewer import CHAIReviewer, CHAIReviewResult, CHAIScore, ReviewDecision
from .moderation import ContentModerationResult, moderate_content

logger = structlog.get_logger(__name__)


# -------------------------------------------------------------------------
# Enums
# -------------------------------------------------------------------------


class ArtifactType(str, Enum):
    MARKET_BRIEF = "market_brief"
    CONTENT_BRIEF = "content_brief"
    COPY_VARIANTS = "copy_variants"
    CREATIVE_ASSETS = "creative_assets"
    EMAIL_SEQUENCE = "email_sequence"
    AD_CREATIVE = "ad_creative"
    TARGETING_PROFILE = "targeting_profile"
    SOCIAL_POST = "social_post"


class GateDecision(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVISE = "REVISE"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    AUTO_APPROVED = "AUTO_APPROVED"  # demo/mock artifacts


# -------------------------------------------------------------------------
# Gate definition
# -------------------------------------------------------------------------


@dataclass
class GateCondition:
    """A single condition within a gate."""

    dimension: str  # C | H | A | I | A
    min_score: float = 4.0
    required: bool = True


@dataclass
class QualityGate:
    """
    A quality gate for a specific artifact type.

    Defines which CHAI dimensions must meet minimum thresholds,
    and which additional checks (moderation, schema) are required.
    """

    artifact_type: ArtifactType
    conditions: list[GateCondition] = field(default_factory=list)
    requires_moderation: bool = True
    min_overall_score: float = 4.0

    # Gate-specific criteria (beyond CHAI)
    extra_checks: list[str] = field(default_factory=list)  # e.g. ["schema_valid", "no_broken_links"]

    def evaluate(self, chai_score: CHAIScore) -> tuple[bool, list[str]]:
        """
        Evaluate a CHAI score against this gate's conditions.

        Returns (passed, list_of_failures)
        """
        failures = []

        for cond in self.conditions:
            score = self._get_score(chai_score, cond.dimension)
            if score < cond.min_score:
                if cond.required:
                    failures.append(
                        f"{cond.dimension}={score:.1f} < {cond.min_score} (required)"
                    )
                else:
                    logger.debug("gate_optional_fail", dimension=cond.dimension, score=score)

        # Overall check
        if chai_score.overall() < self.min_overall_score:
            failures.append(
                f"overall={chai_score.overall():.1f} < {self.min_overall_score}"
            )

        return len(failures) == 0, failures

    @staticmethod
    def _get_score(chai_score: CHAIScore, dimension: str) -> float:
        dim_map = {
            "C": chai_score.complete,
            "H": chai_score.helpful,
            "A": chai_score.accurate,
            "I": chai_score.insightful,
            "A": chai_score.actionable,
        }
        return dim_map.get(dimension, 5.0)


# -------------------------------------------------------------------------
# Default gates per artifact type
# -------------------------------------------------------------------------


# Default gate registry — one gate per artifact type
DEFAULT_GATES: dict[str, QualityGate] = {}


def _build_default_gates() -> dict[str, QualityGate]:
    """Build the default gate registry (lazy, called once)."""

    def gate(
        artifact_type: ArtifactType,
        conditions: list[GateCondition],
        requires_moderation: bool = True,
        extra_checks: list[str] | None = None,
    ) -> QualityGate:
        g = QualityGate(
            artifact_type=artifact_type,
            conditions=conditions,
            requires_moderation=requires_moderation,
            extra_checks=extra_checks or [],
        )
        DEFAULT_GATES[artifact_type.value] = g
        return g

    # market_brief: all dimensions matter, no moderation needed
    _gate(
        ArtifactType.MARKET_BRIEF,
        conditions=[
            GateCondition("C", min_score=3.5),
            GateCondition("H", min_score=3.5),
            GateCondition("A", min_score=4.0),  # accuracy critical for research
            GateCondition("I", min_score=3.5),
            GateCondition("A", min_score=3.5),
        ],
        requires_moderation=False,
    )

    # content_brief: actionable and helpful are key
    _gate(
        ArtifactType.CONTENT_BRIEF,
        conditions=[
            GateCondition("C", min_score=4.0),
            GateCondition("H", min_score=4.0),
            GateCondition("A", min_score=3.5),
            GateCondition("I", min_score=3.5),
            GateCondition("A", min_score=4.0),  # actionable is key for briefs
        ],
        requires_moderation=False,
    )

    # copy_variants: complete, helpful, actionable critical
    _gate(
        ArtifactType.COPY_VARIANTS,
        conditions=[
            GateCondition("C", min_score=4.0),
            GateCondition("H", min_score=4.0),
            GateCondition("A", min_score=3.5),
            GateCondition("I", min_score=3.5),
            GateCondition("A", min_score=4.0),  # CTA must be actionable
        ],
        requires_moderation=True,
        extra_checks=["variant_distinctness", "platform_compliance"],
    )

    # creative_assets: visual consistency (C) and brand compliance
    _gate(
        ArtifactType.CREATIVE_ASSETS,
        conditions=[
            GateCondition("C", min_score=4.0),  # visual must be consistent
            GateCondition("H", min_score=3.5),
            GateCondition("A", min_score=3.5),
            GateCondition("I", min_score=3.5),
            GateCondition("A", min_score=3.5),
        ],
        requires_moderation=True,
    )

    # email_sequence: actionable is critical
    _gate(
        ArtifactType.EMAIL_SEQUENCE,
        conditions=[
            GateCondition("C", min_score=4.0),
            GateCondition("H", min_score=4.0),
            GateCondition("A", min_score=4.0),
            GateCondition("I", min_score=3.5),
            GateCondition("A", min_score=4.0),
        ],
        requires_moderation=True,
    )

    # social_post: short-form copy
    _gate(
        ArtifactType.SOCIAL_POST,
        conditions=[
            GateCondition("C", min_score=3.5),
            GateCondition("H", min_score=4.0),
            GateCondition("A", min_score=3.5),
            GateCondition("I", min_score=3.5),
            GateCondition("A", min_score=4.0),
        ],
        requires_moderation=True,
        extra_checks=["platform_compliance"],
    )

    return DEFAULT_GATES


# Initialise on module load
_build_default_gates()


# -------------------------------------------------------------------------
# GateResult
# -------------------------------------------------------------------------


@dataclass
class GateResult:
    """
    Result of evaluating a quality gate.

    Attributes:
        artifact_type: Type of artifact reviewed
        artifact_ref: Reference ID of the artifact
        gate_decision: PASS | FAIL | REVISE | PASS_WITH_WARNINGS | AUTO_APPROVED
        chai_score: The CHAI scores
        moderation_result: Content moderation result (if applicable)
        failures: List of failure messages
        warnings: List of non-critical warnings
        suggestions: Actionable suggestions for improvement
        mock_mode: Whether mock/demo mode was used
        review_round: Which round this is (1 or 2)
        review_result: The underlying CHAIReviewResult
    """

    artifact_type: str = ""
    artifact_ref: str = ""
    gate_decision: GateDecision = GateDecision.PASS

    chai_score: CHAIScore | None = None
    moderation_result: ContentModerationResult | None = None

    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    mock_mode: bool = False
    review_round: int = 1

    review_result: CHAIReviewResult | None = None

    @property
    def passed(self) -> bool:
        return self.gate_decision in (
            GateDecision.PASS,
            GateDecision.AUTO_APPROVED,
            GateDecision.PASS_WITH_WARNINGS,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_type": self.artifact_type,
            "artifact_ref": self.artifact_ref,
            "gate_decision": self.gate_decision.value,
            "chai_score": self.chai_score.to_dict() if self.chai_score else None,
            "moderation_result": (
                self.moderation_result.to_dict() if self.moderation_result else None
            ),
            "failures": self.failures,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "mock_mode": self.mock_mode,
            "review_round": self.review_round,
            "passed": self.passed,
        }


# -------------------------------------------------------------------------
# QualityGateRunner
# -------------------------------------------------------------------------


class QualityGateRunner:
    """
    Runs quality gates against artifacts.

    Integrates CHAI scoring + moderation + gate conditions.
    Supports demo/mock mode (auto-detected or forced).
    """

    def __init__(self, mock_mode: bool | None = None, force_moderation: bool = False):
        """
        Initialize the gate runner.

        Args:
            mock_mode: Force mock mode. None = auto-detect from env.
            force_moderation: If True, run moderation even in mock mode.
        """
        self.mock_mode = mock_mode if mock_mode is not None else self._detect_mock_mode()
        self.force_moderation = force_moderation
        self.chai = CHAIReviewer(mock_mode=self.mock_mode)
        logger.info("quality_gate_runner_initialized", mock_mode=self.mock_mode)

    def evaluate(
        self,
        artifact: dict[str, Any],
        artifact_type: str,
        stage: str,
        artifact_ref: str = "",
        context: dict[str, Any] | None = None,
        round: int = 1,
    ) -> GateResult:
        """
        Evaluate an artifact against its quality gate.

        Args:
            artifact: The artifact content dict
            artifact_type: Artifact type string (e.g. "copy_variants")
            stage: Pipeline stage name
            artifact_ref: Optional reference ID
            context: Additional context (brand guidelines, market_brief, etc.)
            round: Review round (1 or 2)

        Returns:
            GateResult with decision, scores, and suggestions
        """
        context = context or {}

        # Auto-approve demo artifacts
        if self._is_demo_artifact(artifact):
            logger.info("gate_auto_approving_demo", artifact_type=artifact_type)
            return self._auto_approve(artifact, artifact_type, artifact_ref, round)

        # Step 1: CHAI review
        chai_result = self.chai.review(artifact, artifact_type, stage, context, round)

        # Step 2: Moderation (if required)
        mod_result = None
        gate = self._get_gate(artifact_type)

        if (gate and gate.requires_moderation) or self.force_moderation:
            text_content = self._extract_text(artifact)
            mod_result = moderate_content(text_content, artifact_type=artifact_type)

        # Step 3: Evaluate gate conditions
        failures: list[str] = []
        warnings: list[str] = []
        suggestions: list[str] = []

        if chai_result.passed():
            gate_decision = GateDecision.PASS
        else:
            gate_decision = GateDecision.REVISE

        # Check gate conditions
        if gate and chai_result.chai_score:
            gate_passed, gate_failures = gate.evaluate(chai_result.chai_score)
            failures.extend(gate_failures)
            if not gate_passed:
                gate_decision = GateDecision.REVISE

        # Check moderation
        if mod_result and not mod_result.is_safe:
            warnings.append(f"Moderation flagged: {mod_result.flags}")
            if mod_result.severity == "high":
                gate_decision = GateDecision.FAIL

        # Build suggestions from dimension feedback
        for fb in chai_result.dimension_feedback:
            suggestions.append(f"[{fb.dimension}] {fb.suggestion}")

        # Attach warnings from moderation
        if mod_result and mod_result.warnings:
            warnings.extend(mod_result.warnings)

        result = GateResult(
            artifact_type=artifact_type,
            artifact_ref=artifact_ref,
            gate_decision=gate_decision,
            chai_score=chai_result.chai_score,
            moderation_result=mod_result,
            failures=failures,
            warnings=warnings,
            suggestions=suggestions,
            mock_mode=self.mock_mode,
            review_round=round,
            review_result=chai_result,
        )

        # If CHAI passed and moderation is clean, upgrade to PASS
        if chai_result.passed() and (not mod_result or mod_result.is_safe):
            if not failures:
                result.gate_decision = GateDecision.PASS
            else:
                result.gate_decision = GateDecision.PASS_WITH_WARNINGS

        logger.info(
            "gate_evaluation_complete",
            artifact_type=artifact_type,
            decision=result.gate_decision.value,
            round=round,
            passed=result.passed,
        )

        return result

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------

    @staticmethod
    def _detect_mock_mode() -> bool:
        return not bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))

    def _get_gate(self, artifact_type: str) -> QualityGate | None:
        return DEFAULT_GATES.get(artifact_type)

    def _is_demo_artifact(self, artifact: dict[str, Any]) -> bool:
        """Detect if an artifact is a demo/mock artifact (auto-approve)."""
        # Check for mock markers
        content_str = str(artifact)
        demo_markers = [
            "mock",
            "demo",
            "placeholder",
            "fallback",
            "example",
            "test artifact",
        ]
        return any(m in content_str.lower() for m in demo_markers)

    def _auto_approve(
        self,
        artifact: dict[str, Any],
        artifact_type: str,
        artifact_ref: str,
        round: int,
    ) -> GateResult:
        """Auto-approve demo/mock artifacts."""
        return GateResult(
            artifact_type=artifact_type,
            artifact_ref=artifact_ref,
            gate_decision=GateDecision.AUTO_APPROVED,
            chai_score=CHAIScore(
                complete=4.5,
                helpful=4.5,
                accurate=4.0,
                insightful=4.0,
                actionable=4.5,
            ),
            failures=[],
            warnings=["Auto-approved: demo artifact detected"],
            suggestions=[],
            mock_mode=True,
            review_round=round,
        )

    @staticmethod
    def _extract_text(artifact: dict[str, Any]) -> str:
        """Extract all text content from an artifact for moderation."""
        parts = []

        def _flatten(obj: Any) -> None:
            if isinstance(obj, str):
                parts.append(obj)
            elif isinstance(obj, dict):
                for v in obj.values():
                    _flatten(v)
            elif isinstance(obj, list):
                for item in obj:
                    _flatten(item)

        _flatten(artifact)
        return " ".join(parts)

    def is_mock(self) -> bool:
        return self.mock_mode


# -------------------------------------------------------------------------
# Convenience helpers
# -------------------------------------------------------------------------


def run_quality_gate(
    artifact: dict[str, Any],
    artifact_type: str,
    stage: str,
    artifact_ref: str = "",
    context: dict[str, Any] | None = None,
    round: int = 1,
    mock_mode: bool | None = None,
) -> GateResult:
    """
    Convenience function to run a quality gate evaluation.

    Args:
        artifact: The artifact content dict
        artifact_type: e.g. "copy_variants", "market_brief"
        stage: Pipeline stage name
        artifact_ref: Optional artifact ID
        context: Additional context (brand guidelines, market_brief, etc.)
        round: Review round (1 or 2)
        mock_mode: Force mock mode

    Returns:
        GateResult with pass/fail and suggestions
    """
    runner = QualityGateRunner(mock_mode=mock_mode)
    return runner.evaluate(
        artifact=artifact,
        artifact_type=artifact_type,
        stage=stage,
        artifact_ref=artifact_ref,
        context=context,
        round=round,
    )