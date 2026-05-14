"""LangGraph publish node — publishes to social platforms with partial failure handling."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import structlog

from ..state import EPState, StageStatus
from ..social.publish_manager import PublishManager
from ..social.analytics import AnalyticsCollector
from .publish_chain import run_publish

logger = structlog.get_logger(__name__)


# -------------------------------------------------------------------------
# Node function
# -------------------------------------------------------------------------


def publish_node(state: EPState) -> dict[str, Any]:
    """
    LangGraph node for the publish stage.

    Validates content, publishes to all configured platforms in parallel,
    handles partial failures, and updates state.

    Args:
        state: EPState containing:
            - campaign_id
            - copy_variants: dict[content_id, list[CopyVariant]]
            - creative_assets: dict[content_id, list[CreativeAsset]]
            - organic.platform_credentials

    Returns:
        dict with updated state fields:
            - organic.published (list of publication IDs added)
            - stage_history updated
            - publish_results artifact
    """
    exec_id = state.execution_id
    campaign_id = state.campaign_id
    logger.info("publish_node_started", execution_id=exec_id, campaign_id=campaign_id)

    # Mark stage as in-progress
    state.start_stage("publish")
    state.current_stage = "publish"

    # Determine target platforms from enabled_channels
    enabled = state.enabled_channels or []
    platform_map = {
        "organic": ["twitter", "linkedin", "facebook"],
        "paid": [],
        "email": [],
    }
    target_platforms = platform_map.get(enabled[0] if enabled else "organic", ["twitter", "linkedin"])

    publish_results = None
    errors: list[str] = []

    try:
        # Run the publish chain (LLM-based selection + formatting)
        chain_result = run_publish(state, platforms=target_platforms, execution_id=exec_id)
        publish_results = chain_result.get("publish_results", {})

        # Validate content before publishing (placeholder for moderation)
        validation_errors = _validate_content(state, publish_results)
        if validation_errors:
            logger.warning("content_validation_warnings", errors=validation_errors)

        # Publish via the manager for each successful platform
        manager = PublishManager()
        published_ids: list[str] = []

        publications = publish_results.get("publications", [])
        for pub in publications:
            platform = pub.get("platform", "")
            variant_id = pub.get("variant_id", "")
            status = pub.get("status", "")

            if status == "failed":
                errors.append(f"{platform}: {pub.get('errors', ['unknown error'])}")
                continue

            # Get the actual content from copy_variants
            content = _resolve_variant_body(state, variant_id)

            # Build media dict from creative assets
            media = _resolve_media_for_platform(state, platform, variant_id)

            try:
                result = manager.publish(
                    content=content,
                    platforms=[platform],
                    media={platform: media} if media else {},
                )
                if result.successful > 0:
                    pr = result.platform_results[0]
                    published_ids.append(pr.post_id)
                    logger.info(
                        "platform_published",
                        platform=platform,
                        post_id=pr.post_id,
                        post_url=pr.post_url,
                        mock=pr.mock,
                    )
            except Exception as pub_err:
                logger.error("publish_manager_error", platform=platform, error=str(pub_err))
                errors.append(f"{platform}: {pub_err}")

        # Update state
        state.organic.published.extend(published_ids)

        # Mark stage complete
        failed_count = len(errors)
        total_count = len(publications) if publications else len(target_platforms)
        stage_status = StageStatus.APPROVED if failed_count == 0 else StageStatus.PASS_WITH_WARNINGS

        state.complete_stage("publish", stage_status, artifacts={
            "publish_results": publish_results,
            "publication_ids": published_ids,
            "errors": errors,
        })

        logger.info(
            "publish_node_completed",
            execution_id=exec_id,
            published=len(published_ids),
            failed=failed_count,
            total=total_count,
        )

        return {
            "organic": state.organic,
            "current_stage": "",
            "stage_history": state.stage_history,
            "warnings": state.warnings,
        }

    except Exception as exc:
        logger.error("publish_node_failed", execution_id=exec_id, error=str(exc))
        errors.append(f"publish_node: {exc}")
        state.complete_stage("publish", StageStatus.FAILED, artifacts={"errors": errors})
        return {
            "organic": state.organic,
            "current_stage": "",
            "stage_history": state.stage_history,
            "warnings": state.warnings,
        }


# -------------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------------


def _validate_content(state: EPState, publish_results: dict[str, Any]) -> list[str]:
    """
    Validate content before publishing (moderation check placeholder).

    Returns:
        List of warning strings (empty = passed)
    """
    warnings: list[str] = []

    # Placeholder: check for banned words, link validation, etc.
    # In production, integrate with OpenAI Moderation API or similar

    return warnings


def _check_moderation(text: str) -> bool:
    """
    Placeholder for content moderation check.

    Returns True if content passes, False if it should be rejected.
    """
    # TODO: integrate OpenAI Moderation API
    banned = ["spam", "scam", "click here", "act now"]
    text_lower = text.lower()
    return not any(word in text_lower for word in banned)


# -------------------------------------------------------------------------
# Content resolution
# -------------------------------------------------------------------------


def _resolve_variant_body(state: EPState, variant_id: str) -> str:
    """Extract the body text for a variant_id from state."""
    copy_variants = state.copy_variants or {}
    for content_id, variants in copy_variants.items():
        for variant in variants:
            if variant.variant_id == variant_id:
                return variant.body
    return ""


def _resolve_media_for_platform(
    state: EPState,
    platform: str,
    variant_id: str,
) -> dict[str, Any]:
    """Resolve media assets for a specific platform and variant."""
    creative_assets = state.creative_assets or {}
    media: dict[str, Any] = {}

    # Find assets matching the content_id of the variant
    for content_id, assets in creative_assets.items():
        for asset in assets:
            if asset.platform == platform or asset.platform == "all":
                if "image" in asset.asset_type:
                    media["image_path"] = asset.url  # local path or URL

    return media


# -------------------------------------------------------------------------
# Workflow helpers
# -------------------------------------------------------------------------


def schedule_publish_workflow(
    state: EPState,
    platforms: list[str],
    scheduled_at: str,
) -> dict[str, Any]:
    """
    Schedule content for future publishing via Buffer.

    This is an alternative entry point when the user wants to schedule
    rather than publish immediately.
    """
    manager = PublishManager()

    results = []
    copy_variants = state.copy_variants or {}

    for content_id, variants in copy_variants.items():
        for variant in variants:
            if variant.platform in platforms:
                try:
                    result = manager.publish(
                        content=variant.body,
                        platforms=[variant.platform],
                        scheduled_at=scheduled_at,
                    )
                    results.append(result.to_dict())
                except Exception as exc:
                    logger.error("schedule_error", platform=variant.platform, error=str(exc))

    return {"scheduled_posts": results, "scheduled_at": scheduled_at}