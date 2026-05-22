# 2. No adapter MCP in v1

Date: 2026-05-21

## Status

Accepted

## Context

The plugin must operationalize Meta Work across multiple backends (OmniFocus
today; Things, Todoist, Obsidian, Notion, markdown as the public adopts it).
The standard Integral-Productivity pattern (see `~/GitHub/CLAUDE.md` Tech
Radar, ADRs in `devops-excellence` and our MCP-builder skills) is
**MCP-first**: define a tool-agnostic verb surface as an MCP server, then have
skills consume it. That gives clean contract boundaries, semver, and
non-Claude-Code reuse.

For this plugin specifically, an adapter MCP would mean verbs like
`createMetaWorkGroup(scope, subject)`, `recordPerspectiveCheck(area, kind)`,
`surfaceMetaWorkSignal(...)`, each dispatching internally to the user's
backend of choice.

The cost is real:

- A whole engineering surface (npm + GitHub Packages, StreamableHTTP for
  Vercel + stdio for local, bearer-token auth, deploy pipeline, semver)
- Double indirection on every skill call (adapter → OmniFocus MCP → OF)
- Install friction for the public (plugins are declarative; MCPs require
  hosting or self-host)
- **The right verbs aren't knowable yet.** Adapter shape only emerges after
  driving real backends from real skills for a while.

## Decision

**v1 ships skills + slash commands + subagents only.** No adapter MCP.

Skills compose on top of the existing `mcp__omnifocus__*` MCP for OmniFocus
users (with degrading fallback to URL scheme / TaskPaper paste) and write
directly to filesystem markdown for non-OmniFocus users. The "adapter" is
expressed as skill-level branching in `lib/backends/*.md` — prose, not code.

Extracting an adapter MCP (`@integral-productivity/metawork-mcp`) moves to the
v2 roadmap, to be initiated once **two or more backends are real** and the
skill-level adapter patterns have stabilized into discoverable verbs.

## Consequences

**Positive:**

- v1 ships faster and reaches public users sooner.
- The right adapter abstraction is informed by real usage, not speculation.
- Non-Claude-Code adopters are not blocked — the plugin's `lib/backends/*.md`
  prose is portable as a teaching reference.
- Install bar stays low (declarative plugin manifest, no service to host).

**Negative:**

- Each backend implementation is duplicated logic in skills until the adapter
  is extracted. Two backends = manageable; ten backends would be a problem.
- Skills depending on backend-specific MCPs (e.g., `mcp__omnifocus__*`) carry
  a leaky abstraction. We mitigate via `lib/backends/omnifocus.md` as the
  single source of truth for backend conventions.
- A future MCP migration is a real piece of work; v2 plan must account for it.

**Trigger to revisit:** v2 ADR (extract adapter MCP) should be filed when EITHER
(a) a second backend reaches feature parity with markdown, OR (b) a non-Claude
runtime (e.g., a Vercel serverless agent) needs to drive Meta Work flows
without going through Claude Code.
