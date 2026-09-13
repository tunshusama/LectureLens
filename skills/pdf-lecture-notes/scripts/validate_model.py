#!/usr/bin/env python3
"""Validate profile.json or note.json against the skill's public schemas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lecture_notes.models import ModelValidationError, load_and_validate, validate_profile_match


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("profile", "note"))
    parser.add_argument("path")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    try:
        data = load_and_validate(args.kind, args.path)
        if args.kind == "note":
            profile_path = Path(args.project_root) / data["profile"]
            if profile_path.exists() or data.get("mode") == "zero_foundation":
                validate_profile_match(data, load_and_validate("profile", profile_path))
    except ModelValidationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "kind": args.kind, "path": args.path, "schema_version": data["schema_version"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
