#!/usr/bin/env bash
# Usage: worktree-setup.sh <repo> <worktree_path> <branch> <base> [--env <files...>] [--link <dirs...>]
# Rule: copy scripts into the run folder at the start of a run and run the copies;
# never edit a script while a process is executing it.

set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 <repo> <worktree_path> <branch> <base> [--env <files...>] [--link <dirs...>]" >&2
  exit 2
fi

repo="$1"
worktree="$2"
branch="$3"
base="$4"
shift 4

env_files=()
link_dirs=()
mode=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) mode="env"; shift ;;
    --link) mode="link"; shift ;;
    *)
      if [[ "$mode" == "env" ]]; then
        env_files+=("$1")
      elif [[ "$mode" == "link" ]]; then
        link_dirs+=("$1")
      else
        echo "error: unexpected argument '$1' (use --env or --link)" >&2
        exit 2
      fi
      shift
      ;;
  esac
done

repo_abs="$(cd "$repo" && pwd)"

if git -C "$repo" show-ref --verify --quiet "refs/heads/${branch}"; then
  target_ref="$branch"
  use_existing_branch=1
else
  target_ref="$base"
  use_existing_branch=0
fi

# Validate before creating the worktree so failures leave nothing behind.
for f in "${env_files[@]+"${env_files[@]}"}"; do
  if [[ ! -f "${repo_abs}/${f}" ]]; then
    echo "error: env file not found: ${repo_abs}/${f}" >&2
    exit 1
  fi
done

norm_links=()
for d in "${link_dirs[@]+"${link_dirs[@]}"}"; do
  d="${d#./}"
  d="${d%/}"
  if [[ -z "$d" || "$d" == /* || "$d" == [A-Za-z]:* || "$d" == ".." || "$d" == ../* || "$d" == */.. || "$d" == */../* ]]; then
    echo "error: link dir must be a relative path inside the repo, got '$d'" >&2
    exit 2
  fi
  src="${repo_abs}/${d}"
  if [[ ! -d "$src" ]]; then
    echo "error: link source is not a directory: $src" >&2
    exit 1
  fi
  if [[ -n "$(git -C "$repo" ls-tree "$target_ref" -- "$d")" ]]; then
    echo "error: link path '$d' already exists in checkout of '$target_ref'; remove it or link a different dir" >&2
    exit 1
  fi
  norm_links+=("$d")
done

if [[ "$use_existing_branch" -eq 1 ]]; then
  git -C "$repo" worktree add "$worktree" "$branch"
else
  git -C "$repo" worktree add -b "$branch" "$worktree" "$base"
fi

for f in "${env_files[@]+"${env_files[@]}"}"; do
  src="${repo_abs}/${f}"
  dst="${worktree}/${f}"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
done

wt_abs="$(cd "$worktree" && pwd)"
uname_s="$(uname -s)"

to_win() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$1"
  else
    printf '%s' "$1"
  fi
}

manifest="${wt_abs}/.worktree-links"
: > "$manifest"

for d in "${norm_links[@]+"${norm_links[@]}"}"; do
  src="${repo_abs}/${d}"
  dst="${wt_abs}/${d}"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" || -L "$dst" ]]; then
    if [[ -d "$dst" && ! -L "$dst" ]]; then
      if ! rmdir "$dst"; then
        echo "error: destination directory exists and is not empty: $dst" >&2
        exit 1
      fi
    else
      echo "error: destination already exists: $dst" >&2
      exit 1
    fi
  fi
  case "$uname_s" in
    MINGW*|MSYS*|CYGWIN*)
      MSYS_NO_PATHCONV=1 cmd /c mklink /J "$(to_win "$dst")" "$(to_win "$src")" > /dev/null
      ;;
    *)
      ln -s "$src" "$dst"
      ;;
  esac
  printf '%s\n' "$d" >> "$manifest"
done
