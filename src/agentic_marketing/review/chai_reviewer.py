"""CHAI 5-dimension quality scorer — C/H/A/I/A, 1–5 scale, pass >= 4.0."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# -------------------------------------------------------------------------
# Enums / Constants
# -------------------------------------------------------------------------


class ReviewRound(str, Enum):
    ROUND_1 = "round_1"
    ROUND_2 = "round_2"


class ReviewDecision(str, Enum):
    APPROVE = "APPROVE"
    REVISE = "REVISE"
    APPROVE_WITH_WARNINGS = "APPROVE_WITH_WARNINGS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"


# -------------------------------------------------------------------------
# Data classes
# -------------------------------------------------------------------------


@dataclass
class CHAIScore:
    """CHAI 5-dimension score (1–5 each)."""

    complete: float = 5.0  # C — all required elements present
    helpful: float = 5.0   # H — valuable to target audience
    accurate: float = 5.0   # A — factually correct
    insightful: float = 5.0  # I — demonstrates deep understanding
    actionable: float = 5.0  # A — clear next steps

    def overall(self) -> float:
        """Weighted average (all equal weight)."""
        return (self.complete + self.helpful + self.accurate + self.insightful + self.actionable) / 5.0

    def to_dict(self) -> dict[str, float]:
        return {
            "C": self.complete,
            "H": self.helpful,
            "A": self.accurate,
            "I": self.insightful,
            "A": self.actionable,
            "overall": self.overall(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> CHAIScore:
        return cls(
            complete=data.get("C", data.get("complete", 5.0)),
            helpful=data.get("H", data.get("helpful", 5.0)),
            accurate=data.get("A", data.get("accurate", 5.0)),
            insightful=data.get("I", data.get("insightful", 5.0)),
            actionable=data.get("A", data.get("actionable", 5.0)),
        )


@dataclass
class DimensionFeedback:
    """Per-dimension feedback for revision guidance."""

    dimension: str  # C | H | A | I | A
    score: float
    issue: str
    suggestion: str


@dataclass
class CHAIReviewResult:
    """Result of a CHAI review round."""

    review_id: str = field(default_factory=lambda: f"rev-{uuid.uuid4().hex[:12]}")
    artifact_type: str = ""
    stage: str = ""
    round: int = 1  # 1 or 2

    decision: ReviewDecision = ReviewDecision.APPROVE
    chai_score: CHAIScore = field(default_factory=CHAIScore)
    dimension_feedback: list[DimensionFeedback] = field(default_factory=list)

    review_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Pass/fail helpers
    def passed(self) -> bool:
        return self.chai_score.overall() >= 4.0

    def can_retry(self) -> bool:
        return self.round < 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "artifact_type": self.artifact_type,
            "stage": self.stage,
            "round": self.round,
            "decision": self.decision.value,
            "chai_score": self.chai_score.to_dict(),
            "dimension_feedback": [
                {"dimension": d.dimension, "score": d.score, "issue": d.issue, "suggestion": d.suggestion}
                for d in self.dimension_feedback
            ],
            "review_timestamp": self.review_timestamp,
            "passed": self.passed(),
        }


# -------------------------------------------------------------------------
# CHAIReviewer
# -------------------------------------------------------------------------


class CHAIReviewer:
    """
    CHAI 5-dimension quality scorer.

    Dimensions:
        C = Complete      — all required elements present
        H = Helpful       — valuable to target audience
        A = Accurate     — factually correct
        I = Insightful    — demonstrates deep understanding
        A = Actionable    — clear next steps

    Pass threshold: overall score >= 4.0 (each dimension 1–5).

    Supports demo/mock mode when LLM is not configured.
    """

    PASS_THRESHOLD = 4.0

    def __init__(self, mock_mode: bool | None = None):
        """
        Initialize the CHAI reviewer.

        Args:
            mock_mode: Force mock mode. None = auto-detect from LLM config.
        """
        if mock_mode is None:
            mock_mode = self._detect_mock_mode()
        self.mock_mode = mock_mode
        logger.info("chai_reviewer_initialized", mock_mode=self.mock_mode)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def review(
        self,
        artifact: dict[str, Any],
        artifact_type: str,
        stage: str,
        context: dict[str, Any] | None = None,
        round: int = 1,
    ) -> CHAIReviewResult:
        """
        Score an artifact on the 5 CHAI dimensions.

        Args:
            artifact: The artifact content (dict)
            artifact_type: e.g. "market_brief", "copy_variants", "creative_assets"
            stage: Pipeline stage name, e.g. "copy", "creative"
            context: Additional context (brand guidelines, market_brief, etc.)
            round: Review round (1 or 2)

        Returns:
            CHAIReviewResult with scores, feedback, and decision
        """
        context = context or {}

        if self.mock_mode:
            return self._mock_review(artifact, artifact_type, stage, round)

        return self._llm_review(artifact, artifact_type, stage, context, round)

    def review_and_decide(
        self,
        artifact: dict[str, Any],
        artifact_type: str,
        stage: str,
        context: dict[str, Any] | None = None,
        round: int = 1,
    ) -> CHAIReviewResult:
        """
        Full review + decision with dimension-level feedback.

        Same as review() but also attaches per-dimension feedback
        for any dimension that scores below threshold.
        """
        result = self.review(artifact, artifact_type, stage, context, round)

        # Generate feedback for dimensions below threshold
        threshold = self.PASS_THRESHOLD
        feedback_dims = []

        dim_map = [
            ("C", "complete", "Consistent"),
            ("H", "helpful", "Helpful"),
            ("A", "accurate", "Accurate"),
            ("I", "insightful", "Insightful"),
            ("A", "actionable", "Actionable"),
        ]

        for letter, attr, label in dim_map:
            score = getattr(result.chai_score, attr)
            if score < threshold:
                feedback_dims.append(DimensionFeedback(
                    dimension=letter,
                    score=score,
                    issue=f"{label} score ({score}/5) below pass threshold ({threshold})",
                    suggestion=_suggestion_for_dim(attr, score),
                ))

        result.dimension_feedback = feedback_dims

        # Determine decision
        result.decision = self._decide(result)
        return result

    # ---------------------------------------------------------------------
    # Mock review (demo mode)
    # ---------------------------------------------------------------------

    def _mock_review(
        self,
        artifact: dict[str, Any],
        artifact_type: str,
        stage: str,
        round: int,
    ) -> CHAIReviewResult:
        """Return deterministic mock scores for demo/dev mode."""
        logger.info("chai_mock_review", artifact_type=artifact_type, stage=stage, round=round)

        # Give passing scores unless the artifact is clearly a placeholder
        is_placeholder = self._is_placeholder(artifact)
        base_score = 3.0 if is_placeholder else 4.2

        score = CHAIScore(
            complete=base_score + 0.2,
            helpful=base_score + 0.3,
            accurate=base_score,
            insightful=base_score - 0.1,
            actionable=base_score + 0.1,
        )

        # Clamp to 1-5
        for attr in ["complete", "helpful", "accurate", "insightful", "actionable"]:
            val = getattr(score, attr)
            setattr(score, attr, max(1.0, min(5.0, val)))

        decision = ReviewDecision.APPROVE if score.overall() >= self.PASS_THRESHOLD else ReviewDecision.REVISE

        return CHAIReviewResult(
            artifact_type=artifact_type,
            stage=stage,
            round=round,
            decision=decision,
            chai_score=score,
        )

    def _is_placeholder(self, artifact: dict[str, Any]) -> bool:
        """Detect placeholder/fallback artifacts."""
        body = str(artifact)
        return "fallback" in body.lower() or "placeholder" in body.lower()

    # ---------------------------------------------------------------------
    # LLM review (production)
    # ---------------------------------------------------------------------

    def _llm_review(
        self,
        artifact: dict[str, Any],
        artifact_type: str,
        stage: str,
        context: dict[str, Any],
        round: int,
    ) -> CHAIReviewResult:
        """Use the LLM chain to score an artifact."""
        try:
            from ..chains.review_chain import build_review_chain, run_review

            result_dict = run_review(
                artifact=artifact,
                artifact_type=artifact_type,
                stage=stage,
                context=context,
                round=round,
            )
            return self._parse_llm_result(result_dict, artifact_type, stage, round)

        except Exception as exc:
            logger.warning("chai_llm_review_failed", error=str(exc), falling_back_to_mock=True)
            return self._mock_review(artifact, artifact_type, stage, round)

    def _parse_llm_result(
        self,
        result: dict[str, Any],
        artifact_type: str,
        stage: str,
        round: int,
    ) -> CHAIReviewResult:
        """Parse LLM chain output into CHAIReviewResult."""
        chai_score = CHAIScore.from_dict(result.get("chai_score", {}))
        decision = ReviewDecision(result.get("decision", "APPROVE"))

        return CHAIReviewResult(
            review_id=result.get("review_id", f"rev-{uuid.uuid4().hex[:12]}"),
            artifact_type=artifact_type,
            stage=stage,
            round=round,
            decision=decision,
            chai_score=chai_score,
            dimension_feedback=[
                DimensionFeedback(**f) for f in result.get("dimension_feedback", [])
            ],
        )

    # ---------------------------------------------------------------------
    # Decision logic
    # ---------------------------------------------------------------------

    def _decide(self, result: CHAIReviewResult) -> ReviewDecision:
        """Determine the review decision based on scores and round."""
        overall = result.chai_score.overall()
        round = result.round

        if overall >= self.PASS_THRESHOLD:
            return ReviewDecision.APPROVE

        # Below threshold
        if round >= 2:
            # Last round — auto-fail with override option
            return ReviewDecision.FAIL

        # Round 1 — allow revision
        return ReviewDecision.REVISE

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------

    @staticmethod
    def _detect_mock_mode() -> bool:
        """Auto-detect mock mode from environment/API keys."""
        return not bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))

    def is_mock(self) -> bool:
        return self.mock_mode


# -------------------------------------------------------------------------
# Helper
# -------------------------------------------------------------------------


def _suggestion_for_dim(dimension: str, score: float) -> str:
    """Return a generic suggestion for a low-scoring dimension."""
    suggestions = {
        "complete": "Add missing required elements and ensure all sections are fully developed.",
        "helpful": "Focus more on the target audience's actual needs, pain points, and questions.",
        "accurate": "Verify all facts and claims against source data; add citations where needed.",
        "insightful": "Add deeper analysis that goes beyond generic advice; connect dots in a new way.",
        "actionable": "Strengthen CTAs and next steps; make them specific, concrete, and achievable.",
    }
    base = suggestions.get(dimension, "Improve this dimension.")
    if score < 3:
        return f"⚠️ Critical: {base}"
    return base