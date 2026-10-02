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
    --at NOTATION        Record a decision being made in the group at this
                         horizons_of_focus notation (e.g.
                         20000ft-areas-focus-responsibility), so the
                         scope-axis-mismatch shape can run. Needs exactly one
                         group file as PATH. An unknown notation is an input
                         error (exit 2). See docs/adr/0008, "Decisions and
                         warnings".
    --statement TEXT     Optional wording of that decision (needs --at).

Results are split by SHACL severity. sh:Violation results are
`violations`; sh:Warning and sh:Info results are `warnings`. A scope-axis
mismatch is a warning: the group and the decision are each well-formed, and
zooming out on purpose for one question is legitimate.

Exit codes:
    0  no violations. status is "pass", or "warnings" when only warnings
       were found (printed under WARN:). Warnings never fail a run.
    1  one or more SHACL violations (printed); warnings are printed too
    2  usage or input error (missing file, no frontmatter, bad YAML,
       unknown --at notation, --at without exactly one group file)
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
    names[mo.MW.decisionAltitude] = "decision_altitude"
    names[mo.MW.inGroup] = "decision_group"
    names[mo.MW.statement] = "decision_statement"
    return names


def add_decision(mo, ont, data, file_of, target: Path, notation: str, statement: str | None):
    """Add an mw:Decision in the target group's own node (as lifted by lift_all).

    The scope-axis-mismatch shape joins mw:inGroup to the group's
    mw:horizonsOfFocus, so the decision must name the node this helper built
    for the file, not the upstream tool's stem-only group IRI.
    """
    from rdflib import URIRef

    known = mo.notations_in_scheme(ont, mo.MWV.HorizonsOfFocus)
    if notation not in known:
        raise InputError(f"--at {notation!r} is not a horizons_of_focus notation. "
                         f"Use one of: {', '.join(sorted(known))}")
    group = next(node for node, f in file_of.items() if f == target)
    decision = URIRef(f"{group}#decision-{notation}")
    data += mo.decision_to_rdf(group, notation, ont, statement, decision=decision)
    file_of[decision] = target
    return decision


def describe_value(value, ont=None) -> str | None:
    if value is None:
        return None
    if ont is not None:
        from rdflib.namespace import SKOS

        notation = ont.value(value, SKOS.notation)
        if notation is not None:
            return str(notation)
    s = str(value)
    if ":unknown:" in s or "/unknown:" in s:
        return s.rsplit("unknown:", 1)[1] + " (not a notation in the scheme)"
    if s.startswith("file://"):
        from urllib.parse import unquote

        return unquote(s[len("file://"):])
    if "#" in s:
        return s.rsplit("#", 1)[1]
    return s


def results(mo, report, file_of, ont) -> tuple[list[dict], list[dict]]:
    """Top-level SHACL results, split into (violations, warnings) by severity."""
    from rdflib.namespace import SH

    names = field_names(mo)
    out = []
    for r in report.objects(None, SH.result):
        focus = report.value(r, SH.focusNode)
        path = report.value(r, SH.resultPath)
        out.append({
            "file": str(file_of.get(focus, focus)),
            "field": names.get(path, describe_value(path)) if path is not None else None,
            "value": describe_value(report.value(r, SH.value), ont),
            "severity": describe_value(report.value(r, SH.resultSeverity)),
            "message": str(report.value(r, SH.resultMessage) or ""),
        })
    # One bad value can trip several constraints that share a message (e.g.
    # sh:class and sh:node on the same property); show it once.
    unique = {(v["file"], v["field"], v["value"], v["message"]): v for v in out}
    ordered = sorted(unique.values(), key=lambda v: (v["file"], v["field"] or "", v["message"]))
    # Anything not explicitly a Warning or Info counts as a violation, so an
    # unexpected severity can never turn a failure into a pass.
    soft = {"Warning", "Info"}
    return ([v for v in ordered if v["severity"] not in soft],
            [v for v in ordered if v["severity"] in soft])


# ── CLI ────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--ontology-dir")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--at", metavar="NOTATION")
    ap.add_argument("--statement")
    args = ap.parse_args(argv)

    root, source = resolve_ontology_dir(args.ontology_dir)
    result = {"status": None, "ontology": None, "ontology_source": source,
              "shape_files": [], "files": [], "decision": None,
              "violations": [], "warnings": [], "notes": []}
    try:
        mo, ontology, shape_files = load_tool(root)
        from rdflib import Graph

        ont = Graph().parse(ontology, format="turtle")
        shapes = Graph()
        for s in shape_files:
            shapes.parse(s, format="turtle")
        result["ontology"] = snapshot_label(root)
        result["shape_files"] = [s.name for s in shape_files]

        if args.statement is not None and args.at is None:
            raise InputError("--statement needs --at NOTATION")
        files, notes = collect(args.paths)
        if args.at is not None and (len(args.paths) != 1 or len(files) != 1
                                    or not Path(args.paths[0]).expanduser().is_file()):
            raise InputError("--at needs exactly one group file as PATH "
                             "(the group the decision is being made in)")
        parents = with_parents(files, notes)
        data, file_of = lift_all(mo, ont, parents)
        if args.at is not None:
            add_decision(mo, ont, data, file_of, files[0], args.at, args.statement)
            result["decision"] = {
                "group_file": str(files[0]), "altitude": args.at, "statement": args.statement,
                "group_altitude": (read_frontmatter(files[0]) or {}).get("horizons_of_focus")}
        conforms, report, text = mo.validate(data, ont, shapes)
        result["files"] = [str(f) for f in parents]
        result["notes"] = notes
        result["violations"], result["warnings"] = results(mo, report, file_of, ont)
        # A non-conforming report with no parsed results must not read as a pass.
        if result["violations"] or (not conforms and not result["warnings"]):
            result["status"], code = "fail", EXIT_VIOLATIONS
        else:
            result["status"] = "warnings" if result["warnings"] else "pass"
            code = EXIT_OK
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
    d = r["decision"]
    if d:
        print(f"Decision: at {d['altitude']} in {d['group_file']}"
              + (f" — {d['statement']!r}" if d["statement"] else ""))
    if status == "pass":
        print("PASS: every group conforms to the Meta Work ontology.")
        if d:
            print(f"No scope-axis mismatch: the group is scoped at {d['altitude']}.")
        return
    if r["violations"]:
        print(f"FAIL: {len(r['violations'])} SHACL violation(s)")
        print_results(r["violations"])
    if r["warnings"]:
        print(f"WARN: {len(r['warnings'])} SHACL warning(s)"
              + ("" if r["violations"] else " (no violations; warnings do not fail validation)"))
        print_results(r["warnings"])


def print_results(items: list[dict]) -> None:
    for v in items:
        print(f"  - {v['file']}")
        if v["field"]:
            print(f"      field:   {v['field']}")
        if v["value"]:
            print(f"      value:   {v['value']}")
        print(f"      message: {v['message']}")


if __name__ == "__main__":
    sys.exit(main())
