from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "pdf-lecture-notes"


class SkillContractTests(unittest.TestCase):
    def test_repository_local_skill_validation(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_skill.py"), str(SKILL)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_skill_separates_subject_profile_from_output_contracts(self):
        entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        audience = (SKILL / "references" / "audience-profile.md").read_text(encoding="utf-8")
        self.assertIn("audience-profile.md", entry)
        self.assertIn("output-markdown.md", entry)
        self.assertIn("output-routing.md", entry)
        self.assertIn("Lark/Feishu is preferred", entry)
        self.assertIn("Journalism", audience)
        self.assertIn("Literature", audience)
        self.assertNotIn("zero math / zero code", entry.lower())

    def test_main_skill_makes_profile_questioning_scope_explicit(self):
        entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        audience = (SKILL / "references" / "audience-profile.md").read_text(encoding="utf-8")
        self.assertIn("Do not ask about the user's background on every run", entry)
        self.assertIn("do not treat the first answer as a global user profile", entry)
        self.assertIn("ask once about the user's familiarity with this course", entry)
        self.assertIn("never infer personal familiarity from the material itself", entry)
        self.assertIn("Do not substitute the safe default merely to avoid this question", audience)
        self.assertIn("when the user declines to specify familiarity", audience)

    def test_output_routing_asks_before_lark_install_and_falls_back_after_decline(self):
        entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        routing = (SKILL / "references" / "output-routing.md").read_text(encoding="utf-8")
        self.assertNotIn("Do not publish externally unless the user requested that destination", entry)
        self.assertIn("Before generating notes", entry)
        self.assertIn("proactively offer it", entry)
        self.assertIn("do not interpret silence as a preference for local or Markdown output", routing)
        self.assertIn("ask whether the user wants the notes published to Lark/Feishu", routing)
        self.assertIn("ask whether the user wants to install", routing)
        self.assertIn("declines Lark/Feishu, installation, or configuration", routing)
        self.assertIn("offer Markdown first", routing)


if __name__ == "__main__":
    unittest.main()
