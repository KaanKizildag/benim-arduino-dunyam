"""
Unified LLM client wrapping LiteLLM and Ollama with centralized key resolution,
token tracking, max_token caps, and uniform error handling.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Iterator
import httpx
from litellm import completion

from app.config import get_api_key_for_model, OLLAMA_BASE_URL

logger = logging.getLogger("kid-arduino-studio.llm")


def is_ollama_model(model: str) -> bool:
    return model.startswith("ollama/") or model.startswith("ollama_chat/")


def estimate_tokens(text: str) -> int:
    """Fallback token estimation when provider doesn't report usage."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def call_llm(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 2500,
    response_format: Optional[Dict[str, str]] = None,
    api_key: Optional[str] = None,
    timeout: float = 60.0
) -> Tuple[str, int, int, int]:
    """
    Synchronous LLM call.
    Returns: (content, prompt_tokens, completion_tokens, total_tokens)
    """
    if is_ollama_model(model):
        clean_model = model.replace("ollama/", "").replace("ollama_chat/", "")
        is_reasoning = any(k in clean_model.lower() for k in ("deepseek-r1", "qwq", "r1"))
        
        # Merge system and user messages into prompt if Ollama generate endpoint
        system_text = ""
        prompt_text = ""
        for m in messages:
            if m.get("role") == "system":
                system_text += m.get("content", "") + "\n"
            else:
                prompt_text += m.get("content", "") + "\n"
                
        payload: Dict[str, Any] = {
            "model": clean_model,
            "system": system_text.strip(),
            "prompt": prompt_text.strip(),
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        if response_format and response_format.get("type") == "json_object" and not is_reasoning:
            payload["format"] = "json"

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama HTTP {resp.status_code}: {resp.text}")
            data = resp.json()
            content = data.get("response", "")
            prompt_toks = data.get("prompt_eval_count") or estimate_tokens(system_text + prompt_text)
            comp_toks = data.get("eval_count") or estimate_tokens(content)
            return content, prompt_toks, comp_toks, prompt_toks + comp_toks

    # LiteLLM Cloud Provider
    resolved_key = api_key or get_api_key_for_model(model)
    if not resolved_key:
        raise RuntimeError(f"Seçilen model ('{model}') için API anahtarı bulunamadı. Lütfen .env dosyasını kontrol edin.")

    call_kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "api_key": resolved_key,
        "timeout": timeout,
    }
    if response_format:
        call_kwargs["response_format"] = response_format

    resp = completion(**call_kwargs)
    content = resp.choices[0].message.content or ""
    
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    if hasattr(resp, "usage") and resp.usage:
        prompt_tokens = getattr(resp.usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(resp.usage, "completion_tokens", 0) or 0
        total_tokens = getattr(resp.usage, "total_tokens", 0) or (prompt_tokens + completion_tokens)
    else:
        prompt_tokens = estimate_tokens(str(messages))
        completion_tokens = estimate_tokens(content)
        total_tokens = prompt_tokens + completion_tokens

    return content, prompt_tokens, completion_tokens, total_tokens


def stream_llm(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 2500,
    api_key: Optional[str] = None,
    timeout: float = 120.0
) -> Iterator[str]:
    """
    Streaming LLM call yielding string deltas.
    """
    if is_ollama_model(model):
        clean_model = model.replace("ollama/", "").replace("ollama_chat/", "")
        is_reasoning = any(k in clean_model.lower() for k in ("deepseek-r1", "qwq", "r1"))
        
        system_text = ""
        prompt_text = ""
        for m in messages:
            if m.get("role") == "system":
                system_text += m.get("content", "") + "\n"
            else:
                prompt_text += m.get("content", "") + "\n"
                
        payload: Dict[str, Any] = {
            "model": clean_model,
            "system": system_text.strip(),
            "prompt": prompt_text.strip(),
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        if not is_reasoning:
            payload["format"] = "json"

        with httpx.Client(timeout=timeout) as client:
            with client.stream("POST", f"{OLLAMA_BASE_URL}/api/generate", json=payload) as response:
                if response.status_code != 200:
                    raise RuntimeError(f"Ollama HTTP {response.status_code}")
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        chunk = item.get("response", "")
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue
        return

    # LiteLLM Cloud Provider
    resolved_key = api_key or get_api_key_for_model(model)
    if not resolved_key:
        raise RuntimeError(f"Seçilen model ('{model}') için API anahtarı bulunamadı. Lütfen .env dosyasını kontrol edin.")

    stream_resp = completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=resolved_key,
        stream=True,
        timeout=timeout,
    )
    for chunk_obj in stream_resp:
        if chunk_obj.choices and chunk_obj.choices[0].delta:
            delta = chunk_obj.choices[0].delta.content or ""
            if delta:
                yield delta
