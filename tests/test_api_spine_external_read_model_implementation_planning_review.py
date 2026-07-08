import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    ROOT / "docs" / "api-spine" / "external-read-model-implementation-planning-review.md"
)
COMBINED_REVIEW_PATH = (
    ROOT / "docs" / "api-spine" / "external-read-model-combined-readiness-review.md"
)
DAG_PATH = ROOT / "docs" / "api-spine" / "external-read-model-readiness-dag.json"
SNAPSHOT_PATH = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)

EXPECTED_INPUTS = {
    "combined_readiness_review": "docs/api-spine/external-read-model-combined-readiness-review.md",
    "blocked_readiness_snapshot": "tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json",
    "readiness_status_checker": "scripts/external_read_model_readiness_status.py",
    "readiness_dag": "docs/api-spine/external-read-model-readiness-dag.json",
}

EXPECTED_PLANNING_AREAS = {
    "route_ownership": "not_reviewed",
    "graphql_resolver_ownership": "not_reviewed",
    "authorization_and_scope": "not_reviewed",
    "pagination_and_ordering": "not_reviewed",
    "empty_error_unavailable_states": "not_reviewed",
    "source_manifest_policy": "blocked",
    "test_gate_plan": "not_reviewed",
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding REST routes",
    "adding GraphQL resolvers or GraphQL mutations",
    "adding Pydantic runtime schemas",
    "changing the blocked readiness snapshot",
    "changing readiness flags to `true`",
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "runtime FGA clients",
    "external patient clients",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "Access AI invocation wiring",
    "source manifests as approved runtime configuration",
    "RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping",
    "reminder, message, SMS, practitioner, directory, appointment, billing, result",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def _review_text() -> str:
    return REVIEW_PATH.read_text(encoding="utf-8")


def _input_rows() -> dict[str, dict[str, str]]:
    section = _review_text().split("## Current Readiness Inputs", 1)[1].split(
        "\n## ", 1
    )[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "artifact": cells[1].strip("`"),
            "state": cells[2],
        }
    return rows


def _planning_rows() -> dict[str, dict[str, str]]:
    section = _review_text().split("## Planning Verdict", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "state": cells[1].strip("`"),
            "required": cells[2],
        }
    return rows


def test_planning_review_references_current_blocked_inputs():
    rows = _input_rows()
    combined_review = COMBINED_REVIEW_PATH.read_text(encoding="utf-8")
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    dag = json.loads(DAG_PATH.read_text(encoding="utf-8"))

    assert {key: row["artifact"] for key, row in rows.items()} == EXPECTED_INPUTS
    for artifact in EXPECTED_INPUTS.values():
        assert (ROOT / artifact).exists()
    assert "Overall decision: `blocked`" in combined_review
    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["runtime_authority_node_count"] == 0
    assert dag["decision"] == "blocked"
    assert all(value is False for value in dag["readiness"].values())


def test_planning_review_verdict_keeps_runtime_proposal_blocked():
    review = _review_text()
    rows = _planning_rows()

    assert {key: row["state"] for key, row in rows.items()} == EXPECTED_PLANNING_AREAS
    assert "Overall decision: `blocked`" in review
    assert "Runtime implementation proposal ready: `false`" in review
    assert "Sprint engine state: `continuing`" in review
    assert "Pause required before runtime implementation: `true`" in review


def test_route_and_graphql_planning_requirements_are_preimplementation_only():
    review = _review_text()
    route_section = review.split("## Route Planning Requirements", 1)[1].split(
        "\n## ", 1
    )[0]
    graphql_section = review.split("## GraphQL Planning Requirements", 1)[1].split(
        "\n## ", 1
    )[0]
    compact = " ".join((route_section + graphql_section).split())

    for phrase in [
        "owning router and response schema owner",
        "authenticated user context",
        "practice/patient/source scoping",
        "display-safe fields only",
        "implementation must remain blocked",
        "resolver ownership",
        "resolver authorization",
        "batching or dataloader policy",
        "GraphQL mutation support must remain absent",
    ]:
        assert phrase in compact


def test_candidate_planning_sequence_remains_static_and_unapproved():
    section = _review_text().split("## Candidate Planning Sequence", 1)[1].split(
        "\n## ", 1
    )[0]
    compact = " ".join(section.split())

    for phrase in [
        "static route/schema ownership proposals",
        "source-manifest planning for RACGP/Cochrane before assigning any directory route or schema ownership",
        "GraphQL resolver ownership and resolver authorization mapping",
        "implementation proposal tests and security review requirements before any runtime route",
        "default_limit=20",
        "max_limit=100",
        "not approved by this review",
    ]:
        assert phrase in compact


def test_test_gate_plan_blocks_code_until_tests_are_defined():
    section = _review_text().split("## Test Gate Requirements", 1)[1].split(
        "\n## ", 1
    )[0]

    for phrase in [
        "auth and role denial",
        "practice and patient scoping",
        "active-only practitioner defaults",
        "reminder date/status mapping",
        "patient-message two-table union and raw-body exclusion",
        "RACGP/Cochrane source manifest absent/blocked/unavailable states",
        "pagination, deterministic ordering, and maximum result limits",
        "GraphQL resolver parity with REST/read-service behavior",
        "no provider calls, no Access AI invocation, no RAG/GraphRAG",
        "readiness status and blocked snapshot changes",
    ]:
        assert phrase in section


def test_planning_review_preserves_closed_gates_and_boundary():
    review = _review_text()
    compact = " ".join(review.split())

    for phrase in REQUIRED_CLOSED_GATE_PHRASES:
        assert phrase in review
    assert "does not authorize" in review
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "licence compliance" in compact
    assert "patient-facing client readiness" in review
