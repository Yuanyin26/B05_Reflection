"""Cross-platform checks for the public CLI contract; no model calls."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "src" / "main.py"


class ScaffoldChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="b05-ci-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.inputs = self.root / "input"
        self.inputs.mkdir()
        self.sample = self.inputs / "sample.json"
        self.sample.write_text('{"text":"A generic research note."}\n', encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("LLM_")}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def invoke(self, arguments, extra_env=None):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(ENTRY), *arguments],
            cwd=self.root,
            env=self.env | (extra_env or {}),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )

    def check_args(self, output):
        return ["--check-only", "--data-root", str(self.inputs), "--out-dir", str(output)]

    def test_self_check_preserves_input_and_redacts_model_values(self):
        output = self.root / "output"
        original = hashlib.sha256(self.sample.read_bytes()).hexdigest()
        model = {
            "LLM_BASE_URL": "https://example.invalid/sentinel-endpoint",
            "LLM_API_KEY": "sentinel-not-a-real-credential",
            "LLM_MODEL": "sentinel-model",
            "LLM_USE_JSON_SCHEMA": "1",
            "LLM_ENABLE_THINKING": "0",
        }
        result = self.invoke(["--task", "all", "--test", *self.check_args(output)], model)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((output / "diagnostics/check_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["files"][0]["sha256"], original)
        self.assertEqual(hashlib.sha256(self.sample.read_bytes()).hexdigest(), original)
        self.assertTrue(all(report["model_configuration_present"].values()))
        self.assertFalse(report["model_connectivity_checked"])
        self.assertFalse(report["research_execution_implemented"])
        written = result.stdout + result.stderr
        written += "".join(p.read_text(encoding="utf-8") for p in output.rglob("*") if p.is_file())
        for secret in ("sentinel-endpoint", "sentinel-not-a-real-credential", "sentinel-model"):
            self.assertNotIn(secret, written)
        self.assertFalse((output / "rethink").exists())
        self.assertFalse((output / "norethink").exists())

    def test_bad_json_produces_failed_diagnostics(self):
        self.sample.write_text("{broken", encoding="utf-8")
        output = self.root / "bad-output"
        result = self.invoke(self.check_args(output))
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads((output / "diagnostics/check_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "failed")
        self.assertEqual(len(report["errors"]), 1)

    def test_unimplemented_execution_fails_without_creating_answers(self):
        output = self.root / "not-implemented"
        result = self.invoke(["--task", "all", "--test", "--out-dir", str(output)])
        self.assertEqual(result.returncode, 2)
        self.assertFalse(output.exists())

    def test_invalid_setup_fails_before_output_is_written(self):
        empty = self.root / "empty"
        empty.mkdir()
        cases = [
            ("missing", self.root / "missing", self.root / "missing-output", {}),
            ("empty", empty, self.root / "empty-output", {}),
            ("nested-output", self.inputs, self.inputs / "output", {}),
            ("bad-flag", self.inputs, self.root / "bad-flag-output", {"LLM_USE_JSON_SCHEMA": "invalid"}),
        ]
        for name, data, output, env in cases:
            with self.subTest(name=name):
                result = self.invoke(["--check-only", "--data-root", str(data), "--out-dir", str(output)], env)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
