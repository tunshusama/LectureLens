"""Render the neutral note model to lark-cli document XML."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .pathing import project_relative


def _p(text: str) -> str:
    return f"<p>{escape(text)}</p>"


def _image(block: dict, project_root: Path) -> str:
    path = project_relative(block["image"], project_root)
    return (
        f'<img path="@./{escape(path, quote=True)}" width="720" '
        f'caption="{escape(block["caption"], quote=True)}"/>'
    )


def render(note: dict, output: str | Path, project_root: str | Path) -> Path:
    output_path = Path(output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    root = Path(project_root).resolve()
    lines = [f"<title>{escape(note['title'])}</title>"]

    if note.get("reading_guide"):
        lines.append(_p(note["reading_guide"]))
    if note.get("outline"):
        lines.extend([f'<h1 seq="auto">{escape(note["labels"]["outline"])}</h1>', "<ol>"])
        lines.extend(f"<li>{escape(item)}</li>" for item in note["outline"])
        lines.append("</ol>")

    previous_h1 = None
    for section in note["sections"]:
        h1 = section.get("h1")
        if h1 and h1 != previous_h1:
            lines.append(f'<h1 seq="auto">{escape(h1)}</h1>')
            previous_h1 = h1
        lines.append(f'<h2 seq="auto">{escape(section["h2"])}</h2>')
        for block in section["blocks"]:
            kind = block["type"]
            if kind == "summary":
                lines.append(f"<p><b>{escape(note['labels']['key_point'])}:</b> {escape(block['text'])}</p>")
            elif kind == "paragraph":
                lines.append(_p(block["text"]))
            elif kind in {"slide", "figure"}:
                lines.append(_image(block, root))
                if kind == "figure":
                    lines.append(_p(block["explanation"]))
            elif kind == "formula":
                lines.append(f"<latex>{escape(block['latex'])}</latex>")
                if block["symbols"]:
                    lines.append("<ul>")
                    for item in block["symbols"]:
                        detail = item["meaning"]
                        if item.get("reading"):
                            detail = f"{item['reading']}: {detail}"
                        if item.get("example"):
                            detail += f" {note['labels']['example']}: {item['example']}"
                        lines.append(f"<li><b>{escape(item['symbol'])}</b>: {escape(detail)}</li>")
                    lines.append("</ul>")
            elif kind == "terms":
                lines.append("<table><thead><tr>")
                for heading in (
                    note["labels"]["term"], note["labels"]["translation"], note["labels"]["explanation"]
                ):
                    lines.append(f'<th background-color="light-gray">{_p(heading)}</th>')
                lines.append("</tr></thead><tbody>")
                for item in block["items"]:
                    lines.append("<tr>")
                    for key in ("term", "translation", "explanation"):
                        lines.append(f"<td>{_p(item[key])}</td>")
                    lines.append("</tr>")
                lines.append("</tbody></table>")
            elif kind == "classroom_note":
                text = f"{block['text']} [{block['timestamp']}]"
                lines.append(
                    '<callout emoji="🎧" background-color="light-blue">'
                    f"<p><b>{escape(note['labels']['classroom_note'])}:</b> {escape(text)}</p></callout>"
                )
            elif kind == "learning_note":
                lines.append(
                    '<callout emoji="💡" background-color="light-yellow">'
                    f"<p><b>{escape(block['question'])}</b> {escape(block['answer'])}</p></callout>"
                )
            else:  # protected by schema validation
                raise ValueError(f"Unsupported block type: {kind}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path
