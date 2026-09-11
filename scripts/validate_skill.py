#!/usr/bin/env python3
"""Small repository-local validation for the distributable Skill layout."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    skill = Path(sys.argv[1] if len(sys.argv) > 1 else "skills/pdf-lecture-notes")
    entry = skill / "SKILL.md"
    if not entry.is_file():
        print(f"missing {entry}", file=sys.stderr)
        return 1
    text = entry.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        print("SKILL.md is missing YAML frontmatter", file=sys.stderr)
        return 1
    frontmatter = text.split("---", 2)[1]
    name_match = re.search(r"^name:\s*([^\s]+)\s*$", frontmatter, re.MULTILINE)
    description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not name_match or not re.fullmatch(r"[a-z0-9-]{1,64}", name_match.group(1)):
        print("invalid or missing skill name", file=sys.stderr)
        return 1
    if not description_match or len(description_match.group(1).strip()) < 20:
        print("missing or unhelpful skill description", file=sys.stderr)
        return 1
    for relative in (
        "references/audience-profile.md",
        "references/content-contract.md",
        "references/dependencies.md",
        "references/output-markdown.md",
        "references/output-lark.md",
        "references/output-routing.md",
        "references/schemas/profile.schema.json",
        "references/schemas/note.schema.json",
        "scripts/render_notes.py",
        "scripts/run_context.py",
    ):
        if not (skill / relative).is_file():
            print(f"missing required skill resource: {relative}", file=sys.stderr)
            return 1
    print(f"valid skill: {name_match.group(1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
