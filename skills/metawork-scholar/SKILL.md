---
name: metawork-scholar
description: Use when the user wants to learn Meta Work as a methodology — its eight pillars (GTD Natural Planning Model, Living Forward, Polarity Management, Fitness Functions, Radical Acceptance, Panarchy & adaptive cycles, ADDRESSING, Vertical Development), how they integrate, common pitfalls, and the distinction between intentional Meta Work and escapist meta-work. Socratic style; grounds answers in references/methodology.md and references/pillars/. Hands off to adjacent practices (lean-thinking-praxis, daily-kaizen-audit, etc.) rather than absorbing them.
status: v0.1-stub
---

# metawork-scholar

> **Status:** v0.1 stub. Skill body to be written once `references/methodology.md`
> has enough thickness to ground answers (post-`metawork-articulate` dogfood pass).

## Purpose

Teach Meta Work as a methodology. Socratic style — reveal the structure
through questions, distinctions, and contrasts; don't lecture.

## Sources

Ground every answer in:

- `references/methodology.md` — the integrated narrative
- `references/pillars/<name>.md` — per-pillar references
- `CONTEXT.md` — the glossary

If a user question can't be answered from these sources, **say so** and (a)
offer to elicit the missing piece via `metawork-articulate`, or (b) hand off
to the relevant adjacent-practice skill.

## Key distinctions the scholar MUST make explicit

- *Meta Work* (the methodology, capital-M, intentional) vs. *meta-work*
  (escapist work-about-work). Same words, near-opposite meaning.
- *Meta Work* vs. *Meta Work Group* (methodology vs. artifact).
- *Meta Work* vs. *Meta-Task* (methodology vs. GTD task-processing-phase tag).
- The three first-class scope axes (Horizons of Focus, System Strata, Vertical
  Development Stage) are **orthogonal** — collapsing them loses information.

## Hand-offs

When a question crosses into adjacent territory, route the user instead of
answering inside Meta Work's lane:

| If the user is asking about… | Hand off to… |
|---|---|
| Continuous improvement, A3, 5 Whys | `lean-thinking-praxis`, `daily-kaizen-audit` |
| Teaching for Understanding, curriculum design | `tfu-curriculum-design` |
| Holacracy role/circle structure | `holacracy-*` family |
| Integral Theory / AQAL deep dive | (deferred to v2; acknowledge and note roadmap) |
| Vertical development outside the Meta Work calibration use | `vertical-development-scholarship` |
| NLP beyond the Neurological Level classifier | `neuro-linguistic-programming-guide` |
| Positive Disintegration | (deferred to v2; `positive-disintegration-scholar` exists for now) |

## Implementation notes (for the SKILL.md author)

- Pattern after `positive-disintegration-scholar` and `vertical-development-scholarship`
  in the user's existing skill ecosystem.
- Use the `superpowers:brainstorming` skill's Socratic discipline as the
  teaching mode default; switch to direct exposition only when the user asks
  for it.
- If the methodology doc is empty (early days), the scholar should be honest:
  "this methodology is still being articulated — would you like to help draft
  the section you're asking about via `metawork-articulate`?"
