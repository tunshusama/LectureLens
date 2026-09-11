#!/usr/bin/env python3
"""Normalize timestamped lecture transcripts into JSON and readable text."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


HEADER = re.compile(r"^(?P<speaker>.+?)\s+(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\s*$")


def to_seconds(timestamp: str) -> int:
    parts = [int(value) for value in timestamp.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        if seconds >= 60:
            raise ValueError(f"invalid timestamp: {timestamp}")
        return minutes * 60 + seconds
    hours, minutes, seconds = parts
    if minutes >= 60 or seconds >= 60:
        raise ValueError(f"invalid timestamp: {timestamp}")
    return hours * 3600 + minutes * 60 + seconds


def parse_transcript(lines: list[str]) -> tuple[list[dict], list[str]]:
    segments: list[dict] = []
    preamble: list[str] = []
    current: dict | None = None
    for line in lines:
        stripped = line.strip()
        match = HEADER.match(stripped)
        if match and len(match.group("speaker").strip()) <= 80:
            if current is not None:
                segments.append(current)
            timestamp = match.group("time")
            current = {
                "speaker": match.group("speaker").strip(),
                "t": timestamp,
                "sec": to_seconds(timestamp),
                "text": "",
            }
            continue
        if not stripped:
            continue
        if current is None:
            preamble.append(stripped)
        else:
            current["text"] = f"{current['text']} {stripped}".strip()
    if current is not None:
        segments.append(current)
    for index, segment in enumerate(segments):
        segment["idx"] = index
    return segments, preamble


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("txt")
    parser.add_argument("--out", required=True)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    source = Path(args.txt).resolve()
    output = Path(args.out).resolve()
    project_root = Path(args.project_root).resolve()
    try:
        source_label = source.relative_to(project_root).as_posix()
    except ValueError:
        source_label = source.name
    try:
        lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
        segments, preamble = parse_transcript(lines)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    output.mkdir(parents=True, exist_ok=True)
    duration = segments[-1]["t"] if segments else None
    (output / "transcript.json").write_text(json.dumps({
        "source": source_label,
        "preamble": preamble[:20],
        "count": len(segments),
        "duration": duration,
        "segments": segments,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "transcript.txt").open("w", encoding="utf-8") as handle:
        for segment in segments:
            handle.write(
                f"#{segment['idx']} [{segment['t']}] {segment['speaker']}: {segment['text']}\n"
            )
    print(json.dumps({
        "ok": True,
        "segments": len(segments),
        "duration": duration,
        "out": str(output),
        "unparsed_head_lines": len(preamble),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
