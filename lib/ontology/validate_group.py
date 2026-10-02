#!/usr/bin/env python3
"""Validate markdown-backend Meta Work Groups against the Meta Work ontology.

Lifts each group file's YAML frontmatter to RDF with metawork-ontology's
`frontmatter_to_rdf`, then runs SHACL with its `validate`, using every
`shapes/*.ttl` in the resolved ontology. See docs/adr/0008.

Usage:
    lib/ontology/validate-group.sh [options] PATH [PATH ...]
    python3 lib/ontology/validate_group.py [options] PATH [PATH ...]

PATH is a group `.md` file or a directory (every `*.md` with YAML
frontmatter under it, recursively). Each group's `parent:` chain is
followed and lifted too, so nesting is checked against real files.

Options:
    --ontology-dir DIR   Use this metawork-ontology checkout instead of the
                         vendored snapshot. Also settable via the
                         METAWORK_ONTOLOGY_DIR environment variable.
    --format text|json   Output format (default: text).
    --raw                Also print pyshacl's full report text.

Exit codes:
    0  every group conforms
    1  one or more SHACL violations (printed)
    2  usage or input error (missing file, no frontmatter, bad YAML)
    3  ontology tool unavailable (snapshot missing, or rdflib / pyshacl /
       pyyaml not installed). This is never a pass.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDORED = HERE / "vendor"

EXIT_OK, EXIT_VIOLATIONS, EXIT_INPUT, EXIT_UNAVAILABLE = 0, 1, 2, 3
DEPS_HINT = (
    "Install the ontology tool's Python dependencies, e.g.\n"
    "    python3 -m pip install 'rdflib>=7.0' 'pyshacl>=0.26' 'pyyaml>=6'\n"
    "or run through lib/ontology/validate-group.sh, which uses `uv` when available."
)


class Unavailable(Exception):
    """The ontology tool cannot be run. Reported as exit 3, never as a pass."""


class InputError(Exception):
    """A path or file the caller supplied cannot be validated."""


# ── ontology resolution ────────────────────────────────────────────────────

def resolve_ontology_dir(cli_value: str | None) -> tuple[Path, str]:
    if cli_value:
        return Path(cli_value).expanduser().resolve(), "--ontology-dir"
    env = os.environ.get("METAWORK_ONTOLOGY_DIR")
    if env:
        return Path(env).expanduser().resolve(), "METAWORK_ONTOLOGY_DIR"
    return VENDORED, "vendored snapshot"


def load_tool(root: Path):
    tool = root / "tools" / "metawork_ontology.py"
    ontology = root / "ontology" / "metawork.ttl"
    shape_files = sorted((root / "shapes").glob("*.ttl")) if (root / "shapes").is_dir() else []
    missing = [str(p) for p in (tool, ontology) if not p.is_file()]
    if not shape_files:
        missing.append(str(root / "shapes" / "*.ttl"))
    if missing:
        raise Unavailable("ontology files not found: " + ", ".join(missing))

    try:
        import pyshacl  # noqa: F401
        import rdflib  # noqa: F401
        import yaml  # noqa: F401
    except ImportError as exc:
        raise Unavailable(f"missing Python dependency ({exc.name}).\n{DEPS_HINT}") from exc

    spec = importlib.util.spec_from_file_location("metawork_ontology", tool)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # a broken snapshot must not look like a pass
        raise Unavailable(f"could not import {tool}: {exc}") from exc
    return module, ontology, shape_files


def snapshot_label(root: Path) -> str:
    snap = root / "SNAPSHOT.md"
    if snap.is_file():
        for line in snap.read_text(encoding="utf-8").splitlines():
            if line.startswith("Source:"):
                return line.split("`")[1] if "`" in line else line
    head = root / ".git"
    if head.exists():
        import subprocess

        out = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True)
        if out.returncode == 0:
            return f"Integral-Productivity/metawork-ontology@{out.stdout.strip()} (checkout)"
    return str(root)


# ── group files ────────────────────────────────────────────────────────────

def read_frontmatter(path: Path) -> dict | None:
    import yaml

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        raise InputError(f"{path}: frontmatter is not valid YAML: {exc}") from exc
    return data if isinstance(data, dict) else {}


def collect(paths: list[str]) -> tuple[list[Path], list[str]]:
    files, notes = [], []
    for raw in paths:
        p = Path(raw).expanduser().resolve()
        if p.is_dir():
            for md in sorted(p.rglob("*.md")):
                if read_frontmatter(md) is None:
                    notes.append(f"skipped (no YAML frontmatter): {md}")
                else:
                    files.append(md)
        elif p.is_file():
            if read_frontmatter(p) is None:
                raise InputError(f"{p}: no YAML frontmatter; not a Meta Work Group file")
            files.append(p)
        else:
            raise InputError(f"{p}: no such file or directory")
    if not files:
        raise InputError("no Meta Work Group files found in: " + ", ".join(paths))
    return files, notes


def with_parents(files: list[Path], notes: list[str]) -> dict[Path, Path | None]:
    """Map every file (requested + ancestors) to its resolved parent path, if any."""
    parents: dict[Path, Path | None] = {}
    queue = list(files)
    while queue:
        f = queue.pop()
        if f in parents:
            continue
        ref = (read_frontmatter(f) or {}).get("parent")
        if not ref:
            parents[f] = None
            continue
        target = (f.parent / str(ref)).resolve()
        parents[f] = target
        if target.is_file() and read_frontmatter(target) is not None:
            queue.append(target)
        else:
            notes.append(f"parent of {f} not found as a group file: {target}")
    return parents


# ── lift + validate ────────────────────────────────────────────────────────

def lift_all(mo, ont, parents: dict[Path, Path | None]):
    """Lift each file under a per-directory base IRI and rewire parent links.

    The upstream lift names a node by file stem alone and turns `parent:` into
    an IRI built from the raw relative path, so two `Overview.md` files collide
    and a parent never matches the parent file's node. Lifting under a
    per-directory base and replacing the parent triple with the resolved
    parent's node keeps nesting checkable without changing the upstream tool.
    """
    from rdflib import RDF, Graph, URIRef

    data = Graph()
    node_of: dict[Path, URIRef] = {}
    lifted: dict[Path, Graph] = {}
    for f in parents:
        try:
            g = mo.frontmatter_to_rdf(f, ont, base=f.parent.as_uri() + "/")
        except Exception as exc:
            raise InputError(f"{f}: could not lift frontmatter: {exc}") from exc
        node_of[f] = next(g.subjects(RDF.type, mo.MW.MetaWorkGroup))
        lifted[f] = g
    for f, g in lifted.items():
        g.remove((None, mo.MW.parent, None))
        target = parents[f]
        if target is not None:
            g.add((node_of[f], mo.MW.parent, node_of.get(target, URIRef(target.as_uri()))))
        data += g
    return data, {v: k for k, v in node_of.items()}


def field_names(mo) -> dict:
    names = {prop: key for key, (prop, _) in mo.FIELDS.items()}
    names[mo.MW.parent] = "parent"
    return names


def describe_value(value) -> str | None:
    if value is None:
        return None
    s = str(value)
    if ":unknown:" in s or "/unknown:" in s:
        return s.rsplit("unknown:", 1)[1] + " (not a notation in the scheme)"
    if s.startswith("file://"):
        from urllib.parse import unquote

        return unquote(s[len("file://"):])
    if "#" in s:
        return s.rsplit("#", 1)[1]
    return s


def violations(mo, report, file_of) -> list[dict]:
    from rdflib.namespace import SH

    names = field_names(mo)
    out = []
    for r in report.objects(None, SH.result):
        focus = report.value(r, SH.focusNode)
        path = report.value(r, SH.resultPath)
        out.append({
            "file": str(file_of.get(focus, focus)),
            "field": names.get(path, describe_value(path)) if path is not None else None,
            "value": describe_value(report.value(r, SH.value)),
            "severity": describe_value(report.value(r, SH.resultSeverity)),
            "message": str(report.value(r, SH.resultMessage) or ""),
        })
    # One bad value can trip several constraints that share a message (e.g.
    # sh:class and sh:node on the same property); show it once.
    unique = {(v["file"], v["field"], v["value"], v["message"]): v for v in out}
    return sorted(unique.values(), key=lambda v: (v["file"], v["field"] or "", v["message"]))


# ── CLI ────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--ontology-dir")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--raw", action="store_true")
    args = ap.parse_args(argv)

    root, source = resolve_ontology_dir(args.ontology_dir)
    result = {"status": None, "ontology": None, "ontology_source": source,
              "shape_files": [], "files": [], "violations": [], "notes": []}
    try:
        mo, ontology, shape_files = load_tool(root)
        from rdflib import Graph

        ont = Graph().parse(ontology, format="turtle")
        shapes = Graph()
        for s in shape_files:
            shapes.parse(s, format="turtle")
        result["ontology"] = snapshot_label(root)
        result["shape_files"] = [s.name for s in shape_files]

        files, notes = collect(args.paths)
        parents = with_parents(files, notes)
        data, file_of = lift_all(mo, ont, parents)
        conforms, report, text = mo.validate(data, ont, shapes)
        result["files"] = [str(f) for f in parents]
        result["notes"] = notes
        result["violations"] = violations(mo, report, file_of)
        result["status"] = "pass" if conforms else "fail"
        code = EXIT_OK if conforms else EXIT_VIOLATIONS
    except Unavailable as exc:
        result["status"], result["error"], code = "unavailable", str(exc), EXIT_UNAVAILABLE
        text = None
    except InputError as exc:
        result["status"], result["error"], code = "error", str(exc), EXIT_INPUT
        text = None

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print_text(result, root)
        if args.raw and text:
            print("\n--- pyshacl report ---\n" + text)
    return code


def print_text(r: dict, root: Path) -> None:
    status = r["status"]
    if status == "unavailable":
        print("ONTOLOGY VALIDATION UNAVAILABLE — the group was NOT validated.")
        print(f"  ontology source: {r['ontology_source']} ({root})")
        print(f"  reason: {r['error']}")
        return
    if status == "error":
        print("ONTOLOGY VALIDATION ERROR — the group was NOT validated.")
        print(f"  {r['error']}")
        return

    print(f"Ontology: {r['ontology']} [{r['ontology_source']}]")
    print(f"Shapes:   {', '.join(r['shape_files'])}")
    print(f"Checked {len(r['files'])} group file(s):")
    for f in r["files"]:
        print(f"  {f}")
    for n in r["notes"]:
        print(f"  note: {n}")
    if status == "pass":
        print("PASS: every group conforms to the Meta Work ontology.")
        return
    print(f"FAIL: {len(r['violations'])} SHACL violation(s)")
    for v in r["violations"]:
        print(f"  - {v['file']}")
        if v["field"]:
            print(f"      field:   {v['field']}")
        if v["value"]:
            print(f"      value:   {v['value']}")
        print(f"      message: {v['message']}")


if __name__ == "__main__":
    sys.exit(main())
