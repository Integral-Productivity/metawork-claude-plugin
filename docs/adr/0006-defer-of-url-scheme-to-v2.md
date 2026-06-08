# 6. Defer OmniFocus URL-scheme integration to v2

Date: 2026-05-21

## Status

Accepted

## Context

`lib/backends/omnifocus.md` drafted a three-tier degradation order for
OmniFocus write operations:

1. `mcp__omnifocus__*` MCP tools (preferred).
2. The user's OmniFocus plugin via URL scheme (fallback).
3. TaskPaper render-and-paste (final fallback).

The middle tier is a placeholder. The URL surface is not designed, the
OmniFocus plugin's source repo is not yet named or stood up under
`Integral-Productivity`, and no v1 adopter has surfaced a need that the
MCP-or-TaskPaper-paste path doesn't already meet. `PLAN.md` flagged the
question for resolution in Phase 0.

[ADR-0002](0002-no-adapter-mcp-in-v1.md) already commits v1 to the
*skill-level adapter* pattern — backend dispatch lives in
`lib/backends/*.md` as prose, not in code. Adding URL-scheme support
would introduce a third dispatch target for the same end (write a Meta
Work Group into OmniFocus) before the shape of either the URL surface
or the plugin's verb vocabulary is knowable. The cost is the same one
ADR-0002 identified for the adapter MCP itself, at a smaller scale:
design effort spent on contracts that the first real usage will
invalidate.

## Decision

**v1 OmniFocus degradation is two-tier:** `mcp__omnifocus__*` →
TaskPaper render-and-paste. URL-scheme delegation to a user-maintained
OmniFocus plugin is deferred to v2.

`lib/backends/omnifocus.md` is updated in the same change to:

- drop the URL-scheme step from the §Degradation order, and
- drop the *OF plugin via URL* column from the §Write operations table.

The §Template store section is left intact — it mentions the URL-scheme
path as how the reference user's local OmniFocus plugin *consumes* the local
template instance, which is unrelated to the degradation fallback and
sits outside the v1 plugin's responsibilities.

## Consequences

**Positive:**

- v1 ships without depending on a not-yet-named external repo.
- Two-tier degradation is easier to reason about and to cover with BDD
  scenarios in Phase 5 (MCP-available / MCP-unavailable, no third case).
- The reference user's OmniFocus plugin can evolve on its own cadence without
  shaping this plugin's v1 contract.
- Aligns with [ADR-0002](0002-no-adapter-mcp-in-v1.md)'s discipline of
  deferring contracts until real usage informs their shape.

**Negative:**

- Users who would benefit from native OmniFocus-plugin actions (e.g., a
  faster bulk-create that bypasses MCP rate limits) won't get them in
  v1.
- If `mcp__omnifocus__*` develops a gap for a v1 operation, the
  fallback is TaskPaper paste — slower UX than a URL-scheme action
  would deliver.

**Trigger to revisit:** file ADR-NNNN to restore the URL-scheme tier
when EITHER (a) the OmniFocus plugin's source repo is stood up under
`Integral-Productivity` and its URL surface stabilizes, OR (b) a real
v1 operation hits an `mcp__omnifocus__*` gap where TaskPaper-paste UX
is unacceptable (file an issue against the OF MCP first per the
performance-caveat discipline in `lib/backends/omnifocus.md`).
