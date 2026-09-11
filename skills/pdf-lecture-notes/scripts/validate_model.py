#!/usr/bin/env python3
"""Validate profile.json or note.json against the skill's public schemas."""

from __future__ import annotations

import argparse
import json
import sys

from lecture_notes.models import ModelValidationError, load_and_validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("profile", "note"))
    parser.add_argument("path")
    args = parser.parse_args()
    try:
        data = load_and_validate(args.kind, args.path)
    except ModelValidationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "kind": args.kind, "path": args.path, "schema_version": data["schema_version"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
