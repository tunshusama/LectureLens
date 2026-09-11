#!/usr/bin/env python3
"""Render lecture PDF pages and extract their text into a portable build directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from lecture_notes.pathing import file_sha256

try:
    import fitz
except ImportError as exc:  # pragma: no cover - dependency failure
    raise SystemExit(
        "Missing PyMuPDF. Install project dependencies with: "
        "python3 -m pip install -r <installed-skill>/requirements.txt\n"
        "PyMuPDF uses AGPL-3.0 or a commercial license; review THIRD_PARTY_NOTICES.md."
    ) from exc


def parse_pages(expression: str, total: int) -> list[int]:
    """Parse a 1-based expression such as '1-8,20,22-24'."""
    if not expression:
        return list(range(1, total + 1))
    selected: set[int] = set()
    for raw_part in expression.split(","):
        part = raw_part.strip()
        if not part:
            continue
        try:
            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start, end = int(start_text), int(end_text)
                if start > end:
                    raise ValueError(f"page range starts after it ends: {part}")
                selected.update(range(start, end + 1))
            else:
                selected.add(int(part))
        except ValueError as exc:
            raise ValueError(f"invalid page selection {part!r}") from exc
    return [page for page in sorted(selected) if 1 <= page <= total]


def page_title(page) -> str:
    """Use the largest non-page-number line as a best-effort title."""
    try:
        blocks = page.get_text("dict")["blocks"]
    except Exception:
        return ""
    best_size, best_text = 0.0, ""
    for block in blocks:
        for line in block.get("lines", []):
            text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
            if not text or re.fullmatch(r"[\d\s./|-]+", text):
                continue
            size = max((span.get("size", 0) for span in line.get("spans", [])), default=0)
            if size > best_size:
                best_size, best_text = size, text
    return best_text[:120]


def _within_root(path: Path, project_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(project_root).as_posix()
    except ValueError as exc:
        raise ValueError(f"build output must be inside project root: {resolved}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("--out", required=True, help="Build directory")
    parser.add_argument("--pages", default="", help="Subset such as 1-8,20")
    parser.add_argument("--scale", type=float, default=2.0)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    pdf_path = Path(args.pdf).resolve()
    output = Path(args.out).resolve()
    image_dir = output / "pages"
    image_dir.mkdir(parents=True, exist_ok=True)

    try:
        document = fitz.open(pdf_path)
        selected = parse_pages(args.pages, document.page_count)
        if not selected:
            raise ValueError("page selection does not contain any page in this PDF")
        matrix = fitz.Matrix(args.scale, args.scale)
        records = []
        for page_number in selected:
            page = document[page_number - 1]
            image_path = image_dir / f"p{page_number:04d}.png"
            page.get_pixmap(matrix=matrix, alpha=False).save(image_path)
            text = page.get_text().strip()
            records.append({
                "page": page_number,
                "title": page_title(page),
                "text": text,
                "image": _within_root(image_path, project_root),
                "n_images": len(page.get_images()),
                "char_count": len(text),
            })
    except (ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    source = pdf_path.name
    try:
        source = pdf_path.relative_to(project_root).as_posix()
    except ValueError:
        pass
    output.mkdir(parents=True, exist_ok=True)
    (output / "pages.json").write_text(json.dumps({
        "source": source,
        "source_sha256": file_sha256(pdf_path),
        "total_pages": document.page_count,
        "selected_pages": selected,
        "scale": args.scale,
        "pages": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "pages.txt").open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write("=" * 70 + "\n")
            handle.write(
                f"P{record['page']} | {record['title'] or '(untitled)'} | "
                f"images {record['n_images']} | chars {record['char_count']}\n"
            )
            handle.write("-" * 70 + "\n" + record["text"] + "\n\n")

    print(json.dumps({
        "ok": True,
        "pdf": source,
        "total_pages": document.page_count,
        "rendered": len(records),
        "out": str(output),
        "empty_text_pages": [record["page"] for record in records if record["char_count"] == 0],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
