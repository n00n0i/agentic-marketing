"""Main marketing pipeline agent — orchestrates all director agents via LangGraph."""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from ..config import get_settings
from ..state import MarketingState, StageStatus
from ..models import db_session, Campaign, Artifact, StageAttempt
from .copy_agent import CopyAgent
from .creative_agent import CreativeAgent
from .repurpose_agent import RepurposeAgent

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are the Marketing Director — an Executive Producer for content campaigns.

You orchestrate the full marketing pipeline: research → strategy → copy → creative → publish → analytics.

## Your Responsibilities
1. Review the campaign brief and determine pipeline stages needed
2. Execute each stage in order, respecting dependencies
3. Ensure quality via CHAI review at each stage
4. Log all decisions to the decision log
5. Manage budget and track costs

## Stage Order
1. research — market intelligence and audience research
2. strategy — channel strategy and budget allocation
3. brief — content brief for each piece
4. copy — generate copy variants (3-5 per piece)
5. creative — generate visual assets
6. repurpose — transform 1 piece into 10+ pieces
7. publish — schedule and publish content
8. analytics — track performance and report

## Quality Gate (CHAI Review)
Every stage output must pass CHAI review before proceeding:
- Complete: All required fields present?
- Helpful: Does it serve the audience?
- Accurate: Is the information correct?
- Actionable: Can the next stage use it?
- Insightful: Does it provide genuine value?

## Decision Logging
Log every significant decision:
- Stage start/end
- Options considered
- Selected approach and reasoning
- Issues encountered

## Budget Management
- Estimate cost before each stage
- Reserve budget before spending
- Reconcile after completion
"""


class MarketingAgent:
    """
    Main orchestrating agent using LangGraph for state management.
    
    Coordinates copy_agent, creative_agent, and repurposing_agent
    according to the pipeline manifest.
    """

    def __init__(self, campaign_id: str | None = None):
        self.execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        self.campaign_id = campaign_id
        self.settings = get_settings()
        
        # Initialize sub-agents
        self.copy_agent = CopyAgent(execution_id=self.execution_id)
        self.creative_agent = CreativeAgent(execution_id=self.execution_id)
        self.repurpose_agent = RepurposeAgent(execution_id=self.execution_id)
        
        # LLM for orchestration decisions
        self.llm = ChatAnthropic(
            model=self.settings.anthropic_model,
            api_key=self.settings.anthropic_api_key,
            timeout=60000,
        )
        
        # Build LangGraph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        
        workflow = StateGraph(MarketingState)
        
        # Add nodes
        workflow.add_node("research", self._research_node)
        workflow.add_node("strategy", self._strategy_node)
        workflow.add_node("brief", self._brief_node)
        workflow.add_node("copy", self._copy_node)
        workflow.add_node("creative", self._creative_node)
        workflow.add_node("repurpose", self._repurpose_node)
        workflow.add_node("publish", self._publish_node)
        workflow.add_node("analytics", self._analytics_node)
        workflow.add_node("review", self._review_node)
        
        # Define edges
        workflow.add_edge("research", "strategy")
        workflow.add_edge("strategy", "brief")
        workflow.add_edge("brief", "copy")
        workflow.add_edge("copy", "creative")
        workflow.add_edge("creative", "repurpose")
        workflow.add_edge("repurpose", "publish")
        workflow.add_edge("publish", "analytics")
        workflow.add_edge("analytics", END)
        
        # Conditional: route to review or skip based on stage config
        workflow.add_conditional_edges(
            "brief",
            self._should_review,
            {"review": "review", "skip": "copy"}
        )
        
        workflow.set_entry_point("research")
        return workflow.compile()

    def _should_review(self, state: MarketingState) -> str:
        """Determine if a stage needs human review."""
        stage = state.get("current_stage", "")
        if state.get("human_approval_required", False):
            return "review"
        return "skip"

    def _research_node(self, state: MarketingState) -> dict:
        """Execute research stage."""
        logger.info("research_node_started", execution_id=self.execution_id)
        
        # Placeholder — actual implementation would call research_chain
        result = {
            "stage_status": "completed",
            "artifacts": {
                "market_brief": {
                    "brief_id": f"mb-{uuid.uuid4().hex[:8]}",
                    "topics_covered": state.get("topic", "general"),
                    "audience_segments": [
                        {
                            "segment_id": "seg-1",
                            "name": "B2B SaaS Founders",
                            "demographics": {"age_range": "28-45", "roles": ["Founder", "CEO", "CTO"]},
                            "psychographics": {"fears": ["scaling too slow", "burnout"]},
                        }
                    ],
                }
            },
            "stage_metrics": {"cost_estimate": 0.05, "duration_seconds": 30},
        }
        
        logger.info("research_node_completed", execution_id=self.execution_id)
        return result

    def _strategy_node(self, state: MarketingState) -> dict:
        """Execute strategy stage."""
        logger.info("strategy_node_started", execution_id=self.execution_id)
        
        result = {
            "stage_status": "completed",
            "artifacts": {
                "channel_strategy": {
                    "strategy_id": f"strat-{uuid.uuid4().hex[:8]}",
                    "channels": ["twitter", "linkedin"],
                    "budget_allocation": {"total": 100, "organic": 60, "paid": 40},
                }
            },
            "stage_metrics": {"cost_estimate": 0.03, "duration_seconds": 20},
        }
        
        logger.info("strategy_node_completed", execution_id=self.execution_id)
        return result

    def _brief_node(self, state: MarketingState) -> dict:
        """Execute brief stage."""
        logger.info("brief_node_started", execution_id=self.execution_id)
        
        topic = state.get("topic", "AI Automation for SaaS")
        
        result = {
            "stage_status": "completed",
            "artifacts": {
                "content_brief": {
                    "brief_id": f"cb-{uuid.uuid4().hex[:8]}",
                    "topic": topic,
                    "platforms": ["twitter", "linkedin"],
                    "objectives": {"primary": "awareness", "secondary": ["consideration"]},
                    "target_segment": "seg-1",
                }
            },
            "stage_metrics": {"cost_estimate": 0.02, "duration_seconds": 15},
        }
        
        logger.info("brief_node_completed", execution_id=self.execution_id)
        return result

    def _copy_node(self, state: MarketingState) -> dict:
        """Execute copy generation stage."""
        logger.info("copy_node_started", execution_id=self.execution_id)
        
        market_brief = state.get("artifacts", {}).get("market_brief", {})
        content_brief = state.get("artifacts", {}).get("content_brief", {})
        brand_voice = state.get("brand_voice", {})
        platform = state.get("primary_platform", "twitter")
        
        try:
            copy_result = self.copy_agent.generate_variants(
                market_brief=market_brief,
                content_brief=content_brief,
                brand_voice=brand_voice,
                platform=platform,
            )
        except Exception as e:
            logger.warning("copy_agent_fallback", error=str(e))
            # Fallback variants if LLM fails
            topic = content_brief.get("topic", state.get("topic", "AI Automation"))
            copy_result = _generate_fallback_copy(topic, platform)
        
        logger.info(
            "copy_node_completed",
            execution_id=self.execution_id,
            variant_count=len(copy_result.get("variants", [])),
        )
        
        return {
            "stage_status": "completed",
            "artifacts": {"copy_variants": copy_result},
            "stage_metrics": {
                "cost_estimate": copy_result.get("cost_estimate", 0.08),
                "duration_seconds": 45,
            },
        }

    def _creative_node(self, state: MarketingState) -> dict:
        """Execute creative/image generation stage."""
        logger.info("creative_node_started", execution_id=self.execution_id)
        
        copy_variants = state.get("artifacts", {}).get("copy_variants", {})
        variants = copy_variants.get("variants", [])
        platform = state.get("primary_platform", "twitter")
        
        assets = []
        for i, variant in enumerate(variants[:3]):  # Generate up to 3 images
            try:
                image_result = self.creative_agent.generate_image(
                    prompt=f"Marketing illustration for: {variant.get('body', '')[:200]}",
                    platform=platform,
                    seed=42 + i,
                )
                assets.append(image_result)
            except Exception as e:
                logger.warning("creative_agent_fallback", error=str(e))
                # Fallback: return placeholder
                assets.append({
                    "asset_id": f"asset-{i+1}",
                    "image_url": None,
                    "status": "placeholder",
                    "platform": platform,
                })
        
        result = {
            "stage_status": "completed",
            "artifacts": {"creative_assets": {"assets": assets}},
            "stage_metrics": {"cost_estimate": 0.30, "duration_seconds": 120},
        }
        
        logger.info("creative_node_completed", execution_id=self.execution_id, asset_count=len(assets))
        return result

    def _repurpose_node(self, state: MarketingState) -> dict:
        """Execute content repurposing stage."""
        logger.info("repurpose_node_started", execution_id=self.execution_id)
        
        copy_variants = state.get("artifacts", {}).get("copy_variants", {})
        variants = copy_variants.get("variants", [])
        
        if not variants:
            return {"stage_status": "completed", "artifacts": {"repurposed_content": {"pieces": []}}}
        
        primary_copy = variants[0] if variants else {}
        
        try:
            repurposed = self.repurpose_agent.transform(
                source_content=primary_copy.get("body", ""),
                source_title=primary_copy.get("hook", ""),
                platforms=["twitter", "linkedin", "instagram"],
            )
        except Exception as e:
            logger.warning("repurpose_agent_fallback", error=str(e))
            repurposed = _generate_fallback_repurpose(primary_copy)
        
        result = {
            "stage_status": "completed",
            "artifacts": {"repurposed_content": repurposed},
            "stage_metrics": {"cost_estimate": 0.10, "duration_seconds": 60},
        }
        
        logger.info("repurpose_node_completed", execution_id=self.execution_id)
        return result

    def _publish_node(self, state: MarketingState) -> dict:
        """Execute publishing stage."""
        logger.info("publish_node_started", execution_id=self.execution_id)
        
        result = {
            "stage_status": "completed",
            "artifacts": {
                "publish_log": {
                    "log_id": f"pub-{uuid.uuid4().hex[:8]}",
                    "publications": [
                        {
                            "publication_id": f"pub-{i+1}",
                            "platform": p,
                            "status": "simulated",
                            "scheduled_at": "2026-05-14T12:00:00Z",
                        }
                        for i, p in enumerate(["twitter", "linkedin"])
                    ],
                }
            },
            "stage_metrics": {"cost_estimate": 0.01, "duration_seconds": 10},
        }
        
        logger.info("publish_node_completed", execution_id=self.execution_id)
        return result

    def _analytics_node(self, state: MarketingState) -> dict:
        """Execute analytics/reporting stage."""
        logger.info("analytics_node_started", execution_id=self.execution_id)
        
        result = {
            "stage_status": "completed",
            "artifacts": {
                "performance_report": {
                    "report_id": f"perf-{uuid.uuid4().hex[:8]}",
                    "summary": {
                        "total_impressions": 0,
                        "total_engagements": 0,
                        "engagement_rate": 0.0,
                    },
                    "note": "Analytics will be populated after publication",
                }
            },
            "stage_metrics": {"cost_estimate": 0.01, "duration_seconds": 5},
        }
        
        logger.info("analytics_node_completed", execution_id=self.execution_id)
        return result

    def _review_node(self, state: MarketingState) -> dict:
        """Human review node (placeholder)."""
        logger.info("review_node_started", execution_id=self.execution_id)
        return {"stage_status": "pending_review", "review_requested": True}

    def run(self, topic: str, **kwargs) -> dict[str, Any]:
        """
        Run the full marketing pipeline.
        
        Args:
            topic: The main topic/theme for the campaign
            **kwargs: Additional config (platform, brand_voice, etc.)
            
        Returns:
            Final state with all artifacts
        """
        initial_state = MarketingState(
            execution_id=self.execution_id,
            campaign_id=self.campaign_id,
            topic=topic,
            primary_platform=kwargs.get("platform", "twitter"),
            brand_voice=kwargs.get("brand_voice", {}),
            human_approval_required=False,
            current_stage="research",
            artifacts={},
            stage_status={},
            stage_metrics={},
            decision_log=[],
            budget_reserved=0.0,
            budget_spent=0.0,
        )
        
        logger.info("marketing_agent_run_started", execution_id=self.execution_id, topic=topic)
        
        try:
            final_state = self.graph.invoke(initial_state)
            logger.info(
                "marketing_agent_run_completed",
                execution_id=self.execution_id,
                stages_completed=len(final_state.get("stage_status", {})),
            )
            return final_state
        except Exception as e:
            logger.error("marketing_agent_run_failed", execution_id=self.execution_id, error=str(e))
            raise


def _generate_fallback_copy(topic: str, platform: str) -> dict:
    """Generate minimal copy variants when LLM is unavailable."""
    hooks = [
        f"How {topic} is changing the game",
        f"The truth about {topic} no one tells you",
        f"Why teams fail at {topic} (and how to succeed)",
    ]
    
    return {
        "variants": [
            {
                "variant_id": f"var-{i+1}",
                "approach": approach,
                "hook": hooks[i],
                "body": f"{hooks[i]}. In today's competitive landscape, understanding {topic} is critical for growth. Our approach delivers results.",
                "cta": "Get your free assessment",
                "platform": platform,
                "engagement_score": 7.0 + i * 0.5,
            }
            for i, approach in enumerate(["problem_led", "outcome_led", "stat_led"])
        ],
        "platform": platform,
        "total_variants": 3,
        "cost_estimate": 0.05,
        "generation_method": "fallback",
    }


def _generate_fallback_repurpose(primary_copy: dict) -> dict:
    """Generate minimal repurposed content when LLM is unavailable."""
    body = primary_copy.get("body", "Content about AI automation")
    
    return {
        "pieces": [
            {"platform": "twitter", "content": f"Thread: {body[:200]}...", "type": "thread"},
            {"platform": "linkedin", "content": f"{body}\n\n#AI #Automation", "type": "post"},
            {"platform": "instagram", "content": f"AI automation tip 🧵\n\n{body[:150]}...\n\nSave this!", "type": "caption"},
        ],
        "total_pieces": 3,
        "cost_estimate": 0.03,
        "generation_method": "fallback",
    }


# Convenience function for quick testing
def run_marketing_pipeline(topic: str, **kwargs) -> dict[str, Any]:
    """Run the marketing pipeline with default configuration."""
    agent = MarketingAgent()
    return agent.run(topic=topic, **kwargs)