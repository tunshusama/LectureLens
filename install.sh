#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/pdf-lecture-notes"
TARGET_PROJECT="${1:-}"

if [[ -z "$TARGET_PROJECT" || ! -d "$TARGET_PROJECT" ]]; then
  echo "Usage: $0 /path/to/project" >&2
  exit 1
fi

DESTINATION="$(cd "$TARGET_PROJECT" && pwd)/.agents/skills/pdf-lecture-notes"
if [[ -e "$DESTINATION" ]]; then
  echo "Destination already exists: $DESTINATION" >&2
  echo "Remove it explicitly before reinstalling; no files were changed." >&2
  exit 2
fi

echo "Notice: this Skill uses PyMuPDF, which is separately licensed under AGPL-3.0"
echo "or a commercial license. Review THIRD_PARTY_NOTICES.md before organizational use."
echo

mkdir -p "$(dirname "$DESTINATION")"
cp -R "$SOURCE_DIR" "$DESTINATION"

echo "Installed skill to: $DESTINATION"
echo "Install Python dependencies with:"
echo "  python3 -m pip install -r $DESTINATION/requirements.txt"
echo
echo "Required dependency check:"
python3 -c "import fitz, matplotlib, numpy, PIL, jsonschema" 2>/dev/null \
  && echo "  OK: Python dependencies" \
  || echo "  MISSING: one or more Python dependencies"
echo
echo "Optional Lark publisher:"
if command -v lark-cli >/dev/null 2>&1; then
  echo "  FOUND: lark-cli"
else
  echo "  NOT INSTALLED: Markdown still works. See README for optional Lark setup."
fi
