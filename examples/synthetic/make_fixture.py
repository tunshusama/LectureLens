#!/usr/bin/env python3
"""Generate a repository-owned PDF plus source-scoped example models."""

import json
import sys
from pathlib import Path

import fitz


REPOSITORY = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = REPOSITORY / "skills" / "pdf-lecture-notes" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

from lecture_notes.pathing import build_dir_for_pdf, file_sha256  # noqa: E402


PAGES = [
    ("How News Is Selected", ["A synthetic mini-lecture", "All text is written for this repository."]),
    ("Gatekeeping", ["Editors and routines influence which events become news.", "Selection is a process, not one person's arbitrary choice."]),
    ("News Values", ["Timeliness, relevance, conflict, and prominence are common selection signals.", "Their importance changes across outlets and audiences."]),
    ("Compare the Concepts", ["Gatekeeping describes the selection process.", "News values describe criteria that can shape that process."]),
]


def main() -> None:
    output = Path(__file__).with_name("synthetic_lecture.pdf")
    document = fitz.open()
    for title, bullets in PAGES:
        page = document.new_page(width=960, height=540)
        page.insert_text((70, 90), title, fontsize=28)
        for index, bullet in enumerate(bullets):
            page.insert_text((90, 170 + index * 70), f"• {bullet}", fontsize=17)
        page.insert_text((850, 510), str(len(document)), fontsize=12)
    document.set_metadata({
        "title": "Synthetic media studies lecture",
        "author": "LectureLens contributors",
    })
    document.save(output)
    digest = file_sha256(output)
    build = build_dir_for_pdf(output, REPOSITORY)
    build.mkdir(parents=True, exist_ok=True)
    source_pdf = output.relative_to(REPOSITORY).as_posix()
    build_relative = build.relative_to(REPOSITORY).as_posix()
    profile = {
        "schema_version": 1,
        "source_pdf": source_pdf,
        "source_sha256": digest,
        "discipline": "media studies",
        "audience_level": "beginner",
        "learning_goal": "close_reading",
        "output_language": "English",
        "assumed_knowledge": ["general secondary education"],
        "must_explain": ["gatekeeping", "news values", "the difference between a process and a criterion"],
        "depth": "detailed",
    }
    note = {
        "schema_version": 1,
        "title": "How News Is Selected — Guided Notes",
        "profile": f"{build_relative}/profile.json",
        "source_pdf": source_pdf,
        "labels": {
            "outline": "Outline", "key_point": "Key point", "term": "Term",
            "translation": "Plain-language equivalent", "explanation": "Explanation",
            "classroom_note": "Classroom note", "example": "Example",
        },
        "outline": [
            "Identify gatekeeping as a selection process.",
            "Identify news values as criteria used within that process.",
        ],
        "sections": [
            {
                "id": 1,
                "h1": "Selecting news",
                "h2": "P1–P2 Gatekeeping is a process",
                "pages": [1, 2],
                "blocks": [
                    {"type": "summary", "text": "News selection is shaped by people, routines, tools, and institutions."},
                    {"type": "slide", "page": 1, "image": f"{build_relative}/pages/p0001.png", "caption": "P1 How News Is Selected"},
                    {"type": "paragraph", "text": "The opening page frames the lecture around selection."},
                    {"type": "slide", "page": 2, "image": f"{build_relative}/pages/p0002.png", "caption": "P2 Gatekeeping"},
                    {"type": "paragraph", "text": "Gatekeeping names the wider process through which possible stories are admitted, changed, delayed, or rejected."},
                    {"type": "classroom_note", "text": "Technology and audience expectations participate alongside editors and routines.", "timestamp": "00:45"},
                ],
            },
            {
                "id": 2,
                "h1": None,
                "h2": "P3–P4 News values are criteria",
                "pages": [3, 4],
                "blocks": [
                    {"type": "summary", "text": "News values are possible criteria inside gatekeeping, not a synonym for the whole process."},
                    {"type": "slide", "page": 3, "image": f"{build_relative}/pages/p0003.png", "caption": "P3 News Values"},
                    {"type": "paragraph", "text": "Timeliness and relevance are examples of signals that may influence an outlet."},
                    {"type": "slide", "page": 4, "image": f"{build_relative}/pages/p0004.png", "caption": "P4 Compare the Concepts"},
                    {"type": "learning_note", "question": "Are gatekeeping and news values synonyms?", "answer": "No. One is the wider process; the other names criteria that may operate inside it."},
                ],
            },
        ],
    }
    (build / "profile.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    (build / "note.json").write_text(json.dumps(note, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pdf": source_pdf,
        "source_sha256": digest,
        "build_dir": build_relative,
        "profile": f"{build_relative}/profile.json",
        "note": f"{build_relative}/note.json",
    }, indent=2))


if __name__ == "__main__":
    main()
