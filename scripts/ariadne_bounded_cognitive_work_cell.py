"""Validate the non-executing Ariadne bounded cognitive work-cell proof.

The checked-in document and every result are authored-synthetic protocol
evidence. This module performs pure deterministic transforms only. It does not
connect to a database, event feed, product API, model, provider, container,
mailbox, worker, human-gate runtime or command surface.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = "ariadne.bounded_cognitive_work_cell.v1"
VERIFICATION_VERSION = "ariadne.bounded_cognitive_work_cell_verification.v1"
MANIFEST_VERSION = "ariadne.bounded_cognitive_work_cell_manifests.v1"
EVIDENCE_VERSION = "ariadne.bounded_cognitive_work_cell_evidence.v1"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AUTHORITY_ORDER = ("evidence", "advisory", "candidate", "verified-fact", "command")
PASS_VERDICTS = {
    "pass_to_downstream",
    "pass_to_human_gate",
    "pass_with_canonical_repair",
    "pass_with_repair_to_human_gate",
}
RETRYABLE_VERDICTS = {
    "retryable_schema_reject",
    "retryable_grounding_reject",
}
REQUIRED_VERDICTS = PASS_VERDICTS | RETRYABLE_VERDICTS | {
    "stale_context_reject",
    "authority_reject",
}
REQUIRED_CLOSED_BOUNDARIES = {
    "api-change",
    "appointment-write",
    "autonomous-action",
    "container-runtime",
    "database-connectivity",
    "deployment",
    "event-feed-connectivity",
    "historical-diary",
    "human-gate-runtime",
    "live-mailbox",
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
    "medicare_number",
    "model_output",
    "model_reasoning",
    "patient_name",
    "phone_number",
    "prompt",
    "provider_output",
    "raw_transcript",
    "secret",
    "topic",
    "transcript",
}
FORBIDDEN_VALUE_MARKERS = {
    "amqp://",
    "http://",
    "https://",
    "kafka://",
    "margaret thompson",
    "medicare number",
    "postgresql://",
}
REQUIRED_CHECK_ORDER = [
    "port-and-frame-schema",
    "practice-principal-correlation",
    "declared-source-and-sensitivity",
    "freshness-and-context-revision",
    "authority-ceiling",
    "referential-grounding",
    "candidate-selection-consistency",
    "atomic-output-consistency",
]
REPAIR_ALLOWLIST = [
    "deduplicate-opaque-references",
    "stable-sort-opaque-references",
]


class CognitiveWorkCellError(ValueError):
    """Raised when a fail-closed protocol transform cannot continue."""


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def canonical_sha256(payload: Any) -> str:
    encoded = canonical_json(payload).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def default_document_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "orchestration"
        / "continuity"
        / "ariadne-bounded-cognitive-work-cell-example.json"
    )


def load_document(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise CognitiveWorkCellError(f"document_not_found:{path}") from error
    except json.JSONDecodeError as error:
        raise CognitiveWorkCellError(f"document_invalid_json:{error.msg}") from error
    if not isinstance(payload, dict):
        raise CognitiveWorkCellError("document_must_be_object")
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
    result: set[str] = set()
    errors: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            errors.append(f"{label}_value_invalid:{item}")
        elif item in result:
            errors.append(f"{label}_duplicate:{item}")
        else:
            result.add(item)
    return result, errors


def _authority_rank(value: Any) -> int:
    try:
        return AUTHORITY_ORDER.index(value)
    except ValueError:
        return -1


def _context_sets(input_frames: dict[str, dict[str, Any]]) -> dict[str, set[Any]]:
    patient_ids: set[str] = set()
    practitioner_ids: set[str] = set()
    slot_ids: set[str] = set()
    durations: set[int] = set()
    all_grounding_ids: set[str] = set()
    for frame in input_frames.values():
        payload = frame.get("payload", {})
        if not isinstance(payload, dict):
            continue
        for key, destination in (
            ("candidate_ids", patient_ids),
            ("practitioner_ids", practitioner_ids),
            ("slot_ids", slot_ids),
        ):
            values = payload.get(key, [])
            if isinstance(values, list):
                destination.update(value for value in values if isinstance(value, str))
        selected = payload.get("selected_practitioner_id")
        if isinstance(selected, str):
            practitioner_ids.add(selected)
        allowed_durations = payload.get("allowed_duration_minutes", [])
        if isinstance(allowed_durations, list):
            durations.update(value for value in allowed_durations if isinstance(value, int))
        duration = payload.get("duration_minutes")
        if isinstance(duration, int):
            durations.add(duration)
    all_grounding_ids.update(patient_ids | practitioner_ids | slot_ids)
    return {
        "patient_ids": patient_ids,
        "practitioner_ids": practitioner_ids,
        "slot_ids": slot_ids,
        "durations": durations,
        "all_grounding_ids": all_grounding_ids,
    }


def _canonical_repair(
    draft: dict[str, Any], repair_allowlist: list[str]
) -> tuple[dict[str, Any], list[str]]:
    repaired = copy.deepcopy(draft)
    payload = repaired.get("payload")
    if not isinstance(payload, dict):
        return repaired, []
    values = payload.get("candidate_slot_ids")
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        return repaired, []
    rules: list[str] = []
    unique = list(dict.fromkeys(values))
    if unique != values and "deduplicate-opaque-references" in repair_allowlist:
        values = unique
        rules.append("deduplicate-opaque-references")
    ordered = sorted(values)
    if ordered != values and "stable-sort-opaque-references" in repair_allowlist:
        values = ordered
        rules.append("stable-sort-opaque-references")
    payload["candidate_slot_ids"] = values
    return repaired, rules


def _failure_disposition(
    verdict: str, *, prior_same_failure_count: int, max_same_reason_attempts: int
) -> str:
    if verdict in RETRYABLE_VERDICTS:
        if prior_same_failure_count + 1 >= max_same_reason_attempts:
            return "abort-edge"
        return "request-new-attempt"
    if verdict == "stale_context_reject":
        return "fresh-read-and-supersede"
    if verdict == "authority_reject":
        return "abort-edge"
    if verdict in {
        "pass_to_human_gate",
        "pass_with_repair_to_human_gate",
    }:
        return "release-to-human-gate"
    if verdict in PASS_VERDICTS:
        return "release-to-declared-recipient"
    return "abort-edge"


def _release_edge(
    *,
    case_id: str,
    draft: dict[str, Any],
    port: dict[str, Any],
    verdict: str,
    released_frame: dict[str, Any],
    proofreader_node_id: str,
) -> dict[str, Any]:
    return {
        "id": f"release-{case_id}-{draft['id']}",
        "sender_node_id": proofreader_node_id,
        "original_sender_attempt_id": draft["attempt_id"],
        "recipient_node_id": port["recipient_node_id"],
        "channel": port["channel"],
        "kind": "verified-human-gate-frame"
        if port["human_gate_required"]
        else "verified-frame",
        "frame_type": draft["frame_type"],
        "source_draft_id": draft["id"],
        "verdict": verdict,
        "authority_class": draft["authority_class"],
        "payload_sha256": canonical_sha256(released_frame.get("payload", {})),
        "command_authority": False,
    }


def _verify_single(
    *,
    case_id: str,
    draft: dict[str, Any],
    port: dict[str, Any] | None,
    input_frames: dict[str, dict[str, Any]],
    policy: dict[str, Any],
    prior_same_failure_count: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    draft_id = draft.get("id", "unknown")
    max_attempts = policy.get("retry_policy", {}).get("max_same_reason_attempts", 0)
    if not isinstance(max_attempts, int) or max_attempts < 1:
        max_attempts = 1
    reasons: list[str] = []
    verdict: str
    released_frame = copy.deepcopy(draft)
    repair_receipt: dict[str, Any] | None = None

    if port is None:
        verdict = "retryable_schema_reject"
        reasons = [f"output-port-unknown:{draft.get('output_port_id')}"]
    elif draft.get("frame_type") != port.get("frame_type"):
        verdict = "retryable_schema_reject"
        reasons = [
            f"frame-type-mismatch:{draft.get('frame_type')}:{port.get('frame_type')}"
        ]
    elif not isinstance(draft.get("payload"), dict):
        verdict = "retryable_schema_reject"
        reasons = ["payload-must-be-object"]
    else:
        payload = draft["payload"]
        required = set(port.get("required_payload_fields", []))
        allowed = set(port.get("allowed_payload_fields", []))
        missing = sorted(required - set(payload))
        unknown = sorted(set(payload) - allowed)
        if missing:
            verdict = "retryable_schema_reject"
            reasons = [f"payload-required-missing:{name}" for name in missing]
        elif unknown:
            verdict = "retryable_schema_reject"
            reasons = [f"payload-field-undeclared:{name}" for name in unknown]
        else:
            baseline = next(iter(input_frames.values()), {})
            boundary_fields = ("practice_id", "principal_id", "correlation_id")
            mismatches = [
                field
                for field in boundary_fields
                if draft.get(field) != baseline.get(field)
            ]
            missing_sources = sorted(
                source_id
                for source_id in draft.get("source_frame_ids", [])
                if source_id not in input_frames
            )
            current_revision = policy.get("current_context_revision")
            draft_revision = draft.get("context_revision")
            payload_revision = payload.get("context_revision")
            if mismatches:
                verdict = "authority_reject"
                reasons = [f"scope-boundary-mismatch:{field}" for field in mismatches]
            elif missing_sources:
                verdict = "retryable_grounding_reject"
                reasons = [f"source-frame-unknown:{item}" for item in missing_sources]
            elif draft_revision != current_revision:
                verdict = "stale_context_reject"
                reasons = [
                    f"context-revision-stale:{draft_revision}:{current_revision}"
                ]
            elif payload_revision != draft_revision:
                verdict = "retryable_grounding_reject"
                reasons = [
                    f"payload-context-revision-mismatch:{payload_revision}:{draft_revision}"
                ]
            elif _authority_rank(draft.get("authority_class")) > _authority_rank(
                port.get("authority_ceiling")
            ):
                verdict = "authority_reject"
                reasons = [
                    "authority-ceiling-exceeded:"
                    f"{draft.get('authority_class')}:{port.get('authority_ceiling')}"
                ]
            else:
                released_frame, repair_rules = _canonical_repair(
                    draft, policy.get("repair_allowlist", [])
                )
                grounded = _context_sets(input_frames)
                repaired_payload = released_frame["payload"]
                grounding_errors: list[str] = []
                patient_id = repaired_payload.get("patient_candidate_id")
                if patient_id is not None and patient_id not in grounded["patient_ids"]:
                    grounding_errors.append(f"patient-not-grounded:{patient_id}")
                practitioner_id = repaired_payload.get("practitioner_id")
                if (
                    practitioner_id is not None
                    and practitioner_id not in grounded["practitioner_ids"]
                ):
                    grounding_errors.append(
                        f"practitioner-not-grounded:{practitioner_id}"
                    )
                candidate_slot_ids = repaired_payload.get("candidate_slot_ids", [])
                if isinstance(candidate_slot_ids, list):
                    for slot_id in candidate_slot_ids:
                        if slot_id not in grounded["slot_ids"]:
                            grounding_errors.append(f"slot-not-grounded:{slot_id}")
                selected_slot_id = repaired_payload.get("selected_slot_id")
                if (
                    selected_slot_id is not None
                    and selected_slot_id not in grounded["slot_ids"]
                ):
                    grounding_errors.append(f"slot-not-grounded:{selected_slot_id}")
                if (
                    selected_slot_id is not None
                    and isinstance(candidate_slot_ids, list)
                    and selected_slot_id not in candidate_slot_ids
                ):
                    grounding_errors.append(
                        f"selected-slot-not-in-candidates:{selected_slot_id}"
                    )
                duration = repaired_payload.get("duration_minutes")
                if duration is not None and duration not in grounded["durations"]:
                    grounding_errors.append(f"duration-not-grounded:{duration}")
                grounding_ids = repaired_payload.get("grounding_ids", [])
                if isinstance(grounding_ids, list):
                    for grounding_id in grounding_ids:
                        if grounding_id not in grounded["all_grounding_ids"]:
                            grounding_errors.append(
                                f"advisory-grounding-unknown:{grounding_id}"
                            )
                if grounding_errors:
                    verdict = "retryable_grounding_reject"
                    reasons = sorted(set(grounding_errors))
                    repair_rules = []
                    released_frame = copy.deepcopy(draft)
                else:
                    if repair_rules:
                        verdict = (
                            "pass_with_repair_to_human_gate"
                            if port.get("human_gate_required")
                            else "pass_with_canonical_repair"
                        )
                        reasons = ["canonical-repair-applied"]
                        repair_receipt = {
                            "id": f"repair-{case_id}-{draft_id}",
                            "source_draft_id": draft_id,
                            "repaired_frame_id": f"repaired-{draft_id}",
                            "original_sha256": canonical_sha256(draft),
                            "repaired_sha256": canonical_sha256(released_frame),
                            "repair_rules": repair_rules,
                            "original_immutable": True,
                        }
                    elif port.get("human_gate_required"):
                        verdict = "pass_to_human_gate"
                        reasons = (
                            ["advisory-human-review-required"]
                            if draft.get("authority_class") == "advisory"
                            else ["verified"]
                        )
                    else:
                        verdict = "pass_to_downstream"
                        reasons = ["verified"]

    disposition = _failure_disposition(
        verdict,
        prior_same_failure_count=prior_same_failure_count,
        max_same_reason_attempts=max_attempts,
    )
    result = {
        "draft_id": draft_id,
        "verdict": verdict,
        "disposition": disposition,
        "reason_codes": reasons,
        "repair_receipt": repair_receipt,
        "released_edge": None,
    }
    if verdict in PASS_VERDICTS and port is not None:
        result["released_edge"] = _release_edge(
            case_id=case_id,
            draft=draft,
            port=port,
            verdict=verdict,
            released_frame=released_frame,
            proofreader_node_id=policy.get("proofreader_node_id", "proofreader-v1"),
        )
    return result, released_frame


def _compute_verification(document: dict[str, Any]) -> dict[str, Any]:
    ports, _ = _index(document.get("output_ports", []), label="output_port")
    drafts, _ = _index(document.get("draft_frames", []), label="draft_frame")
    input_frames, _ = _index(document.get("input_frames", []), label="input_frame")
    groups, _ = _index(
        document.get("atomic_output_groups", []), label="atomic_output_group"
    )
    policy = document.get("verification_policy", {})
    max_attempts = policy.get("retry_policy", {}).get("max_same_reason_attempts", 1)
    case_results: list[dict[str, Any]] = []
    all_releases: list[dict[str, Any]] = []
    all_repairs: list[dict[str, Any]] = []

    for case in document.get("verification_cases", []):
        case_id = case.get("id", "unknown")
        prior_count = case.get("prior_same_failure_count", 0)
        frame_results: list[dict[str, Any]] = []
        released_frames: dict[str, dict[str, Any]] = {}
        for draft_id in case.get("draft_ids", []):
            draft = drafts.get(draft_id, {"id": draft_id})
            port = ports.get(draft.get("output_port_id"))
            result, released_frame = _verify_single(
                case_id=case_id,
                draft=draft,
                port=port,
                input_frames=input_frames,
                policy=policy,
                prior_same_failure_count=prior_count,
            )
            frame_results.append(result)
            released_frames[draft_id] = released_frame

        # Atomic consistency is checked only when two or more members of the
        # same declared group occur in this authored-synthetic case.
        for group in groups.values():
            member_ports = set(group.get("member_port_ids", []))
            members = [
                result
                for result in frame_results
                if drafts.get(result["draft_id"], {}).get("output_port_id")
                in member_ports
            ]
            if len(members) < 2:
                continue
            if not all(result["verdict"] in PASS_VERDICTS for result in members):
                reason = f"atomic-group-member-rejected:{group['id']}"
                disposition = _failure_disposition(
                    "retryable_grounding_reject",
                    prior_same_failure_count=prior_count,
                    max_same_reason_attempts=max_attempts,
                )
                for result in members:
                    result["released_edge"] = None
                    if result["verdict"] in PASS_VERDICTS:
                        result.update(
                            {
                                "verdict": "retryable_grounding_reject",
                                "disposition": disposition,
                                "reason_codes": [reason],
                                "repair_receipt": None,
                            }
                        )
                continue
            for field in group.get("consistency_fields", []):
                values = {
                    canonical_json(
                        released_frames[result["draft_id"]]
                        .get("payload", {})
                        .get(field)
                    )
                    for result in members
                }
                if len(values) <= 1:
                    continue
                reason = f"atomic-group-field-mismatch:{group['id']}:{field}"
                disposition = _failure_disposition(
                    "retryable_grounding_reject",
                    prior_same_failure_count=prior_count,
                    max_same_reason_attempts=max_attempts,
                )
                for result in members:
                    result.update(
                        {
                            "verdict": "retryable_grounding_reject",
                            "disposition": disposition,
                            "reason_codes": [reason],
                            "repair_receipt": None,
                            "released_edge": None,
                        }
                    )
                break

        passing = all(result["verdict"] in PASS_VERDICTS for result in frame_results)
        if passing:
            status = "passed"
            disposition = "release-verified-outputs"
        else:
            status = "rejected"
            dispositions = {result["disposition"] for result in frame_results}
            if "abort-edge" in dispositions:
                disposition = "abort-edge"
            elif "fresh-read-and-supersede" in dispositions:
                disposition = "fresh-read-and-supersede"
            else:
                disposition = "request-new-attempt"
        reason_codes = sorted(
            {
                reason
                for result in frame_results
                for reason in result.get("reason_codes", [])
            }
        )
        repair_rules = [
            rule
            for rule in REPAIR_ALLOWLIST
            if any(
                result.get("repair_receipt")
                and rule in result["repair_receipt"]["repair_rules"]
                for result in frame_results
            )
        ]
        releases = [
            result["released_edge"]
            for result in frame_results
            if result.get("released_edge") is not None
        ]
        repairs = [
            result["repair_receipt"]
            for result in frame_results
            if result.get("repair_receipt") is not None
        ]
        all_releases.extend(releases)
        all_repairs.extend(repairs)
        case_results.append(
            {
                "case_id": case_id,
                "status": status,
                "disposition": disposition,
                "frame_results": frame_results,
                "reason_codes": reason_codes,
                "repair_rules": repair_rules,
                "released_edges": releases,
                "repair_receipts": repairs,
            }
        )

    return {
        "schema_version": VERIFICATION_VERSION,
        "protocol_id": document.get("protocol_id"),
        "workflow_id": document.get("workflow_id"),
        "operational_graph_revision": document.get("operational_graph_revision"),
        "execution_enabled": False,
        "case_results": case_results,
        "released_edges": all_releases,
        "repair_receipts": all_repairs,
    }


def _expected_projection(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "disposition": result["disposition"],
        "frame_verdicts": [
            {"draft_id": item["draft_id"], "verdict": item["verdict"]}
            for item in result["frame_results"]
        ],
        "reason_codes": result["reason_codes"],
        "repair_rules": result["repair_rules"],
    }


def validate_document(document: dict[str, Any], *, repo_root: Path) -> list[str]:
    """Return deterministic structure, grounding, authority and lineage errors."""

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
        "node_granularity_policy",
        "execution_classes",
        "nodes",
        "input_frames",
        "output_ports",
        "work_cell_attempts",
        "draft_frames",
        "verification_policy",
        "verification_cases",
        "fresh_read_grants",
        "retry_traces",
        "human_gate_policy",
        "atomic_output_groups",
        "evidence",
    }
    errors.extend(f"top_level_missing:{key}" for key in sorted(required_top - set(document)))
    errors.extend(f"top_level_unknown:{key}" for key in sorted(set(document) - required_top))
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version_invalid:{document.get('schema_version')}")
    for field in ("protocol_id", "workflow_id"):
        value = document.get(field)
        if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
            errors.append(f"{field}_invalid:{value}")
    for field in ("operational_graph_revision", "revision"):
        if not isinstance(document.get(field), int) or document.get(field, 0) < 1:
            errors.append(f"{field}_invalid:{document.get(field)}")
    _, time_errors = _timestamp(document.get("as_of"), label="as-of")
    errors.extend(time_errors)

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

    granularity = document.get("node_granularity_policy", {})
    if granularity.get("principle") != "coarse-cognition-fine-authority":
        errors.append("node_granularity_principle_invalid")
    for field in (
        "topology_is_not_isolation",
        "agent_eligibility_does_not_start_container",
        "future_agentisation_requires_new_generation",
    ):
        if granularity.get(field) is not True:
            errors.append(f"node_granularity_invariant_missing:{field}")

    classes, class_errors = _index(
        document.get("execution_classes"), label="execution_class"
    )
    nodes, node_errors = _index(document.get("nodes"), label="node")
    inputs, input_errors = _index(document.get("input_frames"), label="input_frame")
    ports, port_errors = _index(document.get("output_ports"), label="output_port")
    attempts, attempt_errors = _index(
        document.get("work_cell_attempts"), label="work_cell_attempt"
    )
    drafts, draft_errors = _index(document.get("draft_frames"), label="draft_frame")
    cases, case_errors = _index(
        document.get("verification_cases"), label="verification_case"
    )
    grants, grant_errors = _index(
        document.get("fresh_read_grants"), label="fresh_read_grant"
    )
    traces, trace_errors = _index(document.get("retry_traces"), label="retry_trace")
    groups, group_errors = _index(
        document.get("atomic_output_groups"), label="atomic_output_group"
    )
    errors.extend(
        class_errors
        + node_errors
        + input_errors
        + port_errors
        + attempt_errors
        + draft_errors
        + case_errors
        + grant_errors
        + trace_errors
        + group_errors
    )

    agent_nodes = []
    uncontainerised_leaves = []
    for node_id, node in nodes.items():
        declared_class = classes.get(node.get("execution_class"))
        if declared_class is None:
            errors.append(f"node_execution_class_unknown:{node_id}")
            continue
        if node.get("agent_eligible") != declared_class.get("agent_eligible"):
            errors.append(f"node_agent_eligibility_mismatch:{node_id}")
        if node.get("agent_attached") is not False:
            errors.append(f"node_agent_must_be_absent:{node_id}")
        container_policy = node.get("container_policy")
        if declared_class.get("agent_eligible"):
            agent_nodes.append(node)
            if not isinstance(container_policy, dict):
                errors.append(f"agent_node_container_policy_missing:{node_id}")
            else:
                if container_policy.get("dry_run") is not True:
                    errors.append(f"container_policy_dry_run_required:{node_id}")
                if container_policy.get("container_started") is not False:
                    errors.append(f"container_started_forbidden:{node_id}")
        elif container_policy is not None:
            errors.append(f"deterministic_node_precontainerised:{node_id}")
        if node.get("topological_role") == "leaf" and container_policy is None:
            uncontainerised_leaves.append(node_id)
    if not any(node.get("topological_role") == "interior" for node in agent_nodes):
        errors.append("interior_agent_eligible_work_cell_missing")
    if len(uncontainerised_leaves) < 3:
        errors.append("uncontainerised_leaf_proof_incomplete")

    baseline = next(iter(inputs.values()), {})
    for frame_id, frame in inputs.items():
        for field in ("practice_id", "principal_id", "correlation_id", "context_revision"):
            if frame.get(field) != baseline.get(field):
                errors.append(f"input_frame_boundary_mismatch:{frame_id}:{field}")
        _, freshness_errors = _timestamp(
            frame.get("freshness", {}).get("observed_at"), label=f"input:{frame_id}"
        )
        errors.extend(freshness_errors)
    if not inputs:
        errors.append("input_frames_empty")

    for port_id, port in ports.items():
        if port.get("recipient_node_id") not in nodes:
            errors.append(f"output_port_recipient_unknown:{port_id}")
        atomic_group_id = port.get("atomic_group_id")
        if atomic_group_id is not None and atomic_group_id not in groups:
            errors.append(f"output_port_atomic_group_unknown:{port_id}")
        if _authority_rank(port.get("authority_ceiling")) < 0:
            errors.append(f"output_port_authority_invalid:{port_id}")
        required, required_errors = _string_set(
            port.get("required_payload_fields"), label=f"port_required:{port_id}"
        )
        allowed, allowed_errors = _string_set(
            port.get("allowed_payload_fields"), label=f"port_allowed:{port_id}"
        )
        errors.extend(required_errors + allowed_errors)
        if not required <= allowed:
            errors.append(f"output_port_required_not_allowed:{port_id}")
        if port.get("human_gate_required") and port.get("recipient_node_id") != "human-gate-v1":
            errors.append(f"human_gate_port_recipient_invalid:{port_id}")

    emitted_by_attempt: dict[str, set[str]] = {
        attempt_id: set(attempt.get("emitted_draft_ids", []))
        for attempt_id, attempt in attempts.items()
    }
    for draft_id, draft in drafts.items():
        attempt_id = draft.get("attempt_id")
        if attempt_id not in attempts:
            errors.append(f"draft_attempt_unknown:{draft_id}:{attempt_id}")
        elif draft_id not in emitted_by_attempt.get(attempt_id, set()):
            errors.append(f"draft_not_declared_by_attempt:{draft_id}:{attempt_id}")
        if draft.get("output_port_id") not in ports:
            errors.append(f"draft_output_port_unknown:{draft_id}")
        if not isinstance(draft.get("source_frame_ids"), list) or not draft.get("source_frame_ids"):
            errors.append(f"draft_source_frames_empty:{draft_id}")
        if _authority_rank(draft.get("authority_class")) < 0:
            errors.append(f"draft_authority_invalid:{draft_id}")
        _, freshness_errors = _timestamp(
            draft.get("freshness", {}).get("observed_at"), label=f"draft:{draft_id}"
        )
        errors.extend(freshness_errors)
    for attempt_id, emitted in emitted_by_attempt.items():
        unknown = emitted - set(drafts)
        errors.extend(
            f"attempt_emitted_draft_unknown:{attempt_id}:{draft_id}"
            for draft_id in sorted(unknown)
        )
    primary = attempts.get("work-cell-attempt1", {})
    primary_ports = {
        drafts[draft_id].get("output_port_id")
        for draft_id in primary.get("emitted_draft_ids", [])
        if draft_id in drafts
    }
    if len(primary_ports) < 4:
        errors.append("multi_output_work_cell_proof_incomplete")

    policy = document.get("verification_policy")
    if not isinstance(policy, dict):
        errors.append("verification_policy_must_be_object")
        policy = {}
    if policy.get("default_decision") != "deny":
        errors.append("verification_policy_default_deny_required")
    if policy.get("checks_in_order") != REQUIRED_CHECK_ORDER:
        errors.append("verification_check_order_invalid")
    if policy.get("authority_order") != list(AUTHORITY_ORDER):
        errors.append("verification_authority_order_invalid")
    if policy.get("repair_allowlist") != REPAIR_ALLOWLIST:
        errors.append("verification_repair_allowlist_invalid")
    if policy.get("proofreader_node_id") not in nodes:
        errors.append("proofreader_node_unknown")
    retry_policy = policy.get("retry_policy", {})
    if retry_policy.get("max_same_reason_attempts") != 2:
        errors.append("retry_budget_invalid")
    if retry_policy.get("feedback_includes_draft_content") is not False:
        errors.append("retry_feedback_must_exclude_draft")

    for group_id, group in groups.items():
        member_ports = group.get("member_port_ids", [])
        if not isinstance(member_ports, list) or len(member_ports) < 2:
            errors.append(f"atomic_group_members_invalid:{group_id}")
        errors.extend(
            f"atomic_group_port_unknown:{group_id}:{port_id}"
            for port_id in member_ports
            if port_id not in ports
        )
        errors.extend(
            f"atomic_group_port_declaration_mismatch:{group_id}:{port_id}"
            for port_id in member_ports
            if port_id in ports and ports[port_id].get("atomic_group_id") != group_id
        )
        if group.get("release_mode") != "all-or-none":
            errors.append(f"atomic_group_release_mode_invalid:{group_id}")

    try:
        computed = _compute_verification(document)
        computed_by_case = {item["case_id"]: item for item in computed["case_results"]}
        for case_id, case in cases.items():
            for draft_id in case.get("draft_ids", []):
                if draft_id not in drafts:
                    errors.append(f"verification_case_draft_unknown:{case_id}:{draft_id}")
            result = computed_by_case.get(case_id)
            if result is None:
                errors.append(f"verification_case_result_missing:{case_id}")
            elif case.get("expected") != _expected_projection(result):
                errors.append(f"verification_case_expected_mismatch:{case_id}")
        actual_verdicts = {
            frame["verdict"]
            for case_result in computed["case_results"]
            for frame in case_result["frame_results"]
        }
        errors.extend(
            f"verification_verdict_unproved:{verdict}"
            for verdict in sorted(REQUIRED_VERDICTS - actual_verdicts)
        )
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"verification_projection_failed:{type(error).__name__}")

    for grant_id, grant in grants.items():
        if grant.get("execution_enabled") is not False:
            errors.append(f"grant_execution_must_be_false:{grant_id}")
        if grant.get("returns_data") is not False:
            errors.append(f"grant_returns_data_must_be_false:{grant_id}")
        if grant.get("practice_id") != baseline.get("practice_id"):
            errors.append(f"grant_practice_mismatch:{grant_id}")
        if grant.get("principal_id") != baseline.get("principal_id"):
            errors.append(f"grant_principal_mismatch:{grant_id}")
        issued, issued_errors = _timestamp(grant.get("issued_at"), label=f"grant:{grant_id}:issued")
        expires, expires_errors = _timestamp(grant.get("expires_at"), label=f"grant:{grant_id}:expires")
        errors.extend(issued_errors + expires_errors)
        if issued and expires and issued >= expires:
            errors.append(f"grant_expiry_invalid:{grant_id}")

    for trace_id, trace in traces.items():
        source = attempts.get(trace.get("from_attempt_id"))
        target = attempts.get(trace.get("to_attempt_id"))
        if source is None or target is None:
            errors.append(f"retry_trace_attempt_unknown:{trace_id}")
            continue
        if target.get("attempt", 0) <= source.get("attempt", 0):
            errors.append(f"retry_trace_not_forward:{trace_id}")
        if trace.get("kind").startswith("same-generation"):
            for field in ("container_generation", "policy_revision", "checkpoint_id"):
                if source.get(field) != target.get(field):
                    errors.append(f"same_generation_retry_changed:{trace_id}:{field}")
            if target.get("retry_of") != source.get("id"):
                errors.append(f"same_generation_retry_lineage_invalid:{trace_id}")
            feedback = trace.get("feedback_frame", {})
            if feedback.get("includes_draft_content") is not False:
                errors.append(f"retry_feedback_contains_draft:{trace_id}")
        elif trace.get("kind") == "fresh-context-supersession":
            if target.get("superseded_from") != source.get("id"):
                errors.append(f"supersession_lineage_invalid:{trace_id}")
            if target.get("container_generation") != source.get("container_generation", 0) + 1:
                errors.append(f"supersession_generation_invalid:{trace_id}")
            if target.get("policy_revision") <= source.get("policy_revision", 0):
                errors.append(f"supersession_policy_revision_invalid:{trace_id}")
            if trace.get("fresh_read_grant_id") not in grants:
                errors.append(f"supersession_grant_unknown:{trace_id}")
            if trace.get("stale_completion_disposition") != "rejected-stale-generation":
                errors.append(f"stale_completion_not_rejected:{trace_id}")

    gate = document.get("human_gate_policy", {})
    if gate.get("node_id") not in nodes:
        errors.append("human_gate_node_unknown")
    if gate.get("execution_enabled") is not False:
        errors.append("human_gate_execution_must_be_false")
    if gate.get("command_authority") is not False:
        errors.append("human_gate_command_authority_forbidden")
    if gate.get("confirmation_evidence_only") is not True:
        errors.append("human_gate_confirmation_evidence_required")
    if gate.get("backend_revalidation_required") is not True:
        errors.append("human_gate_backend_revalidation_required")
    if gate.get("rejected_frame_can_be_rehabilitated") is not False:
        errors.append("human_gate_rejected_rehabilitation_forbidden")

    for reference in document.get("evidence", []):
        if not _safe_repo_reference(reference):
            errors.append(f"unsafe_repo_reference:evidence:{reference}")
        elif not (repo_root / reference).is_file():
            errors.append(f"evidence_reference_missing:{reference}")
    return sorted(set(errors))


def build_verification(
    document: dict[str, Any], *, repo_root: Path, validate: bool = True
) -> dict[str, Any]:
    if validate:
        errors = validate_document(document, repo_root=repo_root)
        if errors:
            raise CognitiveWorkCellError("document_invalid:" + "|".join(errors))
    return _compute_verification(document)


def compile_manifests(document: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    errors = validate_document(document, repo_root=repo_root)
    if errors:
        raise CognitiveWorkCellError("document_invalid:" + "|".join(errors))
    classes = {item["id"]: item for item in document["execution_classes"]}
    work_cell = next(
        node for node in document["nodes"] if node["role"] == "bounded-cognitive-work-cell"
    )
    return {
        "schema_version": MANIFEST_VERSION,
        "protocol_id": document["protocol_id"],
        "workflow_id": document["workflow_id"],
        "operational_graph_revision": document["operational_graph_revision"],
        "source_document_sha256": canonical_sha256(document),
        "authority": {
            "dry_run": True,
            "execution_enabled": False,
            "default_decision": "deny",
            "agent_attached": False,
            "container_started": False,
            "adapters_configured": False,
        },
        "node_manifest": {
            "granularity_principle": document["node_granularity_policy"]["principle"],
            "execution_classes": document["execution_classes"],
            "nodes": [
                {
                    "node_id": node["id"],
                    "topological_role": node["topological_role"],
                    "execution_class": node["execution_class"],
                    "agent_eligible": node["agent_eligible"],
                    "agent_attached": node["agent_attached"],
                    "container_declared": node["container_policy"] is not None,
                    "container_started": False,
                }
                for node in document["nodes"]
            ],
            "future_agentisation_requires_new_generation": True,
        },
        "work_cell_manifest": {
            "node_id": work_cell["id"],
            "execution_class": classes[work_cell["execution_class"]]["id"],
            "authority_ceiling": classes[work_cell["execution_class"]]["authority_ceiling"],
            "agent_eligible": True,
            "agent_attached": False,
            "container_started": False,
            "context_frame_types": sorted(
                frame["frame_type"] for frame in document["input_frames"]
            ),
            "output_ports": [
                {
                    "port_id": port["id"],
                    "frame_type": port["frame_type"],
                    "recipient_node_id": port["recipient_node_id"],
                    "channel": port["channel"],
                    "authority_ceiling": port["authority_ceiling"],
                    "human_gate_required": port["human_gate_required"],
                    "atomic_group_id": port["atomic_group_id"],
                }
                for port in document["output_ports"]
            ],
        },
        "proofreader_manifest": {
            "node_id": document["verification_policy"]["proofreader_node_id"],
            "checks_in_order": document["verification_policy"]["checks_in_order"],
            "repair_allowlist": document["verification_policy"]["repair_allowlist"],
            "repair_forbidden": document["verification_policy"]["repair_forbidden"],
            "verdict_dispositions": document["verification_policy"]["verdict_dispositions"],
            "original_draft_immutable": True,
        },
        "retry_manifest": {
            "max_same_reason_attempts": document["verification_policy"]["retry_policy"]["max_same_reason_attempts"],
            "feedback_frame_type": document["verification_policy"]["retry_policy"]["feedback_frame_type"],
            "feedback_includes_draft_content": False,
            "same_policy_retry_allowed": True,
            "policy_change_requires_new_generation": True,
            "stale_context_requires_supersession": True,
            "stale_completion_disposition": "rejected-stale-generation",
        },
        "human_gate_manifest": {
            "node_id": document["human_gate_policy"]["node_id"],
            "required_role": document["human_gate_policy"]["required_role"],
            "accepted_frame_types": document["human_gate_policy"]["accepted_frame_types"],
            "accepted_verdicts": document["human_gate_policy"]["accepted_verdicts"],
            "allowed_actions": document["human_gate_policy"]["allowed_actions"],
            "execution_enabled": False,
            "command_authority": False,
            "confirmation_evidence_only": True,
            "backend_revalidation_required": True,
        },
        "atomic_group_manifest": document["atomic_output_groups"],
        "closed_connections": sorted(REQUIRED_CLOSED_BOUNDARIES),
    }


def build_evidence(document: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    verification = build_verification(document, repo_root=repo_root)
    manifests = compile_manifests(document, repo_root=repo_root)
    frame_results = [
        frame
        for case in verification["case_results"]
        for frame in case["frame_results"]
    ]
    verdicts = {frame["verdict"] for frame in frame_results}
    primary = next(
        attempt
        for attempt in document["work_cell_attempts"]
        if attempt["id"] == "work-cell-attempt1"
    )
    return {
        "schema_version": EVIDENCE_VERSION,
        "result": "ariadne_bounded_cognitive_work_cell_protocol_pass",
        "protocol_id": document["protocol_id"],
        "workflow_id": document["workflow_id"],
        "operational_graph_revision": document["operational_graph_revision"],
        "source_document_sha256": canonical_sha256(document),
        "evidence_label": document["authority"]["evidence_label"],
        "execution_enabled": False,
        "verification_case_count": len(verification["case_results"]),
        "draft_frame_count": len(document["draft_frames"]),
        "released_edge_count": len(verification["released_edges"]),
        "repair_receipt_count": len(verification["repair_receipts"]),
        "proved_verdicts": sorted(verdicts),
        "proofs": {
            "node_topology_execution_and_container_are_orthogonal": (
                any(
                    node["topological_role"] == "interior"
                    and node["agent_eligible"]
                    and node["agent_attached"] is False
                    for node in document["nodes"]
                )
                and sum(
                    node["topological_role"] == "leaf"
                    and node["container_policy"] is None
                    for node in document["nodes"]
                )
                >= 3
            ),
            "one_work_cell_emits_multiple_typed_ports": len(primary["emitted_draft_ids"])
            >= 4,
            "all_frozen_verdicts_are_proved": REQUIRED_VERDICTS <= verdicts,
            "repairs_are_allowlisted_and_immutable": all(
                receipt["original_immutable"] is True
                and set(receipt["repair_rules"]) <= set(REPAIR_ALLOWLIST)
                and receipt["original_sha256"] != receipt["repaired_sha256"]
                for receipt in verification["repair_receipts"]
            ),
            "retry_budget_aborts_repeated_failure": any(
                case["case_id"] == "case-grounding-budget-abort"
                and case["disposition"] == "abort-edge"
                for case in verification["case_results"]
            ),
            "stale_context_requires_fresh_read_supersession": any(
                case["case_id"] == "case-stale-context"
                and case["disposition"] == "fresh-read-and-supersede"
                for case in verification["case_results"]
            ),
            "human_gate_is_verified_but_non_command": (
                any(
                    frame["verdict"] in {
                        "pass_to_human_gate",
                        "pass_with_repair_to_human_gate",
                    }
                    for frame in frame_results
                )
                and document["human_gate_policy"]["command_authority"] is False
            ),
            "atomic_inconsistency_releases_nothing": any(
                case["case_id"] == "case-atomic-inconsistency"
                and not case["released_edges"]
                for case in verification["case_results"]
            ),
            "manifests_are_default_deny_and_non_executing": (
                manifests["authority"]["default_decision"] == "deny"
                and manifests["authority"]["execution_enabled"] is False
                and manifests["authority"]["agent_attached"] is False
                and manifests["authority"]["container_started"] is False
            ),
        },
        "closed_connections": sorted(REQUIRED_CLOSED_BOUNDARIES),
    }


def render_markdown(document: dict[str, Any], *, repo_root: Path) -> str:
    verification = build_verification(document, repo_root=repo_root)
    lines = [
        "# Ariadne Bounded Cognitive Work Cell - Authored-Synthetic Trace",
        "",
        "Execution enabled: **no**",
        "",
        "One agent-eligible but unoccupied work cell emits several typed drafts.",
        "The deterministic proofreader releases, repairs, retries, supersedes or",
        "aborts edges under frozen policy; it starts no runtime and issues no command.",
        "",
        "## Verification decisions",
        "",
        "| Case | Draft | Verdict | Disposition | Reasons |",
        "|---|---|---|---|---|",
    ]
    for case in verification["case_results"]:
        for frame in case["frame_results"]:
            lines.append(
                f"| {case['case_id']} | {frame['draft_id']} | {frame['verdict']} | "
                f"{frame['disposition']} | {', '.join(frame['reason_codes'])} |"
            )
    lines.extend(
        [
            "",
            "## Repair evidence",
            "",
        ]
    )
    for receipt in verification["repair_receipts"]:
        lines.append(
            f"- `{receipt['source_draft_id']}` remains immutable; "
            f"`{receipt['repaired_frame_id']}` applies "
            f"{', '.join(receipt['repair_rules'])}."
        )
    lines.extend(
        [
            "",
            "## Authority stop",
            "",
            "Verified candidates may reach a bounded human gate. Rejected frames cannot",
            "be rehabilitated, and neither proofreader nor gate can confirm, write, call",
            "a product surface or execute an appointment command.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect the non-executing Ariadne bounded cognitive work-cell proof."
    )
    parser.add_argument("--document", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate the authored-synthetic document.")
    subparsers.add_parser("verify", help="Render deterministic proofreader results.")
    subparsers.add_parser(
        "compile-manifests", help="Render inert dry-run policy manifests."
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
        if args.command == "verify":
            print(canonical_json(build_verification(document, repo_root=repo_root)), end="")
            return 0
        if args.command == "compile-manifests":
            print(canonical_json(compile_manifests(document, repo_root=repo_root)), end="")
            return 0
        if args.command == "trace":
            print(render_markdown(document, repo_root=repo_root), end="")
            return 0
    except CognitiveWorkCellError as error:
        print(f"bounded cognitive work cell failed: {error}")
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
