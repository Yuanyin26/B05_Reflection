"""Environment-only configuration; never include credential values in reports."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


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

    @classmethod
    def load(
        cls,
        data_root: str | None,
        out_dir: str | None,
        env: Mapping[str, str] | None = None,
    ) -> RuntimeConfig:
        source = os.environ if env is None else env
        inputs = Path(data_root or source.get("DATA_ROOT", "/input")).resolve()
        outputs = Path(out_dir or source.get("OUTPUT_DIR", "/output")).resolve()
        if outputs.is_relative_to(inputs):
            raise ValueError("Output directory must be outside the input directory")
        return cls(inputs, outputs, ModelConfig.from_env(source))
