# metawork-claude-plugin

> **Status:** v0.1 alpha — scaffolding only. Skill, command, and subagent
> bodies are stubs; methodology references are placeholders pending the first
> dogfood pass through `metawork-articulate`.

A Claude Code plugin for **Meta Work** — a structured practice of intentional
planning, monitoring, and perspective-maintenance applied per project, area,
domain, or identity scope. Meta Work integrates the GTD Natural Planning Model,
Living Forward Life Plan, Polarity Management, Fitness Functions, Radical
Acceptance, Panarchy & adaptive cycles, the ADDRESSING model, and vertical
development calibration into a single per-`(scope, subject)` artifact called a
**Meta Work Group**.

This plugin **teaches** the methodology, **runs** the practice, **sets up** the
practice in your tool of choice, and **coaches** you through resistance, drift,
and breakdowns.

## The shape

| Surface | Artifacts |
|---|---|
| Skills | `metawork-scholar`, `metawork-articulate`, `metawork-set-up`, `metawork-morning`, `metawork-retro`, `metawork-diagnose` |
| Slash commands | `/metawork-set-up`, `/metawork-morning`, `/metawork-retro`, `/metawork-diagnose`, `/metawork-articulate` |
| Subagents | `metawork-scholar` (heavy Socratic teaching), `metawork-orchestrator` (multi-group operations) |
| Backends (v1) | OmniFocus, markdown directory |
| Backends (v2+ roadmap) | Obsidian vault, Things, Todoist, Notion |

There is **no MCP server** in v1. Skills compose on top of the existing
`mcp__omnifocus__*` tools for OmniFocus users and degrade gracefully to
TaskPaper render-and-paste / generated markdown for everyone else. The
methodology is tool-agnostic; the plugin gives you a way to express it
wherever you persist text. See [ADR-0002](docs/adr/0002-no-adapter-mcp-in-v1.md).

## Install

> **Alpha/preview.** Skill, command, and subagent bodies are still stubs (see
> the status note above). The plugin installs and its surfaces load, but the
> methodology behavior is still being filled in.

In Claude Code (CLI) or Claude Desktop (Cowork):

```text
/plugin marketplace add Integral-Productivity/marketplace
/plugin install metawork@integral-productivity-tools
```

Then restart Claude Code so the plugin's skills, commands, and subagents are
picked up. The marketplace entry tracks this repo's `main` branch while
metawork is in alpha; it moves to a tag-driven `stable` channel at the first
real release (see [#6](https://github.com/Integral-Productivity/metawork-claude-plugin/issues/6)).

## Configure

Configuration (backend type + location) lives at `~/.metawork/config.json`. Any
skill that needs state will offer to write the config on first use. You can
also pass `--state-dir` per invocation to override.

## How the methodology is articulated

The methodology itself lives in a sibling repo,
[`Integral-Productivity/metawork-methodology`](https://github.com/Integral-Productivity/metawork-methodology),
and is synced into this plugin's `references/` directory by
`.github/workflows/sync-methodology.yml`. The `metawork-articulate` skill is
the elicitation tool that drafts and extends that methodology doc — a
deliberate closed loop where the articulator writes what the scholar teaches.

## What Meta Work is NOT

- Not the casual, escapist *meta-work* you do when avoiding the work you
  scheduled — that's the opposite, and the plugin's scholar teaches the
  distinction explicitly.
- Not the GTD `Meta-Task` tag (`Task Preprocessing` / `Project Preprocessing`
  / `Task Processing` / `Task Postprocessing`) — unrelated concept, similar
  name. See [CONTEXT.md](CONTEXT.md).

## Related

- [`Integral-Productivity/metawork-methodology`](https://github.com/Integral-Productivity/metawork-methodology)
  — the narrative methodology
- [`Integral-Productivity/omnifocus-taskpaper-templates`](https://github.com/Integral-Productivity/omnifocus-taskpaper-templates)
  — the canonical TaskPaper template for instantiating a Meta Work Group in
  OmniFocus

## License

MIT
