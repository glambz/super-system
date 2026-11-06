# Super-System v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship super-system v2 as a portable Agent Skill in the `glambz/super-system` repo, installable with `npx skills`, and migrate the author's v1 setup onto it.

**Architecture:** A small always-loaded `SKILL.md` (startup, router, mode tables, safeguards, gates, definition of done) plus `references/` files loaded per flow/track/platform, one Python helper script, and one Python check script that guards the spec's anti-goals (size, banned personal strings, dangling references, contrast selftest).

**Tech Stack:** Markdown (Agent Skills `SKILL.md` format), Python 3 stdlib only, git, `npx skills` (Node ≥ 22.20; this machine has v24.13.0).

**Spec:** `docs/superpowers/specs/2026-11-06-super-system-v2-design.md` — the content source for every file below. Each task names the spec sections it turns into prose; executors read the spec, the plan does not repeat it.

## Global Constraints

- Repo root = `C:\Users\indocyber\Desktop\agent\super-system`; skill lives at `skills/super-system/`.
- `SKILL.md` ≤ 8192 bytes. Frontmatter `name: super-system` (must equal folder name).
- Each rule stated once across `SKILL.md` + `references/` (spec §2 anti-goal). References point back; they never restate a SKILL.md rule.
- No personal content anywhere under `skills/`: no `indocyber`, `C:\Users`, `Tasrock`, `FF4905`, `chamfer`, `MiniMax`, `gemini-3.8`, the four SuperDesign UUID prefixes `7f62f9c5` `1a29798d` `4263def4` `4764bd4a`, `antislop-human`, `Creative Animation Effects`.
- Model names allowed only in `references/platforms.md` (Opus/Sonnet/Haiku/Argon/Flash defaults, spec §8).
- Python: stdlib only, runs with `python` on Windows and `python3` elsewhere.
- Never guess a platform's subagent syntax, skill path, or a dependency's install command; take it from current official docs, or write "unknown — not documented" (spec §8, §10).
- Pushing to GitHub and any change under `C:\Users\indocyber\.agents`, `.super-system`, or `Desktop\projects\design-library` happen only in the tasks that own them, and pushing needs the user's explicit go-ahead at that step.
- License MIT, copyright holder `glambz`, year 2026.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Missing or malformed `~/.super-system/config.json`** (absent, invalid JSON, platform entry without `slots` on a non-default platform) → skill runs first-run setup for that platform only and never drops other platforms' entries. Pinned in Task 3's check phrases (`first-run`, `never overwrite other platforms`).
2. **Platform can't be detected confidently** → skill asks; never assumes Claude Code. Pinned in Task 3 (`If unsure, ask`).
3. **One-run override** (`--models economy`) → not persisted unless the user says yes at the end. Pinned in Task 3 (`this run only`).
4. **Library refresh over an existing entry** with historical notes/canvas links → merge, never overwrite. Pinned in Task 5 (`never silently erase` in `track-ui.md`).
5. **Migration appending to `user-taste.md`** → append under a new heading; file byte-length after ≥ before; backup verified before v1 is deleted. Pinned in Task 9 verification steps.

---

## File Structure

| File | Responsibility |
|---|---|
| `LICENSE` | MIT text |
| `.gitignore` | `__pycache__/` |
| `tests/check_skill.py` | Anti-goal guard: frontmatter, size, banned strings, dangling refs, required phrases, contrast selftest |
| `skills/super-system/SKILL.md` | Core (spec §4) |
| `skills/super-system/scripts/contrast-check.py` | WCAG contrast checker (spec §12) |
| `skills/super-system/references/platforms.md` | Per-platform model defaults, subagent spawn syntax, skill detection, single-agent fallback (spec §8, §10) |
| `skills/super-system/references/track-ui.md` | UI track (spec §9 UI column, anti-slop defaults, library write rules §7) |
| `skills/super-system/references/track-backend.md` | Backend track (spec §9 backend column) |
| `skills/super-system/references/design-md-template.md` | v1 template minus personal bits + `[Decided]` variant (spec §7) |
| `skills/super-system/references/flows/{build,change,fix,review,inspect}.md` | One flow each (spec §5, §6) |
| `README.md` | Install, deps, config, usage (spec §13, §10) |

---

### Task 1: Repo scaffold + anti-goal check script

**Files:**
- Create: `LICENSE`, `.gitignore`, `tests/check_skill.py`

**Interfaces:**
- Produces: `python tests/check_skill.py` → exit 0 and prints `check_skill: OK` when all checks pass; otherwise prints one `FAIL: <reason>` line per failure and exits 1. Constants at top of file that later tasks extend: `BANNED` (list[str]), `REQUIRED_PHRASES` (dict[str relative-path, list[str]]), `SKILL_DIR = Path("skills/super-system")`, `MAX_SKILL_BYTES = 8192`.

- [ ] **Step 1:** `git init` in the repo root; `git remote add origin https://github.com/glambz/super-system.git`; `git branch -M main`.
- [ ] **Step 2:** Write `LICENSE` (standard MIT, `Copyright (c) 2026 glambz`) and `.gitignore` (`__pycache__/`).
- [ ] **Step 3: Write `tests/check_skill.py`** with these checks, each a function returning a list of failure strings:
  - `check_frontmatter()`: `SKILL.md` exists, starts with `---`, has `name: super-system` and a non-empty `description:`.
  - `check_size()`: `SKILL.md` bytes ≤ `MAX_SKILL_BYTES`.
  - `check_banned()`: case-insensitive search of every file under `SKILL_DIR` for each `BANNED` string (list = Global Constraints banned list); report `file: string`.
  - `check_models_only_in_platforms()`: `Opus|Sonnet|Haiku|Argon|Flash` (word-boundary regex) appears in no file under `SKILL_DIR` except `references/platforms.md`.
  - `check_refs()`: every `references/...md` or `scripts/...` path mentioned in any skill file exists.
  - `check_phrases()`: for each `(path, phrases)` in `REQUIRED_PHRASES`, every phrase occurs (case-insensitive) in that file. Starts empty; Tasks 3–5 add entries.
  - `check_contrast()`: runs `scripts/contrast-check.py --selftest` via `subprocess` with `sys.executable`; exit code must be 0.
- [ ] **Step 4: Run to verify it fails:** `python tests/check_skill.py` → Expected: exit 1, `FAIL: SKILL.md missing` (and contrast script missing).
- [ ] **Step 5: Commit** `chore: scaffold repo with MIT license and skill check script`.

### Task 2: `contrast-check.py` with self-contained selftest

**Files:**
- Create: `skills/super-system/scripts/contrast-check.py` (start from `C:\Users\indocyber\.agents\skills\super-system\scripts\contrast-check.py`)

**Interfaces:**
- Produces: CLI `contrast-check.py <hex1> <hex2>` (unchanged output/exit codes from v1) and `contrast-check.py --selftest` → exit 0, prints `selftest: N pairs OK`.

- [ ] **Step 1: Write the failing selftest data** — replace the SKILL.md table parsing (`REFERENCE_HEADER`, `reference_doc_path`, `parse_reference_rows`, `parse_pairing`, `NAMED_COLORS`) with an in-script list `KNOWN = [("#FFFFFF","#000000",21.00,True,True), ("#777777","#FFFFFF",4.48,False,True), ("#767676","#FFFFFF",4.54,True,True), ("#999999","#FFFFFF",2.85,False,False)]` and a `selftest()` that recomputes each with `contrast_ratio`, compares `round(raw,2)` to the ratio and `raw>=4.5` / `raw>=3.0` to the two booleans. Remove the "antislop-human" and "R-25" wording from the docstring.
- [ ] **Step 2: Run** `python skills/super-system/scripts/contrast-check.py --selftest` → Expected: `selftest: 4 pairs OK`, exit 0. If a listed ratio is off, the KNOWN value is wrong (fix the data, not the formula — formula is WCAG 2.x and unchanged from v1).
- [ ] **Step 3: Run** `python skills/super-system/scripts/contrast-check.py "#FFFFFF" "#777777"` → Expected: `ratio: 4.48:1`, normal FAIL, large PASS, exit 1.
- [ ] **Step 4: Commit** `feat: contrast checker with self-contained selftest`.

### Task 3: `SKILL.md` core

**Files:**
- Create: `skills/super-system/SKILL.md`
- Modify: `tests/check_skill.py` (`REQUIRED_PHRASES`)

**Interfaces:**
- Consumes: reference file names from the File Structure table (must match exactly).
- Produces: the status-line format `super-system · <Platform> · flow: <flow> · workflow: <mode> · models: <mode|n/a — single agent> · tracks: <ui|backend|ui+backend>`; config path `~/.super-system/config.json`; flags `--workflow` / `--models`; role names `orchestrator`, `scout`, `implementer`, `reviewer`; slot names `top`, `mid`, `cheap`. All other files use these exact names.

- [ ] **Step 1: Add required phrases** to `REQUIRED_PHRASES["skills/super-system/SKILL.md"]`: `~/.super-system/config.json`, `--workflow`, `--models`, `If unsure, ask`, `first-run`, `never overwrite other platforms`, `this run only`, `Gate 1`, `Gate 2`, `reviewer`, `references/platforms.md`, `references/flows/`, `references/track-ui.md`, `references/track-backend.md`, `Definition of done`.
- [ ] **Step 2: Run** `python tests/check_skill.py` → Expected: FAIL on SKILL.md missing.
- [ ] **Step 3: Write `SKILL.md`** in the spec §4 order, content from: §4 startup steps; §5 flow table + invocation line + gate contents; §6 workflow-mode table and override rule; §7 config shape (short — fields and first-run behavior; first-run writes only this platform's entry and never overwrites other platforms); §8 roles, the reviewer ≥ implementer rule, the "mechanical task" list, generic slot mapping table, the weaker-orchestrator warning, single-agent fallback (model names stay in `platforms.md`); §10 dependency check behavior + "techniques, not workflows" usage list; §11 safeguards (5) and definition-of-done checklist + end-of-run report. Description frontmatter per §4.1, ≤ 1024 chars.
- [ ] **Step 4: Run** `python tests/check_skill.py` → Expected: remaining FAILs only for not-yet-created reference files (`check_refs`). Size and banned checks pass.
- [ ] **Step 5: Commit** `feat: SKILL.md core`.

### Task 4: `references/platforms.md` (researched)

**Files:**
- Create: `skills/super-system/references/platforms.md`

**Interfaces:**
- Consumes: role and slot names from Task 3.
- Produces: one section per platform — Claude Code, Antigravity, Cursor, OpenCode, Oh My Pi, Codex, Kilo Code, "Any other" — each with: how to detect it, global skill folder, how to spawn a subagent with a model + effort (or "not supported → single-agent fallback"), how to tell whether another skill is installed, and (Claude Code, Antigravity only) the default slot table from spec §8.

- [ ] **Step 1: Research** each platform's current official docs for subagent spawning with model/effort selection and skill discovery. Skill folders are already verified (Claude Code `~/.claude/skills/`; Codex/Cursor/OpenCode/Kilo `~/.agents/skills/`; Antigravity `~/.gemini/config/skills/`; Oh My Pi `~/.omp/agent/skills/` + `~/.agents/skills/` — secondary sources). Record each doc URL in the section.
- [ ] **Step 2: Write** the file. Default tables exactly as spec §8 (Claude Code: full Opus/Opus/Opus; normal Sonnet/Sonnet/Sonnet; economy Haiku / Sonnet (Haiku mechanical) / Sonnet. Antigravity: full Argon×3; normal Flash/Flash/Argon; economy Flash·high×3). Anything not documented → "unknown — not documented; use single-agent fallback".
- [ ] **Step 3: Run** `python tests/check_skill.py` → Expected: `check_models_only_in_platforms` passes; no new FAILs.
- [ ] **Step 4: Commit** `feat: platform reference with model defaults and subagent syntax`.

### Task 5: Track references + DESIGN.md template

**Files:**
- Create: `skills/super-system/references/track-ui.md`, `track-backend.md`, `design-md-template.md`
- Modify: `tests/check_skill.py` (`REQUIRED_PHRASES`)

**Interfaces:**
- Consumes: workflow-mode names from Task 3; project spec paths `docs/design/DESIGN.md`, `docs/design/prototype-<a|b|c>-design.md`, library path `<designLibrary>/<project-name>/<page-type>/` and `<designLibrary>/<domain>/<page-type>/` (spec §7).
- Produces: section headings `## Explore options`, `## Spec artifact`, `## Verify`, `## Quality lenses` in both track files (flows link to these anchors).

- [ ] **Step 1: Add required phrases:** `track-ui.md` → `never silently erase`, `tasteFile`, `designLibrary`, `1440`, `390`, `44px`, `prefers-reduced-motion`; `track-backend.md` → `never prod`, `ADR`; `design-md-template.md` → `[Measured]`, `[Observed]`, `[Inferred]`, `[Decided]`, `superdesign:`.
- [ ] **Step 2: Run** check → Expected: FAIL for the three missing files.
- [ ] **Step 3: Write `track-ui.md`** from spec §9 UI column + generalized calibration/anti-slop/modern-web/motion defaults + §7 spec-file locations and library refresh rule (merge, never silently erase notes or canvas links) + SuperDesign upload/verify steps from v1 Mode C Phase 4 minus project IDs and archetype names.
- [ ] **Step 4: Write `track-backend.md`** from spec §9 backend column.
- [ ] **Step 5: Write `design-md-template.md`**: v1 template verbatim (v1 SKILL.md lines 312–426) with the `pageType` list kept, plus a "build/change variant" note: `sourceUrl`/`inspectionDate` → `project`/`date`, labels `[Decided]` + `[Inferred]`.
- [ ] **Step 6: Run** check → Expected: only flow-file FAILs remain (if SKILL.md references them).
- [ ] **Step 7: Commit** `feat: UI/backend track references and DESIGN.md template`.

### Task 6: Flow references

**Files:**
- Create: `skills/super-system/references/flows/build.md`, `change.md`, `fix.md`, `review.md`, `inspect.md`

**Interfaces:**
- Consumes: gate names, role names, workflow-mode names (Task 3); track anchors (Task 5).
- Produces: each file = ordered steps of the backbone for that flow (spec §5 row), with per-workflow-mode differences inline only where §6 makes them differ, and links to track sections instead of repeating them.

- [ ] **Step 1: Write** the five files. `build`/`change`: v1 Mode C/B steps restated against the backbone. `fix`: root-cause investigation (systematic-debugging technique) → fix plan → Gate 2 → regression test that fails before the fix → implement + review → verify. `review`: read-only, outputs findings (severity, file:line, why, suggested fix); no edits. `inspect`: v1 Mode A (scope rules, 1440/390 crawl, evidence tagging, SuperDesign draft, library write via `design-md-template.md`).
- [ ] **Step 2: Run** `python tests/check_skill.py` → Expected: `check_skill: OK`, exit 0.
- [ ] **Step 3: Rule-once read-through:** grep the skill dir for the five safeguard ideas and the reviewer ≥ implementer rule (`grep -ril "self-certify\|weaker\|fabricat" skills/super-system`) → each idea defined in exactly one file; other hits are links. Fix duplicates.
- [ ] **Step 4: Commit** `feat: flow references`.

### Task 7: README + local `npx skills` verification

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: install line `npx skills add glambz/super-system -g`; config example (spec §7); dependency table (spec §10).

- [ ] **Step 1: Verify discovery locally:** `npx -y skills add . -l` from the repo root → Expected: lists exactly one skill, `super-system`. If not discovered at `skills/super-system/`, move to the layout the CLI reports and rerun Task 6 Step 2.
- [ ] **Step 2: Determine link vs copy:** run `npx -y skills add . -g -a claude-code -a codex -y` into a throwaway home (`HOME`/`USERPROFILE` set to a scratchpad dir for that one command), then inspect whether `~/.claude/skills/super-system` is a symlink/junction or a copy. Record the result for the README. Delete the throwaway dir.
- [ ] **Step 3: Research dependency sources** (spec §10 table): for each dependency, the official repo/marketplace and the install command per platform (`npx skills add …`, Claude Code `/plugin install …`, etc.). Unknown → write "not published for this platform" (that is the §10 platform-gap case).
- [ ] **Step 4: Write `README.md`** per spec §13: intro, install (global + `-a` form + link/copy finding + the Cursor/OpenCode double-listing note), dependencies table with commands, config section with §7 example, invocation examples (`/super-system build --workflow full --models normal`, `/super-system fix`, `/super-system inspect https://example.com landing-page`), license line.
- [ ] **Step 5: Run** `python tests/check_skill.py` → Expected: `check_skill: OK`.
- [ ] **Step 6: Commit** `docs: README with install, dependencies, config`.

### Task 8: Push to GitHub

- [ ] **Step 1:** Ask the user for go-ahead to push `main` to `https://github.com/glambz/super-system` (public, outward-facing). Wait for yes.
- [ ] **Step 2:** `git push -u origin main` → Expected: branch created on remote.
- [ ] **Step 3:** `npx -y skills add glambz/super-system -l` → Expected: lists `super-system`.

### Task 9: Migrate the author's setup (spec §15)

**Files (outside repo, author's machine):**
- Create: `C:\Users\indocyber\.super-system\backup\super-system-v1-2026-11-06\` (copy of v1)
- Create: `C:\Users\indocyber\.super-system\config.json`
- Modify (append only): `C:\Users\indocyber\Desktop\projects\design-library\user-taste.md`
- Delete (after backup verified): `C:\Users\indocyber\.agents\skills\super-system\`

- [ ] **Step 1: Backup:** copy v1 folder to the backup path. Verify: same file list and byte sizes (`SKILL.md` 32257, `scripts/contrast-check.py` 5941).
- [ ] **Step 2: Config:** write `config.json` exactly as spec §15 step 2 (`tasteFile`, `designLibrary`, `claude-code {workflow: full, models: normal}`, `antigravity {workflow: full, models: economy}`). Verify: `python -c "import json;print(json.load(open(r'C:\Users\indocyber\.super-system\config.json')))"` parses.
- [ ] **Step 3: Taste append:** read `user-taste.md`, record its byte length, append a section `## Migrated from super-system v1 (2026-11-06)` with the items in spec §15 step 3. Verify: new length > old length and the original content is a byte-identical prefix.
- [ ] **Step 4: Remove v1** from `~/.agents/skills/super-system` (only if Step 1 verified).
- [ ] **Step 5: Install v2:** `npx -y skills add glambz/super-system -g -a claude-code -a antigravity -a codex -a cursor -a opencode -a kilo -a pi -y` (agent ids from the `skills` CLI table; drop any it rejects and note it).
- [ ] **Step 6: Verify one copy per platform:** list each platform's global skill folder (Task 4 Step 1 list) and confirm exactly one `super-system` per folder, and that `~/.agents/skills/super-system/SKILL.md` is the v2 file (≤ 8192 bytes, no `indocyber`).
- [ ] **Step 7:** Report to the user what was backed up, written, appended, removed and installed.
