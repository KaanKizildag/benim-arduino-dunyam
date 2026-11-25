"""
Repository for recording and retrieving AI request/response logs.
"""

import json
import os
import time
import uuid
from typing import List, Optional, Dict, Any

from schemas import AILogEntry

AI_LOGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ai_logs.json"
)
AI_LOGS_MEMORY: List[AILogEntry] = []


def _load_ai_logs_from_disk() -> None:
    global AI_LOGS_MEMORY
    if AI_LOGS_MEMORY:
        return
    if os.path.isfile(AI_LOGS_FILE):
        try:
            with open(AI_LOGS_FILE, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            if isinstance(raw_list, list):
                AI_LOGS_MEMORY = [AILogEntry(**item) for item in raw_list[:100]]
        except Exception:
            AI_LOGS_MEMORY = []


def record_ai_log(
    stage: str,
    model: str,
    provider: str,
    duration_ms: int,
    status: str,
    user_goal: str,
    system_prompt: str,
    user_prompt: str,
    raw_response: str,
    processed_output: Optional[Dict[str, Any]] = None,
    notes: Optional[List[str]] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None
) -> AILogEntry:
    """Records an AI request/response pair into memory and disk."""
    _load_ai_logs_from_disk()
    tot = total_tokens
    if tot is None and (prompt_tokens is not None or completion_tokens is not None):
        tot = (prompt_tokens or 0) + (completion_tokens or 0)

    entry = AILogEntry(
        id=f"log_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}",
        timestamp=time.strftime("%d.%m.%Y %H:%M:%S"),
        stage=stage,
        model=model,
        provider=provider,
        duration_ms=duration_ms,
        status=status,
        user_goal=user_goal,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        raw_response=raw_response,
        processed_output=processed_output,
        notes=notes or [],
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=tot
    )
    AI_LOGS_MEMORY.insert(0, entry)
    del AI_LOGS_MEMORY[100:]
    try:
        with open(AI_LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in AI_LOGS_MEMORY], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[AI Log] Disk yazma hatası: {e}")
    return entry


def get_ai_logs() -> List[AILogEntry]:
    _load_ai_logs_from_disk()
    return AI_LOGS_MEMORY


def clear_ai_logs() -> bool:
    global AI_LOGS_MEMORY
    AI_LOGS_MEMORY = []
    if os.path.isfile(AI_LOGS_FILE):
        try:
            os.remove(AI_LOGS_FILE)
        except Exception:
            pass
    return True
