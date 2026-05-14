"""Creative agent — generates visual assets via FLUX on Modal."""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from ..tools.flux_tool import run_flux_generation, FluxTool

logger = structlog.get_logger(__name__)


# Platform aspect ratio specs
PLATFORM_SPECS = {
    "twitter": {"width": 1600, "height": 900, "ratio": "16:9"},
    "linkedin": {"width": 1200, "height": 627, "ratio": "1.91:1"},
    "instagram": {"width": 1080, "height": 1080, "ratio": "1:1"},
    "instagram_reel": {"width": 1080, "height": 1920, "ratio": "9:16"},
    "facebook": {"width": 1200, "height": 630, "ratio": "1.91:1"},
    "google_ads": {"width": 1200, "height": 628, "ratio": "1.91:1"},
    "meta_ads": {"width": 1200, "height": 628, "ratio": "1.91:1"},
}


class CreativeAgent:
    """
    Creative agent that generates visual assets to accompany copy variants.

    Reads the creative-director skill for markup instructions and uses
    FLUX on Modal for AI image generation.
    """

    def __init__(self, execution_id: str | None = None):
        self.execution_id = execution_id or f"exec-{uuid.uuid4().hex[:12]}"
        self.flux_tool = FluxTool()

    def generate_image(
        self,
        prompt: str,
        platform: str = "twitter",
        brand_colors: list[str] | None = None,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate a single visual asset.

        Args:
            prompt: Description of the desired image
            platform: Target platform for format specs
            brand_colors: Optional hex colors to incorporate
            seed: Optional random seed for reproducibility

        Returns:
            dict with image_url, format specs, and asset metadata
        """
        specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["twitter"])

        # Build FLUX prompt
        enhanced_prompt = self._build_prompt(prompt, brand_colors)

        logger.info(
            "creative_agent_generating",
            platform=platform,
            prompt=prompt[:60],
            execution_id=self.execution_id,
        )

        result = run_flux_generation(
            prompt=enhanced_prompt,
            width=specs["width"],
            height=specs["height"],
            seed=seed,
        )

        asset = {
            "asset_id": f"asset-{uuid.uuid4().hex[:8]}",
            "type": "image",
            "purpose": self._infer_purpose(prompt),
            "platform": platform,
            "format": f"{specs['width']}x{specs['height']}",
            "aspect_ratio": specs["ratio"],
            "generation_params": {
                "prompt": enhanced_prompt,
                "width": specs["width"],
                "height": specs["height"],
                "seed": seed,
            },
            "image_url": result.get("image_url"),
            "local_path": result.get("local_path"),
            "status": result.get("status", "unknown"),
        }

        logger.info(
            "creative_agent_completed",
            execution_id=self.execution_id,
            asset_id=asset["asset_id"],
            status=asset["status"],
        )
        return asset

    def generate_quote_graphic(
        self,
        quote: str,
        platform: str = "twitter",
        attribution: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a quote/statement graphic with text overlay.

        Args:
            quote: The quote or statement text
            platform: Target platform
            attribution: Optional attribution line

        Returns:
            dict with image_url and asset metadata
        """
        prompt = (
            f"A clean typographic poster with the text: '{quote}'. "
            f"Minimalist design, high contrast, professional typography. "
            f"No busy backgrounds. Text should be large and readable."
        )
        if attribution:
            prompt += f" Include attribution: '{attribution}'"

        return self.generate_image(prompt, platform=platform)

    def _build_prompt(self, base_prompt: str, brand_colors: list[str] | None) -> str:
        """Enhance a base prompt with brand color and style guidance."""
        prompt = base_prompt
        if brand_colors:
            colors_str = ", ".join(brand_colors)
            prompt += f" Use a color palette centered on: {colors_str}."
        prompt += " Professional photography style, clean composition."
        return prompt

    def _infer_purpose(self, prompt: str) -> str:
        """Guess asset purpose from prompt text."""
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["chart", "graph", "data", "stat"]):
            return "data_visualization"
        if any(word in prompt_lower for word in ["quote", "statement", "text"]):
            return "quote_graphic"
        if any(word in prompt_lower for word in ["product", "hero", "展示"]):
            return "hero_image"
        if any(word in prompt_lower for word in ["ad", "banner"]):
            return "ad_creative"
        return "supporting_visual"


if __name__ == "__main__":
    agent = CreativeAgent()
    result = agent.generate_image(
        prompt="A sleek SaaS dashboard showing customer retention analytics",
        platform="linkedin",
        brand_colors=["#1a1a2e", "#e94560"],
    )
    print("Asset ID:", result["asset_id"])
    print("Status:", result["status"])
    print("Format:", result["format"])