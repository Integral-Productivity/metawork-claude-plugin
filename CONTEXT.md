# CONTEXT — metawork-claude-plugin glossary

This file is the **shared glossary** for the plugin. Whenever a term is introduced
in code, skills, references, or ADRs, it should match the definition below. If a
new usage forces a refinement, update this file in the same PR.

> CONTEXT.md is intentionally **devoid of implementation details, decisions, or
> rationale**. It is a glossary. Decisions live in `docs/adr/`. Implementation
> lives in `skills/`, `commands/`, `agents/`, `lib/`, and `references/`.

## Core terms

### Meta Work (the methodology)

A structured practice of *intentional* planning, monitoring, and
perspective-maintenance, applied per `(scope, subject)`. Capital-M; two words.
Integrates eight v1 pillars (see `references/pillars/`). The methodology is
articulated in the sibling repo `Integral-Productivity/metawork-methodology`
and synced into this plugin's `references/` directory.

**Not to be confused with:**

- **meta-work** (lowercase, hyphenated) — the casual, escapist sense of
  *yak-shaving* and *work-about-work-as-avoidance*. Same words, near-opposite
  meaning. The plugin's `metawork-scholar` skill must teach this distinction
  explicitly because new users (and even seasoned practitioners) conflate them.
- **Meta-Task** — Kraig's GTD-style task-processing-phase tag in OmniFocus
  (with four children: Task Preprocessing, Project Preprocessing, Task
  Processing, Task Postprocessing). Unrelated to Meta Work the methodology.
  Conflation risk; recorded here to prevent it.

### Meta Work Group (the artifact)

A per-`(scope, subject)` instance of the methodology. In code: `metawork-group`.
In OmniFocus: an action group named `Meta Work` attached to a project. In the
markdown backend: a `.md` file with YAML frontmatter conforming to
`lib/schema/metawork-group.schema.yaml`.

Meta Work Groups can be **nested** via a `parent` reference (project nests under
area, area nests under domain, etc.) — this is how the panarchy / adaptive-cycles
pillar is expressed in the data model.

### Subject

The free-text name of *what* this Meta Work Group is about. Examples:
`"Self"`, `"Career"`, `"Praxis platform"`, `"Race"`, `"Sleep"`.

### Scope (multi-axial)

A Meta Work Group is positioned on at least **three first-class axes** plus two
**optional classifiers**. See `references/methodology.md` and ADR-0004 for the
reasoning. Values are stable enumerations; the plugin treats them as a typed
vocabulary, not free text.

| Axis | Kind | Values |
|---|---|---|
| `horizons_of_focus` | first-class | `50000ft-purpose-principles`, `40000ft-vision`, `30000ft-goals-objectives`, `20000ft-areas-focus-responsibility`, `10000ft-projects`, `runway` |
| `system_strata` | first-class | `200-500yr`, `100-200yr`, `50-100yr`, `20-50yr`, `10-20yr`, `5-10yr`, `2-5yr`, `1-2yr`, `3mo-1yr`, `1day-3mo` |
| `vertical_development_stage` | first-class | `self-centric`, `group-centric`, `skill-centric`, `self-determining`, `self-questioning`, `self-actualizing`, `construct-aware`, `unitive` |
| `cynefin_domain` | optional | `simple`, `complicated`, `complex`, `chaotic`, `disordered` |
| `neurological_level` | optional | `environment`, `behavior`, `capability`, `beliefs-values`, `identity`, `spiritual` |

### Life domain

The *organizational* dimension — where this Meta Work Group lives. Distinct
from the scope axes. In the OmniFocus reference DB, life domains are top-level
folders (Vocational, Wellness, Familial, Spiritual, Existential, ...). Identity
domains via the ADDRESSING model (Racial, Genderal, Sexual, ...) are also
first-class life domains. In the markdown backend, life domain maps to a
filesystem path (e.g., `Vocational/Praxis`, `Identity/Racial`).

### Overview pattern (`Overview (X)`)

The canonical naming convention for **area-level** Meta Work Groups in the
OmniFocus backend: a project literally named `Overview (Area Name)` (e.g.,
`Overview (Personal Knowledge Management)`, `Overview (Vertical Development)`).
The Meta Work action group lives inside this project. See ADR-0005.

In the markdown backend, the equivalent is `<area>/Overview.md`.

### Backend

Where Meta Work Group state lives for a user. v1 supports two backends:

- **OmniFocus** (preferred for OF users): state lives as OF projects, action
  groups, and tags. Skills compose on top of the existing `mcp__omnifocus__*`
  tools, with degrading fallback to a Kraig-maintained OF plugin via URL scheme,
  and final fallback to TaskPaper render-and-paste.
- **Markdown directory**: state lives as `.md` files on the filesystem, one per
  Meta Work Group, with YAML frontmatter conforming to
  `lib/schema/metawork-group.schema.yaml`.

Future backends (v2+): Obsidian vault, Things, Todoist, Notion.

### Configuration

The per-user file at `~/.metawork/config.json` that selects the backend
and (for the markdown backend) the state directory. Skills resolve
configuration via a precedence chain: CLI flag (`--state-dir`) →
per-state-dir `<state-dir>/config.json` → global default. Schema and
precedence rules live in `lib/config.md`.

### State directory

The filesystem root for the markdown backend's state, referenced in
prose as `<state-dir>` and as the `state_dir` field in
`~/.metawork/config.json`. Examples: `~/MetaWork`, an Obsidian vault
root. Irrelevant to the OmniFocus backend. See `lib/backends/markdown-dir.md`
for the directory layout and `lib/config.md` for how it is configured.

## Convention notes (not glossary terms)

- **`metawork-*`** is the artifact-naming convention inside the plugin (no
  internal dash). The methodology in prose is **"Meta Work"** (two words).
- **`Stations`** is a tag in Kraig's reference OmniFocus database used as a
  *tool-context* marker (Agile / Airtable / Trello / OmniFocus). It indicates
  *where* a task happens, NOT a panarchy or scope level. The TaskPaper template
  uses `@tags(Stations : OmniFocus)` to mean "this task is done while at the
  OmniFocus station." Recorded here to prevent misinterpretation.

## Pillars

The eight v1 pillars of Meta Work. Each has a dedicated reference at
`references/pillars/<name>.md`:

1. GTD Natural Planning Model (David Allen)
2. Living Forward Life Plan (Hyatt / Harkavy)
3. Polarity Management (Barry Johnson)
4. Fitness Functions (Ford / Parsons / Kua — applied personally)
5. Radical Acceptance / current-reality awareness
6. Panarchy & adaptive cycles (Resilience Alliance)
7. ADDRESSING model (Pamela Hays)
8. Vertical development (Kegan / Cook-Greuter; Kraig's 8-stage synthesis)

Deferred to v2+: Holacracy, Integral Theory / AQAL, Positive Disintegration.

Adjacent practices (plugin hands off, does not absorb): Lean / Kaizen, Teaching
for Understanding, Liberatory Learning, NLP (beyond the Neurological Level
classifier), 5 Whys / A3.
