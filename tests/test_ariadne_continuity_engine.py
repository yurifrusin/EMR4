from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import ariadne_continuity as continuity


REPO_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = REPO_ROOT / "orchestration/continuity/emr4-continuity-graph.json"
SCHEMA_PATH = REPO_ROOT / "orchestration/continuity/ariadne-continuity-graph.schema.json"


def load_graph() -> dict:
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


def find_node(graph: dict, node_id: str) -> dict:
    return next(node for node in graph["nodes"] if node["id"] == node_id)


def materialize_evidence_files(graph: dict, repo_root: Path) -> None:
    references: set[str] = set()
    for contract in graph["contracts"]:
        references.update(contract["evidence"])
    for node in graph["nodes"]:
        for paths in node["evidence"].values():
            references.update(paths)
        for opening in node["authority"]["authorized_openings"]:
            references.add(opening["source"])
        for record in node["contract_evidence"]:
            references.update(record["evidence"])
            if record.get("waiver_source"):
                references.add(record["waiver_source"])
        for decision in node["decisions"]:
            references.add(decision["source"])
    for harvest in graph["harvests"]:
        references.update(harvest["evidence"])
    for reference in references:
        path = repo_root / reference
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("evidence\n", encoding="utf-8")


def test_canonical_graph_passes_structure_and_json_schema() -> None:
    graph = load_graph()

    assert continuity.validate_graph(graph, repo_root=REPO_ROOT) == []

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(graph, schema)


def test_canonical_audit_preserves_historical_acceptance_but_finds_parity_gap() -> None:
    graph = load_graph()

    functional = continuity.audit_graph(
        graph, repo_root=REPO_ROOT, node_id="functional-meta-grid-client"
    )
    live_local = continuity.audit_graph(
        graph, repo_root=REPO_ROOT, node_id="meta-grid-live-local-integration"
    )

    assert find_node(graph, "functional-meta-grid-client")["status"] == "accepted"
    assert functional["status"] == "revision_required"
    assert functional["reasons"] == [
        "contract_gap_open:functional-meta-grid-client:"
        "combined-patient-practitioner-time-duration-intent"
    ]
    assert live_local["status"] == "revision_required"
    assert live_local["reasons"] == [
        "contract_gap_open:meta-grid-live-local-integration:"
        "combined-patient-practitioner-time-duration-intent"
    ]


def test_tooling_protects_review_without_inheriting_product_contract() -> None:
    graph = load_graph()

    assert continuity.required_contracts(graph, "ariadne-continuity-engine-increment1") == []
    report = continuity.audit_graph(
        graph, repo_root=REPO_ROOT, node_id="ariadne-continuity-engine-increment1"
    )

    assert report["status"] == "passed"
    assert report["nodes"][0]["required_contracts"] == []
    assert "appointment-write" in report["nodes"][0]["inherited_closed_boundaries"]
    assert "provider-call" in report["nodes"][0]["inherited_closed_boundaries"]


def test_satisfied_inherited_contract_requires_named_test_evidence() -> None:
    graph = load_graph()
    functional = find_node(graph, "functional-meta-grid-client")
    functional["contract_evidence"][0]["status"] = "satisfied"
    functional["contract_evidence"][0]["evidence"] = [
        "tests/test_bernie_functional_meta_grid.py"
    ]

    passed = continuity.audit_graph(
        graph, repo_root=REPO_ROOT, node_id="functional-meta-grid-client"
    )
    assert passed["status"] == "passed"

    functional["contract_evidence"][0]["evidence"] = [
        "docs/ariadne-continuity-engine-increment1-plan.md"
    ]
    unlinked = continuity.audit_graph(
        graph, repo_root=REPO_ROOT, node_id="functional-meta-grid-client"
    )
    assert unlinked["reasons"] == [
        "contract_evidence_type_unlinked:functional-meta-grid-client:"
        "combined-patient-practitioner-time-duration-intent:tests"
    ]

    functional["contract_evidence"][0]["evidence"] = [
        "tests/test_bernie_functional_meta_grid.py"
    ]
    functional["evidence"]["tests"] = []
    functional["evidence"]["findings"].append("tests/test_bernie_functional_meta_grid.py")
    failed = continuity.audit_graph(
        graph, repo_root=REPO_ROOT, node_id="functional-meta-grid-client"
    )
    assert failed["status"] == "revision_required"
    assert failed["reasons"] == [
        "contract_evidence_type_missing:functional-meta-grid-client:"
        "combined-patient-practitioner-time-duration-intent:tests"
    ]


def test_validation_rejects_cycle_unsafe_reference_and_sensitive_content() -> None:
    cycle_graph = load_graph()
    find_node(cycle_graph, "stage1-combined-intent-foundation")["relationships"] = [
        {"node_id": "meta-grid-live-local-integration", "relation": "builds_on"}
    ]
    assert any(
        reason.startswith("graph_cycle:")
        for reason in continuity.validate_graph(
            cycle_graph, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    unsafe_graph = load_graph()
    find_node(unsafe_graph, "meta-grid-concept")["evidence"]["findings"] = [
        "../outside.json"
    ]
    assert any(
        reason.startswith("unsafe_repo_reference:")
        for reason in continuity.validate_graph(
            unsafe_graph, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    sensitive_graph = load_graph()
    find_node(sensitive_graph, "meta-grid-concept")["raw_transcript"] = "not permitted"
    assert any(
        reason.startswith("sensitive_field_forbidden:")
        for reason in continuity.validate_graph(
            sensitive_graph, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )


def test_validation_rejects_missing_parent_and_duplicate_identifiers() -> None:
    missing_parent_graph = load_graph()
    find_node(missing_parent_graph, "meta-grid-concept")["relationships"][0][
        "node_id"
    ] = "missing-foundation"
    assert (
        "relationship_parent_missing:meta-grid-concept:missing-foundation"
        in continuity.validate_graph(
            missing_parent_graph, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    duplicate_graph = load_graph()
    duplicate_graph["nodes"].append(copy.deepcopy(duplicate_graph["nodes"][0]))
    assert "node_id_missing_or_duplicate" in continuity.validate_graph(
        duplicate_graph, repo_root=REPO_ROOT, require_evidence_files=False
    )


def test_validation_rejects_unknown_contract_and_unproved_boundary_opening() -> None:
    unknown_contract_graph = load_graph()
    find_node(unknown_contract_graph, "meta-grid-concept")["contract_evidence"] = [
        {"contract_id": "unknown-contract", "status": "gap", "evidence": []}
    ]
    assert (
        "contract_evidence_contract_unknown:meta-grid-concept:unknown-contract"
        in continuity.validate_graph(
            unknown_contract_graph, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    opening_graph = load_graph()
    find_node(opening_graph, "reception-one-focused-review")["authority"][
        "authorized_openings"
    ] = [
        {
            "boundary": "appointment-write",
            "source": "docs/bernie-stage1-provider-free-supervised-booking-acceptance-plan.md",
        }
    ]
    assert (
        "authorized_opening_source_not_evidence:reception-one-focused-review:appointment-write"
        in continuity.validate_graph(
            opening_graph, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )


def test_fork_records_coordinates_but_does_not_satisfy_inherited_contract() -> None:
    graph = load_graph()
    at = "2026-07-20T10:00:00Z"

    continuity.fork_node(
        graph,
        parent="functional-meta-grid-client",
        node_id="combined-scope-proof",
        title="Combined-scope proof",
        kind="implementation",
        relation="forked_from",
        git_ref="codex/combined-scope-proof",
        source_head="152e917a3ab32006438dab9c0169d77256e18d63",
        thread_id=None,
        worktree_role="task",
        at=at,
    )

    node = find_node(graph, "combined-scope-proof")
    assert node["relationships"] == [
        {"node_id": "functional-meta-grid-client", "relation": "forked_from"}
    ]
    assert [item["id"] for item in continuity.required_contracts(graph, node["id"])] == [
        "combined-patient-practitioner-time-duration-intent"
    ]
    audit = continuity.audit_graph(graph, repo_root=REPO_ROOT, node_id=node["id"])
    assert audit["reasons"] == [
        "contract_evidence_missing:combined-scope-proof:"
        "combined-patient-practitioner-time-duration-intent"
    ]


def test_checkpoint_requires_explicit_update_for_existing_node() -> None:
    graph = load_graph()
    existing = copy.deepcopy(find_node(graph, "meta-grid-concept"))

    with pytest.raises(
        continuity.ContinuityError,
        match="checkpoint_node_exists:meta-grid-concept",
    ):
        continuity.checkpoint_node(graph, existing, update=False)

    existing["title"] = "Updated title"
    continuity.checkpoint_node(graph, existing, update=True)
    assert find_node(graph, "meta-grid-concept")["title"] == "Updated title"


def test_harvest_is_candidate_only_and_does_not_mutate_target() -> None:
    graph = load_graph()
    target_before = copy.deepcopy(find_node(graph, "reception-one-focused-review"))

    continuity.add_harvest(
        graph,
        harvest_id="visual-ideas-candidate",
        sources=["meta-grid-concept", "functional-meta-grid-client"],
        target="reception-one-focused-review",
        summary="Potential future presentation ideas.",
        decisions=["Do not promote during Increment 1."],
        evidence=["docs/bernie-reception-one-focused-review-context.md"],
        at="2026-07-20T10:00:00Z",
    )

    assert graph["harvests"][0]["status"] == "candidate"
    assert find_node(graph, "reception-one-focused-review") == target_before


def test_compare_is_read_only_and_deterministic() -> None:
    graph = load_graph()
    before = copy.deepcopy(graph)

    first = continuity.compare_nodes(
        graph, ["functional-meta-grid-client", "meta-grid-live-local-integration"]
    )
    second = continuity.compare_nodes(
        graph, ["functional-meta-grid-client", "meta-grid-live-local-integration"]
    )

    assert first == second
    assert graph == before
    assert first["nodes"][0]["required_contracts"] == [
        "combined-patient-practitioner-time-duration-intent"
    ]


def test_close_accepted_requires_acceptance_path() -> None:
    graph = load_graph()

    with pytest.raises(
        continuity.ContinuityError,
        match="close_acceptance_required:ariadne-continuity-engine-increment1",
    ):
        continuity.close_node(
            graph,
            node_id="ariadne-continuity-engine-increment1",
            status="accepted",
            decision="Accept Increment 1.",
            source="docs/ariadne-continuity-engine-increment1-plan.md",
            acceptance=None,
            at="2026-07-20T10:00:00Z",
        )

    continuity.close_node(
        graph,
        node_id="ariadne-continuity-engine-increment1",
        status="accepted",
        decision="Record an externally evidenced acceptance.",
        source="docs/ariadne-continuity-engine-increment1-plan.md",
        acceptance="orchestration/agent_inbox/codex/bernie-functional-meta-grid-sol-acceptance.md",
        at="2026-07-20T10:00:00Z",
    )
    closed = find_node(graph, "ariadne-continuity-engine-increment1")
    assert closed["status"] == "accepted"
    assert closed["evidence"]["acceptances"]


def test_atomic_write_increments_revision_after_full_validation(tmp_path: Path) -> None:
    repo_root = tmp_path / "emr4"
    (repo_root / ".git").mkdir(parents=True)
    (repo_root / "AGENTS.md").write_text("test handover\n", encoding="utf-8")
    graph = load_graph()
    starting_revision = graph["graph_revision"]
    materialize_evidence_files(graph, repo_root)
    graph_path = repo_root / "orchestration/continuity/graph.json"

    continuity.write_graph(
        graph_path,
        graph,
        repo_root=repo_root,
        at="2026-07-20T10:00:00Z",
    )

    written = json.loads(graph_path.read_text(encoding="utf-8"))
    assert written["graph_revision"] == starting_revision + 1
    assert written["updated_at"] == "2026-07-20T10:00:00Z"
    assert not list(graph_path.parent.glob("*.tmp"))


def test_graph_and_input_paths_are_confined_to_repository(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    outside = tmp_path / "outside.json"

    with pytest.raises(continuity.ContinuityError, match="graph_outside_repository"):
        continuity.resolve_repo_path(outside, repo_root, label="graph")
