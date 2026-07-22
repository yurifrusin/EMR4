from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from scripts import ariadne_sandbox_dag as sandbox_dag


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATH = (
    REPO_ROOT / "orchestration/continuity/ariadne-sandbox-dag-example.json"
)
SCHEMA_PATH = REPO_ROOT / "orchestration/continuity/ariadne-sandbox-dag.schema.json"
SCRIPT_PATH = REPO_ROOT / "scripts/ariadne_sandbox_dag.py"


def load_document() -> dict:
    return json.loads(DOCUMENT_PATH.read_text(encoding="utf-8"))


def find_node(document: dict, node_id: str) -> dict:
    return next(node for node in document["nodes"] if node["id"] == node_id)


def find_message(document: dict, message_id: str) -> dict:
    return next(
        message for message in document["exchanges"] if message["message_id"] == message_id
    )


def test_canonical_document_passes_schema_and_semantic_validation() -> None:
    document = load_document()

    assert sandbox_dag.validate_document(document, repo_root=REPO_ROOT) == []

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(document, schema)


def test_trace_proves_forward_context_round_trip_peer_link_join_and_human_stop() -> None:
    trace = sandbox_dag.build_trace(load_document(), repo_root=REPO_ROOT)

    assert trace["status"] == "passed"
    assert trace["authority"] == {
        "advisory_only": True,
        "execution_enabled": False,
        "terminal_gate": "human-gate-v1",
        "terminal_state": "awaiting-human-authority",
    }
    assert trace["context_round_trips"] == [
        {
            "correlation_id": "identity-context",
            "requested_by": "identity-attempt1",
            "brokered_by": "orchestrator-v3",
            "continued_as": "identity-attempt2",
            "frame_type": "patient-reference",
            "disposition": "context-grant",
        }
    ]
    assert trace["declared_peer_exchanges"] == [
        {
            "message_id": "message-08-peer-candidates",
            "sender": "availability-attempt1",
            "recipient": "ranking-attempt1",
            "frame_type": "availability-candidates",
        }
    ]
    assert trace["topological_order"].index("identity-attempt1") < trace[
        "topological_order"
    ].index("orchestrator-v2")
    assert trace["topological_order"].index("orchestrator-v2") < trace[
        "topological_order"
    ].index("context-source-v1")
    assert trace["topological_order"].index("context-source-v1") < trace[
        "topological_order"
    ].index("orchestrator-v3")
    assert trace["topological_order"].index("orchestrator-v3") < trace[
        "topological_order"
    ].index("identity-attempt2")
    assert trace["joins"] == [
        {
            "node_id": "join-v1",
            "sources": ["policy-attempt1", "ranking-attempt1"],
        }
    ]


def test_direct_peer_exchange_requires_bilateral_exact_startup_policy() -> None:
    missing_outbound = load_document()
    find_node(missing_outbound, "availability-attempt1")["communication_policy"][
        "outbound_rules"
    ] = []
    assert (
        "sandbox_outbound_policy_denied:message-08-peer-candidates:"
        "availability-attempt1:ranking-attempt1"
        in sandbox_dag.validate_document(
            missing_outbound, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    missing_inbound = load_document()
    find_node(missing_inbound, "ranking-attempt1")["communication_policy"][
        "inbound_rules"
    ] = []
    assert (
        "sandbox_inbound_policy_denied:message-08-peer-candidates:"
        "availability-attempt1:ranking-attempt1"
        in sandbox_dag.validate_document(
            missing_inbound, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )


def test_peer_link_cannot_carry_control_or_authority_messages() -> None:
    document = load_document()
    message = find_message(document, "message-08-peer-candidates")
    message["channel"] = "control"
    message["kind"] = "authority-gate"
    availability_policy = find_node(document, "availability-attempt1")[
        "communication_policy"
    ]["outbound_rules"][0]
    ranking_policy = find_node(document, "ranking-attempt1")["communication_policy"][
        "inbound_rules"
    ][0]
    availability_policy["channels"] = ["control"]
    ranking_policy["channels"] = ["control"]

    assert (
        "sandbox_peer_control_forbidden:message-08-peer-candidates:"
        "control:authority-gate"
        in sandbox_dag.validate_document(
            document, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )


def test_policy_change_requires_new_container_generation_restart_lineage() -> None:
    live_amendment = load_document()
    identity_second = find_node(live_amendment, "identity-attempt2")
    identity_second["communication_policy"]["revision"] = 2
    assert (
        "live_container_policy_amendment_forbidden:identity:identity-attempt2"
        in sandbox_dag.validate_document(
            live_amendment, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    restarted = load_document()
    identity_second = find_node(restarted, "identity-attempt2")
    identity_second["container"] = {
        "generation": 2,
        "restarted_from": "identity-attempt1",
    }
    identity_second["communication_policy"]["revision"] = 2
    identity_second["communication_policy"]["outbound_rules"].append(
        {
            "peer_instance": "evidence-sink",
            "channels": ["evidence"],
            "frame_types": ["evidence-summary"],
        }
    )

    assert sandbox_dag.validate_document(
        restarted, repo_root=REPO_ROOT, require_evidence_files=False
    ) == []

    bad_restart = copy.deepcopy(restarted)
    find_node(bad_restart, "identity-attempt2")["container"]["restarted_from"] = (
        "availability-attempt1"
    )
    assert (
        "container_restart_lineage_invalid:identity:identity-attempt2"
        in sandbox_dag.validate_document(
            bad_restart, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )


def test_cycle_and_unknown_or_unilateral_peer_fail_closed() -> None:
    cycle = load_document()
    cycle["exchanges"].append(
        {
            **copy.deepcopy(find_message(cycle, "message-08-peer-candidates")),
            "message_id": "message-13-cycle",
            "sender": "ranking-attempt1",
            "recipient": "availability-attempt1",
            "frame_type": "availability-candidates",
            "reason": "Invalid backward edge for cycle testing.",
        }
    )
    ranking = find_node(cycle, "ranking-attempt1")
    ranking["emits"].append("availability-candidates")
    ranking["communication_policy"]["outbound_rules"].append(
        {
            "peer_instance": "availability",
            "channels": ["data"],
            "frame_types": ["availability-candidates"],
        }
    )
    availability = find_node(cycle, "availability-attempt1")
    availability["accepts"].append("availability-candidates")
    availability["communication_policy"]["inbound_rules"].append(
        {
            "peer_instance": "ranking",
            "channels": ["data"],
            "frame_types": ["availability-candidates"],
        }
    )
    assert any(
        reason.startswith("graph_cycle:")
        for reason in sandbox_dag.validate_document(
            cycle, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    unknown = load_document()
    find_node(unknown, "availability-attempt1")["communication_policy"][
        "outbound_rules"
    ][0]["peer_instance"] = "ambient-peer"
    errors = sandbox_dag.validate_document(
        unknown, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert (
        "sandbox_policy_peer_unknown:availability-attempt1:outbound:ambient-peer"
        in errors
    )


def test_context_grant_requires_matching_request_later_attempt_and_freshness() -> None:
    unmatched = load_document()
    find_message(unmatched, "message-04-context-grant")["correlation_id"] = (
        "unmatched-context"
    )
    errors = sandbox_dag.validate_document(
        unmatched, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert "context_response_without_request:unmatched-context" in errors
    assert "context_request_response_count:identity-context:0" in errors

    stale = load_document()
    find_message(stale, "message-04-context-grant")["freshness"]["status"] = (
        "not-applicable"
    )
    assert (
        "context_grant_not_fresh:message-04-context-grant"
        in sandbox_dag.validate_document(
            stale, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    reused_attempt = load_document()
    find_node(reused_attempt, "identity-attempt2")["attempt"] = 1
    errors = sandbox_dag.validate_document(
        reused_attempt, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert "node_attempt_duplicate:identity:1" in errors
    assert "context_response_attempt_not_later:identity-context" in errors


def test_unknown_frame_property_capability_and_execution_state_fail_closed() -> None:
    unknown_property = load_document()
    find_message(unknown_property, "message-06-availability-input")["bindings"].append(
        {"name": "undeclared-field", "value": "synthetic"}
    )
    assert (
        "exchange_property_undeclared:message-06-availability-input:"
        "availability-query:undeclared-field"
        in sandbox_dag.validate_document(
            unknown_property, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    capability = load_document()
    capability["capability_catalog"].append(
        {
            "id": "execute-emr-command",
            "effect": "descriptive-only",
            "description": "Forbidden test capability.",
        }
    )
    assert (
        "executable_or_unknown_capability:execute-emr-command"
        in sandbox_dag.validate_document(
            capability, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    execution = load_document()
    candidate = find_message(execution, "message-11-human-gate")
    next(binding for binding in candidate["bindings"] if binding["name"] == "candidate-state")[
        "value"
    ] = "executed"
    assert (
        "execution_value_forbidden:message-11-human-gate:candidate-state:executed"
        in sandbox_dag.validate_document(
            execution, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )


def test_human_gate_is_required_and_terminal() -> None:
    no_gate = load_document()
    find_node(no_gate, "human-gate-v1")["role"] = "evidence-sink"
    errors = sandbox_dag.validate_document(
        no_gate, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert "human_authority_gate_count:0" in errors
    assert (
        "candidate_transition_requires_human_gate:message-11-human-gate:human-gate-v1"
        in errors
    )

    outgoing = load_document()
    outgoing["exchanges"].append(
        {
            **copy.deepcopy(find_message(outgoing, "message-12-evidence")),
            "message_id": "message-13-gate-output",
            "sender": "human-gate-v1",
            "reason": "Forbidden output from a terminal human gate.",
        }
    )
    find_node(outgoing, "human-gate-v1")["emits"].append("evidence-summary")
    errors = sandbox_dag.validate_document(
        outgoing, repo_root=REPO_ROOT, require_evidence_files=False
    )
    assert "human_gate_must_be_terminal:human-gate-v1" in errors


def test_sensitive_content_unsafe_evidence_and_bad_provenance_fail_closed() -> None:
    sensitive = load_document()
    sensitive["raw_transcript"] = "not permitted"
    assert (
        "sensitive_field_forbidden:$.raw_transcript"
        in sandbox_dag.validate_document(
            sensitive, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    named_person = load_document()
    find_message(named_person, "message-03-context-source")["bindings"][0]["value"] = (
        "Margaret Thompson"
    )
    assert any(
        reason.startswith("sensitive_value_forbidden:")
        for reason in sandbox_dag.validate_document(
            named_person, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    unsafe = load_document()
    unsafe["evidence"] = ["../outside.md"]
    assert (
        "unsafe_repo_reference:evidence:../outside.md"
        in sandbox_dag.validate_document(
            unsafe, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )

    provenance = load_document()
    find_message(provenance, "message-05-identity-result")["provenance"][
        "source_message_ids"
    ] = ["missing-message"]
    assert (
        "exchange_provenance_message_unknown:message-05-identity-result:missing-message"
        in sandbox_dag.validate_document(
            provenance, repo_root=REPO_ROOT, require_evidence_files=False
        )
    )


def test_tool_has_no_actuator_imports_or_write_subcommand() -> None:
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
            "httpx",
            "psycopg",
            "requests",
            "socket",
            "sqlalchemy",
            "subprocess",
            "urllib",
        }
    )
    parser = sandbox_dag.build_parser()
    subparsers_action = next(
        action
        for action in parser._actions  # noqa: SLF001 - parser contract inspection
        if action.dest == "command"
    )
    assert set(subparsers_action.choices) == {"trace", "validate"}


def test_markdown_is_plain_language_deterministic_and_non_executing() -> None:
    trace = sandbox_dag.build_trace(load_document(), repo_root=REPO_ROOT)
    first = sandbox_dag.render_markdown(trace)
    second = sandbox_dag.render_markdown(trace)

    assert first == second
    assert "control plane" not in first.casefold()
    assert "Declared peer links" in first
    assert "bilateral container policy" in first
    assert "Execution enabled: **no**" in first
    assert "awaiting-human-authority" in first
    assert "cannot confirm, write, dispatch or execute" in first
