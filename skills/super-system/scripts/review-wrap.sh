#!/usr/bin/env bash
# Usage: review-wrap.sh <worktree> <base> <command> [args...]
# Rule: copy scripts into the run folder at the start of a run and run the copies;
# never edit a script while a process is executing it.

set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <worktree> <base> <command> [args...]" >&2
  exit 2
fi

source "$(dirname "$0")/_lib.sh"

worktree="$1"
base="$2"
shift 2

find_python

snapshot() {
  "$py_bin" - "$worktree" "$base" <<'PY'
import hashlib
import json
import subprocess
import sys
from pathlib import Path

wt, base = Path(sys.argv[1]), sys.argv[2]

def git_lines(*args):
    r = subprocess.run(["git", "-C", str(wt), *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(r.returncode)
    return [line for line in r.stdout.splitlines() if line]

files = sorted(set(git_lines("diff", "--name-only", base) + git_lines("ls-files", "-o", "--exclude-standard")))
out = {}
for rel in files:
    p = wt / rel
    if p.is_file():
        out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    else:
        out[rel] = "MISSING"
print(json.dumps(out, sort_keys=True))
PY
}

before="$(snapshot)"
set +e
"$@"
rc=$?
set -e
after="$(snapshot)"

if [[ "$before" != "$after" ]]; then
  "$py_bin" - "$before" "$after" <<'PY'
import json
import sys

b, a = json.loads(sys.argv[1]), json.loads(sys.argv[2])
for k in sorted(set(b) | set(a)):
    if b.get(k) != a.get(k):
        print(f"changed: {k}")
PY
  echo "review-wrap: CHANGED"
  exit 1
fi

echo "review-wrap: UNCHANGED"
exit "$rc"
