"""Render the neutral note model to portable Markdown."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from .pathing import copy_asset


def _table_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def _image(block: dict, project_root: Path, asset_dir: Path) -> str:
    name = copy_asset(block["image"], project_root, asset_dir)
    caption = block["caption"].replace("]", "\\]")
    return f"![{caption}](assets/{quote(name)})"


def render(note: dict, output: str | Path, project_root: str | Path) -> Path:
    output_path = Path(output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    asset_dir = output_path.parent / "assets"
    root = Path(project_root).resolve()

    lines = [f"# {note['title']}", ""]
    if note.get("reading_guide"):
        lines.extend([note["reading_guide"], ""])
    if note.get("outline"):
        lines.extend([f"## {note['labels']['outline']}", ""])
        lines.extend(f"{index}. {item}" for index, item in enumerate(note["outline"], 1))
        lines.append("")

    previous_h1 = None
    for section in note["sections"]:
        h1 = section.get("h1")
        if h1 and h1 != previous_h1:
            lines.extend([f"## {h1}", ""])
            previous_h1 = h1
        lines.extend([f"### {section['h2']}", ""])
        for block in section["blocks"]:
            kind = block["type"]
            if kind == "summary":
                lines.extend([f"**{note['labels']['key_point']}:** {block['text']}", ""])
            elif kind == "paragraph":
                lines.extend([block["text"], ""])
            elif kind in {"slide", "figure"}:
                lines.extend([_image(block, root, asset_dir), ""])
                if kind == "figure":
                    lines.extend([block["explanation"], ""])
            elif kind == "formula":
                lines.extend(["$$", block["latex"], "$$", ""])
                for item in block["symbols"]:
                    detail = item["meaning"]
                    if item.get("reading"):
                        detail = f"{item['reading']} — {detail}"
                    if item.get("example"):
                        detail += f" {note['labels']['example']}: {item['example']}"
                    lines.append(f"- **{item['symbol']}**: {detail}")
                lines.append("")
            elif kind == "terms":
                lines.extend([
                    f"| {note['labels']['term']} | {note['labels']['translation']} | {note['labels']['explanation']} |",
                    "|---|---|---|",
                ])
                for item in block["items"]:
                    lines.append(
                        f"| {_table_cell(item['term'])} | {_table_cell(item['translation'])} | "
                        f"{_table_cell(item['explanation'])} |"
                    )
                lines.append("")
            elif kind == "classroom_note":
                lines.extend([
                    f"> 🎧 **{note['labels']['classroom_note']} [{block['timestamp']}]**",
                    f"> {block['text']}",
                    "",
                ])
            elif kind == "learning_note":
                lines.extend([
                    f"> 💡 **{block['question']}**",
                    f"> {block['answer']}",
                    "",
                ])
            else:  # protected by schema validation
                raise ValueError(f"Unsupported block type: {kind}")

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return output_path
