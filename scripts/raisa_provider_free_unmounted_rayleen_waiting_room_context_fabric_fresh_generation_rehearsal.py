"""Pure authored-synthetic Rayleen Context Fabric fresh-generation rehearsal.

The module composes accepted deterministic contracts only.  It performs no
product read, listener, persistence, route, provider, command, or runtime work.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    ContractViolation,
    canonical_json,
    canonical_sha256,
    seal,
    verify_seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    assemble_current_operational_weave,
    build_authored_synthetic_packet,
    build_operational_context_need,
    intersect_operational_scope,
    proofread_current_operational_weave,
)
from scripts.raisa_provider_free_practice_context_fabric_patient_free_temporal_weave import (
    assess_reassembly_result,
    derive_dependency_manifest,
    derive_watch_lease,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly import (
    ASSEMBLED_AT as PREDECESSOR_ASSEMBLED_AT,
    build_authored_synthetic_invalidation_reassembly_packet,
    validate_invalidation_reassembly_packet,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter import (
    adapt_waiting_room_source,
    build_authored_synthetic_alias_manifest,
    build_authored_synthetic_waiting_room_frame,
    extract_waiting_room_source_envelope,
)


SCHEMA_VERSION = (
    "emr4.practice_context_fabric_rayleen_waiting_room_fresh_generation.v1"
)
EVIDENCE_LABEL = (
    "provider_free_authored_synthetic_unmounted_rayleen_fresh_generation_rehearsal"
)
DATA_CLASS = "authored_synthetic_patient_free_operational_metadata"
ASSEMBLED_AT = "2026-08-06T03:00:45Z"
CHECKED_AT = "2026-08-06T03:00:47Z"
NEW_REQUEST_REVISION = 2
DIARY_FRAME_TYPE = "current_diary_projection"
WAITING_FRAME_TYPE = "current_waiting_room_projection"
UNAFFECTED_FRAME_TYPES = (
    "active_practitioner_directory",
    "private_application_session_state",
)


class FreshGenerationViolation(ContractViolation):
    """Raised when the fresh generation cannot be released safely."""


def _instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise FreshGenerationViolation("invalid_timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FreshGenerationViolation("timestamp_requires_timezone")
    return parsed.astimezone(timezone.utc)


def _verify(value: dict[str, Any], field: str) -> None:
    try:
        verify_seal(value, field)
    except ContractViolation as error:
        raise FreshGenerationViolation(f"{field}_invalid") from error


def _validate_closed_typed(
    supplied: Any, trusted: Any, *, path: str = "$"
) -> None:
    """Require the trusted closed shape and exact Python types recursively."""

    if type(supplied) is not type(trusted):
        raise FreshGenerationViolation(f"closed_type_mismatch:{path}")
    if isinstance(trusted, dict):
        if set(supplied) != set(trusted):
            raise FreshGenerationViolation(f"closed_keys_mismatch:{path}")
        for key in sorted(trusted):
            _validate_closed_typed(
                supplied[key], trusted[key], path=f"{path}.{key}"
            )
    elif isinstance(trusted, list):
        if len(supplied) != len(trusted):
            raise FreshGenerationViolation(f"closed_list_length_mismatch:{path}")
        for index, item in enumerate(trusted):
            _validate_closed_typed(
                supplied[index], item, path=f"{path}[{index}]"
            )


def _source(sources: list[dict[str, Any]], frame_type: str) -> dict[str, Any]:
    matches = [item for item in sources if item["frame_type"] == frame_type]
    if len(matches) != 1:
        raise FreshGenerationViolation(f"exact_source_required:{frame_type}")
    return matches[0]


def _reconstruct_predecessor() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Rebuild the accepted old adapted Current generation and seam packet."""

    base = build_authored_synthetic_packet()
    old_frame = build_authored_synthetic_waiting_room_frame()
    old_alias = build_authored_synthetic_alias_manifest(
        old_frame, base["authority_binding"], base["scope_grant"]
    )
    old_adapter = adapt_waiting_room_source(
        old_frame,
        base["authority_binding"],
        base["scope_grant"],
        old_alias,
        assembled_at=PREDECESSOR_ASSEMBLED_AT,
    )
    old_waiting = extract_waiting_room_source_envelope(
        old_adapter,
        old_frame,
        base["authority_binding"],
        base["scope_grant"],
        old_alias,
        assembled_at=PREDECESSOR_ASSEMBLED_AT,
    )
    old_sources = [
        deepcopy(old_waiting)
        if item["frame_type"] == WAITING_FRAME_TYPE
        else deepcopy(item)
        for item in base["source_envelopes"]
    ]
    frame_set, source_trace, weave_trace = assemble_current_operational_weave(
        base["candidate"],
        base["context_need"],
        base["authority_binding"],
        base["scope_grant"],
        old_sources,
        assembled_at=PREDECESSOR_ASSEMBLED_AT,
    )
    proofreader = proofread_current_operational_weave(
        base["candidate"],
        base["context_need"],
        base["authority_binding"],
        base["scope_grant"],
        old_sources,
        frame_set,
        source_trace,
        weave_trace,
        assembled_at=PREDECESSOR_ASSEMBLED_AT,
    )
    if proofreader["release_decision"] != "RELEASE":
        raise FreshGenerationViolation("predecessor_current_not_released")
    adapted = deepcopy(base)
    adapted.update(
        {
            "source_envelopes": old_sources,
            "source_trace": source_trace,
            "frame_set": frame_set,
            "weave_trace": weave_trace,
            "proofreader_trace": proofreader,
        }
    )
    predecessor = build_authored_synthetic_invalidation_reassembly_packet()
    validate_invalidation_reassembly_packet(predecessor)
    requirement = predecessor["reassembly_requirement"]
    instruction = predecessor["fresh_reassembly_instruction"]
    if requirement["superseded_frame_set_digest"] != frame_set["frame_set_digest"]:
        raise FreshGenerationViolation("predecessor_requirement_detached")
    if instruction["requirement_digest"] != requirement["requirement_digest"]:
        raise FreshGenerationViolation("predecessor_instruction_detached")
    if not (
        instruction["execution_enabled"] is False
        and instruction["source_read_executed"] is False
        and instruction["returns_data"] is False
        and instruction["command_authority"] is False
        and instruction["provider_authority"] is False
    ):
        raise FreshGenerationViolation("predecessor_instruction_not_inert")
    return adapted, predecessor, requirement, instruction


def _build_new_request_and_authority(
    old: dict[str, Any], requirement: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    candidate = deepcopy(old["candidate"])
    candidate.update(
        {
            "need_id": "synthetic:need:current-operational-weave-002",
            "issued_at": "2026-08-06T03:00:35Z",
        }
    )
    candidate = seal(
        {key: value for key, value in candidate.items() if key != "candidate_digest"},
        "candidate_digest",
    )
    binding = deepcopy(old["authority_binding"])
    need = build_operational_context_need(
        candidate, binding, assembled_at=ASSEMBLED_AT
    )
    grant = intersect_operational_scope(
        candidate, need, binding, assembled_at=ASSEMBLED_AT
    )
    parent_grant = old["scope_grant"]
    subset_fields = (
        "allowed_frame_types",
        "allowed_source_classes",
        "required_source_classes",
        "allowed_fields",
        "allowed_location_refs",
    )
    no_wider = all(
        set(grant[field]).issubset(set(parent_grant[field]))
        for field in subset_fields
    ) and all(
        grant[field] <= parent_grant[field]
        for field in (
            "maximum_frames",
            "maximum_items_per_frame",
            "maximum_total_bytes",
            "freshness_seconds",
        )
    )
    old_window = parent_grant["effective_time_window"]
    new_window = grant["effective_time_window"]
    no_wider = no_wider and (
        _instant(new_window["starts_at"]) >= _instant(old_window["starts_at"])
        and _instant(new_window["ends_at"]) <= _instant(old_window["ends_at"])
    )
    no_wider = no_wider and all(
        grant[field] == parent_grant[field]
        for field in (
            "requesting_bureau",
            "purpose_code",
            "binding_digest",
            "session_binding_digest",
        )
    )
    no_wider = no_wider and (
        grant["read_only"] is True
        and grant["command_authority"] is False
        and grant["provider_authority"] is False
    )
    if not no_wider or grant["decision"] != "ADMIT":
        raise FreshGenerationViolation("fresh_grant_wider_or_unavailable")
    generation_request = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "request_id": "synthetic:fresh-generation-request:002",
            "need_id": candidate["need_id"],
            "request_revision": NEW_REQUEST_REVISION,
            "supersedes_request_revision": requirement["request_revision"],
            "requirement_digest": requirement["requirement_digest"],
            "session_generation": binding["session_generation"],
            "issued_at": candidate["issued_at"],
            "assembled_at": ASSEMBLED_AT,
            "read_only": True,
            "execution_enabled": False,
            "source_read_executed": False,
            "product_read_executed": False,
            "command_authority": False,
            "provider_authority": False,
        },
        "generation_request_digest",
    )
    authority_trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "requirement_digest": requirement["requirement_digest"],
            "generation_request_digest": generation_request[
                "generation_request_digest"
            ],
            "candidate_digest": candidate["candidate_digest"],
            "binding_digest": binding["binding_digest"],
            "session_binding_digest": binding["session_binding_digest"],
            "need_digest": need["need_digest"],
            "grant_digest": grant["grant_digest"],
            "parent_grant_digest": parent_grant["grant_digest"],
            "distinct_need": need["need_id"] != old["context_need"]["need_id"],
            "monotonic_request_revision": NEW_REQUEST_REVISION
            > requirement["request_revision"],
            "binding_current": _instant(binding["issued_at"])
            <= _instant(ASSEMBLED_AT)
            < _instant(binding["expires_at"]),
            "grant_no_wider": no_wider,
            "identity_equal": all(
                binding[field] == old["authority_binding"][field]
                for field in (
                    "principal_ref",
                    "roles",
                    "practice_id",
                    "session_id",
                    "session_generation",
                    "allowed_bureaus",
                    "allowed_purposes",
                )
            ),
            "scope_dimensions_checked": [
                *subset_fields,
                "effective_time_window",
                "maximum_frames",
                "maximum_items_per_frame",
                "maximum_total_bytes",
                "freshness_seconds",
                "requesting_bureau",
                "purpose_code",
                "binding_digest",
                "session_binding_digest",
                "read_only",
                "command_authority",
                "provider_authority",
            ],
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "authority_trace_digest",
    )
    if not all(
        authority_trace[field] is True
        for field in (
            "distinct_need",
            "monotonic_request_revision",
            "binding_current",
            "grant_no_wider",
            "identity_equal",
        )
    ):
        raise FreshGenerationViolation("fresh_authority_trace_failed")
    return candidate, need, grant, authority_trace


def _build_new_diary(old: dict[str, Any], grant: dict[str, Any]) -> dict[str, Any]:
    diary = deepcopy(_source(old["source_envelopes"], DIARY_FRAME_TYPE))
    diary.update(
        {
            "source_envelope_id": "synthetic:source:diary-002",
            "source_revision": "synthetic:diary-revision:12",
            "session_binding_digest": grant["session_binding_digest"],
            "observed_at": "2026-08-06T03:00:30Z",
            "expires_at": "2026-08-06T03:02:30Z",
        }
    )
    diary["payload"]["context_revision"] = 12
    diary["payload"]["appointments"][0]["status"] = "IN_CONSULT"
    return seal(
        {key: value for key, value in diary.items() if key != "source_digest"},
        "source_digest",
    )


def _build_new_waiting_inputs(
    old: dict[str, Any], grant: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    frame = build_authored_synthetic_waiting_room_frame()
    frame.update(
        {
            "frame_id": "22000000-0000-4000-8000-000000000001",
            "context_revision": 8,
            "generated_at": "2026-08-06T03:00:30Z",
            "expires_at": "2026-08-06T03:02:30Z",
        }
    )
    fact = frame["backend_facts"][0]
    fact["status"] = "in_consult"
    for value in [fact, *frame["derived_signals"]]:
        value["label"]["observed_at"] = frame["generated_at"]
        value["label"]["expires_at"] = frame["expires_at"]
        value["label"]["source_ids"] = [
            "authored_synthetic_fixture:waiting-room-adapter-002"
        ]
    frame["derived_signals"][0]["value"] = 11
    alias = build_authored_synthetic_alias_manifest(
        frame, old["authority_binding"], grant
    )
    alias.update(
        {
            "manifest_id": "synthetic:alias-manifest:rayleen-waiting-002",
            "issued_at": "2026-08-06T03:00:35Z",
            "expires_at": "2026-08-06T03:02:30Z",
        }
    )
    alias = seal(
        {key: value for key, value in alias.items() if key != "alias_manifest_digest"},
        "alias_manifest_digest",
    )
    adapter = adapt_waiting_room_source(
        frame,
        old["authority_binding"],
        grant,
        alias,
        assembled_at=ASSEMBLED_AT,
    )
    extracted = extract_waiting_room_source_envelope(
        adapter,
        frame,
        old["authority_binding"],
        grant,
        alias,
        assembled_at=ASSEMBLED_AT,
    )
    return frame, alias, adapter, extracted


def _build_sources_and_traces(
    old: dict[str, Any],
    requirement: dict[str, Any],
    grant: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    new_diary = _build_new_diary(old, grant)
    new_frame, alias, adapter, new_waiting = _build_new_waiting_inputs(old, grant)
    old_manifest = derive_dependency_manifest(old)
    required_by_frame = {
        item["frame_type"]: item
        for item in old_manifest["dependencies"]
        if item["dependency_id"] in requirement["required_dependency_ids"]
    }
    if set(required_by_frame) != {DIARY_FRAME_TYPE, WAITING_FRAME_TYPE}:
        raise FreshGenerationViolation("required_dependency_coverage_unexpected")
    carried = [
        deepcopy(_source(old["source_envelopes"], frame_type))
        for frame_type in UNAFFECTED_FRAME_TYPES
    ]
    for source in carried:
        dependency = next(
            item
            for item in old_manifest["dependencies"]
            if item["frame_type"] == source["frame_type"]
        )
        if dependency["dependency_id"] in requirement["required_dependency_ids"]:
            raise FreshGenerationViolation("affected_source_carried_forward")
        if _instant(ASSEMBLED_AT) >= _instant(source["expires_at"]):
            raise FreshGenerationViolation("expired_source_carried_forward")
        if source["session_binding_digest"] != grant["session_binding_digest"]:
            raise FreshGenerationViolation("carried_source_session_mismatch")
    refresh_records = []
    for frame_type, source, input_digest in (
        (DIARY_FRAME_TYPE, new_diary, canonical_sha256(new_diary)),
        (WAITING_FRAME_TYPE, new_waiting, canonical_sha256(new_frame)),
    ):
        old_dependency = required_by_frame[frame_type]
        if source["source_digest"] == old_dependency["source_digest"]:
            raise FreshGenerationViolation("required_source_not_refreshed")
        refresh_records.append(
            seal(
                {
                    "schema_version": SCHEMA_VERSION,
                    "dependency_id": old_dependency["dependency_id"],
                    "frame_type": frame_type,
                    "old_source_revision": old_dependency["source_revision"],
                    "old_source_digest": old_dependency["source_digest"],
                    "new_source_revision": source["source_revision"],
                    "new_source_digest": source["source_digest"],
                    "completed_read_shaped_input_digest": input_digest,
                    "independently_authored": True,
                    "event_metadata_used_as_context": False,
                    "source_read_executed": False,
                },
                "refresh_record_digest",
            )
        )
    refresh_trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "requirement_digest": requirement["requirement_digest"],
            "required_dependency_ids": requirement["required_dependency_ids"],
            "refreshed_dependency_ids": sorted(
                item["dependency_id"] for item in refresh_records
            ),
            "refresh_records": refresh_records,
            "waiting_source_frame_digest": canonical_sha256(new_frame),
            "alias_manifest_digest": alias["alias_manifest_digest"],
            "adapter_result_digest": adapter["adapter_result_digest"],
            "adapter_trace_digest": adapter["adapter_trace"]["adapter_trace_digest"],
            "extractor_recomputed_source_digest": new_waiting["source_digest"],
            "complete_coverage": sorted(requirement["required_dependency_ids"])
            == sorted(item["dependency_id"] for item in refresh_records),
            "event_metadata_used_as_context": False,
            "source_read_executed": False,
            "product_read_executed": False,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "refresh_trace_digest",
    )
    if refresh_trace["complete_coverage"] is not True:
        raise FreshGenerationViolation("required_dependency_refresh_incomplete")
    carry_records = [
        seal(
            {
                "schema_version": SCHEMA_VERSION,
                "frame_type": source["frame_type"],
                "source_envelope_id": source["source_envelope_id"],
                "source_revision": source["source_revision"],
                "source_digest_before": source["source_digest"],
                "source_digest_after": source["source_digest"],
                "canonical_bytes_unchanged": True,
                "unaffected": True,
                "granted": source["frame_type"] in grant["allowed_frame_types"],
                "coherent_session": source["session_binding_digest"]
                == grant["session_binding_digest"],
                "unexpired": _instant(ASSEMBLED_AT) < _instant(source["expires_at"]),
            },
            "carry_record_digest",
        )
        for source in carried
    ]
    carry_trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "requirement_digest": requirement["requirement_digest"],
            "carried_frame_types": [item["frame_type"] for item in carry_records],
            "carry_records": carry_records,
            "all_eligible": all(
                all(
                    item[field] is True
                    for field in (
                        "canonical_bytes_unchanged",
                        "unaffected",
                        "granted",
                        "coherent_session",
                        "unexpired",
                    )
                )
                for item in carry_records
            ),
            "persistence_used": False,
            "retention_authority": False,
        },
        "carry_forward_trace_digest",
    )
    if carry_trace["all_eligible"] is not True:
        raise FreshGenerationViolation("carry_forward_not_eligible")
    return [new_diary, new_waiting, *carried], refresh_trace, carry_trace


def _build_candidate_packet() -> dict[str, Any]:
    old, predecessor, requirement, instruction = _reconstruct_predecessor()
    old_bytes = canonical_json(old["frame_set"])
    candidate, need, grant, authority_trace = _build_new_request_and_authority(
        old, requirement
    )
    sources, refresh_trace, carry_trace = _build_sources_and_traces(
        old, requirement, grant
    )
    frame_set, source_trace, weave_trace = assemble_current_operational_weave(
        candidate,
        need,
        old["authority_binding"],
        grant,
        sources,
        assembled_at=ASSEMBLED_AT,
    )
    current_proofreader = proofread_current_operational_weave(
        candidate,
        need,
        old["authority_binding"],
        grant,
        sources,
        frame_set,
        source_trace,
        weave_trace,
        assembled_at=ASSEMBLED_AT,
        proofread_at=CHECKED_AT,
    )
    if current_proofreader["release_decision"] != "RELEASE":
        raise FreshGenerationViolation("new_current_weave_not_released")
    fresh_parent = {
        **deepcopy(old),
        "candidate": candidate,
        "context_need": need,
        "scope_grant": grant,
        "source_envelopes": sources,
        "source_trace": source_trace,
        "frame_set": frame_set,
        "weave_trace": weave_trace,
        "proofreader_trace": current_proofreader,
    }
    manifest = derive_dependency_manifest(
        fresh_parent, issued_at="2026-08-06T03:00:46Z"
    )
    lease = derive_watch_lease(fresh_parent, manifest)
    old_rejection = assess_reassembly_result(
        requirement,
        result_session_generation=requirement["session_generation"],
        result_request_revision=requirement["request_revision"],
        current_session_generation=requirement["session_generation"],
        current_request_revision=NEW_REQUEST_REVISION,
    )
    if old_rejection["decision"] != "REJECT_SUPERSEDED_REQUEST":
        raise FreshGenerationViolation("older_result_not_rejected")
    admission = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "admission_id": "synthetic:fresh-generation-admission:002",
            "requirement_digest": requirement["requirement_digest"],
            "generation_request_digest": authority_trace[
                "generation_request_digest"
            ],
            "authority_trace_digest": authority_trace["authority_trace_digest"],
            "refresh_trace_digest": refresh_trace["refresh_trace_digest"],
            "carry_forward_trace_digest": carry_trace[
                "carry_forward_trace_digest"
            ],
            "current_proofreader_trace_digest": current_proofreader[
                "proofreader_trace_digest"
            ],
            "frame_set_id": frame_set["frame_set_id"],
            "frame_set_digest": frame_set["frame_set_digest"],
            "source_trace_digest": source_trace["source_trace_digest"],
            "manifest_digest": manifest["manifest_digest"],
            "lease_digest": lease["lease_digest"],
            "current_session_generation": requirement["session_generation"],
            "current_request_revision": NEW_REQUEST_REVISION,
            "admission_decision": "ADMIT_NEW_GENERATION",
            "released_trusted_deep_copy_only": True,
            "old_frame_set_restored": False,
            "runtime_state_mounted": False,
            "persistence_used": False,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "admission_digest",
    )
    ordering_traces = [
        seal(
            {
                "schema_version": SCHEMA_VERSION,
                "completion_order": order,
                "older_result_decision_digest": old_rejection[
                    "reassembly_decision_digest"
                ],
                "new_admission_digest": admission["admission_digest"],
                "final_frame_set_digest": frame_set["frame_set_digest"],
                "rollback_occurred": False,
                "old_frame_set_restored": False,
            },
            "ordering_trace_digest",
        )
        for order in ("OLDER_THEN_NEWER", "NEWER_THEN_OLDER")
    ]
    immutability_trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "old_frame_set_id": old["frame_set"]["frame_set_id"],
            "old_frame_set_digest": old["frame_set"]["frame_set_digest"],
            "old_frame_set_bytes_before": canonical_sha256(old["frame_set"]),
            "old_frame_set_bytes_after": canonical_sha256(old["frame_set"]),
            "old_frame_set_bytes_unchanged": canonical_json(old["frame_set"])
            == old_bytes,
            "old_generation_state": "RETIRED",
            "new_frame_set_id": frame_set["frame_set_id"],
            "new_frame_set_digest": frame_set["frame_set_digest"],
            "distinct_generation": (
                frame_set["frame_set_id"] != old["frame_set"]["frame_set_id"]
                and frame_set["frame_set_digest"]
                != old["frame_set"]["frame_set_digest"]
            ),
            "old_frame_set_restored": False,
        },
        "immutability_trace_digest",
    )
    if not (
        immutability_trace["old_frame_set_bytes_unchanged"]
        and immutability_trace["distinct_generation"]
    ):
        raise FreshGenerationViolation("generation_immutability_failed")
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "data_class": DATA_CLASS,
        "predecessor_packet_digest": canonical_sha256(predecessor),
        "predecessor_requirement_digest": requirement["requirement_digest"],
        "predecessor_instruction_digest": instruction["instruction_digest"],
        "authority_trace": authority_trace,
        "required_dependency_refresh_trace": refresh_trace,
        "carry_forward_trace": carry_trace,
        "new_context_need_digest": need["need_digest"],
        "new_scope_grant_digest": grant["grant_digest"],
        "new_source_trace": source_trace,
        "new_frame_set": frame_set,
        "new_weave_trace": weave_trace,
        "current_proofreader_trace": current_proofreader,
        "new_dependency_manifest": manifest,
        "new_watch_lease": lease,
        "fresh_generation_admission": admission,
        "older_result_rejection": old_rejection,
        "completion_order_traces": ordering_traces,
        "old_generation_immutability_trace": immutability_trace,
        "new_frame_set_admitted": True,
        "product_read_executed": False,
        "source_read_executed": False,
        "listener_mounted": False,
        "runtime_state_mounted": False,
        "filesystem_effects": False,
        "network_effects": False,
        "database_effects": False,
        "subprocess_effects": False,
        "persistence_used": False,
        "read_only": True,
        "command_authority": False,
        "command_executed": False,
        "provider_authority": False,
        "provider_called": False,
    }


def _proofreader_trace(
    packet: dict[str, Any],
    expected: dict[str, Any] | None,
    *,
    checked_at: str,
    reasons: list[str],
) -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_digest": canonical_sha256(packet),
            "trusted_reconstruction_digest": (
                canonical_sha256(expected) if expected is not None else None
            ),
            "checked_at": checked_at,
            "reason_codes": sorted(set(reasons)) if reasons else ["ALL_CHECKS_PASSED"],
            "release_decision": "BLOCK" if reasons else "RELEASE",
            "reconstructs_complete_packet": True,
            "releases_trusted_deep_copy_only": True,
            "event_metadata_used_as_context": False,
            "product_read_executed": False,
            "source_read_executed": False,
            "listener_mounted": False,
            "runtime_state_mounted": False,
            "persistence_used": False,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "proofreader_trace_digest",
    )


def _release_candidate(
    candidate: dict[str, Any], *, checked_at: str
) -> dict[str, Any]:
    reasons: list[str] = []
    expected: dict[str, Any] | None = None
    try:
        expected = _build_candidate_packet()
        _validate_closed_typed(candidate, expected)
        if canonical_json(candidate) != canonical_json(expected):
            reasons.append("PACKET_RECONSTRUCTION_MISMATCH")
        if _instant(checked_at) >= _instant(expected["new_frame_set"]["expires_at"]):
            reasons.append("NEW_FRAME_SET_EXPIRED")
        if _instant(checked_at) >= _instant(expected["new_watch_lease"]["expires_at"]):
            reasons.append("NEW_WATCH_LEASE_EXPIRED")
        if expected["current_proofreader_trace"]["release_decision"] != "RELEASE":
            reasons.append("CURRENT_PROOFREADER_BLOCKED")
        if expected["fresh_generation_admission"]["admission_decision"] != (
            "ADMIT_NEW_GENERATION"
        ):
            reasons.append("NEW_GENERATION_NOT_ADMITTED")
        if expected["older_result_rejection"]["decision"] != (
            "REJECT_SUPERSEDED_REQUEST"
        ):
            reasons.append("OLDER_RESULT_NOT_REJECTED")
        if not expected["required_dependency_refresh_trace"]["complete_coverage"]:
            reasons.append("REQUIRED_REFRESH_INCOMPLETE")
        if not expected["carry_forward_trace"]["all_eligible"]:
            reasons.append("CARRY_FORWARD_INELIGIBLE")
        if not expected["old_generation_immutability_trace"][
            "old_frame_set_bytes_unchanged"
        ]:
            reasons.append("OLD_FRAME_SET_MUTATED")
        false_flags = (
            "product_read_executed",
            "source_read_executed",
            "listener_mounted",
            "runtime_state_mounted",
            "filesystem_effects",
            "network_effects",
            "database_effects",
            "subprocess_effects",
            "persistence_used",
            "command_authority",
            "command_executed",
            "provider_authority",
            "provider_called",
        )
        if any(expected[field] is not False for field in false_flags):
            reasons.append("ZERO_EFFECT_POSTURE_INVALID")
    except (KeyError, TypeError, ValueError, ContractViolation) as error:
        reasons.append(f"PACKET_INVALID:{type(error).__name__}")
    trace = _proofreader_trace(
        candidate, expected, checked_at=checked_at, reasons=reasons
    )
    released = None
    if not reasons and expected is not None:
        released = deepcopy(expected)
        released["proofreader_trace"] = deepcopy(trace)
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "release_decision": trace["release_decision"],
            "reason_codes": trace["reason_codes"],
            "proofreader_trace": trace,
            "released_packet": released,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "proofreader_result_digest",
    )


def build_authored_synthetic_fresh_generation_packet() -> dict[str, Any]:
    """Build and proofread the sole authored-synthetic fresh generation."""

    candidate = _build_candidate_packet()
    result = _release_candidate(candidate, checked_at=CHECKED_AT)
    released = result["released_packet"]
    if result["release_decision"] != "RELEASE" or released is None:
        raise FreshGenerationViolation("authored_synthetic_packet_not_released")
    return deepcopy(released)


def validate_fresh_generation_packet(packet: dict[str, Any]) -> None:
    """Validate a released packet against complete trusted reconstruction."""

    trusted = build_authored_synthetic_fresh_generation_packet()
    _validate_closed_typed(packet, trusted)
    if canonical_json(packet) != canonical_json(trusted):
        raise FreshGenerationViolation("released_packet_reconstruction_mismatch")
    for value, field in (
        (packet["authority_trace"], "authority_trace_digest"),
        (packet["required_dependency_refresh_trace"], "refresh_trace_digest"),
        (packet["carry_forward_trace"], "carry_forward_trace_digest"),
        (packet["new_source_trace"], "source_trace_digest"),
        (packet["new_frame_set"], "frame_set_digest"),
        (packet["new_weave_trace"], "weave_trace_digest"),
        (packet["current_proofreader_trace"], "proofreader_trace_digest"),
        (packet["new_dependency_manifest"], "manifest_digest"),
        (packet["new_watch_lease"], "lease_digest"),
        (packet["fresh_generation_admission"], "admission_digest"),
        (packet["older_result_rejection"], "reassembly_decision_digest"),
        (packet["old_generation_immutability_trace"], "immutability_trace_digest"),
        (packet["proofreader_trace"], "proofreader_trace_digest"),
    ):
        _verify(value, field)
    for trace in packet["completion_order_traces"]:
        _verify(trace, "ordering_trace_digest")
    if packet["proofreader_trace"]["release_decision"] != "RELEASE":
        raise FreshGenerationViolation("packet_not_released")


def proofread_fresh_generation_packet(
    packet: dict[str, Any], *, checked_at: str = CHECKED_AT
) -> dict[str, Any]:
    """Reconstruct the packet and atomically release only its trusted copy."""

    reasons: list[str] = []
    expected: dict[str, Any] | None = None
    try:
        expected = build_authored_synthetic_fresh_generation_packet()
        _validate_closed_typed(packet, expected)
        if canonical_json(packet) != canonical_json(expected):
            reasons.append("PACKET_RECONSTRUCTION_MISMATCH")
        if _instant(checked_at) >= _instant(expected["new_frame_set"]["expires_at"]):
            reasons.append("NEW_FRAME_SET_EXPIRED")
        if _instant(checked_at) >= _instant(expected["new_watch_lease"]["expires_at"]):
            reasons.append("NEW_WATCH_LEASE_EXPIRED")
    except (KeyError, TypeError, ValueError, ContractViolation) as error:
        reasons.append(f"PACKET_INVALID:{type(error).__name__}")
    if not reasons and expected is not None:
        trace = deepcopy(expected["proofreader_trace"])
        released = deepcopy(expected)
    else:
        trace = _proofreader_trace(
            packet, expected, checked_at=checked_at, reasons=reasons
        )
        released = None
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "release_decision": "BLOCK" if reasons else "RELEASE",
            "reason_codes": trace["reason_codes"],
            "proofreader_trace": trace,
            "released_packet": released,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "proofreader_result_digest",
    )


# Exact-instance JSON Schema: const recursively closes every nested object and
# list while the public validator additionally enforces exact Python types.
FRESH_GENERATION_PACKET_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Rayleen fresh-generation rehearsal packet",
    "const": build_authored_synthetic_fresh_generation_packet(),
}


__all__ = [
    "EVIDENCE_LABEL",
    "FRESH_GENERATION_PACKET_SCHEMA",
    "FreshGenerationViolation",
    "SCHEMA_VERSION",
    "build_authored_synthetic_fresh_generation_packet",
    "proofread_fresh_generation_packet",
    "validate_fresh_generation_packet",
]
