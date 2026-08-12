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
        "raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal"
    )
    assert report["current_position"]["why_now"]
    assert report["current_position"]["unlocks"]
    assert report["current_position"]["does_not_solve"]
    horizon_by_id = {item["id"]: item for item in report["decision_horizon"]}
    assert "reception-one-yuri-internal-walkthrough-completion" not in horizon_by_id
    assert "reception-one-product-context-proposal-runtime" not in horizon_by_id
    assert "reception-one-bounded-model-text-lane" not in horizon_by_id
    assert horizon_by_id["reception-one-stage3b-participant-execution"]["status"] == (
        "deferred"
    )
    assert horizon_by_id["next-typed-diary-event-family"]["status"] == "candidate"
    assert "shared-application-auth-runtime-foundation" not in horizon_by_id
    assert "shared-application-auth-postgresql-persistence" not in horizon_by_id
    assert "shared-application-auth-runtime-role-secure-transport" not in horizon_by_id
    assert "shared-application-auth-operational-hardening" not in horizon_by_id
    assert "security-finding-governance" not in horizon_by_id
    assert "shared-application-auth-office-cookie-compatibility" not in horizon_by_id
    assert (
        "shared-application-auth-postgresql-office-host-compatibility"
        not in horizon_by_id
    )
    assert "reception-one-word-online-authenticated-dialog-check" not in horizon_by_id
    assert "resume-raisa-word-online-manifest-upload" not in horizon_by_id
    assert not any(
        decision["id"] == "enable-chatgpt-chrome-file-url-access"
        for decision in report["user_owned_decisions"]
    )
    assert any(
        decision["id"] == "authorize-shared-application-auth-runtime-foundation"
        for decision in report["user_owned_decisions"]
    )
    assert any(
        decision["id"] == "authorize-shared-application-auth-postgresql-persistence"
        for decision in report["user_owned_decisions"]
    )
    assert any(
        decision["id"]
        == "authorize-shared-application-auth-runtime-role-secure-transport"
        for decision in report["user_owned_decisions"]
    )
    assert any(
        decision["id"] == "authorize-shared-application-auth-operational-hardening"
        for decision in report["user_owned_decisions"]
    )
    assert any(
        decision["id"] == "authorize-security-finding-governance"
        for decision in report["user_owned_decisions"]
    )
    assert not any(
        item["id"] == "reception-one-visual-synthesis"
        for item in report["decision_horizon"]
    )
    support_ids = {item["id"] for item in report["programme_support_horizon"]}
    assert "ariadne-synaptic-event-router" in support_ids
    assert "ariadne-first-generated-draft-rehearsal" in support_ids
    assert "ariadne-vertex-sydney-bounded-work-cell-rehearsal" in support_ids
    assert "ariadne-vertex-sydney-gemini-25-bounded-work-cell-rehearsal" in support_ids
    assert "ariadne-vertex-sydney-gemini-25-adc-restored-continuation" in support_ids
    router = next(
        item
        for item in report["programme_support_horizon"]
        if item["id"] == "ariadne-synaptic-event-router"
    )
    assert router["status"] == "candidate"
    assert router["boundary_changes"] == ["event-runtime"]
    assert "existing default-off local" in router["strategic_question"]
    assert any(
        decision["id"] == "authorize-synaptic-event-router-runtime-adapter"
        for decision in report["user_owned_decisions"]
    )
    admission = next(
        item
        for item in report["programme_support_horizon"]
        if item["id"] == "ariadne-first-generated-draft-rehearsal"
    )
    assert admission["status"] == "blocked"
    assert admission["boundary_changes"] == ["model-runtime"]
    assert "provider-blocked diagnostic" in admission["strategic_question"]
    assert any(
        decision["id"] == "authorize-generated-draft-gateway-diagnostic-or-retry"
        for decision in report["user_owned_decisions"]
    )
    vertex = next(
        item
        for item in report["programme_support_horizon"]
        if item["id"] == "ariadne-vertex-sydney-bounded-work-cell-rehearsal"
    )
    assert vertex["status"] == "blocked"
    assert vertex["boundary_changes"] == [
        "container-runtime",
        "model-runtime",
        "provider-call",
    ]
    assert "documentary gate" in vertex["strategic_question"]
    vertex_25 = next(
        item
        for item in report["programme_support_horizon"]
        if item["id"] == "ariadne-vertex-sydney-gemini-25-bounded-work-cell-rehearsal"
    )
    assert vertex_25["status"] == "blocked"
    assert vertex_25["boundary_changes"] == [
        "container-runtime",
        "model-runtime",
        "provider-call",
    ]
    assert "restored" in vertex_25["strategic_question"]
    assert "could not refresh non-interactively" in vertex_25["why_it_matters"]
    vertex_25_continuation = next(
        item
        for item in report["programme_support_horizon"]
        if item["id"] == "ariadne-vertex-sydney-gemini-25-adc-restored-continuation"
    )
    assert vertex_25_continuation["status"] == "blocked"
    assert vertex_25_continuation["boundary_changes"] == [
        "container-runtime",
        "model-runtime",
        "provider-call",
    ]
    assert (
        "external cache-control action"
        in (vertex_25_continuation["strategic_question"])
    )
    assert (
        "in-memory caching was not verified disabled"
        in (vertex_25_continuation["why_it_matters"])
    )
    continuation_node = find_node(
        load_graph(),
        "ariadne-vertex-sydney-gemini-25-adc-restored-continuation",
    )
    assert continuation_node["relationships"][0] == {
        "node_id": ("ariadne-vertex-sydney-gemini-25-bounded-work-cell-rehearsal"),
        "relation": "builds_on",
    }
    vertex_decision = next(
        decision
        for decision in report["user_owned_decisions"]
        if decision["id"] == "authorize-next-residency-safe-model-tranche"
    )
    assert "Historical decision satisfied" in vertex_decision["required_before"]
    assert any(
        decision["id"] == "authorize-gemini-25-sydney-reorientation"
        for decision in report["user_owned_decisions"]
    )
    assert any(
        decision["id"] == "resume-gemini-25-sydney-after-adc-reauthentication"
        for decision in report["user_owned_decisions"]
    )
    assert report["user_owned_decisions"]
    runtime_decision = next(
        decision
        for decision in report["user_owned_decisions"]
        if decision["id"] == "authorize-reception-one-product-context-proposal-runtime"
    )
    assert runtime_decision["required_before"].startswith("Satisfied on 2026-07-29")


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
    current_id = not_accepted["current_position"]["node_id"]
    find_node(graph, current_id)["status"] = "active"
    errors = compass.validate_compass(
        not_accepted, graph, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert f"current_position_not_accepted:{current_id}:active" in errors

    current_audit = continuity.audit_graph(
        load_graph(),
        repo_root=REPO_ROOT,
        node_id="reception-one-bureau-model-text-lane",
    )
    assert current_audit["status"] == "passed"
    assert current_audit["nodes"][0]["required_contracts"] == [
        {
            "contract_id": "combined-patient-practitioner-time-duration-intent",
            "status": "satisfied",
            "reasons": [],
        },
        {
            "contract_id": "committed-reschedule-availability-reconciliation",
            "status": "satisfied",
            "reasons": [],
        },
    ]


def test_stale_revision_fabricated_lineage_and_unknown_boundary_fail_closed() -> None:
    graph = load_graph()

    stale = load_compass()
    stale["source_graph_revision"] -= 1
    expected = (
        "compass_graph_revision_mismatch:"
        f"{stale['source_graph_revision']}:{graph['graph_revision']}"
    )
    assert expected in compass.validate_compass(
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
    target = next(
        item
        for item in unknown_boundary["decision_horizon"]
        if item["id"] == "next-typed-diary-event-family"
    )
    target["boundary_changes"] = ["invented-authority"]
    assert (
        "horizon_boundary_unknown:next-typed-diary-event-family:invented-authority"
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


def test_cli_emits_valid_json_and_plain_language(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert compass.main(["--repo-root", str(REPO_ROOT), "validate"]) == 0
    validation = json.loads(capsys.readouterr().out)
    assert validation["status"] == "passed"
    assert validation["journey_count"] == len(load_compass()["journey"])

    assert (
        compass.main(["--repo-root", str(REPO_ROOT), "show", "--format", "markdown"])
        == 0
    )
    rendered = capsys.readouterr().out
    assert rendered.startswith("# Ariadne Compass — EMR4")
    assert "where" not in rendered[:80].casefold()
    assert "compact reference-aligned" in rendered


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
