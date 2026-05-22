# Configuration spec

The **single source of truth** for how Meta Work skills read user
configuration. Any skill, command, or agent that needs a backend or a
state directory must resolve those values through the precedence rules
below rather than re-deriving them.

The file lives at `~/.metawork/config.json` by default. It is JSON, not
YAML, because skills and ad-hoc shell snippets read it without a YAML
dependency.

## Location & precedence

A value is resolved in this order — highest wins:

1. **CLI flag** — `--state-dir <path>` per invocation (and equivalent
   per-field flags as they are added). Always wins.
2. **Per-state-dir override** — `<state-dir>/config.json`, when the
   `state_dir` from the global config (or a CLI override) points at a
   directory that contains one. Lets a vault or project root carry its
   own backend settings.
3. **Global default** — `~/.metawork/config.json`. Written by
   `metawork-set-up` on first use; edited directly thereafter.

If no value resolves, skills that need state prompt the user (the
bootstrap path).

## Schema (v1)

| Field | Type | Required | Description |
|---|---|---|---|
| `backend` | `"omnifocus"` \| `"markdown-dir"` | yes | Selects which `lib/backends/*.md` spec applies. |
| `state_dir` | string (path) | when `backend == "markdown-dir"` | Filesystem root for markdown-backend state. Tilde and `$VAR` expansion are the skill's responsibility, not the file's. |

Full JSON Schema (draft 2020-12):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["backend"],
  "properties": {
    "backend": {
      "type": "string",
      "enum": ["omnifocus", "markdown-dir"],
      "description": "Selects the backend spec under lib/backends/."
    },
    "state_dir": {
      "type": "string",
      "description": "Filesystem root for the markdown-dir backend. Required when backend == 'markdown-dir'; ignored when backend == 'omnifocus'."
    }
  },
  "additionalProperties": true,
  "allOf": [
    {
      "if":   { "properties": { "backend": { "const": "markdown-dir" } } },
      "then": { "required": ["state_dir"] }
    }
  ]
}
```

`additionalProperties: true` is deliberate — see [v2 extension hooks](#v2-extension-hooks-not-implemented-in-v1).

## Examples

**Markdown-backend (most common public-user case):**

```json
{
  "backend": "markdown-dir",
  "state_dir": "~/MetaWork"
}
```

**OmniFocus-backend (the reference user's case):**

```json
{
  "backend": "omnifocus"
}
```

**Per-state-dir override** — global config selects `markdown-dir` with
`~/MetaWork` as the default vault, but a separate work vault overrides
both the backend choice (still `markdown-dir`) and, say, future per-
backend tuning. The override file lives at the state-dir root:

```
~/.metawork/config.json
~/MetaWork/config.json                 # the global vault, no override needed
~/work-vault/config.json               # a second vault with its own settings
```

`~/work-vault/config.json`:

```json
{
  "backend": "markdown-dir",
  "state_dir": "~/work-vault"
}
```

A skill invoked with `--state-dir ~/work-vault` finds this file via the
precedence rule and uses its values instead of the global's.

## Bootstrap behavior

`metawork-set-up` is the canonical bootstrap path:

1. On first invocation, if `~/.metawork/config.json` does not exist,
   prompt for `backend` (and `state_dir` if `markdown-dir`).
2. Write the file using the same atomic-write pattern as the markdown
   backend (temp file in the same directory, then `rename`; see
   `lib/backends/markdown-dir.md` §Atomic writes).
3. Confirm to the user where the config landed and offer to open it.

The file has no secrets and no special permission requirements; standard
user-readable permissions are fine.

## Validation

- **Required-field enforcement** happens at read time. A missing
  `backend` is a hard error. A missing `state_dir` with
  `backend == "markdown-dir"` triggers the bootstrap prompt — not a hard
  error, because first-run is a legitimate state.
- **Type errors** (e.g., `state_dir` as a number, `backend` outside the
  enum) are hard errors with a pointer to this spec.
- **`backend == "omnifocus"` AND `state_dir` set** is a warning, not an
  error — `state_dir` is irrelevant to the OmniFocus backend and is
  ignored, but quietly dropping a user-supplied value would surprise
  someone who switched backends without removing the field.
- **Unknown top-level keys are preserved**, not stripped or rejected.
  See the next section for why.

## v2 extension hooks (not implemented in v1)

The schema sets `additionalProperties: true` so v1 parsers don't reject
fields the methodology will grow into. The known hooks:

- **`naming.area_prefix`** — configurable override for the `Overview (X)`
  convention recorded in ADR-0005. The "Trigger to revisit" in ADR-0005
  is reactive: *"if a meaningful number of v1 adopters arrive with
  incompatible naming conventions, consider making the convention
  configurable via the `~/.metawork/config.json` file (e.g., a
  `naming.area_prefix` key)."* v1 does **not** specify this key's shape
  — first adopter to ask gets the design conversation, the ADR, and the
  schema bump.
- **Per-backend tuning blocks** — anticipated examples:
  `omnifocus.{tag_prefix, folder_root, …}`,
  `markdown-dir.{vault_marker_file, atomic_write, …}`. Same rule as
  `naming`: preserved by v1 parsers, not enforced or interpreted, until
  a real adopter need surfaces.

The discipline is: don't speculate the shape. Real configurability
follows real demand, captured in an ADR, schema-bumped in the same PR.

## See also

- `lib/backends/markdown-dir.md` — what `state_dir` points at.
- `lib/backends/omnifocus.md` — why the OmniFocus backend doesn't need
  `state_dir`.
- `lib/schema/metawork-group.schema.yaml` — the per-group schema; this
  file is the per-user counterpart.
- `docs/adr/0005-overview-project-naming-convention.md` — the source of
  the `naming.area_prefix` extension hook.
