---
name: metawork-retro
description: Use at the end of a session or day to retrospect on Meta Work signals — what surfaced, what got scheduled, what got escapist (yak-shaved as work-about-work-as-avoidance), what got intentionally addressed. Routes to metawork-diagnose if a pattern of drift appears, or to lean-thinking-praxis if a structured root-cause analysis is warranted.
status: v0.1-stub
---

# metawork-retro

> **Status:** v0.1 stub. Implement Phase 8 of the build order, once real
> session signals are visible.

## Purpose

Close the loop on a Meta Work practice session or day. Distinguish intentional
Meta Work from escapist meta-work; surface what to schedule, what to defer,
what to investigate.

## Inputs

- Session context: this conversation, or a date range, or "today"
- Backend config from `~/.metawork/config.json`

## Outputs

- A retro summary with three sections:
  1. **Intentional Meta Work performed** — what was actually planned and
     executed against the methodology
  2. **Escapist meta-work surfaced** — yak-shaving / work-about-work that
     pulled attention away from scheduled commitments (the lowercase sense)
  3. **Open signals** — drifts, breakdowns, or polarities that need follow-up
- Optional: drafts of next-actions to schedule, with routing suggestions.

## Method

1. Survey the session/day for Meta Work activity:
   - Skills invoked (`metawork-*`)
   - Meta Work Groups touched
   - Perspective-check outcomes from `metawork-morning`
2. Apply the intentional-vs-escapist test to each activity:
   - Was this planned, or did it pull attention away from a prior commitment?
   - What was the felt-sense quality (compelling / draining / re-aligning)?
3. Identify open signals — drifts, conflicts, polarities tilting, fitness
   functions out of bounds.
4. Recommend next moves:
   - Schedule specific Meta Work to address a signal
   - Hand off to `metawork-diagnose` if drift is patterned
   - Hand off to `lean-thinking-praxis` if a structured RCA is warranted
   - Hand off to `daily-kaizen-audit` if the practice itself needs tuning

## Hand-offs

- Patterned drift → `metawork-diagnose`
- Structured RCA → `lean-thinking-praxis`
- Practice tuning → `daily-kaizen-audit`
- Session-level retro (the AI conversation itself, not Meta Work) →
  `ai-session-kaizen-retro` (already in the user's skill ecosystem)
