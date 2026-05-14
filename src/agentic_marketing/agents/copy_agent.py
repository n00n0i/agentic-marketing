"""Copy generation agent — produces 3-5 copy variants per platform."""

from __future__ import annotations

import json
import uuid
from typing import Any

import structlog

from ..chains.copy_chain import run_copy_generation
from ..state import CopyVariant

logger = structlog.get_logger(__name__)


class CopyAgent:
    """
    Copy generation agent that transforms a content brief into
    platform-optimized copy variants with engagement scoring.

    Reads the copy-director skill for markup instructions.
    """

    def __init__(self, execution_id: str | None = None):
        self.execution_id = execution_id or f"exec-{uuid.uuid4().hex[:12]}"

    def generate_variants(
        self,
        market_brief: dict[str, Any],
        content_brief: dict[str, Any],
        brand_voice: dict[str, Any],
        platform: str = "twitter",
    ) -> dict[str, Any]:
        """
        Generate copy variants for a specific platform.

        Args:
            market_brief: Full market research brief
            content_brief: Content brief with topic, goal, key_message
            brand_voice: Brand voice guidelines
            platform: Primary platform (twitter | linkedin | email)

        Returns:
            dict with variants list and metadata
        """
        logger.info(
            "copy_agent_generating",
            platform=platform,
            execution_id=self.execution_id,
        )

        result = run_copy_generation(
            market_brief=market_brief,
            content_brief=content_brief,
            brand_voice=brand_voice,
            platform=platform,
            execution_id=self.execution_id,
        )

        # Validate basic structure
        if "variants" not in result or not result["variants"]:
            logger.warning("copy_agent_no_variants", execution_id=self.execution_id)
            result = _build_minimal_variants(content_brief, platform, self.execution_id)

        logger.info(
            "copy_agent_completed",
            execution_id=self.execution_id,
            variant_count=len(result.get("variants", [])),
        )
        return result

    def generate_all_platforms(
        self,
        market_brief: dict[str, Any],
        content_brief: dict[str, Any],
        brand_voice: dict[str, Any],
        platforms: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Generate copy variants across multiple platforms.

        Returns a dict keyed by platform, each containing variants list.
        """
        if platforms is None:
            platforms = ["twitter", "linkedin", "email"]

        all_results = {}
        for platform in platforms:
            all_results[platform] = self.generate_variants(
                market_brief=market_brief,
                content_brief=content_brief,
                brand_voice=brand_voice,
                platform=platform,
            )

        return all_results


def _build_minimal_variants(
    content_brief: dict[str, Any],
    platform: str,
    execution_id: str,
) -> dict[str, Any]:
    """Build 3 hardcoded variants when chain fails completely."""
    topic = content_brief.get("topic", "this topic")
    return {
        "version": "1.0",
        "content_piece_id": f"cp-{uuid.uuid4().hex[:8]}",
        "execution_id": execution_id,
        "primary_message": content_brief.get("key_message", f"Learn about {topic}"),
        "platforms": [platform],
        "variants": [
            {
                "variant_id": f"var-{platform}-1",
                "platform": platform,
                "approach": "problem-led",
                "body": f"Having trouble with {topic}? We can help. →",
                "word_count": 10,
                "character_count": 48,
                "cta": {"type": "resource_download", "text": "Learn More", "placement": "end"},
                "engagement_score": {
                    "overall": 6.5, "hook_strength": 6, "clarity": 7,
                    "relevance": 7, "specificity": 5, "cta_strength": 6,
                    "word_count_fit": 7,
                },
                "engagement_rationale": "Minimal fallback variant",
            },
            {
                "variant_id": f"var-{platform}-2",
                "platform": platform,
                "approach": "stat-led",
                "body": f"Most teams struggle with {topic}. Here's the fix. →",
                "word_count": 11,
                "character_count": 52,
                "cta": {"type": "engagement", "text": "See How", "placement": "end"},
                "engagement_score": {
                    "overall": 6.8, "hook_strength": 7, "clarity": 7,
                    "relevance": 7, "specificity": 5, "cta_strength": 6,
                    "word_count_fit": 7,
                },
                "engagement_rationale": "Minimal fallback variant",
            },
            {
                "variant_id": f"var-{platform}-3",
                "platform": platform,
                "approach": "question-led",
                "body": f"Ready to fix {topic}? Start here. →",
                "word_count": 7,
                "character_count": 36,
                "cta": {"type": "resource_download", "text": "Get Started", "placement": "end"},
                "engagement_score": {
                    "overall": 6.6, "hook_strength": 7, "clarity": 7,
                    "relevance": 6, "specificity": 5, "cta_strength": 6,
                    "word_count_fit": 7,
                },
                "engagement_rationale": "Minimal fallback variant",
            },
        ],
    }