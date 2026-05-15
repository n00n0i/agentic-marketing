"""LLM client — OpenAI-compatible (Ollama Cloud / OpenAI / any compatible API)."""

from __future__ import annotations

import os
import json
from typing import Any

import httpx
import structlog


logger = structlog.get_logger(__name__)

_api_key: str | None = None
_model: str = "gemma4:31b"
_base_url: str = "https://ollama.com"  # Ollama Cloud
_timeout_seconds: int = 600


def init_llm(
    api_key: str | None = None,
    model: str = "gemma4:32b-cloud",
    base_url: str | None = None,
) -> None:
    global _api_key, _model, _base_url
    _api_key = api_key or os.environ.get("OLLAMA_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    _model = model
    if base_url:
        _base_url = base_url.rstrip("/")
    elif os.environ.get("OLLAMA_BASE_URL"):
        _base_url = os.environ["OLLAMA_BASE_URL"].rstrip("/")
    # Ollama Cloud uses Bearer token — no API key prefix needed
    logger.info("llm_init", model=_model, base_url=_base_url, has_key=bool(_api_key))


def _retry_with_backoff(fn, max_attempts=3, base_delay=5):
    """Retry a function with exponential backoff on timeout."""
    import time
    for attempt in range(max_attempts):
        try:
            return fn()
        except (httpx.ReadTimeout, httpx.ConnectError) as e:
            if attempt == max_attempts - 1:
                raise
            delay = min(base_delay * (2 ** attempt), 120)
            logger.warning(f"attempt_{attempt+1}_failed_retrying", error=str(e), delay=delay)
            time.sleep(delay)


def generate(prompt: str, system: str | None = None, stream: bool = False, **kwargs) -> str:
    """Call Ollama Cloud chat API. Handles both streaming and non-streaming."""
    api_key = _api_key or os.environ.get("OLLAMA_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
    if not api_key:
        raise RuntimeError("OLLAMA_API_KEY not set. Call init_llm() first.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    valid_params = ("temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty")
    payload = {
        "model": _model,
        "messages": messages,
        "stream": stream,
        **{k: v for k, v in kwargs.items() if k in valid_params},
    }

    def _do_streaming():
        with httpx.Client(timeout=_timeout_seconds, verify=False) as client:
            response = client.post(
                f"{_base_url}/api/chat", headers=headers, json=payload
            )
            response.raise_for_status()
            full_content = ""
            for line in response.iter_lines():
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        full_content += content
                except json.JSONDecodeError:
                    continue
            return full_content

    def _do_non_streaming():
        with httpx.Client(timeout=_timeout_seconds, verify=False) as client:
            response = client.post(
                f"{_base_url}/api/chat", headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

    if stream:
        return _retry_with_backoff(_do_streaming)
    return _retry_with_backoff(_do_non_streaming)


def generate_json(prompt: str, system: str | None = None, **kwargs) -> dict[str, Any]:
    """Call LLM and parse response as JSON."""
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
    """Estimate cost in USD (Ollama Cloud pricing varies)."""
    # Ollama Cloud gemma4:32b — roughly $0.40/1M input, $1.60/1M output
    model = model or _model
    if "gemma" in model:
        return tokens * 0.40 / 1_000_000
    return tokens * 0.15 / 1_000_000  # fallback