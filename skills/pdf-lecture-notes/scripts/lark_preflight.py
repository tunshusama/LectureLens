#!/usr/bin/env python3
"""Read-only check for the optional lark-cli publisher."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


SETUP = [
    "npx @larksuite/cli@latest install",
    "lark-cli config init",
    "lark-cli auth login --domain docs --domain drive",
    "lark-cli auth status --verify",
]


def main() -> int:
    executable = shutil.which("lark-cli")
    if not executable:
        print(json.dumps({
            "ok": False,
            "state": "missing",
            "reason": "lark-cli is not installed",
            "next_action": "ask whether the user wants to install the preferred Lark publisher",
            "setup": SETUP,
            "docs": "https://github.com/larksuite/cli",
        }, ensure_ascii=False))
        return 2
    result = subprocess.run(
        [executable, "auth", "status", "--verify"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        print(json.dumps({
            "ok": False,
            "state": "not_ready",
            "reason": "lark-cli is installed but user authentication is not ready",
            "next_action": "ask whether the user wants to configure or authenticate Lark",
            "setup": SETUP[1:],
            "details": (result.stderr or result.stdout).strip()[:1000],
        }, ensure_ascii=False))
        return 3
    print(json.dumps({
        "ok": True,
        "state": "ready",
        "preferred_destination": "lark",
        "next_action": "render Lark XML; confirm before publishing unless explicitly requested",
        "executable": executable,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
