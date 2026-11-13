# super-system v3: lessons from the Tasrock audit-fix runs

Source: two full fix runs on the Tasrock project (2026-11-12/13; mixed platforms: Codex scouts/reviewers, Antigravity implementers). Evidence lives in `~/.super-system/runs/todo-list-app-20261112-175719/notes/00-index.md`. This spec turns what went wrong into skill changes. All five parts were approved by the user.

## What went wrong (evidence)

| Problem | Seen | Cost |
|---|---|---|
| Implementers wrote regression tests that already passed on the base code (no real red step) | T3 r1 (I32, AI tools) | 1 extra review round |
| Unrequested changes / bloat: a freeze added where not asked, broad `except Exception`, unused imports, a known-failing test rewritten to pass, a shared helper widened for every caller | T4 r1, T1 r1, T4 r2, T2 r2 | 3–4 extra rounds |
| A fix round silently dropped an existing permission check (critical regression) | T3 r3 | round cap + 1 extra round |
| Insecure compare (`secrets.compare_digest` on non-ASCII str → 500) | T1 r2 | 1 extra round |
| Implementers ran tests with a bare `python` instead of the project's interpreter | T3, T4 | unverified claims |
| `files_changed` did not match the real diff | T3 r3 | manual check |
| Antigravity run status ERROR although the structured answer was complete ("root agent idle; waiting for N background task(s)") | almost every run | manual judgement each time |
| A Codex reviewer ended its turn after one sentence; the result file existed but had no verdict | T4 r1 | a review counted as done by mistake |
| The orchestrator edited a runner script while a process was executing it (bash reads scripts incrementally) → syntax error after the run | T2 review | lost the post-run hash check |
| Shell heredocs broke on quoting (Windows Git Bash) | several | retries |
| More than 3 concurrent MiniMax runs → 429; 5 concurrent for an hour exhausted the 5-hour window | audit run | hours lost |
| Skills (ponytail, TDD, debugging, security) never reached the routed agents: briefs named none, and Antigravity had none installed | whole run | most of the rejections above |
| The skill itself was installed where Codex and Antigravity load skills (trigger risk) | setup | risk |
| Many frontend/backend seam bugs in the audited project (form not sending fields, status vocabulary drift, response-shape mismatch) | audit | motivates the contract-first split |

## Part 1 — Technique cards (skills delivered inside the brief)

New folder `references/techniques/`, one short card per technique (≤ 60 lines each, plain imperative rules, a `Source:` line naming the skill it condenses). Cards are pasted into briefs; they never depend on a skill being installed in the runner.

| Card | For | Content |
|---|---|---|
| `ponytail.md` | implementer, reviewer | The ladder (does it need to exist → already in the codebase → stdlib → native platform → installed dependency → one line → minimum code); no unrequested abstractions, refactors, dependencies or behaviour changes; fix the root cause once in the shared place; fewest files; delete over add; remove anything you added that ends up unused; never edit or weaken a test to make it pass or to hide a bug; leave known-failing tests exactly as they are; reviewer side: reject bloat and unrequested changes as findings. |
| `tdd.md` | implementer, reviewer | Red → green → refactor. For every new test: run it before the fix and keep the failing output (the failure must be the stated cause, not an import or fixture error); a test that passes on the base proves nothing and must be rewritten; then the minimal fix; then the same command green. Reviewer: verify red on the base (scratch copy of base files) and green now. |
| `debugging.md` | fix flow (scout, implementer, reviewer) | Reproduce first; one hypothesis at a time with evidence; trace to where the bad value or missing check originates; grep every caller and sibling path (REST, MCP/CLI tools, services, jobs); fix where all callers route; no symptom patches. |
| `verification.md` | every role | Before claiming done: run the exact command the brief gives with the interpreter/toolchain the brief names (never a bare `python`/`node` when a path is given); read the output; `files_changed` = `git diff --name-only <base>` + new untracked files, exactly; diff the changed files against the base and list every removed line that was a permission, validation, visibility or error check, with the reason it is safe (none may be dropped silently); never say "should pass". |
| `security-backend.md` | backend track | Authorization on every changed route/tool through one shared helper (same rule for REST and any tool layer); membership + role; deny-by-default; input validation at trust boundaries; secrets from env only, no defaults in code; constant-time compares on bytes (encode first); tokens/keys in headers, never query strings; no broad `except` that turns real bugs into auth errors; parameterized queries; no secrets or personal data in logs; tests for both a denied and an allowed actor. |
| `ui-quality.md` | ui track | Condensed from design-taste-frontend, web-design-guidelines and modern-web-guidance: follow the project's design system/tokens; semantic HTML; keyboard reachable, visible focus; contrast; responsive at 375/768/1280; loading, empty and error states; no layout shift; copy rules (plain verbs, sentence case); browser console clean; no new UI dependencies without approval. |
| `contract.md` | both tracks of a split feature | What the contract file holds (routes, request/response bodies, status codes and error shapes, shared type names and their file); backend must satisfy it exactly; frontend codes only against it (mock the API until integration); any change to the contract goes back to the orchestrator, never decided by one side. |

Which cards a brief carries:
- implementer: ponytail, tdd, verification (+ debugging in `fix`; + security-backend on backend; + ui-quality on ui; + contract for a split feature).
- reviewer: the same cards, as review criteria.
- scout: verification (evidence only), + debugging in `fix`.

Where the runner has the matching skill installed (Part 6), the card may name it as further reading. Never name the orchestrator's own skill.

## Part 2 — Red evidence and stronger done checks

- `schemas/implementer.json`: new required property `red_evidence`: array of `{ "test": string, "command": string, "failing_output": string }` (output excerpt ≤ 2,000 characters showing the failure). It may be empty only together with `no_test_reason` (string, new optional property) when the brief says the task needs no test (docs/config). Keep `additionalProperties: false`.
- `schemas/reviewer.json`: new optional property `regression_checks`: array of `{ "test": string, "fails_on_base": boolean, "passes_now": boolean, "how": string }`.
- `roles/implementer.md` and `roles/reviewer.md`: describe the new fields; implementer must list removed checks (verification card); reviewer must fill `regression_checks` in the `fix` flow.
- `runners.md` "Is it done?":
  - implementer: `red_evidence` present and non-empty (or `no_test_reason` allowed by the brief); `files_changed` equals the real diff (mismatch → fix round, not a blocker).
  - reviewer: done only when the answer parses as JSON and has `verdict`; a missing verdict (even with a non-empty file) → rerun fresh once, then a blocker.
  - Antigravity: status `ERROR` with a complete `structured_output` and stderr "root agent idle; waiting for N background task(s) to finish" is a warning, not a failure; the reviewer must re-run the tests. Any other `ERROR` is a blocker.

## Part 3 — Run hygiene (runners.md, new section "Run scripts")

- Copy the runner/queue scripts into the run folder at the start of a run; never edit a script while any process is executing it (bash reads scripts incrementally); make a new versioned copy instead.
- Write briefs and scripts with the file-writing tool, not shell heredocs (quoting breaks, especially on Windows).
- Per-runner concurrency cap `cli.concurrency` (default 3; MiniMax-backed Codex: 3). Queue runs above the cap. On a 429: wait 300 s, retry at most 3 times; repeated 429s across runs → stop and report (the window may be exhausted).
- Results are judged by content (schema-valid JSON with the role's required fields), never by file size or exit code alone.

## Part 4 — Per-track routing and contract-first split

- `modes.md` (Platform mode) and config: a `roles` value may be a string (all tracks) or an object keyed by track, e.g. `"implementer": {"backend": "antigravity", "ui": "antigravity"}`, `"reviewer": {"backend": "codex", "ui": "codex"}`. Missing track → the string/default. UI tasks need a runner whose `cli.tools` includes `browser` (else that check runs native, as today).
- Gate 2 (SKILL.md "Gates", flows `build`/`change`/`fix`, `track-ui.md`, `track-backend.md`): for each feature touching both tracks, decide split or not and show it:
  1. **Contract** — written by the orchestrator before Gate 2 approval: `docs/design/api/<feature>.md` (routes, request/response, status codes, error shapes, shared type names + file). Frozen at Gate 2.
  2. **Backend task** — owns backend files and any shared type definitions the contract assigns to it.
  3. **Frontend task** — owns UI files; codes against the contract, mocks the API.
  2 and 3 run concurrently (their file sets don't overlap).
  4. **Integration check** — after both merge: a reviewer with a browser runs the real UI against the real API plus the end-to-end tests; mismatches go back as fix rounds.
  Don't split when the UI part is tiny or the API can't be known up front: then backend first, frontend after.

## Part 5 — Retrospective and skill-improvement recommendations (SKILL.md)

- Startup: read `~/.super-system/lessons.md` (if present) and apply its active rules in briefs and plans.
- New section "Retrospective" (every run, after the final audit, before the report): write `retro.md` in the run folder with: rounds per task and why each review failed (grouped by root cause), cap hits, scope violations and silently removed checks, blockers and stalls, runner/tool failures, quota events, wall-clock per phase. From it, derive concrete improvement proposals for the skill: file, change, evidence from this run, expected effect. Append durable lessons to `~/.super-system/lessons.md` (one line each: date, lesson, evidence pointer; no duplicates).
- End-of-run report: add the retro summary and the proposals; ask the user which proposals to apply. Never edit the skill without the user's approval.

## Part 6 — Runner skill setup (platforms.md, runners.md "Setup")

- Skills each runner should have installed (role-dependent): ponytail, test-driven-development, systematic-debugging, verification-before-completion, security-and-hardening; UI: web-design-guidelines, modern-web-guidance, design-taste-frontend. Setup checks and offers to install them (copy from the user's installed copies); the cards (Part 1) remain the source of truth.
- The orchestrator's own skill must NOT be installed where routed runners load skills (Codex: `~/.agents/skills`, project `.agents/skills`; Antigravity: `~/.gemini/skills`, `~/.gemini/config/skills`). Setup checks and recommends moving it.

## Also

- `SKILL.md` "Dependencies": say that Superpowers/Ponytail reach routed agents through the technique cards.
- `README.md`: a short "What's new in v3" listing Parts 1–6.
- `tests/check_skill.py`: extend so it checks the new files exist and are referenced (cards, schema fields) and still passes.
- Keep every existing rule unless a part above changes it; keep the trigger-word rule (briefs never instruct an agent to load the orchestrator's skill).
