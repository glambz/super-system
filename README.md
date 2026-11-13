<div align="center">

# super-system

### One delivery workflow for every coding assistant, from brief to verified code.

[![skills](https://img.shields.io/badge/npx-skills-000000?style=flat-square&logo=npm&logoColor=white)](https://github.com/vercel-labs/skills)
[![Node](https://img.shields.io/badge/node-%E2%89%A522.20-339933?style=flat-square&logo=node.js&logoColor=white)](https://nodejs.org)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-6E56CF?style=flat-square)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

**Plans with your best model. Builds with the model you can afford.**
**Two human gates. A reviewer for every implementer. A final audit that doesn't take "looks fine" for an answer.**
**Mix assistants: plan in one, build in another, review in a third.**
**A workflow, not a prompt.**

**Claude Code · Antigravity · Cursor · OpenCode · Oh My Pi · Codex · Kilo Code**

[Install](#install) · [What it does](#what-it-does) · [Flows](#flows) · [Modes](#modes) · [Dependencies](#dependencies) · [FAQ](#faq)

`npx skills add glambz/super-system -g`

</div>

---

## Before and after

| | **Without super-system** | **With super-system** |
|---|---|---|
| **Planning** | The agent starts coding from the first sentence of your request | Questions first, 1–3 options with tradeoffs, then you pick (**Gate 1**) |
| **Scope** | "While I was in there, I also refactored…" | Only what you approved at **Gate 2** changes |
| **Review** | The agent that wrote the code says it's done | A separate reviewer runs the tests, reads the diff, and can reject |
| **Cost** | One model for everything | Best model plans and audits; cheaper models implement, by your choice |
| **Quota** | One subscription's limits cap the whole job | Roles spread across the assistants you already pay for (platform mode) |
| **UI** | Pastel gradients and three cards in a row | Real prototypes, browser QA at 1440 / 768 / 390, accessibility checks |
| **Backend** | Tests "should pass" | Tests shown passing, migrations run on a copy, security and N+1 checks |
| **Done** | "Looks good!" | A definition-of-done checklist; anything unverified is listed as unverified |

---

## Install

One copy, every assistant. The `skills` CLI puts the skill in `~/.agents/skills/super-system/` and links it where each assistant looks.

### npx skills (recommended)

```bash
npx skills add glambz/super-system -g
```

### Pick assistants explicitly

```bash
npx skills add glambz/super-system -g -a claude-code -a antigravity -a codex -a cursor -a opencode -a kilo -a pi -y
```

Codex, Cursor, OpenCode and Kilo Code read `~/.agents/skills/` directly (per their docs); Oh My Pi is reported to as well. Claude Code gets a symlink in `~/.claude/skills/`.

### Antigravity

Antigravity's docs name `~/.gemini/config/skills/` as its global folder. If it doesn't list super-system after install, link it:

```bash
# macOS / Linux
ln -s ~/.agents/skills/super-system ~/.gemini/config/skills/super-system
```

```text
:: Windows
mklink /J %USERPROFILE%\.gemini\config\skills\super-system %USERPROFILE%\.agents\skills\super-system
```

Cursor and OpenCode also read `~/.claude/skills/`, so they may list the skill twice. It's the same files, so nothing conflicts.

### Mixed mode prerequisites (optional)

Only needed if you route roles to other assistants ([platform mode](#platform-mode)). Each assistant you route to needs its CLI installed and signed in on the same machine:

| Runner | Install | Sign in |
|---|---|---|
| Antigravity (`agy`) | the official installer from [antigravity.google](https://antigravity.google/docs/install?tab=cli) | run `agy` once interactively; headless runs reuse that login |
| Codex (`codex exec`) | [Codex CLI](https://learn.chatgpt.com/docs/non-interactive-mode) | your usual Codex login or provider key in `~/.codex/config.toml` (custom providers work) |
| Claude Code (`claude -p`) | [Claude Code](https://code.claude.com/docs) | run `claude` once and log in |

> **Warning:** routed agents run with their skip-all-permissions flags (`--dangerously-skip-permissions` for `agy` and `claude`, `--dangerously-bypass-approvals-and-sandbox` for Codex), so they never stop to ask. That means they can run any command on your machine. Use `mixed` only on projects and machines where you accept that.

---

## What it does

- **Asks before it builds.** One question at a time until it knows what success looks like.
- **Shows options, not a fait accompli.** Prototypes on a SuperDesign canvas for UI; API, schema or architecture options for backend.
- **Stops twice.** Gate 1: you pick the direction. Gate 2: you approve the plan. Nothing is built before Gate 2.
- **Splits the work.** Scouts read, implementers build, reviewers check. A reviewer is never on a weaker model than the implementer it checks.
- **Audits at the end.** The model you chat with checks everything against a written definition of done.
- **Keeps evidence honest.** Nothing measured is invented; nothing generated is passed off as real.

The model you chat with is always the orchestrator. super-system never switches it; it chooses models only for the subagents it sends out.

---

## Flows

| Flow | Covers | Pick it for |
|---|---|---|
| `build` | Understand → options → Gate 1 → plan → Gate 2 → implement + review → verify → audit | A new feature or a new project |
| `change` | Same as `build`, starting with an audit of what exists | A redesign or refactor |
| `fix` | Reproduce → root cause → fix plan → Gate 2 → failing regression test → fix | A bug, fixed where it starts |
| `review` | Read-only audit, findings with `file:line` and severity | A branch, a PR, or a codebase health check |
| `inspect` | Live URL → evidence-labeled `DESIGN.md` + canvas draft | Learning from a site you admire |

Each flow runs a UI track, a backend track, or both, picked from the task and the codebase.

---

## Modes

Three dials, set separately. Workflow and model mode are `full`, `normal` or `economy`; platform mode is `native` or `mixed`.

- **Workflow mode:** how much work gets done (options explored, review frequency, audit depth).
- **Model mode:** which models the subagents run on.
- **Platform mode:** which assistant each subagent runs on.

| Workflow | full | normal | economy |
|---|---|---|---|
| Options explored | 3 per screen/component | 2 for main, 1 for the rest | 1, main only |
| Review | after every task | after every task | once per batch |
| Final audit | every route, viewport and file | changed routes, all viewports | changed routes, desktop + mobile |

| Model mode | Claude Code full | normal | economy | Antigravity full | normal | economy |
|---|---|---|---|---|---|---|
| scout | Opus | Sonnet | Haiku | Argon | Flash | Flash · high |
| implementer | Opus | Sonnet | Sonnet (Haiku for mechanical tasks) | Argon | Flash | Flash · high |
| reviewer | Opus | Sonnet | Sonnet | Argon | Argon | Flash · high |

Antigravity can't set reasoning per subagent; for "Flash · high", set the conversation's thinking level to High. On other assistants, the first run asks which models you have and maps them to `top` / `mid` / `cheap`. Then `full` uses `top`, and `normal` uses `mid`. `economy` uses `cheap` for scouts and `mid` for implementers (cheap for mechanical tasks) and reviewers.

### Platform mode

`native` (the default) runs every subagent inside the assistant you're chatting with. `mixed` sends each role to the assistant you pick, through its headless CLI, while the one you chat with stays the orchestrator: it plans, runs both gates and does the final audit.

| Role | Example route | Runs as |
|---|---|---|
| scout | `native` | a subagent of the chat assistant |
| implementer | `antigravity` | `agy -p …` in the background |
| reviewer | `codex` | `codex exec …` in the background |

- **Models follow the dials.** Model mode still picks `top` / `mid` / `cheap` for each role, and that slot is looked up on the assistant that runs the role. The first `mixed` run reads what each CLI is actually set to (a Codex pointed at another provider stays on that provider) and asks you to confirm the slots.
- **Done means checked.** A run counts as done only when its own answer says so, its result matches the role's format, its changed files match the task, and no permission or quota error shows in its logs. An exit code alone never counts.
- **Bounded loops.** At most 3 review rounds per task and 2 final-audit rounds. After that you get the open problems and decide: another round, or pass.
- **No time limit, but no silent hangs.** Agents run as long as they need. One that prints nothing for 15 minutes (`stallMinutes`) is reported to you with a recommendation.
- **Always asks.** A blocked agent, a missing CLI, a used-up quota or a stall stops that work and comes to you with a recommendation. The orchestrator never quietly does the work itself.
- **Parallel only when safe.** Gate 2 asks whether subagents run concurrently or one at a time; concurrent tasks never share files.
- **Nothing added to your project.** Briefs, logs and answers go to `~/.super-system/runs/<project>-<date-time>/`.

Verified with Claude Code as the orchestrator. Other orchestrators can use `mixed` if they can run a shell command in the background; the skill tells you when that isn't verified.

Your choices are saved per assistant. Override them for one run:

```bash
/super-system build --workflow full --models economy --platforms native
```

**`super-system · Claude Code · flow: build · workflow: full · models: normal · platforms: mixed (scout: native · implementer: antigravity/<model>·high · reviewer: codex/<model>·high) · tracks: ui+backend`**

At the end of an overridden run, it asks once whether to keep the override as the new default.

### More examples

```text
/super-system change checkout
/super-system fix "login returns 500 when email has a plus sign"
/super-system review main..feature/payments
/super-system inspect https://example.com landing-page
```

---

## Settings

Saved in `~/.super-system/config.json`. Reinstalling or updating the skill never touches it.

```json
{
  "platforms": {
    "claude-code": {
      "workflow": "full", "models": "normal",
      "platforms": "mixed",
      "roles": {
        "scout": "native",
        "implementer": { "backend": "antigravity", "ui": "antigravity" },
        "reviewer": "codex"
      }
    },
    "antigravity": {
      "workflow": "full", "models": "economy",
      "cli": {
        "top":   { "model": "<slug from agy models>", "effort": "high" },
        "mid":   { "model": "<slug from agy models>", "effort": "high" },
        "cheap": { "model": "<slug from agy models>", "effort": "high" },
        "tools": ["browser"]
      }
    },
    "codex": {
      "cli": {
        "top":   { "model": "<model from ~/.codex/config.toml>", "effort": "high" },
        "mid":   { "model": "<model from ~/.codex/config.toml>", "effort": "high" },
        "cheap": { "model": "<model from ~/.codex/config.toml>", "effort": "medium" },
        "tools": []
      }
    },
    "cursor": {
      "workflow": "normal",
      "models": "normal",
      "slots": {
        "top":   { "model": "<model id>", "effort": "high" },
        "mid":   { "model": "<model id>", "effort": "medium" },
        "cheap": { "model": "<model id>", "effort": "medium" }
      }
    }
  },
  "tasteFile": null,
  "designLibrary": null,
  "stallMinutes": 15
}
```

- **`platforms` / `roles`:** platform mode for this assistant, and where each role runs when it's `mixed`. A `roles` value can be a single platform string or an object keyed by track (`backend`, `ui`); a missing role or track runs `native`.
- **`cli`:** the models used when this assistant runs as someone else's runner, `tools` (`browser`, `superdesign`) it can use headless, and optional `concurrency` (per-runner cap, default 3). Steps that need a missing tool run natively and the status line says so. An entry with only `cli` is fine.
- **`stallMinutes`:** minutes without output before a subagent is reported as stuck. Default 15.
- **`tasteFile`:** optional path to your own taste and anti-slop notes, read before any design work.
- **`designLibrary`:** optional folder of `DESIGN.md` prior art. `build` and `change` copy UI designs there for later sessions, and `inspect` writes there. The default is `./design-library/` in the project.

---

## Dependencies

super-system uses these as techniques inside its own steps. Each assistant needs its own install. At startup the skill checks for them, and if a required one is missing it stops and shows the install command.

### Core (always required)

| Dependency | Source | Install |
|---|---|---|
| Superpowers | [obra/superpowers](https://github.com/obra/superpowers) | Claude Code: `/plugin install superpowers@claude-plugins-official` · Cursor: `/add-plugin superpowers` · Codex: `/plugins` → search `superpowers` → Install · Antigravity: `agy plugin install https://github.com/obra/superpowers` · Pi: `pi install git:github.com/obra/superpowers` (Oh My Pi: not confirmed upstream) · OpenCode: ask it to "Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md" · Kilo Code: not documented upstream |
| Ponytail | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Claude Code: `/plugin marketplace add DietrichGebert/ponytail` then `/plugin install ponytail@ponytail` · Codex: `codex plugin marketplace add DietrichGebert/ponytail` then `codex plugin add ponytail@ponytail` · Antigravity: `agy plugin install https://github.com/DietrichGebert/ponytail` · Pi: `pi install git:github.com/DietrichGebert/ponytail` (Oh My Pi: not confirmed upstream) · OpenCode: `opencode plugin add @dietrichgebert/ponytail` · Kilo Code: add `{ "plugin": ["@dietrichgebert/ponytail"] }` to `~/.config/kilo/kilo.jsonc` · Cursor / any: `npx skills add DietrichGebert/ponytail -g` |

### UI track (required when a task touches UI)

| Dependency | Source | Install |
|---|---|---|
| SuperDesign | [superdesigndev/superdesign-skill](https://github.com/superdesigndev/superdesign-skill) | `npm install -g @superdesign/cli@latest`, then `superdesign login`, then `npx skills add superdesigndev/superdesign-skill -g` |
| design-taste-frontend | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `npx skills add Leonxlnx/taste-skill --skill design-taste-frontend -g` |
| web-design-guidelines | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | `npx skills add vercel-labs/agent-skills --skill web-design-guidelines -g` |
| modern-web-guidance | [GoogleChrome/modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance) | `npx skills add GoogleChrome/modern-web-guidance -g` (or the wizard: `npx modern-web-guidance@latest install`) |
| animation | no public source confirmed | Optional: used if installed; otherwise the run says it is missing and continues |
| A browser the agent can drive | [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp), [Playwright MCP](https://github.com/microsoft/playwright-mcp), or your assistant's built-in browser | MCP config: `{"mcpServers":{"chrome-devtools":{"command":"npx","args":["-y","chrome-devtools-mcp@latest"]}}}` · Claude Code: `claude mcp add playwright npx @playwright/mcp@latest` · Codex: `codex mcp add playwright npx "@playwright/mcp@latest"` |

Where a platform isn't listed for a dependency, upstream doesn't document an install for it; try `npx skills add <repo> -g`. super-system continues without a dependency only when no version exists for your platform at all, and says so in its status line.

---

## Update

```bash
npx skills update super-system -g
```

Start a new session afterwards; most assistants read skills only at session start.

---

## FAQ

**Does it change the model I'm chatting with?**
No. The model you chat with plans, runs the gates and does the final audit. Model mode only picks models for subagents.

**Why does it offer to write agent files?**
Most assistants (Cursor, OpenCode, Codex, Kilo Code, Antigravity, Oh My Pi) only let you set a subagent's model in an agent file. super-system offers to write three: `super-system-top`, `-mid` and `-cheap`. It asks first.

**My assistant has no subagents. Does it still work?**
Yes. It runs the roles one after another in the same session, and review stays a separate pass over the diff.

**Can I use it for backend-only work?**
Yes. Backend tasks run the backend track only, with no prototypes, no browser QA and no UI dependencies required.

**Will updating wipe my settings?**
No. Settings live in `~/.super-system/config.json`, outside the skill folder.

**Can I mix assistants, say Claude Code planning, Antigravity building and Codex reviewing?**
Yes, with `"platforms": "mixed"` and a `roles` map. Each role runs through that assistant's own CLI, so it uses that assistant's subscription and quota. See [Platform mode](#platform-mode).

**Is skipping permissions safe?**
Only as safe as the machine and project you run it on. Routed agents can run any command without asking; that's what keeps an hour-long implementation from stalling on a prompt nobody sees. Use `native` when that isn't acceptable.

**Isn't two gates slow?**
Gate 1 takes a minute to pick a direction. Gate 2 takes a minute to read a plan. Either way, it's less time than undoing work you didn't ask for.

---

## Roadmap

### What's new in v3.1

1. **Fix-round cap & minor triage**: fix rounds carry at most 3 Critical/Important findings; minors never trigger a fix round on their own and are either accepted (recorded in `retro.md` and surfaced at Gate 1/2 on the next run) or batched into one end-of-run polish round.
2. **Hard constraints & decision log**: every brief includes a hard-constraints block (known-failing base tests, shared files not to touch, repo budgets, interpreter path) and points to the plan's `## Decisions during the run` log.
3. **Tested runner & worktree scripts (`scripts/`)**: `_lib.sh` (shared helpers), `run-agy.sh`, `run-codex.sh`, `review-wrap.sh`, `queue.sh`, `wait-done.sh`, `removed-checks.py` (base-diff guard), `worktree-setup.sh`, and `worktree-cleanup.sh`, plus quota-aware scheduling (`cli.window_hours`) and a parallel worktree recipe.
4. **Review flow verifier & severity rubric**: fresh verifier (`scout` role) re-reads cited lines, checks cheap reproductions, marks duplicates in a findings register, and applies `references/severity.md`; the orchestrator samples all criticals plus at least 1 in 5 of the rest.
5. **Stricter backend & docs checks**: read-only pre-deploy SQL data checks, worked numeric/money examples verified through real functions by script, and sentence-level diff checks on documentation changes.

### What's new in v3

1. **Technique cards in briefs** (`references/techniques/`): short, self-contained cards for Ponytail, TDD, debugging, verification, backend security, UI quality and contracts pasted directly into briefs so routed agents never miss a skill.
2. **Red evidence & stronger done checks**: implementers report `red_evidence` (failing base run before the fix, or `no_test_reason` for docs/config) and list removed checks; reviewers verify `regression_checks` in `fix` and must return a parsed `verdict`; Antigravity background-wait `ERROR` with valid `structured_output` is treated as a warning with reviewer re-test.
3. **Run hygiene**: scripts copied into the run folder and never edited mid-run; briefs/scripts written with file tools instead of shell heredocs; per-runner `cli.concurrency` cap and 429 retry policy; content-based result checks.
4. **Per-track routing & contract-first split**: `roles` can map per track (`backend` / `ui`), and dual-track features can freeze `docs/design/api/<feature>.md` at Gate 2 so backend and mocked-API frontend run concurrently before a browser integration check.
5. **Retrospective & durable lessons**: every run writes `retro.md` with skill-improvement proposals (applied only on user approval) and appends durable lessons to `~/.super-system/lessons.md`, read at startup.
6. **Runner skill setup**: setup checks role helper skills on routed runners and warns if the orchestrator skill itself is installed where routed runners load skills.

**v2.1.0**
- Platform mode: route scouts, implementers and reviewers to other assistants' CLIs
- Round caps, stall reports and a Gate 2 concurrency choice for every subagent

**v2.0.0**
- Five flows, two dials, UI and backend tracks
- Per-assistant settings and model slots
- Install via `npx skills`

**Next**
- Check that a `DESIGN.md` covering several page types has a clear library path
- Stricter reference checks in `tests/check_skill.py`

---

## Development

```bash
python tests/check_skill.py
```

This checks that SKILL.md stays under 8KB, that no personal paths or IDs are present, that model names appear only in `references/platforms.md`, that each rule is stated once, that no references are broken, and that the contrast checker's self-test passes.

---

## Star History

<p align="center">
  <a href="https://star-history.com/#glambz/super-system&Date">
    <img src="https://api.star-history.com/svg?repos=glambz/super-system&type=Date" alt="Star history chart for glambz/super-system" width="600">
  </a>
</p>

## Contributors

<p align="center">
  <a href="https://github.com/glambz/super-system/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=glambz/super-system" alt="Contributors to glambz/super-system">
  </a>
</p>

Issues and pull requests are welcome. Run `python tests/check_skill.py` before opening one.

<hr>
<p align="center"><em>The best code is the code you approved.<br>The second best is the code someone else checked.</em></p>
<hr>

## Disclaimer

The only official source is [github.com/glambz/super-system](https://github.com/glambz/super-system). Skills run with your agent's full permissions, so read any skill before you install it, this one included.

## License

[MIT](LICENSE)
