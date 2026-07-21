from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from scripts import ariadne_compass as compass
from scripts import ariadne_continuity as continuity


REPO_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = REPO_ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS_PATH = REPO_ROOT / "orchestration/continuity/emr4-compass.json"
SCHEMA_PATH = REPO_ROOT / "orchestration/continuity/ariadne-compass.schema.json"


def load_graph() -> dict:
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


def load_compass() -> dict:
    return json.loads(COMPASS_PATH.read_text(encoding="utf-8"))


def find_node(graph: dict, node_id: str) -> dict:
    return next(node for node in graph["nodes"] if node["id"] == node_id)


def test_canonical_compass_passes_schema_and_semantic_validation() -> None:
    graph = load_graph()
    current = load_compass()

    assert compass.validate_compass(current, graph, repo_root=REPO_ROOT) == []

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(current, schema)


def test_report_answers_the_navigation_questions_in_plain_language() -> None:
    report = compass.build_compass_report(
        load_compass(), load_graph(), repo_root=REPO_ROOT
    )

    assert report["status"] == "passed"
    assert report["north_star"]["title"].startswith("A complete AI-native")
    assert report["programme"]["id"] == "reception-one"
    assert report["programme"]["master_plan_phase"].startswith("Phase 2B")
    assert report["current_position"]["node_id"] == (
        "reception-one-availability-reconciliation"
    )
    assert report["current_position"]["why_now"]
    assert report["current_position"]["unlocks"]
    assert report["current_position"]["does_not_solve"]
    assert {item["status"] for item in report["decision_horizon"]} == {"candidate"}
    assert report["user_owned_decisions"]


def test_journey_preserves_real_fork_instead_of_inventing_linear_history() -> None:
    report = compass.build_compass_report(
        load_compass(), load_graph(), repo_root=REPO_ROOT
    )
    steps = {step["node_id"]: step for step in report["journey"]}

    assert steps["meta-grid-live-local-integration"]["lineage_parent"] == (
        "functional-meta-grid-client"
    )
    assert steps["reception-one-combined-scope-proof"]["lineage_parent"] == (
        "functional-meta-grid-client"
    )
    assert steps["reception-one-combined-scope-proof"]["lineage_parent"] != (
        "meta-grid-live-local-integration"
    )


def test_current_position_must_be_terminal_accepted_and_continuity_clean() -> None:
    graph = load_graph()

    nonterminal = load_compass()
    nonterminal["current_position"]["node_id"] = "functional-meta-grid-client"
    errors = compass.validate_compass(
        nonterminal, graph, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert "current_position_not_journey_terminal:functional-meta-grid-client" in errors

    not_accepted = load_compass()
    find_node(graph, "reception-one-availability-reconciliation")["status"] = "active"
    errors = compass.validate_compass(
        not_accepted, graph, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert (
        "current_position_not_accepted:reception-one-availability-reconciliation:active"
        in errors
    )

    graph = load_graph()
    record = find_node(graph, "reception-one-availability-reconciliation")[
        "contract_evidence"
    ][1]
    record["status"] = "gap"
    errors = compass.validate_compass(
        load_compass(), graph, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert (
        "current_position_continuity:contract_gap_open:"
        "reception-one-availability-reconciliation:"
        "committed-reschedule-availability-reconciliation"
        in errors
    )


def test_stale_revision_fabricated_lineage_and_unknown_boundary_fail_closed() -> None:
    graph = load_graph()

    stale = load_compass()
    stale["source_graph_revision"] -= 1
    assert "compass_graph_revision_mismatch:13:14" in compass.validate_compass(
        stale, graph, repo_root=REPO_ROOT, require_evidence_files=False
    )

    fabricated = load_compass()
    fabricated["journey"][4]["lineage_parent"] = "meta-grid-live-local-integration"
    assert (
        "journey_lineage_not_in_graph:reception-one-combined-scope-proof:"
        "meta-grid-live-local-integration"
        in compass.validate_compass(
            fabricated, graph, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    unknown_boundary = load_compass()
    unknown_boundary["decision_horizon"][0]["boundary_changes"] = [
        "invented-authority"
    ]
    assert (
        "horizon_boundary_unknown:reception-one-visual-synthesis:invented-authority"
        in compass.validate_compass(
            unknown_boundary, graph, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )


def test_unsafe_missing_evidence_and_sensitive_keys_fail_closed(tmp_path: Path) -> None:
    graph = load_graph()
    current = load_compass()
    current["north_star"]["evidence"] = ["../outside.md"]
    errors = compass.validate_compass(
        current, graph, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert "unsafe_repo_reference:compass:north_star:../outside.md" in errors

    missing = load_compass()
    missing["north_star"]["evidence"] = ["docs/does-not-exist.md"]
    errors = compass.validate_compass(missing, graph, repo_root=REPO_ROOT)
    assert "evidence_not_found:compass:north_star:docs/does-not-exist.md" in errors

    sensitive = load_compass()
    sensitive["current_position"]["raw_transcript"] = "not allowed"
    errors = compass.validate_compass(
        sensitive, graph, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert "sensitive_field_forbidden:$.current_position.raw_transcript" in errors


def test_json_and_markdown_reports_are_deterministic_and_read_only() -> None:
    graph = load_graph()
    current = load_compass()
    graph_before = copy.deepcopy(graph)
    compass_before = copy.deepcopy(current)

    first = compass.build_compass_report(current, graph, repo_root=REPO_ROOT)
    second = compass.build_compass_report(current, graph, repo_root=REPO_ROOT)
    first_markdown = compass.render_markdown(first)
    second_markdown = compass.render_markdown(second)

    assert first == second
    assert first_markdown == second_markdown
    assert graph == graph_before
    assert current == compass_before
    for heading in (
        "## North star",
        "## Programme position",
        "## Journey so far",
        "## Current position",
        "### What this unlocks",
        "### What it does not solve",
        "## Continuity and authority",
        "## Product decision horizon",
        "## Decisions that remain Yuri's",
        "## Map limits",
    ):
        assert heading in first_markdown
    assert "— candidate" in first_markdown
    assert "— accepted" not in first_markdown.split("## Product decision horizon", 1)[1]
    assert first_markdown == (REPO_ROOT / "docs/ariadne-compass-current.md").read_text(
        encoding="utf-8"
    )


def test_cli_emits_valid_json_and_plain_language(capsys: pytest.CaptureFixture[str]) -> None:
    assert compass.main(["--repo-root", str(REPO_ROOT), "validate"]) == 0
    validation = json.loads(capsys.readouterr().out)
    assert validation["status"] == "passed"
    assert validation["journey_count"] == 7

    assert (
        compass.main(
            ["--repo-root", str(REPO_ROOT), "show", "--format", "markdown"]
        )
        == 0
    )
    rendered = capsys.readouterr().out
    assert rendered.startswith("# Ariadne Compass — EMR4")
    assert "where" not in rendered[:80].casefold()
    assert "working local capability foundation" in rendered


def test_runtime_has_no_network_process_or_write_actuator() -> None:
    source = (REPO_ROOT / "scripts/ariadne_compass.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not imported_roots.intersection(
        {"httpx", "requests", "socket", "subprocess", "urllib"}
    )
    forbidden_calls = {
        "write_text",
        "write_bytes",
        "unlink",
        "replace",
        "system",
        "popen",
    }
    assert not {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        if node.func.attr in forbidden_calls
    }


def test_compass_tooling_node_inherits_no_product_contract() -> None:
    graph = load_graph()
    node = find_node(graph, "ariadne-compass-increment2")

    assert node["kind"] == "tooling"
    assert {item["relation"] for item in node["relationships"]} == {
        "builds_on",
        "protects",
    }
    assert continuity.required_contracts(graph, node["id"]) == []
    audit = continuity.audit_graph(graph, repo_root=REPO_ROOT, node_id=node["id"])
    assert audit["status"] == "passed"
    assert audit["nodes"][0]["required_contracts"] == []
