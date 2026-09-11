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
    if problems:
        raise ModelValidationError("Invalid note model:\n" + "\n".join(f"- {item}" for item in problems))


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
