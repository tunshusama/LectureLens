# Markdown output

Markdown is the first fallback when the user explicitly requests it or declines the preferred Lark/Feishu setup. It is local, portable, and works directly in Obsidian.

```bash
python3 <skill>/scripts/render_notes.py <build>/note.json \
  --format markdown --out <destination>/notes.md --project-root <project-root>
```

The renderer validates the model, copies referenced images into an `assets/` directory beside the note, and writes relative links. It renders formulas as display LaTeX, terminology as tables, and classroom/learning notes as blockquotes.

Do not publish or open another application unless the user requested it. Notion and Word may import or convert the Markdown, but v1 does not promise native layouts for them.
