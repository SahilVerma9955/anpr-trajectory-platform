"""Application configuration helpers and environment loading for the platform."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


class Settings:
    """Read environment variables and YAML defaults."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or BASE_DIR
        self.env = {k: v for k, v in os.environ.items() if v is not None}
        self.system = _read_yaml(CONFIG_DIR / "system.yaml")
        self.models = _read_yaml(CONFIG_DIR / "models.yaml")
        self.cameras = _read_yaml(CONFIG_DIR / "cameras.yaml")

    @property
    def database_url(self) -> str:
        return self.env.get("DATABASE_URL", self.system.get("storage", {}).get("database_url", "sqlite:///./data/processed/anpr.db"))

    @property
    def project_name(self) -> str:
        return self.env.get("PROJECT_NAME", "anpr-trajectory-platform")

    @property
    def api_auth_enabled(self) -> bool:
        flag = self.env.get("API_AUTH_ENABLED", "false")
        return flag.lower() in {"1", "true", "yes", "on"}

    @property
    def api_key(self) -> str:
        return self.env.get("API_KEY", "")

    @property
    def free_flow_speed_kmh(self) -> float:
        value = self.env.get("FREE_FLOW_SPEED_KMH", "50")
        return float(value)


def get_settings() -> Settings:
    """Return the application settings instance."""
    return Settings()


settings = get_settings()
