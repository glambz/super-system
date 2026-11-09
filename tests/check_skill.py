#!/usr/bin/env python3
"""Guard the skill's anti-goals. Run from the repo root: python tests/check_skill.py"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "super-system"
SKILL_MD = SKILL_DIR / "SKILL.md"
MAX_SKILL_BYTES = 8192

# Personal content that must never ship (spec §2 anti-goals, §9 removals).
BANNED = [
    "indocyber", "C:\\Users", "Tasrock", "FF4905", "chamfer", "MiniMax",
    "gemini-3.8", "7f62f9c5", "1a29798d", "4263def4", "4764bd4a",
    "antislop-human", "Creative Animation Effects", "/Users/", "obsidian", "warm clay",
    "Tactical Split", "Monolithic", "Kinetic", "Stepped Asymmetric", "hero stays at top",
]

MODEL_NAMES = re.compile(r"\b(Opus|Sonnet|Haiku|Argon|Flash)\b", re.I)
MODELS_ALLOWED_IN = "references/platforms.md"

# Each rule is stated once (spec §2 anti-goal): these patterns must match exactly once across the skill.
ONCE = [
    r"root-cause instructions",
    r"overrides the generic|role table there overrides",
    r"console errors",
    r"write the minimum|minimum that passes",
]

# path relative to SKILL_DIR -> phrases that must appear (case-insensitive).
REQUIRED_PHRASES = {
    "SKILL.md": [
        "~/.super-system/config.json", "--workflow", "--models", "If unsure, ask",
        "first-run", "never overwrite other platforms", "this run only", "Gate 1",
        "Gate 2", "reviewer", "references/platforms.md", "references/flows/",
        "references/track-ui.md", "references/track-backend.md", "Definition of done",
        "missing or incomplete", "config.json.bak", "never replace it", "config folders only break ties",
        "saved `slots` override", "used if installed",
        "## Conduct", "every subagent brief", "ask when unclear", "no hallucination",
        "no unsupported conclusions", "include it with its reason",
    ],
    "references/track-ui.md": [
        "never silently erase", "tasteFile", "designLibrary", "1440", "390", "44px",
        "prefers-reduced-motion", "refresh means merge", "<skill-dir>/scripts/contrast-check.py",
    ],
    "references/track-backend.md": ["never prod", "ADR"],
    "references/design-md-template.md": [
        "[Measured]", "[Observed]", "[Inferred]", "[Decided]", "superdesign:", "history:",
    ],
    "references/platforms.md": [
        "Config key:** `claude-code`", "Config key:** `antigravity`", "Config key:** `cursor`",
        "Config key:** `opencode`", "Config key:** `oh-my-pi`", "Config key:** `codex`",
        "Config key:** `kilo-code`", "folder-only match",
    ],
    "references/flows/inspect.md": ["every label in every mode"],
    "../../README.md": ["Flash · high", "cheap for mechanical tasks", "reported"],
}


def skill_files():
    return [p for p in SKILL_DIR.rglob("*") if p.is_file() and "__pycache__" not in p.parts]


def rel(p):
    return p.relative_to(SKILL_DIR).as_posix()


def check_frontmatter():
    if not SKILL_MD.is_file():
        return ["SKILL.md missing"]
    text = SKILL_MD.read_text(encoding="utf-8")
    fails = []
    if not text.startswith("---"):
        fails.append("SKILL.md: no frontmatter")
    if not re.search(r"^name: super-system\s*$", text, re.M):
        fails.append("SKILL.md: frontmatter name is not super-system")
    if not re.search(r"^description: \S", text, re.M):
        fails.append("SKILL.md: empty description")
    return fails


def check_size():
    if SKILL_MD.is_file() and SKILL_MD.stat().st_size > MAX_SKILL_BYTES:
        return [f"SKILL.md is {SKILL_MD.stat().st_size} bytes > {MAX_SKILL_BYTES}"]
    return []


def check_banned():
    fails = []
    for p in skill_files():
        text = p.read_text(encoding="utf-8", errors="replace").lower()
        fails += [f"{rel(p)}: banned string {b!r}" for b in BANNED if b.lower() in text]
    return fails


def check_models_only_in_platforms():
    fails = []
    for p in skill_files():
        if rel(p) == MODELS_ALLOWED_IN:
            continue
        m = MODEL_NAMES.search(p.read_text(encoding="utf-8", errors="replace"))
        if m:
            fails.append(f"{rel(p)}: model name {m.group(0)!r} outside {MODELS_ALLOWED_IN}")
    return fails


def check_refs():
    fails = []
    pattern = re.compile(r"(?:references|scripts)/[\w./-]+\.(?:md|py)")
    for p in skill_files():
        for ref in set(pattern.findall(p.read_text(encoding="utf-8", errors="replace"))):
            if not (SKILL_DIR / ref).is_file():
                fails.append(f"{rel(p)}: references missing file {ref}")
    return fails


def check_phrases():
    fails = []
    for path, phrases in REQUIRED_PHRASES.items():
        f = SKILL_DIR / path
        if not f.is_file():
            fails.append(f"{path} missing")
            continue
        text = f.read_text(encoding="utf-8").lower()
        fails += [f"{path}: missing phrase {ph!r}" for ph in phrases if ph.lower() not in text]
    return fails


def check_once():
    texts = [p.read_text(encoding="utf-8", errors="replace") for p in skill_files() if p.suffix == ".md"]
    fails = []
    for pat in ONCE:
        n = sum(len(re.findall(pat, t, re.I)) for t in texts)
        if n != 1:
            fails.append(f"rule {pat!r} stated {n} times, expected once")
    return fails


def check_contrast():
    script = SKILL_DIR / "scripts" / "contrast-check.py"
    if not script.is_file():
        return ["scripts/contrast-check.py missing"]
    r = subprocess.run([sys.executable, str(script), "--selftest"], capture_output=True, text=True)
    return [] if r.returncode == 0 else [f"contrast selftest failed: {r.stdout.strip()}"]


# role -> (exact top-level required fields, (enum field, values) or None). Spec 2026-11-09 §7.
SCHEMAS = {
    "implementer": (["status", "summary", "files_changed", "tests_run", "blocker"], ("status", ["done", "blocked", "failed"])),
    "reviewer": (["verdict", "tests_run", "findings", "not_checked"], ("verdict", ["pass", "fail"])),
    "scout": (["findings", "open_questions", "not_checked"], None),
}


def _strict_objects(node, where, fails):
    """Strict structured-output rules: every object closes additionalProperties and requires all properties."""
    if isinstance(node, dict):
        t = node.get("type")
        if t == "object" or (isinstance(t, list) and "object" in t):
            if node.get("additionalProperties") is not False:
                fails.append(f"{where}: object without additionalProperties: false")
            if set(node.get("required", [])) != set(node.get("properties", {})):
                fails.append(f"{where}: required != properties")
        for k, v in node.items():
            _strict_objects(v, f"{where}.{k}", fails)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _strict_objects(v, f"{where}[{i}]", fails)


def check_schemas():
    fails = []
    for role, (fields, enum) in SCHEMAS.items():
        path = f"references/schemas/{role}.json"
        f = SKILL_DIR / path
        if not f.is_file():
            fails.append(f"{path} missing")
            continue
        try:
            schema = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fails.append(f"{path}: invalid JSON ({e})")
            continue
        if schema.get("type") != "object":
            fails.append(f"{path}: top-level type is not object")
        if sorted(schema.get("required", [])) != sorted(fields):
            fails.append(f"{path}: required is {schema.get('required')}, expected {fields}")
        if enum and schema.get("properties", {}).get(enum[0], {}).get("enum") != enum[1]:
            fails.append(f"{path}: {enum[0]} enum is not {enum[1]}")
        _strict_objects(schema, path, fails)
    return fails


def main():
    fails = []
    for check in (check_frontmatter, check_size, check_banned, check_models_only_in_platforms,
                  check_refs, check_phrases, check_once, check_contrast, check_schemas):
        fails += check()
    for f in fails:
        print(f"FAIL: {f}")
    if fails:
        return 1
    print("check_skill: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
