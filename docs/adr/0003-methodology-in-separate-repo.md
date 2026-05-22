# 3. Methodology lives in a separate repo

Date: 2026-05-21

## Status

Accepted

## Context

Meta Work is both **a software-shaped artifact** (this Claude Code plugin) and
**a body of practice** that could plausibly become a book, a course, a public
site, or material for non-Claude tooling. The methodology has its own intended
audience (practitioners, coaches, students of integral productivity) that is
broader than this plugin's audience (Claude Code users).

Three options were considered:

1. **One repo, all in `references/`** — simplest; plugin and methodology evolve
   together; lowest indirection.
2. **Two repos, plugin pulls methodology at build time** — separation of
   concerns; methodology is portable; cost is a sync mechanism.
3. **Two repos, methodology imported as a git submodule** — similar to (2) but
   without a sync mechanism; users get raw submodule semantics on clone.

Option (1) entangles methodology evolution with plugin engineering velocity and
makes it harder to repurpose the methodology in a non-plugin context.
Option (3) has rough edges with plugin marketplace install (submodules require
manual init).

## Decision

The methodology lives in
[`Integral-Productivity/metawork-methodology`](https://github.com/Integral-Productivity/metawork-methodology).
The plugin pulls it into `references/` at build time via a GitHub Actions
workflow (`.github/workflows/sync-methodology.yml`):

1. On a daily schedule and on manual `workflow_dispatch`, clone
   `metawork-methodology@main`.
2. Copy `docs/methodology.md` and `docs/pillars/*.md` into the plugin's
   `references/` and `references/pillars/`.
3. If the snapshot differs from the committed `references/`, open a PR titled
   `chore(references): sync methodology @ <sha>`.
4. PR is reviewed and merged by a maintainer (no auto-merge — methodology
   changes deserve human eyes on the plugin side).

Users installing the plugin from the marketplace get the snapshot that shipped
with the plugin release; they don't need to clone or init anything.

## Consequences

**Positive:**

- Methodology can be authored, reviewed, and versioned independently of the
  plugin's engineering pace.
- A future docs site, book repo, or course-material repo can consume the
  methodology directly, without depending on the plugin.
- The plugin always ships a frozen snapshot — install does not depend on
  GitHub being reachable.

**Negative:**

- A sync workflow is one more thing to maintain.
- A breaking methodology change (e.g., a renamed pillar) requires coordinated
  PRs across two repos.
- Newcomers must learn that `references/` is generated and edits there will
  be overwritten — the source-of-truth banner at the top of each file is the
  countermeasure.

**Trigger to revisit:** if methodology drifts faster than plugin can keep up
(e.g., methodology is iterating weekly while plugin is stable), consider
whether the sync should auto-merge or whether the plugin should consume
`metawork-methodology` via npm package semver.
