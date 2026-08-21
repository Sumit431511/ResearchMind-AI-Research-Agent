from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    # Updated to the latest supported Groq model (as of 2024-08-21)
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.2-90b-text-preview")
    groq_temperature: float = _get_float("GROQ_TEMPERATURE", 0.0)
    search_results_limit: int = _get_int("SEARCH_RESULTS_LIMIT", 5)
    scrape_source_limit: int = _get_int("SCRAPE_SOURCE_LIMIT", 3)
    search_snippet_char_limit: int = _get_int("SEARCH_SNIPPET_CHAR_LIMIT", 320)
    scrape_char_limit: int = _get_int("SCRAPE_CHAR_LIMIT", 4000)
    scrape_timeout_seconds: int = _get_int("SCRAPE_TIMEOUT_SECONDS", 10)
    critic_pass_score: int = _get_int("CRITIC_PASS_SCORE", 8)
    max_revision_rounds: int = _get_int("MAX_REVISION_ROUNDS", 1)
    user_agent: str = os.getenv(
        "RESEARCHMIND_USER_AGENT",
        "ResearchMind/1.0 (+https://example.com/contact)",
    )


settings = Settings()
