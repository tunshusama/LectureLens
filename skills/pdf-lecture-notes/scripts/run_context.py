#!/usr/bin/env python3
"""Resolve a source-specific build directory and decide whether its profile is reusable."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lecture_notes.models import ModelValidationError, load_and_validate
from lecture_notes.pathing import build_dir_for_pdf, file_sha256


def source_label(source: Path, project_root: Path) -> str:
    try:
        return source.relative_to(project_root).as_posix()
    except ValueError:
        return source.name


def resolve_context(pdf: str | Path, project_root: str | Path, mode: str | None = None) -> dict:
    root = Path(project_root).resolve()
    candidate = Path(pdf)
    source = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"PDF does not exist: {source}")
    digest = file_sha256(source)
    build = build_dir_for_pdf(source, root)
    profile_path = build / "profile.json"
    status = "missing"
    reason = "No course profile exists for this PDF. Create one from the current request and material."
    if profile_path.exists():
        try:
            profile = load_and_validate("profile", profile_path)
        except ModelValidationError as exc:
            status = "invalid"
            reason = str(exc)
        else:
            if profile["source_sha256"] == digest:
                status = "reusable"
                reason = "The stored course profile matches this exact PDF. Reuse it unless the user overrides it."
                if mode is not None and mode != profile.get("mode", "adaptive"):
                    status = "override_required"
                    reason = "Requested mode differs from the cached profile. Refresh the profile before writing."
            else:
                status = "stale"
                reason = "The stored course profile belongs to different PDF content. Create a new profile."
    return {
        "ok": True,
        "source_pdf": source_label(source, root),
        "source_sha256": digest,
        "build_dir": build.relative_to(root).as_posix(),
        "profile_path": profile_path.relative_to(root).as_posix(),
        "profile_status": status,
        "requested_mode": mode,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--mode", choices=("adaptive", "zero_foundation"))
    args = parser.parse_args()
    try:
        result = resolve_context(args.pdf, args.project_root, args.mode)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
