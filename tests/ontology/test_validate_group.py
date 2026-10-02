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


# ── decisions and the scope-axis-mismatch shape (issue #40) ────────────────

AREA_GROUP = FIX / "conforming" / "Wellness" / "Sleep" / "Overview.md"  # 20000ft-areas-focus-responsibility


def test_decision_at_the_groups_altitude_has_no_mismatch():
    code, out = run_json("--at", "20000ft-areas-focus-responsibility", AREA_GROUP)
    assert code == 0, out
    assert out["status"] == "pass"
    assert out["violations"] == [] and out["warnings"] == []
    assert out["decision"]["altitude"] == out["decision"]["group_altitude"]
    proc = run("--at", "20000ft-areas-focus-responsibility", AREA_GROUP)
    assert "No scope-axis mismatch" in proc.stdout


def test_decision_at_another_altitude_is_a_warning_not_a_failure():
    code, out = run_json("--at", "10000ft-projects", "--statement", "Which project next?", AREA_GROUP)
    assert code == 0, out
    assert out["status"] == "warnings"
    assert out["violations"] == []
    [w] = out["warnings"]
    assert w["severity"] == "Warning"
    assert w["field"] == "decision_altitude" and w["value"] == "10000ft-projects"
    assert w["file"] == str(AREA_GROUP)
    assert w["message"].startswith("Scope-axis mismatch")
    assert "10000ft-projects" in w["message"] and "20000ft-areas-focus-responsibility" in w["message"]
    assert out["decision"] == {"group_file": str(AREA_GROUP), "altitude": "10000ft-projects",
                               "statement": "Which project next?",
                               "group_altitude": "20000ft-areas-focus-responsibility"}


def test_mismatch_text_output_is_a_warning_block_not_fail_or_pass():
    proc = run("--at", "50000ft-purpose-principles", AREA_GROUP)
    assert proc.returncode == 0
    assert "WARN: 1 SHACL warning(s)" in proc.stdout
    assert "Scope-axis mismatch" in proc.stdout
    assert "FAIL" not in proc.stdout and "PASS" not in proc.stdout


def test_violations_still_fail_when_a_decision_is_given():
    group = FIX / "violating" / "unknown-enum" / "Sleep.md"  # 20000ft, bad system_strata
    code, out = run_json("--at", "10000ft-projects", group)
    assert code == 1, out
    assert out["status"] == "fail"
    assert [v["field"] for v in out["violations"]] == ["system_strata"]
    assert [w["field"] for w in out["warnings"]] == ["decision_altitude"]


@pytest.mark.parametrize("args", [
    ("--at", "15000ft", AREA_GROUP),                                # unknown notation
    ("--at", "10000ft-projects", FIX / "conforming"),               # directory, not one group file
    ("--at", "10000ft-projects", AREA_GROUP, FIX / "conforming" / "Overview.md"),  # two groups
    ("--statement", "no altitude given", AREA_GROUP),               # --statement without --at
])
def test_bad_decision_input_is_an_input_error(args):
    code, out = run_json(*args)
    assert code == 2, out
    assert out["status"] == "error"


def test_unknown_notation_error_lists_the_valid_ones():
    proc = run("--at", "15000ft", AREA_GROUP)
    assert proc.returncode == 2
    assert "NOT validated" in proc.stdout and "10000ft-projects" in proc.stdout


def test_runs_without_at_are_unchanged_by_warning_shapes():
    # metawork-set-up never passes --at: no Decision exists, so the
    # scope-axis-mismatch shape has no focus nodes and cannot warn or fail.
    code, out = run_json(FIX / "conforming")
    assert code == 0 and out["status"] == "pass"
    assert out["warnings"] == [] and out["decision"] is None
    assert "scope-axis-mismatch.shacl.ttl" in out["shape_files"]


def test_warnings_from_any_shape_do_not_fail_a_run_without_at(tmp_path):
    # A future upstream sh:Warning shape on groups must not start failing set-up.
    onto = tmp_path / "onto"
    shutil.copytree(VENDOR, onto)
    (onto / "shapes" / "zz-warn.shacl.ttl").write_text(
        "@prefix mw: <https://ontology.integralproductivity.com/metawork#> .\n"
        "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
        "[] a sh:NodeShape ; sh:targetClass mw:MetaWorkGroup ;\n"
        "   sh:property [ sh:path mw:cynefinDomain ; sh:minCount 1 ; sh:severity sh:Warning ;\n"
        "                 sh:message \"test: cynefin_domain advised\" ] .\n"
    )
    code, out = run_json("--ontology-dir", onto, FIX / "conforming")
    assert code == 0, out
    assert out["status"] == "warnings" and out["violations"] == []
    assert {w["message"] for w in out["warnings"]} == {"test: cynefin_domain advised"}
