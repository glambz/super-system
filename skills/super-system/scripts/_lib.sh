#!/usr/bin/env bash
# Usage: source "$(dirname "$0")/_lib.sh" (provides find_python, role_from_name, extract_json_file)
# Rule: copy scripts into the run folder at the start of a run and run the copies;
# never edit a script while a process is executing it.

find_python() {
  py_bin=""
  if command -v python3 >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
    py_bin="python3"
  elif command -v python >/dev/null 2>&1; then
    py_bin="python"
  else
    echo "error: python not found" >&2
    return 2
  fi
}

role_from_name() {
  local name="$1"
  local low
  low="$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]')"
  case "$low" in
    *-implementer) printf '%s\n' "implementer" ;;
    *-reviewer) printf '%s\n' "reviewer" ;;
    *-scout) printf '%s\n' "scout" ;;
    *)
      echo "error: name must be <task>-<role> (role: implementer, reviewer, or scout), got '$name'" >&2
      return 2
      ;;
  esac
}

extract_json_file() {
  local in_file="$1"
  local out_file="$2"
  "$py_bin" - "$in_file" "$out_file" <<'PY'
import json
import re
import sys
from pathlib import Path

in_p, out_p = Path(sys.argv[1]), Path(sys.argv[2])
if not in_p.is_file():
    sys.exit(1)

def extract_json_obj(text):
    text = text.strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if m:
        try:
            obj = json.loads(m.group(1))
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            obj = json.loads(text[start:end + 1])
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            pass
    return None

obj = extract_json_obj(in_p.read_text(encoding="utf-8", errors="replace"))
if not isinstance(obj, dict):
    sys.exit(1)
out_p.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
PY
}
