---
name: metawork-morning
description: Use as part of a morning practice — runs the four Living Forward daily perspective checks (acknowledge reality / aligned with purpose & principles / aligned with envisioned futures / aligned with goals & objectives) across the user's active Meta Work Groups. Records outcomes back to the backend. For OmniFocus users this maps to the daily auto-done perspective-check tasks in each Meta Work action group; for markdown users, appends to the group file with a dated entry.
status: v0.1-stub
---

# metawork-morning

> **Status:** v0.1 stub. Implement Phase 6 of the build order, after both
> backends and `metawork-set-up` are in place.

## Purpose

Drive the user through perspective checks across their active Meta Work
Groups, in priority order. Record outcomes so the practice has a trail.

## Inputs

- Backend config from `~/.metawork/config.json` (or `--state-dir` override)
- Optional: filter by life domain, by Horizons of Focus altitude, or by a
  named subset of groups (e.g., "just Vocational" or "just Identity").

## Outputs

- For each active group, a dated record of the four perspective checks with
  the user's response (acknowledged / drifted / blocked / re-aligned / etc.).
- A summary: groups visited, groups skipped (and why), anything that
  surfaced for `metawork-retro` later.

## Method

1. Load active Meta Work Groups from backend (cap at a sensible per-session
   number; offer to filter if too many).
2. For each group, present its `current_reality` summary + the four
   perspective check prompts:
   - "Am I acknowledging reality here?"
   - "Am I aligned with my purpose & principles?"
   - "Am I acting in alignment with my envisioned futures?"
   - "Am I acting in alignment with my goals & objectives?"
3. Record the response. Surface tensions, drifts, or required re-alignments
   to a per-session journal.
4. End-of-session summary: any signals that warrant `metawork-retro`,
   `metawork-diagnose`, or scheduling specific Meta Work.

## Backend behavior

- **OmniFocus:** mark today's auto-done perspective-check tasks complete
  for the user's chosen groups. Use the existing daily-repeat structure
  in the Meta Work action group.
- **Markdown:** append a `## <date>` section to each group file with the
  four checks and the user's response. Schema documented in
  `lib/backends/markdown-dir.md`.

## Pacing

A morning practice should be **light**: skip groups already checked today;
don't push the user to handle more than 7±2 groups in one session.
