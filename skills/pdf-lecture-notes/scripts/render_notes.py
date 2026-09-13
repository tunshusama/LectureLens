#!/usr/bin/env python3
"""Validate and render note.json to Markdown or Lark XML."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lecture_notes.models import ModelValidationError, load_and_validate, validate_profile_match
from lecture_notes import render_lark, render_markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("note", help="Path to note.json")
    parser.add_argument("--format", choices=("markdown", "lark"), default="markdown")
    parser.add_argument("--out", required=True)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    try:
        note = load_and_validate("note", args.note)
        profile_path = Path(args.project_root) / note["profile"]
        if profile_path.exists() or note.get("mode") == "zero_foundation":
            validate_profile_match(note, load_and_validate("profile", profile_path))
        renderer = render_markdown if args.format == "markdown" else render_lark
        output = renderer.render(note, args.out, args.project_root)
    except (ModelValidationError, FileNotFoundError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "format": args.format, "out": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
