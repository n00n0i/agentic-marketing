"""OpenAI LLM client — production ready, no LangChain."""

from __future__ import annotations

import os
import json
from typing import Any

import httpx

import structlog


logger = structlog.get_logger(__name__)

_api_key: str | None = None
_model: str = "gpt-4o-mini"
_base_url: str = "https://api.openai.com/v1"
_timeout_seconds: int = 60


def init_llm(api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
    global _api_key, _model
    _api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    _model = model
    logger.info("llm_init", model=_model, has_key=bool(_api_key))


def generate(prompt: str, system: str | None = None, **kwargs) -> str:
    """Call OpenAI Chat Completions API directly."""
    if not _api_key:
        raise RuntimeError("OPENAI_API_KEY not set. Call init_llm() first.")

    headers = {
        "Authorization": f"Bearer {_api_key}",
        "Content-Type": "application/json",
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": _model,
        "messages": messages,
        **{k: v for k, v in kwargs.items() if k in ("temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty")},
    }

    with httpx.Client(timeout=_timeout_seconds) as client:
        response = client.post(
            f"{_base_url}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]


def generate_json(prompt: str, system: str | None = None, **kwargs) -> dict[str, Any]:
    """Call OpenAI and parse response as JSON."""
    text = generate(prompt, system, **kwargs)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        start = text.find("{")
        end = text.rfind("}") + 1
        if start < end:
            return json.loads(text[start:end])
        raise ValueError(f"Could not parse JSON from response: {text[:200]}")


def count_tokens(text: str) -> int:
    """Approximate token count (rough estimation: 4 chars per token)."""
    return len(text) // 4


def estimate_cost(tokens: int, model: str | None = None) -> float:
    """Estimate cost in USD based on OpenAI pricing."""
    model = model or _model
    # GPT-4o-mini: $0.15/1M input, $0.60/1M output
    if "4o-mini" in model:
        return tokens * 0.15 / 1_000_000
    # GPT-4o: $2.50/1M input, $10/1M output
    if "4o" in model and "mini" not in model:
        return tokens * 2.50 / 1_000_000
    return tokens * 0.15 / 1_000_000