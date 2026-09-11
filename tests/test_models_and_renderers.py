from __future__ import annotations

import base64
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "pdf-lecture-notes" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lecture_notes.models import ModelValidationError, validate_data  # noqa: E402
from lecture_notes import render_lark, render_markdown  # noqa: E402


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def profile():
    return {
        "schema_version": 1,
        "source_pdf": "lecture.pdf",
        "source_sha256": "0" * 64,
        "discipline": "literature",
        "audience_level": "beginner",
        "learning_goal": "close_reading",
        "output_language": "中文",
        "assumed_knowledge": ["普通教育常识"],
        "must_explain": ["历史语境"],
        "depth": "detailed",
    }


def note(image_path: str):
    return {
        "schema_version": 1,
        "title": "合成课件笔记",
        "profile": "profile.json",
        "source_pdf": "lecture.pdf",
        "labels": {
            "outline": "主线",
            "key_point": "要点",
            "term": "术语",
            "translation": "中文",
            "explanation": "解释",
            "classroom_note": "课堂补充",
            "example": "例子",
        },
        "outline": ["先读文本", "再看语境"],
        "sections": [{
            "id": "s1",
            "h1": "文本与语境",
            "h2": "P1 一个自制例子",
            "pages": [1],
            "blocks": [
                {"type": "summary", "text": "文本证据与语境需要分开辨认。"},
                {"type": "slide", "page": 1, "image": image_path, "caption": "P1 合成页"},
                {"type": "paragraph", "text": "这一页只包含仓库自制内容。"},
                {"type": "formula", "latex": "x < y", "symbols": [{"symbol": "x", "meaning": "第一个量", "example": "x=1"}]},
                {"type": "terms", "items": [{"term": "Context", "translation": "语境", "explanation": "文本产生和被阅读的条件"}]},
                {"type": "classroom_note", "text": "这是经过支持的课堂补充。", "timestamp": "01:20"},
                {"type": "learning_note", "question": "语境等于作者生平吗？", "answer": "不等于，作者生平只是可能相关的一部分。"},
            ],
        }],
    }


class ModelTests(unittest.TestCase):
    def test_profile_schema_accepts_subject_specific_profile(self):
        validate_data("profile", profile())

    def test_note_schema_rejects_unknown_block(self):
        data = note("page.png")
        data["sections"][0]["blocks"] = [{"type": "unknown", "text": "x"}]
        with self.assertRaises(ModelValidationError):
            validate_data("note", data)

    def test_note_requires_one_slide_per_declared_page(self):
        data = note("page.png")
        data["sections"][0]["pages"] = [1, 2]
        with self.assertRaisesRegex(ModelValidationError, "must exactly match"):
            validate_data("note", data)

    def test_note_requires_first_theme_heading(self):
        data = note("page.png")
        data["sections"][0]["h1"] = None
        with self.assertRaisesRegex(ModelValidationError, "first section"):
            validate_data("note", data)


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "input").mkdir()
        (self.root / "input" / "page.png").write_bytes(PNG_1X1)
        self.data = note("input/page.png")
        validate_data("note", self.data)

    def tearDown(self):
        self.temp.cleanup()

    def test_markdown_copies_assets_and_uses_localized_labels(self):
        output = render_markdown.render(self.data, self.root / "output" / "notes.md", self.root)
        text = output.read_text(encoding="utf-8")
        self.assertIn("**要点:**", text)
        self.assertIn("| 术语 | 中文 | 解释 |", text)
        self.assertIn("assets/page.png", text)
        self.assertTrue((output.parent / "assets" / "page.png").is_file())

    def test_lark_xml_is_well_formed_and_uses_project_relative_images(self):
        output = render_lark.render(self.data, self.root / "output" / "note.xml", self.root)
        text = output.read_text(encoding="utf-8")
        ET.fromstring("<root>" + text + "</root>")
        self.assertIn('path="@./input/page.png"', text)
        self.assertIn("课堂补充", text)

    def test_rejects_images_outside_project_root(self):
        outside = tempfile.NamedTemporaryFile(suffix=".png")
        self.addCleanup(outside.close)
        outside.write(PNG_1X1)
        outside.flush()
        data = note(outside.name)
        with self.assertRaisesRegex(ValueError, "inside the project root"):
            render_markdown.render(data, self.root / "notes.md", self.root)


if __name__ == "__main__":
    unittest.main()
