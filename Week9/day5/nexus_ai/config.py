"""
nexus_ai/config.py
Central configuration for NEXUS AI.
All agents read from here so one .env change propagates everywhere.
"""

import os
from dotenv import load_dotenv

load_dotenv()

NEXUS_CONFIG = {
    # LLM backend
    "model":    os.getenv("MODEL_NAME", "phi3"),
    "base_url": os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
    "api_key":  os.getenv("OPENAI_API_KEY", "ollama"),

    # Agent defaults
    "max_tokens":   int(os.getenv("MAX_TOKENS", "768")),
    "temperature":  float(os.getenv("TEMPERATURE", "0.4")),

    # Paths
    "logs_dir":    os.getenv("LOGS_DIR", "logs"),
    "memory_dir":  os.getenv("MEMORY_DIR", "data/memory"),
    "files_dir":   os.getenv("FILES_DIR", "data/files"),
    "db_path":     os.getenv("SQLITE_DB_PATH", "data/sales.db"),

    # Pipeline
    "max_retries": int(os.getenv("MAX_RETRIES", "1")),
    "parallel_workers": True,
}


def get_llm_config(temperature: float = None, max_tokens: int = None) -> dict:
    """Returns standard AutoGen llm_config dict."""
    return {
        "config_list": [{
            "model":    NEXUS_CONFIG["model"],
            "base_url": NEXUS_CONFIG["base_url"],
            "api_key":  NEXUS_CONFIG["api_key"],
        }],
        "temperature": temperature if temperature is not None else NEXUS_CONFIG["temperature"],
        "max_tokens":  max_tokens  if max_tokens  is not None else NEXUS_CONFIG["max_tokens"],
    }