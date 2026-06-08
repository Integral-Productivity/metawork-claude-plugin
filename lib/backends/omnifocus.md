# OmniFocus backend spec

This document is the **single source of truth** for how Meta Work skills
interact with OmniFocus. Any skill that touches OF must reference this file
rather than re-deriving the conventions.

## Degradation order (preferred → fallback)

Every write operation should try, in order:

1. **`mcp__omnifocus__*` MCP tools** — if the MCP is connected and responsive.
2. **TaskPaper render-and-paste** — render the Meta Work Group as TaskPaper,
   write to the clipboard or a temp file, and instruct the user to paste
   into OmniFocus (`File > Import` or `⌘V` into a project).

Skills detect availability in that order; degradation is silent unless the
user asks why a path was chosen. URL-scheme delegation to a user-maintained
OmniFocus plugin was considered as a middle tier and deferred to v2; see
[ADR-0006](../../docs/adr/0006-defer-of-url-scheme-to-v2.md).

## Performance caveat

The reference user's OmniFocus database is large (thousands of folders,
projects, and tags). The existing
`mcp__omnifocus__*` MCP times out on aggregate queries against it:
`list_folders`, `get_project_counts`, `list_perspectives`, and unfiltered
`list_projects` all exceeded the 30-second JXA timeout during planning.

**Discipline for backend code:**

- Never bulk-list the database. Always use narrow filters
  (`folder`, `tag`, `project`, status filters).
- Prefer `get_*` over `list_*` when an ID or exact name is known.
- For aggregate reads that the MCP can't handle, fall back to AppleScript
  via shell:

  ```bash
  osascript -e 'tell application "OmniFocus" to tell default document to <expression>'
  ```

  This worked reliably against the reference DB during planning. Wrap in a
  60-second timeout.

- File an issue against the OF MCP server if a needed query consistently
  times out (track separately).

## Tag mapping for scope axes

The plugin's scope axes correspond to pre-existing OF tag hierarchies in the
reference DB. The OF backend treats these as canonical:

| Plugin axis | OmniFocus tag path | Values |
|---|---|---|
| `horizons_of_focus` | `Horizons of Focus / <value>` | `50,000 ft – Purpose & Principles`, `40,000 ft – Vision`, `30,000 ft – Goals and Objectives`, `20,000 ft – Areas of Focus and Responsibility`, `10,000 ft – Projects`, `Runway` |
| `system_strata` | `System Strata / <value>` | `200 years to 500 years`, `100 years to 200 years`, `50 years to 100 years`, `20 years to 50 years`, `10 years to 20 years`, `5 years to 10 years`, `2 years to 5 years`, `1 year to 2 years`, `3 months to 1 year`, `1 day to 3 months` |
| `vertical_development_stage` | `Vertical Development Stage / <value>` | `Self-Centric`, `Group-Centric`, `Skill-Centric`, `Self-Determining`, `Self-Questioning`, `Self-Actualizing`, `Construct-Aware`, `Unitive` |
| `cynefin_domain` (optional) | `Cynefin Domain / <value>` | `Simple`, `Complicated`, `Complex`, `Chaotic`, `Disordered` |
| `neurological_level` (optional) | `Neurological Level / <value>` | `Environment`, `Behavior`, `Capability`, `Beliefs & Values`, `Identity`, `Spiritual` |

The `metawork-set-up` skill's OF-onboarding step verifies these tag
hierarchies exist; if missing, offers to create them (using the values
above as the canonical labels).

## `Overview (X)` project convention

Area-level Meta Work Groups (i.e., `horizons_of_focus =
20000ft-areas-focus-responsibility`) live in projects literally named
`Overview (Area Name)` — e.g., `Overview (Personal Knowledge Management)`.
See ADR-0005 for the rationale and altitude→container mapping.

The Meta Work action group is created as a child task of the `Overview (X)`
project, with the TaskPaper template structure expanded inside it.

## Template store

The TaskPaper template lives in two places:

- **Canonical:** [`Integral-Productivity/omnifocus-taskpaper-templates/actionGroups/Meta Work.taskpaper`](https://github.com/Integral-Productivity/omnifocus-taskpaper-templates/blob/main/actionGroups/Meta%20Work.taskpaper)
- **Local instance** (in the reference user's OF DB): a project named
  `Meta Work TaskPaper Template` in folder `TaskPaper Templates`. The reference user's OF
  plugin uses this local copy as the instantiation source.

When the plugin writes a new Meta Work Group via MCP, it renders the
canonical TaskPaper template (fetched at install time and cached) and
expands the tasks programmatically. The local instance is used only when
delegating to the reference user's OF plugin via URL scheme.

## Read operations

Common patterns and their MCP/AppleScript implementations:

| Operation | MCP first | AppleScript fallback |
|---|---|---|
| Find all Meta Work Groups | `mcp__omnifocus__search_tasks` with query `"Meta Work"` and `status: "all"` | `flattened tasks whose name is "Meta Work"` |
| Get a specific Meta Work Group's structure | `mcp__omnifocus__get_task` with id | `task id "<id>"`, then `tasks of <task>` recursively |
| Check tag exists | `mcp__omnifocus__search_tags` with name | `(name of tag "<name>") exists` |
| Find Overview projects in a folder | `mcp__omnifocus__list_projects` with `folder: "<folder>"`, filter for `name starting with "Overview ("` | `flattened projects of folder "<folder>" whose name starts with "Overview ("` |

## Write operations

Common patterns:

| Operation | MCP first | TaskPaper paste |
|---|---|---|
| Create an Overview project | `mcp__omnifocus__create_project` with name `"Overview (X)"` and `folder` set | render TaskPaper, prompt user to paste |
| Create the Meta Work action group inside a project | iterate `mcp__omnifocus__create_task` per template node, setting `parent` | render TaskPaper, prompt user to paste |
| Tag a project/task with scope axes | `mcp__omnifocus__add_tag_*` (or set tags on creation) | render TaskPaper with `@tags(...)` |
| Mark today's perspective check complete | `mcp__omnifocus__complete_task` on the auto-done daily-repeat task | (n/a — markdown alternative used) |
