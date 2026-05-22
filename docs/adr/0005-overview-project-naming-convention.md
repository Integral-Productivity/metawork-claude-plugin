# 5. `Overview (X)` project naming convention for area-level Meta Work

Date: 2026-05-21

## Status

Accepted

## Context

When a Meta Work Group's `horizons_of_focus` axis is set to
`20000ft-areas-focus-responsibility` (i.e., this group is about an *area* of
focus and responsibility, not a specific project), it needs a containing
project in the OmniFocus backend. OmniFocus's data model doesn't have a
first-class "area" object distinct from "project"; areas are typically
represented as folders.

Inspection of Kraig's reference database reveals a consistent existing
convention: area-level Meta Work Groups live in projects named
`Overview (Area Name)`. Examples observed:

- `Overview (Vertical Development)`
- `Overview (Personal Knowledge Management)`
- `Overview (BetterTouchTool)`
- `Overview (Hook)`
- `Overview (hypothes.is)`
- `Overview (Pushcut)`
- `Overview (SaneBox)`
- `Overview (Stream Deck Profiles)`

These projects sit inside area folders and contain area-level Meta Work
groups (plus other area-spanning maintenance tasks). They are distinct from
the individual project files that nest under them.

The same need exists for the markdown backend, where a flat directory has no
first-class "area" file — we need a convention there too.

## Decision

The OmniFocus backend (`lib/backends/omnifocus.md`) **codifies the
`Overview (X)` naming convention** as the canonical container for area-level
Meta Work. `metawork-set-up` produces `Overview (X)` projects automatically
when the user picks `20000ft-areas-focus-responsibility`. Pre-existing
`Overview (X)` projects are recognized and offered as the target.

The markdown backend uses the equivalent: an `Overview.md` file at the area
directory's root, with the area name implicit in the directory path. E.g.,
the markdown equivalent of `Overview (Personal Knowledge Management)` is
`<state-dir>/Vocational/Personal Knowledge Management/Overview.md`.

For other Horizons of Focus altitudes:

| Altitude | OmniFocus container | Markdown filename |
|---|---|---|
| `50000ft-purpose-principles` | `Overview (Purpose & Principles)` at root | `<state-dir>/Overview.md` (root) |
| `40000ft-vision` | `Overview (Vision)` at root | `<state-dir>/Vision.md` |
| `30000ft-goals-objectives` | `Overview (Goals & Objectives)` at root or under a domain | `<state-dir>/<domain>/Goals.md` |
| `20000ft-areas-focus-responsibility` | `Overview (Area Name)` | `<state-dir>/<life_domain>/<area>/Overview.md` |
| `10000ft-projects` | the project itself (no separate `Overview (...)` wrapper) | `<state-dir>/<life_domain>/<area>/<project>.md` |
| `runway` | the action group within the project | (n/a — runway-altitude groups are rarely standalone) |

## Consequences

**Positive:**

- Codifies an existing, working convention rather than inventing a new one.
- Migration effort for Kraig (the reference user) is zero — the plugin
  matches the database as-is.
- Cross-backend consistency: a public user reading both the OF and markdown
  backend docs sees the same conceptual structure.

**Negative:**

- The `Overview (X)` convention is opinionated. A user who already uses a
  different convention (e.g., `Area: X` or `X — Overview`) must either adapt
  or run a one-time migration.
- For backends beyond OF and markdown (v2+: Things, Todoist, Notion), the
  convention has to be re-expressed in each tool's idiom.

**Trigger to revisit:** if a meaningful number of v1 adopters arrive with
incompatible naming conventions, consider making the convention configurable
via the `~/.metawork/config.json` file (e.g., a `naming.area_prefix` key).
