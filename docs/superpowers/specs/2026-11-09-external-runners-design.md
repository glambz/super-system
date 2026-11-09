# super-system — Platform mode (external runners) — Design

Date: 2026-11-09. Builds on `2026-11-06-super-system-v2-design.md` (the v2 spec). Where this document is silent, v2 stands.

## 1. Intent

Let the orchestrator (the model the user chats with) hand each subagent role to a **different coding assistant**, run headless from the shell. The author's case: chat with Claude Code as the orchestrator ("the mastermind"), run implementers on Antigravity's CLI (`agy`, a Flash model), run reviewers on Codex (`codex exec`, configured to use MiniMax-M3.1-Flash through a custom provider). The orchestrator plans, the outside agents build and review, and the orchestrator does the final audit and decides pass or redo.

Why: each platform has its own subscription quota (5-hour and weekly windows), so spreading roles across them stretches what one run can do. A reviewer from a different model family than the implementer also catches different mistakes.

## 2. Goals, non-goals, anti-goals

**Goals**
- A third dial, **platform mode** (`native` | `mixed`), saved per platform like workflow mode and model mode, with a per-run override.
- In `mixed`, each role (scout, implementer, reviewer) is routed to a platform: the current one (`native`) or another assistant's headless CLI.
- Model mode still picks each role's slot (`top` / `mid` / `cheap`); the slot resolves to a model **on the platform that runs the role**. The user confirms those models; nothing assumes a platform's usual vendor models.
- Outside agents get a role file and a task, never the orchestrator skill.
- Bounded loops, stall detection, concurrency choice at Gate 2, and a "stop and ask" rule for every blocker. These apply to native subagents too.
- No files added to the user's project by the run machinery.

**Non-goals**
- Talking to model APIs directly, proxies or gateways (LiteLLM etc.). Only each platform's own first-party CLI.
- Using one platform's login inside another tool (the OAuth-sharing plugins that got Antigravity accounts banned).
- Runner support for every platform on day one: verified runners are Antigravity (`agy`) and Codex (`codex exec`); Claude Code (`claude -p`) is added because the skill is public and Claude is a likely runner target when someone orchestrates from elsewhere. Any other platform goes through the "ask the user for the command" path (§6.5).
- Git worktrees per task. Not needed with file-disjoint concurrency (§9).

**Anti-goals** (it fails even if it "works" when…)
- The orchestrator silently does a runner's work itself, or silently falls back to native, when a runner is blocked, out of quota, stuck, or not installed.
- An outside agent starts acting as an orchestrator (dispatching agents, running gates) because it loaded the full skill.
- "Done" is decided from an exit code alone.
- A loop runs forever.
- Run artifacts (briefs, logs, reviewer temp files) end up inside the user's project.
- SKILL.md grows past its 8192-byte budget (v2 rule, still enforced by `tests/check_skill.py`).

## 3. Decided by the user

1. **Verification of a finished agent:** check the process result and the changed files, **and** read the agent's own answer to see whether it says it is done.
2. **Permissions:** outside agents run with no permission prompts at all.
3. **Reviewer may write**, but only into an exclusive **scratch folder** outside the project; it reviews the real project folder. The orchestrator checks it did not edit the reviewed task's files.
4. **Briefs are self-contained** (each run starts with no memory).
5. **Role files, not the full skill:** each outside agent gets only its role's reference file, so it knows its role and never becomes the orchestrator.
6. **Loop caps:** at most 3 reviewer rounds per task and 2 final-audit rounds. After a cap, report the deficiencies; the user decides between another round and passing it as is. Any blocker is always reported; the orchestrator asks the user what to do, with a recommendation.
7. **Quota:** all three platforms have 5-hour and weekly limits. When one is hit, ask the user; never do the work instead.
8. **Concurrency is a Gate 2 question:** "run subagents concurrently or one at a time?" Only tasks with no shared files may run together (example: feature A backend touches files a, b; feature B backend touches c; both frontends touch d, e → the two backend tasks may run together, the two frontend tasks may not).
9. **No time limit:** agents run in the background as long as they need. Only an agent that stops progressing (no new output) counts as stuck.
10. **Two model-ish dials:** model mode and platform mode.
11. **Final audit happens once, at the end of the run**, after every task's implement/review loop is done.
12. **Stuck-agent reports, blockers, quota, cap reached:** always ask the user.
13. **Scouts are routable too** (the author is choosing between Codex and `agy` for scouts).
14. **Model mode picks the model on the runner platform**, and setup **asks the user to confirm** the models it found.
15. Stall threshold default **15 minutes**, configurable. Caps, stall check and the concurrency question **also apply to native subagents**.
16. The reviewer's exclusive folder is a **scratch folder**, not a copy of the repo.

## 4. Platform mode and role routing

- `native` (default; today's behavior): every role runs as a subagent of the current platform.
- `mixed`: each role runs on the platform named in this platform's `roles` map. A role missing from the map runs `native`.
- Override for one run: `--platforms native|mixed` (or plain words). Same rule as the other dials: this run only; at the end, ask once whether to save.
- Slot choice is unchanged: the generic role table in SKILL.md (scout / implementer / reviewer × full / normal / economy → top / mid / cheap) picks the slot. **For a role routed to another platform, the generic table is used, not the orchestrator platform's own role table** (that table describes its own subagents). The slot then resolves to the runner platform's `cli` slots (§5).
- "A reviewer's slot is never below the implementer's" still holds, compared by slot. No cross-vendor strength comparison is attempted; the user confirmed the models.

## 5. Saved settings

`~/.super-system/config.json` gains, per platform entry:

```json
{
  "platforms": {
    "claude-code": {
      "workflow": "full", "models": "normal",
      "platforms": "mixed",
      "roles": { "scout": "native", "implementer": "antigravity", "reviewer": "codex" }
    },
    "antigravity": {
      "workflow": "full", "models": "economy",
      "cli": {
        "top":   { "model": "<slug from agy models>", "effort": "high" },
        "mid":   { "model": "<slug>", "effort": "high" },
        "cheap": { "model": "<slug>", "effort": "high" }
      }
    },
    "codex": {
      "cli": {
        "top":   { "model": "MiniMax-M3.1-Flash", "effort": "<as confirmed>" },
        "mid":   { "model": "MiniMax-M3.1-Flash", "effort": "<as confirmed>" },
        "cheap": { "model": "MiniMax-M3.1-Flash", "effort": "<as confirmed>" }
      }
    }
  },
  "stallMinutes": 15
}
```

- `platforms` (the field inside an entry): `native` | `mixed`. Missing = `native`.
- `roles`: role → config key of a platform (`native` allowed). Only read when `platforms` is `mixed`.
- `cli`: the slots used **when this platform runs as an outside runner**. Separate from `slots`, because a native slot can be an alias that only means something inside that platform (Antigravity's `inherit` / `flash`), while a CLI run needs a real model slug.
- An entry that only has `cli` is a **runner-only entry**. It is not "incomplete" for runner use. If the user later chats on that platform, normal first-run setup fills `workflow` / `models` and keeps `cli` (v2's never-overwrite rule).
- `stallMinutes`: top-level, default 15.
- All writes keep v2's rules: write only the relevant entry/field, never overwrite others, invalid JSON → `config.json.bak` and offer to fix in place.

## 6. Runners

### 6.1 Setup (first `mixed` run on a platform, or when a routed platform has no `cli` entry)

1. Ask which platform runs each role (scout, implementer, reviewer): `native` or another platform's config key.
2. For each routed platform: check the CLI is installed and signed in (§6.4 per-platform check). Missing → stop, show the install/sign-in steps from the README, ask.
3. Read what the platform is actually set to. Never assume its vendor's usual models:
   - Codex: `model`, `model_provider`, `model_reasoning_effort` in `~/.codex/config.toml` (the author's points at MiniMax through a custom provider).
   - Antigravity: `agy models`.
   - Claude Code: the documented aliases (`opus` / `sonnet` / `haiku`).
4. Propose `cli.top` / `cli.mid` / `cli.cheap` (model + effort each) and **ask the user to confirm or correct**.
5. Save `platforms`, `roles` on the orchestrator's entry and `cli` on each runner's entry.

### 6.2 Run folder (scratch)

Each run gets `~/.super-system/runs/<project-name>-<YYYYMMDD-HHMMSS>/`, outside the project:

```
briefs/<task>-<role>-r<round>.md      what the agent was told
logs/<task>-<role>-r<round>.jsonl     the CLI's event stream (stdout)
logs/<task>-<role>-r<round>.err       stderr (permission notices, errors)
results/<task>-<role>-r<round>.json   the agent's structured answer
scratch/<task>-<role>-r<round>/       the agent's own temp files (reviewer notes, test output copies)
```

The orchestrator never writes run artifacts into the project. The folder is kept after the run (it is the evidence for the report); the end-of-run report gives its path. Cleanup is the user's call.

### 6.3 Briefs and role files

New files `references/roles/scout.md`, `references/roles/implementer.md`, `references/roles/reviewer.md`. Each holds: what the role does and must not do, the Conduct rules (v2 SKILL.md "Conduct", restated for a subagent), the result format, and "never dispatch other agents, never run approval gates, never start an orchestration workflow". Reviewer role also: review the real project folder; write only into the given scratch folder; never edit project files; run the tests; apply the quality lenses given in the brief.

A brief = the role file's text + the task: goal, files allowed to change, interface produced/consumed, test command, quality lenses (copied from the active track file), scratch folder path, result file path. Briefs and role files **never contain the skill's trigger words** (`super-system`, `supersystem`, `/super-system`), so an outside agent that has the skill installed can't start the main flow. `tests/check_skill.py` enforces this for the role files.

The same role files are used for native subagents, so every subagent gets the same rules wherever it runs.

### 6.4 Per-platform runner commands

Recorded in a new reference file (name is the builder's call, e.g. `references/runners.md`), one section per runner platform. Each section: install/sign-in check, the command, how model and effort are set, permissions flag, where the event stream and final answer go, how to resume a conversation, how to pass the result schema. Verified flags (2026-11-09):

**Antigravity — `agy`** (docs: antigravity.google/docs/cli/headless, /docs/cli/reference)
- Check: `agy --version`; signed in = a cached login from one interactive `agy` session (headless without one exits with "authentication required").
- Run from the project folder (no `--cd` flag): `agy -p "<prompt>" --model <slug> --effort <level> --dangerously-skip-permissions --output-format stream-json --json-schema <schema file> --add-dir <scratch>`.
- Final answer: the stream's `result` event (`status`, `response`, `structured_output`, `conversation_id`, `usage`).
- Resume: `--conversation <id>`.
- Watch out: in headless mode, a refused approval is a **soft deny** — the run continues and exits 0, with a notice on stderr. Always read the `.err` log (§7).
- `--print-timeout` stays unset (default `0s` = no limit), per decision 9.

**Codex — `codex exec`** (docs: learn.chatgpt.com non-interactive mode and CLI reference; flags checked against the installed codex-cli 0.166.0)
- Check: `codex --version`; signed in or provider key configured (a test call in the smoke test, §12).
- `codex exec -C <project> -m <model> -c model_reasoning_effort=<level> --dangerously-bypass-approvals-and-sandbox --json --output-schema <schema file> -o <result file> --add-dir <scratch> "<prompt>"` (or `-` to read the prompt from stdin).
- Uses the user's `~/.codex/config.toml`, so custom providers (MiniMax) apply.
- Resume: `codex exec resume <session-id>`.

**Claude Code — `claude -p`**: the builder verifies the current flags with `claude --help` (model, effort, skip-permissions, stream-json output, JSON schema, resume) and records them the same way.

**Any other platform:** ask the user for the headless command and its model, effort, permission and output flags; save it as that platform's runner entry. If there is no headless mode, the role can't be routed there; say so.

### 6.5 Permissions

Outside agents always run with the platform's skip-all-permissions flag (decision 2). The user doesn't set anything by hand. README states the cost plainly: those agents can run any command on the machine without asking.

## 7. Deciding an agent is done (decision 1)

After a run's process ends, the orchestrator checks all of these; any failure means "not done" and is handled as a blocker (§10) or a review fail:

1. Process exit code and the CLI's status field (`agy`: `status` = `SUCCESS`; Codex: a `turn.completed` event, no `turn.failed` / `error`).
2. `.err` log: no soft-deny / permission-refused notices, no quota or auth errors.
3. The result file exists and matches the role's schema.
4. **The agent's own answer**: implementer `status` is `done` (not `blocked` / `failed`); reviewer `verdict` is `pass` or `fail` with findings.
5. Files: the implementer changed only the files its task allows (compare `git status` / `git diff --name-only` before and after; with concurrency, compare against the union of running tasks' allowed files and attribute by task). The reviewer changed **none of the reviewed task's files** (hash them before and after the review) and nothing else in the project.

### Result schemas

New files `references/schemas/implementer.json`, `reviewer.json`, `scout.json` (JSON Schema; passed to `--json-schema` / `--output-schema`; native subagents are told to return the same JSON).
- implementer: `status` (`done` | `blocked` | `failed`), `summary`, `files_changed[]`, `tests_run` (command + result), `blocker` (question + what was tried; required when blocked).
- reviewer: `verdict` (`pass` | `fail`), `tests_run`, `findings[]` (`file`, `line`, `severity`, `root_cause`, `fix_instruction`), `not_checked[]`.
- scout: `findings[]` (claim + evidence `file:line` or command output), `open_questions[]`, `not_checked[]`.

## 8. Loops and caps (decision 6; native too)

Per task: implement → review → (fail) implementer fixes using the findings → review … at most **3 review rounds**. Fix rounds resume the implementer's own conversation (`agy --conversation`, `codex exec resume`) so it doesn't re-read everything; the reviewer is always a fresh run.

After every task has passed its reviews (or hit its cap), the orchestrator runs the **final audit** once (decision 11). If it fails, its findings become new briefs for the affected tasks, which go through implement → review again (each with a fresh 3-round budget), then the final audit runs again. At most **2 final-audit rounds**.

When a cap is reached: stop that loop, and report to the user the open deficiencies (each with file, what's wrong, the evidence, what was tried) and a recommendation. The user decides: another round, or pass as is. A deficiency the user passes is listed in the end-of-run report as **accepted by the user**; the Definition of done treats it as closed only with that label.

## 9. Concurrency (decision 8; native too)

- The Gate 2 plan lists, for each task, the files it may change.
- Gate 2 asks: run subagents concurrently or one at a time? Default proposal: one at a time.
- Concurrent mode: tasks run together only when their file sets don't overlap; overlapping tasks run in plan order. The plan shows which tasks would run together.
- The orchestrator also names shared runtime resources that could collide (dev-server port, test database) at Gate 2; tasks that share one run one at a time unless the user says otherwise.
- A reviewer may run while another task's implementer is still working. The reviewer's "changed nothing" check is limited to its own task's files (§7 item 5), and its tests are the ones its brief names, not the whole suite. The full suite runs in the final audit, after all work is done.

## 10. Long runs, stalls, blockers, quota (decisions 7, 9, 12)

- Every outside run starts in the background with no time limit, stdout to the `.jsonl` log and stderr to the `.err` log.
- **Stall check:** if a running agent's logs haven't grown for `stallMinutes` (default 15), the orchestrator reads the last events, checks the process is alive, and reports to the user: which agent, how long since its last output, what it was last doing, and a recommendation (wait longer, or stop and retry). It never kills or retries on its own.
- How to wait without busy-polling is platform-specific and goes in `platforms.md` (Claude Code: background shell job, which notifies on exit, plus a log-watching monitor for the stall check).
- **Blockers** (implementer `blocked`, missing/signed-out CLI, permission refusal, schema-invalid answer, quota or rate-limit error, stall, cap reached): stop the affected work, keep unaffected concurrent work running, and ask the user — what happened, what's left, a recommendation. Never do the work itself, never switch the role to native, without the user's answer.

## 11. Status line and report

- Status line gains `platforms`: `· platforms: native`, or `· platforms: mixed (scout: native · implementer: antigravity/<model>·<effort> · reviewer: codex/<model>·<effort>)`. Showing the resolved model lets the user catch a wrong model every run.
- End-of-run report gains: the run folder path; per task, rounds used and which platform/model ran each role; any accepted-by-user deficiencies; any stall/blocker events and what the user chose.

## 12. Smoke test (part of this job, before calling it done)

On a throwaway git repo outside the project: one `agy` implementer run that edits a file and returns schema-valid JSON, and one `codex exec` reviewer run that reads it, writes only to its scratch folder and returns schema-valid JSON. Prerequisite the user does by hand: install `agy` (official installer from antigravity.google) and sign in once interactively. Report the commands and outputs.

## 13. Files touched

- `skills/super-system/SKILL.md`: Startup (platform mode in settings/overrides/status line), Roles (routing pointer), Gate 2 (concurrency question), caps + stall + blocker rule, Definition of done ("accepted by the user"). Must stay ≤ 8192 bytes: move detail into references. Which v2 text moves out is the builder's call, as long as every rule is still stated exactly once and SKILL.md points to where it went.
- `references/platforms.md`: runner `cli` slot notes per platform, how to wait/watch on each orchestrator platform.
- New: runner commands reference, `references/roles/*.md`, `references/schemas/*.json`.
- `references/flows/build.md` (step 7 concurrency text is replaced by the Gate 2 question), `change.md` / `fix.md` (inherit), `review.md` (scouts may be routed).
- `tests/check_skill.py`: required phrases for the new rules; role files contain no trigger words; schema files are valid JSON; references resolve; model names still only in `platforms.md` (and the runner reference, if it names models — builder's call to allow it there or keep model names out).
- `README.md`: platform mode, `mixed` setup example, installing/signing in to `agy` and Codex, the permissions warning, the run folder.

## 14. Migration of the author's setup

After the build: set `claude-code` → `platforms: mixed`, `roles: implementer → antigravity, reviewer → codex`, scout as the author chooses (open: Codex or `agy`); fill `antigravity.cli` from `agy models` and `codex.cli` from `~/.codex/config.toml`, each confirmed by the author before writing. Reinstall with `npx skills update super-system -g` after pushing (push needs the author's go-ahead).

## 15. Builder-check answers

**Tools a runner lacks (user decided: check at setup).** Setup (§6.1) also asks, per runner platform, whether its CLI has a browser it can drive and SuperDesign. Saved on the runner's entry as `cli.tools: ["browser", "superdesign"]` (whatever it has). At dispatch, a step that needs a tool the runner lacks — Gate 1 prototype drafts and uploads (SuperDesign), UI reviewer lenses that need a real browser (responsive widths, console, focus, CLS), `inspect` crawling (browser) — goes to a native subagent for that step in this run, and the status line says so (e.g. `reviewer: codex/<model> (browser checks: native)`). The runner still does the parts it can (code review, tests); the orchestrator's final audit covers the browser checks as v2 already requires. This is a routing rule, not a silent fallback: it's decided at setup, shown every run, and listed in the report.

**Stall check on native subagents (user decided: best effort).** Caps (§8) and the concurrency question (§9) apply to native subagents in full. The stall check runs on native subagents only where the platform shows progress the orchestrator can watch; where it can't, the end-of-run report says the stall check wasn't available for those subagents (Safeguard 2: never claim a check that didn't run).

**Which orchestrators support `mixed` (my call).** Claude Code is the verified orchestrator: background shell jobs that notify on exit, plus a log watch for the stall check. On any other orchestrator platform, `mixed` is allowed only if it can run a shell command in the background and later read its logs; platforms.md marks those as "not verified". If the platform can't, the orchestrator says `mixed` isn't supported there and runs `native`, after telling the user.

**Slot agent names (my call).** Keep the file names `super-system-top` / `-mid` / `-cheap` (renaming would force a migration of users' installed agent files for little gain: the name isn't put in the subagent's prompt). Change only their one instruction line so it has no trigger word: "You are a subagent. Follow the role file and task in your prompt exactly." Setup rewrites existing slot agent files with the new line the next time it touches them, after asking, as v2 already does.

## 16. Left to the builder

- File names for the runner reference; exact wording of role files.
- Which v2 SKILL.md text moves to references to stay under budget.
- Exact `claude -p` flags (verify locally).
- Exact JSON Schema shapes beyond the fields in §7.
- How "process alive" is checked on each OS.
