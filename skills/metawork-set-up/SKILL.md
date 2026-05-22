---
name: metawork-set-up
description: Use when a user wants to set up a new Meta Work Group for a specific subject — walking them through pick-a-scope (Horizons of Focus + System Strata + Vertical Development Stage), name-the-subject, optional parent-group nesting, and the GTD Natural Planning Model (purpose, vision, scenarios, goals, polarities, systems, measures, brainstorm, organize, next actions), then producing the artifact in the user's configured backend (OmniFocus or markdown). For OmniFocus area-level groups, uses the Overview (X) project naming convention. Reads ~/.metawork/config.json for backend; accepts --state-dir to override.
status: v0.1-stub
---

# metawork-set-up

> **Status:** v0.1 stub. Implement against the markdown backend first
> (Phase 3 in the build order), then the OmniFocus backend (Phase 5).

## Purpose

Create a new Meta Work Group end-to-end: scope axes, subject, parent (if
nested), the full GTD Natural Planning Model walk-through, performance &
health monitoring setup, habits — persisted to the user's backend.

## Inputs

- Subject (prompted if not provided)
- Scope axes:
  - `horizons_of_focus` (controlled vocabulary; see `CONTEXT.md`)
  - `system_strata` (controlled vocabulary)
  - `vertical_development_stage` (controlled vocabulary)
  - Optional: `cynefin_domain`, `neurological_level`
- Life domain (filesystem path or OF folder)
- Optional: parent group reference (for nesting)
- Backend override: `--state-dir` (overrides `~/.metawork/config.json`)

## Outputs

- Markdown backend: a `.md` file at
  `<state-dir>/<life_domain>/<subject>.md` conforming to
  `lib/schema/metawork-group.schema.yaml`.
- OmniFocus backend: per `lib/backends/omnifocus.md` — area-level groups
  produce `Overview (X)` projects with tagged Meta Work action group; other
  altitudes per the altitude→container mapping in ADR-0005.

## Method

1. **Bootstrap config** if `~/.metawork/config.json` doesn't exist — prompt
   for backend + location, write the file, confirm. See `lib/config.md`
   for the schema and precedence rules.
2. **Pick scope** — walk three first-class axes one at a time, with definitions
   and reasonable defaults. Optional classifiers offered last.
3. **Name subject + life domain** — free-text subject, filesystem-path or
   OF-folder for life domain.
4. **Nesting** — offer to declare a parent group from the user's existing
   groups in this backend (skip if none yet).
5. **GTD Natural Planning Model walk-through** — purpose & principles,
   mission & vision, scenarios (at minimum utopia + dystopia), goals &
   outcomes, polarities, systems needed, lagging & leading measures,
   brainstorm, organize (components, dependencies, environment, habits to
   change/build, fitness functions), next actions.
6. **Perspective checks setup** — the four daily Living Forward checks
   (reality, purpose, futures, goals) configured for the backend.
7. **Performance & health monitoring + habits** — capture the user's
   chosen measures and habit definitions.
8. **Persist** — write to backend per `lib/backends/<backend>.md`.
9. **Summarize** — show the user where the Meta Work Group lives and how
   `metawork-morning` will find it.

## Hand-offs

- If the user picks `20000ft-areas-focus-responsibility` and there is no
  existing area folder/dir, prompt them to create one before continuing.
- If the user describes a subject that sounds like an existing pillar
  (e.g., "Polarity Management"), redirect to `metawork-scholar` first.
- If the user struggles with the developmental-altitude axis, offer
  `vertical-development-scholarship` for a deeper exploration.
