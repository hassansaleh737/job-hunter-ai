"""Environment configuration for Job Hunter AI.

For local development, values from the project's ignored .env file take
precedence over stale values inherited by the PowerShell/Streamlit process.
No secrets are printed or logged.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.is_file():
    load_dotenv(dotenv_path=ENV_FILE, override=True)

GREENHOUSE_BOARDS = {
    "constructortech": "Constructor TECH",
    "ritual": "Ritual",
    "solutions": "Cadence Solutions",
    "orbisoperations": "Orbis",
}


@dataclass(frozen=True)
class Settings:
    token: str
    model: str
    provider: str


def settings() -> Settings:
    return Settings(
        token=os.getenv("HF_TOKEN", "").strip(),
        model=os.getenv("HF_MODEL", "Qwen/Qwen3.5-9B").strip(),
        provider=os.getenv("HF_PROVIDER", "deepinfra").strip(),
    )
