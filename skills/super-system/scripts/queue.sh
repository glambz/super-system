#!/usr/bin/env bash
# Usage: queue.sh <concurrency> <stagger_seconds> <commands_file_or_->
# Rule: copy scripts into the run folder at the start of a run and run the copies;
# never edit a script while a process is executing it.

set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <concurrency> <stagger_seconds> <commands_file_or_->" >&2
  exit 2
fi

cap="$1"
stagger="$2"
src="$3"

if ! [[ "$cap" =~ ^[0-9]+$ ]] || [[ "$cap" -lt 1 ]]; then
  echo "error: concurrency must be >= 1" >&2
  exit 2
fi

pids=()
failures=0

reap_finished() {
  local alive=()
  local pid
  for pid in "${pids[@]+"${pids[@]}"}"; do
    if kill -0 "$pid" 2>/dev/null; then
      alive+=("$pid")
    else
      if ! wait "$pid"; then
        failures=$((failures + 1))
      fi
    fi
  done
  pids=("${alive[@]+"${alive[@]}"}")
}

run_stream() {
  local first=1
  local line
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    [[ -z "$line" || "$line" == \#* ]] && continue

    while [[ "${#pids[@]}" -ge "$cap" ]]; do
      sleep 0.2
      reap_finished
    done

    if [[ "$first" -eq 0 && "$stagger" != "0" ]]; then
      sleep "$stagger"
    fi
    first=0

    bash -c "$line" &
    pids+=("$!")
  done
}

if [[ "$src" == "-" ]]; then
  run_stream
else
  run_stream < "$src"
fi

for pid in "${pids[@]+"${pids[@]}"}"; do
  if ! wait "$pid"; then
    failures=$((failures + 1))
  fi
done

if [[ "$failures" -gt 0 ]]; then
  exit 1
fi
