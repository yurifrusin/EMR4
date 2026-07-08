import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DAG_PATH = ROOT / "docs" / "api-spine" / "external-read-model-readiness-dag.json"

EXPECTED_NODES = {
    "external_gap_inventory",
    "external_gap_status_checker",
    "practitioner_directory_design",
    "patient_reminders_design",
    "patient_messages_design",
    "directory_source_review",
    "directory_read_shape_design",
    "combined_readiness_review",
    "rest_route_wiring",
    "graphql_resolver_wiring",
    "provider_memory_external_clients",
}

EXPECTED_CLOSED_GATES = {
    "runtime graph execution",
    "GraphRAG runtime wiring",
    "GraphQL resolvers or GraphQL mutations",
    "new REST routes",
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "runtime FGA clients",
    "external patient clients",
    "H15/H-series runtime imports",
    "memory/RAG runtime wiring",
    "broad historical diary trove mining",
    "Access AI invocation wiring",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def _dag() -> dict:
    return json.loads(DAG_PATH.read_text(encoding="utf-8"))


def _assert_acyclic(node_ids: set[str], edges: list[dict[str, str]]) -> None:
    outgoing = {node_id: [] for node_id in node_ids}
    incoming_count = {node_id: 0 for node_id in node_ids}
    for edge in edges:
        outgoing[edge["from"]].append(edge["to"])
        incoming_count[edge["to"]] += 1

    ready = [node_id for node_id, count in incoming_count.items() if count == 0]
    visited = []
    while ready:
        node_id = ready.pop()
        visited.append(node_id)
        for child_id in outgoing[node_id]:
            incoming_count[child_id] -= 1
            if incoming_count[child_id] == 0:
                ready.append(child_id)

    assert set(visited) == node_ids


def test_external_read_model_readiness_dag_has_expected_nodes_and_edges():
    dag = _dag()
    nodes = dag["nodes"]
    edges = dag["edges"]
    node_ids = {node["id"] for node in nodes}

    assert dag["schema_version"] == "api_spine.external_read_model_readiness_dag.v1"
    assert dag["decision"] == "blocked"
    assert node_ids == EXPECTED_NODES
    assert len(edges) == 14
    assert all(edge["from"] in node_ids and edge["to"] in node_ids for edge in edges)
    assert all(edge["from"] != edge["to"] for edge in edges)


def test_external_read_model_readiness_dag_is_acyclic():
    dag = _dag()
    node_ids = {node["id"] for node in dag["nodes"]}

    _assert_acyclic(node_ids, dag["edges"])


def test_external_read_model_readiness_dag_preserves_blocked_runtime_posture():
    dag = _dag()

    assert dag["decision"] == "blocked"
    assert dag["readiness"] == {
        "external_read_model_runtime_ready": False,
        "graphql_resolver_ready": False,
        "rest_route_ready": False,
        "provider_or_directory_runtime_ready": False,
        "runtime_or_memory_ready": False,
        "write_authority_ready": False,
        "raw_compat_mode_change_ready": False,
    }
    assert all(node["runtime_authority"] is False for node in dag["nodes"])
    assert {node["status"] for node in dag["nodes"]} >= {
        "static_complete",
        "design_complete_no_runtime",
        "blocked",
    }


def test_external_read_model_readiness_dag_artifacts_exist_or_are_blocked_future_nodes():
    dag = _dag()
    future_nodes = {
        "rest_route_wiring",
        "graphql_resolver_wiring",
        "provider_memory_external_clients",
    }

    for node in dag["nodes"]:
        artifact = node["artifact"]
        if node["id"] in future_nodes:
            assert artifact == ""
            assert node["status"].startswith("blocked")
        else:
            assert artifact
            assert (ROOT / artifact).exists()


def test_external_read_model_readiness_dag_closed_gates_are_complete():
    dag = _dag()

    assert set(dag["closed_gates"]) == EXPECTED_CLOSED_GATES
    assert "does not create runtime graph execution" in dag["purpose"]
    assert "runtime graph execution" in dag["closed_gates"]


def test_external_read_model_readiness_dag_safe_content_boundary():
    serialized = json.dumps(_dag(), sort_keys=True).casefold()

    for forbidden in [
        "local_data",
        "raw diary",
        "patient_id",
        "appointment_id",
        "provider prompt",
        "database query",
        "write_authority\": true",
        "runtime_authority\": true",
    ]:
        assert forbidden not in serialized
