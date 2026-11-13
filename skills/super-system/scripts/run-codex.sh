#!/usr/bin/env bash
# Usage: run-codex.sh <task>-<role> <project_folder> <run_folder> <round> <schema_file> <model> <effort> [thread_id]
# <task>-<role> must end in -implementer, -reviewer, or -scout (selects briefs/<task>-<role>-r<round>.md
# and the required JSON key: status, verdict, or findings).
# Rule: copy scripts into the run folder at the start of a run and run the copies;
# never edit a script while a process is executing it.

set -euo pipefail

if [[ $# -lt 7 || $# -gt 8 ]]; then
  echo "Usage: $0 <task>-<role> <project_folder> <run_folder> <round> <schema_file> <model> <effort> [thread_id]" >&2
  exit 2
fi

source "$(dirname "$0")/_lib.sh"

task_name="$1"
project_dir="$(cd "$2" && pwd)"
mkdir -p "$3/logs" "$3/results"
run_folder="$(cd "$3" && pwd)"
round="${4#r}"
schema_file="$(cd "$(dirname "$5")" && pwd)/$(basename "$5")"
model="$6"
effort="$7"
thread_id="${8:-}"

role="$(role_from_name "$task_name")"
find_python

name="${task_name}-r${round}"
brief_path="${run_folder}/briefs/${name}.md"
jsonl_path="${run_folder}/logs/${name}.jsonl"
err_path="${run_folder}/logs/${name}.err"
result_path="${run_folder}/results/${name}.json"
meta_path="${run_folder}/results/${name}.meta"

if [[ ! -f "$brief_path" ]]; then
  echo "error: brief not found: $brief_path" >&2
  exit 2
fi

prompt="Read ${brief_path} and follow it exactly. Your final answer is JSON matching the schema you were given."

retry_sleep="${RETRY_SLEEP:-300}"
max_retries=3
attempt=0
rc=1

while true; do
  rm -f "$result_path"
  set +e
  if [[ -n "$thread_id" ]]; then
    (cd "$project_dir" && codex exec resume "$thread_id" -m "$model" -c "model_reasoning_effort=$effort" --dangerously-bypass-approvals-and-sandbox --json --output-schema "$schema_file" -o "$result_path" "$prompt" < /dev/null > "$jsonl_path" 2> "$err_path")
    rc=$?
  else
    codex exec -C "$project_dir" -m "$model" -c "model_reasoning_effort=$effort" --dangerously-bypass-approvals-and-sandbox --json --output-schema "$schema_file" -o "$result_path" --add-dir "$run_folder" "$prompt" < /dev/null > "$jsonl_path" 2> "$err_path"
    rc=$?
  fi
  set -e

  if grep -Eiq '(^|[^0-9])429([^0-9]|$)|rate[ _-]?limit' "$err_path" "$jsonl_path" 2>/dev/null; then
    if [[ $attempt -lt $max_retries ]]; then
      attempt=$((attempt + 1))
      sleep "$retry_sleep"
      continue
    fi
  fi
  break
done

extract_json_file "$result_path" "$result_path"

"$py_bin" - "$role" "$jsonl_path" "$result_path" "$meta_path" "$rc" <<'PY'
import json
import sys
from pathlib import Path

role, jsonl_p, res_p, meta_p, rc_str = sys.argv[1:6]
rc = int(rc_str)

thread_id = ""
turn_completed = False
turn_failed = False

for line in Path(jsonl_p).read_text(encoding="utf-8", errors="replace").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    etype = ev.get("type", "")
    if etype == "thread.started":
        thread_id = ev.get("thread_id") or thread_id
    elif etype == "turn.completed":
        turn_completed = True
    elif etype in ("turn.failed", "error"):
        turn_failed = True

Path(meta_p).write_text(f"exit={rc}\nthread_id={thread_id}\n", encoding="utf-8")

req_key = {"reviewer": "verdict", "implementer": "status", "scout": "findings"}[role]
obj = json.loads(Path(res_p).read_text(encoding="utf-8"))
if obj.get(req_key) in (None, ""):
    sys.stderr.write(f"error: missing required key {req_key!r} for role {role}\n")
    sys.exit(1)

if rc != 0 or turn_failed or not turn_completed:
    sys.exit(rc if rc != 0 else 1)
sys.exit(0)
PY
