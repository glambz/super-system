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
5. Ask whether that CLI can drive a browser and use SuperDesign. Save what it has as `cli.tools` (for example `["browser", "superdesign"]`, or `[]`).
6. Save `roles` on this platform's entry and `cli` on each runner's entry; write only those fields. `platforms` follows the override rule in SKILL.md: a `--platforms mixed` run asks at its end whether to save it.

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
- the test command;
- for a reviewer, the review command `git diff <base> -- <files allowed>` and the new files among them (see "Baseline");
- the quality lenses, copied from the active track file;
- the scratch folder path;
- the result schema from `references/schemas/`.

A brief must stand on its own: the agent starts with no memory of this run.

- **Baseline.** Before each implementer run, record `<base>`: the commit `git stash create` prints (a snapshot of the working tree that leaves it untouched), or `git rev-parse HEAD` when it prints nothing because the tree is clean. Also record `git ls-files -o --exclude-standard` (untracked files). The done checks and the reviewer's diff use both. This requires a git repository: if the project has none, ask the user before dispatching (recommend `git init` and a first commit).
- **No trigger word.** Never write this skill's name or its trigger word in a brief as an instruction or a skill to load: an outside agent that has the skill installed must not start the main flow. Call yourself "the orchestrator". File paths are exempt (the run folder, schemas and scripts sit in folders named after the skill); the role files tell agents never to load or run that skill.
- **How the agent gets it.** The prompt you pass to the CLI is one line, "Read `<brief path>` and follow it exactly. Your final answer is JSON matching the schema you were given." Add the run folder with `--add-dir` so the agent can read the brief and write to its scratch folder.
- **Fix rounds** resume the implementer's own conversation (the "Resume" command under each runner) with a brief that holds only the reviewer's findings. That way it doesn't re-read everything.
- **Reviews** are always a fresh run.

## Commands

Start every run in the background with no time limit: stdout goes to the `.jsonl` log, stderr to the `.err` log. Pass the role's model and effort from the runner's `cli` slot (slot choice: `references/modes.md`).

Each runner runs with its skip-all-permissions flag: the user chose no permission prompts. The README warns that this lets the agent run any command.

**Antigravity (`agy`)**
- **Check:** `agy --version`. Headless runs reuse the login from one interactive `agy` session; without one, the run exits with "authentication required".
- **Run:** from the project folder (there is no `--cd` flag):
  `agy -p "<prompt>" --model <slug> --effort <level> --dangerously-skip-permissions --output-format stream-json --json-schema <schema file> --add-dir <run folder>`
- **Answer:** the stream's `result` event, with `status`, `response`, `structured_output` and `conversation_id`. Save `structured_output` as the result file.
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

## Is it done?

Never decide from the exit code alone. When a run's process ends, check all of the following. Any failure means the run is not done: handle it under "Stalls and blockers", or as a review fail.

1. **Exit status:** the exit code and the CLI's own status.
   - `agy`: `status` is `SUCCESS`.
   - Codex: a `turn.completed` event, and no `turn.failed` or `error` event.
   - Claude: `is_error` is false.
2. **The `.err` log:** look for permission notices, quota or rate-limit errors, and auth errors. In headless mode `agy` turns a refused approval into a soft deny: the run continues and still exits 0.
3. **The answer:** the result file exists and matches the role's schema.
4. **What the agent says:**
   - implementer: `status` is `done`;
   - reviewer: `verdict` is set and every finding is complete;
   - scout: every finding has evidence.
5. **The files** (see "Baseline"):
   - The implementer: its changes are `git diff --name-only <base>` plus untracked files that weren't in the recorded list. All must be inside its files allowed, and `files_changed` matches that list (and is not empty for `done`). When tasks run concurrently, a change inside another running task's files allowed belongs to that task; a change outside the union of running tasks' files allowed is a scope violation.
   - The reviewer: hash the reviewed task's files before and after; they must be unchanged. A new untracked file outside that union counts against the reviewer.

## Stalls and blockers

**Stall.** A run counts as stalled when its logs haven't grown for `stallMinutes` (config, default 15). Then:
1. Read the last events and check the process is still alive.
2. Report to the user: which agent, how long since its last output, what it was doing, and your recommendation (wait longer, or stop and retry).

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
