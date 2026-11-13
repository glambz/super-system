#!/usr/bin/env bash
# Usage: run-agy.sh <task>-<role> <worktree> <run_folder> <round> <schema_file> <model> <effort> [conversation_id]
# <task>-<role> must end in -implementer, -reviewer, or -scout (matches briefs/<task>-<role>-r<round>.md).
# Rule: copy scripts into the run folder at the start of a run and run the copies;
# never edit a script while a process is executing it.

set -euo pipefail

if [[ $# -lt 7 || $# -gt 8 ]]; then
  echo "Usage: $0 <task>-<role> <worktree> <run_folder> <round> <schema_file> <model> <effort> [conversation_id]" >&2
  exit 2
fi

source "$(dirname "$0")/_lib.sh"

task_name="$1"
worktree="$2"
run_folder="$3"
round="${4#r}"
schema_file="$5"
model="$6"
effort="$7"
conv_id="${8:-}"

role_from_name "$task_name" > /dev/null
find_python

name="${task_name}-r${round}"
brief_path="${run_folder}/briefs/${name}.md"
jsonl_path="${run_folder}/logs/${name}.jsonl"
err_path="${run_folder}/logs/${name}.err"
result_path="${run_folder}/results/${name}.json"
raw_path="${result_path}.raw"
meta_path="${run_folder}/results/${name}.meta"

mkdir -p "${run_folder}/logs" "${run_folder}/results"

if [[ ! -f "$brief_path" ]]; then
  echo "error: brief not found: $brief_path" >&2
  exit 2
fi

prompt="Read ${brief_path} and follow it exactly. Your final answer is JSON matching the schema you were given."

cmd=(agy -p "$prompt" --model "$model" --effort "$effort" --dangerously-skip-permissions --output-format stream-json --json-schema "$schema_file" --add-dir "$run_folder")
if [[ -n "$conv_id" ]]; then
  cmd+=(--conversation "$conv_id")
fi

set +e
(cd "$worktree" && "${cmd[@]}" < /dev/null > "$jsonl_path" 2> "$err_path")
rc=$?
set -e

rm -f "$raw_path"
set +e
"$py_bin" - "$jsonl_path" "$err_path" "$result_path" "$raw_path" "$meta_path" "$rc" <<'PY'
import json
import sys
from pathlib import Path

jsonl_p, err_p, res_p, raw_p, meta_p, rc_str = sys.argv[1:7]
rc = int(rc_str)

status = ""
conv_id = ""
structured = None
raw_response = ""

for line in Path(jsonl_p).read_text(encoding="utf-8", errors="replace").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    if ev.get("event") == "init" and isinstance(ev.get("init"), dict):
        conv_id = ev["init"].get("conversation_id") or conv_id
    if ev.get("event") == "result" and isinstance(ev.get("result"), dict):
        res = ev["result"]
        status = res.get("status", "")
        conv_id = res.get("conversation_id") or conv_id
        structured = res.get("structured_output")
        raw_response = res.get("response", "") or ""

Path(meta_p).write_text(
    f"exit={rc}\nstatus={status}\nconversation_id={conv_id}\n",
    encoding="utf-8",
)

if isinstance(structured, dict):
    Path(res_p).write_text(json.dumps(structured, indent=2) + "\n", encoding="utf-8")
else:
    if Path(res_p).is_file():
        Path(res_p).unlink()
    if raw_response:
        Path(raw_p).write_text(raw_response, encoding="utf-8")

err_txt = Path(err_p).read_text(encoding="utf-8", errors="replace") if Path(err_p).is_file() else ""
idle_warn = status == "ERROR" and "root agent idle; waiting for" in err_txt

if (status == "SUCCESS" and rc == 0) or idle_warn:
    sys.exit(0)
sys.exit(rc if rc != 0 else 1)
PY
parse_rc=$?
set -e

if [[ -f "$raw_path" ]]; then
  if ! extract_json_file "$raw_path" "$result_path"; then
    rm -f "$raw_path"
    exit 1
  fi
  rm -f "$raw_path"
fi

if [[ ! -f "$result_path" ]]; then
  exit 1
fi
exit "$parse_rc"
