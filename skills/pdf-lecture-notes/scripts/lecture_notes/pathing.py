"""Safe project-relative path and asset handling."""

from __future__ import annotations

import hashlib
import re
import shutil
import unicodedata
from pathlib import Path


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_dir_for_pdf(pdf: str | Path, project_root: str | Path) -> Path:
    source = Path(pdf).resolve()
    root = Path(project_root).resolve()
    normalized = unicodedata.normalize("NFKC", source.stem)
    slug = re.sub(r"[^\w.-]+", "-", normalized, flags=re.UNICODE).strip("-._")[:48]
    slug = slug or "lecture"
    return root / ".notes_build" / f"{slug}-{file_sha256(source)[:12]}"


def project_path(value: str, project_root: str | Path) -> Path:
    root = Path(project_root).resolve()
    candidate = Path(value)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Referenced file must be inside the project root: {value}") from exc
    if not resolved.is_file():
        raise FileNotFoundError(f"Referenced file does not exist: {resolved}")
    return resolved


def project_relative(value: str, project_root: str | Path) -> str:
    root = Path(project_root).resolve()
    return project_path(value, root).relative_to(root).as_posix()


def copy_asset(value: str, project_root: str | Path, asset_dir: Path) -> str:
    source = project_path(value, project_root)
    asset_dir.mkdir(parents=True, exist_ok=True)
    destination = asset_dir / source.name
    if destination.exists() and destination.read_bytes() != source.read_bytes():
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:10]
        destination = asset_dir / f"{source.stem}-{digest}{source.suffix}"
    if not destination.exists():
        shutil.copy2(source, destination)
    return destination.name
