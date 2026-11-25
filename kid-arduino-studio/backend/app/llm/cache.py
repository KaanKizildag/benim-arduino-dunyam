"""
In-memory and file-based response caching for project generations.
Identical requests (same prompt, inventory, model) are returned instantly with 0 tokens.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, List

# In-memory cache: key -> {"timestamp": float, "data": dict}
_MEMORY_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600 * 4  # 4 hours


def make_cache_key(prompt: str, inventory: Optional[List[str]] = None, model: str = "") -> str:
    norm_prompt = " ".join(prompt.strip().lower().split())
    norm_inv = sorted([i.strip().lower() for i in (inventory or [])])
    raw = f"{model.strip().lower()}::{norm_prompt}::{','.join(norm_inv)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_cached_project(prompt: str, inventory: Optional[List[str]] = None, model: str = "") -> Optional[Dict[str, Any]]:
    key = make_cache_key(prompt, inventory, model)
    entry = _MEMORY_CACHE.get(key)
    if not entry:
        return None
    if time.time() - entry["timestamp"] > CACHE_TTL_SECONDS:
        del _MEMORY_CACHE[key]
        return None
    return entry["data"]


def set_cached_project(prompt: str, inventory: Optional[List[str]] = None, model: str = "", data: Optional[Dict[str, Any]] = None) -> None:
    if not data:
        return
    key = make_cache_key(prompt, inventory, model)
    _MEMORY_CACHE[key] = {
        "timestamp": time.time(),
        "data": data,
    }


def clear_cache() -> None:
    _MEMORY_CACHE.clear()
