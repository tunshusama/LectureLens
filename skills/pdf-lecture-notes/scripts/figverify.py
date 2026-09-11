#!/usr/bin/env python3
"""Render a matplotlib figure and report common hard layout failures."""

from __future__ import annotations

import os
import warnings

from matplotlib import text as mtext
from PIL import Image


def _bbox_of(text, renderer):
    try:
        bbox = (
            mtext.Text.get_window_extent(text, renderer=renderer)
            if isinstance(text, mtext.Annotation)
            else text.get_window_extent(renderer=renderer)
        )
    except Exception:
        return None
    return bbox if bbox.width > 0 and bbox.height > 0 else None


def _overlap(first, second) -> float:
    width = min(first.x1, second.x1) - max(first.x0, second.x0)
    height = min(first.y1, second.y1) - max(first.y0, second.y0)
    return width * height if width > 0 and height > 0 else 0.0


def _curve_hits(axis, items):
    samples = []
    for line in axis.lines:
        coordinates = line.get_xydata()
        if len(coordinates) == 0:
            continue
        dense = []
        for index in range(len(coordinates) - 1):
            dense.extend(
                coordinates[index] + (coordinates[index + 1] - coordinates[index]) * step / 24
                for step in range(25)
            )
        samples.append((line.get_label() or "line", axis.transData.transform(dense or coordinates)))
    for collection in axis.collections:
        offsets = collection.get_offsets()
        if offsets is not None and len(offsets):
            samples.append((collection.get_label() or "scatter", axis.transData.transform(offsets)))

    hits = []
    for label, bbox, boxed in items:
        if boxed:
            continue
        for name, points in samples:
            count = sum(1 for x, y in points if bbox.x0 <= x <= bbox.x1 and bbox.y0 <= y <= bbox.y1)
            if count:
                hits.append(f"{label!r} overlaps {name} ({count} sampled points)")
                break
    return hits


def check(
    figure,
    path,
    points=None,
    allow_overlap=(),
    pad=6.0,
    min_overlap=40.0,
    check_curves=True,
    min_width=800,
    max_width=2400,
):
    """Save a figure and return ``(ok, report)`` after deterministic checks."""
    report, problems = [], []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
    glyph_warnings = sorted({
        str(item.message) for item in caught if "missing from font" in str(item.message)
    })
    if glyph_warnings:
        problems.append("missing glyphs: " + " | ".join(glyph_warnings[:5]))
    else:
        report.append("glyph check passed")

    axis_items = {}
    for axis in figure.get_axes():
        items = []
        axis_bbox = axis.get_window_extent(renderer=renderer)
        for text in axis.texts:
            if not text.get_visible() or not text.get_text().strip():
                continue
            bbox = _bbox_of(text, renderer)
            if bbox is None:
                continue
            label = text.get_text().replace("\n", " / ")[:50]
            boxed = text.get_bbox_patch() is not None
            items.append((label, bbox, boxed))
            if (
                bbox.x0 < axis_bbox.x0 - pad or bbox.x1 > axis_bbox.x1 + pad
                or bbox.y0 < axis_bbox.y0 - pad or bbox.y1 > axis_bbox.y1 + pad
            ):
                problems.append(f"text outside plot area: {label!r}")
        axis_items[axis] = items
        for index, first in enumerate(items):
            for second in items[index + 1:]:
                if first[0] in allow_overlap or second[0] in allow_overlap:
                    continue
                area = _overlap(first[1], second[1])
                if area > min_overlap:
                    problems.append(f"text overlap {area:.0f}px2: {first[0]!r} x {second[0]!r}")
        if check_curves:
            problems.extend(f"annotation overlap: {hit}" for hit in _curve_hits(axis, items))

        legend = axis.get_legend()
        if legend is not None:
            legend_bbox = legend.get_window_extent(renderer=renderer)
            for label, bbox, _boxed in items:
                if _overlap(legend_bbox, bbox) > min_overlap:
                    problems.append(f"legend overlaps annotation: {label!r}")
            problems.extend(
                "legend " + hit.split(" ", 1)[1]
                for hit in _curve_hits(axis, [("legend", legend_bbox, False)])
            )

    if points:
        for name, axis, (x_value, y_value) in points:
            x_min, x_max = sorted(axis.get_xlim())
            y_min, y_max = sorted(axis.get_ylim())
            if not (x_min <= x_value <= x_max and y_min <= y_value <= y_max):
                problems.append(f"point outside axes: {name} = ({x_value:.3f}, {y_value:.3f})")

    figure.savefig(path)
    size = os.path.getsize(path)
    with Image.open(path) as image:
        width, height = image.size
    report.append(f"output {width}x{height}px, {size} bytes")
    if size == 0:
        problems.append("output file is empty")
    if not min_width <= width <= max_width:
        problems.append(f"width {width}px is outside configured range {min_width}-{max_width}px")

    for message in report:
        print("  ✓ " + message)
    for problem in problems:
        print("  ✗ " + problem)
    print("verification: " + ("failed" if problems else "passed"))
    return not problems, report
