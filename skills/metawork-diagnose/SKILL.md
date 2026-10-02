---
name: metawork-diagnose
description: Use when the Meta Work practice is slipping — skipped reviews, drift from commitments, conflation of intentional Meta Work with escapist meta-work, polarities tilting hard to one pole, a Meta Work Group going stale. Diagnoses the breakdown using the methodology's own frameworks (scope-axis mismatch, developmental-altitude pressure, panarchy-level confusion, fitness-function drift, etc.) and routes to adjacent practices when the root cause sits outside Meta Work's lane.
status: v0.1-stub
---

# metawork-diagnose

> **Status:** v0.1 stub. Implement Phase 8 of the build order alongside
> `metawork-retro`, once breakdown patterns are observable.
> **Implemented:** the ontology validation step below (issue #39,
> ADR-0008). The diagnostic patterns are still prose.

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
- The ontology validation result for the group(s) involved, including any
  SHACL violations (see below).

## Validate against the ontology (required before any diagnosis)

When the Meta Work Group(s) involved are markdown-backend files, validate
them before reporting a diagnosis. Pass the group file(s), or the state
directory to check every group in it:

```bash
"${CLAUDE_PLUGIN_ROOT}/lib/ontology/validate-group.sh" "<group file or state dir>" [...]
```

The script lifts each group's frontmatter (and its `parent:` chain) to RDF
and runs every SHACL shape in the vendored metawork-ontology snapshot; new
shapes added upstream apply after the next ontology sync with no change
here. Use `--format json` if you need the violations as data
(`status`, `violations[].file|field|value|message`).

- **Exit 0 — conforms.** Say so in one line in the diagnosis output.
- **Exit 1 — SHACL violations.** Include a **Ontology violations** section in
  the diagnosis that shows the `FAIL:` block as printed: for each violation
  the file, field, value, and message. Treat each as evidence: a value
  outside a scheme or a missing axis often *is* the breakdown (for example a
  scope-axis mismatch). Do not present the group as healthy.
- **Exit 2 or 3 — not validated.** Show the output and state plainly that
  the group could not be validated and why (input error, or ontology tool
  unavailable with the install fix it names). Do not report the diagnosis
  as complete or the group as conforming.

OmniFocus-backend groups are not covered by the lift yet; say that rather
than implying validation ran.

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
