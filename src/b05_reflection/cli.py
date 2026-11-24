"""Scaffold diagnostics only; no research algorithm or model execution yet."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .config import RuntimeConfig


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Reflection research scaffold")
    result.add_argument("--task", default="all")
    result.add_argument("--test", action="store_true", help="Accept the official evaluation flag")
    result.add_argument("--out-dir", default=None)
    result.add_argument("--data-root", default=None, help="Local override of DATA_ROOT")
    result.add_argument("--config", default=None, help="Non-sensitive TOML config; environment and CLI values take precedence")
    result.add_argument("--log-level", type=str.upper, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default=None)
    result.add_argument("--check-only", action="store_true", help="Check JSON syntax and configuration presence")
    return result


def inspect_json(data_root: Path) -> tuple[list[dict], list[dict]]:
    if not data_root.is_dir():
        raise ValueError("Input directory does not exist or is not a directory")
    files = sorted(data_root.rglob("*.json"))
    if not files:
        raise ValueError("Input directory contains no JSON files")
    records, errors = [], []
    for path in files:
        name = path.relative_to(data_root).as_posix()
        try:
            raw = path.read_bytes()
            value = json.loads(raw.decode("utf-8-sig"))
            records.append({
                "file": name,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "json_type": type(value).__name__,
            })
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append({"file": name, "error": str(exc)})
    return records, errors


def run_check(config: RuntimeConfig, task: str) -> int:
    # Inspect before creating output directories, so missing input never appears successful.
    files, errors = inspect_json(config.data_root)
    diagnostics = config.out_dir / "diagnostics"
    diagnostics.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("b05_reflection.check")
    log.setLevel(config.log_level)
    log.propagate = False
    handler = logging.FileHandler(diagnostics / "research.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(handler)
    report = {
        "kind": "scaffold_check",
        "version": __version__,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "log_level": config.log_level,
        "status": "failed" if errors else "passed",
        "files": files,
        "errors": errors,
        "model_configuration_present": config.model.presence(),
        "model_connectivity_checked": False,
        "research_execution_implemented": False,
    }
    try:
        destination = diagnostics / "check_report.json"
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log.info("Scaffold check: valid_files=%d invalid_files=%d", len(files), len(errors))
        print(f"Scaffold check {report['status']}: {len(files)} valid, {len(errors)} invalid JSON files")
        print(f"Report: {destination}")
        print("No model request, prediction, or evaluation result was produced.")
    finally:
        log.removeHandler(handler)
        handler.close()
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    arg_parser = parser()
    args = arg_parser.parse_args(argv)
    if not args.check_only:
        arg_parser.exit(2, "Research execution is not implemented. Use --check-only for scaffold diagnostics.\n")
    try:
        config = RuntimeConfig.load(args.data_root, args.out_dir, config_path=args.config, log_level=args.log_level)
        return run_check(config, args.task)
    except (ValueError, OSError) as exc:
        arg_parser.exit(1, f"Scaffold check failed: {exc}\n")
