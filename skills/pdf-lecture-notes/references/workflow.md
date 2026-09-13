# Workflow

Run commands from the project root. First resolve the source-specific build directory:

```bash
python3 <skill>/scripts/run_context.py lecture.pdf --project-root .
```

Use the returned `build_dir` and `profile_path` in subsequent commands. Different PDFs cannot overwrite each other's profile or intermediate files.

## Prepare the PDF

```bash
python3 <skill>/scripts/pdf_prep.py lecture.pdf --out <build_dir> --project-root .
```

Use `--pages 1-8` for a sample. `pages.json` records the original total page count, so a partial sample keeps its correct lecture-time position.

If `empty_text_pages` is non-empty, use available visual inspection or OCR. State the limitation when neither is available.

## Prepare an optional transcript

```bash
python3 <skill>/scripts/transcript_prep.py transcript.txt --out <build_dir> --project-root .
python3 <skill>/scripts/align_hint.py --build <build_dir>
```

`align.json` is a mechanical hint based on word and number overlap with a monotonic timeline. Inspect the referenced transcript span before using a classroom note.

## Build the models

Reuse or create `profile.json` according to `run_context.py`, then create `plan.json` and `note.json` in that same build directory. Validate the two public models:

```bash
python3 <skill>/scripts/validate_model.py profile <build_dir>/profile.json
python3 <skill>/scripts/validate_model.py note <build_dir>/note.json --project-root .
```

Before rendering, complete [accuracy-review.md](accuracy-review.md) and save the
review record beside note.json. Resolve findings before delivery. The validator
checks structure and profile/mode consistency, not the truth of prose.

## Render

Resolve the destination using `output-routing.md`. For a Markdown selection:

```bash
python3 <skill>/scripts/render_notes.py <build_dir>/note.json --format markdown --out course/notes.md --project-root .
```

For Lark XML, follow `output-lark.md` and render with `--format lark`.

## Artifact lifecycle

- Source: the user's PDF and optional transcript; never modify them.
- Intermediate: `.notes_build/`; retain for resuming or troubleshooting and never publish by default.
- Final: `notes.md` plus `assets/`, or a user-requested Lark document.
- Disposable Lark draft folders: remove after successful publication; leave them on failure for diagnosis and tell the user where they are.
