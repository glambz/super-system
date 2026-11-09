# Platform Mode (External Runners) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let super-system route scout / implementer / reviewer roles to other assistants' headless CLIs (`agy`, `codex exec`, `claude -p`) under a new "platform mode" dial, with bounded loops, stall checks, a Gate 2 concurrency choice and stop-and-ask blockers, then smoke-test it and migrate the author's setup.

**Architecture:** All new behavior lives in reference files the orchestrator reads at dispatch time: `references/runners.md` (setup, run folder, per-CLI commands, done checks, stalls, blockers), `references/roles/*.md` (what each subagent is told), `references/schemas/*.json` (each role's answer format), and `references/modes.md` (workflow/model/platform dials, moved out of SKILL.md to make room). SKILL.md keeps one line per rule plus pointers. `tests/check_skill.py` pins every rule as a required phrase.

**Tech Stack:** Markdown (Agent Skills format), JSON Schema, Python 3 stdlib (check script), git, `npx skills`. CLIs: codex-cli 0.166.0 (installed), Claude Code 2.1.146 (installed), `agy` (user installs before Task 7).

**Spec:** `docs/superpowers/specs/2026-11-09-external-runners-design.md` (and `2026-11-06-super-system-v2-design.md` where it is silent). Each task names the spec sections it turns into prose; read them, the plan does not repeat them.

## Global Constraints

- Repo root `C:\Users\indocyber\Desktop\agent\super-system`; skill at `skills/super-system/`. Work on `main` (same as v2).
- `SKILL.md` ≤ 8192 bytes. Every rule stated once across `SKILL.md` + `references/`; references point, never restate.
- Model names (`Opus|Sonnet|Haiku|Argon|Flash`, case-insensitive) only in `references/platforms.md`. Runner docs say "the slug from `agy models`" / "the alias in platforms.md".
- Banned strings stay banned under `skills/` (incl. `MiniMax`, `gemini-3.8`, `indocyber`, `C:\Users`). The author's MiniMax setup appears only in the spec, README examples are generic, and the author's config lives in `~/.super-system/config.json`.
- Files under `references/roles/` never contain `super-system` or `supersystem` (spec §6.3).
- Schemas are strict-mode safe: every object has `"additionalProperties": false` and lists every property in `required`; optional values are nullable (`["object","null"]`), not omitted. Reason: `codex exec --output-schema` uses OpenAI structured outputs.
- Verified CLI flags (spec §6.4; `claude --help` checked 2026-11-09): `claude -p --model <alias> --effort <low|medium|high|xhigh|max> --dangerously-skip-permissions --output-format stream-json --json-schema '<schema JSON string>' --add-dir <dir> -r <session-id>`. Note `--json-schema` takes the schema **text**, not a path (agy and codex take a path).
- Python stdlib only. Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Anything outside the repo (`~/.super-system`, installed skills) and any `git push` only in Task 8, and a push needs the user's explicit go-ahead at that step.

## Review Focus

1. **Runner exits 0 but did nothing** (agy soft-deny, missing result file, `status: blocked`) → treated as not done, reported to the user. Pinned in Task 3 phrases `soft deny`, `exit code alone`.
2. **Runner CLI missing, signed out, or out of quota** → stop and ask; never silently do the work or switch the role to native. Pinned in Task 3 (`never switch the role to native`).
3. **Runner-only config entry** (a platform with only `cli`) → usable as a runner; if the user later chats on that platform, first-run setup fills `workflow`/`models` and keeps `cli`. Pinned in Task 4 (`runner-only entry` in modes.md).
4. **Concurrent tasks with overlapping files** → never run together. Pinned in Task 4 (`file sets don't overlap` in SKILL.md).
5. **Cap reached** → loop stops, deficiencies reported, user decides; passed items labeled accepted by the user. Pinned in Task 4 (`3 review rounds`, `2 final-audit rounds`, `accepted by the user`; the first two in `ONCE`).

---

## File Structure

| File | Responsibility |
|---|---|
| `skills/super-system/references/schemas/{implementer,reviewer,scout}.json` | Answer format each role must return (spec §7) |
| `skills/super-system/references/roles/{scout,implementer,reviewer}.md` | What a subagent is told: its role, limits, Conduct, answer format (spec §6.3) |
| `skills/super-system/references/runners.md` | Mixed-mode machinery: setup, run folder, briefs, per-CLI commands, permissions, done checks, stalls, blockers, missing tools (spec §6, §7, §10, §15) |
| `skills/super-system/references/modes.md` | The three dials: workflow table, role→slot table, platform mode + routing + `cli` slot resolution (moved from SKILL.md + spec §4, §5) |
| `skills/super-system/SKILL.md` | Pointers + one-line rules: platform dial in startup/overrides/status line, caps, Gate 2 concurrency, stall, blockers, DoD label, report additions |
| `skills/super-system/references/platforms.md` | Slot-agent line, per-orchestrator wait/watch method, where each platform's real model setup is read (spec §15, §6.1) |
| `skills/super-system/references/flows/build.md` | Step 7 concurrency now follows Gate 2 choice; fix the missing newline before step 6 |
| `README.md` | Platform mode docs, install/sign-in for `agy` and Codex, permissions warning, run folder |
| `tests/check_skill.py` | New checks: schemas, trigger words, required phrases, ONCE patterns |

---

### Task 1: Result schemas

Spec §7 ("Result schemas").

**Files:**
- Create: `skills/super-system/references/schemas/implementer.json`, `reviewer.json`, `scout.json`
- Modify: `tests/check_skill.py`

**Interfaces:**
- Produces: schema paths `references/schemas/<role>.json`; field names used by Tasks 2–3: implementer `status` (`done|blocked|failed`), `summary`, `files_changed`, `tests_run`, `blocker`; reviewer `verdict` (`pass|fail`), `tests_run`, `findings` (items: `file`, `line`, `severity`, `root_cause`, `fix_instruction`), `not_checked`; scout `findings` (items: `claim`, `evidence`), `open_questions`, `not_checked`. `tests_run` = object `{command, result}` (reviewer/implementer), nullable on implementer when blocked.

- [ ] **Step 1: Add `check_schemas()` to `tests/check_skill.py` and call it from `main()`**

```python
SCHEMAS = {
    "implementer": (["status", "summary", "files_changed", "tests_run", "blocker"], ("status", ["done", "blocked", "failed"])),
    "reviewer": (["verdict", "tests_run", "findings", "not_checked"], ("verdict", ["pass", "fail"])),
    "scout": (["findings", "open_questions", "not_checked"], None),
}
```
For each: file exists under `references/schemas/`, parses with `json.loads`, top-level `type == "object"`, `additionalProperties is False`, `sorted(required) == sorted(fields)`, and when an enum pair is given, `properties[name]["enum"] == values`. Also walk every nested dict with `"type"` containing `"object"` and assert `additionalProperties is False` and `set(required) == set(properties)`.

- [ ] **Step 2: Run `python tests/check_skill.py`** — Expected: FAIL lines for the three missing schema files.
- [ ] **Step 3: Write the three schema files** to satisfy the check and the Interfaces block (`severity`: enum `critical|important|minor`; `line`: integer or null; `blocker`: object `{question, tried}` or null).
- [ ] **Step 4: Run `python tests/check_skill.py`** — Expected: `check_skill: OK`.
- [ ] **Step 5: Commit** `git add tests/check_skill.py skills/super-system/references/schemas && git commit -m "Add role result schemas"`

### Task 2: Role files

Spec §6.3, §3 decisions 1, 3, 5; reviewer scratch rule (decision 16).

**Files:**
- Create: `skills/super-system/references/roles/scout.md`, `implementer.md`, `reviewer.md`
- Modify: `tests/check_skill.py`

**Interfaces:**
- Consumes: Task 1 schema paths and field names.
- Produces: role file paths used by Task 3 ("a brief = role file text + task").

- [ ] **Step 1: Add `check_role_files()`**: for each file in `references/roles/`, fail if it contains `super-system` or `supersystem` (case-insensitive). Add REQUIRED_PHRASES:
  - `references/roles/scout.md`: `read-only`, `evidence`, `references/schemas/scout.json`, `never dispatch`
  - `references/roles/implementer.md`: `files allowed`, `blocked`, `references/schemas/implementer.json`, `never dispatch`
  - `references/roles/reviewer.md`: `scratch folder`, `never edit project files`, `not_checked`, `references/schemas/reviewer.json`, `never dispatch`
- [ ] **Step 2: Run the check** — Expected: FAIL (files missing).
- [ ] **Step 3: Write the role files.** Each: one-line role statement; may / must not (incl. never dispatch other agents, never run approval gates, never start an orchestration workflow); the Conduct rules restated as subagent instructions (thorough, ask by returning the question in the answer, no hallucination, no unsupported conclusions, include recommendations); "your final answer is JSON matching `references/schemas/<role>.json`". Implementer: change only the files allowed in the brief; run the brief's test; return `blocked` with a question instead of guessing. Reviewer: review the real project folder; write only in the scratch folder given in the brief; never edit project files; run the tests named in the brief; apply the lenses in the brief; list skipped lenses in `not_checked`. Scout: read-only; every claim carries evidence (`file:line` or command output).
- [ ] **Step 4: Run the check** — Expected: `check_skill: OK`.
- [ ] **Step 5: Commit** `"Add subagent role files"`

### Task 3: Runner reference

Spec §6.1–6.5, §7, §10, §15 (missing tools; native stall best effort is in Task 4).

**Files:**
- Create: `skills/super-system/references/runners.md`
- Modify: `tests/check_skill.py`

**Interfaces:**
- Consumes: Task 1 schemas, Task 2 role files.
- Produces: section names Task 4 points to: "Setup", "Run folder", "Briefs", "Commands", "Is it done?", "Stalls and blockers", "Missing tools".

- [ ] **Step 1: Add REQUIRED_PHRASES** for `references/runners.md`: `~/.super-system/runs/`, `agy models`, `model_provider`, `ask the user to confirm`, `cli.tools`, `agy -p`, `codex exec`, `claude -p`, `--dangerously-skip-permissions`, `--dangerously-bypass-approvals-and-sandbox`, `--conversation`, `codex exec resume`, `--json-schema`, `--output-schema`, `soft deny`, `exit code alone`, `trigger word`, `never switch the role to native`, `stallMinutes`, `references/roles/`, `references/schemas/`. Add `r"soft deny"` to `ONCE`.
- [ ] **Step 2: Run the check** — Expected: FAIL (file missing).
- [ ] **Step 3: Write `runners.md`** with the seven sections above, turning spec §6.1–6.5, §7, §10 and §15's "tools a runner lacks" into instructions. Commands exactly as spec §6.4 and Global Constraints (claude's `--json-schema` takes the file's text). Stall section: logs not grown for `stallMinutes` → read last events, check process alive, report with recommendation, never kill or retry alone. Blockers section: list from spec §10; "never do the work yourself and never switch the role to native without the user's answer". Briefs section also: fix rounds resume the implementer's own conversation (`--conversation`, `codex exec resume`, `claude -r`); a reviewer is always a fresh run. "Is it done?" includes the concurrency-scoped file check of spec §7 item 5.
- [ ] **Step 4: Run the check** — Expected: `check_skill: OK` (model-name check must pass: no model names in this file).
- [ ] **Step 5: Commit** `"Add runner reference for mixed platform mode"`

### Task 4: Modes reference + SKILL.md

Spec §4, §5, §8, §9, §11, §15 (native stall best effort; mixed on other orchestrators), §3 decisions 6, 8, 11, 15.

**Files:**
- Create: `skills/super-system/references/modes.md`
- Modify: `skills/super-system/SKILL.md`, `tests/check_skill.py`

**Interfaces:**
- Consumes: Task 3 section names; Task 2 role path.
- Produces: `references/modes.md` sections "Workflow mode", "Model mode", "Platform mode" (Task 5 and README link to them).

- [ ] **Step 1: Update REQUIRED_PHRASES.**
  - `references/modes.md`: `platform mode`, `native`, `mixed`, `generic role table`, `cli`, `runner-only entry`, `never below`, `root-cause instructions`, `mechanical task`.
  - `SKILL.md` add: `--platforms`, `references/modes.md`, `references/runners.md`, `references/roles/`, `3 review rounds`, `2 final-audit rounds`, `accepted by the user`, `concurrently or one at a time`, `file sets don't overlap`, `stallMinutes`, `stall check wasn't available`.
  - Add `r"3 review rounds"` and `r"2 final-audit rounds"` to `ONCE`.
- [ ] **Step 2: Run the check** — Expected: FAIL (modes.md missing; new SKILL.md phrases missing).
- [ ] **Step 3: Create `modes.md`** by moving SKILL.md's "Workflow mode" and "Roles and model mode" sections there unchanged (they keep `root-cause instructions` stated once), then add "Platform mode": `native`/`mixed`, `roles` map, generic role table for routed roles, slot resolves to the runner's `cli` slots, runner-only entry rule, `mixed` verified only with Claude Code as orchestrator (others need a background shell + readable logs, marked not verified; otherwise say so and run native after telling the user).
- [ ] **Step 4: Edit SKILL.md.** Replace the two moved sections with a short "Modes" section pointing to `references/modes.md` (three dials, one line each). Startup: step 2 reads `platforms`/`roles` too; step 3 adds `--platforms`; status line adds `· platforms: <native | mixed (role: platform/model·effort …)>`. Invocation line adds `--platforms native|mixed`. Gate 2 bullet adds: lists each task's files and asks whether to run subagents concurrently or one at a time; concurrent only where file sets don't overlap. New "Loops and blockers" lines: at most 3 review rounds per task and 2 final-audit rounds, then report deficiencies and the user decides; blockers → stop, ask with a recommendation; stall check per `stallMinutes` (runners: `references/runners.md`; native: only where progress is visible, else the report says the stall check wasn't available). Roles line: dispatch to other platforms per `references/runners.md`; every brief starts from `references/roles/`. DoD: an item passed by the user counts as closed only labeled accepted by the user. Report: run folder path, rounds and platform/model per role, accepted deficiencies, blocker/stall events.
- [ ] **Step 5: Run the check** — Expected: `check_skill: OK`, and `wc -c skills/super-system/SKILL.md` ≤ 8192.
- [ ] **Step 6: Commit** `"Add platform mode dial; move mode tables to references/modes.md"`

### Task 5: platforms.md + build flow

Spec §15 (slot-agent line, which orchestrators), §6.1 step 3, §10 (how to wait), §13.

**Files:**
- Modify: `skills/super-system/references/platforms.md`, `skills/super-system/references/flows/build.md`, `tests/check_skill.py`

- [ ] **Step 1: REQUIRED_PHRASES**: platforms.md `You are a subagent. Follow the role file and task in your prompt exactly.`, `not verified`, `run_in_background`; build.md `chosen at Gate 2`. Add a BANNED-style check that platforms.md no longer contains `You are a super-system subagent`.
- [ ] **Step 2: Run the check** — Expected: FAIL on those phrases.
- [ ] **Step 3: Edit.** platforms.md: new slot-agent instruction line (and "rewrite existing slot agent files with it after asking"); a "Waiting on runners" subsection per orchestrator — Claude Code: Bash `run_in_background` (notifies on exit) + a log-watching monitor for the stall check; every other platform: not verified; per runner platform, where its real model setup is read (Codex `~/.codex/config.toml`, Antigravity `agy models`, Claude Code aliases). build.md: step 5 Plan also names shared runtime resources that could collide (dev-server port, test database; tasks sharing one run one at a time unless the user says otherwise — spec §9); step 7 parallel sentence → "Run tasks concurrently only if chosen at Gate 2"; put "6. **Gate 2.**" on its own line. Add phrase `shared runtime resources` to build.md's REQUIRED_PHRASES in Step 1.
- [ ] **Step 4: Run the check** — Expected: `check_skill: OK`.
- [ ] **Step 5: Commit** `"Document runner waiting, slot-agent line, Gate 2 concurrency in build flow"`

### Task 6: README

Spec §13 README bullet, §6.5, §6.2.

**Files:**
- Modify: `README.md`, `tests/check_skill.py`

- [ ] **Step 1: REQUIRED_PHRASES** for `../../README.md` add: `--platforms`, `"platforms": "mixed"`, `agy`, `codex exec`, `--dangerously-skip-permissions`, `~/.super-system/runs/`, `can run any command`.
- [ ] **Step 2: Run the check** — Expected: FAIL on those phrases.
- [ ] **Step 3: Edit README** (keep its anti-slop style): Modes section gains platform mode (third table: role → platform, example), status-line example with `platforms`; Settings JSON adds `platforms`, `roles`, `cli`, `stallMinutes`; Install gains "Mixed mode prerequisites" (install + sign in to `agy` once, Codex installed and configured; `claude` CLI if routing to Claude); a plain warning that routed agents run with skip-permissions flags and can run any command; run folder location; FAQ entry "Can I mix assistants?".
- [ ] **Step 4: Run the check** — Expected: `check_skill: OK`.
- [ ] **Step 5: Commit** `"README: platform mode"`

### Task 7: Smoke test

Spec §12. **Prerequisite (user, by hand):** install `agy` with the official installer from antigravity.google and run `agy` once interactively to sign in. If not done, stop and ask.

- [ ] **Step 1:** Create a throwaway git repo in the session scratchpad with `calc.py` (`def add(a, b): return a - b`) and `test_calc.py` asserting `add(2, 3) == 5`; commit. Create a run folder `~/.super-system/runs/smoke-<timestamp>/` with `briefs/ logs/ results/ scratch/`.
- [ ] **Step 2:** Run an implementer through `agy -p` per runners.md (role file + brief: fix `add`, files allowed `calc.py`, test `python -m pytest -q` or `python test_calc.py`), stream-json to the log, schema `implementer.json`. Expected: exit 0, `status` SUCCESS, `structured_output.status == "done"`, `git diff --name-only` == `calc.py`, no soft-deny in `.err`.
- [ ] **Step 3:** Hash `calc.py`; run a reviewer through `codex exec` per runners.md (schema `reviewer.json`, `-o` result, scratch `--add-dir`). Expected: result file valid against the schema, `verdict` present, `calc.py` hash unchanged, nothing new in the repo outside ignored files.
- [ ] **Step 4:** Record commands and outputs for the report. If a flag in runners.md was wrong, fix runners.md (and its phrase test), re-run the check, commit `"Fix runner flags found in smoke test"`.

### Task 8: Migrate the author's setup, push, reinstall

Spec §14.

- [ ] **Step 1:** Ask the author: scout platform (Codex or `agy`). Read `agy models` and `~/.codex/config.toml` (`model`, `model_provider`, `model_reasoning_effort`); propose `cli` slots + `cli.tools` for each; ask the author to confirm.
- [ ] **Step 2:** Back up `~/.super-system/config.json` to `config.json.bak-2026-11-09`; write with Python `json` (not a heredoc): `claude-code.platforms = "mixed"`, `claude-code.roles`, `antigravity.cli`, `codex.cli`, top-level `stallMinutes: 15`. Verify by re-reading: the old keys unchanged, new keys present.
- [ ] **Step 3:** Ask for the go-ahead to push; on yes `git push origin main`, then `npx skills update super-system -g`; verify `~/.agents/skills/super-system/SKILL.md` equals the repo's.
