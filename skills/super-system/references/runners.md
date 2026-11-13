# Runners and briefs

How to brief subagents, and how to run a role on another assistant's headless CLI. "Run folder", "Briefs" and "Is it done?" apply to every run, in every platform mode (items 1–2 of "Is it done?" only to CLI runs). The rest applies when platform mode is `mixed` (rules in `references/modes.md`, "Platform mode"). Flags were checked against official docs and installed CLIs on 2026-11-09; CLIs change, so when a flag fails, read the CLI's `--help`, tell the user, and fix this file.

## Setup

Run on the first `mixed` run on this platform, or when a routed platform has no `cli` entry in `~/.super-system/config.json`.

1. Ask which platform runs each role (scout, implementer, reviewer): `native` or another platform's config key from `references/platforms.md`.
2. For each routed platform, check its CLI is installed and signed in (see "Commands"). Missing or signed out: stop, show the README's install and sign-in steps, and ask.
3. Read what that platform is actually set to. Never assume its vendor's usual models: a CLI can point at another provider.
   - Codex: `model`, `model_provider` and `model_reasoning_effort` in `~/.codex/config.toml`.
   - Antigravity: `agy models`.
   - Claude Code: the aliases in `references/platforms.md`.
4. Propose `cli.top`, `cli.mid`, `cli.cheap` (model and effort each) and ask the user to confirm or correct them.
5. Ask whether that CLI can drive a browser and use SuperDesign. Save what it has as `cli.tools` (for example `["browser", "superdesign"]`, or `[]`). Optionally set `cli.concurrency` (default 3; custom-provider Codex: 3).
6. Check runner skills: verify whether each routed runner has the role-relevant helper skills installed (`ponytail`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `security-and-hardening`; plus `web-design-guidelines`, `modern-web-guidance`, `design-taste-frontend` for UI) and offer to install missing ones by copying from the user's installed copies (the technique cards remain the source of truth). Also check that the orchestrator's own skill is not installed where routed runners load skills (`references/platforms.md`); if it is, recommend moving it.
7. Save `roles` on this platform's entry and `cli` on each runner's entry; write only those fields. `platforms` follows the override rule in SKILL.md: a `--platforms mixed` run asks at its end whether to save it.

## Run folder

Each run gets `~/.super-system/runs/<project-name>-<YYYYMMDD-HHMMSS>/`, outside the project. Name every file `<task>-<role>-r<round>`:

- `briefs/<name>.md`: what the agent was told.
- `logs/<name>.jsonl`: the CLI's stdout (its event stream; CLI runs only).
- `logs/<name>.err`: the CLI's stderr.
- `results/<name>.json`: the agent's answer, as JSON.
- `scratch/<name>/`: the agent's own temporary files.

Never write run files into the project. Keep the folder after the run; the end-of-run report gives its path.

## Briefs

A brief is the role file from `references/roles/` (its full text) followed by the task:
- the goal;
- the files allowed to change;
- the interface the task produces or consumes;
- the test command, naming the exact interpreter/toolchain path when the project uses one (never a bare `python` or `node`);
- a **hard constraints** block: known-failing tests that must stay failing (list them by running the suite once on the base before Gate 2), shared files or helpers the task must not change, repo-enforced budgets/checks and the approved way to meet them, and the interpreter/toolchain path;
- the plan file's `## Decisions during the run` section (briefs point to it; reviewers judge against it);
- for a reviewer, the review command `git diff <base> -- <files allowed>` and the new files among them (see "Baseline");
- the quality lenses, copied from the active track file;
- the **technique cards** pasted in full (never rely on a skill being installed in the runner; where the runner has the matching skill installed, the card may name it as further reading, never naming the orchestrator's own skill):
  - implementer: `references/techniques/ponytail.md`, `references/techniques/tdd.md`, `references/techniques/verification.md` (+ `references/techniques/debugging.md` in `fix`; + `references/techniques/security-backend.md` on `backend`; + `references/techniques/ui-quality.md` on `ui`; + `references/techniques/contract.md` for a split feature);
  - reviewer: the same cards, as review criteria;
  - scout: `references/techniques/verification.md` (evidence only), + `references/techniques/debugging.md` in `fix`;
- the scratch folder path;
- the schema's full text, pasted from `references/schemas/<role>.json`, with: "Your final message is only the JSON object: no prose, no code fence." Pass the schema file to the CLI's schema flag as well, but don't rely on it: with a custom provider the flag may be not enforced (the smoke test on 2026-11-09 found Codex with a non-default provider ignored `--output-schema`, and the agent couldn't see the file).

A brief must stand on its own: the agent starts with no memory of this run.

- **Baseline.** Before each implementer run, record `<base>`: the commit `git stash create` prints (a snapshot of the working tree that leaves it untouched), or `git rev-parse HEAD` when it prints nothing because the tree is clean. Also record `git ls-files -o --exclude-standard` (untracked files). The done checks and the reviewer's diff use both. This requires a git repository: if the project has none, ask the user before dispatching (recommend `git init` and a first commit).
- **No trigger word.** Never write this skill's name or its trigger word in a brief as an instruction or a skill to load: an outside agent that has the skill installed must not start the main flow. Call yourself "the orchestrator". File paths are exempt (the run folder, schemas and scripts sit in folders named after the skill); the role files tell agents never to load or run that skill.
- **How the agent gets it.** The prompt you pass to the CLI is one line, "Read `<brief path>` and follow it exactly. Your final answer is JSON matching the schema you were given." Add the run folder with `--add-dir` so the agent can read the brief and write to its scratch folder.
- **Fix rounds** resume the implementer's own conversation (the "Resume" command under each runner) with a brief that holds only the reviewer's findings. That way it doesn't re-read everything.
- **Reviews** are always a fresh run.

## Commands

Start every run in the background with no time limit: stdout goes to the `.jsonl` log, stderr to the `.err` log. Close stdin on every run (`< /dev/null` in a POSIX shell, `< NUL` in cmd): `codex exec` given a prompt argument with an open stdin waits to read more input and never starts (smoke test, 2026-11-09). Pass the role's model and effort from the runner's `cli` slot (slot choice: `references/modes.md`).

Each runner runs with its skip-all-permissions flag: the user chose no permission prompts. The README warns that this lets the agent run any command.

**Antigravity (`agy`)**
- **Check:** `agy --version`. Headless runs reuse the login from one interactive `agy` session; without one, the run exits with "authentication required".
- **Run:** from the project folder (there is no `--cd` flag):
  `agy -p "<prompt>" --model <slug> --effort <level> --dangerously-skip-permissions --output-format stream-json --json-schema <schema file> --add-dir <run folder>`
- **Answer:** each stream line is shaped `{"event": "<name>", "<name>": {…}}` (events `init`, `step_update`, `result`). The last line is `{"event": "result", "result": {…}}`, holding `status`, `response`, `structured_output` and `conversation_id`. Save `structured_output` as the result file.
- **Resume:** from the project folder, `agy -p "<prompt>" --conversation <id> --model <slug> --effort <level> --dangerously-skip-permissions --output-format stream-json --json-schema <schema file> --add-dir <run folder>`.

**Codex (`codex exec`)**
- **Check:** `codex --version`. It uses the user's `~/.codex/config.toml`, including custom providers.
- **Run:** `codex exec -C <project> -m <model> -c model_reasoning_effort=<level> --dangerously-bypass-approvals-and-sandbox --json --output-schema <schema file> -o <result file> --add-dir <run folder> "<prompt>"`
- **Answer:** the `-o` file. The session id is in the `thread.started` event.
- **Resume:** from the project folder (`resume` takes neither `-C` nor `--add-dir`; the bypass flag already lets it read the run folder), `codex exec resume <id> -m <model> -c model_reasoning_effort=<level> --dangerously-bypass-approvals-and-sandbox --json --output-schema <schema file> -o <result file> "<prompt>"`.

**Claude Code (`claude -p`)**
- **Check:** `claude --version`, then a one-line `claude -p` call. A signed-out CLI returns `is_error: true` with "Not logged in", while `subtype` still says `success`.
- **Run:** from the project folder:
  `claude -p "<prompt>" --model <alias> --effort <level> --dangerously-skip-permissions --output-format stream-json --verbose --json-schema "<schema text>" --add-dir <run folder>`
  - `--json-schema` takes the schema's text, not a path.
  - `stream-json` requires `--verbose`.
- **Answer:** the `result` event. Check `is_error` and `permission_denials`. The parsed answer is expected in `structured_output`; if it is empty, parse `result` as JSON. (This was not verified on a signed-in CLI.)
- **Resume:** from the project folder, `claude -p "<prompt>" -r <session_id> --model <alias> --effort <level> --dangerously-skip-permissions --output-format stream-json --verbose --json-schema "<schema text>" --add-dir <run folder>`.

**Any other platform:** ask the user for its headless command and its model, effort, permission and output flags, and save them as that platform's runner entry. A platform with no headless mode can't take a routed role; say so.

## Run scripts

- Copy any runner or queue scripts into the run folder at the start of a run; never edit a script while a process is executing it (bash reads scripts incrementally) — write a new versioned copy instead.
- Shipped helper scripts live in `scripts/` (`_lib.sh`, `run-agy.sh`, `run-codex.sh`, `review-wrap.sh`, `queue.sh`, `wait-done.sh`, `removed-checks.py`, `worktree-setup.sh`, `worktree-cleanup.sh`); copy all of `scripts/` that the run uses (including `_lib.sh`) to the run folder at the start of a run and run the copies.
- Write briefs and scripts with the file-writing tool, never shell heredocs (quoting breaks, especially on Windows).
- Cap concurrent runs per runner at `cli.concurrency` (default 3; custom-provider Codex: 3) and queue runs above the cap. On a 429 rate-limit error: wait 300 s and retry at most 3 times; repeated 429s across runs → stop and report (the quota window may be exhausted).
- **Quota-aware scheduling:** before launching `N` runs on a runner, estimate `N × typical run length` against `cli.concurrency` and its provider window (optional `cli.window_hours` in config). If it won't fit, tell the user and propose staggering or deferring.
- Judge results by content (schema-valid JSON with the role's required fields), never by file size or exit code alone.

## Is it done?

Never decide from the exit code or file size alone. When a run's process ends, check all of the following. Any failure means the run is not done: handle it under "Stalls and blockers", or as a review fail.

1. **Exit status:** the exit code and the CLI's own status.
   - `agy`: `status` is `SUCCESS`. Status `ERROR` with a complete `structured_output` and stderr `"root agent idle; waiting for N background task(s) to finish"` is a warning, not a failure — record it and have the reviewer re-run the tests. Any other `ERROR` is a blocker.
   - Codex: a `turn.completed` event, and no top-level `turn.failed` or `error` event. An `item.completed` whose item is of type `error` is a warning (for example missing model metadata): list it in the report, don't fail the run for it.
   - Claude: `is_error` is false.
2. **The `.err` log:** look for permission notices, quota or rate-limit errors, and auth errors. In headless mode `agy` turns a refused approval into a soft deny: the run continues and still exits 0.
3. **The answer:** the result file exists and matches the role's schema. If the agent wrapped the JSON in prose or a code fence, take the one JSON object out of it first, then check it. Still no valid object: a blocker.
4. **What the agent says:**
   - implementer: `status` is `done`, and `red_evidence` is present and non-empty (unless `no_test_reason` is set because the brief explicitly says no test is needed; for `blocked` and `failed`, `red_evidence` may be empty);
   - reviewer: `verdict` is set (`pass` or `fail`), every finding is complete, and `regression_checks` is populated in `fix`. A missing `verdict` (even with a non-empty result file) → rerun fresh once, then a blocker;
   - scout: every finding has evidence.
5. **The files** (see "Baseline"):
   - The implementer: its changes are `git diff --name-only <base>` plus untracked files that weren't in the recorded list. All must be inside its files allowed, and `files_changed` matches that list (and is not empty for `done`); a `files_changed` mismatch alone → fix round, not a blocker. When tasks run concurrently, a change inside another running task's files allowed belongs to that task; a change outside the union of running tasks' files allowed is a scope violation.
   - The reviewer: hash the reviewed task's files before and after; they must be unchanged. A new untracked file outside that union counts against the reviewer.
   - **Base-diff guard:** before dispatching the reviewer, run `scripts/removed-checks.py <worktree> <base> <files…>` and pass its list of removed permission, visibility, validation, or error lines to the reviewer, who must confirm each is safe or reject.

## Parallel tasks in worktrees

- Create one worktree per concurrent task from the base branch (`scripts/worktree-setup.sh`).
- Copy the git-ignored env files that tests need into each worktree.
- Link dependency folders instead of copying them (for example a `node_modules` directory junction on Windows, symlink elsewhere).
- Put absolute worktree paths in every brief (agents' working directories drift).
- **Merge order and conflicts:** merge completed, reviewed tasks back in plan/dependency order; on a conflict, stop and resolve or ask the user before continuing, and re-run tests after merging.
- **Cleanup:** run `scripts/worktree-cleanup.sh`. Unlink dependency links first (without following them), then remove worktrees and prune — worktrees hold copies of env secrets.

## Stalls and blockers

**Stall.** A run counts as stalled when its logs haven't grown for `stallMinutes` (config, default 15). Then:
1. Read the last events and check the process is still alive.
2. Report to the user: which agent, how long since its last output, what it was doing, and your recommendation (wait longer, or stop and retry).
3. If the user says stop: stop the CLI process itself, found by its command line. On Windows, stopping the shell that started it leaves the CLI running.

How to wait and watch on each orchestrator platform is in `references/platforms.md`.

**Blockers.** For runners, these count as blockers under "Loops, stalls, blockers" in SKILL.md:
- an implementer returns `blocked` or `failed`;
- a CLI is missing or signed out;
- a permission refusal;
- a scope violation (an implementer outside its files allowed, a reviewer that changed project files);
- a project with no git repository;
- an answer that doesn't match its schema;
- a quota or rate-limit error;
- a stall;
- a round cap reached.

Work that isn't affected keeps running. Never switch the role to native without the user's answer.

## Missing tools

Some steps need a tool the runner may lack:
- **SuperDesign:** Gate 1 prototype drafts and their upload.
- **A browser:** UI reviewer lenses for responsive widths, console, focus and layout shift, and `inspect` crawling.

If the runner's `cli.tools` lacks the tool, that step runs on a native subagent for this run. Show this in the status line, for example `reviewer: codex/<model> (browser checks: native)`, and list it in the report. The runner still does everything else (code review, tests).
