# Output routing

This file is the single authority for choosing the output destination. Resolve it once per run before generating notes; do not store the result as part of the course familiarity profile.

## Priority

1. If the user explicitly requested a destination, honor it.
2. Otherwise, honor `destination_preference` in the current project's `.lecture-notes.json` when present.
3. With neither of the above, do not interpret silence as a preference for local or Markdown output. Lark/Feishu is preferred: run `scripts/lark_preflight.py` and proactively offer Lark/Feishu before generating notes.
4. If Lark is ready, ask whether the user wants the notes published to Lark/Feishu. Continue only after the answer; acceptance is an explicit destination choice and does not require a duplicate confirmation immediately before creation.
5. If the CLI is missing, ask whether the user wants to install `lark-cli`. If they agree, show the official setup commands and resume after setup. Do not install it silently, and do not treat agreement to install as agreement to publish.
6. If the CLI exists but is not configured or authenticated, ask whether the user wants to complete setup. Resume after verification, then ask whether to publish.
7. If the user declines Lark/Feishu, installation, or configuration, offer Markdown first. Mention Notion or Word only as manual-import alternatives, not as native v1 publishers.

Do not silently select Markdown merely because the user did not name a destination, and do not silently fall back to it after a Lark failure. Preserve `profile.json`, `note.json`, images, and rendered XML so the publication stage can resume.

## Explicit Markdown requests

An explicit Markdown or Obsidian request skips Lark preflight. Do not ask the user to install an unrelated tool.
