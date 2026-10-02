"""Acceptance tests for lib/ontology/validate-group.sh (issue #39, ADR-0008).

Run: python3 -m pytest -q tests/ontology
Needs rdflib, pyshacl, pyyaml (lib/ontology/vendor/requirements.txt).
Set METAWORK_ONTOLOGY_DIR to test against a metawork-ontology checkout
instead of the vendored snapshot.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
WRAPPER = REPO / "lib" / "ontology" / "validate-group.sh"
SCRIPT = REPO / "lib" / "ontology" / "validate_group.py"
VENDOR = REPO / "lib" / "ontology" / "vendor"
FIX = REPO / "tests" / "fixtures" / "ontology"


def run(*args, env=None):
    e = {**os.environ, "METAWORK_PYTHON": sys.executable, **(env or {})}
    return subprocess.run([str(WRAPPER), *map(str, args)], capture_output=True, text=True, env=e)


def run_json(*args, env=None):
    proc = run("--format", "json", *args, env=env)
    return proc.returncode, json.loads(proc.stdout)


def test_conforming_tree_passes():
    code, out = run_json(FIX / "conforming")
    assert code == 0, out
    assert out["status"] == "pass"
    assert out["violations"] == []
    assert len(out["files"]) == 3


def test_parent_chain_is_followed_and_same_stem_files_do_not_collide():
    # Wellness/Sleep/Overview.md has parent ../../Overview.md: same stem, different
    # file. A stem-only IRI would make it its own parent; it must still conform.
    code, out = run_json(FIX / "conforming" / "Wellness" / "Sleep" / "Evening wind-down.md")
    assert code == 0, out
    names = sorted(Path(f).relative_to(FIX / "conforming").as_posix() for f in out["files"])
    assert names == ["Overview.md", "Wellness/Sleep/Evening wind-down.md", "Wellness/Sleep/Overview.md"]


@pytest.mark.parametrize("case, field, value_fragment", [
    ("unknown-enum", "system_strata", "someday"),
    ("missing-axis", "vertical_development_stage", None),
    ("missing-parent", "parent", "nowhere/Overview.md"),
])
def test_violating_group_fails_and_names_the_field(case, field, value_fragment):
    code, out = run_json(FIX / "violating" / case)
    assert code == 1, out
    assert out["status"] == "fail"
    assert [v["field"] for v in out["violations"]] == [field]
    if value_fragment:
        assert value_fragment in out["violations"][0]["value"]


def test_text_output_shows_violation_and_never_says_pass():
    proc = run(FIX / "violating" / "unknown-enum")
    assert proc.returncode == 1
    assert "FAIL: 1 SHACL violation(s)" in proc.stdout
    assert "system_strata" in proc.stdout and "someday" in proc.stdout
    assert "PASS" not in proc.stdout


def test_whole_fixture_tree_fails_when_any_group_violates():
    code, out = run_json(FIX / "conforming", FIX / "violating")
    assert code == 1
    assert len(out["violations"]) == 3


def test_file_without_frontmatter_is_an_input_error():
    code, out = run_json(FIX / "not-a-group.md")
    assert code == 2 and out["status"] == "error"


def test_missing_ontology_is_unavailable_not_pass(tmp_path):
    code, out = run_json("--ontology-dir", tmp_path, FIX / "conforming")
    assert code == 3 and out["status"] == "unavailable"


def test_missing_python_deps_is_unavailable_not_pass(tmp_path):
    # An interpreter with no site-packages: -S and -I hide rdflib/pyshacl/yaml.
    proc = subprocess.run([sys.executable, "-S", "-I", str(SCRIPT), str(FIX / "conforming")],
                          capture_output=True, text=True)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert "UNAVAILABLE" in proc.stdout and "PASS" not in proc.stdout


def test_every_shapes_file_is_loaded(tmp_path):
    # A new shapes/*.ttl upstream (e.g. the #40 scope-axis-mismatch shape) must be
    # enforced without changing the helper. Add a shape that demands cynefin_domain.
    onto = tmp_path / "onto"
    shutil.copytree(VENDOR, onto)
    (onto / "shapes" / "zz-extra.shacl.ttl").write_text(
        "@prefix mw: <https://ontology.integralproductivity.com/metawork#> .\n"
        "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
        "[] a sh:NodeShape ; sh:targetClass mw:MetaWorkGroup ;\n"
        "   sh:property [ sh:path mw:cynefinDomain ; sh:minCount 1 ;\n"
        "                 sh:message \"test: cynefin_domain required\" ] .\n"
    )
    code, out = run_json("--ontology-dir", onto, FIX / "conforming")
    assert code == 1, out
    assert "zz-extra.shacl.ttl" in out["shape_files"]
    assert {v["message"] for v in out["violations"]} == {"test: cynefin_domain required"}
