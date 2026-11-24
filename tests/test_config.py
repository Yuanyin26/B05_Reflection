"""Configuration precedence and boundaries, using temporary non-sensitive files."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from b05_reflection.config import RuntimeConfig


class ConfigurationChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="b05-config-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = self.root / "configs" / "example.toml"
        self.config.parent.mkdir()
        self.config.write_text(
            '[runtime]\ndata_root="../inputs"\nout_dir="../outputs"\nlog_level="DEBUG"\n',
            encoding="utf-8",
        )

    def load(self, **kwargs):
        options = {"data_root": None, "out_dir": None, "env": {}, "config_path": str(self.config)}
        return RuntimeConfig.load(**(options | kwargs))

    def test_relative_paths_resolve_from_configuration_directory(self):
        result = self.load()
        self.assertEqual(result.data_root, (self.root / "inputs").resolve())
        self.assertEqual(result.out_dir, (self.root / "outputs").resolve())
        self.assertEqual(result.log_level, "DEBUG")
        self.assertFalse(any(result.model.presence().values()))

    def test_environment_overrides_file_and_cli_overrides_environment(self):
        environment = {
            "DATA_ROOT": str(self.root / "env-input"),
            "OUTPUT_DIR": str(self.root / "env-output"),
            "B05_LOG_LEVEL": "WARNING",
        }
        result = self.load(env=environment)
        self.assertEqual(result.data_root, (self.root / "env-input").resolve())
        self.assertEqual(result.out_dir, (self.root / "env-output").resolve())
        self.assertEqual(result.log_level, "WARNING")
        result = self.load(env=environment, data_root=str(self.root / "cli-input"), out_dir=str(self.root / "cli-output"), log_level="ERROR")
        self.assertEqual(result.data_root, (self.root / "cli-input").resolve())
        self.assertEqual(result.out_dir, (self.root / "cli-output").resolve())
        self.assertEqual(result.log_level, "ERROR")

    def test_empty_environment_uses_file_settings(self):
        result = self.load(env={"DATA_ROOT": "", "OUTPUT_DIR": "", "B05_LOG_LEVEL": ""})
        self.assertEqual(result.data_root, (self.root / "inputs").resolve())
        self.assertEqual(result.log_level, "DEBUG")

    def test_invalid_or_sensitive_configuration_is_rejected(self):
        cases = [
            '[model]\napi_key="not-a-real-key"\n',
            '[runtime]\napi_key="not-a-real-key"\n',
            '[runtime]\ndata_root=12\n',
            '[runtime]\nout_dir=""\n',
            '[runtime]\nlog_level="unknown"\n',
            '[runtime\n',
        ]
        for content in cases:
            with self.subTest(content=content):
                self.config.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.load()

    def test_file_configuration_cannot_write_under_input_directory(self):
        self.config.write_text('[runtime]\ndata_root="../inputs"\nout_dir="../inputs/output"\n', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.load()


if __name__ == "__main__":
    unittest.main()
