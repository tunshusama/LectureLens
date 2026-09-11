from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "pdf-lecture-notes" / "scripts"


class EndToEndTests(unittest.TestCase):
    def test_synthetic_pdf_to_markdown_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            pdf = project / "lecture.pdf"
            document = fitz.open()
            for title in ("Gatekeeping", "News values"):
                page = document.new_page()
                page.insert_text((72, 72), title, fontsize=24)
                page.insert_text((72, 120), "Repository-owned synthetic teaching text.", fontsize=12)
            document.save(pdf)
            build = project / ".notes_build"

            prepared = subprocess.run([
                sys.executable, str(SCRIPTS / "pdf_prep.py"), str(pdf),
                "--out", str(build), "--project-root", str(project),
            ], capture_output=True, text=True, check=False)
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            pages_data = json.loads((build / "pages.json").read_text(encoding="utf-8"))
            self.assertRegex(pages_data["source_sha256"], r"^[a-f0-9]{64}$")
            pages = pages_data["pages"]
            note = {
                "schema_version": 1,
                "title": "Synthetic notes",
                "profile": ".notes_build/profile.json",
                "source_pdf": "lecture.pdf",
                "labels": {
                    "outline": "Outline", "key_point": "Key point", "term": "Term",
                    "translation": "Plain language", "explanation": "Explanation",
                    "classroom_note": "Classroom note", "example": "Example",
                },
                "sections": [{
                    "id": 1, "h1": "News selection", "h2": "P1–P2 Two related concepts",
                    "pages": [1, 2],
                    "blocks": [
                        {"type": "summary", "text": "The process and its criteria are related but distinct."},
                        *[
                            {"type": "slide", "page": page["page"], "image": page["image"], "caption": page["title"]}
                            for page in pages
                        ],
                    ],
                }],
            }
            note_path = build / "note.json"
            note_path.write_text(json.dumps(note), encoding="utf-8")
            rendered = subprocess.run([
                sys.executable, str(SCRIPTS / "render_notes.py"), str(note_path),
                "--format", "markdown", "--out", str(project / "output" / "notes.md"),
                "--project-root", str(project),
            ], capture_output=True, text=True, check=False)
            self.assertEqual(rendered.returncode, 0, rendered.stdout + rendered.stderr)
            self.assertTrue((project / "output" / "notes.md").is_file())
            self.assertEqual(len(list((project / "output" / "assets").glob("*.png"))), 2)


if __name__ == "__main__":
    unittest.main()
