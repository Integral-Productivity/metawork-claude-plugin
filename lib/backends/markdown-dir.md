# Markdown directory backend spec

The **default** backend for non-OmniFocus users (and for OmniFocus users who
prefer text-first persistence). State lives as plain `.md` files on the
filesystem.

## Layout

```
<state-dir>/                           # e.g., ~/MetaWork/ or an Obsidian vault root
├── config.json                        # optional per-state-dir override of ~/.metawork/config.json
├── Overview.md                        # 50,000 ft (Purpose & Principles) group, if set up
├── Vision.md                          # 40,000 ft (Vision), if set up
├── Goals.md                           # 30,000 ft (Goals & Objectives), if set up
└── <life_domain>/                     # e.g., Vocational/, Wellness/, Identity/Racial/
    ├── <area>/                        # e.g., Personal Knowledge Management/, Sleep/
    │   ├── Overview.md                # 20,000 ft area-level Meta Work Group
    │   └── <project>.md               # 10,000 ft project-level Meta Work Groups
    └── <project>.md                   # area-less domain-level project groups
```

The `<state-dir>` is whatever the user configured in `~/.metawork/config.json`
or passed via `--state-dir`.

## File format

Each Meta Work Group is a single markdown file with YAML frontmatter
conforming to `lib/schema/metawork-group.schema.yaml`, followed by sections.

```markdown
---
subject: Personal Knowledge Management
parent: ../../Overview.md             # optional, relative path to parent group
life_domain: Vocational/Personal Knowledge Management
horizons_of_focus: 20000ft-areas-focus-responsibility
system_strata: 5-10yr
vertical_development_stage: self-questioning
# optional classifiers
cynefin_domain: complicated
neurological_level: capability
---

# Personal Knowledge Management — Meta Work Group

## Current reality

- ...

## GTD Natural Planning Model

### Purpose & guiding principles

- ...

### Mission & vision

- ...

### Scenarios

#### Utopia

- ...

#### Dystopia

- ...

### Goals & outcomes

- ...

### Polarities

- ...

### Systems needed

- ...

### Measures

#### Lagging

- ...

#### Leading

- ...

### Brainstorm

- ...

### Organize

#### Components & subprojects

- ...

#### Dependencies & resources

- ...

#### Environment conditions

- ...

#### Review artifacts

- ...

#### Habits to change

- ...

#### Habits to build

- ...

#### Backend setup action

- ...

#### Fitness functions

- ...

### Next actions

- ...

## Perspective checks (auto-appended by metawork-morning)

### 2026-05-21

- **Reality:** ...
- **Purpose & principles:** ...
- **Envisioned futures:** ...
- **Goals & objectives:** ...

## Monitor performance

- ...

## Monitor health

- ...

## Habits

- ...
```

## Nesting

Nesting is expressed via the `parent:` frontmatter key, holding a relative
path from this file to the parent group's file. Skills resolve the path at
read time.

## Daily perspective checks

`metawork-morning` **appends** a dated `### <date>` block under
`## Perspective checks` in each group's file. It never edits prior dates.

## Section ordering

Section order is **fixed** for parsing convenience. Skills that read group
files expect the sections in the order above. Writing skills produce them in
that order.

## Atomic writes

Skills writing to group files use the atomic-write pattern (write to a
temp file in the same directory, then `rename`) to avoid leaving a
half-written file on crash.
