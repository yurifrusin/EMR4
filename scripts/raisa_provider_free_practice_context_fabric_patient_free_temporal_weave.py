"""Pure patient-free temporal watcher and bitemporal Context Fabric contract."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    ContractViolation,
    canonical_sha256,
    seal,
    verify_seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    build_authored_synthetic_packet,
)


SCHEMA_VERSION = "emr4.practice_context_fabric_patient_free_temporal_weave.v1"
EVIDENCE_LABEL = "provider_free_authored_synthetic_patient_free_temporal_weave"
DATA_CLASS = "authored_synthetic_patient_free_operational_metadata"
HANDLING_POLICY = "REASSEMBLE_AT_BOUNDARY"

EVENT_SCHEMAS = {
    "diary.appointment_rescheduled": "emr4.diary.appointment_rescheduled.v1",
    "diary.waiting_state_changed": "emr4.diary.waiting_state_changed.v1",
    "practice.practitioner_directory_changed": (
        "emr4.practice.practitioner_directory_changed.v1"
    ),
    "session.application_state_changed": "emr4.session.application_state_changed.v1",
}

FRAME_EVENT_FAMILIES = {
    "current_diary_projection": (
        "diary.appointment_rescheduled",
        "diary.waiting_state_changed",
        "practice.practitioner_directory_changed",
    ),
    "current_waiting_room_projection": (
        "diary.appointment_rescheduled",
        "diary.waiting_state_changed",
        "practice.practitioner_directory_changed",
    ),
    "active_practitioner_directory": (
        "practice.practitioner_directory_changed",
    ),
    "private_application_session_state": (
        "diary.appointment_rescheduled",
        "session.application_state_changed",
    ),
}

SIGNAL_KEYS = {
    "schema_version",
    "signal_id",
    "event_type",
    "event_schema_version",
    "commit_state",
    "practice_binding_digest",
    "aggregate_class",
    "aggregate_ref",
    "aggregate_revision",
    "affected_location_refs",
    "affected_practitioner_refs",
    "affected_frame_types",
    "occurred_at",
    "received_at",
    "expires_at",
    "previous_transaction_position",
    "transaction_position",
    "observed_cursor",
    "baseline_established",
    "sensitivity",
    "evidence_label",
    "data_class",
    "read_only",
    "command_authority",
    "signal_digest",
}


class TemporalWeaveViolation(ContractViolation):
    """Raised when temporal context cannot be admitted safely."""


def _instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise TemporalWeaveViolation("invalid_timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TemporalWeaveViolation("timestamp_requires_timezone")
    return parsed.astimezone(timezone.utc)


def _z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _expect_keys(value: dict[str, Any], keys: set[str], code: str) -> None:
    if set(value) != keys:
        raise TemporalWeaveViolation(code)


def _practice_binding_digest(parent: dict[str, Any]) -> str:
    return canonical_sha256(
        {"practice_id": parent["authority_binding"]["practice_id"]}
    )


def _parent_binding(parent: dict[str, Any]) -> dict[str, Any]:
    frame_set = parent["frame_set"]
    verify_seal(frame_set, "frame_set_digest")
    verify_seal(parent["scope_grant"], "grant_digest")
    verify_seal(parent["authority_binding"], "binding_digest")
    verify_seal(parent["source_trace"], "source_trace_digest")
    if parent["proofreader_trace"]["release_decision"] != "RELEASE":
        raise TemporalWeaveViolation("parent_not_released")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "parent_schema_version": parent["schema_version"],
            "parent_frame_set_id": frame_set["frame_set_id"],
            "parent_frame_set_digest": frame_set["frame_set_digest"],
            "parent_frame_set_bytes_digest": canonical_sha256(frame_set),
            "parent_need_digest": frame_set["need_digest"],
            "parent_grant_digest": frame_set["grant_digest"],
            "parent_authority_binding_digest": frame_set["binding_digest"],
            "parent_source_trace_digest": frame_set["source_trace_digest"],
            "practice_binding_digest": _practice_binding_digest(parent),
            "session_binding_digest": parent["authority_binding"][
                "session_binding_digest"
            ],
            "session_generation": parent["authority_binding"]["session_generation"],
            "policy_version": parent["authority_binding"]["policy_version"],
            "assembled_at": frame_set["assembled_at"],
            "expires_at": frame_set["expires_at"],
            "read_only": True,
            "command_authority": False,
        },
        "parent_binding_record_digest",
    )


def _frame_selectors(frame: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    content = frame["content"]
    appointments: set[str] = set()
    practitioners: set[str] = set()
    locations = set(frame["location_refs"])
    for row_name in ("appointments", "entries"):
        for row in content.get(row_name, []):
            if row.get("appointment_ref"):
                appointments.add(row["appointment_ref"])
            if row.get("practitioner_ref"):
                practitioners.add(row["practitioner_ref"])
    for row in content.get("practitioners", []):
        practitioners.add(row["practitioner_ref"])
        if row.get("default_location_ref"):
            locations.add(row["default_location_ref"])
    for field in ("focus_appointment_ref",):
        if content.get(field):
            appointments.add(content[field])
    for field in ("active_practitioner_ref",):
        if content.get(field):
            practitioners.add(content[field])
    if content.get("visible_location_ref"):
        locations.add(content["visible_location_ref"])
    return sorted(appointments), sorted(practitioners), sorted(locations)


def derive_dependency_manifest(
    parent: dict[str, Any], *, issued_at: str = "2026-08-06T03:00:01Z"
) -> dict[str, Any]:
    parent_binding = _parent_binding(parent)
    frame_set = parent["frame_set"]
    dependencies = []
    high_watermarks: dict[str, int] = {}
    for frame in frame_set["frames"]:
        appointments, practitioners, locations = _frame_selectors(frame)
        for appointment_ref in appointments:
            high_watermarks.setdefault(appointment_ref, 11)
        dependencies.append(
            seal(
                {
                    "schema_version": SCHEMA_VERSION,
                    "dependency_id": f"synthetic:dependency:{frame['frame_type']}",
                    "frame_id": frame["frame_id"],
                    "frame_digest": frame["frame_digest"],
                    "frame_type": frame["frame_type"],
                    "source_class": frame["source_class"],
                    "source_contract_id": frame["source_contract_id"],
                    "source_revision": frame["source_revision"],
                    "source_digest": frame["source_digest"],
                    "appointment_refs": appointments,
                    "practitioner_refs": practitioners,
                    "location_refs": locations,
                    "event_types": list(FRAME_EVENT_FAMILIES[frame["frame_type"]]),
                    "expires_at": frame["expires_at"],
                    "read_only": True,
                    "command_authority": False,
                },
                "dependency_digest",
            )
        )
    high_watermarks.setdefault("synthetic:directory:active", 5)
    high_watermarks.setdefault("synthetic:session:active", 19)
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "manifest_id": "synthetic:temporal-manifest:001",
            "parent_frame_set_id": frame_set["frame_set_id"],
            "parent_frame_set_digest": frame_set["frame_set_digest"],
            "parent_need_digest": frame_set["need_digest"],
            "parent_grant_digest": frame_set["grant_digest"],
            "parent_binding_digest": frame_set["binding_digest"],
            "parent_source_trace_digest": frame_set["source_trace_digest"],
            "practice_binding_digest": parent_binding["practice_binding_digest"],
            "session_binding_digest": parent_binding["session_binding_digest"],
            "session_generation": parent_binding["session_generation"],
            "policy_version": parent_binding["policy_version"],
            "dependencies": dependencies,
            "accepted_event_types": sorted(
                {event for events in FRAME_EVENT_FAMILIES.values() for event in events}
            ),
            "aggregate_high_watermarks": [
                {"aggregate_ref": ref, "aggregate_revision": revision}
                for ref, revision in sorted(high_watermarks.items())
            ],
            "starting_checkpoint": {
                "stream_id": "synthetic:practice-event-stream:001",
                "transaction_position": 100,
                "observed_cursor": "synthetic:cursor:100",
                "baseline_established": True,
            },
            "issued_at": issued_at,
            "expires_at": frame_set["expires_at"],
            "handling_policy": HANDLING_POLICY,
            "read_only": True,
            "command_authority": False,
        },
        "manifest_digest",
    )


def derive_watch_lease(
    parent: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    verify_seal(manifest, "manifest_digest")
    binding = _parent_binding(parent)
    expected = derive_dependency_manifest(parent, issued_at=manifest["issued_at"])
    if expected != manifest:
        raise TemporalWeaveViolation("manifest_not_parent_derived")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "lease_id": "synthetic:temporal-watch-lease:001",
            "manifest_id": manifest["manifest_id"],
            "manifest_digest": manifest["manifest_digest"],
            "parent_frame_set_digest": manifest["parent_frame_set_digest"],
            "parent_grant_digest": manifest["parent_grant_digest"],
            "parent_binding_digest": manifest["parent_binding_digest"],
            "practice_binding_digest": manifest["practice_binding_digest"],
            "session_binding_digest": manifest["session_binding_digest"],
            "session_generation": manifest["session_generation"],
            "policy_version": manifest["policy_version"],
            "accepted_event_types": manifest["accepted_event_types"],
            "allowed_dependency_ids": [
                item["dependency_id"] for item in manifest["dependencies"]
            ],
            "allowed_location_refs": sorted(
                {
                    ref
                    for dependency in manifest["dependencies"]
                    for ref in dependency["location_refs"]
                }
            ),
            "starting_checkpoint": manifest["starting_checkpoint"],
            "maximum_signals": 20,
            "sensitivity_ceiling": "INTERNAL_OPERATIONAL",
            "handling_policy": HANDLING_POLICY,
            "issued_at": manifest["issued_at"],
            "expires_at": min(manifest["expires_at"], binding["expires_at"]),
            "revoked": False,
            "execution_enabled": False,
            "returns_data": False,
            "read_only": True,
            "command_authority": False,
        },
        "lease_digest",
    )


def make_signal(
    *,
    signal_id: str,
    event_type: str,
    aggregate_ref: str,
    aggregate_revision: int,
    previous_transaction_position: int,
    transaction_position: int,
    location_refs: list[str],
    practitioner_refs: list[str] | None = None,
    frame_types: list[str] | None = None,
    practice_binding_digest: str,
    occurred_at: str,
    received_at: str,
    expires_at: str = "2026-08-06T04:00:00Z",
    baseline_established: bool = False,
) -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "signal_id": signal_id,
            "event_type": event_type,
            "event_schema_version": EVENT_SCHEMAS[event_type],
            "commit_state": "COMMITTED",
            "practice_binding_digest": practice_binding_digest,
            "aggregate_class": "APPOINTMENT",
            "aggregate_ref": aggregate_ref,
            "aggregate_revision": aggregate_revision,
            "affected_location_refs": sorted(location_refs),
            "affected_practitioner_refs": sorted(practitioner_refs or []),
            "affected_frame_types": sorted(frame_types or []),
            "occurred_at": occurred_at,
            "received_at": received_at,
            "expires_at": expires_at,
            "previous_transaction_position": previous_transaction_position,
            "transaction_position": transaction_position,
            "observed_cursor": f"synthetic:cursor:{transaction_position}",
            "baseline_established": baseline_established,
            "sensitivity": "INTERNAL_OPERATIONAL",
            "evidence_label": EVIDENCE_LABEL,
            "data_class": DATA_CLASS,
            "read_only": True,
            "command_authority": False,
        },
        "signal_digest",
    )


def _intersecting_dependencies(
    signal: dict[str, Any], manifest: dict[str, Any]
) -> list[dict[str, Any]]:
    matches = []
    signal_locations = set(signal["affected_location_refs"])
    signal_practitioners = set(signal["affected_practitioner_refs"])
    signal_frames = set(signal["affected_frame_types"])
    for dependency in manifest["dependencies"]:
        if signal["event_type"] not in dependency["event_types"]:
            continue
        if signal_locations and not signal_locations.intersection(
            dependency["location_refs"]
        ):
            continue
        aggregate_match = signal["aggregate_ref"] in dependency["appointment_refs"]
        practitioner_match = bool(
            signal_practitioners.intersection(dependency["practitioner_refs"])
        )
        frame_match = dependency["frame_type"] in signal_frames
        if aggregate_match or practitioner_match or frame_match:
            matches.append(dependency)
    return matches


def _decision(
    signal: dict[str, Any], decision: str, reasons: list[str], affected: list[dict]
) -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "signal_id": signal["signal_id"],
            "signal_digest": signal["signal_digest"],
            "decision": decision,
            "reason_codes": sorted(set(reasons)),
            "affected_dependency_ids": sorted(
                item["dependency_id"] for item in affected
            ),
            "affected_frame_ids": sorted(item["frame_id"] for item in affected),
            "replacement_context_included": False,
            "command_authority": False,
        },
        "decision_digest",
    )


def process_signals(
    parent: dict[str, Any],
    manifest: dict[str, Any],
    lease: dict[str, Any],
    signals: list[dict[str, Any]],
    *,
    observed_at: str = "2026-08-06T03:01:00Z",
    current_session_generation: int | None = None,
) -> tuple[
    dict[str, Any],
    dict[str, Any] | None,
    dict[str, Any],
    list[dict],
    list[dict],
    dict,
]:
    now = _instant(observed_at)
    parent_binding = _parent_binding(parent)
    expected_manifest = derive_dependency_manifest(parent, issued_at=manifest["issued_at"])
    if manifest != expected_manifest:
        raise TemporalWeaveViolation("manifest_not_parent_derived")
    expected_lease = derive_watch_lease(parent, manifest)
    if lease != expected_lease:
        raise TemporalWeaveViolation("lease_not_manifest_derived")
    verify_seal(lease, "lease_digest")
    before_parent = canonical_sha256(parent["frame_set"])
    current_generation = (
        parent_binding["session_generation"]
        if current_session_generation is None
        else current_session_generation
    )
    checkpoint = deepcopy(manifest["starting_checkpoint"])
    seen: set[str] = set()
    high_watermarks = {
        item["aggregate_ref"]: item["aggregate_revision"]
        for item in manifest["aggregate_high_watermarks"]
    }
    state_code = "CURRENT"
    cause_digests: list[str] = []
    required_dependency_ids: set[str] = set()
    decisions = []
    transitions = []

    if len(signals) > lease["maximum_signals"]:
        raise TemporalWeaveViolation("signal_limit_exceeded")

    for signal in signals:
        _expect_keys(signal, SIGNAL_KEYS, "signal_shape_invalid")
        verify_seal(signal, "signal_digest")
        affected: list[dict] = []
        reason: list[str] = []
        decision_code: str

        if (
            lease["revoked"]
            or current_generation != lease["session_generation"]
            or lease["session_binding_digest"] != manifest["session_binding_digest"]
        ):
            state_code = "REVOKED"
            decision_code, reason = "REVOKED", ["AUTHORITY_OR_SESSION_REVOKED"]
        elif now >= _instant(lease["expires_at"]) or now >= _instant(
            parent_binding["expires_at"]
        ):
            state_code = "EXPIRED"
            decision_code, reason = "EXPIRED", ["LEASE_OR_FRAME_SET_EXPIRED"]
        elif signal["practice_binding_digest"] != lease["practice_binding_digest"]:
            decision_code, reason = "SUPPRESSED", ["FOREIGN_PRACTICE"]
        elif (
            signal["commit_state"] != "COMMITTED"
            or signal["event_type"] not in lease["accepted_event_types"]
            or EVENT_SCHEMAS.get(signal["event_type"])
            != signal["event_schema_version"]
            or signal["sensitivity"] != lease["sensitivity_ceiling"]
        ):
            decision_code, reason = "SUPPRESSED", ["EVENT_NOT_ADMITTED"]
        elif now >= _instant(signal["expires_at"]):
            decision_code, reason = "SUPPRESSED", ["SIGNAL_EXPIRED"]
        elif signal["signal_id"] in seen:
            decision_code, reason = "SUPPRESSED", ["EXACT_REPLAY"]
        elif signal["baseline_established"] and checkpoint["transaction_position"] > (
            manifest["starting_checkpoint"]["transaction_position"]
        ):
            state_code = "REASSEMBLY_REQUIRED"
            decision_code, reason = "CURSOR_GAP", ["NONINITIAL_REBASELINE"]
        elif signal["previous_transaction_position"] != checkpoint[
            "transaction_position"
        ]:
            if (
                signal["transaction_position"] <= checkpoint["transaction_position"]
                and signal["aggregate_revision"]
                > high_watermarks.get(signal["aggregate_ref"], 0)
            ):
                decision_code, reason = "ORDERING_UNCERTAIN", [
                    "LATE_NEWER_AGGREGATE_REVISION"
                ]
            else:
                decision_code, reason = "CURSOR_GAP", ["CHECKPOINT_MISMATCH"]
            state_code = "REASSEMBLY_REQUIRED"
        elif signal["transaction_position"] != checkpoint["transaction_position"] + 1:
            state_code = "REASSEMBLY_REQUIRED"
            decision_code, reason = "CURSOR_GAP", ["TRANSACTION_POSITION_GAP"]
        else:
            prior_revision = high_watermarks.get(signal["aggregate_ref"], 0)
            if signal["aggregate_revision"] <= prior_revision:
                decision_code, reason = "SUPPRESSED", ["REVISION_NOT_NEWER"]
            elif prior_revision and signal["aggregate_revision"] > prior_revision + 1:
                state_code = "REASSEMBLY_REQUIRED"
                decision_code, reason = "REVISION_GAP", ["AGGREGATE_REVISION_GAP"]
            else:
                affected = _intersecting_dependencies(signal, manifest)
                if not affected:
                    decision_code, reason = "IRRELEVANT", ["NO_DEPENDENCY_INTERSECTION"]
                elif state_code == "CURRENT":
                    state_code = "REASSEMBLY_REQUIRED"
                    decision_code, reason = "REASSEMBLY_REQUIRED", [
                        "DEPENDENCY_MAY_BE_STALE"
                    ]
                else:
                    decision_code, reason = "COALESCED", [
                        "REASSEMBLY_ALREADY_REQUIRED"
                    ]
                high_watermarks[signal["aggregate_ref"]] = signal[
                    "aggregate_revision"
                ]

            checkpoint = {
                "stream_id": checkpoint["stream_id"],
                "transaction_position": signal["transaction_position"],
                "observed_cursor": signal["observed_cursor"],
                "baseline_established": signal["baseline_established"],
            }
            seen.add(signal["signal_id"])

        if decision_code in {
            "REASSEMBLY_REQUIRED",
            "COALESCED",
            "CURSOR_GAP",
            "REVISION_GAP",
            "ORDERING_UNCERTAIN",
        }:
            cause_digests.append(signal["signal_digest"])
            if affected:
                required_dependency_ids.update(
                    item["dependency_id"] for item in affected
                )
            else:
                required_dependency_ids.update(lease["allowed_dependency_ids"])
        decision_record = _decision(signal, decision_code, reason, affected)
        decisions.append(decision_record)
        transitions.append(
            seal(
                {
                    "schema_version": SCHEMA_VERSION,
                    "signal_digest": signal["signal_digest"],
                    "observed_cursor": {
                        "stream_id": checkpoint["stream_id"],
                        "previous_transaction_position": signal[
                            "previous_transaction_position"
                        ],
                        "transaction_position": signal["transaction_position"],
                        "cursor": signal["observed_cursor"],
                        "baseline_established": signal["baseline_established"],
                    },
                    "decision_digest": decision_record["decision_digest"],
                    "decision": decision_code,
                    "state_after": state_code,
                    "next_checkpoint": deepcopy(checkpoint),
                    "reassembly_requirement_emitted": decision_code
                    in {
                        "REASSEMBLY_REQUIRED",
                        "CURSOR_GAP",
                        "REVISION_GAP",
                        "ORDERING_UNCERTAIN",
                    },
                    "fresh_read_executed": False,
                    "command_authority": False,
                },
                "transition_digest",
            )
        )

    checkpoint_record = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "stream_id": checkpoint["stream_id"],
            "transaction_position": checkpoint["transaction_position"],
            "observed_cursor": checkpoint["observed_cursor"],
            "baseline_established": checkpoint["baseline_established"],
            "seen_signal_ids": sorted(seen),
            "aggregate_high_watermarks": [
                {"aggregate_ref": ref, "aggregate_revision": revision}
                for ref, revision in sorted(high_watermarks.items())
            ],
            "classified_at": observed_at,
        },
        "checkpoint_digest",
    )

    state = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "parent_frame_set_id": manifest["parent_frame_set_id"],
            "parent_frame_set_digest": manifest["parent_frame_set_digest"],
            "state": state_code,
            "cause_signal_digests": cause_digests,
            "usable_for_new_reasoning": state_code == "CURRENT",
            "frames_mutated": False,
            "recorded_at": observed_at,
        },
        "state_digest",
    )

    requirement = None
    if state_code == "REASSEMBLY_REQUIRED":
        requirement = seal(
            {
                "schema_version": SCHEMA_VERSION,
                "requirement_id": "synthetic:reassembly-requirement:001",
                "superseded_frame_set_id": manifest["parent_frame_set_id"],
                "superseded_frame_set_digest": manifest["parent_frame_set_digest"],
                "manifest_digest": manifest["manifest_digest"],
                "lease_digest": lease["lease_digest"],
                "grant_digest": manifest["parent_grant_digest"],
                "binding_digest": manifest["parent_binding_digest"],
                "session_generation": manifest["session_generation"],
                "request_revision": 1,
                "required_dependency_ids": sorted(required_dependency_ids),
                "cause_signal_digests": cause_digests,
                "issued_at": observed_at,
                "expires_at": lease["expires_at"],
                "execution_enabled": False,
                "returns_data": False,
                "read_only": True,
                "command_authority": False,
            },
            "requirement_digest",
        )

    after_parent = canonical_sha256(parent["frame_set"])
    trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "parent_frame_set_digest": manifest["parent_frame_set_digest"],
            "parent_frame_set_bytes_before": before_parent,
            "parent_frame_set_bytes_after": after_parent,
            "parent_frame_set_unchanged": before_parent == after_parent,
            "decision_digests": [item["decision_digest"] for item in decisions],
            "transition_digests": [
                item["transition_digest"] for item in transitions
            ],
            "checkpoint_digest": checkpoint_record["checkpoint_digest"],
            "state_digest": state["state_digest"],
            "requirement_digest": (
                requirement["requirement_digest"] if requirement else None
            ),
            "event_payload_used_as_truth": False,
            "source_read_executed": False,
            "command_executed": False,
        },
        "temporal_trace_digest",
    )
    return state, requirement, checkpoint_record, decisions, transitions, trace


def assess_reassembly_result(
    requirement: dict[str, Any],
    *,
    result_session_generation: int,
    result_request_revision: int,
    current_session_generation: int,
    current_request_revision: int,
) -> dict[str, Any]:
    verify_seal(requirement, "requirement_digest")
    if result_session_generation != current_session_generation:
        decision = "REJECT_STALE_GENERATION"
    elif result_request_revision != current_request_revision:
        decision = "REJECT_SUPERSEDED_REQUEST"
    elif (
        result_session_generation != requirement["session_generation"]
        or result_request_revision != requirement["request_revision"]
    ):
        decision = "REJECT_REQUIREMENT_MISMATCH"
    else:
        decision = "ADMIT_NEW_GENERATION"
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "requirement_digest": requirement["requirement_digest"],
            "result_session_generation": result_session_generation,
            "result_request_revision": result_request_revision,
            "current_session_generation": current_session_generation,
            "current_request_revision": current_request_revision,
            "decision": decision,
            "old_frame_set_restored": False,
            "command_authority": False,
        },
        "reassembly_decision_digest",
    )


def make_snapshot(
    *,
    snapshot_id: str,
    source_revision: str,
    practice_binding_digest: str,
    location_ref: str,
    valid_from: str,
    valid_to: str,
    transaction_from: str,
    transaction_to: str | None,
    waiting_count: int,
    correction_of: str | None = None,
    superseded_by: str | None = None,
    coverage_state: str = "COMPLETE",
) -> dict[str, Any]:
    content = {
        "appointment_count": 3,
        "waiting_count": waiting_count,
        "status_codes": ["ARRIVED", "IN_CONSULT"],
    }
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": snapshot_id,
            "frame_type": "historical_waiting_room_projection",
            "source_class": "historical_operational_state",
            "source_contract_id": "emr4.historical_waiting_room_snapshot.v1",
            "source_revision": source_revision,
            "source_digest": canonical_sha256(
                {"source_revision": source_revision, "content": content}
            ),
            "practice_binding_digest": practice_binding_digest,
            "location_ref": location_ref,
            "subject_selector": "synthetic:waiting-room:location",
            "purpose_code": "TEMPORAL_OPERATIONAL_RECALL",
            "valid_time": {"starts_at": valid_from, "ends_at": valid_to},
            "transaction_time": {
                "starts_at": transaction_from,
                "ends_at": transaction_to,
            },
            "coverage_state": coverage_state,
            "retention_class": "SHORT_OPERATIONAL_RECALL",
            "correction_of": correction_of,
            "superseded_by": superseded_by,
            "content": content,
            "current_truth_authority": False,
            "read_only": True,
            "command_authority": False,
        },
        "snapshot_digest",
    )


def _contains(interval: dict[str, str | None], point: datetime) -> bool:
    start = _instant(str(interval["starts_at"]))
    end_value = interval["ends_at"]
    return start <= point and (end_value is None or point < _instant(str(end_value)))


def _validate_snapshots(snapshots: list[dict[str, Any]]) -> None:
    by_id = {item["snapshot_id"]: item for item in snapshots}
    if len(by_id) != len(snapshots):
        raise TemporalWeaveViolation("duplicate_snapshot_id")
    correction_children: dict[str, list[str]] = {}
    for item in snapshots:
        verify_seal(item, "snapshot_digest")
        valid_start = _instant(item["valid_time"]["starts_at"])
        valid_end = _instant(item["valid_time"]["ends_at"])
        transaction_start = _instant(item["transaction_time"]["starts_at"])
        transaction_end_value = item["transaction_time"]["ends_at"]
        if valid_start >= valid_end:
            raise TemporalWeaveViolation("invalid_valid_time")
        if transaction_end_value is not None and transaction_start >= _instant(
            transaction_end_value
        ):
            raise TemporalWeaveViolation("invalid_transaction_time")
        if item["correction_of"] is not None:
            correction_children.setdefault(item["correction_of"], []).append(
                item["snapshot_id"]
            )
            predecessor = by_id.get(item["correction_of"])
            if predecessor is None or predecessor["superseded_by"] != item["snapshot_id"]:
                raise TemporalWeaveViolation("broken_correction_lineage")
            if predecessor["valid_time"] != item["valid_time"]:
                raise TemporalWeaveViolation("correction_valid_time_mismatch")
            if predecessor["transaction_time"]["ends_at"] != item[
                "transaction_time"
            ]["starts_at"]:
                raise TemporalWeaveViolation("correction_transaction_gap_or_overlap")
    if any(len(children) > 1 for children in correction_children.values()):
        raise TemporalWeaveViolation("correction_lineage_fork")
    for index, left in enumerate(snapshots):
        for right in snapshots[index + 1 :]:
            if (
                left["coverage_state"] != "COMPLETE"
                or right["coverage_state"] != "COMPLETE"
                or left["subject_selector"] != right["subject_selector"]
                or left["location_ref"] != right["location_ref"]
                or left["valid_time"] != right["valid_time"]
            ):
                continue
            left_start = _instant(left["transaction_time"]["starts_at"])
            right_start = _instant(right["transaction_time"]["starts_at"])
            left_end = (
                _instant(left["transaction_time"]["ends_at"])
                if left["transaction_time"]["ends_at"] is not None
                else None
            )
            right_end = (
                _instant(right["transaction_time"]["ends_at"])
                if right["transaction_time"]["ends_at"] is not None
                else None
            )
            if (left_end is None or right_start < left_end) and (
                right_end is None or left_start < right_end
            ):
                raise TemporalWeaveViolation("overlapping_transaction_versions")


def build_historical_candidate(*, known_at: str) -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "query_id": f"synthetic:historical-query:{known_at}",
            "requesting_bureau": "RAYLEEN",
            "purpose_code": "TEMPORAL_OPERATIONAL_RECALL",
            "requested_source_classes": ["historical_operational_state"],
            "requested_location_refs": ["synthetic:location:brisbane-one"],
            "valid_at": "2026-08-06T00:30:00Z",
            "known_at": known_at,
            "maximum_results": 4,
            "requested_fields": [
                "appointment_count",
                "waiting_count",
                "status_codes",
            ],
            "read_only": True,
            "command_authority": False,
        },
        "candidate_digest",
    )


def build_historical_policy(parent_binding: dict[str, Any]) -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "policy_id": "synthetic:historical-policy:001",
            "practice_binding_digest": parent_binding["practice_binding_digest"],
            "allowed_bureaus": ["RAYLEEN"],
            "allowed_purposes": ["TEMPORAL_OPERATIONAL_RECALL"],
            "allowed_source_classes": ["historical_operational_state"],
            "allowed_location_refs": ["synthetic:location:brisbane-one"],
            "allowed_retention_classes": ["SHORT_OPERATIONAL_RECALL"],
            "allowed_fields": [
                "appointment_count",
                "waiting_count",
                "status_codes",
            ],
            "maximum_results": 4,
            "maximum_lookback_seconds": 86400,
            "issued_at": "2026-08-06T03:00:01Z",
            "expires_at": parent_binding["expires_at"],
            "read_only": True,
            "command_authority": False,
        },
        "historical_policy_digest",
    )


def select_historical_snapshots(
    candidate: dict[str, Any],
    policy: dict[str, Any],
    snapshots: list[dict[str, Any]],
) -> dict[str, Any]:
    verify_seal(candidate, "candidate_digest")
    verify_seal(policy, "historical_policy_digest")
    _validate_snapshots(snapshots)
    if candidate["requesting_bureau"] not in policy["allowed_bureaus"]:
        selected: list[dict[str, Any]] = []
        disposition = "NOT_AVAILABLE"
    else:
        valid_at = _instant(candidate["valid_at"])
        known_at = _instant(candidate["known_at"])
        allowed_sources = set(candidate["requested_source_classes"]).intersection(
            policy["allowed_source_classes"]
        )
        allowed_locations = set(candidate["requested_location_refs"]).intersection(
            policy["allowed_location_refs"]
        )
        allowed_fields = set(candidate["requested_fields"]).intersection(
            policy["allowed_fields"]
        )
        lookback_floor = _instant(policy["issued_at"]) - timedelta(
            seconds=policy["maximum_lookback_seconds"]
        )
        selected = []
        if (
            candidate["purpose_code"] not in policy["allowed_purposes"]
            or valid_at < lookback_floor
        ):
            return seal(
                {
                    "schema_version": SCHEMA_VERSION,
                    "query_id": candidate["query_id"],
                    "candidate_digest": candidate["candidate_digest"],
                    "historical_policy_digest": policy[
                        "historical_policy_digest"
                    ],
                    "valid_at": candidate["valid_at"],
                    "known_at": candidate["known_at"],
                    "disposition": "NOT_AVAILABLE",
                    "frames": [],
                    "missing_coverage_is_not_absence_evidence": True,
                    "event_delivery_ttl_controls_retention": False,
                    "current_truth_authority": False,
                    "command_authority": False,
                },
                "historical_result_digest",
            )
        for item in snapshots:
            if (
                item["practice_binding_digest"]
                != policy["practice_binding_digest"]
                or item["source_class"] not in allowed_sources
                or item["location_ref"] not in allowed_locations
                or item["retention_class"]
                not in policy["allowed_retention_classes"]
                or item["purpose_code"] != candidate["purpose_code"]
                or item["coverage_state"] != "COMPLETE"
                or not _contains(item["valid_time"], valid_at)
                or not _contains(item["transaction_time"], known_at)
            ):
                continue
            selected.append(
                seal(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "snapshot_id": item["snapshot_id"],
                        "snapshot_digest": item["snapshot_digest"],
                        "valid_time": item["valid_time"],
                        "transaction_time": item["transaction_time"],
                        "coverage_state": item["coverage_state"],
                        "content": {
                            key: value
                            for key, value in item["content"].items()
                            if key in allowed_fields
                        },
                        "current_truth_authority": False,
                        "read_only": True,
                        "command_authority": False,
                    },
                    "historical_frame_digest",
                )
            )
        selected.sort(
            key=lambda item: (
                item["valid_time"]["starts_at"],
                item["transaction_time"]["starts_at"],
                item["snapshot_id"],
            )
        )
        maximum = min(candidate["maximum_results"], policy["maximum_results"])
        selected = selected[:maximum]
        disposition = "ADMIT" if selected else "NO_COVERAGE"
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "query_id": candidate["query_id"],
            "candidate_digest": candidate["candidate_digest"],
            "historical_policy_digest": policy["historical_policy_digest"],
            "valid_at": candidate["valid_at"],
            "known_at": candidate["known_at"],
            "disposition": disposition,
            "frames": selected,
            "missing_coverage_is_not_absence_evidence": True,
            "event_delivery_ttl_controls_retention": False,
            "current_truth_authority": False,
            "command_authority": False,
        },
        "historical_result_digest",
    )


def _build_packet_without_proofreader() -> tuple[dict[str, Any], dict[str, Any]]:
    parent = build_authored_synthetic_packet()
    parent_binding = _parent_binding(parent)
    manifest = derive_dependency_manifest(parent)
    lease = derive_watch_lease(parent, manifest)
    location = "synthetic:location:brisbane-one"
    appointment = "synthetic:appointment:one"
    practitioner = "synthetic:practitioner:one"
    signals = [
        make_signal(
            signal_id="synthetic:signal:reschedule-101",
            event_type="diary.appointment_rescheduled",
            aggregate_ref=appointment,
            aggregate_revision=12,
            previous_transaction_position=100,
            transaction_position=101,
            location_refs=[location],
            practitioner_refs=[practitioner],
            occurred_at="2026-08-06T03:00:10Z",
            received_at="2026-08-06T03:00:11Z",
            practice_binding_digest=parent_binding["practice_binding_digest"],
        ),
        make_signal(
            signal_id="synthetic:signal:waiting-102",
            event_type="diary.waiting_state_changed",
            aggregate_ref=appointment,
            aggregate_revision=13,
            previous_transaction_position=101,
            transaction_position=102,
            location_refs=[location],
            practitioner_refs=[practitioner],
            occurred_at="2026-08-06T03:00:20Z",
            received_at="2026-08-06T03:00:21Z",
            practice_binding_digest=parent_binding["practice_binding_digest"],
        ),
        make_signal(
            signal_id="synthetic:signal:unrelated-103",
            event_type="diary.appointment_rescheduled",
            aggregate_ref="synthetic:appointment:outside-scope",
            aggregate_revision=1,
            previous_transaction_position=102,
            transaction_position=103,
            location_refs=["synthetic:location:outside-scope"],
            occurred_at="2026-08-06T03:00:30Z",
            received_at="2026-08-06T03:00:31Z",
            practice_binding_digest=parent_binding["practice_binding_digest"],
        ),
    ]
    state, requirement, checkpoint, decisions, transitions, trace = process_signals(
        parent, manifest, lease, signals
    )
    if requirement is None:
        raise TemporalWeaveViolation("canonical_requirement_missing")
    snapshots = [
        make_snapshot(
            snapshot_id="synthetic:snapshot:waiting-original",
            source_revision="synthetic:waiting-history:1",
            practice_binding_digest=parent_binding["practice_binding_digest"],
            location_ref=location,
            valid_from="2026-08-06T00:00:00Z",
            valid_to="2026-08-06T01:00:00Z",
            transaction_from="2026-08-06T00:05:00Z",
            transaction_to="2026-08-06T02:00:00Z",
            waiting_count=2,
            superseded_by="synthetic:snapshot:waiting-corrected",
        ),
        make_snapshot(
            snapshot_id="synthetic:snapshot:waiting-corrected",
            source_revision="synthetic:waiting-history:2",
            practice_binding_digest=parent_binding["practice_binding_digest"],
            location_ref=location,
            valid_from="2026-08-06T00:00:00Z",
            valid_to="2026-08-06T01:00:00Z",
            transaction_from="2026-08-06T02:00:00Z",
            transaction_to=None,
            waiting_count=3,
            correction_of="synthetic:snapshot:waiting-original",
        ),
        make_snapshot(
            snapshot_id="synthetic:snapshot:waiting-successor",
            source_revision="synthetic:waiting-history:3",
            practice_binding_digest=parent_binding["practice_binding_digest"],
            location_ref=location,
            valid_from="2026-08-06T01:00:00Z",
            valid_to="2026-08-06T02:00:00Z",
            transaction_from="2026-08-06T01:02:00Z",
            transaction_to=None,
            waiting_count=1,
        ),
        make_snapshot(
            snapshot_id="synthetic:snapshot:explicit-gap",
            source_revision="synthetic:waiting-history:gap-1",
            practice_binding_digest=parent_binding["practice_binding_digest"],
            location_ref=location,
            valid_from="2026-08-06T02:00:00Z",
            valid_to="2026-08-06T02:30:00Z",
            transaction_from="2026-08-06T02:05:00Z",
            transaction_to=None,
            waiting_count=0,
            coverage_state="GAP",
        ),
    ]
    policy = build_historical_policy(parent_binding)
    candidates = [
        build_historical_candidate(known_at="2026-08-06T01:00:00Z"),
        build_historical_candidate(known_at="2026-08-06T02:30:00Z"),
    ]
    results = [
        select_historical_snapshots(candidate, policy, snapshots)
        for candidate in candidates
    ]
    packet = {
        "schema_version": SCHEMA_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "parent_binding": parent_binding,
        "dependency_manifest": manifest,
        "watch_lease": lease,
        "signals": signals,
        "invalidation_decisions": decisions,
        "watcher_transitions": transitions,
        "committed_checkpoint": checkpoint,
        "frame_set_state": state,
        "reassembly_requirement": requirement,
        "stale_reassembly_decision": assess_reassembly_result(
            requirement,
            result_session_generation=manifest["session_generation"],
            result_request_revision=1,
            current_session_generation=manifest["session_generation"],
            current_request_revision=2,
        ),
        "historical_policy": policy,
        "historical_candidates": candidates,
        "historical_snapshots": snapshots,
        "historical_results": results,
        "temporal_trace": trace,
    }
    return parent, packet


def proofread_temporal_packet(
    parent: dict[str, Any], packet: dict[str, Any], *, checked_at: str
) -> dict[str, Any]:
    reasons: list[str] = []
    try:
        expected_parent, expected = _build_packet_without_proofreader()
        if canonical_sha256(expected_parent["frame_set"]) != canonical_sha256(
            parent["frame_set"]
        ):
            reasons.append("PARENT_FRAME_SET_MISMATCH")
        if packet != expected:
            reasons.append("TEMPORAL_PACKET_MISMATCH")
        if _instant(checked_at) >= _instant(packet["watch_lease"]["expires_at"]):
            reasons.append("TEMPORAL_PACKET_EXPIRED")
        if not packet["temporal_trace"]["parent_frame_set_unchanged"]:
            reasons.append("PARENT_FRAME_SET_MUTATED")
        if packet["temporal_trace"]["event_payload_used_as_truth"]:
            reasons.append("EVENT_PAYLOAD_PROMOTED_TO_TRUTH")
    except (KeyError, TypeError, ValueError, TemporalWeaveViolation) as error:
        reasons.append(f"PACKET_INVALID:{type(error).__name__}")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "packet_digest": canonical_sha256(packet),
            "checked_at": checked_at,
            "reason_codes": sorted(set(reasons)) if reasons else ["ALL_CHECKS_PASSED"],
            "release_decision": "BLOCK" if reasons else "RELEASE",
            "read_only": True,
            "command_authority": False,
        },
        "proofreader_trace_digest",
    )


def build_authored_synthetic_temporal_packet() -> dict[str, Any]:
    parent, packet = _build_packet_without_proofreader()
    packet["proofreader_trace"] = proofread_temporal_packet(
        parent, packet, checked_at="2026-08-06T03:01:01Z"
    )
    return packet


__all__ = [
    "DATA_CLASS",
    "EVIDENCE_LABEL",
    "EVENT_SCHEMAS",
    "HANDLING_POLICY",
    "SCHEMA_VERSION",
    "TemporalWeaveViolation",
    "assess_reassembly_result",
    "build_authored_synthetic_temporal_packet",
    "build_historical_candidate",
    "build_historical_policy",
    "derive_dependency_manifest",
    "derive_watch_lease",
    "make_signal",
    "make_snapshot",
    "process_signals",
    "proofread_temporal_packet",
    "select_historical_snapshots",
]
