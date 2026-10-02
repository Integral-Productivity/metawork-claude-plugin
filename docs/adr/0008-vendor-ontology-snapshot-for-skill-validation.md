# 8. Skills validate groups against a vendored ontology snapshot

Date: 2026-10-02

## Status

Accepted

Follows the pattern of [ADR-0003](0003-methodology-in-separate-repo.md) and
[ADR-0007](0007-github-app-token-for-cross-repo-ci.md).

## Context

[metawork-ontology ADR-0003](https://github.com/Integral-Productivity/metawork-ontology/blob/main/docs/adr/0003-first-consumer-is-the-plugin.md)
names this plugin as the ontology's first consumer. Its item 2 requires that
`metawork-set-up` and `metawork-diagnose` run `tools/metawork_ontology.py`
`lift` + `validate` (or an equivalent) on a markdown-backend Meta Work Group
before reporting success, instead of trusting the enum strings. Issue #39
tracks this, and asks that the way the skills reach the ontology tool be
written down.

The skills run on a user's machine, inside Claude Code, from an installed
plugin. The ontology lives in a separate public repo,
`Integral-Productivity/metawork-ontology`, as a Python script plus Turtle
files (`ontology/metawork.ttl`, `shapes/*.ttl`). It needs `rdflib`,
`pyshacl` and `pyyaml`. It is not packaged for pip (no `pyproject.toml`).

Options considered:

1. **Vendored snapshot, synced like the methodology.** Copy the tool, the
   ontology and every `shapes/*.ttl` into `lib/ontology/vendor/`, refreshed by
   a scheduled workflow that opens a PR.
2. **pip-installed package.** Publish metawork-ontology to PyPI or GitHub
   Packages and `pip install` it.
3. **Checkout at runtime.** Clone or pull metawork-ontology into
   `~/.metawork/` the first time a skill validates.

Weighed against what the skills need:

| | Vendored (1) | pip (2) | Runtime clone (3) |
|---|---|---|---|
| Works without the ontology repo cloned | yes | yes, after install | needs network on first use |
| Version pinned to the plugin release | yes (snapshot SHA) | yes, if pinned | no; drifts with `main` unless pinned by hand |
| New shapes reach the skills | next sync PR, no plugin change | needs a new release in the ontology repo | immediately, unreviewed |
| Work required in the ontology repo | none | packaging + release process | none |
| Python deps | user's Python, or `uv` | same | same |

The Python dependencies are the same problem under every option, so they do
not decide between them.

## Decision

**Vendor a snapshot (option 1).**

- `scripts/sync-ontology.sh <checkout>` copies `tools/metawork_ontology.py`,
  `ontology/*.ttl`, **every** `shapes/*.ttl`, `requirements.txt` and
  `LICENSE.md` into `lib/ontology/vendor/`, and writes `SNAPSHOT.md` with the
  source SHA. Files under `vendor/` are never hand-edited.
- `.github/workflows/sync-ontology.yml` runs it daily (and on
  `workflow_dispatch` / `repository_dispatch: metawork-ontology-updated`) and
  opens a `chore(ontology): sync metawork-ontology @ <sha>` PR when the
  snapshot changes. The ontology repo is public, so the checkout needs no
  token; the PR is opened with the existing sync App token (ADR-0007) so that
  CI runs on it. A maintainer merges it; a new shape changes what the skills
  accept, which deserves review.
- Skills call one entry point, `lib/ontology/validate-group.sh`, which runs
  `lib/ontology/validate_group.py`:
  - **Ontology resolution:** `--ontology-dir DIR` → `$METAWORK_ONTOLOGY_DIR`
    → the vendored snapshot. The override exists for ontology development and
    for CI's upstream-main leg.
  - **Shapes:** every `shapes/*.ttl` in the resolved ontology, loaded by the
    helper itself. The upstream `load()` reads a single named shapes file, so
    relying on it would silently skip a newly added shape.
  - **Lift + validate:** upstream `frontmatter_to_rdf` and `validate`. The
    helper lifts each file under a per-directory base IRI, follows the
    `parent:` chain, and rewires parent links to the parent file's node, so
    nesting is checked against real files and two `Overview.md` files in
    different directories do not collide.
  - **Python:** `$METAWORK_PYTHON`/`python3` if it can import the deps;
    otherwise `uv run --with rdflib --with pyshacl --with pyyaml`; otherwise
    exit 3.
  - **Exit codes:** 0 pass, 1 SHACL violations, 2 input error, 3 tool
    unavailable. Exit 3 is never a pass; the skills report it as "not
    validated" and do not report success.
- CI (`validate-plugin.yml`, job `ontology-validate`) runs
  `tests/ontology/` against the vendored snapshot and against
  `metawork-ontology@main`, proving the helper passes a conforming group tree
  and fails each violating fixture.

## Consequences

**Positive:**

- Validation works offline on an installed plugin; nothing to clone.
- What a plugin release accepts is pinned to a recorded ontology SHA.
- A new upstream shape (for example the scope-axis-mismatch shape from
  ontology ADR-0003 item 3) is enforced after the next sync PR merges, with
  no helper or skill change. A test proves an extra `shapes/*.ttl` is picked
  up.
- The upstream-main CI leg shows a shape change that would break the skills
  before the sync PR is merged.

**Negative:**

- One more sync workflow to maintain, and the plugin can lag the ontology by
  up to a day plus review time.
- The user needs Python with three packages, or `uv`. Without either the
  skills cannot validate and say so (exit 3) rather than pass.
- The helper works around two behaviours of the upstream lift (stem-only
  node IRIs, raw-path parent IRIs). If upstream changes them, the workaround
  in `lift_all` should be revisited.

**Trigger to revisit:** if metawork-ontology gains a second Python consumer,
publish it as a package and switch the plugin to a pinned install (option 2).
