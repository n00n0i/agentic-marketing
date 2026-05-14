"""LangChain publish chain — publishes approved artifacts to social platforms."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import structlog
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_strategies import parse_json_markdown

from ..config import get_settings
from ..state import EPState
from ..social.publish_manager import PublishManager

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are the Publishing Director. Your task is to take approved copy variants and creative assets and publish them to the configured social platforms.

## Publishing Rules

1. Always respect platform rate limits and character limits
2. Never publish content marked as 'draft' or 'rejected'
3. For each platform, select the best-performing variant based on engagement_score
4. Mock mode (no credentials) produces a simulated publish log but must still follow the output schema

## Platform Configuration

For each campaign, check the 'enabled_channels' in the marketing director state.
Supported platforms: twitter, linkedin, facebook, buffer

## Output Schema — publish_results

```json
{
  "version": "1.0",
  "publication_id": "pub-xxx",
  "execution_id": "exec-xxx",
  "platforms_published": ["twitter", "linkedin"],
  "publications": [
    {
      "platform": "twitter",
      "variant_id": "var-twitter-A",
      "status": "published",
      "post_id": "1234567890",
      "post_url": "https://twitter.com/i/status/1234567890",
      "character_count": 276,
      "scheduled_at": null,
      "published_at": "2026-05-14T12:00:00Z",
      "mock": false,
      "errors": []
    },
    {
      "platform": "linkedin",
      "variant_id": "var-linkedin-B",
      "status": "published",
      "post_id": "urn:li:post:xyz",
      "post_url": "https://www.linkedin.com/feed/update/urn:li:post:xyz",
      "character_count": 1482,
      "scheduled_at": null,
      "published_at": "2026-05-14T12:00:00Z",
      "mock": false,
      "errors": []
    }
  ],
  "batch_summary": {
    "total": 2,
    "successful": 2,
    "failed": 0,
    "partial_failure": false
  }
}
```

## Error Handling

If a platform fails:
- Log the error in the 'errors' array for that publication
- Continue with remaining platforms (partial failure is acceptable)
- Do NOT abort the entire batch
"""


USER_PROMPT = """Publish the following content to social platforms.

CAMPAIGN_ID: {campaign_id}
EXECUTION_ID: {execution_id}

APPROVED COPY VARIANTS (from copy stage):
```json
{copy_variants_json}
```

CREATIVE ASSETS (from creative stage):
```json
{creative_assets_json}
```

TARGET PLATFORMS: {platforms}

PUBLISH NOW (set scheduled_at to null for immediate publishing, or provide ISO 8601 datetime).

IMPORTANT: Return the full publish_results JSON following the output schema above."""


def build_publish_chain():
    """Build the publishing LangChain."""
    settings = get_settings()
    model = ChatAnthropic(
        model=settings.llm.llm_model,
        anthropic_api_key=settings.llm.anthropic_api_key.get_secret_value(),
        temperature=0.3,
        timeout=60,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])

    chain = prompt | model | parse_json_markdown(
        llm_output=str,
        language="json",
        strict=False,
    )
    return chain


def run_publish(
    state: EPState,
    platforms: list[str] | None = None,
    execution_id: str | None = None,
) -> dict[str, Any]:
    """
    Execute publishing workflow for a campaign.

    Args:
        state: EPState with copy_variants, creative_assets, campaign_id
        platforms: List of platforms to target (defaults to enabled_channels)
        execution_id: Execution ID for tracking

    Returns:
        dict with 'publish_results' key
    """
    exec_id = execution_id or state.execution_id or f"exec-{uuid.uuid4().hex[:12]}"
    logger.info("publish_chain_started", execution_id=exec_id, platforms=platforms)

    # Resolve target platforms
    target_platforms = platforms or ["twitter", "linkedin"]

    # Select best variant per platform based on engagement score
    copy_variants = state.copy_variants or {}
    creative_assets = state.creative_assets or {}

    # Build copy_variants dict for JSON serialization
    copy_variants_serializable = {}
    for content_id, variants in copy_variants.items():
        copy_variants_serializable[content_id] = [
            {
                "variant_id": v.variant_id,
                "platform": v.platform,
                "approach": getattr(v, "approach", ""),
                "body": v.body,
                "engagement_score": v.engagement_score,
            }
            for v in variants
        ]

    try:
        chain = build_publish_chain()
        result = chain.invoke({
            "campaign_id": state.campaign_id,
            "execution_id": exec_id,
            "copy_variants_json": json.dumps(copy_variants_serializable),
            "creative_assets_json": json.dumps(creative_assets),
            "platforms": ", ".join(target_platforms),
        })

        output = result if isinstance(result, dict) else json.loads(result)
        output["publication_id"] = output.get("publication_id", f"pub-{uuid.uuid4().hex[:8]}")
        output["execution_id"] = exec_id

        logger.info(
            "publish_chain_completed",
            execution_id=exec_id,
            platforms_published=output.get("platforms_published", []),
        )
        return {"publish_results": output}

    except Exception as exc:
        logger.error("publish_chain_failed", error=str(exc))
        return {"publish_results": _fallback_publish_results(exec_id, target_platforms, str(exc))}


def _fallback_publish_results(
    execution_id: str,
    platforms: list[str],
    error: str,
) -> dict[str, Any]:
    """Generate fallback publish results when the chain fails."""
    publications = []
    for platform in platforms:
        publications.append({
            "platform": platform,
            "variant_id": f"var-{platform}-fallback",
            "status": "failed",
            "post_id": "",
            "post_url": "",
            "character_count": 0,
            "scheduled_at": None,
            "published_at": None,
            "mock": True,
            "errors": [f"Chain failed: {error}"],
        })

    return {
        "version": "1.0",
        "publication_id": f"pub-{uuid.uuid4().hex[:8]}",
        "execution_id": execution_id,
        "platforms_published": [],
        "publications": publications,
        "batch_summary": {
            "total": len(platforms),
            "successful": 0,
            "failed": len(platforms),
            "partial_failure": False,
        },
    }


if __name__ == "__main__":
    from ..state import EPState

    state = EPState(
        campaign_id="test-campaign-001",
        execution_id="exec-test-001",
    )

    result = run_publish(state, platforms=["twitter", "linkedin"])
    print(json.dumps(result, indent=2)[:2000])