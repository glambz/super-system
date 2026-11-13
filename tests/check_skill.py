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
    r"soft deny",
    r"3 review rounds",
    r"2 final-audit rounds",
]

# path relative to SKILL_DIR -> phrases that must appear (case-insensitive).
REQUIRED_PHRASES = {
    "SKILL.md": [
        "~/.super-system/config.json", "--workflow", "--models", "If unsure, ask",
        "first-run", "this run only", "Gate 1",
        "Gate 2", "reviewer", "references/platforms.md", "references/flows/",
        "references/track-ui.md", "references/track-backend.md", "Definition of done",
        "missing or incomplete", "config folders only break ties",
        "saved `slots` override", "used if installed",
        "## Conduct", "every subagent brief", "ask when unclear", "no hallucination",
        "no unsupported conclusions", "include it with its reason",
        "--platforms", "references/modes.md", "references/runners.md", "references/roles/",
        "3 review rounds", "2 final-audit rounds", "accepted by the user", "concurrently or one at a time",
        "file sets don't overlap", "stallMinutes", "stall check wasn't available",
        "in every platform mode", "never kill a running agent", "after the earlier task's loop ends",
        "reopened tasks get fresh review rounds",
        "~/.super-system/lessons.md", "## Retrospective", "retro.md", "contract-first",
        "references/retrospective.md", "technique cards", "references/techniques/",
        "brainstorming", "test-driven-development", "systematic-debugging", "verification-before-completion",
        "accepted minors",
    ],
    "references/modes.md": [
        "platform mode", "native", "mixed", "generic role table", "cli", "runner-only entry", "never below",
        "root-cause instructions", "mechanical task",
        "keyed by track", "cli.tools",
        "fix-round size", "polish round", "accepted minors",
    ],
    "references/track-ui.md": [
        "never silently erase", "tasteFile", "designLibrary", "1440", "390", "44px",
        "prefers-reduced-motion", "refresh means merge", "<skill-dir>/scripts/contrast-check.py", "references/modes.md",
        "docs/design/api/", "contract",
    ],
    "references/track-backend.md": [
        "never prod", "ADR", "references/modes.md", "docs/design/api/", "contract",
        "pre-deploy data checks", "read-only sql", "numeric rules",
    ],
    "references/design-md-template.md": [
        "[Measured]", "[Observed]", "[Inferred]", "[Decided]", "superdesign:", "history:",
    ],
    "references/platforms.md": [
        "Config key:** `claude-code`", "Config key:** `antigravity`", "Config key:** `cursor`",
        "Config key:** `opencode`", "Config key:** `oh-my-pi`", "Config key:** `codex`",
        "Config key:** `kilo-code`", "folder-only match",
        "You are a subagent. Follow the role file and task in your prompt exactly.", "not verified",
        "run_in_background", "references/modes.md",
        "~/.agents/skills", "~/.gemini/config/skills",
        "## First-run setup", "never overwrite other platforms", "config.json.bak", "never replace it",
    ],
    "references/retrospective.md": [
        "## Retrospective", "retro.md", "~/.super-system/lessons.md",
        "## End-of-run report", "never edit the skill without the user's approval",
        "accepted minors", "<project-name>-*",
    ],
    "references/severity.md": [
        "critical", "important", "minor", "latent issues", "exploitable without auth",
    ],
    "references/flows/inspect.md": ["every label in every mode", "Retrospective"],
    "references/flows/review.md": [
        "Retrospective", "references/severity.md", "verifier", "findings register", "1 in 5",
    ],
    "references/flows/build.md": [
        "chosen at Gate 2", "shared runtime resources", "docs/design/api/", "contract", "integration check",
        "decisions during the run",
    ],
    "references/flows/change.md": ["contract", "decisions during the run", "changed pre-existing sentence"],
    "references/flows/fix.md": ["contract", "regression_checks", "decisions during the run"],
    "references/runners.md": [
        "references/modes.md", "~/.super-system/runs/", "agy models", "model_provider", "ask the user to confirm", "cli.tools",
        "agy -p", "codex exec", "claude -p", "--dangerously-skip-permissions",
        "--dangerously-bypass-approvals-and-sandbox", "--conversation", "codex exec resume", "--json-schema",
        "--output-schema", "soft deny", "exit code alone", "trigger word", "never switch the role to native",
        "stallMinutes", "references/roles/", "references/schemas/",
        "git stash create", "git diff <base>", "requires a git repository", "`files_changed` matches",
        "file paths are exempt", "codex exec resume <id> -m <model>", "--conversation <id> --model",
        "-r <session_id> --model", "apply to every run", "`platforms` follows the override rule",
        "outside that union",
        "close stdin", "< /dev/null", '{"event": "result", "result"', "stopping the shell that started it",
        "the schema's full text", "code fence", "not enforced", "is of type `error`",
        "## Run scripts", "red_evidence", "no_test_reason", "concurrency", "429", "root agent idle",
        "references/techniques/ponytail.md", "references/techniques/tdd.md", "references/techniques/debugging.md",
        "references/techniques/verification.md", "references/techniques/security-backend.md",
        "references/techniques/ui-quality.md", "references/techniques/contract.md",
        "ponytail", "test-driven-development", "systematic-debugging", "verification-before-completion", "security-and-hardening",
        "may be empty",
        "## Parallel tasks in worktrees", "quota-aware scheduling", "hard constraints",
        "known-failing tests", "scripts/removed-checks.py", "scripts/worktree-cleanup.sh",
        "decisions during the run", "cli.window_hours", "_lib.sh",
    ],
    "references/roles/scout.md": ["read-only", "evidence", "references/schemas/scout.json", "only the JSON object", "never dispatch", "never load or run that skill"],
    "references/roles/implementer.md": ["files allowed", "blocked", "references/schemas/implementer.json", "only the JSON object", "never dispatch", "never load or run that skill", "red_evidence", "no_test_reason", "may be empty"],
    "references/roles/reviewer.md": [
        "scratch folder", "never edit project files", "not yours to judge", "never load or run that skill", "not_checked", "references/schemas/reviewer.json", "only the JSON object", "never dispatch", "regression_checks",
        "changed pre-existing sentence", "worked examples", "references/severity.md",
    ],
    "references/techniques/security-backend.md": ["security-and-hardening", "run lessons"],
    "../../README.md": [
        "Flash · high", "cheap for mechanical tasks", "reported", "--platforms", '"platforms": "mixed"', "agy",
        "codex exec", "--dangerously-skip-permissions", "~/.super-system/runs/", "can run any command",
        "What's new in v3", "What's new in v3.1", "concurrency", "keyed by track",
    ],
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
    pattern = re.compile(r"(?:references|scripts)/[\w./-]+\.(?:md|py|sh)")
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


# role -> (exact top-level required fields, (enum field, values) or None). Spec 2026-11-09 §7 + 2026-11-13 v3.
SCHEMAS = {
    "implementer": (["status", "summary", "files_changed", "tests_run", "blocker", "red_evidence", "no_test_reason"], ("status", ["done", "blocked", "failed"])),
    "reviewer": (["verdict", "tests_run", "findings", "not_checked", "regression_checks"], ("verdict", ["pass", "fail"])),
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


TRIGGER_WORDS = ("super-system", "supersystem")  # role files must not start the orchestrator (spec 2026-11-09 §6.3)


# Pointers that went stale when the mode tables moved to references/modes.md (spec 2026-11-09 §13).
STALE = ["workflow-mode table in SKILL.md", "role table in SKILL.md", "single-agent fallback from SKILL.md",
         "You are a super-system subagent", "as defined in SKILL.md"]


def check_stale():
    fails = []
    for p in skill_files():
        if p.suffix == ".md":
            text = p.read_text(encoding="utf-8")
            fails += [f"{rel(p)}: stale pointer {s!r}" for s in STALE if s in text]
    return fails


def check_no_duplicate_phrase_keys():
    """A dict literal silently keeps the last duplicate key; that once disabled the track-file phrases."""
    import ast
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "REQUIRED_PHRASES" for t in node.targets):
            keys = [k.value for k in node.value.keys]
            dups = sorted({k for k in keys if keys.count(k) > 1})
            return [f"REQUIRED_PHRASES has duplicate keys {dups}"] if dups else []
    return ["REQUIRED_PHRASES not found"]


def check_role_files():
    roles = SKILL_DIR / "references" / "roles"
    if not roles.is_dir():
        return ["references/roles/ missing"]
    fails = []
    for p in roles.glob("*.md"):
        text = p.read_text(encoding="utf-8").lower()
        fails += [f"{rel(p)}: contains trigger word {w!r}" for w in TRIGGER_WORDS if w in text]
    return fails


TECHNIQUES = [
    "ponytail", "tdd", "debugging", "verification",
    "security-backend", "ui-quality", "contract",
]


def check_techniques():
    fails = []
    runners_path = SKILL_DIR / "references" / "runners.md"
    runners_text = runners_path.read_text(encoding="utf-8") if runners_path.is_file() else ""
    for name in TECHNIQUES:
        rel_path = f"references/techniques/{name}.md"
        p = SKILL_DIR / rel_path
        if not p.is_file():
            fails.append(f"{rel_path} missing")
            continue
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        if len(lines) > 60:
            fails.append(f"{rel_path}: {len(lines)} lines > 60")
        if not re.search(r"^Source:", text, re.M):
            fails.append(f"{rel_path}: missing Source: line")
        low = text.lower()
        fails += [f"{rel_path}: contains trigger word {w!r}" for w in TRIGGER_WORDS if w in low]
        if rel_path not in runners_text:
            fails.append(f"references/runners.md: missing reference to {rel_path}")
    return fails


def main():
    fails = []
    for check in (check_frontmatter, check_size, check_banned, check_models_only_in_platforms,
                  check_refs, check_phrases, check_once, check_contrast, check_schemas, check_role_files,
                  check_techniques, check_stale, check_no_duplicate_phrase_keys):
        fails += check()
    for f in fails:
        print(f"FAIL: {f}")
    if fails:
        return 1
    print("check_skill: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
