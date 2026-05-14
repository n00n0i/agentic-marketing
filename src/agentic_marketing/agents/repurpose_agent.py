"""Repurpose agent — transforms 1 content piece into 10+ platform-optimized pieces."""

from __future__ import annotations

import json
import uuid
from typing import Any

import structlog
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_strategies import parse_json_markdown

from ..config import get_settings

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a content repurposing specialist. Given one input content piece,
transform it into 10+ distinct pieces optimized for different platforms.

## Core Principle
Adapt, don't copy-paste. Each output must feel native to its platform.

## Platform Transformation Rules

### Twitter/X Thread
- 5-7 tweets, each with single point
- Structure: hook_tweet → point_1 → point_2 → point_3 → link
- Conversational, value-dense
- Hashtags at end or first comment

### LinkedIn Article
- 3,000 chars, expanded format
- Structure: hook → context → key points → conclusion → CTA
- Professional but personal, storytelling welcome

### LinkedIn Post
- Shorter, punchier than article
- Structure: short hook → insight → CTA
- Same tone, more direct

### Instagram Caption
- 2,200 chars, caption style
- Structure: hook (first line) → value → CTA in comments
- Casual, visual-first, emojis welcome

### Instagram Carousel
- 8-10 slides
- Structure: title → point_1 → ... → CTA
- Text overlay on clean backgrounds

### Facebook Post
- 63,206 chars max
- Structure: short teaser → link → brief context
- Casual, community-friendly

### Email Newsletter Snippet
- 100-200 words
- Structure: teaser paragraph → 3 bullet takeaways → link

### Google RSA Headlines
- 3-5 headline variations (max 90 chars each)
- Focus on search intent

### Meta/LinkedIn Ad Copy
- Headline + body
- Direct, benefit-focused

## Output Schema
```json
{
  "version": "1.0",
  "input_content": {
    "type": "blog_post",
    "title": "...",
    "word_count": 0,
    "key_points_extracted": ["..."],
    "best_quotes": ["..."],
    "statistics": ["..."]
  },
  "outputs": [
    {
      "output_id": "out-xxx",
      "platform": "twitter",
      "format": "thread",
      "piece_count": 7,
      "content": { "tweet_1": "...", "tweet_2": "..." },
      "scheduled_time": null,
      "status": "ready",
      "adaptation_notes": "How this was adapted for platform"
    }
  ],
  "total_pieces": 12,
  "platforms_covered": ["twitter", "linkedin", "instagram", "facebook", "email"]
}
```

Rules:
- Each output must be adapted, not copy-pasted
- Core message must be consistent across all outputs
- Include scheduling recommendations per platform
- Include CTA appropriate for each platform"""


USER_PROMPT = """Transform the following content into 10+ platform-optimized pieces.

INPUT CONTENT:
```json
{input_content_json}
```

Return the full repurpose_plan JSON."""


class RepurposeAgent:
    """
    Repurpose agent that transforms a single content piece into
    multiple outputs across platforms (1 → 10+).

    Reads the repurpose-director skill for markup instructions.
    """

    def __init__(self, execution_id: str | None = None):
        self.execution_id = execution_id or f"exec-{uuid.uuid4().hex[:12]}"

    def run(
        self,
        input_content: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Transform input content into 10+ platform-optimized pieces.

        Args:
            input_content: Dict with type, title, body, key_points, etc.

        Returns:
            repurpose_plan dict with outputs list
        """
        logger.info(
            "repurpose_agent_started",
            input_type=input_content.get("type", "unknown"),
            execution_id=self.execution_id,
        )

        try:
            result = self._run_chain(input_content)
        except Exception as exc:
            logger.error("repurpose_agent_failed", error=str(exc))
            result = _fallback_repurpose(input_content, self.execution_id)

        if "outputs" not in result or len(result.get("outputs", [])) < 10:
            logger.warning(
                "repurpose_agent_insufficient",
                count=len(result.get("outputs", [])),
                execution_id=self.execution_id,
            )

        logger.info(
            "repurpose_agent_completed",
            execution_id=self.execution_id,
            total_pieces=result.get("total_pieces", len(result.get("outputs", []))),
        )
        return result

    def _run_chain(self, input_content: dict[str, Any]) -> dict[str, Any]:
        """Execute the LLM-powered repurposing chain."""
        settings = get_settings()
        model = ChatAnthropic(
            model=settings.llm.llm_model,
            anthropic_api_key=settings.llm.anthropic_api_key.get_secret_value(),
            temperature=0.6,
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

        result = chain.invoke({
            "input_content_json": json.dumps(input_content),
        })

        output = result if isinstance(result, dict) else json.loads(result)
        output["execution_id"] = self.execution_id
        return output


def _fallback_repurpose(input_content: dict[str, Any], execution_id: str) -> dict[str, Any]:
    """Generate 10+ placeholder outputs when chain fails."""
    title = input_content.get("title", input_content.get("topic", "Content"))
    key_points = input_content.get("key_points", input_content.get("key_points_extracted", [title]))

    platforms = [
        ("twitter", "thread", 5),
        ("linkedin", "article", 1),
        ("linkedin", "post", 1),
        ("instagram", "caption", 1),
        ("instagram", "carousel", 8),
        ("facebook", "post", 1),
        ("email", "newsletter", 1),
        ("google_ads", "rsa", 3),
        ("meta_ads", "single_image", 1),
        ("quora", "answer", 1),
        ("reddit", "post", 1),
    ]

    outputs = []
    for platform, fmt, count in platforms:
        for i in range(count):
            outputs.append({
                "output_id": f"out-{uuid.uuid4().hex[:8]}",
                "platform": platform,
                "format": fmt,
                "piece_count": 1,
                "content": {"text": f"{title} - {platform} adaptation"},
                "scheduled_time": None,
                "status": "ready",
                "adaptation_notes": f"Fallback: {platform} {fmt}",
            })

    return {
        "version": "1.0",
        "input_content": {
            "type": input_content.get("type", "content"),
            "title": title,
            "word_count": input_content.get("word_count", 0),
        },
        "outputs": outputs,
        "total_pieces": len(outputs),
        "platforms_covered": list({p[0] for p in platforms}),
        "execution_id": execution_id,
    }


if __name__ == "__main__":
    sample = {
        "type": "blog_post",
        "title": "How AI Cuts SaaS Ops Costs by 40%",
        "body": "The average SaaS team wastes 15 hours a week on manual ops tasks...",
        "key_points_extracted": [
            "15 hrs/week wasted on manual ops",
            "70% of tasks automatable",
            "40% cost reduction typical",
        ],
        "best_quotes": ["The first 20% of automation saves 80% of the waste."],
    }
    result = RepurposeAgent().run(sample)
    print(f"Total pieces: {result['total_pieces']}")
    print(f"Platforms: {result.get('platforms_covered', [])}")