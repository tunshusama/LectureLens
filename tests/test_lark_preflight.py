from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "skills" / "pdf-lecture-notes" / "scripts" / "lark_preflight.py"


class LarkPreflightTests(unittest.TestCase):
    def test_missing_cli_returns_setup_without_creating_artifacts(self):
        with tempfile.TemporaryDirectory() as empty_path:
            environment = os.environ.copy()
            environment["PATH"] = empty_path
            result = subprocess.run(
                [sys.executable, str(PREFLIGHT)],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["state"], "missing")
            self.assertIn("ask whether", payload["next_action"])
            self.assertIn("npx @larksuite/cli@latest install", payload["setup"])
            self.assertEqual(list(Path(empty_path).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
