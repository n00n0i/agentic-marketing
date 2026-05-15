"""Embedding client — Cohere embed-english-v3.0, no LangChain."""

from __future__ import annotations

import os
import math
import httpx

import structlog


logger = structlog.get_logger(__name__)

_api_key: str | None = None
_model: str = "embed-english-v3.0"
_dim: int = 1024
_base_url: str = "https://api.cohere.ai/v1"


def init_embedder(api_key: str | None = None, model: str = "embed-english-v3.0") -> None:
    global _api_key, _model, _dim
    _api_key = api_key or os.environ.get("COHERE_API_KEY", "")
    _model = model
    # Cohere embed-english-v3.0: 1024 dims
    _dim = 1024
    logger.info("embedder_init", model=_model, dim=_dim)


def embed(text: str) -> list[float]:
    """Return embedding vector for a single text."""
    if not _api_key:
        raise RuntimeError("COHERE_API_KEY not set. Call init_embedder() first.")

    headers = {
        "Authorization": f"Bearer {_api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": _model, "input_type": "search_document", "texts": [text]}

    with httpx.Client(timeout=30, verify=False) as client:
        response = client.post(
            f"{_base_url}/embed",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return data["embeddings"][0]


def embed_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Embed multiple texts in batches."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        if not _api_key:
            raise RuntimeError("COHERE_API_KEY not set. Call init_embedder() first.")

        headers = {
            "Authorization": f"Bearer {_api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": _model, "input_type": "search_document", "texts": batch}

        with httpx.Client(timeout=60, verify=False) as client:
            response = client.post(
                f"{_base_url}/embed",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        for item in data["embeddings"]:
            results.append(item)

    logger.info("embed_batch_done", total=len(texts), batches=math.ceil(len(texts) / batch_size))
    return results


def get_dim() -> int:
    return _dim