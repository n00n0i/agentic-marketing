"""Embedding client — OpenAI text-embedding-3-small, no LangChain."""

from __future__ import annotations

import os
import math
import httpx

import structlog


logger = structlog.get_logger(__name__)

_api_key: str | None = None
_model: str = "text-embedding-3-small"
_dim: int = 1536
_base_url: str = "https://api.openai.com/v1"


def init_embedder(api_key: str | None = None, model: str = "text-embedding-3-small") -> None:
    global _api_key, _model, _dim
    _api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    _model = model
    # text-embedding-3-small: 1536 dims, text-embedding-3-large: 3072 dims
    _dim = 3072 if "3-large" in model else 1536
    logger.info("embedder_init", model=_model, dim=_dim)


def embed(text: str) -> list[float]:
    """Return embedding vector for a single text."""
    if not _api_key:
        raise RuntimeError("OPENAI_API_KEY not set. Call init_embedder() first.")

    headers = {
        "Authorization": f"Bearer {_api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": _model, "input": text}

    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{_base_url}/embeddings",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return data["data"][0]["embedding"]


def embed_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Embed multiple texts in batches."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        if not _api_key:
            raise RuntimeError("OPENAI_API_KEY not set. Call init_embedder() first.")

        headers = {
            "Authorization": f"Bearer {_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": _model, "input": batch}

        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{_base_url}/embeddings",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        for item in data["data"]:
            results.append(item["embedding"])

    logger.info("embed_batch_done", total=len(texts), batches=math.ceil(len(texts) / batch_size))
    return results


def get_dim() -> int:
    return _dim