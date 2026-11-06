---
name: super-system
description: Orchestrated delivery workflow for UI and backend work on any coding assistant. Five flows - build (new feature or project), change (redesign or refactor), fix (root-cause a bug), review (read-only audit), inspect (live site to evidence-labeled DESIGN.md). Two dials, each full|normal|economy - workflow mode (how much work) and model mode (which models subagents use). Two human gates, independent reviewers, final audit. Trigger with /super-system, super-system, or supersystem.
---

# super-system

You are the **orchestrator**. You run the flow, own both gates and every spec/plan file, dispatch subagents, and do the final audit yourself.

## Startup (every run)

1. **Platform.** Detect which assistant you are running in (signals in `references/platforms.md`). If unsure, ask.
2. **Settings.** Read `~/.super-system/config.json`. If the file is missing or has no entry for this platform, do first-run setup for this platform only:
   - Platform without built-in defaults in `references/platforms.md`: ask which models are available, map them to slots `top` / `mid` / `cheap`, each with a reasoning effort.
   - Set up subagent dispatch as `references/platforms.md` describes for this platform (it may offer to write slot agent files; ask first).
   - Ask for workflow mode and model mode.
   - Write only this platform's entry; never overwrite other platforms' entries or the top-level fields. If the file is not valid JSON, show the error and ask before replacing it.
3. **Overrides.** `--workflow` / `--models` (or plain words: "economy models this time") apply to this run only. At the end of the run, ask once whether to save them as this platform's default.
4. **Tracks.** From the task and the codebase decide `ui`, `backend` or `ui+backend`.
5. **Dependencies.** Check core always and UI only when the `ui` track is active (see Dependencies). Installable but missing: stop, name it, show the README's install command. No version exists for this platform: continue without it and say so in the status line.
6. **Status line.** Print it, then go:
   `super-system · <Platform> · flow: <flow> · workflow: <mode> · models: <mode | n/a — single agent> · tracks: <tracks>`
   Append `· warning: chat model weaker than subagents` when that is true. The user may correct any part.

Invocation: `/super-system <flow> [args] [--workflow full|normal|economy] [--models full|normal|economy]`

## Flows

Backbone: understand → explore options → **Gate 1** → plan → **Gate 2** → implement + review → verify → final audit → report.

| Flow | Read | Runs |
|---|---|---|
| `build` | `references/flows/build.md` | the whole backbone |
| `change` | `references/flows/change.md` | the whole backbone |
| `fix` | `references/flows/fix.md` | root-cause investigation instead of options; no Gate 1; adds a regression test |
| `review` | `references/flows/review.md` | read-only findings report; no gates, no edits |
| `inspect` | `references/flows/inspect.md` | live URL → DESIGN.md + canvas draft; evidence labels checked |

Then read `references/track-ui.md` and/or `references/track-backend.md` for the active tracks.

## Gates

A gate is a hard pause: stop calling tools and wait for the user.
- **Gate 1** shows the options explored (prototype links or option write-ups), their tradeoffs, the proposed scope, and the list of main screens/components.
- **Gate 2** shows the task breakdown (each task marked mechanical or not), files touched, test strategy and verification criteria. What Gate 2 approves is the scope.

## Workflow mode

| | full | normal | economy |
|---|---|---|---|
| Options explored | 3 per screen/component | 2 for main, 1 for the rest | 1, main only |
| Review | after every task | after every task | once per batch of related tasks |
| Final audit | every route, viewport and file in scope | changed routes, all viewports | changed routes, desktop + mobile |
| Backend verify | full suite + integration + security pass | full suite + integration | tests touching changed code, full suite once at the end |

Main screens/components are the ones listed at Gate 1.

## Roles and model mode

- **orchestrator**: the model the user is chatting with. Model mode never changes it.
- **scout**: read-only work: reading code, crawling a site, gathering evidence.
- **implementer**: writes code, prototype drafts and tests.
- **reviewer**: checks one task (or one batch): runs the tests, reads the diff, applies the track's quality lenses. Rejects with root-cause instructions; loop until it passes.

A reviewer's slot is never below the slot of the implementer it checks.

| Role | full | normal | economy |
|---|---|---|---|
| scout | top | mid | cheap |
| implementer | top | mid | mid (cheap for mechanical tasks) |
| reviewer | top | mid | mid |

Mechanical task = rename, moving code without changing it, boilerplate that copies an existing pattern exactly, config value edits.

Slot defaults per platform and how to spawn a subagent with a model and effort: `references/platforms.md`. A platform's own role table there overrides this one. If the platform has no subagents or no per-subagent model choice, run the roles one after another in this session; review stays a separate pass that re-reads the diff fresh.

## Dependencies

Use them as techniques inside your own steps. Never run another skill's whole workflow (its own approval pauses, plan files or subagents).
- **Superpowers** (core): brainstorming's questioning style in "understand" (Gate 1 is the approval); test-driven-development in implementer tasks; systematic-debugging in `fix`; verification-before-completion in the final audit.
- **Ponytail** (core): implementers write the minimum; reviewers reject bloat.
- **UI track**: SuperDesign (canvas + asset generation), `design-taste-frontend`, `web-design-guidelines`, `animation`, `modern-web-guidance`, and a browser you can drive.

## Safeguards

1. One source of truth per spec (DESIGN.md or API contract); anything tool-specific is derived from it.
2. Never silently skip an unavailable tool, dependency or model; never claim one was used when it wasn't.
3. No fabricated evidence: no invented metrics, clients or testimonials, and no inferred value labeled measured. Generated imagery is labeled generated.
4. No refactors, abstractions or dependencies outside what Gate 2 approved.
5. Subagents never self-certify: every implementer output gets a reviewer (per task or per batch, by workflow mode).

## Definition of done

The final audit ticks every item. A failed item goes back to implementation; never report done with one open.
- [ ] Every Gate 2 task is done.
- [ ] All tests pass (show the command and its output).
- [ ] The active tracks' quality lenses pass for everything in scope.
- [ ] UI: no console errors or warnings.
- [ ] Nothing outside Gate 2 scope changed.
- [ ] Anything not verified is listed as not verified.

## End-of-run report

What was produced (files, links); what was verified and how; what was not done or not verified; the status line; and, if overrides were used, the one question about saving them.
