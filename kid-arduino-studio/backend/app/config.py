"""
Uygulama genelinde merkezi konfigürasyon ve ortam değişkenleri yönetimi.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE") or os.getenv("OLLAMA_URL") or "http://127.0.0.1:11434"
DEFAULT_MODEL = os.getenv("LLM_MODEL") or "gemini/gemini-2.5-flash"
PORT = int(os.getenv("PORT") or "8001")
ARDUINO_CLI_PATH = os.getenv("ARDUINO_CLI_PATH") or "arduino-cli"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or ""

def get_api_key_for_model(model: str, explicit_key: Optional[str] = None) -> Optional[str]:
    """Model adına göre doğru sağlayıcı API anahtarını döner."""
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    model_lower = model.lower()
    if "gemini" in model_lower:
        return os.getenv("GEMINI_API_KEY") or None
    if "gpt" in model_lower or "openai" in model_lower:
        return os.getenv("OPENAI_API_KEY") or None
    if "claude" in model_lower or "anthropic" in model_lower:
        return os.getenv("ANTHROPIC_API_KEY") or None
    return None
