#!/usr/bin/env python3
"""Cross-platform matplotlib defaults for explanatory figures."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402


CJK_CANDIDATES = [
    "Noto Sans CJK SC", "Noto Sans CJK TC", "Source Han Sans SC", "Source Han Sans TC",
    "PingFang SC", "PingFang HK", "Hiragino Sans GB", "Microsoft YaHei", "Microsoft JhengHei",
    "SimHei", "Heiti SC", "STHeiti", "Arial Unicode MS",
]
BLUE = "#2b6cb0"
ORANGE = "#dd6b20"
GRAY = "#a0aec0"
GREEN = "#2f855a"
RED = "#c53030"


def cjk_fonts() -> list[str]:
    available = {font.name for font in font_manager.fontManager.ttflist}
    return [name for name in CJK_CANDIDATES if name in available]


def cjk_font() -> str | None:
    fonts = cjk_fonts()
    return fonts[0] if fonts else None


def apply(figsize=(8, 4.5), dpi=160):
    fonts = cjk_fonts()
    if fonts:
        plt.rcParams["font.family"] = fonts
    plt.rcParams.update({
        "axes.unicode_minus": False,
        "figure.figsize": figsize,
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        "savefig.bbox": "tight",
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "font.size": 11,
        "legend.frameon": False,
    })
    return plt
