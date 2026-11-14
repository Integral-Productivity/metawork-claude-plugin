"""Small helper library for the Meta Work ontology.

Jobs:
  1. load()             — read the ontology and every shapes/*.ttl into rdflib graphs
                          (ontology_tooling.load, with this repository's paths)
  2. frontmatter_to_rdf — lift a markdown-backend Meta Work Group file
                          (YAML frontmatter, per metawork-claude-plugin
                          lib/backends/markdown-dir.md) into RDF, resolving
                          enum strings to SKOS concepts via skos:notation
  3. decision_to_rdf    — record that a decision is being made inside a group
                          at a given horizons_of_focus altitude (mw:Decision),
                          the input the scope-axis-mismatch shape needs
  4. validate()         — run SHACL and return (conforms, report_graph, report_text)
                          (ontology_tooling.validate: ontology merged in, no inference)
  5. findings()         — the top-level results of a report, with severity

Usage:
    python tools/metawork_ontology.py validate examples/valid-groups.ttl
    python tools/metawork_ontology.py validate a.ttl b.ttl group.md     # inputs are merged
    python tools/metawork_ontology.py validate group.md --at 20000ft-areas-focus-responsibility \
        [--statement "Which areas do I drop this quarter?"]
    python tools/metawork_ontology.py lift path/to/group.md [--at NOTATION [--statement TEXT]]

Inputs ending in .md are lifted from frontmatter; anything else is parsed as
Turtle. --at (one .md input only) adds an mw:Decision in that group at the
given Horizons of Focus notation, so the scope-axis-mismatch shape can run.

Exit status: 0 conforms; 1 any SHACL result (Violation or Warning); 2 usage.
A scope-axis mismatch is a sh:Warning: the report line reads
"Severity: sh:Warning" followed by "Message: Scope-axis mismatch: ...".
"""
from __future__ import annotations

import sys
from pathlib import Path

import ontology_tooling
import yaml
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import SH, SKOS, XSD

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology" / "metawork.ttl"
SHAPES_DIR = ROOT / "shapes"
SHAPES = SHAPES_DIR / "metawork-group.shacl.ttl"  # kept for callers that import it

MW = Namespace("https://ontology.integralproductivity.com/metawork#")
MWV = Namespace("https://ontology.integralproductivity.com/metawork/vocab/")

# frontmatter key -> (property, concept scheme or None for literal)
FIELDS = {
    "subject": (MW.subject, None),
    "life_domain": (MW.lifeDomain, None),
    "horizons_of_focus": (MW.horizonsOfFocus, MWV.HorizonsOfFocus),
    "system_strata": (MW.systemStrata, MWV.SystemStrata),
    "vertical_development_stage": (MW.verticalDevelopmentStage, MWV.VerticalDevelopmentStage),
    "cynefin_domain": (MW.cynefinDomain, MWV.CynefinDomain),
    "neurological_level": (MW.neurologicalLevel, MWV.NeurologicalLevel),
    "perspective_checks": (MW.perspectiveCheck, MWV.PerspectiveCheck),
}


def load() -> tuple[Graph, Graph]:
    return ontology_tooling.load(ONTOLOGY, SHAPES_DIR)


def concept_for_notation(ont: Graph, scheme: URIRef, notation: str) -> URIRef | None:
    for c in ont.subjects(SKOS.inScheme, scheme):
        if (c, SKOS.notation, Literal(notation)) in ont:
            return c
    return None


def notations_in_scheme(ont: Graph, scheme: URIRef) -> set[str]:
    return {str(n) for c in ont.subjects(SKOS.inScheme, scheme) for n in ont.objects(c, SKOS.notation)}


def group_iri(md_path: Path, base: str = "urn:metawork:group:") -> URIRef:
    return URIRef(base + md_path.stem.replace(" ", "-").lower())


def frontmatter_to_rdf(md_path: Path, ont: Graph, base: str = "urn:metawork:group:") -> Graph:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{md_path}: no YAML frontmatter")
    _, fm, *_ = text.split("---", 2)
    data = yaml.safe_load(fm) or {}

    g = Graph()
    node = group_iri(md_path, base)
    g.add((node, RDF.type, MW.MetaWorkGroup))

    for key, (prop, scheme) in FIELDS.items():
        if key not in data or data[key] is None:
            continue
        values = data[key] if isinstance(data[key], list) else [data[key]]
        for v in values:
            if scheme is None:
                g.add((node, prop, Literal(str(v), datatype=XSD.string)))
            else:
                c = concept_for_notation(ont, scheme, str(v))
                # Unknown notation: emit a dangling IRI so SHACL reports it
                # (sh:class skos:Concept fails) instead of silently dropping it.
                g.add((node, prop, c or URIRef(base + "unknown:" + str(v))))

    if data.get("parent"):
        g.add((node, MW.parent, URIRef(base + str(data["parent"]).replace(".md", "").replace(" ", "-").lower())))
    return g


def decision_to_rdf(
    group: URIRef,
    altitude: str,
    ont: Graph,
    statement: str | None = None,
    decision: URIRef | None = None,
) -> Graph:
    """An mw:Decision in `group` at the Horizons of Focus notation `altitude`.

    An unknown notation becomes a dangling IRI so DecisionShape reports it,
    mirroring frontmatter_to_rdf.
    """
    g = Graph()
    node = decision or URIRef(f"{group}/decision/{altitude}")
    g.add((node, RDF.type, MW.Decision))
    g.add((node, MW.inGroup, group))
    c = concept_for_notation(ont, MWV.HorizonsOfFocus, altitude)
    g.add((node, MW.decisionAltitude, c or URIRef("urn:metawork:group:unknown:" + altitude)))
    if statement:
        g.add((node, MW.statement, Literal(statement, datatype=XSD.string)))
    return g


def validate(data: Graph, ont: Graph, shapes: Graph) -> tuple[bool, Graph, str]:
    # Data is validated *with the ontology loaded* so sh:class / inScheme
    # checks can see the concept declarations.
    return ontology_tooling.validate(data, ont, shapes)


def findings(report: Graph) -> list[tuple[URIRef, URIRef, URIRef | None, str]]:
    """Top-level results as (severity, focus node, path, message).

    Nested sh:detail results are skipped; they explain a parent result.
    """
    return [
        (report.value(r, SH.resultSeverity), report.value(r, SH.focusNode),
         report.value(r, SH.resultPath), str(report.value(r, SH.resultMessage)))
        for r in report.objects(None, SH.result)
    ]


def _parse_args(argv: list[str]):
    cmd, paths, at, statement = argv[1], [], None, None
    it = iter(argv[2:])
    for a in it:
        if a == "--at":
            at = next(it, None)
        elif a == "--statement":
            statement = next(it, None)
        else:
            paths.append(Path(a))
    return cmd, paths, at, statement


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in {"validate", "lift"}:
        print(__doc__)
        return 2
    cmd, paths, at, statement = _parse_args(argv)
    md = [p for p in paths if p.suffix == ".md"]
    if not paths or (cmd == "lift" and (len(paths) != 1 or not md)) or (at and len(md) != 1):
        print(__doc__)
        return 2
    ont, shapes = load()
    data = Graph()
    for p in paths:
        data += frontmatter_to_rdf(p, ont) if p.suffix == ".md" else Graph().parse(p, format="turtle")
    if at:
        data += decision_to_rdf(group_iri(md[0]), at, ont, statement)
    if cmd == "lift":
        print(data.serialize(format="turtle"))
    conforms, _, text = validate(data, ont, shapes)
    print(text)
    return 0 if conforms else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
