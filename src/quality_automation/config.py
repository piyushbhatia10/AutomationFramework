"""Configuration that keeps secrets in environment variables, not test files."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ApiConfig:
    base_url: str = ""
    timeout_seconds: float = 20.0


@dataclass(frozen=True)
class UiConfig:
    base_url: str = ""
    browser: str = "chromium"
    headless: bool = True


@dataclass(frozen=True)
class DataConfig:
    warehouse: str = ""
    database: str = ""
    schema: str = ""


@dataclass(frozen=True)
class QualityGates:
    minimum_pass_rate: float = 0.98
    maximum_failed_tests: int = 0
    minimum_coverage: float | None = None


@dataclass(frozen=True)
class FrameworkConfig:
    environment: str = "local"
    api: ApiConfig = field(default_factory=ApiConfig)
    ui: UiConfig = field(default_factory=UiConfig)
    data: DataConfig = field(default_factory=DataConfig)
    quality_gates: QualityGates = field(default_factory=QualityGates)


def _section(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"'{key}' must be a JSON object")
    return value


def load_config(path: str | Path | None = None) -> FrameworkConfig:
    """Load non-secret framework configuration from JSON.

    `QA_CONFIG_FILE` takes precedence when no path is supplied. Missing config is
    valid, which keeps focused unit tests free from environment setup.
    """
    config_path = Path(path or os.getenv("QA_CONFIG_FILE", "framework.json"))
    if not config_path.exists():
        return FrameworkConfig()
    with config_path.open(encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("Framework configuration must be a JSON object")
    return FrameworkConfig(
        environment=str(payload.get("environment", "local")),
        api=ApiConfig(**_section(payload, "api")),
        ui=UiConfig(**_section(payload, "ui")),
        data=DataConfig(**_section(payload, "data")),
        quality_gates=QualityGates(**_section(payload, "quality_gates")),
    )
