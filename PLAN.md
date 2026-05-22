# PLAN — metawork-claude-plugin build order

> **What this file is.** The canonical build order from the v0.1 scaffold
> to a marketplace-ready `v0.1.0`. Every `Phase N` reference in a skill,
> command, agent, ADR, or backend spec resolves here.
>
> **What this file is NOT.** A record of decisions. Decisions live in
> `docs/adr/`. PLAN.md is *execution sequencing* — it tells you what to
> build next and why, not why we chose any particular shape.
>
> **How to update it.** When you do work that lands a phase (or
> meaningfully changes one), edit PLAN.md in the same PR. The build
> order stays truthful only if it moves with the work.

## How to read the phases

- Phases are **strictly ordered by blocking dependency**, not by calendar.
  Phase 4 can land before Phase 3 in time, but its content can't be
  *written* until Phase 2 finishes.
- Each phase lists: **work**, **dependencies**, and an **exit criterion**
  you can answer yes/no to.
- "Parallelizable with Phase N" means the dependencies overlap, not
  that order is irrelevant.
- A phase isn't done until its exit criterion is demonstrably met — not
  when the code merges.

## Phase 0 — Prerequisites

These exist outside the skill/command/agent surface but block everything
that follows. Land them before Phase 1 starts.

- **Stand up `Integral-Productivity/metawork-methodology`.** Create the
  sibling repo with at minimum `docs/methodology.md` (can be a stub
  paragraph) and `docs/pillars/` (can be empty) so
  `.github/workflows/sync-methodology.yml` has something to sync. Wire
  the repo's CI to fire `repository_dispatch` of type
  `metawork-methodology-updated` on push to `main` (referenced in our
  workflow).
- ~~**Write `lib/config.md`**~~ — **done**; see `lib/config.md` for the
  schema, precedence rules, and bootstrap behavior. v1 does not specify
  `naming.area_prefix`; it is documented as a reactive v2 extension hook
  per ADR-0005's "Trigger to revisit."
- **Resolve the OF-plugin URL scheme open question** flagged in
  `lib/backends/omnifocus.md`. Either:
  - **Design it** — document the URL surface, file as ADR-0006, and
    keep the three-tier degradation order intact, OR
  - **Defer to v2** — file a one-paragraph ADR saying "v1 degradation
    goes MCP → TaskPaper paste; URL-scheme path deferred until the OF
    plugin repo is finalized," and remove the URL row from the write-
    operations table in `lib/backends/omnifocus.md`.

**Exit criterion:** `references/` populates successfully via the sync
workflow against the new sibling repo; `lib/config.md` exists and is
referenced from at least one SKILL.md; the OF URL-scheme question is no
longer "open" in `lib/backends/omnifocus.md`.

## Phase 1 — `metawork-articulate` skill body

The elicitation tool. First skill implemented because it's what lets us
thicken `references/methodology.md` in Phase 2.

- Implement against `superpowers:brainstorming` discipline (interview,
  one question at a time, walk down the design tree).
- Output paths per the stub: if `~/GitHub/metawork-methodology/` is
  cloned, write into `docs/pillars/` or `docs/methodology.md`;
  otherwise write `metawork-draft-<topic>.md` to cwd with paste
  instructions.
- BDD scenarios for: drafts a pillar section from scratch; extends an
  existing section; surfaces new glossary terms as proposed CONTEXT.md
  edits.

**Dependencies:** Phase 0.

**Exit criterion:** the skill produces a PR-ready section against the
sibling repo (`gh pr create` succeeds with a non-trivial diff) in one
unattended walk-through of a pillar topic.

## Phase 2 — First articulation pass (dogfood)

A working session, not a code change. Drive `metawork-articulate`
through enough topics that the scholar has material to ground on.

- Draft the integrated narrative `docs/methodology.md` in the sibling
  repo.
- Draft the four anchor pillars (these unblock the most downstream
  work): GTD Natural Planning Model, Living Forward Life Plan,
  Polarity Management, Vertical Development.
- The remaining four pillars (Fitness Functions, Radical Acceptance,
  Panarchy & adaptive cycles, ADDRESSING) can land here or in Phase 4
  alongside scholar tuning.

**Dependencies:** Phase 1.

**Exit criterion:** `references/methodology.md` plus the four anchor
pillars exist in this repo via the sync workflow, and the prose is
thick enough that a non-trivial scholar question doesn't bottom out at
"this isn't articulated yet."

## Phase 3 — `metawork-set-up` skill body (markdown backend)

Implement the 9-step method from the SKILL.md stub against the markdown
backend only. Defer OmniFocus to Phase 5 so we don't blend backend
detail with methodology flow during the first build.

- Bootstrap-config behavior (per `lib/config.md` from Phase 0).
- Scope walk: three first-class axes with controlled vocabularies (per
  `lib/schema/metawork-group.schema.yaml`); optional classifiers last.
- GTD walkthrough produces all sections per `lib/backends/markdown-dir.md`.
- Atomic-write pattern (temp file + `rename`) per the markdown backend
  spec.
- BDD scenarios for: bootstrap config; scope walk; full GTD
  walkthrough; parent nesting; atomic write under crash simulation.
- **First skill to need Cucumber feature placement** — make the call
  here and file ADR-0007 (per the cross-cutting tracks section).

**Dependencies:** Phase 0 (`lib/config.md`). Independent of Phases 1, 2.

**Exit criterion:** a markdown-backend user can set up an area-level
group at `<state-dir>/<life_domain>/<area>/Overview.md` and a
project-level group at `<state-dir>/<life_domain>/<area>/<project>.md`,
both schema-valid and with the parent reference resolving.

## Phase 4 — `metawork-scholar` skill body

Parallelizable with Phase 3 once Phase 2 lands.

- Socratic by default; switch to direct exposition only when asked.
- Ground every answer in `references/methodology.md`, `references/pillars/`,
  `CONTEXT.md`.
- Hand-offs per the SKILL.md stub table. When a question crosses into
  adjacent territory, name the hand-off rather than absorbing it.
- Honesty rule: if the methodology doc doesn't cover a question, say
  so and offer `metawork-articulate`.

**Dependencies:** Phase 2.

**Exit criterion:** the scholar answers a Polarity-Management-meets-
Vertical-Development question grounded in `references/` only — no
fabrication beyond the source material.

## Phase 5 — `metawork-set-up` skill body (OmniFocus backend)

Layer OmniFocus support onto the markdown-first skill. Two-backend
parity is the trigger condition recorded in ADR-0002 for considering
the adapter MCP, so this phase matters strategically.

- Tag-hierarchy verification + creation per `lib/backends/omnifocus.md`.
- `Overview (X)` convention per ADR-0005, including the altitude →
  container mapping table.
- Degradation order: MCP → URL scheme (if Phase 0 designed it) →
  TaskPaper paste.
- Respect the performance discipline in `lib/backends/omnifocus.md`:
  no bulk-list, AppleScript fallback wrapped in 60s timeout, file an
  issue against the OF MCP if a needed query times out.

**Dependencies:** Phase 3 (markdown patterns established).

**Exit criterion:** Kraig's reference DB accepts a new area-level and
project-level Meta Work Group via the skill without hand-editing in
OmniFocus.

## Phase 6 — `metawork-morning` skill body

Both backends supported. Implements the daily perspective-check loop
per the four Living Forward checks.

- Load active groups (with filtering for life domain / altitude /
  named subset) — never bulk-list OF.
- Per-group: present `current_reality` summary + four checks; record
  responses.
- OmniFocus: complete today's auto-done perspective-check tasks for
  user-selected groups.
- Markdown: append a dated `### <date>` block under `## Perspective
  checks` (never edit prior dates).
- Pacing cap: skip groups already checked today; default to 7±2 groups
  per session.

**Dependencies:** Phase 3 and Phase 5.

**Exit criterion:** one morning's run across Kraig's active groups
completes without exhausting the conversation's context window, and
both backends' records reflect the session correctly.

## Phase 7 — Real dogfooding pass

A working stretch, not a code change. The point: get real breakdown
signals before designing the diagnose/retro patterns in Phase 8.

- Use `metawork-set-up` to instantiate Meta Work Groups across Kraig's
  life domains: Vocational, Wellness, Familial, Spiritual, Existential,
  plus ADDRESSING identity domains as appropriate.
- Run `metawork-morning` daily for at least a week.
- Log breakdown patterns observed to `docs/observed-breakdowns.md` —
  this becomes the v1 pattern catalog Phase 8 designs against.
- Loop unresolved methodology gaps back into `metawork-articulate` (a
  small Phase 2 mini-pass per gap).

**Dependencies:** Phase 6.

**Exit criterion:** at least 7 real Meta Work Groups in active use for
a week, with `docs/observed-breakdowns.md` populated by lived signals
(not speculation).

## Phase 8 — `metawork-retro` + `metawork-diagnose` skill bodies

Implement against the breakdown patterns observed in Phase 7. The stubs
already enumerate a starting set of diagnostic patterns — replace those
with the patterns that actually showed up.

- `metawork-retro`: three-section summary (Intentional Meta Work
  performed / Escapist meta-work surfaced / Open signals); routing to
  diagnose, lean-thinking-praxis, daily-kaizen-audit per the stub.
- `metawork-diagnose`: name the breakdown precisely; distinguish
  in-methodology causes from adjacent-practice hand-offs; reference
  `docs/observed-breakdowns.md` for the v1 pattern catalog.

**Dependencies:** Phase 7.

**Exit criterion:** a retro session on a real day correctly
distinguishes intentional Meta Work from escapist meta-work; diagnose
names a real breakdown observed in Phase 7 from the user's symptom
description alone.

## Phase 9 — Subagents (`metawork-scholar`, `metawork-orchestrator`)

Extract subagents once the delegation surface is clear from running
skills in conversation.

- `metawork-scholar` (subagent): read-only Socratic teacher;
  separately-contexted so long teaching arcs don't consume the main
  conversation. Hand-offs named explicitly in responses; main agent
  routes.
- `metawork-orchestrator`: bulk and parallel operations across many
  groups. Backend behavior respects the OF performance discipline.

**Dependencies:** Phases 4, 5, 6 (scholar skill stable; set-up and
morning stable enough to drive programmatically).

**Exit criterion:** a bulk-morning operation across 7+ groups runs in
the orchestrator without consuming the main conversation; a deep
multi-pillar teaching arc runs in the scholar subagent without
polluting main context.

## Phase 10 — v0.1.0 release

Public-ready. Replaces the "v0.1.0 post-bootstrap" promise in README.

- Marketplace listing (Claude Code plugin marketplace once it's
  available; until then, document the `git clone ~/.claude/plugins/`
  install path with a real, tested invocation).
- Install + first-run docs at the README level.
- CHANGELOG seeded with the v0.1 phases.
- Version bump in `plugin.json` from `0.1.0-alpha` to `0.1.0`;
  `status.stability` to `beta` or `stable` per actual confidence.
- Tag the release; cut release notes.

**Dependencies:** Phases 1, 3–6, 8, 9.

**Exit criterion:** a clean clone of the plugin into a fresh
`~/.claude/plugins/` works end-to-end for both backends, per the
documented install steps.

## Cross-cutting tracks

These run alongside every phase. They're not "one phase" — they're
discipline.

- **BDD acceptance per skill.** Cucumber outer loop, `node:test` +
  `assert/strict` inner loop, per `~/.claude/CLAUDE.md`. First
  Cucumber feature lands in Phase 3 — file ADR-0007 for placement
  (per-skill `features/` vs. top-level `features/`) at that moment.
- **ADR discipline.** File an ADR when an architectural decision is
  made. Route per `~/GitHub/CLAUDE.md`: org-wide architecture →
  `software-architecture-excellence/docs/adr/` (SAE-NNN); DevOps/CI →
  `devops-excellence/docs/adr/` (ADR-NNN); plugin-scoped → this repo's
  `docs/adr/` (NNNN-).
- **Branch naming.** Claude-authored work uses `claude/<slug>` to
  enable auto-merge on green CI; no draft PRs.
- **Conventional Commits everywhere** (`feat:`, `fix:`,
  `chore(scope):`, `docs:`, `ci:`). No `--no-verify`; no skipping
  fitness checks.
- **Truthful PLAN.md.** Update this file in the same PR as the work
  that moves a phase forward.
- **Skill contribution discipline.** At the end of any session that
  modifies a skill, complete the contribution flow at
  `~/GitHub/skills/docs/contribution-workflow.md`.

## Open questions

Named explicitly so future-Kraig can see what's unresolved.

- **OF plugin URL scheme** — design now (ADR-0006) or defer to v2?
  Forces a decision in Phase 0.
- **`omnifocus-taskpaper-templates` repo** — `lib/backends/omnifocus.md`
  treats this as canonical. Is it assumed already standing, or does
  Phase 0 also confirm/stand it up?
- **Cucumber feature placement** — per-skill `features/` directory, or
  one top-level `features/` tree? Decided in Phase 3 via ADR-0007.
- **Adapter MCP trigger** — per ADR-0002, revisit when a second
  backend reaches feature parity (Phase 5 + Phase 6) OR a non-Claude
  runtime needs to drive Meta Work flows. Track here so we don't miss
  the trigger condition.
