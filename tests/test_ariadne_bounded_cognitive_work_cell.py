from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from scripts import ariadne_bounded_cognitive_work_cell as work_cell
from scripts import ariadne_sandbox_dag as sandbox_dag
from scripts import ariadne_synaptic_event_router as event_router


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-bounded-cognitive-work-cell-example.json"
)
SCHEMA_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-bounded-cognitive-work-cell.schema.json"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-bounded-cognitive-work-cell-dry-run-manifests.json"
)
EVIDENCE_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-bounded-cognitive-work-cell-evidence.json"
)
GRAPH_PATH = REPO_ROOT / "orchestration/continuity/emr4-continuity-graph.json"
NODE_PATH = (
    REPO_ROOT
    / "orchestration/agent_inbox/codex/"
    "ariadne-bounded-cognitive-work-cell-protocol-node.json"
)
SANDBOX_PATH = REPO_ROOT / "orchestration/continuity/ariadne-sandbox-dag-example.json"
ROUTER_PATH = (
    REPO_ROOT / "orchestration/continuity/ariadne-synaptic-event-router-example.json"
)
SCRIPT_PATH = REPO_ROOT / "scripts/ariadne_bounded_cognitive_work_cell.py"


def load_document() -> dict:
    return json.loads(DOCUMENT_PATH.read_text(encoding="utf-8"))


def find_item(document: dict, collection: str, item_id: str) -> dict:
    return next(item for item in document[collection] if item["id"] == item_id)


def errors(document: dict) -> list[str]:
    return work_cell.validate_document(document, repo_root=REPO_ROOT)


def verification_by_case(document: dict | None = None) -> dict[str, dict]:
    result = work_cell.build_verification(
        document or load_document(), repo_root=REPO_ROOT
    )
    return {item["case_id"]: item for item in result["case_results"]}


def test_canonical_document_passes_schema_and_semantic_validation() -> None:
    document = load_document()

    assert errors(document) == []

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(document, schema)


def test_descendant_preserves_sandbox_and_router_predecessors() -> None:
    sandbox = json.loads(SANDBOX_PATH.read_text(encoding="utf-8"))
    router = json.loads(ROUTER_PATH.read_text(encoding="utf-8"))
    document = load_document()

    assert len(sandbox["nodes"]) == 13
    assert len(sandbox["exchanges"]) == 13
    assert sandbox_dag.validate_document(sandbox, repo_root=REPO_ROOT) == []
    assert event_router.validate_document(router, repo_root=REPO_ROOT) == []
    assert document["operational_graph_revision"] > router[
        "operational_graph_revision"
    ]


def test_topology_execution_container_and_agent_posture_are_orthogonal() -> None:
    document = load_document()
    nodes = {item["id"]: item for item in document["nodes"]}
    work_node = nodes["booking-work-cell-v1"]

    assert work_node["topological_role"] == "interior"
    assert work_node["agent_eligible"] is True
    assert work_node["agent_attached"] is False
    assert work_node["container_policy"]["dry_run"] is True
    assert work_node["container_policy"]["container_started"] is False
    assert work_node["container_policy"]["generation"] == 1
    assert work_node["container_policy"]["policy_revision"] == 1
    assert work_node["container_policy"]["isolation_requirement"] == (
        "dedicated-sandbox-if-separately-authorised"
    )
    leaves = [node for node in nodes.values() if node["topological_role"] == "leaf"]
    assert len(leaves) == 3
    assert all(node["container_policy"] is None for node in leaves)
    assert all(
        node["container_policy"] is None
        for node in nodes.values()
        if not node["agent_eligible"]
    )


def test_container_and_future_agentisation_mutations_fail_closed() -> None:
    deterministic_container = load_document()
    find_item(deterministic_container, "nodes", "proofreader-v1")[
        "container_policy"
    ] = {"dry_run": True, "container_started": False}
    assert "deterministic_node_precontainerised:proofreader-v1" in errors(
        deterministic_container
    )

    attached = load_document()
    find_item(attached, "nodes", "booking-work-cell-v1")["agent_attached"] = True
    assert "node_agent_must_be_absent:booking-work-cell-v1" in errors(attached)

    started = load_document()
    find_item(started, "nodes", "booking-work-cell-v1")["container_policy"][
        "container_started"
    ] = True
    assert "container_started_forbidden:booking-work-cell-v1" in errors(started)

    unchanged_generation = load_document()
    unchanged_generation["node_granularity_policy"][
        "future_agentisation_requires_new_generation"
    ] = False
    assert (
        "node_granularity_invariant_missing:"
        "future_agentisation_requires_new_generation"
    ) in errors(unchanged_generation)


def test_one_work_cell_emits_five_typed_outputs_under_one_authority_boundary() -> None:
    document = load_document()
    primary = find_item(document, "work_cell_attempts", "work-cell-attempt1")
    drafts = {item["id"]: item for item in document["draft_frames"]}
    ports = {item["id"]: item for item in document["output_ports"]}
    emitted = [drafts[item] for item in primary["emitted_draft_ids"]]

    assert len(emitted) == 5
    assert len({item["output_port_id"] for item in emitted}) == 5
    assert len({item["frame_type"] for item in emitted}) == 5
    assert {item["practice_id"] for item in emitted} == {"practice-synth-a"}
    assert {item["principal_id"] for item in emitted} == {"principal-reception"}
    assert {ports[item["output_port_id"]]["recipient_node_id"] for item in emitted} == {
        "audit-sink-v1",
        "human-gate-v1",
        "orchestrator-v1",
        "ux-projection-v1",
    }


def test_proofreader_is_deterministic_and_proves_every_frozen_verdict() -> None:
    document = load_document()
    first = work_cell.build_verification(document, repo_root=REPO_ROOT)
    second = work_cell.build_verification(document, repo_root=REPO_ROOT)

    assert first == second
    assert first["execution_enabled"] is False
    assert len(first["case_results"]) == 10
    assert len(document["draft_frames"]) == 15
    assert len(first["released_edges"]) == 8
    assert len(first["repair_receipts"]) == 2
    assert {
        frame["verdict"]
        for case in first["case_results"]
        for frame in case["frame_results"]
    } == work_cell.REQUIRED_VERDICTS


def test_released_factual_references_are_grounded_in_supplied_context() -> None:
    document = load_document()
    verification = work_cell.build_verification(document, repo_root=REPO_ROOT)
    drafts = {item["id"]: item for item in document["draft_frames"]}
    context = work_cell._context_sets(  # noqa: SLF001 - protocol contract
        {item["id"]: item for item in document["input_frames"]}
    )

    for edge in verification["released_edges"]:
        payload = drafts[edge["source_draft_id"]]["payload"]
        assert set(payload.get("candidate_slot_ids", [])) <= context["slot_ids"]
        assert payload.get("selected_slot_id") in context["slot_ids"] | {None}
        assert payload.get("patient_candidate_id") in context["patient_ids"] | {None}
        assert payload.get("practitioner_id") in context["practitioner_ids"] | {None}
        assert payload.get("duration_minutes") in context["durations"] | {None}
        assert set(payload.get("grounding_ids", [])) <= context["all_grounding_ids"]


def test_canonical_repairs_are_lossless_hashed_and_leave_originals_immutable() -> None:
    document = load_document()
    before = copy.deepcopy(document)
    result = work_cell.build_verification(document, repo_root=REPO_ROOT)
    receipts = {item["source_draft_id"]: item for item in result["repair_receipts"]}
    drafts = {item["id"]: item for item in document["draft_frames"]}

    assert document == before
    assert set(receipts) == {"draft-human-repair", "draft-ux-repair"}
    for draft_id, receipt in receipts.items():
        repaired = copy.deepcopy(drafts[draft_id])
        repaired["payload"]["candidate_slot_ids"] = sorted(
            set(repaired["payload"]["candidate_slot_ids"])
        )
        assert receipt["original_sha256"] == work_cell.canonical_sha256(
            drafts[draft_id]
        )
        assert receipt["repaired_sha256"] == work_cell.canonical_sha256(repaired)
        assert receipt["original_sha256"] != receipt["repaired_sha256"]
        assert receipt["original_immutable"] is True
        assert set(receipt["repair_rules"]) == set(work_cell.REPAIR_ALLOWLIST)


def test_proofreader_never_repairs_an_unknown_reference_or_authority_claim() -> None:
    cases = verification_by_case()
    grounding = cases["case-grounding-retry"]["frame_results"][0]
    authority = cases["case-authority-abort"]["frame_results"][0]

    assert grounding["verdict"] == "retryable_grounding_reject"
    assert grounding["repair_receipt"] is None
    assert grounding["released_edge"] is None
    assert "slot-not-grounded:slot-unknown" in grounding["reason_codes"]
    assert authority["verdict"] == "authority_reject"
    assert authority["disposition"] == "abort-edge"
    assert authority["repair_receipt"] is None
    assert authority["released_edge"] is None


def test_retry_is_immutable_bounded_and_repeated_failure_aborts_edge() -> None:
    document = load_document()
    cases = verification_by_case(document)
    schema_retry = cases["case-schema-retry"]["frame_results"][0]
    corrected = cases["case-schema-retry-success"]["frame_results"][0]
    repeated = cases["case-grounding-budget-abort"]["frame_results"][0]
    trace = find_item(document, "retry_traces", "retry-schema-correction")
    attempts = {item["id"]: item for item in document["work_cell_attempts"]}

    assert schema_retry["verdict"] == "retryable_schema_reject"
    assert schema_retry["disposition"] == "request-new-attempt"
    assert corrected["verdict"] == "pass_to_human_gate"
    assert repeated["verdict"] == "retryable_grounding_reject"
    assert repeated["disposition"] == "abort-edge"
    assert trace["feedback_frame"]["includes_draft_content"] is False
    assert attempts[trace["to_attempt_id"]]["retry_of"] == trace["from_attempt_id"]
    assert attempts[trace["to_attempt_id"]]["attempt"] > attempts[
        trace["from_attempt_id"]
    ]["attempt"]


def test_stale_context_requires_inert_fresh_read_supersession() -> None:
    document = load_document()
    cases = verification_by_case(document)
    stale = cases["case-stale-context"]["frame_results"][0]
    trace = find_item(document, "retry_traces", "supersession-stale-context")
    attempts = {item["id"]: item for item in document["work_cell_attempts"]}
    source = attempts[trace["from_attempt_id"]]
    target = attempts[trace["to_attempt_id"]]
    grant = find_item(document, "fresh_read_grants", trace["fresh_read_grant_id"])

    assert stale["verdict"] == "stale_context_reject"
    assert stale["disposition"] == "fresh-read-and-supersede"
    assert grant["execution_enabled"] is False
    assert grant["returns_data"] is False
    assert target["container_generation"] == source["container_generation"] + 1
    assert target["policy_revision"] > source["policy_revision"]
    assert target["superseded_from"] == source["id"]
    assert target["state"] == "awaiting-fresh-context"
    assert trace["stale_completion_disposition"] == "rejected-stale-generation"

    stale_allowed = load_document()
    find_item(stale_allowed, "retry_traces", "supersession-stale-context")[
        "stale_completion_disposition"
    ] = "accepted"
    assert "stale_completion_not_rejected:supersession-stale-context" in errors(
        stale_allowed
    )


def test_atomic_group_mismatch_or_member_failure_releases_no_group_edge() -> None:
    canonical = verification_by_case()["case-atomic-inconsistency"]
    assert canonical["status"] == "rejected"
    assert canonical["released_edges"] == []
    assert all(
        frame["verdict"] == "retryable_grounding_reject"
        for frame in canonical["frame_results"]
    )

    member_failure = load_document()
    find_item(member_failure, "draft_frames", "draft-human-atomic")["payload"][
        "selected_slot_id"
    ] = "slot-unknown"
    raw = work_cell.build_verification(
        member_failure, repo_root=REPO_ROOT, validate=False
    )
    case = next(
        item
        for item in raw["case_results"]
        if item["case_id"] == "case-atomic-inconsistency"
    )
    assert case["released_edges"] == []
    assert all(frame["released_edge"] is None for frame in case["frame_results"])
    assert any(
        "atomic-group-member-rejected:booking-review" in frame["reason_codes"]
        for frame in case["frame_results"]
    )


def test_atomic_group_and_proofreader_references_fail_closed() -> None:
    unknown_group = load_document()
    find_item(unknown_group, "output_ports", "port-ux")[
        "atomic_group_id"
    ] = "missing-group"
    assert "output_port_atomic_group_unknown:port-ux" in errors(unknown_group)

    mismatched_group = load_document()
    find_item(mismatched_group, "output_ports", "port-ux")[
        "atomic_group_id"
    ] = None
    assert (
        "atomic_group_port_declaration_mismatch:booking-review:port-ux"
        in errors(mismatched_group)
    )

    unknown_proofreader = load_document()
    unknown_proofreader["verification_policy"]["proofreader_node_id"] = "missing-node"
    assert "proofreader_node_unknown" in errors(unknown_proofreader)


def test_human_gate_is_a_verified_non_command_success_path() -> None:
    document = load_document()
    gate = document["human_gate_policy"]
    result = work_cell.build_verification(document, repo_root=REPO_ROOT)
    human_edges = [
        edge
        for edge in result["released_edges"]
        if edge["recipient_node_id"] == "human-gate-v1"
    ]

    assert gate["accepted_verdicts"] == [
        "pass_to_human_gate",
        "pass_with_repair_to_human_gate",
    ]
    assert gate["execution_enabled"] is False
    assert gate["command_authority"] is False
    assert gate["confirmation_evidence_only"] is True
    assert gate["backend_revalidation_required"] is True
    assert gate["rejected_frame_can_be_rehabilitated"] is False
    assert human_edges
    assert all(edge["command_authority"] is False for edge in human_edges)
    advisory = find_item(document, "output_ports", "port-advisory")
    assert advisory["authority_ceiling"] == "advisory"
    assert advisory["recipient_node_id"] == "human-gate-v1"


def test_compiled_manifests_are_exact_default_deny_and_inert() -> None:
    document = load_document()
    first = work_cell.compile_manifests(document, repo_root=REPO_ROOT)
    second = work_cell.compile_manifests(document, repo_root=REPO_ROOT)
    committed = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert first == second == committed
    assert first["authority"] == {
        "dry_run": True,
        "execution_enabled": False,
        "default_decision": "deny",
        "agent_attached": False,
        "container_started": False,
        "adapters_configured": False,
    }
    assert first["retry_manifest"]["stale_context_requires_supersession"] is True
    assert first["human_gate_manifest"]["command_authority"] is False
    assert first["proofreader_manifest"]["original_draft_immutable"] is True
    serialized = work_cell.canonical_json(first).casefold()
    assert all(
        forbidden not in serialized
        for forbidden in (
            "postgresql://",
            "http://",
            "https://",
            '"dsn"',
            '"endpoint"',
            '"topic"',
            '"container_command"',
        )
    )


def test_evidence_is_exact_and_claims_only_the_non_executing_proof() -> None:
    evidence = work_cell.build_evidence(load_document(), repo_root=REPO_ROOT)
    committed = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))

    assert evidence == committed
    assert evidence["result"] == (
        "ariadne_bounded_cognitive_work_cell_protocol_pass"
    )
    assert evidence["evidence_label"] == (
        "authored_synthetic_repository_local_non_executing"
    )
    assert evidence["verification_case_count"] == 10
    assert evidence["draft_frame_count"] == 15
    assert evidence["released_edge_count"] == 8
    assert evidence["repair_receipt_count"] == 2
    assert all(evidence["proofs"].values())


def test_accepted_continuity_node_is_exact_metadata_only_descendant() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    node = json.loads(NODE_PATH.read_text(encoding="utf-8"))
    canonical = next(item for item in graph["nodes"] if item["id"] == node["id"])

    assert canonical == node
    assert node["status"] == "accepted"
    assert node["kind"] == "exploration"
    assert node["authority"]["authorized_openings"] == []
    assert {item["node_id"] for item in node["relationships"]} == {
        "ariadne-sandbox-dag-fork",
        "ariadne-synaptic-event-router-protocol",
    }
    assert {item["relation"] for item in node["relationships"]} == {"builds_on"}


def test_sensitive_content_unsafe_evidence_and_unknown_fields_fail_closed() -> None:
    sensitive = load_document()
    sensitive["raw_transcript"] = "not permitted"
    sensitive_errors = errors(sensitive)
    assert "sensitive_or_actuator_field_forbidden:$.raw_transcript" in sensitive_errors
    assert "top_level_unknown:raw_transcript" in sensitive_errors

    connection = load_document()
    find_item(connection, "fresh_read_grants", "grant-booking-context-v2")[
        "endpoint"
    ] = "https://example.invalid"
    connection_errors = errors(connection)
    assert any(
        item.startswith("sensitive_or_actuator_field_forbidden:")
        for item in connection_errors
    )
    assert any(
        item.startswith("sensitive_or_connection_value_forbidden:")
        for item in connection_errors
    )

    unsafe = load_document()
    unsafe["evidence"] = ["../outside.md"]
    assert "unsafe_repo_reference:evidence:../outside.md" in errors(unsafe)


def test_tool_has_no_runtime_actuator_imports_and_only_inert_commands() -> None:
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert imports.isdisjoint(
        {
            "app",
            "asyncpg",
            "docker",
            "httpx",
            "openai",
            "psycopg",
            "requests",
            "socket",
            "sqlalchemy",
            "subprocess",
            "urllib",
        }
    )
    parser = work_cell.build_parser()
    subparsers_action = next(
        action
        for action in parser._actions  # noqa: SLF001 - parser contract inspection
        if action.dest == "command"
    )
    assert set(subparsers_action.choices) == {
        "validate",
        "verify",
        "compile-manifests",
        "trace",
    }


def test_markdown_trace_is_deterministic_plain_language_and_non_executing() -> None:
    document = load_document()
    first = work_cell.render_markdown(document, repo_root=REPO_ROOT)
    second = work_cell.render_markdown(document, repo_root=REPO_ROOT)

    assert first == second
    assert "Execution enabled: **no**" in first
    assert "case-primary-multi-output" in first
    assert "pass_with_repair_to_human_gate" in first
    assert "fresh-read-and-supersede" in first
    assert "abort-edge" in first
    assert "can confirm, write, call\na product surface" in first
