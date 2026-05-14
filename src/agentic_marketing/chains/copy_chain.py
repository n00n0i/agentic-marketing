"""Copy writing chain — generates 3-5 variants per platform with engagement scoring."""

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
from ..state import CopyVariant

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a senior copywriter specializing in B2B SaaS content.
Given a market brief, generate 3-5 distinct copy variants for each target platform.

## Platform Specs

| Platform | Max Chars | Tone | Format |
|----------|-----------|------|--------|
| Twitter/X | 280 | Conversational, value-dense | Hook + link |
| LinkedIn | 3,000 | Professional, storytelling | Hook + body + CTA |
| Instagram | 2,200 | Visual-first, casual | Caption + CTA in comments |
| Email Subject | 50 | Curiosity + urgency | Question or number |
| Email Body | 150-300 words | Personal, helpful | Story + value + CTA |

## Approaches (use one per variant)
- Problem-Led: Start with pain point → show solution → CTA
- Outcome-Led: Start with desired state → quantify → proof → CTA
- Question-Led: Start with engaging question → reveal → CTA
- Stat-Led: Lead with surprising number → explain → solution → CTA
- Story-Led: Brief narrative → pivot to insight → CTA

## CTA Rules
- NEVER use "click here" or "learn more"
- Be specific: "Get the 2026 AI Marketing Report" not "get our report"
- Match commitment level to awareness level

## Engagement Scoring (1-10 per factor)
- hook_strength: Does the first line grab attention?
- clarity: Is the message immediately understood?
- relevance: Does it resonate with target segment?
- specificity: Are claims backed with specifics?
- cta_strength: Is the CTA specific and compelling?
- word_count_fit: Is length appropriate for platform?

Overall = weighted avg (hooks:0.25, clarity:0.15, relevance:0.20,
                           specificity:0.15, cta:0.15, fit:0.10)

## Output Schema
```json
{
  "version": "1.0",
  "content_piece_id": "cp-xxx",
  "market_brief_ref": "mb-xxx",
  "primary_message": "Core message all variants share",
  "target_segment": "seg-xxx",
  "platforms": ["twitter", "linkedin"],
  "variants": [
    {
      "variant_id": "var-platform-ltr",
      "platform": "twitter",
      "approach": "problem-led",
      "body": "Full copy text...",
      "word_count": 0,
      "character_count": 0,
      "cta": {
        "type": "resource_download",
        "text": "Specific CTA text",
        "url": "https://...",
        "placement": "end"
      },
      "engagement_score": {
        "overall": 0.0,
        "hook_strength": 0,
        "clarity": 0,
        "relevance": 0,
        "specificity": 0,
        "cta_strength": 0,
        "word_count_fit": 0
      },
      "engagement_rationale": "Why this scored this way",
      "posting_time": { "day": "Wednesday", "time": "7am EST" }
    }
  ]
}
```

Rules:
- Each variant must have a DISTINCT approach (not just rewording)
- Character count MUST be within platform limits
- All claims must be grounded in market_brief data
- Brand voice: professional but approachable (use contractions appropriately)
"""


USER_PROMPT = """Generate copy variants for the following content brief.

MARKET BRIEF (from research stage):
```json
{market_brief_json}
```

CONTENT BRIEF:
```json
{content_brief_json}
```

BRAND VOICE:
```json
{brand_voice_json}
```

TARGET PLATFORM: {platform}

Return the full copy_variants JSON with 3-5 distinct variants for Twitter/LinkedIn/Email."""


def load_skill_markup(skill_path: str) -> str:
    """Read a skill .md file and return its contents."""
    project_root = Path(__file__).resolve().parents[3]
    path = project_root / "skills" / f"{skill_path}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def build_copy_chain():
    """Build the copy writing chain."""
    settings = get_settings()
    model = ChatAnthropic(
        model=settings.llm.llm_model,
        anthropic_api_key=settings.llm.anthropic_api_key.get_secret_value(),
        temperature=0.7,
        timeout=90,
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


def run_copy_generation(
    market_brief: dict[str, Any],
    content_brief: dict[str, Any],
    brand_voice: dict[str, Any],
    platform: str = "twitter",
    execution_id: str | None = None,
) -> dict[str, Any]:
    """
    Generate copy variants for a content piece.

    Args:
        market_brief: Output from research stage
        content_brief: Content brief dict with topic, goal, key_message
        brand_voice: Brand voice configuration
        platform: Primary platform (twitter, linkedin, email)
        execution_id: Execution ID for tracking

    Returns:
        copy_variants dict with 3-5 variants and engagement scores
    """
    exec_id = execution_id or f"exec-{uuid.uuid4().hex[:12]}"
    logger.info("copy_generation_started", platform=platform, execution_id=exec_id)

    try:
        chain = build_copy_chain()
        result = chain.invoke({
            "market_brief_json": json.dumps(market_brief),
            "content_brief_json": json.dumps(content_brief),
            "brand_voice_json": json.dumps(brand_voice),
            "platform": platform,
        })

        output = result if isinstance(result, dict) else json.loads(result)
        output["execution_id"] = exec_id
        output["platform"] = platform

        logger.info(
            "copy_generation_completed",
            execution_id=exec_id,
            variants=len(output.get("variants", [])),
        )
        return output

    except Exception as exc:
        logger.error("copy_generation_failed", error=str(exc))
        return _fallback_copy_variants(market_brief, content_brief, platform, exec_id)


def _fallback_copy_variants(
    market_brief: dict[str, Any],
    content_brief: dict[str, Any],
    platform: str,
    execution_id: str,
) -> dict[str, Any]:
    """Generate placeholder variants when the chain fails."""
    topic = content_brief.get("topic", market_brief.get("topic", "Marketing"))
    primary_msg = content_brief.get("key_message", f"Learn about {topic}")

    return {
        "version": "1.0",
        "content_piece_id": f"cp-{uuid.uuid4().hex[:8]}",
        "market_brief_ref": market_brief.get("execution_id", execution_id),
        "primary_message": primary_msg,
        "target_segment": market_brief.get("audience_segments", [{}])[0].get("segment_id", "seg-001"),
        "platforms": [platform],
        "variants": [
            {
                "variant_id": f"var-{platform}-A",
                "platform": platform,
                "approach": "problem-led",
                "body": f"Struggling with {topic}? Here's how to fix it. [Full guide →]",
                "word_count": 15,
                "character_count": 65,
                "cta": {"type": "resource_download", "text": "Get the Guide", "placement": "end"},
                "engagement_score": {
                    "overall": 7.0,
                    "hook_strength": 7,
                    "clarity": 7,
                    "relevance": 7,
                    "specificity": 6,
                    "cta_strength": 7,
                    "word_count_fit": 8,
                },
                "engagement_rationale": "Fallback variant - chain failed",
            },
            {
                "variant_id": f"var-{platform}-B",
                "platform": platform,
                "approach": "stat-led",
                "body": f"73% of teams using AI for {topic} see major improvements. Are you in the 27% yet?",
                "word_count": 22,
                "character_count": 98,
                "cta": {"type": "engagement", "text": "Comment below", "placement": "end"},
                "engagement_score": {
                    "overall": 7.5,
                    "hook_strength": 8,
                    "clarity": 7,
                    "relevance": 7,
                    "specificity": 7,
                    "cta_strength": 7,
                    "word_count_fit": 8,
                },
                "engagement_rationale": "Fallback variant - chain failed",
            },
            {
                "variant_id": f"var-{platform}-C",
                "platform": platform,
                "approach": "question-led",
                "body": f"Is your team still doing {topic} manually? The cost is higher than you think.",
                "word_count": 18,
                "character_count": 82,
                "cta": {"type": "resource_download", "text": "Free Audit", "placement": "end"},
                "engagement_score": {
                    "overall": 7.2,
                    "hook_strength": 8,
                    "clarity": 7,
                    "relevance": 7,
                    "specificity": 6,
                    "cta_strength": 7,
                    "word_count_fit": 8,
                },
                "engagement_rationale": "Fallback variant - chain failed",
            },
        ],
        "execution_id": execution_id,
    }


if __name__ == "__main__":
    sample_brief = {
        "execution_id": "exec-test",
        "topic": "AI for SaaS",
        "audience_segments": [
            {
                "segment_id": "seg-001",
                "name": "SaaS Founders",
                "demographics": {"age": "30-50"},
                "psychographics": {"pain_points": ["churn", "manual ops"]},
            }
        ],
        "strategic_angles": [
            {"angle_id": "angle-001", "name": "Churn reduction", "description": "AI predicts churn"}
        ],
    }
    sample_content = {
        "topic": "AI for SaaS churn prevention",
        "goal": "Drive trial signups",
        "key_message": "AI can reduce churn by 40%",
    }
    result = run_copy_generation(sample_brief, sample_content, {}, "twitter")
    print(json.dumps(result, indent=2)[:1500])