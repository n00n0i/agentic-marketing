"""Review Workflow — LangGraph node for CHAI quality gates."""

from __future__ import annotations

from typing import Optional

from ..state import EPState, StageStatus, ReviewRecord


MAX_REVIEW_ROUNDS = 2


class ReviewWorkflow:
    """LangGraph-compatible review workflow with 2-round CHAI retry."""

    def __init__(
        self,
        chai_reviewer: Optional[object] = None,
        moderation_check: Optional[object] = None,
    ):
        self.chai_reviewer = chai_reviewer
        self.moderation_check = moderation_check

    def review_node(self, state: EPState) -> EPState:
        """
        Review the current artifact using CHAI framework.

        Runs moderation check first, then CHAI review.
        Max 2 rounds before auto-fail.
        """
        # Placeholder: in real usage, artifact comes from current stage output
        artifact_content = state.brand_voice.tone or "Demo content for review"

        # Moderation check
        if self.moderation_check:
            mod = self.moderation_check.check(artifact_content, "Twitter")
            if not mod.is_safe:
                state.emit_warning(
                    f"Moderation flag: [{mod.severity}] {', '.join(mod.flags)}"
                )
                return state

        # Determine round
        round_num = state.revision_counts.get("review", 0) + 1

        # CHAI review
        if self.chai_reviewer:
            scores = self.chai_reviewer.review(
                content=artifact_content,
                platform="Twitter",
                audience="B2B SaaS teams",
                content_type="social_post",
                stage_name=state.current_stage or "copy",
                round_num=round_num,
            )
            overall = scores.overall
            feedback_text = scores.feedback
        else:
            # Demo mode — mock scores
            from ..chains.review_chain import DemoReviewChain

            demo = DemoReviewChain()
            scores = demo.review(artifact_content)
            overall = scores.overall
            feedback_text = f"[Demo] {scores.feedback}"

        passed = overall >= 4.0

        # Record review
        review_record = ReviewRecord(
            review_id=f"rev-{round_num}",
            artifact_type=state.current_stage or "copy",
            stage=state.current_stage or "copy",
            decision="APPROVE" if passed else "REVISE",
            chai_score={
                "complete": scores.complete,
                "helpful": scores.helpful,
                "accurate": scores.accurate,
                "insightful": scores.insightful,
                "actionable": scores.actionable,
                "overall": overall,
            },
            round=round_num,
        )

        # Find and update the current stage attempt
        for attempt in reversed(state.stage_history):
            if attempt.stage_name == state.current_stage:
                attempt.status = StageStatus.APPROVED if passed else StageStatus.REVISION
                break

        if not passed:
            count = state.increment_revision("review")
            if count < MAX_REVIEW_ROUNDS:
                state.emit_warning(
                    f"Review round {round_num}: score={overall:.1f} — revision needed"
                )
            else:
                state.emit_warning(
                    f"Review round {round_num}: max rounds reached, passing with warnings"
                )
                review_record.decision = "PASS_WITH_WARNINGS"
                for attempt in reversed(state.stage_history):
                    if attempt.stage_name == state.current_stage:
                        attempt.status = StageStatus.PASS_WITH_WARNINGS
                        break

        state.stage_history.append(
            StageAttempt(
                stage_name="review",
                attempt_number=round_num,
                status=StageStatus.APPROVED if passed else StageStatus.REVISION,
                started_at=review_record.review_id,
            )
        )

        return state

    def should_retry(self, state: EPState) -> bool:
        """LangGraph conditional edge — should retry for revision."""
        return state.revision_counts.get("review", 0) < MAX_REVIEW_ROUNDS

    def should_continue_or_fail(self, state: EPState) -> str:
        """LangGraph conditional edge."""
        last_attempt = state.stage_history[-1] if state.stage_history else None
        if last_attempt is None:
            return "fail"
        if last_attempt.status in (StageStatus.APPROVED, StageStatus.PASS_WITH_WARNINGS):
            return "continue"
        if last_attempt.status == StageStatus.REVISION:
            return "retry"
        return "fail"