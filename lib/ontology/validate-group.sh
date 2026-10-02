#!/usr/bin/env bash
# Entry point skills call to validate Meta Work Groups against the ontology.
#
#   lib/ontology/validate-group.sh [--ontology-dir DIR] [--format text|json] PATH [PATH ...]
#
# Picks a Python that has rdflib + pyshacl + pyyaml:
#   1. $METAWORK_PYTHON, or python3, if it can already import them;
#   2. otherwise `uv run --with ...` (ephemeral env, cached after first use);
#   3. otherwise exit 3 (tool unavailable) — never a silent pass.
# Exit codes: 0 pass, 1 SHACL violations, 2 input error, 3 tool unavailable.
# See docs/adr/0008-vendor-ontology-snapshot-for-skill-validation.md.
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$DIR/validate_group.py"
PY="${METAWORK_PYTHON:-python3}"
PROBE='import rdflib, pyshacl, yaml'

if command -v "$PY" >/dev/null 2>&1 && "$PY" -c "$PROBE" >/dev/null 2>&1; then
  exec "$PY" "$SCRIPT" "$@"
fi

if command -v uv >/dev/null 2>&1; then
  UV=(uv run --quiet --no-project --with 'rdflib>=7.0' --with 'pyshacl>=0.26' --with 'pyyaml>=6' python)
  if "${UV[@]}" -c "$PROBE" >/dev/null 2>&1; then
    exec "${UV[@]}" "$SCRIPT" "$@"
  fi
fi

echo "ONTOLOGY VALIDATION UNAVAILABLE — the group was NOT validated." >&2
echo "  reason: no Python with rdflib, pyshacl and pyyaml, and uv could not provide one." >&2
echo "  fix: python3 -m pip install 'rdflib>=7.0' 'pyshacl>=0.26' 'pyyaml>=6'  (or install uv)" >&2
exit 3
