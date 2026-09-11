# Output routing

This file is the single authority for choosing the output destination. Resolve it once per run; do not store the result as part of the course familiarity profile.

## Priority

1. If the user explicitly requested a destination, honor it.
2. Otherwise, honor `destination_preference` in the current project's `.lecture-notes.json` when present.
3. With neither of the above, Lark/Feishu is the preferred destination. Run `scripts/lark_preflight.py` before selecting it.
4. If Lark is ready, render local XML. Because publishing is an external write, obtain confirmation immediately before the cloud document is created unless the current request explicitly asked for Lark/Feishu publication.
5. If the CLI is missing, ask whether the user wants to install `lark-cli`. If they agree, show the official setup commands and resume after setup. Do not install it silently.
6. If the CLI exists but is not configured or authenticated, ask whether the user wants to complete setup. Resume after verification.
7. If the user declines installation/configuration, offer Markdown first. Mention Notion or Word only as manual-import alternatives, not as native v1 publishers.

Do not silently fall back to Markdown after a Lark failure. Preserve `profile.json`, `note.json`, images, and rendered XML so the publication stage can resume.

## Explicit Markdown requests

An explicit Markdown or Obsidian request skips Lark preflight. Do not ask the user to install an unrelated tool.
