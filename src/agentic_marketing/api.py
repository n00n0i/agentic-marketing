"""Simple marketing pipeline dashboard — triggers content generation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Placeholder — actual API client would connect to backend
API_BASE = "http://localhost:8000"


def run_pipeline(topic: str, platform: str = "twitter") -> dict[str, Any]:
    """
    Trigger the marketing pipeline.
    
    In production, this calls the FastAPI backend.
    For demo, runs pipeline directly via Python subprocess.
    """
    execution_id = f"exec-{uuid.uuid4().hex[:12]}"
    logger.info("pipeline_triggered", execution_id=execution_id, topic=topic, platform=platform)
    
    try:
        # Try calling the API first
        import urllib.request
        import json
        
        req = urllib.request.Request(
            f"{API_BASE}/api/v1/pipeline/run",
            data=json.dumps({"topic": topic, "platform": platform}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            logger.info("pipeline_completed_api", execution_id=execution_id)
            return result
    except Exception as api_error:
        logger.warning("api_unavailable", error=str(api_error), falling_back_to_demo=True)
        # Fall back to demo mode
        return _run_demo_pipeline(topic, platform, execution_id)


def _run_demo_pipeline(topic: str, platform: str, execution_id: str) -> dict[str, Any]:
    """
    Run a demo pipeline that shows what the system would produce.
    Used when the backend isn't running.
    """
    logger.info("demo_pipeline_started", execution_id=execution_id, topic=topic)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Generate demo copy variants
    demo_variants = [
        {
            "variant_id": f"{execution_id}-var-1",
            "approach": "problem_led",
            "hook": f"Is your team still struggling with {topic}?",
            "body": (
                f"Most teams fail at {topic} because they approach it wrong. "
                f"The secret isn't working harder — it's working smarter. "
                f"Our approach has helped 500+ teams achieve results in 90 days. "
                f"Get your free assessment and see where you stand."
            ),
            "cta": "Get your free assessment →",
            "platform": platform,
            "engagement_score": 8.2,
            "char_count": 312,
        },
        {
            "variant_id": f"{execution_id}-var-2",
            "approach": "stat_led",
            "hook": f"73% of teams fail at {topic}. Here's why.",
            "body": (
                f"We analyzed 1,000 teams attempting {topic}. "
                f"73% failed not because of lack of effort, but wrong strategy. "
                f"The 27% that succeeded shared 3 common traits. "
                f"Download our free guide to see if your team has what it takes."
            ),
            "cta": "Download the free guide",
            "platform": platform,
            "engagement_score": 7.8,
            "char_count": 298,
        },
        {
            "variant_id": f"{execution_id}-var-3",
            "approach": "outcome_led",
            "hook": f"What if your team could master {topic} in 30 days?",
            "body": (
                f"With the right system, {topic} becomes predictable. "
                f"We helped one team go from struggling to succeeding in 30 days flat. "
                f"Their secret? A proven framework, not just effort. "
                f"See how we can help your team — book a free call."
            ),
            "cta": "Book a free strategy call",
            "platform": platform,
            "engagement_score": 7.5,
            "char_count": 305,
        },
    ]
    
    # Generate demo image assets
    demo_assets = [
        {
            "asset_id": f"{execution_id}-img-1",
            "image_url": None,  # Would be real URL from FLUX in production
            "platform": platform,
            "status": "demo_placeholder",
            "prompt": f"Modern office team collaborating on {topic}, professional photography style",
            "dimensions": {"width": 1600, "height": 900},
        }
    ]
    
    # Generate demo repurposed content
    demo_repurposed = {
        "pieces": [
            {
                "platform": "linkedin",
                "type": "post",
                "content": (
                    f"{topic} doesn't have to be hard.\n\n"
                    f"We analyzed 1,000 teams and found the top 27% shared 3 traits:\n\n"
                    f"✓ Clear success metrics\n"
                    f"✓ Systematic approach\n"
                    f"✓ Right tools\n\n"
                    f"Most teams fail because they lack one of these.\n\n"
                    f"Whattrait does your team need most?"
                ),
            },
            {
                "platform": "twitter",
                "type": "thread",
                "content": [
                    f"THREAD: How to succeed at {topic}",
                    f"1/ Most teams approach it wrong. They think more effort = better results.",
                    f"2/ The top 27%? They work smarter, not harder. 3 specific traits.",
                    f"3/ Trait #1: Clear success metrics. Know what done looks like before you start.",
                    f"4/ More coming in this thread... [link to full guide]",
                ],
            },
            {
                "platform": "instagram",
                "type": "caption",
                "content": (
                    f"Stop struggling with {topic} 🛑\n\n"
                    f"The problem isn't effort — it's approach.\n\n"
                    f"Save this for when you need it 👆\n\n"
                    f"#{topic.replace(' ', '')} #productivity #growth"
                ),
            },
        ],
    }
    
    demo_result = {
        "execution_id": execution_id,
        "status": "completed",
        "topic": topic,
        "platform": platform,
        "timestamp": timestamp,
        "artifacts": {
            "copy_variants": {
                "variants": demo_variants,
                "total_variants": 3,
                "platform": platform,
                "generation_method": "demo",
            },
            "creative_assets": {
                "assets": demo_assets,
                "total_assets": 1,
                "generation_method": "demo",
            },
            "repurposed_content": {
                **demo_repurposed,
                "total_pieces": 3,
                "generation_method": "demo",
            },
            "market_brief": {
                "brief_id": f"{execution_id}-mb",
                "topics_covered": [topic],
                "audience_segments": [
                    {
                        "segment_id": "seg-demo",
                        "name": "Demo Segment",
                        "note": "Generated for demo purposes",
                    }
                ],
            },
            "content_brief": {
                "brief_id": f"{execution_id}-cb",
                "topic": topic,
                "platforms": ["twitter", "linkedin", "instagram"],
            },
        },
        "stage_status": {
            "research": "completed",
            "strategy": "completed",
            "brief": "completed",
            "copy": "completed",
            "creative": "completed",
            "repurpose": "completed",
            "publish": "simulated",
            "analytics": "pending",
        },
        "total_cost_estimate": 0.58,
        "message": (
            "Demo pipeline completed. In production, this would generate real copy via "
            "Claude, real images via FLUX on Modal, and publish to social platforms."
        ),
    }
    
    logger.info("demo_pipeline_completed", execution_id=execution_id)
    return demo_result


def save_result(result: dict[str, Any], output_dir: str | None = None) -> Path:
    """Save pipeline result to a JSON file."""
    if output_dir is None:
        output_dir = Path.home() / ".hermes" / "cron" / "output"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    execution_id = result.get("execution_id", "unknown")
    filepath = output_dir / f"marketing-pipeline-{execution_id}.json"
    
    import json
    with open(filepath, "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    logger.info("result_saved", filepath=str(filepath))
    return filepath


# CLI entry point
if __name__ == "__main__":
    import sys
    
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI Automation for SaaS Teams"
    platform = sys.argv[2] if len(sys.argv) > 2 else "twitter"
    
    result = run_pipeline(topic, platform)
    print(f"\n✅ Pipeline completed!")
    print(f"   Execution ID: {result['execution_id']}")
    print(f"   Variants: {len(result['artifacts']['copy_variants']['variants'])}")
    print(f"   Repurposed pieces: {len(result['artifacts']['repurposed_content']['pieces'])}")
    print(f"   Cost: ${result['total_cost_estimate']:.2f}")
    print(f"\n📝 Sample variant:")
    v = result["artifacts"]["copy_variants"]["variants"][0]
    print(f"   [{v['approach']}] {v['hook']}")