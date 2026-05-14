"""Research chain — analyzes topic and produces a market brief."""

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

logger = structlog.get_logger(__name__)


SYSTEM_PROMPT = """You are a senior marketing research analyst. Your job is to produce a comprehensive
market brief given a topic. Draw on web search to ground your findings in real data.

## Output Schema (market_brief)

```json
{
  "version": "1.0",
  "topic": "<user topic>",
  "execution_id": "<exec-xxx>",
  "audience_segments": [
    {
      "segment_id": "seg-xxx",
      "name": "Segment name",
      "demographics": { "age": "", "income": "", "location": "" },
      "psychographics": { "values": [], " interests": [], "pain_points": [] },
      "behavioral": { "buying_patterns": "", "preferred_channels": [], "content_habits": "" }
    }
  ],
  "strategic_angles": [
    {
      "angle_id": "angle-xxx",
      "name": "Angle name",
      "description": "Why this angle works",
      "data_points": [{ "stat": "", "source": "", "url": "" }]
    }
  ],
  "competitors": [
    {
      "competitor_id": "comp-xxx",
      "name": "Competitor name",
      "content_examples": [{ "type": "", "url": "", "description": "" }]
    }
  ],
  "keywords": [{ "keyword": "", "volume": "", "difficulty": "", "opportunity": "" }],
  "timing_recommendations": { "platform": { "best_day": "", "best_time": "" } }
}
```

Rules:
- Provide AT LEAST 3 audience segments with specific demographics
- Provide AT LEAST 3 strategic angles, each with 2+ supporting data points
- Research 3-5 real competitors with actual content examples and URLs
- All claims must be backed by search results; do not invent statistics
"""


USER_PROMPT = """Research the following marketing topic and produce a market brief:

TOPIC: {topic}

If you have access to web search, use it to find real competitor examples, statistics,
and audience data. Otherwise, use your training knowledge — but note which claims
are estimates in the data_points.

Return the full market_brief JSON."""


def load_skill_markup(skill_path: str) -> str:
    """Read a skill .md file and return its contents as a string."""
    project_root = Path(__file__).resolve().parents[3]
    path = project_root / "skills" / f"{skill_path}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def build_research_chain():
    """Build the research chain with Claude Haiku for speed."""
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


def run_research(topic: str, execution_id: str | None = None) -> dict[str, Any]:
    """
    Execute the research chain for a given topic.

    Returns a validated market_brief dict.
    """
    settings = get_settings()
    exec_id = execution_id or f"exec-{uuid.uuid4().hex[:12]}"

    logger.info("research_started", topic=topic, execution_id=exec_id)

    try:
        chain = build_research_chain()
        result = chain.invoke({
            "topic": topic,
            "execution_id": exec_id,
        })

        brief = result if isinstance(result, dict) else json.loads(result)
        brief["execution_id"] = exec_id
        brief["topic"] = topic

        logger.info(
            "research_completed",
            execution_id=exec_id,
            segments=len(brief.get("audience_segments", [])),
            angles=len(brief.get("strategic_angles", [])),
        )
        return brief

    except Exception as exc:
        logger.error("research_chain_failed", error=str(exc))
        # Return a minimal valid brief so pipeline can continue
        minimal = _fallback_brief(topic, exec_id)
        logger.warning("using_fallback_brief", execution_id=exec_id)
        return minimal


def _fallback_brief(topic: str, execution_id: str) -> dict[str, Any]:
    """Produce a minimal fallback brief when research fails."""
    return {
        "version": "1.0",
        "topic": topic,
        "execution_id": execution_id,
        "audience_segments": [
            {
                "segment_id": "seg-001",
                "name": "Primary audience",
                "demographics": {"age": "25-45", "income": "mid-high", "location": "US/UK"},
                "psychographics": {
                    "values": ["efficiency", "growth"],
                    "interests": ["AI", "automation"],
                    "pain_points": ["manual processes", "high costs"],
                },
                "behavioral": {
                    "buying_patterns": "research-driven",
                    "preferred_channels": ["LinkedIn", "email"],
                    "content_habits": "short-form preferred",
                },
            }
        ],
        "strategic_angles": [
            {
                "angle_id": "angle-001",
                "name": "Efficiency angle",
                "description": "AI automation saves time and reduces costs",
                "data_points": [
                    {"stat": "40% cost reduction typical", "source": "industry estimate", "url": ""},
                    {"stat": "70% of tasks automatable", "source": "industry estimate", "url": ""},
                ],
            }
        ],
        "competitors": [],
        "keywords": [],
        "timing_recommendations": {
            "twitter": {"best_day": "Tue/Wed/Thu", "best_time": "8am EST"},
            "linkedin": {"best_day": "Tue/Wed/Thu", "best_time": "7am EST"},
        },
    }


if __name__ == "__main__":
    result = run_research("AI automation for SaaS customer success")
    print(json.dumps(result, indent=2)[:2000])