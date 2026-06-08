# 4. Multi-axial scope model for Meta Work Groups

Date: 2026-05-21

## Status

Accepted

## Context

A Meta Work Group needs to express **what scope of work it addresses**. The
original plan assumed a single panarchy-derived enumeration:
`whole-self | domain | area | project | identity-facet`.

Inspection of the reference OmniFocus database revealed that the actual
practice uses **three independent axes** (plus two optional classifiers), each
backed by its own dedicated tag hierarchy already in active use:

- **Horizons of Focus** (David Allen / GTD) — `50,000 ft Purpose & Principles`
  through `Runway`. The *granularity* axis: how zoomed-in this Meta Work
  Group's altitude of concern is.
- **System Strata** (a custom synthesis) — `200–500 yr` through
  `1 day – 3 mo`. The *temporal horizon* axis: how far out the consequences
  of this work extend.
- **Vertical Development Stage** (an 8-stage synthesis after Kegan /
  Cook-Greuter) — `Self-Centric` through `Unitive`. The *developmental
  altitude* axis: the meaning-making stage from which the practitioner is
  operating on this work.

These three axes are *orthogonal* in practice: a `10,000 ft Projects`
granularity group can have a `1–2 yr` strata horizon and be operated at a
`Self-Questioning` developmental altitude. Collapsing them into a single
enumeration loses meaningful information that the practitioner uses.

Two optional classifiers also surfaced as actively-tagged dimensions:

- **Cynefin Domain** (Snowden) — `Simple` / `Complicated` / `Complex` /
  `Chaotic` / `Disordered`
- **Neurological Level** (Dilts / NLP) — `Environment` through `Spiritual`

These are not always relevant to a Meta Work Group, so they are optional.

## Decision

A Meta Work Group's scope is **multi-axial**. The schema
(`lib/schema/metawork-group.schema.yaml`) declares the three first-class axes
as required (or with explicit defaults) and the two classifiers as optional.

The `metawork-set-up` skill prompts for each axis individually using the
controlled vocabularies above. The OmniFocus backend maps each axis value to
the corresponding pre-existing OF tag (`Horizons of Focus : <value>`,
`System Strata : <value>`, etc.); the markdown backend stores each axis as a
top-level YAML key in frontmatter.

The original single-enumeration "panarchy scope" is **not** dropped — it lives
on as the `parent` reference (for nesting) plus `life_domain` (for
organizational placement). The structural intuition behind it (project nests
under area nests under domain nests under whole-self) is preserved through
parent-references, not enumeration values.

## Consequences

**Positive:**

- The data model reflects how Meta Work is actually practiced in the
  reference database.
- The three axes give the plugin three rich vocabularies that skill prompts
  can lean on — e.g., `metawork-diagnose` can ask "is this a vertical
  development stage issue or a Cynefin domain mismatch?" with precision.
- Adopters who don't yet know these frameworks have controlled vocabularies
  with embedded teaching opportunities (each enum value can be a doc link).

**Negative:**

- More upfront cognitive load on first-time users — three axes to pick from
  instead of one. Mitigation: `metawork-set-up` walks the user through them
  one at a time with definitions and reasonable defaults.
- Skills depend on the axis vocabularies; renaming or restructuring an axis
  is a breaking change.
- The methodology doc must teach all three frameworks coherently (work for
  `metawork-articulate`).

**Trigger to revisit:** if real use shows one axis is rarely set or rarely
informs decisions, consider demoting it to "optional classifier" status.
Conversely, if a new axis emerges as load-bearing (e.g., AQAL quadrant when
Integral Theory enters v2), promote it via a new ADR.
