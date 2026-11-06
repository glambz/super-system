# Super-System v2 — Design

Date: 2026-11-06
Source being replaced: `C:\Users\indocyber\.agents\skills\super-system\` (SKILL.md 32KB + `scripts/contrast-check.py`)
Target: this folder (`C:\Users\indocyber\Desktop\agent\super-system`), which becomes a public git repo installable with `npx skills`.

## 1. Intent

Today super-system is one person's web-design workflow: it has their file paths, SuperDesign project IDs, brand palette and two hardcoded subagent models baked in, and it only covers UI work.

v2 makes it a general skill **any developer can install** on **any code assistant that supports Agent Skills** (Claude Code, Antigravity, Cursor, OpenCode, Oh My Pi, Codex, Kilo Code, and others), covering **backend and non-UI work as well as UI**, with the cost controllable by two dials.

The parts that made v1 good stay: two human gates, an implementer never self-certifying, a final audit by the lead agent, evidence-labeled design specs, zero fabricated evidence, strict scope.

## 2. Goals, non-goals, anti-goals

Goals
- One skill, installed once globally, works on all listed platforms.
- Five flows: `build`, `change`, `fix`, `review`, `inspect`.
- Two independent dials, each `full | normal | economy`: **workflow mode** (how much work) and **model mode** (which models subagents use).
- Choices are saved per platform and not asked again unless the user overrides.
- UI work and backend work each get their own matching steps; full-stack tasks get both.
- SKILL.md small enough to load every trigger cheaply; detail loaded only when the run needs it.

Non-goals
- Our own installer. `npx skills` does installation.
- Choosing or switching the model the user chats with. That is always the user's choice.
- Shipping the dependencies inside this repo. They are installed separately and documented.

Anti-goals (would be a failure even if it "works")
- Any personal path, project ID, brand palette or name of the original author left in the skill.
- A rule stated more than once across SKILL.md and references.
- Silently working around a missing dependency or tool, or claiming a model/tool was used when it wasn't.
- A reviewer subagent running on a weaker model than the implementer it checks.
- UI-only steps (prototypes, browser QA, assets) forced onto a backend-only task.

## 3. Repo layout

```
super-system/                      (repo root)
  README.md                        install, dependencies, usage, config
  LICENSE                          MIT
  skills/super-system/
    SKILL.md                       core: ≤ ~8KB
    references/
      flows/build.md
      flows/change.md
      flows/fix.md
      flows/review.md
      flows/inspect.md
      track-ui.md                  UI steps, quality lenses, anti-slop defaults
      track-backend.md             backend steps, quality lenses
      platforms.md                 per-platform model defaults + how to spawn subagents with a model/effort
      design-md-template.md        canonical DESIGN.md template (moved verbatim from v1, minus personal bits)
    scripts/
      contrast-check.py
  docs/superpowers/specs/          this document
```

Builder must verify that `npx skills add <owner>/super-system` discovers a skill at `skills/super-system/SKILL.md`; if it requires a different layout, use what it requires.

## 4. SKILL.md contents (the always-loaded core)

In this order, each rule stated once:

1. Frontmatter: `name: super-system`, a description that triggers on `/super-system`, "super-system", "supersystem" and names the five flows and that it covers UI and backend.
2. **Startup** (every run):
   1. Detect the platform. If unsure, ask.
   2. Read `~/.super-system/config.json`. If this platform has no entry → first-run setup (§7).
   3. Apply overrides from the invocation (§6).
   4. Decide tracks: UI, backend, or both (§9).
   5. Dependency check for core + the active tracks (§10). Missing → stop and tell the user exactly what to install.
   6. Print one status line, e.g. `super-system · Claude Code · flow: build · workflow: full · models: normal · tracks: ui+backend`.
3. Flow router: which reference file to read for the chosen flow, and which track files.
4. Roles and model-mode rule (§8), pointing to `platforms.md` for the table.
5. Workflow-mode table (§6).
6. Safeguards (§11) — once each.
7. The two gates (§5).
8. Definition of done (§11) and the end-of-run report format.

## 5. Flows and the shared backbone

Backbone: understand → explore options → **Gate 1** → plan → **Gate 2** → implement + review → verify → final audit → report.

| Flow | Purpose | Explore options | Gate 1 | Plan + Gate 2 | Implement + review | Verify + final audit |
|---|---|---|---|---|---|---|
| `build` | New feature or new project (replaces v1 fullflow) | yes | yes | yes | yes | yes |
| `change` | Redesign / refactor existing code (replaces v1 redesign) | yes | yes | yes | yes | yes |
| `fix` | Root-cause a bug and fix it | no — root-cause investigation instead | no | yes (fix plan) | yes | yes + a regression test that fails before the fix |
| `review` | Audit existing code; read-only | no | no | no | no — findings report only | no |
| `inspect` | Live URL → evidence-labeled DESIGN.md + SuperDesign canvas draft | no | no | no | writes DESIGN.md | every token's evidence label checked |

Gates are hard pauses: the agent stops calling tools and waits for the user.
- Gate 1 shows: the options explored (prototype links for UI; option writeups for backend), tradeoffs, proposed scope.
- Gate 2 shows: task breakdown, files touched, test strategy, verification criteria.

Invocation: `/super-system <flow> [args] [--workflow full|normal|economy] [--models full|normal|economy]`. Natural language works too ("use economy models this time").

## 6. Workflow mode (how much work)

| | full | normal | economy |
|---|---|---|---|
| Options explored (UI: prototypes per screen; backend: design options per component) | 3 per screen/component | 2 for main screens/components, 1 for the rest | 1, main screens/components only |
| UI prototype viewports | desktop + mobile | desktop + mobile | desktop + mobile |
| Review | reviewer after every task | reviewer after every task | one reviewer per batch of related tasks |
| Final audit | every route, viewport (1440/768/390) and file in scope | changed routes, all three viewports | changed routes, desktop + mobile |
| Backend verify | full suite + integration + security pass | full suite + integration | tests touching changed code + full suite once at the end |

"Main screens/components" = the orchestrator lists them at Gate 1; the user can change the list.

Overrides via flag or natural language apply **to this run only**. At the end of the run, the skill asks once whether to save the override as this platform's new default.

## 7. Saved settings: `~/.super-system/config.json`

Lives outside the skill folder so reinstall/update never wipes it. Created on first run; never contains secrets.

```json
{
  "platforms": {
    "claude-code": { "workflow": "full", "models": "normal" },
    "antigravity": { "workflow": "full", "models": "economy" },
    "cursor": {
      "workflow": "normal",
      "models": "normal",
      "slots": {
        "top":   { "model": "<user-provided>", "effort": "high" },
        "mid":   { "model": "<user-provided>", "effort": "medium" },
        "cheap": { "model": "<user-provided>", "effort": "medium" }
      }
    }
  },
  "tasteFile": null,
  "designLibrary": null
}
```

- **Known platforms** (Claude Code, Antigravity) have built-in slot defaults in `platforms.md`; `slots` is only written if the user customizes them.
- **Every other platform**: first run asks which models are available, maps them to `top / mid / cheap` (+ reasoning effort), saves them as `slots`, *then* asks for the two modes.
- `tasteFile`: optional path to the user's taste/anti-slop notes. If set, read before any design exploration in any flow.
- `designLibrary`: optional folder of DESIGN.md prior art, consulted during UI exploration in later sessions.

**Where spec files go (decided by the user: project + library).**
- `build` / `change`: the project's own copy is the source of truth, at `docs/design/DESIGN.md` (+ `prototype-<a|b|c>-design.md`) for UI and `docs/design/` (API contract / schema / ADR) for backend *(exact project paths: my call)*. UI designs are also copied to `<designLibrary>/<project-name>/<page-type>/` for lookup in later sessions; the library copy is never edited directly — it is refreshed from the project copy.
- `inspect`: writes to `<designLibrary>/<domain>/<page-type>/DESIGN.md`. If `designLibrary` is null, to `./design-library/<domain>/<page-type>/DESIGN.md` in the current project.
- Existing library entries are updated, never silently erased (keep historical notes and canvas links).

**Template variant.** `inspect` uses the canonical template as-is (`[Measured] / [Observed] / [Inferred]`). DESIGN.md from `build`/`change` uses the same structure with `sourceUrl`/`inspectionDate` replaced by `project`/`date`, and the evidence label `[Decided]` (chosen at Gate 1) alongside `[Inferred]`. *(My call.)*

## 8. Roles and model mode (which models)

- **Orchestrator** = the model the user is chatting with. Always. It explores options with the user, plans, runs both gates, and does the final audit. Model mode never changes it.
- **Scout**: read-only work — reading code, crawling a site, gathering evidence.
- **Implementer**: writes code, authors prototype drafts, writes tests.
- **Reviewer**: checks one implementer's (or one batch's) output: runs tests, reads the diff, checks the track's quality lenses. Can reject with root-cause instructions; loop until it passes.

Hard rule: **reviewer's slot ≥ implementer's slot**.

If the chat model (orchestrator) is weaker than the subagent slots chosen (e.g. chatting on Sonnet with `models: full`), allow it but warn once in the status line. *(My call.)*

Defaults (go in `platforms.md`):

| Role | Claude Code full | normal | economy | Antigravity full | normal | economy |
|---|---|---|---|---|---|---|
| Scout | Opus | Sonnet | Haiku | Argon | Flash | Flash · high |
| Implementer | Opus | Sonnet | Sonnet (Haiku for mechanical tasks) | Argon | Flash | Flash · high |
| Reviewer | Opus | Sonnet | Sonnet | Argon | Argon | Flash · high |

Generic mapping for other platforms (using the user's slots):

| Role | full | normal | economy |
|---|---|---|---|
| Scout | top | mid | cheap |
| Implementer | top | mid | mid (cheap for mechanical tasks) |
| Reviewer | top | mid | mid |

"Mechanical task" = renames, moving code, boilerplate that follows an existing pattern exactly, config edits — defined in SKILL.md as that short list; the orchestrator labels tasks at Gate 2.

**Platforms without subagents, or without per-subagent model choice**: run the same roles one after another in the main session on the user's current model. Say so in the status line (`models: n/a — single agent`). The review step still happens as a separate pass with a fresh read of the diff.

`platforms.md` must give, for each listed platform, how to spawn a subagent with a specific model and effort (or that it can't). Builder researches this from each platform's current docs; don't guess syntax.

## 9. Tracks: UI and backend

The orchestrator decides from the task and the codebase, states it in the status line, and the user can correct it. Full-stack → both.

| Step | UI track (`track-ui.md`) | Backend track (`track-backend.md`) |
|---|---|---|
| Explore options | Prototypes on SuperDesign canvas (desktop 1440×900 + mobile 390×844), with rationale per option | 2–3 API / schema / architecture options with tradeoffs |
| Spec artifact | DESIGN.md (+ per-prototype docs when prototypes exist) | API contract / schema doc / ADR as fits |
| Verify | Real-browser QA at 1440/768/390 | Test suite, contract/integration tests, migrations run against a copy, never prod |
| Quality lenses | Visual fidelity, functional behavior, responsive (touch ≥44px), accessibility (keyboard, focus-visible, contrast ≥4.5/3, reduced motion), technical (console clean, CLS 0) — against Vercel Web Interface Guidelines | Correctness, error handling at boundaries, security (input validation, authz, secrets), performance (N+1, unbounded queries), observability (logs/errors on failure paths) |
| Assets | Generated visuals via SuperDesign (Nano Banana) only when the screen needs them, labeled as generated | none |

`track-ui.md` keeps from v1, generalized: purpose calibration (utility/forms → practical and plain; SaaS/workflows → dense and clear; brand/editorial → expressive), anti-slop defaults (no generic pastel gradients, cookie-cutter 3-card rows, empty 3D blobs, placeholder fluff; don't default to Inter/Roboto/Arial/Open Sans/Helvetica — pick type to match the brand), modern-web defaults (semantic HTML, native `<dialog>`/Popover, container queries, `@starting-style`, `text-wrap`), motion defaults (transform-based, no heavy animation libraries, `prefers-reduced-motion`). The user's `tasteFile` overrides these defaults; it never forbids proposing something new.

Removed from v1 entirely: hazard-orange/clay/obsidian palette, 45° chamfer prescriptions, "Tasrock", the four SuperDesign project UUIDs, the per-screen archetype names (Tactical Split View etc.), "hero stays at top" check. (Those were the original author's taste; they can live in their own `tasteFile`.)

## 10. Dependencies

Required, installed separately, listed in README with install steps per platform:

| Group | Dependency | Needed when |
|---|---|---|
| Core | Superpowers (brainstorming, writing-plans, TDD, systematic debugging) | always |
| Core | Ponytail | always |
| UI | SuperDesign (canvas + asset generation) | UI track |
| UI | `design-taste-frontend` | UI track |
| UI | `web-design-guidelines` (Vercel) | UI track |
| UI | `animation` | UI track |
| UI | `modern-web-guidance` | UI track |
| UI | A browser the agent can drive (e.g. built-in browser, Chrome DevTools MCP, Playwright) | UI track verify/inspect |

Dropped: "Creative Animation Effects" (no known source).

**How dependencies are used (decided by the user).** Super-system owns the backbone, both gates, all spec/plan files, and all subagents (so model mode and reviewer ≥ implementer always hold). It never runs Superpowers' brainstorming → writing-plans → subagent-driven-development as whole workflows. It uses Superpowers as techniques inside its own steps:
- brainstorming's questioning style in the "understand" step (no separate approval pause; Gate 1 is the approval);
- test-driven development inside implementer tasks;
- systematic debugging in `fix`;
- verification-before-completion in the final audit.

Ponytail's ladder is applied by implementers (write the minimum) and reviewers (reject bloat). UI skills (`design-taste-frontend`, `web-design-guidelines`, `animation`, `modern-web-guidance`) are consulted during exploration, implementation and review on the UI track.

SuperDesign is required for every UI-track run, including `inspect`; the DESIGN.md `superdesign:` block stays required.

If a dependency publishes **no version at all** for the current platform (not merely uninstalled), the skill continues without it, says so in the status line, and the README lists that platform gap. *(My call.)*

Startup check verifies core always and UI only when the UI track is active. Installed-able but missing → stop, name what's missing, show the install command from the README. How a skill detects another installed skill differs by platform (agent's own skill list vs looking in the skill folders); builder picks the most reliable per platform and documents it in `platforms.md`.

Builder researches the real source and install command for each dependency on each platform (some are `npx skills` installable, Superpowers and Ponytail are plugins on Claude Code). Unknown → say so in the README rather than guess.

## 11. Safeguards and definition of done

Safeguards (stated once in SKILL.md):
1. One source of truth per spec (DESIGN.md / API contract); anything tool-specific is derived from it.
2. Never silently skip an unavailable tool, dependency or model; never claim one was used when it wasn't.
3. Zero fabricated evidence: no invented metrics, clients, testimonials, or "measured" values that were inferred. Generated imagery is labeled generated.
4. Scope is what Gate 2 approved. No unapproved refactors, abstractions or dependencies.
5. Subagents never self-certify; every implementer output is reviewed (per task or per batch, per workflow mode).

Definition of done (replaces v1's repeated "1% incorrect" wording): a concrete checklist the orchestrator ticks in the final audit — every Gate-2 task done; all tests pass (output shown); the active track's quality lenses pass for everything in scope; no console errors (UI); nothing outside approved scope changed; anything not verified is listed as not verified. Any failed item goes back to implementation; the run is not reported done with a failed item.

End-of-run report: what was produced, what was verified and how, what was not done or not verified, and the run's settings line.

## 12. `contrast-check.py`

Keep the checker. Replace `--selftest` (which looks for a table in SKILL.md that never existed) with a self-contained check of a few known pairs, e.g. white on black = 21.00 pass/pass, `#777777` on white = 4.48 fail/pass. Remove the "antislop-human" references.

## 13. README.md

- What it is, the five flows, the two dials, tracks — short.
- Install: `npx skills add <owner>/super-system -g`, plus the `-a claude-code -a antigravity -a codex …` form. One real copy is the goal; builder verifies whether `npx skills` links or copies per agent and documents the result.
- Note: Cursor and OpenCode also read `~/.claude/skills/`, so they may list the skill twice if it is also there.
- Dependencies table (§10) with install steps per platform.
- Config file explained, with the example from §7.
- Examples of invocations.

## 14. Decided vs left to the builder

Decided by the user:
- Usable by anyone; covers backend and non-UI work.
- Two dials: workflow mode and model mode; the chat model is always the orchestrator.
- Claude Code: normal = Sonnet implements, Opus (the chat model) plans; economy brings in Haiku. Antigravity: full = Argon, normal = Argon + Flash, economy = Argon chat model + all subagents Flash at high reasoning.
- Other platforms: ask which models are available before asking for modes.
- Settings saved per platform; ask only on override.
- The five flows.
- Dependencies are required, installed separately, documented in README.
- Install via `npx skills`, global by default; no installer of our own.
- Trims 1–4 from the review (remove personal details; state each rule once; roles instead of hardcoded models; small core + references).
- Workflow mode scales work, not only models; single-agent fallback for platforms without subagents.

My calls (user may override):
- Config location `~/.super-system/config.json` and its shape.
- Role set (scout / implementer / reviewer) and the exact cells of the model tables beyond the user's examples.
- Reviewer ≥ implementer rule.
- Workflow-mode table cells (§6).
- Repo layout `skills/super-system/`.
- Removing the v1 personal aesthetics and archetype names rather than generalizing them.
- Keeping generic anti-slop defaults (including the overused-font list) in `track-ui.md`.

Left to the builder:
- Exact wording, as long as each rule appears once and SKILL.md stays ≈8KB or less.
- Per-platform subagent spawn syntax and skill-detection method (from current docs).
- Dependency sources and install commands (from current docs).
- Platform detection heuristics.

Decided after the builder check:
- GitHub repo: `glambz/super-system` (https://github.com/glambz/super-system). Install line: `npx skills add glambz/super-system -g`.
- License: MIT.

## 15. Migrating the author's own setup (part of this job)

1. Back up `C:\Users\indocyber\.agents\skills\super-system\` to a dated folder outside every skills directory (so it isn't loaded twice), e.g. `C:\Users\indocyber\.super-system\backup\super-system-v1-2026-11-06\`.
2. Write `C:\Users\indocyber\.super-system\config.json` with `tasteFile` = `C:\Users\indocyber\Desktop\projects\design-library\user-taste.md`, `designLibrary` = `C:\Users\indocyber\Desktop\projects\design-library`, and entries `claude-code: { workflow: full, models: normal }`, `antigravity: { workflow: full, models: economy }`.
3. Append the personal content removed from v1 to `user-taste.md` under a clearly marked section (read the file first; append, never overwrite): the brand-showcase palette (warm clay `#EEEEEE`/`#F2EEE8`, obsidian `#000000`/`#111111`, hazard orange `#FF4905` under 10%), 45° chamfers / stepped notches, the per-screen prototype archetypes (utility: Tactical Split View, Streamlined Progressive Disclosure, Dense Monolithic Utility; brand: Monolithic Architectural Editorial, Kinetic Shutter Physics, Stepped Asymmetric Polygons), the font preference list, the "Tasrock" calibration reference, and the four SuperDesign project IDs as prior-art references.
4. Remove the v1 folder from `~/.agents/skills/` only after step 1 is verified, then install v2 with `npx skills add glambz/super-system -g` (after it is pushed) and confirm each platform sees exactly one `super-system`.
