"""Pure provider-free Practice Context Fabric and Bureau Memory Bank contract."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


SCHEMA_VERSION = "emr4.practice_context_fabric_bureau_memory.v1"
EVIDENCE_LABEL = "provider_free_authored_synthetic_context_fabric_contract"
READ_FIELDS = {
    "originating_bureau",
    "request_label_code",
    "action_family",
    "outcome_code",
    "initiator_relation",
    "target_kind",
    "opaque_target_ref",
    "started_at",
    "completed_at",
    "source_receipt_ref",
    "source_revision",
    "source_digest",
    "supersession_state",
    "relevance_reason_codes",
    "authority_ceiling",
}
REQUESTABLE_FIELDS = {"request_label_code", "opaque_target_ref"}


class ContractViolation(ValueError):
    """Raised when a closed deterministic contract fails."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _without(value: dict[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def seal(value: dict[str, Any], field: str) -> dict[str, Any]:
    result = dict(value)
    result[field] = canonical_sha256(_without(result, field))
    return result


def verify_seal(value: dict[str, Any], field: str) -> None:
    if value.get(field) != canonical_sha256(_without(value, field)):
        raise ContractViolation(f"{field}_mismatch")


def _instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise ContractViolation("invalid_timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContractViolation("timestamp_requires_timezone")
    return parsed.astimezone(timezone.utc)


def _z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _window(value: dict[str, str]) -> tuple[datetime, datetime]:
    start, end = _instant(value["starts_at"]), _instant(value["ends_at"])
    if start >= end:
        raise ContractViolation("empty_time_window")
    return start, end


def _intersection(requested: list[str], allowed: list[str]) -> list[str]:
    allowed_set = set(allowed)
    return list(dict.fromkeys(item for item in requested if item in allowed_set))


def _project_memory_item(
    item: dict[str, Any], allowed_fields: list[str]
) -> dict[str, Any]:
    projected = dict(item)
    if "opaque_target_ref" not in allowed_fields:
        projected.pop("opaque_target_ref", None)
    return seal(projected, "memory_item_digest")


def build_context_need(
    candidate: dict[str, Any],
    authority_binding: dict[str, Any],
    *,
    assembled_at: str,
) -> dict[str, Any]:
    verify_seal(candidate, "candidate_digest")
    verify_seal(authority_binding, "binding_digest")
    if candidate["command_authority"] is not False:
        raise ContractViolation("candidate_command_authority")
    now = _instant(assembled_at)
    if _instant(candidate["issued_at"]) > now:
        raise ContractViolation("candidate_issued_in_future")
    verify_seal(candidate["bureau_memory_selector"], "selector_digest")
    if candidate["temporal_hint"] != candidate["bureau_memory_selector"]["temporal_hint"]:
        raise ContractViolation("candidate_selector_temporal_hint_mismatch")
    if now < _instant(authority_binding["issued_at"]) or now >= _instant(
        authority_binding["expires_at"]
    ):
        raise ContractViolation("authority_binding_not_current")
    need = {
        "schema_version": SCHEMA_VERSION,
        "need_id": candidate["need_id"],
        "candidate_digest": candidate["candidate_digest"],
        "binding_digest": authority_binding["binding_digest"],
        "assembled_at": assembled_at,
        "read_only": True,
        "command_authority": False,
    }
    return seal(need, "need_digest")


def intersect_context_scope(
    candidate: dict[str, Any],
    context_need: dict[str, Any],
    authority_binding: dict[str, Any],
    *,
    assembled_at: str,
) -> dict[str, Any]:
    verify_seal(candidate, "candidate_digest")
    verify_seal(context_need, "need_digest")
    verify_seal(authority_binding, "binding_digest")
    if not set(candidate["requested_fields"]).issubset(REQUESTABLE_FIELDS):
        raise ContractViolation("candidate_requested_fields_unknown")
    if not set(authority_binding["allowed_fields"]).issubset(REQUESTABLE_FIELDS):
        raise ContractViolation("binding_allowed_fields_unknown")
    if context_need["candidate_digest"] != candidate["candidate_digest"]:
        raise ContractViolation("need_candidate_binding_mismatch")
    if context_need["binding_digest"] != authority_binding["binding_digest"]:
        raise ContractViolation("need_authority_binding_mismatch")
    if context_need["assembled_at"] != assembled_at:
        raise ContractViolation("need_assembly_time_mismatch")

    reductions: list[str] = []
    bureau = candidate["requesting_bureau"]
    purpose = candidate["purpose_code"]
    bureau_allowed = bureau in authority_binding["allowed_bureaus"]
    purpose_allowed = purpose in authority_binding["allowed_purposes"]
    frame_types = _intersection(
        candidate["requested_frame_types"], authority_binding["allowed_frame_types"]
    )
    source_classes = _intersection(
        candidate["source_classes"], authority_binding["allowed_source_classes"]
    )
    fields = _intersection(
        candidate["requested_fields"], authority_binding["allowed_fields"]
    )
    selector = candidate["bureau_memory_selector"]
    verify_seal(selector, "selector_digest")
    originating_bureaus = _intersection(
        selector["originating_bureaus"], authority_binding["allowed_bureaus"]
    )
    action_families = _intersection(
        selector["action_families"], authority_binding["allowed_action_families"]
    )
    actor_relations = _intersection(
        selector["actor_relations"], authority_binding["allowed_actor_relations"]
    )
    outcome_codes = _intersection(
        selector["outcome_codes"], authority_binding["allowed_outcome_codes"]
    )
    requested_start, requested_end = _window(candidate["requested_time_window"])
    policy_start, policy_end = _window(authority_binding["authorized_time_window"])
    effective_start, effective_end = max(requested_start, policy_start), min(
        requested_end, policy_end
    )
    maximum_results = min(
        candidate["maximum_results"],
        selector["maximum_results"],
        authority_binding["maximum_results"],
    )
    freshness_seconds = min(
        candidate["freshness_seconds"], authority_binding["maximum_freshness_seconds"]
    )
    if fields != candidate["requested_fields"]:
        reductions.append("FIELDS_NARROWED")
    if effective_start != requested_start or effective_end != requested_end:
        reductions.append("TIME_WINDOW_NARROWED")
    if maximum_results != candidate["maximum_results"]:
        reductions.append("RESULT_LIMIT_NARROWED")
    mandatory = [
        bureau_allowed,
        purpose_allowed,
        bool(frame_types),
        bool(source_classes),
        bool(fields),
        "request_label_code" in fields,
        bool(originating_bureaus),
        bool(action_families),
        bool(actor_relations),
        bool(outcome_codes),
        effective_start < effective_end,
        maximum_results > 0,
    ]
    decision = "ADMIT" if all(mandatory) else "NOT_AVAILABLE"
    if decision == "NOT_AVAILABLE":
        reductions = ["SCOPE_NOT_AVAILABLE"]
    freshness_deadline = _instant(assembled_at).timestamp() + freshness_seconds
    freshness_dt = datetime.fromtimestamp(freshness_deadline, tz=timezone.utc)
    expires = min(_instant(authority_binding["expires_at"]), freshness_dt)
    grant = {
        "schema_version": SCHEMA_VERSION,
        "grant_id": "grant:" + context_need["need_id"],
        "need_digest": context_need["need_digest"],
        "binding_digest": authority_binding["binding_digest"],
        "selector_digest": selector["selector_digest"],
        "policy_version": authority_binding["policy_version"],
        "decision": decision,
        "requesting_bureau": bureau if bureau_allowed else "NOT_AVAILABLE",
        "purpose_code": purpose if purpose_allowed else "NOT_AVAILABLE",
        "allowed_frame_types": frame_types if decision == "ADMIT" else [],
        "allowed_source_classes": source_classes if decision == "ADMIT" else [],
        "allowed_fields": fields if decision == "ADMIT" else [],
        "originating_bureaus": originating_bureaus if decision == "ADMIT" else [],
        "action_families": action_families if decision == "ADMIT" else [],
        "actor_relations": actor_relations if decision == "ADMIT" else [],
        "outcome_codes": outcome_codes if decision == "ADMIT" else [],
        "effective_time_window": {
            "starts_at": _z(effective_start),
            "ends_at": _z(effective_end),
        }
        if decision == "ADMIT"
        else None,
        "maximum_results": maximum_results if decision == "ADMIT" else 0,
        "maximum_bytes": authority_binding["maximum_bytes"],
        "freshness_deadline": _z(freshness_dt),
        "reduction_reason_codes": reductions,
        "issued_at": assembled_at,
        "expires_at": _z(expires),
        "read_only": True,
        "command_authority": False,
        "provider_authority": False,
    }
    return seal(grant, "grant_digest")


def select_bureau_memory_items(
    selector: dict[str, Any],
    available_items: list[dict[str, Any]],
    scope_grant: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    verify_seal(scope_grant, "grant_digest")
    verify_seal(selector, "selector_digest")
    if scope_grant["selector_digest"] != selector["selector_digest"]:
        raise ContractViolation("grant_selector_binding_mismatch")
    if scope_grant["decision"] != "ADMIT":
        selected: list[dict[str, Any]] = []
        excluded = ["SCOPE_NOT_AVAILABLE"]
    else:
        start, end = _window(scope_grant["effective_time_window"])
        selected = []
        excluded = []
        for item in available_items:
            verify_seal(item, "memory_item_digest")
            if _instant(item["started_at"]) > _instant(item["completed_at"]):
                raise ContractViolation("memory_item_time_order_invalid")
            completed = _instant(item["completed_at"])
            matches = (
                item["originating_bureau"] in scope_grant["originating_bureaus"]
                and item["action_family"] in scope_grant["action_families"]
                and item["initiator_relation"] in scope_grant["actor_relations"]
                and item["outcome_code"] in scope_grant["outcome_codes"]
                and item["supersession_state"] == "CURRENT"
                and start <= completed < end
                and item["authority_ceiling"] == "read_context_only"
            )
            if matches:
                selected.append(
                    _project_memory_item(item, scope_grant["allowed_fields"])
                )
            else:
                excluded.append("ITEM_NOT_ADMITTED")
        selected.sort(
            key=lambda item: (
                -_instant(item["completed_at"]).timestamp(),
                item["memory_item_id"],
            )
        )
        if len(selected) > scope_grant["maximum_results"]:
            excluded.append("RESULT_LIMIT_APPLIED")
            selected = selected[: scope_grant["maximum_results"]]
        disclosed_bytes = 0
        byte_bounded: list[dict[str, Any]] = []
        for item in selected:
            item_bytes = len(canonical_json(item).encode("utf-8"))
            if disclosed_bytes + item_bytes <= scope_grant["maximum_bytes"]:
                byte_bounded.append(item)
                disclosed_bytes += item_bytes
            else:
                excluded.append("BYTE_LIMIT_APPLIED")
        selected = byte_bounded
    trace = {
        "schema_version": SCHEMA_VERSION,
        "selector_version": "context-memory-selector.v1",
        "selector_digest": selector["selector_digest"],
        "grant_digest": scope_grant["grant_digest"],
        "candidate_item_digests": sorted(
            item["memory_item_digest"] for item in available_items
        ),
        "selected_item_ids": [item["memory_item_id"] for item in selected],
        "rule_steps": [
            "scope_intersection",
            "half_open_time_filter",
            "supersession_filter",
            "canonical_order",
            "result_cap",
        ],
        "exclusion_reason_codes": sorted(set(excluded)),
    }
    return selected, seal(trace, "trace_digest")


def assemble_context_frame_set(
    context_need: dict[str, Any],
    scope_grant: dict[str, Any],
    selector: dict[str, Any],
    available_items: list[dict[str, Any]],
    *,
    assembled_at: str,
    source_revision: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    verify_seal(context_need, "need_digest")
    verify_seal(scope_grant, "grant_digest")
    selected, selector_trace = select_bureau_memory_items(
        selector, available_items, scope_grant
    )
    frames: list[dict[str, Any]] = []
    if scope_grant["decision"] == "ADMIT":
        frame = {
            "schema_version": SCHEMA_VERSION,
            "frame_id": "frame:" + context_need["need_id"],
            "frame_type": "bureau_memory_item_set",
            "source_class": "recent_collective_work",
            "source_refs": [item["source_receipt_ref"] for item in selected],
            "practice_binding_digest": scope_grant["binding_digest"],
            "purpose_code": scope_grant["purpose_code"],
            "items": selected,
            "coverage_complete": False,
            "omission_codes": selector_trace["exclusion_reason_codes"],
            "observed_at": assembled_at,
            "assembled_at": assembled_at,
            "freshness_deadline": scope_grant["freshness_deadline"],
            "expires_at": scope_grant["expires_at"],
            "source_revision": source_revision,
            "evidence_mode": "authored_synthetic",
            "redaction_disposition": "minimal_allowlist_only",
            "supersession_state": "CURRENT",
            "read_only": True,
            "command_authority": False,
        }
        frames = [seal(frame, "content_digest")]
    frame_set = {
        "schema_version": SCHEMA_VERSION,
        "frame_set_id": "frame-set:" + context_need["need_id"],
        "need_digest": context_need["need_digest"],
        "grant_digest": scope_grant["grant_digest"],
        "binding_digest": scope_grant["binding_digest"],
        "selector_digest": selector["selector_digest"],
        "frames": frames,
        "source_revisions": [source_revision] if frames else [],
        "omission_codes": selector_trace["exclusion_reason_codes"],
        "ambiguity_state": "NONE",
        "maximum_disclosure": scope_grant["maximum_results"],
        "assembled_at": assembled_at,
        "expires_at": scope_grant["expires_at"],
        "read_only": True,
        "command_authority": False,
    }
    frame_set = seal(frame_set, "frame_set_digest")
    weave = {
        "schema_version": SCHEMA_VERSION,
        "weave_version": "context-weave.v1",
        "need_digest": context_need["need_digest"],
        "grant_digest": scope_grant["grant_digest"],
        "selector_digest": selector["selector_digest"],
        "selector_trace_digest": selector_trace["trace_digest"],
        "frame_set_digest": frame_set["frame_set_digest"],
        "source_classes_queried": ["recent_collective_work"],
        "scope_reduction_codes": scope_grant["reduction_reason_codes"],
        "released_frame_ids": [frame["frame_id"] for frame in frames],
        "raw_audit_accessed": False,
    }
    return frame_set, selector_trace, seal(weave, "trace_digest")


def proofread_same_packet(
    context_need: dict[str, Any],
    scope_grant: dict[str, Any],
    selector: dict[str, Any],
    frame_set: dict[str, Any],
    selector_trace: dict[str, Any],
    weave_trace: dict[str, Any],
    *,
    proofread_at: str,
) -> dict[str, Any]:
    for value, field in (
        (context_need, "need_digest"),
        (scope_grant, "grant_digest"),
        (selector, "selector_digest"),
        (frame_set, "frame_set_digest"),
        (selector_trace, "trace_digest"),
        (weave_trace, "trace_digest"),
    ):
        verify_seal(value, field)
    reasons: list[str] = []
    if frame_set["need_digest"] != context_need["need_digest"]:
        reasons.append("NEED_DIGEST_MISMATCH")
    if frame_set["grant_digest"] != scope_grant["grant_digest"]:
        reasons.append("GRANT_DIGEST_MISMATCH")
    if scope_grant["selector_digest"] != selector["selector_digest"]:
        reasons.append("GRANT_SELECTOR_DIGEST_MISMATCH")
    if frame_set["selector_digest"] != selector["selector_digest"]:
        reasons.append("FRAME_SET_SELECTOR_DIGEST_MISMATCH")
    if selector_trace["selector_digest"] != selector["selector_digest"]:
        reasons.append("SELECTOR_TRACE_SELECTOR_DIGEST_MISMATCH")
    if selector_trace["grant_digest"] != scope_grant["grant_digest"]:
        reasons.append("SELECTOR_TRACE_GRANT_DIGEST_MISMATCH")
    if weave_trace["selector_digest"] != selector["selector_digest"]:
        reasons.append("WEAVE_SELECTOR_DIGEST_MISMATCH")
    if weave_trace["frame_set_digest"] != frame_set["frame_set_digest"]:
        reasons.append("FRAME_SET_DIGEST_MISMATCH")
    if weave_trace["selector_trace_digest"] != selector_trace["trace_digest"]:
        reasons.append("SELECTOR_TRACE_DIGEST_MISMATCH")
    if weave_trace["need_digest"] != context_need["need_digest"]:
        reasons.append("WEAVE_NEED_DIGEST_MISMATCH")
    if weave_trace["grant_digest"] != scope_grant["grant_digest"]:
        reasons.append("WEAVE_GRANT_DIGEST_MISMATCH")
    if _instant(proofread_at) >= _instant(frame_set["expires_at"]):
        reasons.append("FRAME_SET_EXPIRED")
    if scope_grant["decision"] != "ADMIT":
        reasons.append("SCOPE_NOT_AVAILABLE")
    if (
        scope_grant["read_only"] is not True
        or scope_grant["command_authority"] is not False
        or scope_grant["provider_authority"] is not False
    ):
        reasons.append("GRANT_AUTHORITY_CEILING_INVALID")
    if frame_set["binding_digest"] != scope_grant["binding_digest"]:
        reasons.append("FRAME_SET_BINDING_DIGEST_MISMATCH")
    if frame_set["maximum_disclosure"] != scope_grant["maximum_results"]:
        reasons.append("FRAME_SET_DISCLOSURE_LIMIT_MISMATCH")
    if frame_set["expires_at"] != scope_grant["expires_at"]:
        reasons.append("FRAME_SET_EXPIRY_MISMATCH")
    if (
        frame_set["read_only"] is not True
        or frame_set["command_authority"] is not False
    ):
        reasons.append("FRAME_SET_AUTHORITY_CEILING_INVALID")
    if len(frame_set["frames"]) > 1:
        reasons.append("FRAME_CARDINALITY_INVALID")
    released_ids = [frame["frame_id"] for frame in frame_set["frames"]]
    if released_ids != weave_trace["released_frame_ids"]:
        reasons.append("RELEASED_FRAME_IDS_MISMATCH")
    if weave_trace["raw_audit_accessed"] is not False:
        reasons.append("RAW_AUDIT_ACCESSED")
    if not set(weave_trace["source_classes_queried"]).issubset(
        scope_grant["allowed_source_classes"]
    ):
        reasons.append("WEAVE_SOURCE_SCOPE_INVALID")
    selected_ids: list[str] = []
    for frame in frame_set["frames"]:
        verify_seal(frame, "content_digest")
        if frame["frame_type"] not in scope_grant["allowed_frame_types"]:
            reasons.append("FRAME_TYPE_INVALID")
        if frame["source_class"] not in scope_grant["allowed_source_classes"]:
            reasons.append("SOURCE_CLASS_INVALID")
        if frame["purpose_code"] != scope_grant["purpose_code"]:
            reasons.append("FRAME_PURPOSE_INVALID")
        if frame["practice_binding_digest"] != scope_grant["binding_digest"]:
            reasons.append("FRAME_PRACTICE_BINDING_INVALID")
        if frame["expires_at"] != frame_set["expires_at"]:
            reasons.append("FRAME_EXPIRY_MISMATCH")
        if _instant(frame["expires_at"]) > _instant(frame["freshness_deadline"]):
            reasons.append("FRAME_EXPIRY_EXCEEDS_FRESHNESS")
        if frame["supersession_state"] != "CURRENT":
            reasons.append("FRAME_SUPERSEDED")
        if frame["read_only"] is not True or frame["command_authority"] is not False:
            reasons.append("AUTHORITY_CEILING_INVALID")
        if len(frame["items"]) > scope_grant["maximum_results"]:
            reasons.append("ITEM_CARDINALITY_INVALID")
        if frame["source_revision"] not in frame_set["source_revisions"]:
            reasons.append("SOURCE_REVISION_MISMATCH")
        if frame["source_refs"] != [
            item["source_receipt_ref"] for item in frame["items"]
        ]:
            reasons.append("SOURCE_REFS_MISMATCH")
        disclosed_bytes = sum(
            len(canonical_json(item).encode("utf-8")) for item in frame["items"]
        )
        if disclosed_bytes > scope_grant["maximum_bytes"]:
            reasons.append("BYTE_LIMIT_EXCEEDED")
        start, end = _window(scope_grant["effective_time_window"])
        for item in frame["items"]:
            verify_seal(item, "memory_item_digest")
            if set(item) - (
                READ_FIELDS
                | {
                    "schema_version",
                    "memory_item_id",
                    "request_kind",
                    "memory_item_digest",
                }
            ):
                reasons.append("MEMORY_ITEM_NOT_MINIMIZED")
            if (
                "opaque_target_ref" in item
                and "opaque_target_ref" not in scope_grant["allowed_fields"]
            ):
                reasons.append("FIELD_SCOPE_INVALID")
            completed = _instant(item["completed_at"])
            if not start <= completed < end:
                reasons.append("ITEM_TIME_SCOPE_INVALID")
            if item["originating_bureau"] not in scope_grant["originating_bureaus"]:
                reasons.append("ITEM_BUREAU_SCOPE_INVALID")
            if item["action_family"] not in scope_grant["action_families"]:
                reasons.append("ITEM_ACTION_SCOPE_INVALID")
            if item["initiator_relation"] not in scope_grant["actor_relations"]:
                reasons.append("ITEM_ACTOR_SCOPE_INVALID")
            if item["outcome_code"] not in scope_grant["outcome_codes"]:
                reasons.append("ITEM_OUTCOME_SCOPE_INVALID")
            if item["supersession_state"] != "CURRENT":
                reasons.append("ITEM_SUPERSEDED")
            if item["authority_ceiling"] != "read_context_only":
                reasons.append("ITEM_AUTHORITY_CEILING_INVALID")
            selected_ids.append(item["memory_item_id"])
    if selected_ids != selector_trace["selected_item_ids"]:
        reasons.append("SELECTED_ITEM_IDS_MISMATCH")
    trace = {
        "schema_version": SCHEMA_VERSION,
        "proofreader_version": "context-proofreader.v1",
        "need_digest": context_need["need_digest"],
        "grant_digest": scope_grant["grant_digest"],
        "selector_digest": selector["selector_digest"],
        "frame_set_digest": frame_set["frame_set_digest"],
        "selector_trace_digest": selector_trace["trace_digest"],
        "weave_trace_digest": weave_trace["trace_digest"],
        "checks": [
            "tenant_and_binding",
            "purpose_and_scope",
            "source_and_fields",
            "freshness_and_expiry",
            "minimisation_and_provenance",
            "supersession_and_authority",
            "same_packet_digest",
        ],
        "release_decision": "RELEASE" if not reasons else "BLOCK",
        "reason_codes": sorted(set(reasons)),
        "proofread_at": proofread_at,
    }
    return seal(trace, "trace_digest")


def build_contract_packet(
    candidate: dict[str, Any],
    authority_binding: dict[str, Any],
    available_items: list[dict[str, Any]],
    *,
    assembled_at: str,
    proofread_at: str,
    source_revision: str,
) -> dict[str, Any]:
    need = build_context_need(candidate, authority_binding, assembled_at=assembled_at)
    grant = intersect_context_scope(
        candidate, need, authority_binding, assembled_at=assembled_at
    )
    selector = candidate["bureau_memory_selector"]
    frame_set, selector_trace, weave_trace = assemble_context_frame_set(
        need,
        grant,
        selector,
        available_items,
        assembled_at=assembled_at,
        source_revision=source_revision,
    )
    proofreader = proofread_same_packet(
        need,
        grant,
        selector,
        frame_set,
        selector_trace,
        weave_trace,
        proofread_at=proofread_at,
    )
    packet = {
        "schema_version": SCHEMA_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "candidate": candidate,
        "authority_binding": authority_binding,
        "context_need": need,
        "scope_grant": grant,
        "memory_selector": selector,
        "available_memory_items": available_items,
        "selector_trace": selector_trace,
        "frame_set": frame_set,
        "weave_trace": weave_trace,
        "proofreader_trace": proofreader,
        "authority_ceiling": "read_context_only",
        "blocked_boundaries": [
            "raw_audit",
            "provider",
            "database",
            "persistence",
            "product_runtime",
            "command",
            "write",
            "deployment",
            "production",
            "release",
            "protected_evidence",
            "protected_refs",
        ],
    }
    return seal(packet, "contract_digest")
