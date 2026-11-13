#!/usr/bin/env bash
# Usage: wait-done.sh <file> <ere_pattern> <idle_minutes> [poll_seconds]
# <ere_pattern> is matched as a POSIX extended regular expression (grep -Eq).
# Rule: copy scripts into the run folder at the start of a run and run the copies;
# never edit a script while a process is executing it.

set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "Usage: $0 <file> <ere_pattern> <idle_minutes> [poll_seconds]" >&2
  exit 2
fi

file="$1"
pattern="$2"
idle_minutes="$3"
poll_seconds="${4:-30}"

idle_secs="$(awk -v m="$idle_minutes" 'BEGIN { printf "%d", m * 60 }')"
last_active="$(date +%s)"
last_sig=""

while true; do
  if [[ -f "$file" ]] && grep -Eq -- "$pattern" "$file"; then
    echo "done"
    exit 0
  fi

  now="$(date +%s)"
  if [[ -f "$file" ]]; then
    size="$(wc -c < "$file" | tr -d ' ')"
    mtime="$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null || echo 0)"
    sig="${size}:${mtime}"
    if [[ "$sig" != "$last_sig" ]]; then
      last_sig="$sig"
      last_active="$now"
    fi
  fi

  if [[ $((now - last_active)) -ge "$idle_secs" ]]; then
    echo "stalled"
    exit 1
  fi

  sleep "$poll_seconds"
done
