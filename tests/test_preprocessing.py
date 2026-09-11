from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "pdf-lecture-notes" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from align_hint import align_pages  # noqa: E402
from pdf_prep import parse_pages  # noqa: E402
from run_context import resolve_context  # noqa: E402
from transcript_prep import parse_transcript, to_seconds  # noqa: E402


class PageSelectionTests(unittest.TestCase):
    def test_parses_and_deduplicates_page_ranges(self):
        self.assertEqual(parse_pages("1-3,2,7,12", 10), [1, 2, 3, 7])

    def test_empty_expression_selects_every_page(self):
        self.assertEqual(parse_pages("", 3), [1, 2, 3])

    def test_reversed_range_is_actionable_error(self):
        with self.assertRaisesRegex(ValueError, "invalid page selection"):
            parse_pages("5-2", 10)


class TranscriptTests(unittest.TestCase):
    def test_supports_multiword_and_chinese_speakers(self):
        segments, preamble = parse_transcript([
            "Lecture title",
            "Course Instructor 00:00",
            "Opening thought.",
            "王老师 1:02:03",
            "下一段。",
        ])
        self.assertEqual(preamble, ["Lecture title"])
        self.assertEqual([item["speaker"] for item in segments], ["Course Instructor", "王老师"])
        self.assertEqual(segments[1]["sec"], 3723)

    def test_rejects_invalid_seconds(self):
        with self.assertRaisesRegex(ValueError, "invalid timestamp"):
            to_seconds("02:75")

    def test_empty_transcript_is_valid(self):
        self.assertEqual(parse_transcript([]), ([], []))


class AlignmentTests(unittest.TestCase):
    def test_empty_segments_return_explicit_unmatched_pages(self):
        results = align_pages([{"page": 2, "text": "hello"}], [], total_pages=8)
        self.assertIsNone(results[0]["best_idx"])
        self.assertIsNone(results[0]["span"])

    def test_assignments_are_monotonic(self):
        pages = [
            {"page": 1, "text": "alpha introduction"},
            {"page": 2, "text": "beta method"},
            {"page": 3, "text": "gamma conclusion"},
        ]
        segments = [
            {"t": "00:00", "text": "alpha introduction"},
            {"t": "00:20", "text": "beta method"},
            {"t": "00:40", "text": "gamma conclusion"},
        ]
        results = align_pages(pages, segments, total_pages=3)
        indices = [item["best_idx"] for item in results]
        self.assertEqual(indices, sorted(indices))
        self.assertTrue(all(0 <= item["span"][0] <= item["span"][1] < 3 for item in results))

    def test_partial_page_range_keeps_global_timeline_position(self):
        pages = [{"page": 9, "text": ""}, {"page": 10, "text": ""}]
        segments = [{"t": f"00:{index:02d}", "text": ""} for index in range(10)]
        results = align_pages(pages, segments, total_pages=10, diagonal_strength=10)
        self.assertGreaterEqual(results[0]["best_idx"], 7)


class RunContextTests(unittest.TestCase):
    def test_profile_is_reused_only_for_matching_pdf_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_pdf = root / "course-a.pdf"
            second_pdf = root / "course-b.pdf"
            first_pdf.write_bytes(b"course A content")
            second_pdf.write_bytes(b"course B content")

            first = resolve_context("course-a.pdf", root)
            second = resolve_context("course-b.pdf", root)
            self.assertEqual(first["profile_status"], "missing")
            self.assertEqual(second["profile_status"], "missing")
            self.assertNotEqual(first["build_dir"], second["build_dir"])

            profile_path = root / first["profile_path"]
            profile_path.parent.mkdir(parents=True)
            profile_path.write_text(json.dumps({
                "schema_version": 1,
                "source_pdf": first["source_pdf"],
                "source_sha256": first["source_sha256"],
                "discipline": "course A",
                "audience_level": "advanced",
                "learning_goal": "review",
                "output_language": "English",
                "assumed_knowledge": ["course A foundations"],
                "must_explain": ["new material only"],
                "depth": "concise",
            }), encoding="utf-8")

            repeated = resolve_context("course-a.pdf", root)
            untouched_second = resolve_context("course-b.pdf", root)
            self.assertEqual(repeated["profile_status"], "reusable")
            self.assertEqual(untouched_second["profile_status"], "missing")


if __name__ == "__main__":
    unittest.main()
