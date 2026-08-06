"""Pure provider-free Current operational weave for the Practice Context Fabric."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    ContractViolation,
    canonical_json,
    canonical_sha256,
    seal,
    verify_seal,
)


SCHEMA_VERSION = "emr4.practice_context_fabric_current_operational_weave.v1"
EVIDENCE_LABEL = "provider_free_authored_synthetic_current_operational_weave"
DATA_CLASS = "authored_synthetic_no_product_data"

FRAME_ORDER = (
    "current_diary_projection",
    "current_waiting_room_projection",
    "active_practitioner_directory",
    "private_application_session_state",
)

SOURCE_TRIPLES = {
    "current_diary_projection": (
        "current_diary",
        "api_spine.appointment_diary_read.v1",
    ),
    "current_waiting_room_projection": (
        "current_waiting_room",
        "emr4.waiting_room_context_frame.v1",
    ),
    "active_practitioner_directory": (
        "practitioner_directory",
        "practice-practitioner-directory-read.v1",
    ),
    "private_application_session_state": (
        "private_session_state",
        "emr4.native_diary_application_session_state.v1",
    ),
}

REQUESTABLE_FIELDS = {
    "diary_practitioner_ref",
    "diary_time",
    "diary_status",
    "waiting_practitioner_ref",
    "waiting_status",
    "waiting_elapsed_minutes",
    "waiting_threshold_code",
    "directory_display_label",
    "directory_role_label",
    "directory_default_location_ref",
    "session_visible_diary",
    "session_active_practitioner_ref",
    "session_focus_appointment_ref",
    "session_proposal_state",
}


class OperationalWeaveViolation(ContractViolation):
    """Raised when the bounded operational weave fails closed."""


def _instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise OperationalWeaveViolation("invalid_timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise OperationalWeaveViolation("timestamp_requires_timezone")
    return parsed.astimezone(timezone.utc)


def _z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _window(value: dict[str, str]) -> tuple[datetime, datetime]:
    start, end = _instant(value["starts_at"]), _instant(value["ends_at"])
    if start >= end:
        raise OperationalWeaveViolation("empty_time_window")
    return start, end


def _intersection(requested: list[str], allowed: list[str]) -> list[str]:
    allowed_set = set(allowed)
    return list(dict.fromkeys(item for item in requested if item in allowed_set))


def _session_binding_digest(authority_binding: dict[str, Any]) -> str:
    return canonical_sha256(
        {
            "practice_id": authority_binding["practice_id"],
            "principal_ref": authority_binding["principal_ref"],
            "session_id": authority_binding["session_id"],
            "session_generation": authority_binding["session_generation"],
        }
    )


def _verify_candidate_source_pairing(candidate: dict[str, Any]) -> None:
    expected = {
        SOURCE_TRIPLES[frame_type][0]
        for frame_type in candidate["requested_frame_types"]
    }
    if expected != set(candidate["source_classes"]):
        raise OperationalWeaveViolation("candidate_frame_source_pairing_invalid")
    if not set(candidate["required_source_classes"]).issubset(expected):
        raise OperationalWeaveViolation("candidate_required_sources_invalid")


def build_operational_context_need(
    candidate: dict[str, Any],
    authority_binding: dict[str, Any],
    *,
    assembled_at: str,
) -> dict[str, Any]:
    verify_seal(candidate, "candidate_digest")
    verify_seal(authority_binding, "binding_digest")
    _verify_candidate_source_pairing(candidate)
    if candidate["command_authority"] is not False:
        raise OperationalWeaveViolation("candidate_command_authority")
    if candidate["provider_authority"] is not False:
        raise OperationalWeaveViolation("candidate_provider_authority")
    now = _instant(assembled_at)
    if _instant(candidate["issued_at"]) > now:
        raise OperationalWeaveViolation("candidate_issued_in_future")
    if now < _instant(authority_binding["issued_at"]) or now >= _instant(
        authority_binding["expires_at"]
    ):
        raise OperationalWeaveViolation("authority_binding_not_current")
    if authority_binding["session_binding_digest"] != _session_binding_digest(
        authority_binding
    ):
        raise OperationalWeaveViolation("session_binding_digest_mismatch")
    need = {
        "schema_version": SCHEMA_VERSION,
        "need_id": candidate["need_id"],
        "candidate_digest": candidate["candidate_digest"],
        "binding_digest": authority_binding["binding_digest"],
        "assembled_at": assembled_at,
        "read_only": True,
        "command_authority": False,
        "provider_authority": False,
    }
    return seal(need, "need_digest")


def intersect_operational_scope(
    candidate: dict[str, Any],
    context_need: dict[str, Any],
    authority_binding: dict[str, Any],
    *,
    assembled_at: str,
) -> dict[str, Any]:
    verify_seal(candidate, "candidate_digest")
    verify_seal(context_need, "need_digest")
    verify_seal(authority_binding, "binding_digest")
    _verify_candidate_source_pairing(candidate)
    if not set(candidate["requested_fields"]).issubset(REQUESTABLE_FIELDS):
        raise OperationalWeaveViolation("candidate_requested_fields_unknown")
    if not set(authority_binding["allowed_fields"]).issubset(REQUESTABLE_FIELDS):
        raise OperationalWeaveViolation("binding_allowed_fields_unknown")
    if context_need["candidate_digest"] != candidate["candidate_digest"]:
        raise OperationalWeaveViolation("need_candidate_digest_mismatch")
    if context_need["binding_digest"] != authority_binding["binding_digest"]:
        raise OperationalWeaveViolation("need_binding_digest_mismatch")
    if context_need["assembled_at"] != assembled_at:
        raise OperationalWeaveViolation("need_assembly_time_mismatch")

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
    required_sources = _intersection(
        candidate["required_source_classes"],
        authority_binding["allowed_required_source_classes"],
    )
    fields = _intersection(
        candidate["requested_fields"], authority_binding["allowed_fields"]
    )
    locations = _intersection(
        candidate["requested_location_refs"],
        authority_binding["allowed_location_refs"],
    )
    requested_start, requested_end = _window(candidate["requested_time_window"])
    policy_start, policy_end = _window(authority_binding["authorized_time_window"])
    effective_start, effective_end = max(requested_start, policy_start), min(
        requested_end, policy_end
    )
    maximum_frames = min(
        candidate["maximum_frames"], authority_binding["maximum_frames"]
    )
    maximum_items_per_frame = min(
        candidate["maximum_items_per_frame"],
        authority_binding["maximum_items_per_frame"],
    )
    maximum_total_bytes = min(
        candidate["maximum_total_bytes"],
        authority_binding["maximum_total_bytes"],
    )
    freshness_seconds = min(
        candidate["freshness_seconds"], authority_binding["maximum_freshness_seconds"]
    )

    requested_expected_sources = {
        SOURCE_TRIPLES[frame_type][0] for frame_type in frame_types
    }
    mandatory = (
        bureau_allowed,
        purpose_allowed,
        bool(frame_types),
        set(source_classes) == requested_expected_sources,
        set(required_sources).issubset(set(source_classes)),
        bool(locations),
        effective_start < effective_end,
        maximum_frames >= len(frame_types),
        maximum_items_per_frame > 0,
        maximum_total_bytes > 0,
        freshness_seconds > 0,
    )
    if not bureau_allowed:
        reductions.append("BUREAU_NOT_ALLOWED")
    if not purpose_allowed:
        reductions.append("PURPOSE_NOT_ALLOWED")
    if frame_types != candidate["requested_frame_types"]:
        reductions.append("FRAME_TYPES_NARROWED")
    if source_classes != candidate["source_classes"]:
        reductions.append("SOURCE_CLASSES_NARROWED")
    if required_sources != candidate["required_source_classes"]:
        reductions.append("REQUIRED_SOURCES_NARROWED")
    if fields != candidate["requested_fields"]:
        reductions.append("FIELDS_NARROWED")
    if locations != candidate["requested_location_refs"]:
        reductions.append("LOCATIONS_NARROWED")
    if (effective_start, effective_end) != (requested_start, requested_end):
        reductions.append("TIME_WINDOW_NARROWED")
    if maximum_frames != candidate["maximum_frames"]:
        reductions.append("FRAME_LIMIT_NARROWED")
    if maximum_items_per_frame != candidate["maximum_items_per_frame"]:
        reductions.append("ITEM_LIMIT_NARROWED")
    if maximum_total_bytes != candidate["maximum_total_bytes"]:
        reductions.append("BYTE_LIMIT_NARROWED")
    if freshness_seconds != candidate["freshness_seconds"]:
        reductions.append("FRESHNESS_NARROWED")

    decision = "ADMIT" if all(mandatory) else "NOT_AVAILABLE"
    if decision == "NOT_AVAILABLE":
        reductions = ["SCOPE_NOT_AVAILABLE"]
        frame_types = []
        source_classes = []
        required_sources = []
        fields = []
        locations = []
        effective_start = effective_end = _instant(assembled_at)
        maximum_frames = maximum_items_per_frame = maximum_total_bytes = 0
        freshness_seconds = 0

    expires_at = min(
        _instant(authority_binding["expires_at"]),
        effective_end if decision == "ADMIT" else _instant(assembled_at),
    )
    grant = {
        "schema_version": SCHEMA_VERSION,
        "grant_id": f"grant:{candidate['need_id']}",
        "decision": decision,
        "need_digest": context_need["need_digest"],
        "binding_digest": authority_binding["binding_digest"],
        "session_binding_digest": authority_binding["session_binding_digest"],
        "requesting_bureau": bureau if bureau_allowed else "NOT_AVAILABLE",
        "purpose_code": purpose if purpose_allowed else "NOT_AVAILABLE",
        "allowed_frame_types": frame_types,
        "allowed_source_classes": source_classes,
        "required_source_classes": required_sources,
        "allowed_fields": fields,
        "allowed_location_refs": locations,
        "effective_time_window": {
            "starts_at": _z(effective_start),
            "ends_at": _z(effective_end),
        },
        "maximum_frames": maximum_frames,
        "maximum_items_per_frame": maximum_items_per_frame,
        "maximum_total_bytes": maximum_total_bytes,
        "freshness_seconds": freshness_seconds,
        "scope_reduction_codes": reductions,
        "issued_at": assembled_at,
        "expires_at": _z(expires_at),
        "read_only": True,
        "command_authority": False,
        "provider_authority": False,
    }
    return seal(grant, "grant_digest")


def _validate_source_envelope(
    envelope: dict[str, Any],
    *,
    binding: dict[str, Any],
    grant: dict[str, Any],
    assembled_at: str,
) -> None:
    verify_seal(envelope, "source_digest")
    frame_type = envelope["frame_type"]
    if frame_type not in SOURCE_TRIPLES:
        raise OperationalWeaveViolation("source_frame_type_unknown")
    expected_source, expected_contract = SOURCE_TRIPLES[frame_type]
    if (
        envelope["source_class"] != expected_source
        or envelope["source_contract_id"] != expected_contract
    ):
        raise OperationalWeaveViolation("source_contract_pairing_invalid")
    if frame_type not in grant["allowed_frame_types"]:
        raise OperationalWeaveViolation("source_frame_not_granted")
    if envelope["source_class"] not in grant["allowed_source_classes"]:
        raise OperationalWeaveViolation("source_class_not_granted")
    if envelope["practice_id"] != binding["practice_id"]:
        raise OperationalWeaveViolation("source_practice_mismatch")
    if envelope["session_binding_digest"] != grant["session_binding_digest"]:
        raise OperationalWeaveViolation("source_session_mismatch")
    if not set(envelope["location_refs"]).issubset(
        set(grant["allowed_location_refs"])
    ):
        raise OperationalWeaveViolation("source_location_not_granted")
    if envelope["evidence_label"] != EVIDENCE_LABEL:
        raise OperationalWeaveViolation("source_evidence_label_invalid")
    if envelope["data_class"] != DATA_CLASS:
        raise OperationalWeaveViolation("source_data_class_invalid")
    if (
        envelope["read_only"] is not True
        or envelope["command_authority"] is not False
        or envelope["provider_authority"] is not False
    ):
        raise OperationalWeaveViolation("source_authority_ceiling_invalid")
    if envelope["supersession_state"] != "CURRENT":
        raise OperationalWeaveViolation("source_superseded")
    now = _instant(assembled_at)
    observed = _instant(envelope["observed_at"])
    expires = _instant(envelope["expires_at"])
    start, end = _window(grant["effective_time_window"])
    if observed > now:
        raise OperationalWeaveViolation("source_observed_in_future")
    if not start <= observed < end:
        raise OperationalWeaveViolation("source_outside_grant_window")
    if now >= expires:
        raise OperationalWeaveViolation("source_expired")
    if (now - observed).total_seconds() > grant["freshness_seconds"]:
        raise OperationalWeaveViolation("source_stale")


def _project_diary(payload: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    appointments = []
    for item in payload["appointments"]:
        projected: dict[str, Any] = {"appointment_ref": item["appointment_ref"]}
        if "diary_practitioner_ref" in fields:
            projected["practitioner_ref"] = item["practitioner_ref"]
        if "diary_time" in fields:
            projected["starts_at"] = item["starts_at"]
            projected["ends_at"] = item["ends_at"]
        if "diary_status" in fields:
            projected["status"] = item["status"]
        appointments.append(projected)
    return {
        "diary_date": payload["diary_date"],
        "location_ref": payload["location_ref"],
        "context_revision": payload["context_revision"],
        "appointments": appointments,
    }


def _project_waiting(payload: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    entries = []
    for item in payload["entries"]:
        projected: dict[str, Any] = {"appointment_ref": item["appointment_ref"]}
        if "waiting_practitioner_ref" in fields:
            projected["practitioner_ref"] = item["practitioner_ref"]
        if "waiting_status" in fields:
            projected["status"] = item["status"]
        if "waiting_elapsed_minutes" in fields:
            projected["elapsed_wait_minutes"] = item["elapsed_wait_minutes"]
        if "waiting_threshold_code" in fields:
            projected["threshold_code"] = item["threshold_code"]
        entries.append(projected)
    return {
        "location_ref": payload["location_ref"],
        "context_revision": payload["context_revision"],
        "entries": entries,
    }


def _project_directory(payload: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    practitioners = []
    for item in payload["practitioners"]:
        projected: dict[str, Any] = {
            "practitioner_ref": item["practitioner_ref"],
            "active": item["active"],
        }
        if "directory_display_label" in fields:
            projected["display_label"] = item["display_label"]
        if "directory_role_label" in fields:
            projected["role_label"] = item["role_label"]
        if "directory_default_location_ref" in fields:
            projected["default_location_ref"] = item["default_location_ref"]
        practitioners.append(projected)
    return {
        "directory_revision": payload["directory_revision"],
        "active_only": payload["active_only"],
        "practitioners": practitioners,
    }


def _project_session(payload: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    projected: dict[str, Any] = {
        "session_generation": payload["session_generation"],
        "request_revision": payload["request_revision"],
        "supersession_state": payload["supersession_state"],
    }
    if "session_visible_diary" in fields:
        projected["visible_diary_date"] = payload["visible_diary_date"]
        projected["visible_location_ref"] = payload["visible_location_ref"]
    if "session_active_practitioner_ref" in fields:
        projected["active_practitioner_ref"] = payload["active_practitioner_ref"]
    if "session_focus_appointment_ref" in fields:
        projected["focus_appointment_ref"] = payload["focus_appointment_ref"]
    if "session_proposal_state" in fields:
        projected["proposal_state"] = payload["proposal_state"]
    return projected


PROJECTORS = {
    "current_diary_projection": _project_diary,
    "current_waiting_room_projection": _project_waiting,
    "active_practitioner_directory": _project_directory,
    "private_application_session_state": _project_session,
}


def _cross_source_coherence(envelopes: dict[str, dict[str, Any]]) -> list[str]:
    diary = envelopes["current_diary_projection"]["payload"]
    waiting = envelopes["current_waiting_room_projection"]["payload"]
    directory = envelopes["active_practitioner_directory"]["payload"]
    session = envelopes["private_application_session_state"]["payload"]
    checks: list[str] = []

    if waiting["location_ref"] != diary["location_ref"]:
        raise OperationalWeaveViolation("waiting_diary_location_mismatch")
    checks.append("WAITING_DIARY_LOCATION_MATCH")

    diary_appointments = {item["appointment_ref"] for item in diary["appointments"]}
    waiting_appointments = {item["appointment_ref"] for item in waiting["entries"]}
    if not waiting_appointments.issubset(diary_appointments):
        raise OperationalWeaveViolation("waiting_appointment_not_in_diary")
    checks.append("WAITING_APPOINTMENTS_RESOLVE_TO_DIARY")

    active_practitioners = {
        item["practitioner_ref"]
        for item in directory["practitioners"]
        if item["active"] is True
    }
    referenced_practitioners = {
        item["practitioner_ref"] for item in diary["appointments"]
    } | {item["practitioner_ref"] for item in waiting["entries"]}
    if session["active_practitioner_ref"] is not None:
        referenced_practitioners.add(session["active_practitioner_ref"])
    if not referenced_practitioners.issubset(active_practitioners):
        raise OperationalWeaveViolation("practitioner_not_in_active_directory")
    checks.append("PRACTITIONERS_RESOLVE_TO_ACTIVE_DIRECTORY")

    if (
        session["visible_diary_date"] != diary["diary_date"]
        or session["visible_location_ref"] != diary["location_ref"]
    ):
        raise OperationalWeaveViolation("session_visible_diary_mismatch")
    checks.append("SESSION_VISIBLE_DIARY_MATCH")

    focus = session["focus_appointment_ref"]
    if focus is not None and focus not in diary_appointments:
        raise OperationalWeaveViolation("session_focus_not_in_diary")
    checks.append("SESSION_FOCUS_RESOLVES_TO_DIARY")
    return checks


def assemble_current_operational_weave(
    candidate: dict[str, Any],
    context_need: dict[str, Any],
    authority_binding: dict[str, Any],
    scope_grant: dict[str, Any],
    source_envelopes: list[dict[str, Any]],
    *,
    assembled_at: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    verify_seal(candidate, "candidate_digest")
    verify_seal(context_need, "need_digest")
    verify_seal(authority_binding, "binding_digest")
    verify_seal(scope_grant, "grant_digest")
    if scope_grant["decision"] != "ADMIT":
        raise OperationalWeaveViolation("scope_not_available")
    if scope_grant["need_digest"] != context_need["need_digest"]:
        raise OperationalWeaveViolation("grant_need_digest_mismatch")
    if scope_grant["binding_digest"] != authority_binding["binding_digest"]:
        raise OperationalWeaveViolation("grant_binding_digest_mismatch")
    if assembled_at != context_need["assembled_at"]:
        raise OperationalWeaveViolation("assembly_time_mismatch")

    by_frame: dict[str, dict[str, Any]] = {}
    for envelope in source_envelopes:
        _validate_source_envelope(
            envelope,
            binding=authority_binding,
            grant=scope_grant,
            assembled_at=assembled_at,
        )
        if envelope["frame_type"] in by_frame:
            raise OperationalWeaveViolation("duplicate_source_frame")
        by_frame[envelope["frame_type"]] = envelope

    supplied_sources = {item["source_class"] for item in source_envelopes}
    if not set(scope_grant["required_source_classes"]).issubset(supplied_sources):
        raise OperationalWeaveViolation("required_source_missing")
    if not set(by_frame).issubset(set(scope_grant["allowed_frame_types"])):
        raise OperationalWeaveViolation("unexpected_source_frame")
    missing_required_frames = {
        frame_type
        for frame_type in scope_grant["allowed_frame_types"]
        if SOURCE_TRIPLES[frame_type][0] in scope_grant["required_source_classes"]
        and frame_type not in by_frame
    }
    if missing_required_frames:
        raise OperationalWeaveViolation("required_frame_missing")
    if len(by_frame) > scope_grant["maximum_frames"]:
        raise OperationalWeaveViolation("frame_limit_exceeded")

    required_for_coherence = set(FRAME_ORDER)
    if required_for_coherence.issubset(by_frame):
        coherence_checks = _cross_source_coherence(by_frame)
    else:
        raise OperationalWeaveViolation("coherence_source_missing")

    allowed_fields = set(scope_grant["allowed_fields"])
    frames: list[dict[str, Any]] = []
    for frame_type in FRAME_ORDER:
        envelope = by_frame.get(frame_type)
        if envelope is None:
            continue
        payload = envelope["payload"]
        items = payload.get("appointments", payload.get("entries", payload.get("practitioners", [])))
        if len(items) > scope_grant["maximum_items_per_frame"]:
            raise OperationalWeaveViolation("source_item_limit_exceeded")
        projected = PROJECTORS[frame_type](payload, allowed_fields)
        frame = {
            "schema_version": SCHEMA_VERSION,
            "frame_id": f"frame:{envelope['source_envelope_id']}",
            "frame_type": frame_type,
            "source_class": envelope["source_class"],
            "source_contract_id": envelope["source_contract_id"],
            "practice_binding_digest": canonical_sha256(
                {"practice_id": authority_binding["practice_id"]}
            ),
            "session_binding_digest": scope_grant["session_binding_digest"],
            "location_refs": envelope["location_refs"],
            "content": projected,
            "observed_at": envelope["observed_at"],
            "assembled_at": assembled_at,
            "expires_at": _z(
                min(
                    _instant(envelope["expires_at"]),
                    _instant(scope_grant["expires_at"]),
                    _instant(authority_binding["expires_at"]),
                )
            ),
            "source_revision": envelope["source_revision"],
            "source_digest": envelope["source_digest"],
            "disclosure_fields": scope_grant["allowed_fields"],
            "evidence_label": EVIDENCE_LABEL,
            "data_class": DATA_CLASS,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
            "supersession_state": "CURRENT",
        }
        frame["content_digest"] = canonical_sha256(projected)
        frames.append(seal(frame, "frame_digest"))

    omission_codes = [
        f"OPTIONAL_SOURCE_OMITTED:{SOURCE_TRIPLES[frame_type][0]}"
        for frame_type in scope_grant["allowed_frame_types"]
        if frame_type not in by_frame
    ]
    source_trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "need_digest": context_need["need_digest"],
            "grant_digest": scope_grant["grant_digest"],
            "source_envelope_ids": [
                by_frame[frame_type]["source_envelope_id"]
                for frame_type in FRAME_ORDER
                if frame_type in by_frame
            ],
            "source_digests": [frame["source_digest"] for frame in frames],
            "coherence_check_codes": coherence_checks,
            "omission_codes": omission_codes,
        },
        "source_trace_digest",
    )
    expires_at = min(_instant(frame["expires_at"]) for frame in frames)
    frame_set = {
        "schema_version": SCHEMA_VERSION,
        "frame_set_id": f"operational-weave:{candidate['need_id']}",
        "need_digest": context_need["need_digest"],
        "grant_digest": scope_grant["grant_digest"],
        "binding_digest": authority_binding["binding_digest"],
        "source_trace_digest": source_trace["source_trace_digest"],
        "frames": frames,
        "omission_codes": omission_codes,
        "ambiguity_state": "NONE",
        "assembled_at": assembled_at,
        "expires_at": _z(expires_at),
        "maximum_disclosure_bytes": scope_grant["maximum_total_bytes"],
        "read_only": True,
        "command_authority": False,
        "provider_authority": False,
    }
    frame_set = seal(frame_set, "frame_set_digest")
    if len(canonical_json(frame_set).encode("utf-8")) > scope_grant[
        "maximum_total_bytes"
    ]:
        raise OperationalWeaveViolation("frame_set_byte_limit_exceeded")
    weave_trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "need_digest": context_need["need_digest"],
            "grant_digest": scope_grant["grant_digest"],
            "source_trace_digest": source_trace["source_trace_digest"],
            "released_frame_ids": [frame["frame_id"] for frame in frames],
            "released_frame_digests": [frame["frame_digest"] for frame in frames],
            "frame_set_digest": frame_set["frame_set_digest"],
            "read_only": True,
            "command_authority": False,
        },
        "weave_trace_digest",
    )
    return frame_set, source_trace, weave_trace


def proofread_current_operational_weave(
    candidate: dict[str, Any],
    context_need: dict[str, Any],
    authority_binding: dict[str, Any],
    scope_grant: dict[str, Any],
    source_envelopes: list[dict[str, Any]],
    frame_set: dict[str, Any],
    source_trace: dict[str, Any],
    weave_trace: dict[str, Any],
    *,
    assembled_at: str,
    proofread_at: str | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    checked_at = proofread_at or assembled_at
    try:
        verify_seal(candidate, "candidate_digest")
        verify_seal(context_need, "need_digest")
        verify_seal(authority_binding, "binding_digest")
        verify_seal(scope_grant, "grant_digest")
        verify_seal(frame_set, "frame_set_digest")
        verify_seal(source_trace, "source_trace_digest")
        verify_seal(weave_trace, "weave_trace_digest")
        expected_need = build_operational_context_need(
            candidate,
            authority_binding,
            assembled_at=assembled_at,
        )
        if context_need != expected_need:
            reasons.append("CONTEXT_NEED_RECOMPUTATION_MISMATCH")
        expected_grant = intersect_operational_scope(
            candidate,
            expected_need,
            authority_binding,
            assembled_at=assembled_at,
        )
        if scope_grant != expected_grant:
            reasons.append("SCOPE_GRANT_RECOMPUTATION_MISMATCH")
        expected_set, expected_source_trace, expected_weave_trace = (
            assemble_current_operational_weave(
                candidate,
                expected_need,
                authority_binding,
                expected_grant,
                source_envelopes,
                assembled_at=assembled_at,
            )
        )
        if frame_set != expected_set:
            reasons.append("FRAME_SET_RECOMPUTATION_MISMATCH")
        if source_trace != expected_source_trace:
            reasons.append("SOURCE_TRACE_RECOMPUTATION_MISMATCH")
        if weave_trace != expected_weave_trace:
            reasons.append("WEAVE_TRACE_RECOMPUTATION_MISMATCH")
        if _instant(checked_at) < _instant(assembled_at):
            reasons.append("PROOFREAD_BEFORE_ASSEMBLY")
        if _instant(checked_at) >= _instant(frame_set["expires_at"]):
            reasons.append("FRAME_SET_EXPIRED")
        if frame_set["source_trace_digest"] != source_trace["source_trace_digest"]:
            reasons.append("FRAME_SET_SOURCE_TRACE_MISMATCH")
        if weave_trace["frame_set_digest"] != frame_set["frame_set_digest"]:
            reasons.append("WEAVE_FRAME_SET_MISMATCH")
        if (
            frame_set["read_only"] is not True
            or frame_set["command_authority"] is not False
            or frame_set["provider_authority"] is not False
        ):
            reasons.append("FRAME_SET_AUTHORITY_CEILING_INVALID")
    except (ContractViolation, KeyError, TypeError, ValueError) as error:
        reasons.append(f"PACKET_INVALID:{type(error).__name__}")
    reasons = sorted(set(reasons))
    trace = {
        "schema_version": SCHEMA_VERSION,
        "need_digest": context_need.get("need_digest", "invalid"),
        "grant_digest": scope_grant.get("grant_digest", "invalid"),
        "source_trace_digest": source_trace.get("source_trace_digest", "invalid"),
        "weave_trace_digest": weave_trace.get("weave_trace_digest", "invalid"),
        "frame_set_digest": frame_set.get("frame_set_digest", "invalid"),
        "checked_at": checked_at,
        "reason_codes": reasons,
        "release_decision": "RELEASE" if not reasons else "BLOCK",
    }
    return seal(trace, "proofreader_trace_digest")


def build_authored_synthetic_packet() -> dict[str, Any]:
    assembled_at = "2026-08-06T03:00:00Z"
    location = "synthetic:location:brisbane-one"
    practitioner_one = "synthetic:practitioner:one"
    practitioner_two = "synthetic:practitioner:two"
    appointment_one = "synthetic:appointment:one"
    appointment_two = "synthetic:appointment:two"
    frame_types = list(FRAME_ORDER)
    source_classes = [SOURCE_TRIPLES[item][0] for item in frame_types]
    requested_fields = sorted(REQUESTABLE_FIELDS)
    candidate = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "need_id": "synthetic:need:current-operational-weave-001",
            "requesting_bureau": "RAYLEEN",
            "purpose_code": "CURRENT_OPERATIONAL_AWARENESS",
            "requested_frame_types": frame_types,
            "source_classes": source_classes,
            "required_source_classes": source_classes,
            "requested_fields": requested_fields,
            "requested_location_refs": [location],
            "requested_time_window": {
                "starts_at": "2026-08-06T02:55:00Z",
                "ends_at": "2026-08-06T03:05:00Z",
            },
            "maximum_frames": 4,
            "maximum_items_per_frame": 8,
            "maximum_total_bytes": 24000,
            "freshness_seconds": 180,
            "issued_at": "2026-08-06T02:59:50Z",
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "candidate_digest",
    )
    binding_base = {
        "schema_version": SCHEMA_VERSION,
        "binding_id": "synthetic:binding:current-operational-weave-001",
        "principal_ref": "synthetic:principal:reception-one",
        "roles": ["RECEPTIONIST"],
        "practice_id": "synthetic:practice:one",
        "session_id": "synthetic:session:one",
        "session_generation": 7,
        "allowed_bureaus": ["BERNIE", "RAYLEEN"],
        "allowed_purposes": ["CURRENT_OPERATIONAL_AWARENESS"],
        "allowed_frame_types": frame_types,
        "allowed_source_classes": source_classes,
        "allowed_required_source_classes": source_classes,
        "allowed_fields": requested_fields,
        "allowed_location_refs": [location],
        "authorized_time_window": {
            "starts_at": "2026-08-06T02:58:00Z",
            "ends_at": "2026-08-06T03:04:00Z",
        },
        "maximum_frames": 4,
        "maximum_items_per_frame": 6,
        "maximum_total_bytes": 22000,
        "maximum_freshness_seconds": 120,
        "policy_version": "context-fabric-current-operational-weave.v1",
        "issued_at": "2026-08-06T02:59:00Z",
        "expires_at": "2026-08-06T03:04:00Z",
    }
    binding_base["session_binding_digest"] = _session_binding_digest(binding_base)
    authority_binding = seal(binding_base, "binding_digest")
    context_need = build_operational_context_need(
        candidate, authority_binding, assembled_at=assembled_at
    )
    scope_grant = intersect_operational_scope(
        candidate,
        context_need,
        authority_binding,
        assembled_at=assembled_at,
    )

    common = {
        "schema_version": SCHEMA_VERSION,
        "practice_id": authority_binding["practice_id"],
        "session_binding_digest": authority_binding["session_binding_digest"],
        "location_refs": [location],
        "observed_at": "2026-08-06T02:59:30Z",
        "expires_at": "2026-08-06T03:02:00Z",
        "evidence_label": EVIDENCE_LABEL,
        "data_class": DATA_CLASS,
        "read_only": True,
        "command_authority": False,
        "provider_authority": False,
        "supersession_state": "CURRENT",
    }
    sources = [
        seal(
            {
                **common,
                "source_envelope_id": "synthetic:source:diary-001",
                "frame_type": "current_diary_projection",
                "source_class": "current_diary",
                "source_contract_id": "api_spine.appointment_diary_read.v1",
                "source_revision": "synthetic:diary-revision:11",
                "payload": {
                    "diary_date": "2026-08-06",
                    "location_ref": location,
                    "context_revision": 11,
                    "appointments": [
                        {
                            "appointment_ref": appointment_one,
                            "practitioner_ref": practitioner_one,
                            "starts_at": "2026-08-06T03:10:00Z",
                            "ends_at": "2026-08-06T03:25:00Z",
                            "status": "ARRIVED",
                        },
                        {
                            "appointment_ref": appointment_two,
                            "practitioner_ref": practitioner_two,
                            "starts_at": "2026-08-06T03:20:00Z",
                            "ends_at": "2026-08-06T03:35:00Z",
                            "status": "BOOKED",
                        },
                    ],
                },
            },
            "source_digest",
        ),
        seal(
            {
                **common,
                "source_envelope_id": "synthetic:source:waiting-001",
                "frame_type": "current_waiting_room_projection",
                "source_class": "current_waiting_room",
                "source_contract_id": "emr4.waiting_room_context_frame.v1",
                "source_revision": "synthetic:waiting-revision:7",
                "payload": {
                    "location_ref": location,
                    "context_revision": 7,
                    "entries": [
                        {
                            "appointment_ref": appointment_one,
                            "practitioner_ref": practitioner_one,
                            "status": "ARRIVED",
                            "elapsed_wait_minutes": 10,
                            "threshold_code": "UNDER_15_MINUTES",
                        }
                    ],
                },
            },
            "source_digest",
        ),
        seal(
            {
                **common,
                "source_envelope_id": "synthetic:source:directory-001",
                "frame_type": "active_practitioner_directory",
                "source_class": "practitioner_directory",
                "source_contract_id": "practice-practitioner-directory-read.v1",
                "source_revision": "synthetic:directory-revision:5",
                "payload": {
                    "directory_revision": 5,
                    "active_only": True,
                    "practitioners": [
                        {
                            "practitioner_ref": practitioner_one,
                            "display_label": "Synthetic Dr One",
                            "role_label": "General practitioner",
                            "active": True,
                            "default_location_ref": location,
                        },
                        {
                            "practitioner_ref": practitioner_two,
                            "display_label": "Synthetic Nurse Two",
                            "role_label": "Practice nurse",
                            "active": True,
                            "default_location_ref": location,
                        },
                    ],
                },
            },
            "source_digest",
        ),
        seal(
            {
                **common,
                "source_envelope_id": "synthetic:source:session-001",
                "frame_type": "private_application_session_state",
                "source_class": "private_session_state",
                "source_contract_id": "emr4.native_diary_application_session_state.v1",
                "source_revision": "synthetic:session-revision:19",
                "payload": {
                    "session_generation": 7,
                    "request_revision": 19,
                    "visible_diary_date": "2026-08-06",
                    "visible_location_ref": location,
                    "active_practitioner_ref": practitioner_one,
                    "focus_appointment_ref": appointment_one,
                    "proposal_state": "NONE",
                    "supersession_state": "CURRENT",
                },
            },
            "source_digest",
        ),
    ]
    frame_set, source_trace, weave_trace = assemble_current_operational_weave(
        candidate,
        context_need,
        authority_binding,
        scope_grant,
        sources,
        assembled_at=assembled_at,
    )
    proofreader_trace = proofread_current_operational_weave(
        candidate,
        context_need,
        authority_binding,
        scope_grant,
        sources,
        frame_set,
        source_trace,
        weave_trace,
        assembled_at=assembled_at,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "candidate": candidate,
        "authority_binding": authority_binding,
        "context_need": context_need,
        "scope_grant": scope_grant,
        "source_envelopes": sources,
        "source_trace": source_trace,
        "frame_set": frame_set,
        "weave_trace": weave_trace,
        "proofreader_trace": proofreader_trace,
    }


__all__ = [
    "DATA_CLASS",
    "EVIDENCE_LABEL",
    "FRAME_ORDER",
    "OperationalWeaveViolation",
    "REQUESTABLE_FIELDS",
    "SCHEMA_VERSION",
    "SOURCE_TRIPLES",
    "assemble_current_operational_weave",
    "build_authored_synthetic_packet",
    "build_operational_context_need",
    "intersect_operational_scope",
    "proofread_current_operational_weave",
]
