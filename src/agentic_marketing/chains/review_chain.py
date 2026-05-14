"""CHAI Review Chain — LangChain chain for 5-dimension content review."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class CHAIScores(BaseModel):
    """CHAI review scores for an artifact."""

    complete: int = Field(description="C — Complete: all required elements present (1-5)")
    helpful: int = Field(description="H — Helpful: valuable to target audience (1-5)")
    accurate: int = Field(description="A — Accurate: factually correct (1-5)")
    insightful: int = Field(description="I — Insightful: demonstrates deep understanding (1-5)")
    actionable: int = Field(description="A — Actionable: clear next steps (1-5)")
    overall: float = Field(description="Weighted overall score (0-5)")
    feedback: str = Field(description="Specific feedback per dimension, max 2 sentences each")
    strengths: list[str] = Field(description="What works well (1-3 points)")
    weaknesses: list[str] = Field(description="What needs improvement (1-3 points)")


PROMPT = ChatPromptTemplate.from_template("""You are a senior marketing content reviewer applying the CHAI framework.

Evaluate the following content artifact for a {platform} campaign targeting {audience}.

---
Content Type: {content_type}
Stage: {stage_name}

Content to review:
{content}
---

Rate each dimension 1-5:
- C (Complete): All required elements are present for this stage?
- H (Helpful): Does this provide genuine value to the target audience?
- A (Accurate): Are facts, statistics, and claims correct and verifiable?
- I (Insightful): Does this demonstrate deep audience understanding and market knowledge?
- A (Actionable): Can the reader/listener take clear next steps?

Overall = (C + H + A + I + A) / 5 * 0.9 + min(strengths_count, 3) * 0.1

Pass threshold: overall >= 4.0
Review round: {round_num} of 2

Return your assessment in the specified JSON format.""")


class ReviewChain:
    """LangChain chain for CHAI content review."""

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self._chain = PROMPT | self.llm.with_structured_output(CHAIScores)

    def review(
        self,
        content: str,
        *,
        platform: str = "Twitter",
        audience: str = "B2B SaaS teams",
        content_type: str = "social_post",
        stage_name: str = "copy",
        round_num: int = 1,
    ) -> CHAIScores:
        """
        Run CHAI review on content.

        Args:
            content: Content to review
            platform: Target platform
            audience: Target audience
            content_type: Type of content
            stage_name: Pipeline stage
            round_num: Review round (1 or 2)

        Returns:
            CHAIScores with 5-dimension ratings
        """
        return self._chain.invoke({
            "content": content,
            "platform": platform,
            "audience": audience,
            "content_type": content_type,
            "stage_name": stage_name,
            "round_num": round_num,
        })

    def review_batch(
        self,
        contents: list[str],
        **kwargs,
    ) -> list[CHAIScores]:
        """Review multiple content items."""
        return [self.review(c, **kwargs) for c in contents]


# Demo chain — returns mock scores without LLM
class DemoReviewChain:
    """Demo review chain that returns mock scores."""

    def review(self, content: str, **kwargs) -> CHAIScores:
        words = len(content.split())
        base = 3.5 + (words % 10) * 0.1

        return CHAIScores(
            complete=min(5, max(3, base + 0.3)),
            helpful=min(5, max(3, base + 0.5)),
            accurate=min(5, max(3, base + 0.2)),
            insightful=min(5, max(3, base - 0.1)),
            actionable=min(5, max(3, base + 0.4)),
            overall=min(5.0, base + 0.3),
            feedback="Demo review — configure LLM API key for real evaluation.",
            strengths=["Clear message", "Good structure"],
            weaknesses=["Could be more specific"],
        )

    def review_batch(self, contents: list[str], **kwargs) -> list[CHAIScores]:
        return [self.review(c, **kwargs) for c in contents]