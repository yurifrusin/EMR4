from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import ariadne_sandbox_dag as sandbox_dag
from scripts import ariadne_synaptic_event_router as router


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-synaptic-event-router-example.json"
)
SCHEMA_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-synaptic-event-router.schema.json"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-synaptic-event-router-dry-run-manifests.json"
)
EVIDENCE_PATH = (
    REPO_ROOT
    / "orchestration/continuity/ariadne-synaptic-event-router-evidence.json"
)
PREDECESSOR_PATH = REPO_ROOT / "orchestration/continuity/ariadne-sandbox-dag-example.json"
SCRIPT_PATH = REPO_ROOT / "scripts/ariadne_synaptic_event_router.py"


def load_document() -> dict:
    return json.loads(DOCUMENT_PATH.read_text(encoding="utf-8"))


def find_item(document: dict, collection: str, item_id: str) -> dict:
    return next(item for item in document[collection] if item["id"] == item_id)


def errors(document: dict) -> list[str]:
    return router.validate_document(document, repo_root=REPO_ROOT)


def test_canonical_document_passes_schema_and_semantic_validation() -> None:
    document = load_document()

    assert errors(document) == []

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(document, schema)


def test_extension_preserves_predecessor_and_uses_its_exchange_grammar() -> None:
    predecessor = json.loads(PREDECESSOR_PATH.read_text(encoding="utf-8"))

    assert len(predecessor["nodes"]) == 13
    assert len(predecessor["exchanges"]) == 13
    assert sandbox_dag.validate_document(predecessor, repo_root=REPO_ROOT) == []

    document = load_document()
    routing = router.build_routing(document, repo_root=REPO_ROOT)
    assert document["workflow_id"] == predecessor["workflow_id"]
    assert document["operational_graph_revision"] > predecessor["graph_revision"]
    for delivery in routing["deliveries"]:
        assert delivery["sender_instance"] == "synaptic-router"
        assert delivery["recipient_node_id"] == delivery["node_id"]
        assert delivery["channel"] == "control"
        assert delivery["kind"] == "scope-change-notice"
        assert delivery["correlation_id"].startswith("steer-")
        assert delivery["provenance"]["kind"] == "authored-synthetic-committed-event"
        assert delivery["freshness"]["status"] == "requires-fresh-read"


def test_routing_is_deterministic_and_proves_match_fanout_and_suppression() -> None:
    document = load_document()
    first = router.build_routing(document, repo_root=REPO_ROOT)
    second = router.build_routing(document, repo_root=REPO_ROOT)

    assert first == second
    assert first["execution_enabled"] is False
    assert len(first["decisions"]) == 11
    assert len(first["deliveries"]) == 2
    assert first["deliveries"] == document["expected_mailbox_deliveries"]

    delivered = [item for item in first["decisions"] if item["decision"] == "deliver"]
    suppressed = [item for item in first["decisions"] if item["decision"] == "suppress"]
    assert [item["lease_id"] for item in delivered] == [
        "lease-availability-v2",
        "lease-ranking-v1",
    ]
    assert {item["reason"] for item in suppressed} == {
        "aggregate-revision-not-newer",
        "event-type-or-version-not-declared",
        "lease-expired",
        "lease-sensitivity-denied",
        "lease-superseded",
        "practice-boundary-mismatch",
        "replay-duplicate-coordinate",
        "scope-no-intersection-aggregate",
        "steering-frame-not-bilateral",
    }


def test_router_and_lease_must_bilaterally_name_peer_channel_kind_and_frame() -> None:
    sender = load_document()
    sender["route_policy"]["sender_instance"] = "ambient-router"
    sender_errors = errors(sender)
    assert "route_policy_sender_invalid" in sender_errors
    assert "lease_router_instance_not_bilateral:lease-availability-v2" in sender_errors

    channel = load_document()
    find_item(channel, "scope_leases", "lease-ranking-v1")[
        "accepted_channel"
    ] = "data"
    assert "lease_channel_not_bilateral:lease-ranking-v1" in errors(channel)

    kind = load_document()
    find_item(kind, "scope_leases", "lease-ranking-v1")["accepted_kind"] = (
        "authority-gate"
    )
    assert "lease_kind_not_bilateral:lease-ranking-v1" in errors(kind)

    frame = load_document()
    find_item(frame, "scope_leases", "lease-ranking-v1")[
        "accepted_steering_frames"
    ] = ["different-notice"]
    route = router.build_routing(frame, validate=False)
    decision = next(
        item for item in route["decisions"] if item["attempt_id"] == "route-02-ranking"
    )
    assert decision["reason"] == "steering-frame-not-bilateral"


def test_same_generation_lease_revision_can_only_narrow() -> None:
    canonical = load_document()
    assert errors(canonical) == []

    selector_expansion = load_document()
    find_item(selector_expansion, "scope_leases", "lease-availability-v2")[
        "selectors"
    ]["aggregate_ids"].append("appointment-200")
    assert (
        "lease_narrowing_selector_expansion:lease-availability-v2:"
        "lease-availability-v1:aggregate_ids"
        in errors(selector_expansion)
    )

    time_expansion = load_document()
    find_item(time_expansion, "scope_leases", "lease-availability-v2")["selectors"][
        "time_window"
    ]["ends_at"] = "2026-07-23T19:00:00+10:00"
    assert (
        "lease_narrowing_time_expansion:lease-availability-v2:lease-availability-v1"
        in errors(time_expansion)
    )

    peer_amendment = load_document()
    find_item(peer_amendment, "scope_leases", "lease-availability-v2")[
        "accepted_router_instance"
    ] = "different-router"
    assert (
        "lease_narrowing_identity_changed:lease-availability-v2:"
        "lease-availability-v1:accepted_router_instance"
        in errors(peer_amendment)
    )


def test_cross_practice_expiry_revision_sensitivity_and_stale_nodes_fail_closed() -> None:
    routing = router.build_routing(load_document(), repo_root=REPO_ROOT)
    decisions = {item["attempt_id"]: item for item in routing["decisions"]}

    assert decisions["route-04-cross-practice"]["reason"] == (
        "practice-boundary-mismatch"
    )
    assert decisions["route-06-stale-generation"]["reason"] == "lease-superseded"
    assert decisions["route-07-expired"]["reason"] == "lease-expired"
    assert decisions["route-08-revision"]["reason"] == (
        "aggregate-revision-not-newer"
    )
    assert decisions["route-09-sensitive"]["reason"] == "lease-sensitivity-denied"
    assert decisions["route-11-undeclared-event"]["reason"] == (
        "event-type-or-version-not-declared"
    )


def test_ambiguous_routes_and_invalid_time_coordinates_fail_closed() -> None:
    ambiguous = load_document()
    ambiguous["route_policy"]["rules"].append(
        {**ambiguous["route_policy"]["rules"][0], "id": "route-rescheduled-duplicate"}
    )
    assert "route_rule_ambiguous:diary.appointment_rescheduled:1" in errors(ambiguous)

    invalid_lease = load_document()
    lease_window = find_item(
        invalid_lease, "scope_leases", "lease-availability-v2"
    )["selectors"]["time_window"]
    lease_window["ends_at"] = lease_window["starts_at"]
    assert "lease_time_window_invalid:lease-availability-v2" in errors(invalid_lease)

    invalid_event = load_document()
    event_coordinates = find_item(
        invalid_event, "committed_events", "event-reschedule-001"
    )["coordinates"]
    event_coordinates["ends_at"] = event_coordinates["starts_at"]
    assert "event_time_window_invalid:event-reschedule-001" in errors(invalid_event)


def test_fresh_read_grants_are_exact_expiring_and_non_executing() -> None:
    document = load_document()
    for grant in document["fresh_read_grants"]:
        assert grant["action"] == "read-scoped-context"
        assert grant["execution_enabled"] is False
        assert grant["returns_data"] is False

    executing = load_document()
    find_item(executing, "fresh_read_grants", "grant-availability")[
        "execution_enabled"
    ] = True
    assert "grant_execution_must_be_false:grant-availability" in errors(executing)

    broad_resource = load_document()
    find_item(broad_resource, "fresh_read_grants", "grant-availability")[
        "resource_selectors"
    ].append("appointment/appointment-200")
    assert "grant_resources_not_exact:grant-availability" in errors(broad_resource)

    cross_practice = load_document()
    find_item(cross_practice, "fresh_read_grants", "grant-availability")[
        "practice_id"
    ] = "practice-synth-b"
    assert "grant_boundary_mismatch:grant-availability:practice_id" in errors(
        cross_practice
    )


def test_mailbox_deduplication_prevents_a_second_delivery() -> None:
    routing = router.build_routing(load_document(), repo_root=REPO_ROOT)
    replay = next(
        item for item in routing["decisions"] if item["attempt_id"] == "route-03-replay"
    )

    assert replay == {
        "attempt_id": "route-03-replay",
        "event_id": "event-reschedule-001",
        "lease_id": "lease-availability-v2",
        "decision": "suppress",
        "reason": "replay-duplicate-coordinate",
        "delivery_id": None,
    }
    assert sum(
        delivery["mailbox_id"] == "mailbox-availability"
        for delivery in routing["deliveries"]
    ) == 1


def test_reconciliation_and_supersession_are_forward_only_and_reject_stale_completion() -> None:
    document = load_document()
    ranking = find_item(
        document, "reconciliation_traces", "reconciliation-ranking"
    )
    supersession = ranking["supersession"]

    assert supersession["superseded_from"] == "ranking-v1"
    assert supersession["attempt"] == 2
    assert supersession["container_generation"] == 2
    assert supersession["policy_revision"] == 2
    assert ranking["stale_completion"]["disposition"] == (
        "rejected-stale-generation"
    )
    assert ranking["command_authority"] is False

    reused_generation = load_document()
    find_item(
        reused_generation, "reconciliation_traces", "reconciliation-ranking"
    )["supersession"]["container_generation"] = 1
    assert "trace_supersession_generation_invalid:reconciliation-ranking" in errors(
        reused_generation
    )

    stale_allowed = load_document()
    find_item(stale_allowed, "reconciliation_traces", "reconciliation-ranking")[
        "stale_completion"
    ]["disposition"] = "accepted"
    assert "trace_stale_completion_not_rejected:reconciliation-ranking" in errors(
        stale_allowed
    )


def test_compiled_manifests_are_exact_default_deny_and_inert() -> None:
    document = load_document()
    first = router.compile_manifests(document, repo_root=REPO_ROOT)
    second = router.compile_manifests(document, repo_root=REPO_ROOT)
    committed = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert first == second == committed
    assert first["authority"] == {
        "dry_run": True,
        "execution_enabled": False,
        "default_decision": "deny",
        "adapters_configured": False,
    }
    assert first["startup_manifest"]["mailbox_contract"] == {
        "sender_instance": "synaptic-router",
        "channel": "control",
        "kind": "scope-change-notice",
        "frame_type": "scope-change-notice",
        "delivery_boundary": "declared-mailbox-checkpoint",
        "deduplication_coordinate": [
            "event-id",
            "lease-id",
            "lease-revision",
            "container-generation",
            "steering-frame-type",
        ],
    }
    rejected = {
        item["lease_id"]: item["reason"]
        for item in first["startup_manifest"]["rejected_scope_leases"]
    }
    assert rejected == {
        "lease-availability-v1": "lease-superseded",
        "lease-expired-v1": "lease-expired",
        "lease-retired-v1": "lease-superseded",
        "lease-undeclared-v1": "event-frame-route-not-bilateral",
    }
    serialized = router.canonical_json(first).casefold()
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
    evidence = router.build_evidence(load_document(), repo_root=REPO_ROOT)
    committed = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))

    assert evidence == committed
    assert evidence["result"] == "ariadne_synaptic_event_router_protocol_pass"
    assert evidence["evidence_label"] == (
        "authored_synthetic_repository_local_non_executing"
    )
    assert evidence["delivery_count"] == 2
    assert evidence["suppression_count"] == 9
    assert all(evidence["proofs"].values())


def test_sensitive_content_unsafe_evidence_and_unknown_fields_fail_closed() -> None:
    sensitive = load_document()
    sensitive["raw_transcript"] = "not permitted"
    sensitive_errors = errors(sensitive)
    assert "sensitive_or_actuator_field_forbidden:$.raw_transcript" in sensitive_errors
    assert "top_level_unknown:raw_transcript" in sensitive_errors

    connection = load_document()
    find_item(connection, "fresh_read_grants", "grant-availability")["endpoint"] = (
        "https://example.invalid"
    )
    connection_errors = errors(connection)
    assert any(item.startswith("sensitive_or_actuator_field_forbidden:") for item in connection_errors)
    assert any(item.startswith("sensitive_or_connection_value_forbidden:") for item in connection_errors)

    unsafe = load_document()
    unsafe["evidence"] = ["../outside.md"]
    assert "unsafe_repo_reference:evidence:../outside.md" in errors(unsafe)


def test_tool_has_no_runtime_actuator_imports_and_only_read_only_commands() -> None:
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
    parser = router.build_parser()
    subparsers_action = next(
        action
        for action in parser._actions  # noqa: SLF001 - parser contract inspection
        if action.dest == "command"
    )
    assert set(subparsers_action.choices) == {
        "validate",
        "route",
        "compile-manifests",
        "trace",
    }


def test_markdown_trace_is_deterministic_plain_language_and_non_executing() -> None:
    document = load_document()
    first = router.render_markdown(document, repo_root=REPO_ROOT)
    second = router.render_markdown(document, repo_root=REPO_ROOT)

    assert first == second
    assert "Execution enabled: **no**" in first
    assert "11-undeclared-event" in first
    assert "requires `grant-availability`" in first
    assert "rejected" in first
    assert "cannot confirm, write, dispatch" in first
