"""Small helper library for the Meta Work ontology.

Three jobs:
  1. load()            — read ontology + shapes into rdflib graphs
  2. frontmatter_to_rdf — lift a markdown-backend Meta Work Group file
                          (YAML frontmatter, per metawork-claude-plugin
                          lib/backends/markdown-dir.md) into RDF, resolving
                          enum strings to SKOS concepts via skos:notation
  3. validate()        — run SHACL and return (conforms, report_text)

Usage:
    python tools/metawork_ontology.py validate examples/valid-groups.ttl
    python tools/metawork_ontology.py lift path/to/group.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml
from pyshacl import validate as shacl_validate
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import SKOS, XSD

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology" / "metawork.ttl"
SHAPES = ROOT / "shapes" / "metawork-group.shacl.ttl"

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
    ont = Graph().parse(ONTOLOGY, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")
    return ont, shapes


def concept_for_notation(ont: Graph, scheme: URIRef, notation: str) -> URIRef | None:
    for c in ont.subjects(SKOS.inScheme, scheme):
        if (c, SKOS.notation, Literal(notation)) in ont:
            return c
    return None


def notations_in_scheme(ont: Graph, scheme: URIRef) -> set[str]:
    return {str(n) for c in ont.subjects(SKOS.inScheme, scheme) for n in ont.objects(c, SKOS.notation)}


def frontmatter_to_rdf(md_path: Path, ont: Graph, base: str = "urn:metawork:group:") -> Graph:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{md_path}: no YAML frontmatter")
    _, fm, *_ = text.split("---", 2)
    data = yaml.safe_load(fm) or {}

    g = Graph()
    node = URIRef(base + md_path.stem.replace(" ", "-").lower())
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


def validate(data: Graph, ont: Graph, shapes: Graph) -> tuple[bool, Graph, str]:
    # Data is validated *with the ontology loaded* so sh:class / inScheme
    # checks can see the concept declarations.
    conforms, report_graph, report_text = shacl_validate(
        data + ont, shacl_graph=shapes, inference="none", advanced=True, abort_on_first=False
    )
    return conforms, report_graph, report_text


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in {"validate", "lift"}:
        print(__doc__)
        return 2
    ont, shapes = load()
    target = Path(argv[2])
    if argv[1] == "lift":
        data = frontmatter_to_rdf(target, ont)
        print(data.serialize(format="turtle"))
    else:
        data = Graph().parse(target, format="turtle")
    conforms, _, text = validate(data, ont, shapes)
    print(text)
    return 0 if conforms else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
