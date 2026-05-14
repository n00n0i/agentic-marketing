"""Modal FLUX image generation tool."""

from __future__ import annotations

import io
import uuid
from typing import Any

import structlog
from modal import Image, App, Volume, method
from modal.runner import deploy_app

logger = structlog.get_logger(__name__)

# Modal app and volume
APP_NAME = "agentic-marketing-flux"
FLUX_VOLUME = Volume.from_name("flux-assets", create_if_missing=True)

# Base image with FLUX dependencies
flux_image = (
    Image.debian_slim()
    .pip_install("flux-dev", "transformers", "torch>=2.0")
    .env({"HF_HOME": "/assets/hf_cache"})
)


app = App(APP_NAME, image=flux_image)


@app.cls(image=flux_image, volumes={"/assets": FLUX_VOLUME}, timeout=600)
class FluxGenerator:
    """FLUX.1-schnell image generator on Modal."""

    @method()
    def generate(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 28,
        guidance_scale: float = 3.5,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate an image using FLUX.1-schnell via Modal.

        Returns a dict with 'image_url' (data URI) or 'error'.
        """
        import base64
        import tempfile
        from pathlib import Path

        try:
            from diffusers import FluxPipeline
            import torch

            model_id = "black-forest-labs/FLUX.1-schnell"
            cache_dir = "/assets/hf_cache"

            pipe = FluxPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.bfloat16,
                cache_dir=cache_dir,
            )
            pipe = pipe.to("cuda")

            generator = None
            if seed is not None:
                generator = torch.Generator(device="cuda").manual_seed(seed)

            image = pipe(
                prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
            ).images[0]

            # Save to volume
            out_dir = Path(f"/assets/{uuid.uuid4().hex[:8]}")
            out_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{uuid.uuid4().hex[:12]}.png"
            filepath = out_dir / filename
            image.save(str(filepath))

            # Return as base64 data URI
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            data_uri = f"data:image/png;base64,{b64}"

            logger.info("flux_image_generated", prompt=prompt[:50], path=str(filepath))
            return {"image_url": data_uri, "local_path": str(filepath), "status": "success"}

        except Exception as exc:
            logger.error("flux_generation_failed", error=str(exc))
            return {"error": str(exc), "status": "failed"}


# --------------------------------------------------------------------------


def run_flux_generation(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    num_inference_steps: int = 28,
    guidance_scale: float = 3.5,
    seed: int | None = None,
) -> dict[str, Any]:
    """
    Remote call to Modal FLUX endpoint.

    For local development / fallback, returns a placeholder response.
    In production, set MODAL_TOKEN_ID + MODAL_TOKEN_SECRET env vars and
    this function calls the deployed Modal app.
    """
    import os

    if os.environ.get("MODAL_TOKEN_ID") and os.environ.get("MODAL_TOKEN_SECRET"):
        # Call remote Modal app
        from modal import Client

        client = Client()
        app_handle = deploy_app(APP_NAME, skip_confirm=True)
        # Use .remote() call pattern via stubs
        # For simplicity, call via Modal client directly
        stub = FluxGenerator
        return stub.remote.generate(
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed,
        )
    else:
        # Dev/fallback: return a placeholder so the pipeline can still demo
        logger.warning("modal_fallback_mode", message="FLUX running in fallback mode (no Modal credentials)")
        placeholder_b64 = _generate_placeholder_image(prompt, width, height)
        return {
            "image_url": f"data:image/png;base64,{placeholder_b64}",
            "local_path": None,
            "status": "fallback",
            "prompt": prompt,
        }


def _generate_placeholder_image(prompt: str, width: int, height: int) -> str:
    """Generate a simple gradient placeholder PNG as base64 (pure Pillow, no GPU needed)."""
    import base64
    from io import BytesIO
    from PIL import Image as PILImage

    img = PILImage.new("RGB", (width, height), color=(30, 30, 60))
    # Add a simple gradient to make it look less bare
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    for i in range(0, height, 4):
        shade = int(30 + (i / height) * 40)
        draw.rectangle([(0, i), (width, i + 4)], fill=(shade, shade, shade + 20))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# --------------------------------------------------------------------------


class FluxTool:
    """
    LangChain-compatible tool wrapping Modal FLUX image generation.

    Use this as a langchain.tools.Tool so agents can call it directly.
    """

    name = "flux_image_generator"
    description = (
        "Generates visual assets using FLUX AI image generation via Modal. "
        "Input: dict with 'prompt' (str), 'width' (int, default 1024), "
        "'height' (int, default 1024), 'num_inference_steps' (int, default 28), "
        "'guidance_scale' (float, default 3.5), 'seed' (int, optional). "
        "Output: dict with 'image_url' (data URI or URL) or 'error'."
    )

    def invoke(self, tool_input: dict[str, Any] | str) -> str:
        if isinstance(tool_input, str):
            tool_input = {"prompt": tool_input}
        result = run_flux_generation(**tool_input)
        if result.get("status") == "failed":
            return f"Image generation failed: {result.get('error')}"
        return f"Image generated: {result.get('image_url', result.get('local_path', 'unknown'))}"


if __name__ == "__main__":
    # Quick smoke test
    result = run_flux_generation("A sleek dashboard showing marketing analytics", width=512, height=512)
    print(result["status"])