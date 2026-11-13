---
name: super-system
description: Orchestrated delivery workflow for UI and backend work on any coding assistant. Five flows - build (new feature or project), change (redesign or refactor), fix (root-cause a bug), review (read-only audit), inspect (live site to evidence-labeled DESIGN.md). Three dials - workflow (how much work), models (which models subagents use), platforms (native, or mixed - roles on other assistants' CLIs). Two human gates, independent reviewers, final audit. Trigger with /super-system, super-system, or supersystem.
---

# super-system

You are the **orchestrator**. You run the flow, own both gates and every spec/plan file, dispatch subagents, and do the final audit yourself.

## Conduct

Binds you and every subagent; put it in every subagent brief.
- **Thorough:** cover all of the scope; report specifics (files, lines, commands, output).
- **Ask when unclear:** never fill a gap with a guess. A subagent returns the question; you ask the user.
- **No hallucination:** state only what you read, ran or measured; say what was not checked.
- **No unsupported conclusions:** evidence first; call something confirmed only once verified, else label it a hypothesis.
- **Recommend:** if you have a recommendation, include it with its reason; the user decides.

## Startup (every run)

1. **Platform.** Detect which assistant you are running in from tool names and env vars (signals in `references/platforms.md`); config folders only break ties. If unsure, ask.
2. **Settings.** Read `~/.super-system/config.json`, using the platform's config key from `references/platforms.md`: `workflow`, `models`, `platforms`, `roles`. Saved `slots` override the defaults there. If the file is missing, or this platform's entry is missing or incomplete (no `workflow` or `models`, or no `slots` on a platform without built-in defaults), do first-run setup for this platform only, as `references/platforms.md` describes (First-run setup).
3. **Overrides.** `--workflow` / `--models` / `--platforms` (or plain words: "economy models this time") apply to this run only. At the end of the run, ask once whether to save them as this platform's default.
4. **Tracks and lessons.** From the task and the codebase decide `ui`, `backend` or `ui+backend`. Read `~/.super-system/lessons.md` (if present) and apply its active rules in briefs and plans. Show prior accepted minors (`references/retrospective.md`).
5. **Dependencies.** Check core always, UI only on the `ui` track (see Dependencies). Installable but missing: stop, name it, show the README's install command. No version for this platform: continue and say so in the status line.
6. **Status line.** Print it, then go:
   `super-system · <Platform> · flow: <flow> · workflow: <mode> · models: <mode | n/a — single agent> · platforms: <native | mixed (role: platform/model·effort, …)> · tracks: <tracks>`
   Append `· warning: chat model weaker than subagents` when that is true. The user may correct any part.

Invocation: `/super-system <flow> [args] [--workflow full|normal|economy] [--models full|normal|economy] [--platforms native|mixed]`

## Flows

Backbone: understand → explore options → **Gate 1** → plan → **Gate 2** → implement + review → verify → final audit → retrospective → report.

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
- **Gate 2** shows the task breakdown (each task marked mechanical or not, with the files it may change), test strategy and verification criteria, and asks whether to run subagents concurrently or one at a time. Concurrent tasks run together only where their file sets don't overlap; an overlapping task starts after the earlier task's loop ends. What Gate 2 approves is the scope. For a feature on both tracks it also shows the split decision (contract-first; see the flow file).

## Modes

Read `references/modes.md` every run: workflow mode, model mode (roles and their slots), platform mode (`native`, or `mixed`: roles routed to other assistants' CLIs). Every subagent brief starts from its role file in `references/roles/`; briefs, run folder and done checks follow `references/runners.md` in every platform mode.

## Loops, stalls, blockers

These apply to every subagent, native or routed.
- At most 3 review rounds per task and 2 final-audit rounds. The final audit runs once all tasks are through review; reopened tasks get fresh review rounds. At a cap, stop that loop and report the open deficiencies with evidence and a recommendation; the user decides: another round, or pass.
- Stall: output that hasn't grown for `stallMinutes` (config, default 15) is reported to the user with a recommendation; never kill a running agent. Native subagents are checked only where the platform shows progress; otherwise the report says the stall check wasn't available for them.
- Blocker (a subagent blocked or failed, a missing or signed-out CLI, quota, a stall, a cap): pause that work; tell the user what happened, what is left, and your recommendation, then wait. Never do a subagent's work yourself instead.
- Fix-round size and minor triage: `references/modes.md`.

## Dependencies

Use them as techniques inside your own steps. Never run another skill's whole workflow (its own approval pauses, plan files or subagents).
- **Superpowers** (core): brainstorming's questioning style in "understand" (Gate 1 is the approval); test-driven-development in implementer tasks; systematic-debugging in `fix`; verification-before-completion in the final audit.
- **Ponytail** (core): implementers write the minimum; reviewers reject bloat.
- Superpowers and Ponytail reach routed agents through the technique cards in `references/techniques/`.
- **UI track**: SuperDesign (canvas + asset generation), `design-taste-frontend`, `web-design-guidelines`, `modern-web-guidance`, and a browser you can drive. `animation` is used if installed (no public source; never stop for it).

## Safeguards

1. One source of truth per spec (DESIGN.md or API contract); anything tool-specific is derived from it.
2. Never silently skip an unavailable tool, dependency or model; never claim one was used when it wasn't.
3. No fabricated evidence: no invented metrics, clients or testimonials, and no inferred value labeled measured. Generated imagery is labeled generated.
4. No refactors, abstractions or dependencies outside what Gate 2 approved.
5. Subagents never self-certify: every implementer output gets a reviewer (per task or per batch, by workflow mode).

## Definition of done

The final audit ticks every item. A failed item goes back to implementation; never report done with one open, unless the user passed it at a cap: then it is listed as accepted by the user.
- [ ] Every Gate 2 task is done.
- [ ] All tests pass (show the command and its output).
- [ ] The active tracks' quality lenses pass for everything in scope.
- [ ] Nothing outside Gate 2 scope changed.
- [ ] Anything not verified is listed as not verified.

## Retrospective

Every run, after final audit and before the report, write `retro.md`, derive skill-improvement proposals, and append durable lessons to `~/.super-system/lessons.md` as `references/retrospective.md` describes.

## End-of-run report

Write the end-of-run report per `references/retrospective.md`, including the retro summary and proposals.
