# Platforms

How to detect each platform, which models fill the `top` / `mid` / `cheap` slots, and how to spawn a subagent on a slot. Researched from official docs on 2026-11-06; platforms change, so when something here fails, check the linked docs and tell the user.

## Slot agents (most platforms)

Most platforms only let you choose a subagent's model in an **agent definition file**, not at spawn time. On those platforms, first-run setup offers to write three agent files, `super-system-top`, `super-system-mid` and `super-system-cheap`, in the platform's global agents folder (listed per platform below). Each holds only the model, the reasoning effort and one instruction line: "You are a super-system subagent. Follow the role and task in your prompt exactly." Ask the user before writing them, and rewrite them only when the user changes slots. To dispatch a role, spawn the slot agent that the role table in SKILL.md picks and put the role (scout / implementer / reviewer) and the task in the prompt.

If a platform can't run subagents at all, or the user declines the slot agents, use the single-agent fallback from SKILL.md.

## Claude Code

- **Detect:** `Agent` and `Skill` tools exist; env `CLAUDECODE=1`; `.claude/` folder.
- **Spawn:** `Agent` tool with `model` (`opus` | `sonnet` | `haiku`) and `effort` (`low` | `medium` | `high` | `xhigh` | `max`) set per call. No slot agents needed.
- **Installed skills:** listed in your context; load with the `Skill` tool.
- **Default slots:** top = `opus`, mid = `sonnet`, cheap = `haiku`, effort `high` for all.
- **Default role models:**

| Role | full | normal | economy |
|---|---|---|---|
| scout | Opus | Sonnet | Haiku |
| implementer | Opus | Sonnet | Sonnet (Haiku for mechanical tasks) |
| reviewer | Opus | Sonnet | Sonnet |

- Docs: https://code.claude.com/docs/en/sub-agents, https://code.claude.com/docs/en/skills

## Antigravity

- **Detect:** `invoke_subagent` tool exists; `.agents/` and `~/.gemini/config/` folders; `agy` CLI.
- **Spawn:** `invoke_subagent` on a slot agent. Agent files go in `~/.gemini/config/agents/<name>.md`; frontmatter `model:` accepts only `inherit` | `flash` | `pro`.
- **Effort:** not settable per subagent. Thinking level (Low / Medium / High) is a conversation setting; for "Flash · high" ask the user to set High.
- **Installed skills:** listed in your context each turn.
- **Default slots:** top = `inherit` (the chat model, e.g. Gemini 4 Argon), mid = `flash`, cheap = `flash`.
- **Default role models:**

| Role | full | normal | economy |
|---|---|---|---|
| scout | Argon (`inherit`) | Flash | Flash · high |
| implementer | Argon (`inherit`) | Flash | Flash · high |
| reviewer | Argon (`inherit`) | Argon (`inherit`) | Flash · high |

This table overrides the generic one in SKILL.md: in normal the reviewer stays on the chat model while scouts and implementers use `flash`; in economy every subagent uses `flash`.

- Docs: https://antigravity.google/docs/subagents, https://antigravity.google/docs/models, https://antigravity.google/docs/skills

## Cursor

- **Detect:** `.cursor/` folder; the Task tool lists custom subagents. No env var documented.
- **Spawn:** Task tool on a slot agent in `~/.cursor/agents/<name>.md`. Frontmatter `model:` takes a model ID; effort goes in brackets, e.g. `model: <model-id>[effort=high]`.
- **Installed skills:** discovered at startup and shown to you.
- **Slots:** ask the user (first run). The model list is at https://cursor.com/docs/models.
- Docs: https://cursor.com/docs/subagents, https://cursor.com/docs/context/skills

## OpenCode

- **Detect:** `task` and `skill` tools; `.opencode/` folder.
- **Spawn:** `task` tool on a slot agent in `~/.config/opencode/agents/<name>.md` with `mode: subagent` and `model: <provider>/<model-id>`. Effort: a provider pass-through key such as `reasoningEffort: high`.
- **Installed skills:** the `skill` tool's description lists them in `<available_skills>`.
- **Slots:** ask the user (first run); `opencode models` lists what is available.
- Docs: https://opencode.ai/docs/agents/, https://opencode.ai/docs/skills/

## Oh My Pi (omp)

- **Detect:** `task` tool and `skill://` URLs; `~/.omp/agent/` folder.
- **Spawn:** `task` tool with `agent: <slot agent>`. Agent files go in `~/.omp/agent/agents/<name>.md`, frontmatter `model: <provider>/<model-id>:<level>` (level `low` … `max`). A per-call `model` only works if the user enabled `task.perCallModel`; don't rely on it.
- **Installed skills:** listed in the system prompt; load with `skill://<name>`.
- **Slots:** ask the user (first run); omp's `smol` / `slow` roles are a hint for cheap / top.
- Docs: https://github.com/can1357/oh-my-pi (README, docs/task-agent-discovery.md, docs/models.md)

## Codex

- **Detect:** `.codex/` or `~/.codex/` folder; `AGENTS.md`. No env var documented.
- **Spawn:** ask Codex to spawn the slot agent by name. Agent files: `~/.codex/agents/<name>.toml` with `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort` (`low` … `ultra`, as the model supports). Spawn-time model overrides are unreliable; use the agent file.
- **Installed skills:** name, description and path are listed in your context.
- **Slots:** ask the user (first run). The model list is at https://learn.chatgpt.com/docs/models.
- Docs: https://learn.chatgpt.com/docs/agent-configuration/subagents, https://learn.chatgpt.com/docs/build-skills

## Kilo Code

- **Detect:** `.kilo/` folder; `~/.config/kilo/kilo.jsonc`; `kilo` CLI.
- **Spawn:** `task` tool on a slot agent in `~/.config/kilo/agents/<name>.md` with `model: <provider>/<model-id>`. Effort: a provider pass-through key such as `reasoningEffort`.
- **Installed skills:** name, description and path are listed in the system prompt.
- **Slots:** ask the user (first run). The live list is at https://kilo.ai/models.
- Docs: https://kilo.ai/docs/customize/custom-subagents, https://kilo.ai/docs/code-with-ai/agents/model-selection, https://kilo.ai/docs/customize/skills

## Any other platform

Ask the user: does it support subagents, and how is a subagent's model chosen (per call, or in an agent file, and where)? Then use per-call selection, slot agents, or the single-agent fallback, in that order of preference. Ask for the available models and fill the slots.

## Telling platforms apart

OpenCode, Kilo Code and Oh My Pi share tool names (`task`, `skill`). Use the config folders above to tell them apart, and if signals conflict, ask.
