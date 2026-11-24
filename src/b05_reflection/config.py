"""Non-sensitive TOML settings plus environment-only model configuration."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


def runtime_file(path: str | None) -> tuple[dict[str, str], Path | None]:
    if path is None:
        return {}, None
    source = Path(path).resolve()
    with source.open("rb") as handle:
        document = tomllib.load(handle)
    if set(document) - {"runtime"}:
        raise ValueError("Only a [runtime] table is supported; model settings must use LLM_* environment variables")
    settings = document.get("runtime", {})
    allowed = {"data_root", "out_dir", "log_level"}
    if not isinstance(settings, dict) or set(settings) - allowed:
        raise ValueError("Runtime configuration supports only data_root, out_dir and log_level")
    if any(not isinstance(value, str) or not value.strip() for value in settings.values()):
        raise ValueError("Runtime configuration values must be non-empty strings")
    return settings, source.parent


def runtime_path(
    explicit: str | None,
    environment: str | None,
    configured: str | None,
    directory: Path | None,
    default: str,
) -> Path:
    if explicit:
        return Path(explicit).resolve()
    if environment and environment.strip():
        return Path(environment).resolve()
    if configured is not None:
        path = Path(configured)
        if not path.is_absolute() and directory is not None:
            path = directory / path
        return path.resolve()
    return Path(default).resolve()


def optional_flag(env: Mapping[str, str], name: str) -> bool | None:
    value = env.get(name, "").strip()
    if not value:
        return None
    if value not in {"0", "1"}:
        raise ValueError(f"{name} must be 0 or 1")
    return value == "1"


@dataclass(frozen=True)
class ModelConfig:
    base_url: str = field(repr=False)
    api_key: str = field(repr=False)
    model: str = field(repr=False)
    use_json_schema: bool | None = None
    enable_thinking: bool | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> ModelConfig:
        return cls(
            base_url=env.get("LLM_BASE_URL", "").strip(),
            api_key=env.get("LLM_API_KEY", ""),
            model=env.get("LLM_MODEL", "").strip(),
            use_json_schema=optional_flag(env, "LLM_USE_JSON_SCHEMA"),
            enable_thinking=optional_flag(env, "LLM_ENABLE_THINKING"),
        )

    def presence(self) -> dict[str, bool]:
        return {
            "LLM_BASE_URL": bool(self.base_url),
            "LLM_API_KEY": bool(self.api_key.strip()),
            "LLM_MODEL": bool(self.model),
        }


@dataclass(frozen=True)
class RuntimeConfig:
    data_root: Path
    out_dir: Path
    model: ModelConfig
    log_level: str = "INFO"

    @classmethod
    def load(
        cls,
        data_root: str | None,
        out_dir: str | None,
        env: Mapping[str, str] | None = None,
        config_path: str | None = None,
        log_level: str | None = None,
    ) -> RuntimeConfig:
        source = os.environ if env is None else env
        settings, directory = runtime_file(config_path)
        inputs = runtime_path(data_root, source.get("DATA_ROOT"), settings.get("data_root"), directory, "/input")
        outputs = runtime_path(out_dir, source.get("OUTPUT_DIR"), settings.get("out_dir"), directory, "/output")
        level = (log_level or source.get("B05_LOG_LEVEL", "").strip() or settings.get("log_level", "INFO")).strip().upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("Log level must be DEBUG, INFO, WARNING, ERROR or CRITICAL")
        if outputs.is_relative_to(inputs):
            raise ValueError("Output directory must be outside the input directory")
        return cls(inputs, outputs, ModelConfig.from_env(source), level)
