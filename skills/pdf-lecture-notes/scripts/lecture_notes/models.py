"""Load and validate the public JSON boundary models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - actionable dependency failure
    raise SystemExit(
        "Missing jsonschema. Install project dependencies with: "
        "python3 -m pip install -r <installed-skill>/requirements.txt"
    ) from exc


SCHEMA_DIR = Path(__file__).resolve().parents[2] / "references" / "schemas"
SCHEMAS = {
    "profile": SCHEMA_DIR / "profile.schema.json",
    "note": SCHEMA_DIR / "note.schema.json",
}


class ModelValidationError(ValueError):
    """Raised when a profile or note does not satisfy its public schema."""


def _format_path(parts: list[object]) -> str:
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


def validate_data(kind: str, data: Any) -> None:
    if kind not in SCHEMAS:
        raise ValueError(f"Unknown model kind {kind!r}; choose one of: {', '.join(SCHEMAS)}")
    with SCHEMAS[kind].open(encoding="utf-8") as handle:
        schema = json.load(handle)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        details = [f"{_format_path(list(error.absolute_path))}: {error.message}" for error in errors]
        raise ModelValidationError(f"Invalid {kind} model:\n" + "\n".join(f"- {item}" for item in details))
    if kind == "note":
        _validate_note_semantics(data)


def _validate_note_semantics(data: dict[str, Any]) -> None:
    problems = []
    sections = data["sections"]
    if not sections[0].get("h1"):
        problems.append("$.sections[0].h1: the first section must start a top-level theme")
    translations: dict[str, str] = {}
    all_pages = [page for section in sections for page in section["pages"]]
    if all_pages != sorted(set(all_pages)):
        problems.append("$.sections: pages must be unique and increasing across sections")
    for item in data.get("self_check", {}).get("items", []):
        if not set(item["pages"]).issubset(all_pages):
            problems.append("$.self_check: references pages outside this note")
    for section_index, section in enumerate(sections):
        pages = section["pages"]
        if pages != sorted(set(pages)):
            problems.append(f"$.sections[{section_index}].pages: pages must be unique and increasing")
        slide_pages = [
            block["page"] for block in section["blocks"] if block["type"] == "slide"
        ]
        if slide_pages != pages:
            problems.append(
                f"$.sections[{section_index}].blocks: slide pages {slide_pages} must exactly match {pages}"
            )
        for block_index, block in enumerate(section["blocks"]):
            if block["type"] != "terms":
                continue
            for item in block["items"]:
                key = item["term"].casefold()
                previous = translations.get(key)
                if previous is not None and previous != item["translation"]:
                    problems.append(
                        f"$.sections[{section_index}].blocks[{block_index}]: "
                        f"term {item['term']!r} has inconsistent translations"
                    )
                translations[key] = item["translation"]
    if data.get("mode") == "zero_foundation":
        if not data.get("reading_guide", "").strip() or not data.get("outline"):
            problems.append("zero_foundation requires a reading guide and outline")
        if not data.get("self_check"):
            problems.append("zero_foundation requires a self_check with answers and source pages")
        if translations and not data.get("glossary_title"):
            problems.append("zero_foundation requires glossary_title when terms are introduced")
        for index, section in enumerate(sections):
            blocks = section["blocks"]
            if section.get("kind", "content") == "content":
                if blocks[0]["type"] != "summary" or not any(b["type"] == "learning_note" for b in blocks):
                    problems.append(f"$.sections[{index}]: content requires an opening summary and learning_note")
            for j, block in enumerate(blocks):
                path = f"$.sections[{index}].blocks[{j}]"
                if block["type"] == "slide":
                    if j + 1 == len(blocks) or blocks[j + 1]["type"] != "paragraph":
                        problems.append(f"{path}: each slide needs an immediate explanation")
                if block["type"] == "formula":
                    if not block["symbols"] or any(not s.get("reading", "").strip() for s in block["symbols"]):
                        problems.append(f"{path}: formula symbols require readings and meanings")
                    if not block.get("worked_example", "").strip():
                        problems.append(f"{path}: formula requires a worked_example")
    if problems:
        raise ModelValidationError("Invalid note model:\n" + "\n".join(f"- {item}" for item in problems))


def validate_profile_match(note: dict, profile: dict) -> None:
    """Prevent a requested teaching mode from silently disappearing during drafting."""
    if note.get("mode", "adaptive") != profile.get("mode", "adaptive"):
        raise ModelValidationError("Note mode must match the source profile mode")
    if note["source_pdf"] != profile["source_pdf"]:
        raise ModelValidationError("Note source_pdf must match the source profile")


def load_and_validate(kind: str, path: str | Path) -> dict[str, Any]:
    model_path = Path(path)
    try:
        with model_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ModelValidationError(f"Model file does not exist: {model_path}") from exc
    except json.JSONDecodeError as exc:
        raise ModelValidationError(
            f"Invalid JSON in {model_path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    validate_data(kind, data)
    return data
