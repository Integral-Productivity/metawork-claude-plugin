---
name: metawork-articulate
description: Use when the user (Kraig or another practitioner) wants to draft or extend the canonical Meta Work methodology document. Interviews the user about a pillar, distinction, breakdown pattern, or integration point, then produces a PR-ready markdown section for the metawork-methodology repo (or, if cloning that repo isn't possible, a markdown file the user can copy in). Closes the loop with metawork-scholar — what articulate writes is what scholar teaches.
status: v0.1-stub
---

# metawork-articulate

> **Status:** v0.1 stub. This is the **first skill to be implemented** per the
> build order — it's the elicitation tool that lets us thicken the methodology
> doc through real practice.

## Purpose

Elicit Meta Work as a methodology from a practitioner (initially Kraig) and
produce PR-ready markdown sections for `metawork-methodology`.

## Inputs

- A topic to articulate: a pillar name, an integration point between pillars,
  a glossary distinction, a breakdown pattern, a daily-rhythm refinement, etc.
- Optionally: existing draft material the user wants to extend.

## Outputs

- A markdown file or section, ready to PR into
  `Integral-Productivity/metawork-methodology`.
- A summary of any new glossary terms introduced (for inclusion in
  `CONTEXT.md` of the plugin repo).
- Optional: notes for the scholar skill on Socratic prompts that worked well
  during the elicitation (these become teaching scaffolds).

## Method

Mirror `grill-with-docs`'s discipline:

1. Interview relentlessly about every aspect of the topic until shared
   understanding.
2. Walk down each branch of the design tree, resolving dependencies one-by-one.
3. For each question, provide a recommended answer.
4. Ask one question at a time; wait for feedback.
5. Challenge against the existing glossary; sharpen fuzzy language;
   stress-test with concrete scenarios; cross-reference with existing
   methodology content.

## Where output goes

If `metawork-methodology` is cloned at `~/GitHub/metawork-methodology/`:

- Pillar drafts → `docs/pillars/<name>.md`
- Methodology narrative additions → `docs/methodology.md`
- New glossary terms → propose CONTEXT.md edits in both repos (methodology
  and plugin)

If not cloned, write the draft to the current working directory with
`metawork-draft-<topic>.md` and instruct the user how to land it.

## Implementation notes

- Use the `superpowers:brainstorming` skill's interview discipline.
- Keep sessions tight (45–90 minutes) so output is review-able as one PR.
- After each session, summarize: what was articulated, what was deferred,
  what new questions emerged.
