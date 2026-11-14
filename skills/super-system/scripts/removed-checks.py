#!/usr/bin/env python3
"""List removed lines vs <base> that look like permission/visibility/validation/error checks
(raise, HTTPException, assert, deny, forbidden, 401/403/404, permission, visible, scope,
require_*, check_*, if not, not in, return False, return {"error"...}, or return / return None
on or directly after an if/elif line).

Rule: copy scripts into the run folder at the start of a run and run the copies;
never edit a script while a process is executing it.

Usage:
    python removed-checks.py <worktree> <base> [--] [files...]
"""

import ast
import os
import re
import subprocess
import sys

CHECK_RE = re.compile(
    r"\b(raise|HTTPException|assert|deny|forbidden|401|403|404|permission|visible|scope)\b"
    r"|\b(require_|check_)"
    r"|\bif\s+not\b"
    r"|\bnot\s+in\b"
    r"|\breturn\s+False\b"
    r"|\breturn\s*\{\s*['\"]error['\"]",
    re.IGNORECASE,
)
IF_RE = re.compile(r"^\s*(?:if|elif)\b")
RETURN_NONE_RE = re.compile(
    r"^\s*(?:(?:if|elif)\b[^#\n]*[:)]\s*)?return(?:\s+None)?\s*(?:(?:[;#]|//).*)?$"
)
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+")


def header_path(raw):
    """Path from a ---/+++ header: git C-quotes unusual names and tab-terminates names with spaces."""
    raw = raw.rstrip("\t")
    if raw.startswith('"'):
        raw = ast.literal_eval("b" + raw).decode("utf-8", "replace")
    return raw[2:]  # drop the a/ or b/ prefix


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) < 2:
        print("usage: removed-checks.py <worktree> <base> [--] [files...]", file=sys.stderr)
        return 2

    worktree, base, *files = argv
    files = [f for f in files if f != "--"]
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
    prev_was_if = False
    for line in proc.stdout.splitlines():
        if line.startswith("diff --git "):
            current_file = ""
            prev_was_if = False
        elif line.startswith(("--- a/", "+++ b/", '--- "a/', '+++ "b/')):
            current_file = header_path(line[4:])
            prev_was_if = False
        elif line.startswith("@@ "):
            m = HUNK_RE.match(line)
            old_line = int(m.group(1)) if m else 0
            prev_was_if = False
        elif line.startswith("-") and not line.startswith("--- "):
            content = line[1:]
            is_if = bool(IF_RE.match(content))
            if CHECK_RE.search(content) or (
                (is_if or prev_was_if) and RETURN_NONE_RE.match(content)
            ):
                print(f"{current_file}:{old_line}: {content}")
            prev_was_if = is_if
            old_line += 1
        else:
            prev_was_if = False
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
