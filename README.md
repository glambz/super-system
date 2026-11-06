# super-system

An orchestrated delivery workflow for coding assistants, covering UI and backend work. It runs on any assistant that supports [Agent Skills](https://agentskills.io): Claude Code, Antigravity, Cursor, OpenCode, Oh My Pi, Codex, Kilo Code, and others.

- **Five flows:** `build` (new feature or project), `change` (redesign or refactor), `fix` (root-cause a bug), `review` (read-only audit), `inspect` (live site → evidence-labeled `DESIGN.md`).
- **Two dials,** each `full | normal | economy`:
  - **workflow mode:** how much work (options explored, how often review happens, how deep the final audit goes)
  - **model mode:** which models the subagents use. The model you chat with is always the orchestrator.
- **Tracks:** UI steps (prototypes, browser QA, accessibility) and backend steps (design options, contract/integration tests, security), or both for full-stack work.
- **Guardrails:** two human gates (approve the direction, approve the plan), a reviewer for every implementer, and a final audit against a written definition of done.

## Install

```bash
npx skills add glambz/super-system -g
```

To pick assistants explicitly:

```bash
npx skills add glambz/super-system -g -a claude-code -a antigravity -a codex -a cursor -a opencode -a kilo -a pi -y
```

This keeps **one real copy** in `~/.agents/skills/super-system/`. Codex, Cursor, OpenCode and Kilo Code read that folder directly (per their docs); Oh My Pi is reported to as well. Claude Code gets a symlink to it in `~/.claude/skills/`. Updating (`npx skills update super-system -g`) updates every assistant at once.

Notes:
- **Antigravity:** its docs name `~/.gemini/config/skills/` as the global folder. If Antigravity doesn't list super-system, link it there:
  - macOS/Linux: `ln -s ~/.agents/skills/super-system ~/.gemini/config/skills/super-system`
  - Windows: `mklink /J %USERPROFILE%\.gemini\config\skills\super-system %USERPROFILE%\.agents\skills\super-system`
- **Cursor and OpenCode** also read `~/.claude/skills/`, so they may list the skill twice. It's the same files, so nothing conflicts.
- Requires Node.js 22.20 or later for `npx skills`.

## Dependencies

super-system uses these as techniques inside its own steps. Install them for each assistant you use; each harness needs its own install. The skill checks at startup and stops with the install command if a required one is missing.

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
| animation | no public source confirmed | Optional: if you have an `animation` skill installed it is used; otherwise the run says it is missing and continues |
| A browser the agent can drive | [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) or [Playwright MCP](https://github.com/microsoft/playwright-mcp), or your assistant's built-in browser | MCP config: `{"mcpServers":{"chrome-devtools":{"command":"npx","args":["-y","chrome-devtools-mcp@latest"]}}}` · Claude Code: `claude mcp add playwright npx @playwright/mcp@latest` · Codex: `codex mcp add playwright npx "@playwright/mcp@latest"` |

Where a platform isn't listed for a dependency, upstream doesn't document an install for it; try `npx skills add <repo> -g`. super-system continues without a dependency only when no version exists for your platform at all, and says so in its status line.

## Usage

```
/super-system build --workflow full --models normal
/super-system change checkout
/super-system fix "login returns 500 when email has a plus sign"
/super-system review main..feature/payments
/super-system inspect https://example.com landing-page
```

Every run starts with a status line:

```
super-system · Claude Code · flow: build · workflow: full · models: normal · tracks: ui+backend
```

`--workflow` and `--models` (or plain words like "use economy models this time") apply to that run only. At the end the skill asks whether to keep them as the new default.

## Settings

The first run on each assistant does the following:

1. If the assistant isn't Claude Code or Antigravity, it asks which models you have and maps them to `top` / `mid` / `cheap`.
2. Where the assistant only lets you choose subagent models in agent files, it offers to write three small agent files (`super-system-top`, `-mid`, `-cheap`).
3. It asks for your two modes and saves them to `~/.super-system/config.json`.

Later runs on that assistant don't ask again. Reinstalling or updating the skill never touches this file.

```json
{
  "platforms": {
    "claude-code": { "workflow": "full", "models": "normal" },
    "antigravity": { "workflow": "full", "models": "economy" },
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
  "designLibrary": null
}
```

- `tasteFile`: optional path to your own taste / anti-slop notes, read before any design exploration.
- `designLibrary`: optional folder of `DESIGN.md` prior art. `build` and `change` copy UI designs there for later sessions. `inspect` writes there (default: `./design-library/` in the project).

### Default models

| Role | Claude Code full | normal | economy | Antigravity full | normal | economy |
|---|---|---|---|---|---|---|
| scout | Opus | Sonnet | Haiku | Argon | Flash | Flash · high |
| implementer | Opus | Sonnet | Sonnet (Haiku for mechanical tasks) | Argon | Flash | Flash · high |
| reviewer | Opus | Sonnet | Sonnet | Argon | Argon | Flash · high |

Antigravity can't set reasoning per subagent; for "Flash · high" set the conversation's thinking level to High.

On other assistants, `full` uses your `top` slot everywhere. `normal` uses `mid`. `economy` uses `cheap` for scouts and `mid` for implementers (cheap for mechanical tasks) and reviewers.

## Development

```bash
python tests/check_skill.py
```

This checks that SKILL.md stays under 8KB, that no personal paths or IDs are present, that model names appear only in `references/platforms.md`, that no references are broken, and that the contrast checker's self-test passes.

## License

MIT
