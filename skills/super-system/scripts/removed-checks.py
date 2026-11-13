#!/usr/bin/env python3
"""List removed lines vs <base> that look like permission/visibility/validation/error checks.

Rule: copy scripts into the run folder at the start of a run and run the copies;
never edit a script while a process is executing it.

Usage:
    python removed-checks.py <worktree> <base> [files...]
"""

import os
import re
import subprocess
import sys

CHECK_RE = re.compile(
    r"\b(raise|HTTPException|assert|deny|forbidden|401|403|404|permission|visible|scope)\b"
    r"|\b(require_|check_)"
    r"|\bif\s+not\b",
    re.IGNORECASE,
)
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+")


def main(argv):
    if len(argv) < 2:
        print("usage: removed-checks.py <worktree> <base> [files...]", file=sys.stderr)
        return 2

    worktree, base, *files = argv
    cmd = ["git", "-C", worktree, "diff", "-U0", base]
    if files:
        cmd += ["--", *files]

    env = os.environ.copy()
    env["MSYS_NO_PATHCONV"] = "1"
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if proc.returncode != 0:
        print(proc.stderr.strip() or f"git diff failed with exit {proc.returncode}", file=sys.stderr)
        return proc.returncode

    current_file = ""
    old_line = 0
    for line in proc.stdout.splitlines():
        if line.startswith("diff --git "):
            current_file = ""
        elif line.startswith("--- a/"):
            current_file = line[6:]
        elif line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("@@ "):
            m = HUNK_RE.match(line)
            old_line = int(m.group(1)) if m else 0
        elif line.startswith("-") and not line.startswith("--- "):
            content = line[1:]
            if CHECK_RE.search(content):
                print(f"{current_file}:{old_line}: {content}")
            old_line += 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
