#!/usr/bin/env python3
"""Produce monotonic page-to-transcript alignment hints using weighted overlap."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path


STOP_WORDS = set("""the a an and or of to in for on with is are was were be been that this these those
it its as by at from we you i they he she not no do does did can could will would should
so if then than there here what which who how why when about into over under more most very
just also only some any all each other same such own too much many one two do doing done
ok okay right yes now next let us our your their have has had get got make made use used
using thing things something anything everything way ways case cases point points""".split())
WORD = re.compile(r"[A-Za-z][A-Za-z\-']+|\d+(?:\.\d+)?")


def tokens(text: str) -> list[str]:
    return [
        token.lower() for token in WORD.findall(text)
        if token.lower() not in STOP_WORDS and len(token) >= 3
    ]


def align_pages(
    pages: list[dict],
    segments: list[dict],
    total_pages: int,
    diagonal_strength: float = 1.5,
    margin: int = 2,
) -> list[dict]:
    if not pages:
        return []
    if not segments:
        return [{
            "page": page["page"], "best_idx": None, "best_t": None, "score": 0.0,
            "span": None, "span_t": None,
        } for page in pages]

    segment_tokens = [Counter(tokens(segment.get("text", ""))) for segment in segments]
    frequencies = Counter()
    for counts in segment_tokens:
        frequencies.update(counts.keys())
    segment_count = len(segments)
    similarities = [[0.0] * segment_count for _ in pages]
    lexical_scores = [[0.0] * segment_count for _ in pages]

    for page_index, page in enumerate(pages):
        page_tokens = Counter(tokens(page.get("text", "")))
        page_progress = (page["page"] - 1) / max(total_pages - 1, 1)
        for segment_index, counts in enumerate(segment_tokens):
            score = 0.0
            for word, count in counts.items():
                if word in page_tokens:
                    weight = 1.0 + 2.0 / (1 + frequencies[word] / segment_count * 10)
                    score += min(count, 3) * weight
            if counts:
                score /= math.sqrt(sum(counts.values()))
            lexical_scores[page_index][segment_index] = score
            segment_progress = segment_index / max(segment_count - 1, 1)
            similarities[page_index][segment_index] = (
                score - diagonal_strength * abs(segment_progress - page_progress)
            )

    negative_infinity = float("-inf")
    page_count = len(pages)
    dynamic = [[negative_infinity] * segment_count for _ in pages]
    back = [[-1] * segment_count for _ in pages]
    dynamic[0] = similarities[0][:]
    for page_index in range(1, page_count):
        best_previous, best_index = negative_infinity, -1
        for segment_index in range(segment_count):
            if dynamic[page_index - 1][segment_index] > best_previous:
                best_previous = dynamic[page_index - 1][segment_index]
                best_index = segment_index
            dynamic[page_index][segment_index] = similarities[page_index][segment_index] + best_previous
            back[page_index][segment_index] = best_index

    current = max(range(segment_count), key=lambda index: dynamic[-1][index])
    assignments = [0] * page_count
    for page_index in range(page_count - 1, -1, -1):
        assignments[page_index] = current
        if page_index:
            current = back[page_index][current]

    results = []
    for page_index, page in enumerate(pages):
        segment_index = assignments[page_index]
        lower_anchor = assignments[page_index - 1] if page_index else segment_index
        upper_anchor = assignments[page_index + 1] if page_index + 1 < page_count else segment_index
        lower = max(0, lower_anchor - margin)
        upper = min(segment_count - 1, upper_anchor + margin)
        results.append({
            "page": page["page"],
            "best_idx": segment_index,
            "best_t": segments[segment_index]["t"],
            "score": round(lexical_scores[page_index][segment_index], 2),
            "span": [lower, upper],
            "span_t": [segments[lower]["t"], segments[upper]["t"]],
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", required=True)
    parser.add_argument("--diag", type=float, default=1.5, help="Diagonal timeline prior strength")
    parser.add_argument("--margin", type=int, default=2, help="Segments added around neighboring matches")
    args = parser.parse_args()
    build = Path(args.build)
    try:
        pages_data = json.loads((build / "pages.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": f"cannot read pages.json: {exc}"}, ensure_ascii=False))
        return 1
    transcript_path = build / "transcript.json"
    if transcript_path.exists():
        try:
            segments = json.loads(transcript_path.read_text(encoding="utf-8")).get("segments", [])
        except json.JSONDecodeError as exc:
            print(json.dumps({"ok": False, "error": f"invalid transcript.json: {exc}"}, ensure_ascii=False))
            return 1
    else:
        segments = []
    results = align_pages(
        pages_data.get("pages", []), segments, pages_data.get("total_pages", len(pages_data.get("pages", []))),
        diagonal_strength=args.diag, margin=max(0, args.margin),
    )
    payload = {
        "note": "Mechanical overlap hint; verify the transcript before citing it.",
        "segments": len(segments),
        "pages": results,
    }
    (build / "align.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    confident = sum(1 for result in results if result["score"] > 0.5)
    print(json.dumps({
        "ok": True, "pages": len(results), "segments": len(segments),
        "confident": confident, "out": str(build / "align.json"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
