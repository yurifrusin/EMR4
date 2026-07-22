"""Validate and explain a non-executing Ariadne sandbox-DAG protocol trace.

The document is an authored-synthetic architectural artifact. This tool does
not invoke models, spawn workers, read product data, issue commands or write
files. Exchanges are immutable graph edges; a context round trip creates later
orchestrator and sandbox attempts so the history remains acyclic.
"""

from __future__ import annotations

import argparse
import heapq
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from scripts import ariadne_continuity as continuity
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    import ariadne_continuity as continuity  # type: ignore[no-redef]


SCHEMA_VERSION = "ariadne.sandbox_dag.v1"
TRACE_VERSION = "ariadne.sandbox_dag_trace.v1"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

ROLES = {
    "orchestrator",
    "sandbox",
    "join",
    "human-context-source",
    "human-authority-gate",
    "evidence-sink",
}
NODE_STATES = {
    "ready",
    "complete",
    "needs-context",
    "blocked",
    "awaiting-human-authority",
}
ANALYTICAL_CAPABILITIES = {
    "inspect-typed-frame",
    "request-typed-context",
    "evaluate-predicate",
    "emit-candidate-transition",
    "record-evidence",
}
CHANNEL_KINDS = {
    "data": {"input", "context-grant", "result", "join-input"},
    "control": {
        "context-request",
        "context-source-request",
        "context-denial",
        "candidate-transition",
        "authority-gate",
    },
    "evidence": {"evidence-receipt"},
}
REQUIRED_CLOSED_BOUNDARIES = {
    "api-change",
    "appointment-write",
    "autonomous-action",
    "deployment",
    "event-runtime",
    "historical-diary",
    "production",
    "protected-evidence",
    "provider-call",
    "release",
    "pii",
    "stage-3b",
    "voice",
}
FORBIDDEN_KEYS = {
    "password",
    "secret",
    "token",
    "access_token",
    "bearer_token",
    "credential",
    "credentials",
    "raw_transcript",
    "transcript",
    "prompt",
    "model_reasoning",
    "pii",
    "date_of_birth",
    "dob",
    "medicare_number",
    "clinical_note",
    "diagnosis",
}
FORBIDDEN_VALUE_MARKERS = {
    "margaret thompson",
    "dr shera",
    "medicare number",
    "clinical note",
}
FORBIDDEN_EXECUTION_VALUES = {
    "confirmed",
    "committed",
    "dispatched",
    "executed",
    "write-authorized",
    "write-authorised",
}


class SandboxDagError(ValueError):
    """Raised for a fail-closed document or command error."""


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def default_document_path(repo_root: Path) -> Path:
    return repo_root / "orchestration" / "continuity" / "ariadne-sandbox-dag-example.json"


def load_document(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SandboxDagError(f"document_not_found:{path}") from error
    except json.JSONDecodeError as error:
        raise SandboxDagError(f"document_invalid_json:{error.msg}") from error
    if not isinstance(payload, dict):
        raise SandboxDagError("document_must_be_object")
    return payload


def _ids(items: Any, *, label: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    index: dict[str, dict[str, Any]] = {}
    if not isinstance(items, list):
        return {}, [f"{label}_must_be_array"]
    for position, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}_item_invalid:{position}")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not ID_PATTERN.fullmatch(item_id):
            errors.append(f"{label}_id_invalid:{position}:{item_id}")
            continue
        if item_id in index:
            errors.append(f"{label}_id_duplicate:{item_id}")
            continue
        index[item_id] = item
    return index, errors


def _sensitive_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text.casefold() in FORBIDDEN_KEYS:
                errors.append(f"sensitive_field_forbidden:{path}.{key_text}")
            errors.extend(_sensitive_errors(child, f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_sensitive_errors(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        folded = value.casefold()
        for marker in FORBIDDEN_VALUE_MARKERS:
            if marker in folded:
                errors.append(f"sensitive_value_forbidden:{path}:{marker}")
    return errors


def _safe_repo_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "://" in value:
        return False
    pure = PurePosixPath(value)
    return not (
        pure.is_absolute()
        or any(part in {"", ".", ".."} for part in pure.parts)
        or ":" in pure.parts[0]
    )


def _string_ids(value: Any, *, label: str) -> tuple[list[str], list[str]]:
    if not isinstance(value, list):
        return [], [f"{label}_must_be_array"]
    result: list[str] = []
    errors: list[str] = []
    for item in value:
        if not isinstance(item, str) or not ID_PATTERN.fullmatch(item):
            errors.append(f"{label}_id_invalid:{item}")
        else:
            result.append(item)
    if len(result) != len(set(result)):
        errors.append(f"{label}_duplicate")
    return result, errors


def _topological_order(
    nodes: dict[str, dict[str, Any]], exchanges: list[dict[str, Any]]
) -> tuple[list[str], list[str]]:
    indegree = {node_id: 0 for node_id in nodes}
    children: dict[str, set[str]] = {node_id: set() for node_id in nodes}
    for exchange in exchanges:
        sender = exchange.get("sender")
        recipient = exchange.get("recipient")
        if sender not in nodes or recipient not in nodes or sender == recipient:
            continue
        if recipient not in children[sender]:
            children[sender].add(recipient)
            indegree[recipient] += 1
    ready = [node_id for node_id, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        node_id = heapq.heappop(ready)
        order.append(node_id)
        for child in sorted(children[node_id]):
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(ready, child)
    if len(order) != len(nodes):
        remaining = sorted(node_id for node_id, degree in indegree.items() if degree > 0)
        return order, [f"graph_cycle:{'->'.join(remaining)}"]
    return order, []


def _policy_allows(
    node: dict[str, Any],
    *,
    direction: str,
    peer_instance: Any,
    channel: Any,
    frame_type: Any,
) -> bool:
    policy = node.get("communication_policy")
    if not isinstance(policy, dict):
        return False
    rules = policy.get(f"{direction}_rules")
    if not isinstance(rules, list):
        return False
    return any(
        isinstance(rule, dict)
        and rule.get("peer_instance") == peer_instance
        and channel in rule.get("channels", [])
        and frame_type in rule.get("frame_types", [])
        for rule in rules
    )


def validate_document(
    document: dict[str, Any], *, repo_root: Path, require_evidence_files: bool = True
) -> list[str]:
    """Return deterministic protocol, isolation and authority errors."""

    errors = _sensitive_errors(document)
    required_top = {
        "schema_version",
        "workflow_id",
        "graph_revision",
        "title",
        "authority",
        "capability_catalog",
        "frame_catalog",
        "nodes",
        "exchanges",
        "evidence",
    }
    missing = sorted(required_top - set(document))
    extra = sorted(set(document) - required_top)
    errors.extend(f"top_level_missing:{key}" for key in missing)
    errors.extend(f"top_level_unknown:{key}" for key in extra)

    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version_invalid:{document.get('schema_version')}")
    workflow_id = document.get("workflow_id")
    if not isinstance(workflow_id, str) or not ID_PATTERN.fullmatch(workflow_id):
        errors.append(f"workflow_id_invalid:{workflow_id}")
    graph_revision = document.get("graph_revision")
    if not isinstance(graph_revision, int) or isinstance(graph_revision, bool) or graph_revision < 1:
        errors.append(f"graph_revision_invalid:{graph_revision}")
    if not isinstance(document.get("title"), str) or not document.get("title", "").strip():
        errors.append("title_invalid")

    authority = document.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority_invalid")
        authority = {}
    authority_keys = {
        "advisory_only",
        "execution_enabled",
        "final_authority",
        "closed_boundaries",
    }
    if set(authority) != authority_keys:
        errors.append("authority_shape_invalid")
    if authority.get("advisory_only") is not True:
        errors.append("authority_must_be_advisory_only")
    if authority.get("execution_enabled") is not False:
        errors.append("execution_must_be_disabled")
    if authority.get("final_authority") != "human":
        errors.append("final_authority_must_be_human")
    closed, closed_errors = _string_ids(
        authority.get("closed_boundaries"), label="closed_boundaries"
    )
    errors.extend(closed_errors)
    missing_boundaries = sorted(REQUIRED_CLOSED_BOUNDARIES - set(closed))
    errors.extend(f"closed_boundary_missing:{item}" for item in missing_boundaries)

    capabilities, capability_errors = _ids(
        document.get("capability_catalog"), label="capability"
    )
    errors.extend(capability_errors)
    unknown_capabilities = sorted(set(capabilities) - ANALYTICAL_CAPABILITIES)
    missing_capabilities = sorted(ANALYTICAL_CAPABILITIES - set(capabilities))
    errors.extend(f"executable_or_unknown_capability:{item}" for item in unknown_capabilities)
    errors.extend(f"analytical_capability_missing:{item}" for item in missing_capabilities)
    for capability_id, capability in capabilities.items():
        if capability.get("effect") != "descriptive-only":
            errors.append(f"capability_effect_invalid:{capability_id}")
        if not isinstance(capability.get("description"), str) or not capability["description"].strip():
            errors.append(f"capability_description_invalid:{capability_id}")

    frames, frame_errors = _ids(document.get("frame_catalog"), label="frame")
    errors.extend(frame_errors)
    frame_properties: dict[str, set[str]] = {}
    frame_required: dict[str, set[str]] = {}
    for frame_id, frame in frames.items():
        properties = frame.get("properties")
        if not isinstance(properties, list) or not properties:
            errors.append(f"frame_properties_invalid:{frame_id}")
            frame_properties[frame_id] = set()
            frame_required[frame_id] = set()
            continue
        names: set[str] = set()
        required_names: set[str] = set()
        for position, prop in enumerate(properties):
            if not isinstance(prop, dict):
                errors.append(f"frame_property_invalid:{frame_id}:{position}")
                continue
            prop_name = prop.get("name")
            if not isinstance(prop_name, str) or not ID_PATTERN.fullmatch(prop_name):
                errors.append(f"frame_property_name_invalid:{frame_id}:{prop_name}")
                continue
            if prop_name in names:
                errors.append(f"frame_property_duplicate:{frame_id}:{prop_name}")
            names.add(prop_name)
            if prop.get("required") is True:
                required_names.add(prop_name)
            if prop.get("type") not in {"string", "number", "integer", "boolean", "string-list"}:
                errors.append(f"frame_property_type_invalid:{frame_id}:{prop_name}")
            if prop.get("sensitivity") not in {
                "public",
                "authored-synthetic",
                "operational-metadata",
            }:
                errors.append(f"frame_property_sensitivity_invalid:{frame_id}:{prop_name}")
        frame_properties[frame_id] = names
        frame_required[frame_id] = required_names

    nodes, node_errors = _ids(document.get("nodes"), label="node")
    errors.extend(node_errors)
    attempts: set[tuple[str, int]] = set()
    sandbox_instances: dict[str, list[dict[str, Any]]] = {}
    for node_id, node in nodes.items():
        role = node.get("role")
        if role not in ROLES:
            errors.append(f"node_role_invalid:{node_id}:{role}")
        instance = node.get("instance")
        attempt = node.get("attempt")
        if not isinstance(instance, str) or not ID_PATTERN.fullmatch(instance):
            errors.append(f"node_instance_invalid:{node_id}:{instance}")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            errors.append(f"node_attempt_invalid:{node_id}:{attempt}")
        elif isinstance(instance, str):
            coordinate = (instance, attempt)
            if coordinate in attempts:
                errors.append(f"node_attempt_duplicate:{instance}:{attempt}")
            attempts.add(coordinate)
        state = node.get("state")
        if state not in NODE_STATES:
            errors.append(f"node_state_invalid:{node_id}:{state}")
        if role == "human-authority-gate" and state != "awaiting-human-authority":
            errors.append(f"human_gate_state_invalid:{node_id}:{state}")
        for field in ("accepts", "emits", "capability_descriptor"):
            values, value_errors = _string_ids(node.get(field), label=f"node_{field}:{node_id}")
            errors.extend(value_errors)
            catalogue = set(frames) if field != "capability_descriptor" else set(capabilities)
            for value in sorted(set(values) - catalogue):
                errors.append(f"node_{field}_undeclared:{node_id}:{value}")

        container = node.get("container")
        policy = node.get("communication_policy")
        if role != "sandbox":
            if container is not None:
                errors.append(f"non_sandbox_container_forbidden:{node_id}")
            if policy is not None:
                errors.append(f"non_sandbox_policy_forbidden:{node_id}")
            continue

        if isinstance(instance, str):
            sandbox_instances.setdefault(instance, []).append(node)
        if not isinstance(container, dict):
            errors.append(f"sandbox_container_invalid:{node_id}")
            container = {}
        generation = container.get("generation")
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
            errors.append(f"container_generation_invalid:{node_id}:{generation}")
        restarted_from = container.get("restarted_from")
        if restarted_from is not None and (
            not isinstance(restarted_from, str) or not ID_PATTERN.fullmatch(restarted_from)
        ):
            errors.append(f"container_restart_reference_invalid:{node_id}:{restarted_from}")

        if not isinstance(policy, dict):
            errors.append(f"sandbox_policy_invalid:{node_id}")
            policy = {}
        if policy.get("mode") != "declared-peers-only":
            errors.append(f"sandbox_policy_mode_invalid:{node_id}")
        if policy.get("immutable_for_container_generation") is not True:
            errors.append(f"sandbox_policy_not_immutable:{node_id}")
        revision = policy.get("revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            errors.append(f"sandbox_policy_revision_invalid:{node_id}:{revision}")
        for direction in ("inbound", "outbound"):
            rules = policy.get(f"{direction}_rules")
            if not isinstance(rules, list):
                errors.append(f"sandbox_policy_rules_invalid:{node_id}:{direction}")
                continue
            signatures: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
            for position, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    errors.append(f"sandbox_policy_rule_invalid:{node_id}:{direction}:{position}")
                    continue
                peer = rule.get("peer_instance")
                if not isinstance(peer, str) or not ID_PATTERN.fullmatch(peer):
                    errors.append(f"sandbox_policy_peer_invalid:{node_id}:{direction}:{peer}")
                channels, channel_errors = _string_ids(
                    rule.get("channels"), label=f"sandbox_policy_channels:{node_id}:{direction}"
                )
                errors.extend(channel_errors)
                for value in sorted(set(channels) - set(CHANNEL_KINDS)):
                    errors.append(f"sandbox_policy_channel_unknown:{node_id}:{direction}:{value}")
                rule_frames, rule_frame_errors = _string_ids(
                    rule.get("frame_types"),
                    label=f"sandbox_policy_frames:{node_id}:{direction}",
                )
                errors.extend(rule_frame_errors)
                for value in sorted(set(rule_frames) - set(frames)):
                    errors.append(f"sandbox_policy_frame_unknown:{node_id}:{direction}:{value}")
                if isinstance(peer, str):
                    signature = (peer, tuple(sorted(channels)), tuple(sorted(rule_frames)))
                    if signature in signatures:
                        errors.append(f"sandbox_policy_rule_duplicate:{node_id}:{direction}:{peer}")
                    signatures.add(signature)

    for instance, instance_nodes in sandbox_instances.items():
        ordered = sorted(instance_nodes, key=lambda item: item.get("attempt", 0))
        previous: dict[str, Any] | None = None
        for node in ordered:
            node_id = node["id"]
            container = node.get("container", {})
            policy = node.get("communication_policy", {})
            if previous is None:
                if container.get("restarted_from") is not None:
                    errors.append(f"initial_container_restart_forbidden:{node_id}")
                previous = node
                continue
            previous_container = previous.get("container", {})
            previous_policy = previous.get("communication_policy", {})
            generation = container.get("generation")
            previous_generation = previous_container.get("generation")
            policy_changed = policy != previous_policy
            if isinstance(generation, int) and isinstance(previous_generation, int):
                if generation < previous_generation:
                    errors.append(f"container_generation_regressed:{instance}:{node_id}")
                elif generation == previous_generation:
                    if policy_changed:
                        errors.append(f"live_container_policy_amendment_forbidden:{instance}:{node_id}")
                    if container.get("restarted_from") is not None:
                        errors.append(f"same_generation_restart_reference_forbidden:{node_id}")
                else:
                    if container.get("restarted_from") != previous.get("id"):
                        errors.append(f"container_restart_lineage_invalid:{instance}:{node_id}")
                    current_revision = policy.get("revision")
                    previous_revision = previous_policy.get("revision")
                    if (
                        not isinstance(current_revision, int)
                        or not isinstance(previous_revision, int)
                        or current_revision <= previous_revision
                    ):
                        errors.append(f"container_restart_policy_revision_not_higher:{instance}:{node_id}")
            previous = node

    known_instances = {
        node.get("instance") for node in nodes.values() if isinstance(node.get("instance"), str)
    }
    for node_id, node in nodes.items():
        policy = node.get("communication_policy")
        if not isinstance(policy, dict):
            continue
        for direction in ("inbound", "outbound"):
            for rule in policy.get(f"{direction}_rules", []):
                if isinstance(rule, dict) and rule.get("peer_instance") not in known_instances:
                    errors.append(
                        f"sandbox_policy_peer_unknown:{node_id}:{direction}:"
                        f"{rule.get('peer_instance')}"
                    )

    exchanges_raw = document.get("exchanges")
    exchanges: list[dict[str, Any]] = []
    message_ids: set[str] = set()
    if not isinstance(exchanges_raw, list):
        errors.append("exchanges_must_be_array")
    else:
        for position, exchange in enumerate(exchanges_raw):
            if not isinstance(exchange, dict):
                errors.append(f"exchange_invalid:{position}")
                continue
            exchanges.append(exchange)
            message_id = exchange.get("message_id")
            if not isinstance(message_id, str) or not ID_PATTERN.fullmatch(message_id):
                errors.append(f"message_id_invalid:{position}:{message_id}")
            elif message_id in message_ids:
                errors.append(f"message_id_duplicate:{message_id}")
            else:
                message_ids.add(message_id)

    requests: dict[str, dict[str, Any]] = {}
    responses: dict[str, list[dict[str, Any]]] = {}
    outgoing: dict[str, int] = {node_id: 0 for node_id in nodes}
    incoming: dict[str, int] = {node_id: 0 for node_id in nodes}
    for exchange in exchanges:
        message_id = exchange.get("message_id")
        sender = exchange.get("sender")
        recipient = exchange.get("recipient")
        channel = exchange.get("channel")
        kind = exchange.get("kind")
        frame_type = exchange.get("frame_type")
        correlation_id = exchange.get("correlation_id")
        prefix = str(message_id)

        if exchange.get("workflow_id") != workflow_id:
            errors.append(f"exchange_workflow_mismatch:{prefix}")
        if exchange.get("graph_revision") != graph_revision:
            errors.append(f"exchange_revision_mismatch:{prefix}")
        if sender not in nodes:
            errors.append(f"exchange_sender_unknown:{prefix}:{sender}")
        if recipient not in nodes:
            errors.append(f"exchange_recipient_unknown:{prefix}:{recipient}")
        if sender == recipient and sender in nodes:
            errors.append(f"exchange_self_edge:{prefix}:{sender}")
        if sender in nodes and recipient in nodes:
            outgoing[sender] += 1
            incoming[recipient] += 1
            if nodes[sender].get("role") == "human-authority-gate":
                errors.append(f"human_gate_must_be_terminal:{sender}")
        if channel not in CHANNEL_KINDS:
            errors.append(f"exchange_channel_invalid:{prefix}:{channel}")
        elif kind not in CHANNEL_KINDS[channel]:
            errors.append(f"exchange_kind_channel_invalid:{prefix}:{channel}:{kind}")
        if not isinstance(correlation_id, str) or not ID_PATTERN.fullmatch(correlation_id):
            errors.append(f"exchange_correlation_invalid:{prefix}:{correlation_id}")
        if frame_type not in frames:
            errors.append(f"exchange_frame_unknown:{prefix}:{frame_type}")

        bindings = exchange.get("bindings")
        binding_names: set[str] = set()
        if not isinstance(bindings, list):
            errors.append(f"exchange_bindings_invalid:{prefix}")
            bindings = []
        for binding in bindings:
            if not isinstance(binding, dict):
                errors.append(f"exchange_binding_invalid:{prefix}")
                continue
            name = binding.get("name")
            if not isinstance(name, str) or not ID_PATTERN.fullmatch(name):
                errors.append(f"exchange_binding_name_invalid:{prefix}:{name}")
                continue
            if name in binding_names:
                errors.append(f"exchange_binding_duplicate:{prefix}:{name}")
            binding_names.add(name)
            if frame_type in frame_properties and name not in frame_properties[frame_type]:
                errors.append(f"exchange_property_undeclared:{prefix}:{frame_type}:{name}")
            value = binding.get("value")
            if isinstance(value, str) and value.casefold() in FORBIDDEN_EXECUTION_VALUES:
                errors.append(f"execution_value_forbidden:{prefix}:{name}:{value}")
        if kind not in {
            "context-request",
            "context-source-request",
            "context-denial",
            "evidence-receipt",
        } and frame_type in frame_required:
            for name in sorted(frame_required[frame_type] - binding_names):
                errors.append(f"exchange_required_binding_missing:{prefix}:{frame_type}:{name}")

        reason = exchange.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"exchange_reason_invalid:{prefix}")
        provenance = exchange.get("provenance")
        if not isinstance(provenance, dict):
            errors.append(f"exchange_provenance_invalid:{prefix}")
            provenance = {}
        if provenance.get("kind") not in {"authored-synthetic", "derived", "human-supplied"}:
            errors.append(f"exchange_provenance_kind_invalid:{prefix}")
        if not isinstance(provenance.get("source"), str) or not provenance.get("source", "").strip():
            errors.append(f"exchange_provenance_source_invalid:{prefix}")
        source_messages = provenance.get("source_message_ids")
        if not isinstance(source_messages, list) or any(
            not isinstance(source, str) or not ID_PATTERN.fullmatch(source)
            for source in source_messages
        ):
            errors.append(f"exchange_provenance_messages_invalid:{prefix}")
        else:
            for source_message in source_messages:
                if source_message not in message_ids:
                    errors.append(f"exchange_provenance_message_unknown:{prefix}:{source_message}")
                if source_message == message_id:
                    errors.append(f"exchange_provenance_self_reference:{prefix}")
        freshness = exchange.get("freshness")
        if not isinstance(freshness, dict):
            errors.append(f"exchange_freshness_invalid:{prefix}")
            freshness = {}
        if freshness.get("status") not in {"fresh", "not-applicable"}:
            errors.append(f"exchange_freshness_status_invalid:{prefix}")
        if not isinstance(freshness.get("observed_at"), str) or not freshness.get("observed_at"):
            errors.append(f"exchange_freshness_observed_invalid:{prefix}")
        maximum_age = freshness.get("maximum_age_seconds")
        if not isinstance(maximum_age, int) or isinstance(maximum_age, bool) or maximum_age < 0:
            errors.append(f"exchange_freshness_age_invalid:{prefix}")

        if sender in nodes and recipient in nodes and frame_type in frames:
            sender_node = nodes[sender]
            recipient_node = nodes[recipient]
            if sender_node.get("role") == "sandbox" and not _policy_allows(
                sender_node,
                direction="outbound",
                peer_instance=recipient_node.get("instance"),
                channel=channel,
                frame_type=frame_type,
            ):
                errors.append(f"sandbox_outbound_policy_denied:{prefix}:{sender}:{recipient}")
            if recipient_node.get("role") == "sandbox" and not _policy_allows(
                recipient_node,
                direction="inbound",
                peer_instance=sender_node.get("instance"),
                channel=channel,
                frame_type=frame_type,
            ):
                errors.append(f"sandbox_inbound_policy_denied:{prefix}:{sender}:{recipient}")
            if (
                sender_node.get("role") == "sandbox"
                and recipient_node.get("role") == "sandbox"
                and (channel != "data" or kind not in {"result", "join-input"})
            ):
                errors.append(f"sandbox_peer_control_forbidden:{prefix}:{channel}:{kind}")
            if kind == "context-request":
                if sender_node.get("role") != "sandbox" or recipient_node.get("role") != "orchestrator":
                    errors.append(f"context_request_route_invalid:{prefix}")
                if frame_type not in sender_node.get("accepts", []):
                    errors.append(f"context_request_frame_not_accepted:{prefix}:{frame_type}")
                if bindings:
                    errors.append(f"context_request_must_not_carry_values:{prefix}")
                if isinstance(correlation_id, str):
                    if correlation_id in requests:
                        errors.append(f"context_request_correlation_duplicate:{correlation_id}")
                    requests[correlation_id] = exchange
            elif kind == "context-source-request":
                if (
                    sender_node.get("role") != "orchestrator"
                    or recipient_node.get("role") != "human-context-source"
                ):
                    errors.append(f"context_source_request_route_invalid:{prefix}")
                if bindings:
                    errors.append(f"context_source_request_must_not_carry_values:{prefix}")
                if frame_type not in sender_node.get("emits", []):
                    errors.append(f"exchange_frame_not_emitted:{prefix}:{sender}:{frame_type}")
                if frame_type not in recipient_node.get("accepts", []):
                    errors.append(f"exchange_frame_not_accepted:{prefix}:{recipient}:{frame_type}")
            elif kind in {"context-grant", "context-denial"}:
                if sender_node.get("role") != "orchestrator" or recipient_node.get("role") != "sandbox":
                    errors.append(f"context_response_route_invalid:{prefix}")
                if frame_type not in recipient_node.get("accepts", []):
                    errors.append(f"context_response_frame_not_accepted:{prefix}:{frame_type}")
                if isinstance(correlation_id, str):
                    responses.setdefault(correlation_id, []).append(exchange)
                if kind == "context-grant" and freshness.get("status") != "fresh":
                    errors.append(f"context_grant_not_fresh:{prefix}")
            else:
                if frame_type not in sender_node.get("emits", []):
                    errors.append(f"exchange_frame_not_emitted:{prefix}:{sender}:{frame_type}")
                if frame_type not in recipient_node.get("accepts", []):
                    errors.append(f"exchange_frame_not_accepted:{prefix}:{recipient}:{frame_type}")

            if channel == "evidence" and recipient_node.get("role") != "evidence-sink":
                errors.append(f"evidence_recipient_invalid:{prefix}:{recipient}")
            if kind == "candidate-transition" and recipient_node.get("role") != "human-authority-gate":
                errors.append(f"candidate_transition_requires_human_gate:{prefix}:{recipient}")

    for correlation_id, request in requests.items():
        matches = responses.get(correlation_id, [])
        if len(matches) != 1:
            errors.append(f"context_request_response_count:{correlation_id}:{len(matches)}")
            continue
        response = matches[0]
        if response.get("frame_type") != request.get("frame_type"):
            errors.append(f"context_response_frame_mismatch:{correlation_id}")
        request_node = nodes.get(request.get("sender"), {})
        response_node = nodes.get(response.get("recipient"), {})
        if request_node.get("instance") != response_node.get("instance"):
            errors.append(f"context_response_instance_mismatch:{correlation_id}")
        request_attempt = request_node.get("attempt")
        response_attempt = response_node.get("attempt")
        if not isinstance(request_attempt, int) or not isinstance(response_attempt, int) or response_attempt <= request_attempt:
            errors.append(f"context_response_attempt_not_later:{correlation_id}")
    for correlation_id in sorted(set(responses) - set(requests)):
        errors.append(f"context_response_without_request:{correlation_id}")

    order, graph_errors = _topological_order(nodes, exchanges)
    errors.extend(graph_errors)
    if nodes and order:
        connected = {
            node_id
            for node_id in nodes
            if incoming.get(node_id, 0) > 0 or outgoing.get(node_id, 0) > 0
        }
        for node_id in sorted(set(nodes) - connected):
            errors.append(f"node_disconnected:{node_id}")

    gates = [node_id for node_id, node in nodes.items() if node.get("role") == "human-authority-gate"]
    if len(gates) != 1:
        errors.append(f"human_authority_gate_count:{len(gates)}")
    for gate in gates:
        if outgoing.get(gate, 0) != 0:
            errors.append(f"human_gate_must_be_terminal:{gate}")
        if incoming.get(gate, 0) == 0:
            errors.append(f"human_gate_input_missing:{gate}")

    evidence = document.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence_invalid")
    else:
        for reference in evidence:
            if not _safe_repo_reference(reference):
                errors.append(f"unsafe_repo_reference:evidence:{reference}")
            elif require_evidence_files and not (repo_root / reference).is_file():
                errors.append(f"evidence_not_found:{reference}")

    return sorted(set(errors))


def build_trace(document: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    errors = validate_document(document, repo_root=repo_root)
    if errors:
        return {
            "schema_version": TRACE_VERSION,
            "status": "revision_required",
            "reasons": errors,
            "workflow_id": document.get("workflow_id"),
            "graph_revision": document.get("graph_revision"),
        }
    nodes = {node["id"]: node for node in document["nodes"]}
    order, _ = _topological_order(nodes, document["exchanges"])
    context_round_trips = []
    requests = {
        item["correlation_id"]: item
        for item in document["exchanges"]
        if item["kind"] == "context-request"
    }
    for response in document["exchanges"]:
        if response["kind"] not in {"context-grant", "context-denial"}:
            continue
        request = requests[response["correlation_id"]]
        context_round_trips.append(
            {
                "correlation_id": response["correlation_id"],
                "requested_by": request["sender"],
                "brokered_by": response["sender"],
                "continued_as": response["recipient"],
                "frame_type": response["frame_type"],
                "disposition": response["kind"],
            }
        )
    fan_out = []
    for node_id in order:
        targets = sorted(
            {
                item["recipient"]
                for item in document["exchanges"]
                if item["sender"] == node_id
            }
        )
        if len(targets) > 1:
            fan_out.append({"node_id": node_id, "targets": targets})
    joins = [
        {
            "node_id": node_id,
            "sources": sorted(
                {
                    item["sender"]
                    for item in document["exchanges"]
                    if item["recipient"] == node_id
                }
            ),
        }
        for node_id in order
        if nodes[node_id]["role"] == "join"
    ]
    peer_exchanges = [
        {
            "message_id": item["message_id"],
            "sender": item["sender"],
            "recipient": item["recipient"],
            "frame_type": item["frame_type"],
        }
        for item in document["exchanges"]
        if nodes[item["sender"]]["role"] == "sandbox"
        and nodes[item["recipient"]]["role"] == "sandbox"
    ]
    gate = next(
        node for node in document["nodes"] if node["role"] == "human-authority-gate"
    )
    return {
        "schema_version": TRACE_VERSION,
        "status": "passed",
        "reasons": [],
        "workflow_id": document["workflow_id"],
        "graph_revision": document["graph_revision"],
        "authority": {
            "advisory_only": True,
            "execution_enabled": False,
            "terminal_gate": gate["id"],
            "terminal_state": gate["state"],
        },
        "topological_order": order,
        "context_round_trips": sorted(
            context_round_trips, key=lambda item: item["correlation_id"]
        ),
        "fan_out": fan_out,
        "joins": joins,
        "declared_peer_exchanges": peer_exchanges,
        "exchange_count": len(document["exchanges"]),
        "evidence": sorted(document["evidence"]),
    }


def render_markdown(trace: dict[str, Any]) -> str:
    if trace.get("status") != "passed":
        reasons = "\n".join(f"- `{reason}`" for reason in trace.get("reasons", []))
        return f"# Ariadne sandbox DAG\n\nStatus: **revision required**\n\n{reasons}\n"
    lines = [
        "# Ariadne sandbox DAG trace",
        "",
        "This is a non-executing, authored-synthetic protocol trace. It shows how typed context can move through isolated leaves while all messages remain forward edges in a DAG.",
        "",
        f"- Workflow: `{trace['workflow_id']}`",
        f"- Graph revision: `{trace['graph_revision']}`",
        f"- Exchanges: `{trace['exchange_count']}`",
        f"- Final state: **{trace['authority']['terminal_state']}**",
        "- Execution enabled: **no**",
        "",
        "## Immutable order",
        "",
    ]
    lines.extend(f"{index}. `{node_id}`" for index, node_id in enumerate(trace["topological_order"], 1))
    lines.extend(["", "## Context round trips", ""])
    for item in trace["context_round_trips"]:
        lines.append(
            f"- `{item['requested_by']}` requested `{item['frame_type']}`; "
            f"`{item['brokered_by']}` returned `{item['disposition']}` to the later "
            f"attempt `{item['continued_as']}`."
        )
    lines.extend(["", "## Fan-out and joins", ""])
    for item in trace["fan_out"]:
        lines.append(f"- `{item['node_id']}` fans out to {', '.join(f'`{target}`' for target in item['targets'])}.")
    for item in trace["joins"]:
        lines.append(f"- `{item['node_id']}` joins {', '.join(f'`{source}`' for source in item['sources'])}.")
    lines.extend(["", "## Declared peer links", ""])
    for item in trace["declared_peer_exchanges"]:
        lines.append(
            f"- `{item['sender']}` sends `{item['frame_type']}` directly to "
            f"`{item['recipient']}` under bilateral container policy."
        )
    lines.extend(
        [
            "",
            "## Authority",
            "",
            f"The trace terminates at `{trace['authority']['terminal_gate']}`. It can present a candidate for human review, but it cannot confirm, write, dispatch or execute it.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect the non-executing Ariadne sandbox-DAG protocol."
    )
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--document", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate protocol, DAG, context and authority semantics.")
    trace = subparsers.add_parser("trace", help="Render the deterministic non-executing trace.")
    trace.add_argument("--format", choices=["json", "markdown"], default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo_root = continuity.resolve_repo_root(args.repo_root)
        document_path = continuity.resolve_repo_path(
            args.document if args.document else default_document_path(repo_root),
            repo_root,
            label="sandbox_dag_document",
        )
        document = load_document(document_path)
        trace = build_trace(document, repo_root=repo_root)
        if args.command == "validate":
            sys.stdout.write(canonical_json(trace))
        elif args.format == "json":
            sys.stdout.write(canonical_json(trace))
        else:
            sys.stdout.write(render_markdown(trace))
        return 0 if trace["status"] == "passed" else 2
    except (SandboxDagError, continuity.ContinuityError, OSError) as error:
        sys.stdout.write(
            canonical_json(
                {
                    "schema_version": TRACE_VERSION,
                    "status": "revision_required",
                    "reasons": [str(error)],
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
