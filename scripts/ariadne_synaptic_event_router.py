"""Validate and explain the non-executing Ariadne Synaptic Event Router proof.

The input is a checked-in authored-synthetic protocol document. This module
performs pure deterministic transforms only: it does not connect to a database,
event feed, product API, model, container, mailbox, worker or command surface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = "ariadne.synaptic_event_router.v1"
ROUTING_VERSION = "ariadne.synaptic_event_router_routing.v1"
MANIFEST_VERSION = "ariadne.synaptic_event_router_manifests.v1"
EVIDENCE_VERSION = "ariadne.synaptic_event_router_evidence.v1"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SENSITIVITY_LEVELS = ("public", "internal", "restricted")
HANDLING_POLICIES = {"reconcile-at-boundary", "cancel-and-supersede"}
LEASE_STATES = {"current", "superseded"}
NODE_STATES = {"active", "superseded"}
REQUIRED_CLOSED_BOUNDARIES = {
    "api-change",
    "appointment-write",
    "autonomous-action",
    "container-runtime",
    "database-connectivity",
    "deployment",
    "event-feed-connectivity",
    "historical-diary",
    "model-provider",
    "pii",
    "product-api",
    "production",
    "protected-evidence",
    "release",
    "stage-3b",
}
FORBIDDEN_KEYS = {
    "access_token",
    "appointment_note",
    "appointment_reason_text",
    "bearer_token",
    "clinical_content",
    "clinical_note",
    "container_command",
    "credential",
    "credentials",
    "database_row",
    "date_of_birth",
    "diagnosis",
    "dob",
    "dsn",
    "endpoint",
    "free_text",
    "medicare_number",
    "model_output",
    "model_reasoning",
    "patient_name",
    "phone_number",
    "prompt",
    "provider_output",
    "raw_instruction",
    "raw_transcript",
    "returned_data",
    "secret",
    "topic",
    "transcript",
}
FORBIDDEN_VALUE_MARKERS = {
    "margaret thompson",
    "dr shera",
    "medicare number",
    "postgresql://",
    "amqp://",
    "kafka://",
    "http://",
    "https://",
}
FORBIDDEN_ACTION_MARKERS = {
    "confirm",
    "commit",
    "create",
    "delete",
    "dispatch",
    "execute",
    "mutate",
    "publish",
    "update",
    "write",
}


class SynapticRouterError(ValueError):
    """Raised for a fail-closed document or CLI error."""


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def canonical_sha256(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def default_document_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "orchestration"
        / "continuity"
        / "ariadne-synaptic-event-router-example.json"
    )


def load_document(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SynapticRouterError(f"document_not_found:{path}") from error
    except json.JSONDecodeError as error:
        raise SynapticRouterError(f"document_invalid_json:{error.msg}") from error
    if not isinstance(payload, dict):
        raise SynapticRouterError("document_must_be_object")
    return payload


def _index(items: Any, *, label: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if not isinstance(items, list):
        return {}, [f"{label}_must_be_array"]
    result: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for position, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}_item_invalid:{position}")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not ID_PATTERN.fullmatch(item_id):
            errors.append(f"{label}_id_invalid:{position}:{item_id}")
        elif item_id in result:
            errors.append(f"{label}_id_duplicate:{item_id}")
        else:
            result[item_id] = item
    return result, errors


def _timestamp(value: Any, *, label: str) -> tuple[datetime | None, list[str]]:
    if not isinstance(value, str):
        return None, [f"timestamp_invalid:{label}:{value}"]
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None, [f"timestamp_invalid:{label}:{value}"]
    if parsed.tzinfo is None:
        return None, [f"timestamp_timezone_required:{label}:{value}"]
    return parsed, []


def _safe_repo_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "://" in value:
        return False
    pure = PurePosixPath(value)
    return not (
        pure.is_absolute()
        or any(part in {"", ".", ".."} for part in pure.parts)
        or ":" in pure.parts[0]
    )


def _sensitive_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text.casefold() in FORBIDDEN_KEYS:
                errors.append(f"sensitive_or_actuator_field_forbidden:{path}.{key_text}")
            errors.extend(_sensitive_errors(child, f"{path}.{key_text}"))
    elif isinstance(value, list):
        for position, child in enumerate(value):
            errors.extend(_sensitive_errors(child, f"{path}[{position}]"))
    elif isinstance(value, str):
        folded = value.casefold()
        for marker in FORBIDDEN_VALUE_MARKERS:
            if marker in folded:
                errors.append(f"sensitive_or_connection_value_forbidden:{path}:{marker}")
    return errors


def _string_set(value: Any, *, label: str) -> tuple[set[str], list[str]]:
    if not isinstance(value, list):
        return set(), [f"{label}_must_be_array"]
    errors: list[str] = []
    result: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item:
            errors.append(f"{label}_value_invalid:{item}")
        elif item in result:
            errors.append(f"{label}_duplicate:{item}")
        else:
            result.add(item)
    return result, errors


def _sensitivity_rank(value: Any) -> int:
    try:
        return SENSITIVITY_LEVELS.index(value)
    except ValueError:
        return -1


def _event_acceptance_pairs(lease: dict[str, Any]) -> set[tuple[str, int]]:
    pairs: set[tuple[str, int]] = set()
    accepted = lease.get("accepted_events", [])
    if not isinstance(accepted, list):
        return pairs
    for declaration in accepted:
        if not isinstance(declaration, dict):
            continue
        event_type = declaration.get("event_type")
        versions = declaration.get("schema_versions", [])
        if isinstance(event_type, str) and isinstance(versions, list):
            for version in versions:
                if isinstance(version, int):
                    pairs.add((event_type, version))
    return pairs


def _route_rule(
    policy: dict[str, Any], event_type: Any, schema_version: Any
) -> dict[str, Any] | None:
    rules = policy.get("rules", [])
    if not isinstance(rules, list):
        return None
    for rule in rules:
        if (
            isinstance(rule, dict)
            and rule.get("event_type") == event_type
            and schema_version in rule.get("schema_versions", [])
        ):
            return rule
    return None


def _selector_intersection_reason(
    event: dict[str, Any], lease: dict[str, Any]
) -> str | None:
    selectors = lease.get("selectors")
    coordinates = event.get("coordinates")
    if not isinstance(selectors, dict) or not isinstance(coordinates, dict):
        return "selector-shape-invalid"
    dimensions = (
        ("aggregate_ids", "aggregate_id", "aggregate"),
        ("practitioner_ids", "practitioner_id", "practitioner"),
        ("location_ids", "location_id", "location"),
        ("projection_ids", "projection_id", "projection"),
        ("proposal_ids", "proposal_id", "proposal"),
    )
    declared_dimensions = 0
    for selector_key, coordinate_key, reason in dimensions:
        selected = selectors.get(selector_key, [])
        if not isinstance(selected, list):
            return f"selector-invalid-{reason}"
        if selected:
            declared_dimensions += 1
            if coordinates.get(coordinate_key) not in selected:
                return f"scope-no-intersection-{reason}"
    window = selectors.get("time_window")
    if window is not None:
        declared_dimensions += 1
        if not isinstance(window, dict):
            return "selector-invalid-time"
        event_start, start_errors = _timestamp(
            coordinates.get("starts_at"), label="event-start"
        )
        event_end, end_errors = _timestamp(coordinates.get("ends_at"), label="event-end")
        lease_start, lease_start_errors = _timestamp(
            window.get("starts_at"), label="lease-start"
        )
        lease_end, lease_end_errors = _timestamp(window.get("ends_at"), label="lease-end")
        if start_errors or end_errors or lease_start_errors or lease_end_errors:
            return "selector-invalid-time"
        assert event_start and event_end and lease_start and lease_end
        if event_start >= event_end or lease_start >= lease_end:
            return "selector-invalid-time"
        if event_end <= lease_start or event_start >= lease_end:
            return "scope-no-intersection-time"
    if declared_dimensions == 0:
        return "scope-selector-empty"
    return None


def _validate_lease_narrowing(
    lease: dict[str, Any], predecessor: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    lease_id = lease.get("id")
    predecessor_id = predecessor.get("id")
    unchanged = {
        "practice_id",
        "principal_id",
        "node_id",
        "instance",
        "attempt",
        "container_generation",
        "policy_revision",
        "mailbox_id",
        "checkpoint_id",
        "handling_policy",
        "accepted_router_instance",
        "accepted_channel",
        "accepted_kind",
    }
    for field in sorted(unchanged):
        if lease.get(field) != predecessor.get(field):
            errors.append(
                f"lease_narrowing_identity_changed:{lease_id}:{predecessor_id}:{field}"
            )
    if not isinstance(lease.get("revision"), int) or lease.get("revision", 0) <= predecessor.get(
        "revision", 0
    ):
        errors.append(f"lease_narrowing_revision_invalid:{lease_id}:{predecessor_id}")
    if predecessor.get("state") != "superseded" or lease.get("state") != "current":
        errors.append(f"lease_narrowing_state_invalid:{lease_id}:{predecessor_id}")
    if not _event_acceptance_pairs(lease) <= _event_acceptance_pairs(predecessor):
        errors.append(f"lease_narrowing_event_expansion:{lease_id}:{predecessor_id}")
    current_frames, frame_errors = _string_set(
        lease.get("accepted_steering_frames"), label=f"lease_frames:{lease_id}"
    )
    prior_frames, prior_frame_errors = _string_set(
        predecessor.get("accepted_steering_frames"),
        label=f"lease_frames:{predecessor_id}",
    )
    errors.extend(frame_errors + prior_frame_errors)
    if not current_frames <= prior_frames:
        errors.append(f"lease_narrowing_frame_expansion:{lease_id}:{predecessor_id}")
    current_selectors = lease.get("selectors", {})
    prior_selectors = predecessor.get("selectors", {})
    for selector in (
        "aggregate_ids",
        "practitioner_ids",
        "location_ids",
        "projection_ids",
        "proposal_ids",
    ):
        current_values = set(current_selectors.get(selector, []))
        prior_values = set(prior_selectors.get(selector, []))
        if not current_values <= prior_values:
            errors.append(
                f"lease_narrowing_selector_expansion:{lease_id}:{predecessor_id}:{selector}"
            )
    current_window = current_selectors.get("time_window")
    prior_window = prior_selectors.get("time_window")
    if (current_window is None) != (prior_window is None):
        errors.append(f"lease_narrowing_time_shape_changed:{lease_id}:{predecessor_id}")
    elif isinstance(current_window, dict) and isinstance(prior_window, dict):
        current_start, errors_a = _timestamp(
            current_window.get("starts_at"), label=f"lease-window:{lease_id}:start"
        )
        current_end, errors_b = _timestamp(
            current_window.get("ends_at"), label=f"lease-window:{lease_id}:end"
        )
        prior_start, errors_c = _timestamp(
            prior_window.get("starts_at"), label=f"lease-window:{predecessor_id}:start"
        )
        prior_end, errors_d = _timestamp(
            prior_window.get("ends_at"), label=f"lease-window:{predecessor_id}:end"
        )
        errors.extend(errors_a + errors_b + errors_c + errors_d)
        if current_start and current_end and prior_start and prior_end:
            if current_start < prior_start or current_end > prior_end:
                errors.append(
                    f"lease_narrowing_time_expansion:{lease_id}:{predecessor_id}"
                )
    if _sensitivity_rank(lease.get("sensitivity_ceiling")) > _sensitivity_rank(
        predecessor.get("sensitivity_ceiling")
    ):
        errors.append(f"lease_narrowing_sensitivity_expansion:{lease_id}:{predecessor_id}")
    return errors


def validate_document(document: dict[str, Any], *, repo_root: Path) -> list[str]:
    """Return deterministic protocol, privacy, isolation and authority errors."""

    errors = _sensitive_errors(document)
    required_top = {
        "schema_version",
        "protocol_id",
        "workflow_id",
        "operational_graph_revision",
        "revision",
        "title",
        "as_of",
        "authority",
        "route_policy",
        "nodes",
        "scope_leases",
        "committed_events",
        "fresh_read_grants",
        "route_attempts",
        "expected_mailbox_deliveries",
        "reconciliation_traces",
        "evidence",
    }
    errors.extend(f"top_level_missing:{key}" for key in sorted(required_top - set(document)))
    errors.extend(f"top_level_unknown:{key}" for key in sorted(set(document) - required_top))
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version_invalid:{document.get('schema_version')}")
    if not isinstance(document.get("protocol_id"), str) or not ID_PATTERN.fullmatch(
        document.get("protocol_id", "")
    ):
        errors.append(f"protocol_id_invalid:{document.get('protocol_id')}")
    if not isinstance(document.get("workflow_id"), str) or not ID_PATTERN.fullmatch(
        document.get("workflow_id", "")
    ):
        errors.append(f"workflow_id_invalid:{document.get('workflow_id')}")
    if not isinstance(document.get("operational_graph_revision"), int) or document.get(
        "operational_graph_revision", 0
    ) < 1:
        errors.append(
            f"operational_graph_revision_invalid:{document.get('operational_graph_revision')}"
        )
    if not isinstance(document.get("revision"), int) or document.get("revision", 0) < 1:
        errors.append(f"revision_invalid:{document.get('revision')}")
    _, as_of_errors = _timestamp(document.get("as_of"), label="as-of")
    errors.extend(as_of_errors)

    authority = document.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority_must_be_object")
        authority = {}
    if authority.get("authored_synthetic_only") is not True:
        errors.append("authority_authored_synthetic_required")
    if authority.get("advisory_only") is not True:
        errors.append("authority_advisory_only_required")
    if authority.get("execution_enabled") is not False:
        errors.append("authority_execution_must_be_false")
    if authority.get("default_decision") != "deny":
        errors.append("authority_default_deny_required")
    boundaries, boundary_errors = _string_set(
        authority.get("closed_boundaries"), label="closed_boundaries"
    )
    errors.extend(boundary_errors)
    errors.extend(
        f"closed_boundary_missing:{boundary}"
        for boundary in sorted(REQUIRED_CLOSED_BOUNDARIES - boundaries)
    )

    policy = document.get("route_policy")
    if not isinstance(policy, dict):
        errors.append("route_policy_must_be_object")
        policy = {}
    if policy.get("default_decision") != "deny":
        errors.append("route_policy_default_deny_required")
    if policy.get("sender_instance") != "synaptic-router":
        errors.append("route_policy_sender_invalid")
    if policy.get("channel") != "control":
        errors.append("route_policy_channel_invalid")
    if policy.get("kind") != "scope-change-notice":
        errors.append("route_policy_kind_invalid")
    if not isinstance(policy.get("revision"), int) or policy.get("revision", 0) < 1:
        errors.append(f"route_policy_revision_invalid:{policy.get('revision')}")
    policy_rules, rule_errors = _index(policy.get("rules"), label="route_rule")
    errors.extend(rule_errors)
    declared_route_pairs: set[tuple[Any, Any]] = set()
    for rule_id, rule in policy_rules.items():
        versions, version_errors = _string_set(
            [str(value) for value in rule.get("schema_versions", [])],
            label=f"route_rule_versions:{rule_id}",
        )
        errors.extend(version_errors)
        if not versions:
            errors.append(f"route_rule_versions_empty:{rule_id}")
        for version in rule.get("schema_versions", []):
            pair = (rule.get("event_type"), version)
            if pair in declared_route_pairs:
                errors.append(
                    f"route_rule_ambiguous:{rule.get('event_type')}:{version}"
                )
            declared_route_pairs.add(pair)
        if rule.get("steering_frame_type") != "scope-change-notice":
            errors.append(f"route_rule_frame_invalid:{rule_id}")
        if _sensitivity_rank(rule.get("sensitivity_max")) < 0:
            errors.append(f"route_rule_sensitivity_invalid:{rule_id}")

    nodes, node_errors = _index(document.get("nodes"), label="node")
    leases, lease_errors = _index(document.get("scope_leases"), label="scope_lease")
    events, event_errors = _index(document.get("committed_events"), label="event")
    grants, grant_errors = _index(
        document.get("fresh_read_grants"), label="fresh_read_grant"
    )
    attempts, attempt_errors = _index(document.get("route_attempts"), label="route_attempt")
    deliveries, delivery_errors = _index(
        document.get("expected_mailbox_deliveries"), label="mailbox_delivery"
    )
    traces, trace_errors = _index(
        document.get("reconciliation_traces"), label="reconciliation_trace"
    )
    errors.extend(
        node_errors
        + lease_errors
        + event_errors
        + grant_errors
        + attempt_errors
        + delivery_errors
        + trace_errors
    )

    current_per_node: dict[str, list[str]] = {}
    for node_id, node in nodes.items():
        if node.get("state") not in NODE_STATES:
            errors.append(f"node_state_invalid:{node_id}:{node.get('state')}")
        for field in ("attempt", "container_generation", "policy_revision"):
            if not isinstance(node.get(field), int) or node.get(field, 0) < 1:
                errors.append(f"node_coordinate_invalid:{node_id}:{field}")
        if node.get("practice_id") != policy.get("practice_id"):
            errors.append(f"node_practice_outside_policy:{node_id}")
        if node.get("principal_id") != policy.get("principal_id"):
            errors.append(f"node_principal_outside_policy:{node_id}")

    for lease_id, lease in leases.items():
        node = nodes.get(lease.get("node_id"))
        if node is None:
            errors.append(f"lease_node_unknown:{lease_id}:{lease.get('node_id')}")
        else:
            for field in (
                "practice_id",
                "principal_id",
                "instance",
                "attempt",
                "container_generation",
                "policy_revision",
                "mailbox_id",
                "checkpoint_id",
            ):
                if lease.get(field) != node.get(field):
                    errors.append(f"lease_node_coordinate_mismatch:{lease_id}:{field}")
        if lease.get("state") not in LEASE_STATES:
            errors.append(f"lease_state_invalid:{lease_id}:{lease.get('state')}")
        if lease.get("handling_policy") not in HANDLING_POLICIES:
            errors.append(f"lease_handling_policy_invalid:{lease_id}")
        if lease.get("accepted_router_instance") != policy.get("sender_instance"):
            errors.append(f"lease_router_instance_not_bilateral:{lease_id}")
        if lease.get("accepted_channel") != policy.get("channel"):
            errors.append(f"lease_channel_not_bilateral:{lease_id}")
        if lease.get("accepted_kind") != policy.get("kind"):
            errors.append(f"lease_kind_not_bilateral:{lease_id}")
        if not isinstance(lease.get("revision"), int) or lease.get("revision", 0) < 1:
            errors.append(f"lease_revision_invalid:{lease_id}")
        if lease.get("state") == "current":
            current_per_node.setdefault(str(lease.get("node_id")), []).append(lease_id)
        expires, expiry_errors = _timestamp(lease.get("expires_at"), label=f"lease:{lease_id}")
        errors.extend(expiry_errors)
        if expires is None:
            continue
        if _sensitivity_rank(lease.get("sensitivity_ceiling")) < 0:
            errors.append(f"lease_sensitivity_invalid:{lease_id}")
        frames, frame_errors = _string_set(
            lease.get("accepted_steering_frames"), label=f"lease_frames:{lease_id}"
        )
        errors.extend(frame_errors)
        if not frames:
            errors.append(f"lease_frames_empty:{lease_id}")
        if not _event_acceptance_pairs(lease):
            errors.append(f"lease_events_empty:{lease_id}")
        if _selector_intersection_reason(
            {
                "coordinates": {
                    "aggregate_id": None,
                    "practitioner_id": None,
                    "location_id": None,
                    "projection_id": None,
                    "proposal_id": None,
                    "starts_at": document.get("as_of"),
                    "ends_at": document.get("as_of"),
                }
            },
            lease,
        ) == "scope-selector-empty":
            errors.append(f"lease_selectors_empty:{lease_id}")
        selectors = lease.get("selectors", {})
        window = selectors.get("time_window") if isinstance(selectors, dict) else None
        if isinstance(window, dict):
            starts, start_errors = _timestamp(
                window.get("starts_at"), label=f"lease-window:{lease_id}:start"
            )
            ends, end_errors = _timestamp(
                window.get("ends_at"), label=f"lease-window:{lease_id}:end"
            )
            errors.extend(start_errors + end_errors)
            if starts and ends and starts >= ends:
                errors.append(f"lease_time_window_invalid:{lease_id}")
        predecessor_id = lease.get("narrowed_from")
        if predecessor_id is not None:
            predecessor = leases.get(predecessor_id)
            if predecessor is None:
                errors.append(f"lease_narrowed_from_unknown:{lease_id}:{predecessor_id}")
            else:
                errors.extend(_validate_lease_narrowing(lease, predecessor))
    for node_id, lease_ids in current_per_node.items():
        if len(lease_ids) != 1:
            errors.append(f"node_current_lease_count:{node_id}:{len(lease_ids)}")

    for event_id, event in events.items():
        if event.get("committed") is not True:
            errors.append(f"event_not_committed:{event_id}")
        if not isinstance(event.get("schema_version"), int) or event.get(
            "schema_version", 0
        ) < 1:
            errors.append(f"event_schema_version_invalid:{event_id}")
        if not isinstance(event.get("aggregate_revision"), int) or event.get(
            "aggregate_revision", 0
        ) < 1:
            errors.append(f"event_aggregate_revision_invalid:{event_id}")
        if _sensitivity_rank(event.get("sensitivity")) < 0:
            errors.append(f"event_sensitivity_invalid:{event_id}")
        coordinates = event.get("coordinates")
        if not isinstance(coordinates, dict):
            errors.append(f"event_coordinates_invalid:{event_id}")
        elif coordinates.get("aggregate_id") != event.get("aggregate_id"):
            errors.append(f"event_aggregate_coordinate_mismatch:{event_id}")
        if isinstance(coordinates, dict):
            starts, start_errors = _timestamp(
                coordinates.get("starts_at"), label=f"event:{event_id}:start"
            )
            ends, end_errors = _timestamp(
                coordinates.get("ends_at"), label=f"event:{event_id}:end"
            )
            errors.extend(start_errors + end_errors)
            if starts and ends and starts >= ends:
                errors.append(f"event_time_window_invalid:{event_id}")
        _, occurred_errors = _timestamp(
            event.get("occurred_at"), label=f"event:{event_id}:occurred"
        )
        errors.extend(occurred_errors)

    for grant_id, grant in grants.items():
        lease = leases.get(grant.get("lease_id"))
        event = events.get(grant.get("event_id"))
        if lease is None:
            errors.append(f"grant_lease_unknown:{grant_id}:{grant.get('lease_id')}")
        if event is None:
            errors.append(f"grant_event_unknown:{grant_id}:{grant.get('event_id')}")
        if grant.get("execution_enabled") is not False:
            errors.append(f"grant_execution_must_be_false:{grant_id}")
        if grant.get("returns_data") is not False:
            errors.append(f"grant_returns_data_must_be_false:{grant_id}")
        action = grant.get("action")
        if action != "read-scoped-context" or any(
            marker in str(action).casefold() for marker in FORBIDDEN_ACTION_MARKERS
        ):
            errors.append(f"grant_action_invalid:{grant_id}:{action}")
        issued, issued_errors = _timestamp(grant.get("issued_at"), label=f"grant:{grant_id}:issued")
        expires, expires_errors = _timestamp(
            grant.get("expires_at"), label=f"grant:{grant_id}:expires"
        )
        errors.extend(issued_errors + expires_errors)
        if issued and expires and issued >= expires:
            errors.append(f"grant_expiry_invalid:{grant_id}")
        if lease and event:
            for field in ("practice_id", "principal_id"):
                if grant.get(field) != lease.get(field) or grant.get(field) != event.get(field):
                    errors.append(f"grant_boundary_mismatch:{grant_id}:{field}")
            if grant.get("aggregate_revision") != event.get("aggregate_revision"):
                errors.append(f"grant_revision_mismatch:{grant_id}")
            occurred, occurred_errors = _timestamp(
                event.get("occurred_at"), label=f"grant:{grant_id}:event-occurred"
            )
            errors.extend(occurred_errors)
            if issued and occurred and issued < occurred:
                errors.append(f"grant_issued_before_event:{grant_id}")
            expected_resources = {
                f"appointment/{event.get('aggregate_id')}",
                f"projection/{event.get('coordinates', {}).get('projection_id')}",
            }
            resources, resource_errors = _string_set(
                grant.get("resource_selectors"), label=f"grant_resources:{grant_id}"
            )
            errors.extend(resource_errors)
            if resources != expected_resources:
                errors.append(f"grant_resources_not_exact:{grant_id}")

    computed = build_routing(document, validate=False)
    actual_decisions = computed["decisions"]
    for attempt_id, attempt in attempts.items():
        decision = next(
            (item for item in actual_decisions if item["attempt_id"] == attempt_id), None
        )
        if decision is None:
            errors.append(f"route_decision_missing:{attempt_id}")
            continue
        if decision.get("decision") != attempt.get("expected_decision"):
            errors.append(
                f"route_decision_mismatch:{attempt_id}:{decision.get('decision')}:"
                f"{attempt.get('expected_decision')}"
            )
        if decision.get("reason") != attempt.get("expected_reason"):
            errors.append(
                f"route_reason_mismatch:{attempt_id}:{decision.get('reason')}:"
                f"{attempt.get('expected_reason')}"
            )
    computed_deliveries = computed["deliveries"]
    if canonical_json(computed_deliveries) != canonical_json(list(deliveries.values())):
        errors.append("mailbox_deliveries_do_not_match_computed_routes")

    delivered_attempts = {
        item["attempt_id"] for item in actual_decisions if item["decision"] == "deliver"
    }
    trace_attempts = {trace.get("route_attempt_id") for trace in traces.values()}
    if trace_attempts != delivered_attempts:
        errors.append("reconciliation_trace_coverage_invalid")
    for trace_id, trace in traces.items():
        attempt = attempts.get(trace.get("route_attempt_id"))
        if attempt is None:
            errors.append(f"trace_attempt_unknown:{trace_id}")
            continue
        lease = leases.get(attempt.get("lease_id"))
        grant = grants.get(trace.get("fresh_read_grant_id"))
        if lease is None or grant is None:
            errors.append(f"trace_lease_or_grant_unknown:{trace_id}")
            continue
        if trace.get("handling_policy") != lease.get("handling_policy"):
            errors.append(f"trace_handling_policy_mismatch:{trace_id}")
        if grant.get("lease_id") != lease.get("id") or grant.get("event_id") != attempt.get(
            "event_id"
        ):
            errors.append(f"trace_grant_link_invalid:{trace_id}")
        if trace.get("command_authority") is not False:
            errors.append(f"trace_command_authority_must_be_false:{trace_id}")
        if lease.get("handling_policy") == "reconcile-at-boundary":
            if trace.get("outcome") != "awaiting-fresh-read":
                errors.append(f"trace_reconcile_outcome_invalid:{trace_id}")
            if trace.get("boundary") != "mailbox-checkpoint-boundary":
                errors.append(f"trace_reconcile_boundary_invalid:{trace_id}")
        else:
            supersession = trace.get("supersession")
            if not isinstance(supersession, dict):
                errors.append(f"trace_supersession_missing:{trace_id}")
                continue
            old_node = nodes.get(lease.get("node_id"), {})
            if supersession.get("superseded_from") != old_node.get("id"):
                errors.append(f"trace_superseded_from_invalid:{trace_id}")
            if supersession.get("instance") != old_node.get("instance"):
                errors.append(f"trace_supersession_instance_invalid:{trace_id}")
            if supersession.get("practice_id") != old_node.get("practice_id") or supersession.get(
                "principal_id"
            ) != old_node.get("principal_id"):
                errors.append(f"trace_supersession_boundary_invalid:{trace_id}")
            if supersession.get("attempt") != old_node.get("attempt", 0) + 1:
                errors.append(f"trace_supersession_attempt_invalid:{trace_id}")
            if supersession.get("container_generation") != old_node.get(
                "container_generation", 0
            ) + 1:
                errors.append(f"trace_supersession_generation_invalid:{trace_id}")
            if supersession.get("policy_revision") <= old_node.get("policy_revision", 0):
                errors.append(f"trace_supersession_policy_revision_invalid:{trace_id}")
            if supersession.get("checkpoint_id") != old_node.get("checkpoint_id"):
                errors.append(f"trace_supersession_checkpoint_invalid:{trace_id}")
            decision = next(
                (
                    item
                    for item in actual_decisions
                    if item["attempt_id"] == trace.get("route_attempt_id")
                ),
                {},
            )
            if supersession.get("notice_delivery_id") != decision.get("delivery_id"):
                errors.append(f"trace_supersession_notice_invalid:{trace_id}")
            if supersession.get("fresh_read_grant_id") != trace.get(
                "fresh_read_grant_id"
            ):
                errors.append(f"trace_supersession_grant_invalid:{trace_id}")
            if supersession.get("state") != "awaiting-fresh-read":
                errors.append(f"trace_supersession_state_invalid:{trace_id}")
            stale = trace.get("stale_completion")
            if not isinstance(stale, dict) or stale.get("node_id") != old_node.get("id"):
                errors.append(f"trace_stale_completion_node_invalid:{trace_id}")
            elif stale.get("disposition") != "rejected-stale-generation":
                errors.append(f"trace_stale_completion_not_rejected:{trace_id}")
            elif stale.get("container_generation") != old_node.get(
                "container_generation"
            ):
                errors.append(f"trace_stale_completion_generation_invalid:{trace_id}")
            if trace.get("outcome") != "superseded-awaiting-fresh-read":
                errors.append(f"trace_supersession_outcome_invalid:{trace_id}")

    evidence = document.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence_must_be_array")
    else:
        for value in evidence:
            if not _safe_repo_reference(value):
                errors.append(f"unsafe_repo_reference:evidence:{value}")
            elif not (repo_root / value).is_file():
                errors.append(f"evidence_file_missing:{value}")
    return sorted(set(errors))


def _route_one(
    *,
    event: dict[str, Any] | None,
    lease: dict[str, Any] | None,
    policy: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    grants: dict[str, dict[str, Any]],
    workflow_id: Any,
    operational_graph_revision: Any,
    attempt_id: Any,
    evaluated_at: Any,
    seen: set[tuple[Any, ...]],
) -> tuple[str, str, dict[str, Any] | None]:
    if event is None:
        return "suppress", "event-unknown", None
    if lease is None:
        return "suppress", "lease-unknown", None
    if event.get("committed") is not True:
        return "suppress", "event-not-committed", None
    rule = _route_rule(policy, event.get("event_type"), event.get("schema_version"))
    if rule is None:
        return "suppress", "event-type-or-version-not-declared", None
    if lease.get("state") != "current":
        return "suppress", "lease-superseded", None
    node = nodes.get(lease.get("node_id"))
    if node is None or node.get("state") != "active":
        return "suppress", "node-generation-not-current", None
    evaluated, evaluated_errors = _timestamp(evaluated_at, label="route-evaluated")
    expires, expiry_errors = _timestamp(lease.get("expires_at"), label="lease-expires")
    if evaluated_errors or expiry_errors or evaluated is None or expires is None:
        return "suppress", "lease-time-invalid", None
    if evaluated >= expires:
        return "suppress", "lease-expired", None
    if event.get("practice_id") != policy.get("practice_id") or event.get(
        "practice_id"
    ) != lease.get("practice_id"):
        return "suppress", "practice-boundary-mismatch", None
    if event.get("principal_id") != policy.get("principal_id") or event.get(
        "principal_id"
    ) != lease.get("principal_id"):
        return "suppress", "principal-boundary-mismatch", None
    if lease.get("policy_revision") != policy.get("revision"):
        return "suppress", "policy-revision-mismatch", None
    if lease.get("accepted_router_instance") != policy.get("sender_instance"):
        return "suppress", "router-instance-not-bilateral", None
    if lease.get("accepted_channel") != policy.get("channel"):
        return "suppress", "steering-channel-not-bilateral", None
    if lease.get("accepted_kind") != policy.get("kind"):
        return "suppress", "steering-kind-not-bilateral", None
    event_pair = (event.get("event_type"), event.get("schema_version"))
    if event_pair not in _event_acceptance_pairs(lease):
        return "suppress", "lease-event-not-declared", None
    frame_type = rule.get("steering_frame_type")
    if frame_type not in lease.get("accepted_steering_frames", []):
        return "suppress", "steering-frame-not-bilateral", None
    event_rank = _sensitivity_rank(event.get("sensitivity"))
    if event_rank < 0 or event_rank > _sensitivity_rank(rule.get("sensitivity_max")):
        return "suppress", "route-policy-sensitivity-denied", None
    if event_rank > _sensitivity_rank(lease.get("sensitivity_ceiling")):
        return "suppress", "lease-sensitivity-denied", None
    if event.get("aggregate_revision", 0) <= lease.get("minimum_aggregate_revision", 0):
        return "suppress", "aggregate-revision-not-newer", None
    if event.get("aggregate_revision", 0) <= lease.get(
        "mailbox_checkpoint_revision", 0
    ):
        return "suppress", "mailbox-checkpoint-not-newer", None
    intersection_reason = _selector_intersection_reason(event, lease)
    if intersection_reason is not None:
        return "suppress", intersection_reason, None
    dedup = (
        event.get("id"),
        lease.get("id"),
        lease.get("revision"),
        lease.get("container_generation"),
        frame_type,
    )
    if dedup in seen:
        return "suppress", "replay-duplicate-coordinate", None
    grant = grants.get(lease.get("fresh_read_grant_id"))
    if grant is None:
        return "suppress", "fresh-read-grant-missing", None
    if grant.get("event_id") != event.get("id") or grant.get("lease_id") != lease.get("id"):
        return "suppress", "fresh-read-grant-link-mismatch", None
    grant_expiry, grant_expiry_errors = _timestamp(
        grant.get("expires_at"), label="grant-expires"
    )
    if grant_expiry_errors or grant_expiry is None or evaluated >= grant_expiry:
        return "suppress", "fresh-read-grant-expired", None
    seen.add(dedup)
    coordinates = event.get("coordinates", {})
    delivery = {
        "id": "delivery-" + str(event.get("id")) + "-" + str(lease.get("id")),
        "workflow_id": workflow_id,
        "operational_graph_revision": operational_graph_revision,
        "sender_instance": policy.get("sender_instance"),
        "recipient_node_id": lease.get("node_id"),
        "channel": policy.get("channel"),
        "kind": policy.get("kind"),
        "correlation_id": "steer-" + str(event.get("id")) + "-" + str(lease.get("id")),
        "mailbox_id": lease.get("mailbox_id"),
        "event_id": event.get("id"),
        "event_type": event.get("event_type"),
        "event_schema_version": event.get("schema_version"),
        "lease_id": lease.get("id"),
        "lease_revision": lease.get("revision"),
        "node_id": lease.get("node_id"),
        "container_generation": lease.get("container_generation"),
        "steering_frame_type": frame_type,
        "aggregate_id": event.get("aggregate_id"),
        "aggregate_revision": event.get("aggregate_revision"),
        "affected_coordinates": {
            "practitioner_id": coordinates.get("practitioner_id"),
            "location_id": coordinates.get("location_id"),
            "starts_at": coordinates.get("starts_at"),
            "ends_at": coordinates.get("ends_at"),
            "projection_id": coordinates.get("projection_id"),
            "proposal_id": coordinates.get("proposal_id"),
        },
        "freshness_required": True,
        "route_reason": "exact-scope-intersection",
        "fresh_read_grant_id": grant.get("id"),
        "provenance": {
            "kind": "authored-synthetic-committed-event",
            "source": event.get("id"),
            "source_message_ids": [],
            "source_route_attempt_id": attempt_id,
        },
        "freshness": {
            "status": "requires-fresh-read",
            "observed_at": event.get("occurred_at"),
            "maximum_age_seconds": 0,
        },
        "execution_enabled": False,
    }
    return "deliver", "exact-scope-intersection", delivery


def build_routing(
    document: dict[str, Any], *, repo_root: Path | None = None, validate: bool = True
) -> dict[str, Any]:
    if validate:
        if repo_root is None:
            raise SynapticRouterError("repo_root_required_for_validation")
        errors = validate_document(document, repo_root=repo_root)
        if errors:
            raise SynapticRouterError(";".join(errors))
    nodes, _ = _index(document.get("nodes"), label="node")
    leases, _ = _index(document.get("scope_leases"), label="scope_lease")
    events, _ = _index(document.get("committed_events"), label="event")
    grants, _ = _index(document.get("fresh_read_grants"), label="fresh_read_grant")
    seen: set[tuple[Any, ...]] = set()
    decisions: list[dict[str, Any]] = []
    deliveries: list[dict[str, Any]] = []
    for attempt in document.get("route_attempts", []):
        decision, reason, delivery = _route_one(
            event=events.get(attempt.get("event_id")),
            lease=leases.get(attempt.get("lease_id")),
            policy=document.get("route_policy", {}),
            nodes=nodes,
            grants=grants,
            workflow_id=document.get("workflow_id"),
            operational_graph_revision=document.get("operational_graph_revision"),
            attempt_id=attempt.get("id"),
            evaluated_at=attempt.get("evaluated_at"),
            seen=seen,
        )
        decisions.append(
            {
                "attempt_id": attempt.get("id"),
                "event_id": attempt.get("event_id"),
                "lease_id": attempt.get("lease_id"),
                "decision": decision,
                "reason": reason,
                "delivery_id": delivery.get("id") if delivery else None,
            }
        )
        if delivery:
            deliveries.append(delivery)
    return {
        "schema_version": ROUTING_VERSION,
        "protocol_id": document.get("protocol_id"),
        "source_revision": document.get("revision"),
        "status": "passed",
        "execution_enabled": False,
        "decisions": decisions,
        "deliveries": deliveries,
    }


def compile_manifests(
    document: dict[str, Any], *, repo_root: Path | None = None, validate: bool = True
) -> dict[str, Any]:
    if validate:
        if repo_root is None:
            raise SynapticRouterError("repo_root_required_for_validation")
        errors = validate_document(document, repo_root=repo_root)
        if errors:
            raise SynapticRouterError(";".join(errors))
    policy = document.get("route_policy", {})
    nodes, _ = _index(document.get("nodes"), label="node")
    as_of, _ = _timestamp(document.get("as_of"), label="manifest-as-of")
    current_leases: list[dict[str, Any]] = []
    rejected_leases: list[dict[str, Any]] = []
    for lease in sorted(
        document.get("scope_leases", []), key=lambda item: str(item.get("id"))
    ):
        node = nodes.get(lease.get("node_id"), {})
        expires, _ = _timestamp(lease.get("expires_at"), label="manifest-lease-expires")
        reason: str | None = None
        if lease.get("state") != "current":
            reason = "lease-superseded"
        elif node.get("state") != "active":
            reason = "node-generation-not-current"
        elif as_of is None or expires is None or as_of >= expires:
            reason = "lease-expired"
        elif lease.get("policy_revision") != policy.get("revision"):
            reason = "policy-revision-mismatch"
        elif lease.get("accepted_router_instance") != policy.get("sender_instance"):
            reason = "router-instance-not-bilateral"
        elif lease.get("accepted_channel") != policy.get("channel"):
            reason = "steering-channel-not-bilateral"
        elif lease.get("accepted_kind") != policy.get("kind"):
            reason = "steering-kind-not-bilateral"
        elif not any(
            _route_rule(policy, event_type, schema_version)
            and _route_rule(policy, event_type, schema_version).get(
                "steering_frame_type"
            )
            in lease.get("accepted_steering_frames", [])
            for event_type, schema_version in _event_acceptance_pairs(lease)
        ):
            reason = "event-frame-route-not-bilateral"
        if reason:
            rejected_leases.append(
                {"lease_id": lease.get("id"), "compile_disposition": "deny", "reason": reason}
            )
            continue
        current_leases.append(
            {
                "lease_id": lease.get("id"),
                "lease_revision": lease.get("revision"),
                "node_id": lease.get("node_id"),
                "container_generation": lease.get("container_generation"),
                "mailbox_id": lease.get("mailbox_id"),
                "checkpoint_id": lease.get("checkpoint_id"),
                "handling_policy": lease.get("handling_policy"),
                "accepted_router_instance": lease.get("accepted_router_instance"),
                "accepted_channel": lease.get("accepted_channel"),
                "accepted_kind": lease.get("accepted_kind"),
                "accepted_events": lease.get("accepted_events"),
                "accepted_steering_frames": lease.get("accepted_steering_frames"),
                "selectors": lease.get("selectors"),
                "expires_at": lease.get("expires_at"),
                "sensitivity_ceiling": lease.get("sensitivity_ceiling"),
            }
        )
    subscriptions = sorted(
        (
            {
                "event_type": rule.get("event_type"),
                "schema_versions": sorted(rule.get("schema_versions", [])),
                "steering_frame_type": rule.get("steering_frame_type"),
                "sensitivity_max": rule.get("sensitivity_max"),
            }
            for rule in policy.get("rules", [])
        ),
        key=lambda item: str(item["event_type"]),
    )
    return {
        "schema_version": MANIFEST_VERSION,
        "source_protocol_id": document.get("protocol_id"),
        "workflow_id": document.get("workflow_id"),
        "operational_graph_revision": document.get("operational_graph_revision"),
        "source_revision": document.get("revision"),
        "source_sha256": canonical_sha256(document),
        "compiled_at": document.get("as_of"),
        "authority": {
            "dry_run": True,
            "execution_enabled": False,
            "default_decision": "deny",
            "adapters_configured": False,
        },
        "startup_manifest": {
            "kind": "inspectable-startup-policy",
            "practice_id": policy.get("practice_id"),
            "principal_id": policy.get("principal_id"),
            "policy_id": policy.get("id"),
            "policy_revision": policy.get("revision"),
            "default_decision": "deny",
            "compiled_scope_leases": current_leases,
            "rejected_scope_leases": rejected_leases,
            "mailbox_contract": {
                "sender_instance": policy.get("sender_instance"),
                "channel": policy.get("channel"),
                "kind": policy.get("kind"),
                "frame_type": "scope-change-notice",
                "delivery_boundary": "declared-mailbox-checkpoint",
                "deduplication_coordinate": [
                    "event-id",
                    "lease-id",
                    "lease-revision",
                    "container-generation",
                    "steering-frame-type",
                ],
            },
            "fresh_read_grant_contract": {
                "action": "read-scoped-context",
                "exact_practice_principal_role_action_resource_required": True,
                "execution_enabled": False,
                "returns_data": False,
            },
        },
        "subscription_manifest": {
            "kind": "inspectable-subscription-policy",
            "practice_partition": policy.get("practice_id"),
            "default_decision": "deny",
            "subscriptions": subscriptions,
            "connection_configured": False,
        },
        "restart_policy_manifest": {
            "kind": "inspectable-restart-policy",
            "default_decision": "deny",
            "same_generation_lease_change": "narrow-only",
            "scope_expansion": "new-container-generation-and-higher-policy-revision",
            "supersession_requires": [
                "exact-practice-and-principal",
                "same-instance",
                "incremented-attempt",
                "incremented-container-generation",
                "higher-policy-revision",
                "exact-checkpoint-lineage",
                "bound-scope-change-notice",
                "bound-fresh-read-grant",
            ],
            "stale_completion_disposition": "rejected-stale-generation",
        },
    }


def build_evidence(document: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    errors = validate_document(document, repo_root=repo_root)
    if errors:
        raise SynapticRouterError(";".join(errors))
    routing = build_routing(document, validate=False)
    manifests = compile_manifests(document, validate=False)
    delivered = [item for item in routing["decisions"] if item["decision"] == "deliver"]
    suppressed = [item for item in routing["decisions"] if item["decision"] == "suppress"]
    return {
        "schema_version": EVIDENCE_VERSION,
        "result": "ariadne_synaptic_event_router_protocol_pass",
        "evidence_label": "authored_synthetic_repository_local_non_executing",
        "source_protocol_id": document.get("protocol_id"),
        "source_revision": document.get("revision"),
        "source_sha256": canonical_sha256(document),
        "manifest_sha256": canonical_sha256(manifests),
        "route_attempt_count": len(routing["decisions"]),
        "delivery_count": len(delivered),
        "suppression_count": len(suppressed),
        "suppression_reasons": sorted({item["reason"] for item in suppressed}),
        "proofs": {
            "exact_match": True,
            "fan_out": len(delivered) >= 2,
            "replay_suppressed": any(
                item["reason"] == "replay-duplicate-coordinate" for item in suppressed
            ),
            "cross_practice_suppressed": any(
                item["reason"] == "practice-boundary-mismatch" for item in suppressed
            ),
            "stale_generation_suppressed": any(
                item["reason"] in {"lease-superseded", "node-generation-not-current"}
                for item in suppressed
            ),
            "fresh_read_grants_non_executing": all(
                grant.get("execution_enabled") is False and grant.get("returns_data") is False
                for grant in document.get("fresh_read_grants", [])
            ),
            "supersession_rejects_stale_completion": any(
                (trace.get("stale_completion") or {}).get("disposition")
                == "rejected-stale-generation"
                for trace in document.get("reconciliation_traces", [])
            ),
            "typed_exchange_grammar_preserved": all(
                delivery.get("workflow_id") == document.get("workflow_id")
                and delivery.get("operational_graph_revision")
                == document.get("operational_graph_revision")
                and delivery.get("sender_instance") == "synaptic-router"
                and delivery.get("recipient_node_id") == delivery.get("node_id")
                and delivery.get("channel") == "control"
                and delivery.get("kind") == "scope-change-notice"
                and isinstance(delivery.get("provenance"), dict)
                and isinstance(delivery.get("freshness"), dict)
                for delivery in routing["deliveries"]
            ),
            "manifests_default_deny_and_non_executing": (
                manifests["authority"]["default_decision"] == "deny"
                and manifests["authority"]["execution_enabled"] is False
            ),
        },
        "closed_connections": sorted(REQUIRED_CLOSED_BOUNDARIES),
    }


def render_markdown(document: dict[str, Any], *, repo_root: Path) -> str:
    routing = build_routing(document, repo_root=repo_root)
    lines = [
        "# Ariadne Synaptic Event Router - Authored-Synthetic Trace",
        "",
        f"Result: `{build_evidence(document, repo_root=repo_root)['result']}`",
        "",
        "Execution enabled: **no**",
        "",
        "This is a deterministic repository-local protocol trace. It does not read a",
        "database or event feed, contact a product API or model, start a container,",
        "deliver to a live mailbox, or issue a command.",
        "",
        "## Routing decisions",
        "",
        "| Attempt | Event | Lease | Decision | Reason |",
        "|---|---|---|---|---|",
    ]
    for decision in routing["decisions"]:
        lines.append(
            "| {attempt_id} | {event_id} | {lease_id} | {decision} | {reason} |".format(
                **decision
            )
        )
    lines.extend(
        [
            "",
            "## Mailbox steering",
            "",
        ]
    )
    for delivery in routing["deliveries"]:
        lines.append(
            f"- `{delivery['id']}` marks `{delivery['aggregate_id']}` revision "
            f"{delivery['aggregate_revision']} stale for `{delivery['node_id']}` and "
            f"requires `{delivery['fresh_read_grant_id']}` at its declared boundary."
        )
    lines.extend(
        [
            "",
            "## Authority stop",
            "",
            "Every notice is a staleness cue, every fresh-read grant is inert, and every",
            "superseded completion is rejected. The trace cannot confirm, write, dispatch",
            "or execute an EMR action.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect the non-executing Ariadne Synaptic Event Router proof."
    )
    parser.add_argument("--document", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate the authored-synthetic document.")
    subparsers.add_parser("route", help="Render deterministic route decisions as JSON.")
    subparsers.add_parser(
        "compile-manifests", help="Render inert dry-run policy manifests as JSON."
    )
    subparsers.add_parser("trace", help="Render a plain-language Markdown trace.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    path = args.document or default_document_path(repo_root)
    try:
        document = load_document(path)
        if args.command == "validate":
            errors = validate_document(document, repo_root=repo_root)
            payload = {
                "schema_version": SCHEMA_VERSION,
                "status": "passed" if not errors else "revision_required",
                "execution_enabled": False,
                "errors": errors,
            }
            print(canonical_json(payload), end="")
            return 0 if not errors else 2
        if args.command == "route":
            print(canonical_json(build_routing(document, repo_root=repo_root)), end="")
            return 0
        if args.command == "compile-manifests":
            print(canonical_json(compile_manifests(document, repo_root=repo_root)), end="")
            return 0
        if args.command == "trace":
            print(render_markdown(document, repo_root=repo_root), end="")
            return 0
    except SynapticRouterError as error:
        print(f"synaptic event router failed: {error}")
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
