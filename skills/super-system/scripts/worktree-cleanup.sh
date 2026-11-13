#!/usr/bin/env bash
# Usage: worktree-cleanup.sh <repo> <worktree_path>... [--links <rel_path>...]
# Reads <worktree>/.worktree-links (written by worktree-setup.sh) and removes only those links
# without following them (or explicit --links when manifest is missing; refuses if neither).
# Rule: copy scripts into the run folder at the start of a run and run the copies;
# never edit a script while a process is executing it.

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <repo> <worktree_path>... [--links <rel_path>...]" >&2
  exit 2
fi

repo="$1"
shift

worktrees=()
explicit_links=()
has_explicit_links=0
mode="wt"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --links)
      has_explicit_links=1
      mode="links"
      shift
      ;;
    *)
      if [[ "$mode" == "wt" ]]; then
        worktrees+=("$1")
      else
        [[ "$1" != "none" ]] && explicit_links+=("$1")
      fi
      shift
      ;;
  esac
done

if [[ "${#worktrees[@]}" -eq 0 ]]; then
  echo "Usage: $0 <repo> <worktree_path>... [--links <rel_path>...]" >&2
  exit 2
fi

uname_s="$(uname -s)"

to_win() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$1"
  else
    printf '%s' "$1"
  fi
}

unlink_one() {
  local wt="$1"
  local rel="${2#./}"
  rel="${rel%/}"
  [[ -z "$rel" ]] && return 0
  if [[ "$rel" == /* || "$rel" == [A-Za-z]:* || "$rel" == ".." || "$rel" == ../* || "$rel" == */.. || "$rel" == */../* ]]; then
    echo "error: refusing unsafe link path in manifest: '$rel'" >&2
    return 1
  fi

  local link_abs="${wt%/}/${rel}"
  if [[ ! -e "$link_abs" && ! -L "$link_abs" ]]; then
    return 0
  fi
  if [[ ! -L "$link_abs" ]]; then
    echo "error: refusing to remove non-link path: $link_abs" >&2
    return 1
  fi

  case "$uname_s" in
    MINGW*|MSYS*|CYGWIN*)
      if [[ -d "$link_abs" ]]; then
        MSYS_NO_PATHCONV=1 cmd /c rmdir "$(to_win "$link_abs")" > /dev/null
      else
        rm -f "$link_abs"
      fi
      ;;
    *)
      rm -f "$link_abs"
      ;;
  esac
}

for wt in "${worktrees[@]}"; do
  if [[ -d "$wt" ]]; then
    manifest="${wt%/}/.worktree-links"
    links_to_remove=()
    if [[ -f "$manifest" ]]; then
      while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%$'\r'}"
        [[ -z "$line" ]] && continue
        links_to_remove+=("$line")
      done < "$manifest"
    elif [[ "$has_explicit_links" -eq 1 ]]; then
      links_to_remove=("${explicit_links[@]+"${explicit_links[@]}"}")
    else
      echo "error: $wt has no .worktree-links manifest and no --links were given; refusing to remove (a recursive delete could follow an unknown link)" >&2
      exit 1
    fi

    for rel in "${links_to_remove[@]+"${links_to_remove[@]}"}"; do
      unlink_one "$wt" "$rel"
    done

    # Safety net: unlink any remaining symlinks/junctions without descending into links.
    wt_clean="${wt%/}"
    while IFS= read -r -d '' found; do
      rel="${found#"${wt_clean}/"}"
      unlink_one "$wt_clean" "$rel"
    done < <(find "$wt_clean" -type l -print0 2>/dev/null || true)

    remaining="$(find "$wt_clean" -type l 2>/dev/null || true)"
    if [[ -n "$remaining" ]]; then
      echo "error: links remain in worktree '$wt'; refusing git worktree remove:" >&2
      printf '%s\n' "$remaining" >&2
      exit 1
    fi
    rm -f "$manifest"
  fi
  git -C "$repo" worktree remove --force "$wt"
done

git -C "$repo" worktree prune
