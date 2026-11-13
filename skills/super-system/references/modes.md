# Modes

Three dials, each saved per platform in `~/.super-system/config.json` and each overridable for one run (Startup in SKILL.md): workflow mode (how much work), model mode (which slot each role uses), platform mode (where each role runs).

## Workflow mode

| | full | normal | economy |
|---|---|---|---|
| Options explored | 3 per screen/component | 2 for main, 1 for the rest | 1, main only |
| Review | after every task | after every task | once per batch of related tasks |
| Final audit | every route, viewport and file in scope | changed routes, all viewports | changed routes, desktop + mobile |
| Backend verify | full suite + integration + security pass | full suite + integration | tests touching changed code, full suite once at the end |

Main screens/components are the ones listed at Gate 1.

## Model mode

- **orchestrator**: the model the user is chatting with. Model mode never changes it.
- **scout**: read-only work: reading code, crawling a site, gathering evidence.
- **implementer**: writes code, prototype drafts and tests.
- **reviewer**: checks one task (or one batch): runs the tests, reads the diff, applies the track's quality lenses. Rejects with root-cause instructions; loops until it passes or reaches the round cap in SKILL.md.

A reviewer's slot is never below the slot of the implementer it checks.

| Role | full | normal | economy |
|---|---|---|---|
| scout | top | mid | cheap |
| implementer | top | mid | mid (cheap for mechanical tasks) |
| reviewer | top | mid | mid |

Mechanical task = rename, moving code without changing it, boilerplate that copies an existing pattern exactly, config value edits.

Slot defaults per platform and how to spawn a subagent with a model and effort: `references/platforms.md`. A platform's own role table there overrides this one for its own subagents. If the platform has no subagents or no per-subagent model choice, run the roles one after another in this session; review stays a separate pass that re-reads the diff fresh.

## Platform mode

- **`native`** (default): every role runs as a subagent of the platform you are running on.
- **`mixed`**: each role runs on the platform named in this platform's `roles` map (for example `"roles": {"scout": "native", "implementer": "antigravity", "reviewer": "codex"}`). A `roles` value may also be an object keyed by track (for example `"implementer": {"backend": "antigravity", "ui": "antigravity"}`, `"reviewer": {"backend": "codex", "ui": "codex"}`). A missing role or missing track falls back to the string/default (`native`). UI tasks need a runner whose `cli.tools` includes `browser` (otherwise browser checks run `native`).

For a role routed to another platform, use the generic role table above (not this platform's own table), then take that slot from the runner's `cli` slots (`cli.top`, `cli.mid`, `cli.cheap`, each a model and an effort). Slots are compared as slots: a routed reviewer is still never below its implementer's slot.

A **runner-only entry** is a platform entry that has only `cli`. It is complete for runner use. If the user later chats on that platform, first-run setup fills `workflow` and `models` and keeps `cli`.

Where `mixed` works: it is verified with Claude Code as the orchestrator. Another orchestrator platform can use it only if it can start a shell command in the background and read its logs later; `references/platforms.md` marks those as not verified. If it can't, tell the user `mixed` isn't supported here and run `native`.

Setup, commands, briefs and done checks for routed roles: `references/runners.md`.
