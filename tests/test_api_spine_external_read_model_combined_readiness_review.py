from pathlib import Path

from scripts.external_read_model_gap_status import build_gap_status


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    ROOT / "docs" / "api-spine" / "external-read-model-combined-readiness-review.md"
)
DAG_PATH = ROOT / "docs" / "api-spine" / "external-read-model-readiness-dag.json"

EXPECTED_PREREQUISITES = {
    "external_gap_inventory": "docs/api-spine/external-router-read-model-gap-inventory.md",
    "external_gap_status_checker": "scripts/external_read_model_gap_status.py",
    "practitioner_directory_design": "docs/api-spine/practitioner-directory-read-shape-design.md",
    "patient_reminders_design": "docs/api-spine/patient-reminders-read-shape-design.md",
    "patient_messages_design": "docs/api-spine/patient-messages-read-shape-design.md",
    "directory_source_review": "docs/api-spine/directory-source-licensing-review.md",
    "directory_read_shape_design": "docs/api-spine/directory-read-shape-design.md",
}

EXPECTED_FALSE_FLAGS = {
    "external_read_model_runtime_ready",
    "graphql_resolver_ready",
    "rest_route_ready",
    "provider_or_directory_runtime_ready",
    "runtime_or_memory_ready",
    "write_authority_ready",
    "raw_compat_mode_change_ready",
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding REST routes",
    "adding GraphQL resolvers or GraphQL mutations",
    "adding Pydantic runtime schemas",
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "runtime FGA clients",
    "external patient clients",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "Access AI invocation wiring",
    "RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping",
    "source manifests as approved runtime configuration",
    "reminder, message, SMS, practitioner, directory, appointment, billing, result",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def _review_text() -> str:
    return REVIEW_PATH.read_text(encoding="utf-8")


def _prerequisite_rows() -> dict[str, dict[str, str]]:
    section = _review_text().split("## Reviewed Prerequisites", 1)[1].split(
        "\n## ", 1
    )[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "artifact": cells[1].strip("`"),
            "posture": cells[2].strip("`"),
        }
    return rows


def _verdict_rows() -> dict[str, dict[str, str]]:
    section = _review_text().split("## Combined Verdict", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "value": cells[1].strip("`"),
            "reason": cells[2],
        }
    return rows


def test_combined_review_references_all_static_prerequisites():
    rows = _prerequisite_rows()

    assert {node: row["artifact"] for node, row in rows.items()} == EXPECTED_PREREQUISITES
    for artifact in EXPECTED_PREREQUISITES.values():
        assert (ROOT / artifact).exists()
    assert rows["external_gap_inventory"]["posture"] == "static_complete"
    assert rows["external_gap_status_checker"]["posture"] == "static_complete"
    assert rows["directory_source_review"]["posture"] == "static_complete"
    assert rows["directory_read_shape_design"]["posture"] == "design_complete_no_runtime"


def test_combined_review_verdict_stays_blocked_and_false():
    review = _review_text()
    rows = _verdict_rows()
    gap_status = build_gap_status()

    assert set(rows) == EXPECTED_FALSE_FLAGS
    assert all(row["value"] == "false" for row in rows.values())
    assert "Overall decision: `blocked`" in review
    assert "Sprint engine state: `continuing`" in review
    assert "Pause required: `false`" in review
    for flag in EXPECTED_FALSE_FLAGS - {"external_read_model_runtime_ready"}:
        assert gap_status[flag] is False


def test_combined_review_names_runtime_prerequisites_without_authorizing_runtime():
    section = _review_text().split("## Still-Blocked Runtime Gates", 1)[1].split(
        "\n## ", 1
    )[0]

    for phrase in [
        "REST route paths, response schemas, auth dependencies",
        "GraphQL resolver ownership, resolver authorization",
        "RACGP/Cochrane source manifests, licence decisions",
        "provider/runtime boundaries",
        "security review for patient-facing and external-client exposure",
        "migration/deployment readiness",
        "not runtime implementation",
    ]:
        assert phrase in " ".join(section.split())


def test_combined_review_updates_dag_artifact_and_keeps_downstream_gates_blocked():
    dag = DAG_PATH.read_text(encoding="utf-8")

    assert '"id": "combined_readiness_review"' in dag
    assert '"status": "static_complete"' in dag
    assert (
        '"artifact": "docs/api-spine/external-read-model-combined-readiness-review.md"'
        in dag
    )
    for node_id in [
        "rest_route_wiring",
        "graphql_resolver_wiring",
        "provider_memory_external_clients",
    ]:
        assert f'"id": "{node_id}"' in dag
    for fragment in [
        '"external_read_model_runtime_ready": false',
        '"graphql_resolver_ready": false',
        '"rest_route_ready": false',
        '"provider_or_directory_runtime_ready": false',
        '"runtime_or_memory_ready": false',
        '"write_authority_ready": false',
        '"raw_compat_mode_change_ready": false',
    ]:
        assert fragment in dag


def test_combined_review_preserves_closed_gates_and_boundary():
    review = _review_text()
    compact = " ".join(review.split())

    for phrase in REQUIRED_CLOSED_GATE_PHRASES:
        assert phrase in review
    assert "does not authorize" in review
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "licence compliance" in compact
    assert "patient-facing client readiness" in review
