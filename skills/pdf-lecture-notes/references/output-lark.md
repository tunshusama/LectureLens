# Lark / Feishu output

Use this path only when the user explicitly requests Lark or Feishu. Publishing sends course material to an external service and is a write action.

## Preflight

```bash
python3 <skill>/scripts/lark_preflight.py
```

If the CLI is missing or unauthenticated, keep all local artifacts and pause only the publication stage. Give the user the reported setup steps. Do not install software, initiate authorization, or fall back to another destination without their request.

Human setup, based on the official CLI documentation:

```bash
npx @larksuite/cli@latest install
lark-cli config init
lark-cli auth login --domain docs --domain drive
lark-cli auth status --verify
```

Official source: https://github.com/larksuite/cli

## Render and publish

```bash
python3 <skill>/scripts/render_notes.py <build>/note.json \
  --format lark --out <build>/note.xml --project-root <project-root>
```

When a compatible `lark-doc` skill is available, use its current create workflow. Otherwise inspect `lark-cli docs --help` instead of guessing flags. Validate the XML before creation, publish in manageable batches when the document is large, and fetch the document after writes to verify images and sections.

All `<img path>` values are `@./` paths relative to the project root. Run `lark-cli` from that same root.
