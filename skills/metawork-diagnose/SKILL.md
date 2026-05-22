---
name: metawork-diagnose
description: Use when the Meta Work practice is slipping — skipped reviews, drift from commitments, conflation of intentional Meta Work with escapist meta-work, polarities tilting hard to one pole, a Meta Work Group going stale. Diagnoses the breakdown using the methodology's own frameworks (scope-axis mismatch, developmental-altitude pressure, panarchy-level confusion, fitness-function drift, etc.) and routes to adjacent practices when the root cause sits outside Meta Work's lane.
status: v0.1-stub
---

# metawork-diagnose

> **Status:** v0.1 stub. Implement Phase 8 of the build order alongside
> `metawork-retro`, once breakdown patterns are observable.

## Purpose

When the practice slips, name the breakdown precisely instead of letting it
drift further. Distinguish causes that sit inside Meta Work (re-tunable
within the methodology) from causes that sit outside it (route to the right
adjacent practice).

## Inputs

- Symptom description from the user, or an observation surfaced by
  `metawork-retro`.
- Optional: the specific Meta Work Group(s) involved.

## Outputs

- A diagnosis: which breakdown pattern this matches and why.
- A recommended next move: a specific Meta Work intervention, an adjacent
  practice hand-off, or a scope/altitude/strata re-calibration.

## Diagnostic patterns (v1 starting set)

- **Escapist conflation** — what looks like Meta Work is actually yak-shaving.
  Surface the missed scheduled commitment; ask the 5-whys question:
  "what about the scheduled work felt avoidable in the moment?"
- **Scope-axis mismatch** — a group's `horizons_of_focus` value doesn't match
  the altitude at which the user is actually trying to make decisions. Often
  a `10000ft-projects` group being used to grapple with `20000ft-areas`
  questions, or vice versa.
- **Developmental-altitude pressure** — the prompts in the group are
  pitched above (or below) the user's `vertical_development_stage`. Often
  shows up as "I keep writing the same thing in the polarities section"
  or "the fitness functions feel arbitrary."
- **Panarchy-level confusion** — a parent group's signals are landing in
  the child group instead of being addressed at the parent's level.
- **Fitness-function drift** — measures defined but never checked; or
  checked but always-green (suggesting the threshold is wrong).
- **Polarities tilting** — one pole of a named polarity has run away;
  practice needs a deliberate pull back to the opposite pole. Reference:
  `references/pillars/polarity-management.md`.
- **Practice-itself failure** — the cadence isn't working. Hand off to
  `daily-kaizen-audit` to inspect the practice rather than the content.

## Hand-offs

| Diagnosis | Hand off to |
|---|---|
| Practice-itself failure | `daily-kaizen-audit` |
| Structural breakdown needing RCA | `lean-thinking-praxis` (5 Whys / A3) |
| Developmental pressure beyond Meta Work scope | `vertical-development-scholarship` |
| Inner-work breakdown (e.g., parts conflict surfacing) | (deferred to v2; for now: `positive-disintegration-scholar` for adjacent reading) |
| AI-session friction (this conversation, not the Meta Work) | `ai-session-kaizen-retro` |
