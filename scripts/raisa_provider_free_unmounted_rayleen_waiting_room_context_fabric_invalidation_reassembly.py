"""Pure Rayleen waiting-room invalidation and inert reassembly seam.

This module composes accepted provider-free source-adapter, Current-weave, and
temporal-weave functions.  It has no listener, source reader, persistence,
route, provider, or command surface.
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
    proofread_current_operational_weave,
)
from scripts.raisa_provider_free_practice_context_fabric_patient_free_temporal_weave import (
    assess_reassembly_result,
    derive_dependency_manifest,
    derive_watch_lease,
    make_signal,
    process_signals,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter import (
    adapt_waiting_room_source,
    build_authored_synthetic_alias_manifest,
    build_authored_synthetic_waiting_room_frame,
    extract_waiting_room_source_envelope,
)


SCHEMA_VERSION = (
    "emr4.practice_context_fabric_rayleen_waiting_room_"
    "invalidation_reassembly.v1"
)
EVIDENCE_LABEL = (
    "provider_free_authored_synthetic_unmounted_rayleen_"
    "invalidation_reassembly_seam"
)
DATA_CLASS = "authored_synthetic_patient_free_operational_metadata"
ASSEMBLED_AT = "2026-08-06T03:00:00Z"
OBSERVED_AT = "2026-08-06T03:00:30Z"
CHECKED_AT = "2026-08-06T03:00:31Z"
WAITING_FRAME_TYPE = "current_waiting_room_projection"
INSTRUCTION_STEPS = [
    "fresh_authority_check",
    "fresh_waiting_room_source_read",
    "rerun_waiting_room_source_adapter",
    "assemble_new_current_weave",
    "same_packet_proofread",
]


class RayleenInvalidationReassemblyViolation(ContractViolation):
    """Raised when the seam cannot safely release its closed packet."""


# Stable public name used by acceptance composition.
InvalidationReassemblyViolation = RayleenInvalidationReassemblyViolation


def _instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise RayleenInvalidationReassemblyViolation("invalid_timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RayleenInvalidationReassemblyViolation(
            "timestamp_requires_timezone"
        )
    return parsed.astimezone(timezone.utc)


def _verify(value: dict[str, Any], field: str) -> None:
    try:
        verify_seal(value, field)
    except ContractViolation as error:
        raise RayleenInvalidationReassemblyViolation(
            f"{field}_invalid"
        ) from error


def _validate_closed_typed(
    supplied: Any, trusted: Any, *, path: str = "$"
) -> None:
    """Recursively require the trusted closed shape and exact Python types.

    Exact type identity deliberately rejects ``bool`` where a trusted integer
    is expected.  Dict keys and list lengths are closed at every depth.
    """

    if type(supplied) is not type(trusted):
        raise RayleenInvalidationReassemblyViolation(
            f"closed_type_mismatch:{path}"
        )
    if isinstance(trusted, dict):
        if set(supplied) != set(trusted):
            raise RayleenInvalidationReassemblyViolation(
                f"closed_keys_mismatch:{path}"
            )
        for key in sorted(trusted):
            _validate_closed_typed(
                supplied[key], trusted[key], path=f"{path}.{key}"
            )
    elif isinstance(trusted, list):
        if len(supplied) != len(trusted):
            raise RayleenInvalidationReassemblyViolation(
                f"closed_list_length_mismatch:{path}"
            )
        for index, item in enumerate(trusted):
            _validate_closed_typed(
                supplied[index], item, path=f"{path}[{index}]"
            )


def _waiting(items: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [item for item in items if item["frame_type"] == WAITING_FRAME_TYPE]
    if len(matches) != 1:
        raise RayleenInvalidationReassemblyViolation(
            "exact_waiting_component_required"
        )
    return matches[0]


def _build_adapted_parent(
    parent: dict[str, Any],
    source_frame: dict[str, Any],
    alias_manifest: dict[str, Any],
    adapter_result: dict[str, Any],
    *,
    assembled_at: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    extracted = extract_waiting_room_source_envelope(
        adapter_result,
        source_frame,
        parent["authority_binding"],
        parent["scope_grant"],
        alias_manifest,
        assembled_at=assembled_at,
    )
    original_sources = parent["source_envelopes"]
    sources = [
        deepcopy(extracted) if item["frame_type"] == WAITING_FRAME_TYPE else deepcopy(item)
        for item in original_sources
    ]
    if len(sources) != len(original_sources):
        raise RayleenInvalidationReassemblyViolation("source_count_changed")
    for before, after in zip(original_sources, sources, strict=True):
        if before["frame_type"] != WAITING_FRAME_TYPE and before != after:
            raise RayleenInvalidationReassemblyViolation(
                "non_waiting_source_changed"
            )
    frame_set, source_trace, weave_trace = assemble_current_operational_weave(
        parent["candidate"],
        parent["context_need"],
        parent["authority_binding"],
        parent["scope_grant"],
        sources,
        assembled_at=assembled_at,
    )
    parent_proofreader = proofread_current_operational_weave(
        parent["candidate"],
        parent["context_need"],
        parent["authority_binding"],
        parent["scope_grant"],
        sources,
        frame_set,
        source_trace,
        weave_trace,
        assembled_at=assembled_at,
    )
    if parent_proofreader["release_decision"] != "RELEASE":
        raise RayleenInvalidationReassemblyViolation(
            "adapted_parent_not_released"
        )
    adapted = deepcopy(parent)
    adapted.update(
        {
            "source_envelopes": sources,
            "source_trace": source_trace,
            "frame_set": frame_set,
            "weave_trace": weave_trace,
            "proofreader_trace": parent_proofreader,
        }
    )
    return adapted, extracted, parent_proofreader


def _binding_trace(
    *,
    parent: dict[str, Any],
    adapted_parent: dict[str, Any],
    source_frame: dict[str, Any],
    alias_manifest: dict[str, Any],
    adapter_result: dict[str, Any],
    extracted: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    waiting_frame = _waiting(adapted_parent["frame_set"]["frames"])
    waiting_dependency = next(
        (
            item
            for item in manifest["dependencies"]
            if item["frame_type"] == WAITING_FRAME_TYPE
        ),
        None,
    )
    if waiting_dependency is None:
        raise RayleenInvalidationReassemblyViolation(
            "waiting_dependency_missing"
        )
    if not (
        source_frame
        and adapter_result["source_frame_digest"] == canonical_sha256(source_frame)
        and adapter_result["alias_manifest_digest"]
        == alias_manifest["alias_manifest_digest"]
        and adapter_result["source_envelope"] == extracted
        and waiting_frame["source_digest"] == extracted["source_digest"]
        and waiting_dependency["frame_id"] == waiting_frame["frame_id"]
        and waiting_dependency["frame_digest"] == waiting_frame["frame_digest"]
        and waiting_dependency["source_digest"] == extracted["source_digest"]
    ):
        raise RayleenInvalidationReassemblyViolation(
            "adapter_frame_dependency_chain_invalid"
        )
    non_waiting_before = [
        item for item in parent["source_envelopes"] if item["frame_type"] != WAITING_FRAME_TYPE
    ]
    non_waiting_after = [
        item
        for item in adapted_parent["source_envelopes"]
        if item["frame_type"] != WAITING_FRAME_TYPE
    ]
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "source_frame_digest": canonical_sha256(source_frame),
            "alias_manifest_digest": alias_manifest["alias_manifest_digest"],
            "adapter_result_digest": adapter_result["adapter_result_digest"],
            "adapter_trace_digest": adapter_result["adapter_trace"][
                "adapter_trace_digest"
            ],
            "extracted_source_envelope_id": extracted["source_envelope_id"],
            "extracted_source_revision": extracted["source_revision"],
            "extracted_source_digest": extracted["source_digest"],
            "waiting_frame_id": waiting_frame["frame_id"],
            "waiting_frame_digest": waiting_frame["frame_digest"],
            "waiting_dependency_id": waiting_dependency["dependency_id"],
            "waiting_dependency_digest": waiting_dependency["dependency_digest"],
            "source_trace_digest": adapted_parent["source_trace"][
                "source_trace_digest"
            ],
            "rebuilt_frame_set_id": adapted_parent["frame_set"]["frame_set_id"],
            "rebuilt_frame_set_digest": adapted_parent["frame_set"][
                "frame_set_digest"
            ],
            "manifest_digest": manifest["manifest_digest"],
            "binding_digest": adapted_parent["authority_binding"]["binding_digest"],
            "grant_digest": adapted_parent["scope_grant"]["grant_digest"],
            "session_binding_digest": adapted_parent["authority_binding"][
                "session_binding_digest"
            ],
            "original_frame_set_digest": parent["frame_set"]["frame_set_digest"],
            "non_waiting_sources_before_digest": canonical_sha256(
                non_waiting_before
            ),
            "non_waiting_sources_after_digest": canonical_sha256(
                non_waiting_after
            ),
            "replacement_count": 1,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "adapter_binding_trace_digest",
    )


def _fresh_instruction(
    requirement: dict[str, Any], binding_trace: dict[str, Any]
) -> dict[str, Any]:
    _verify(requirement, "requirement_digest")
    _verify(binding_trace, "adapter_binding_trace_digest")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "instruction_id": "synthetic:fresh-context-reassembly:001",
            "requirement_digest": requirement["requirement_digest"],
            "superseded_frame_set_id": requirement["superseded_frame_set_id"],
            "superseded_frame_set_digest": requirement[
                "superseded_frame_set_digest"
            ],
            "manifest_digest": requirement["manifest_digest"],
            "lease_digest": requirement["lease_digest"],
            "adapter_binding_trace_digest": binding_trace[
                "adapter_binding_trace_digest"
            ],
            "adapter_result_digest": binding_trace["adapter_result_digest"],
            "waiting_source_digest": binding_trace["extracted_source_digest"],
            "waiting_frame_digest": binding_trace["waiting_frame_digest"],
            "session_generation": requirement["session_generation"],
            "request_revision": requirement["request_revision"],
            "ordered_steps": list(INSTRUCTION_STEPS),
            "issued_at": requirement["issued_at"],
            "expires_at": requirement["expires_at"],
            "execution_enabled": False,
            "source_read_executed": False,
            "returns_data": False,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "instruction_digest",
    )


def _validate_instruction(instruction: dict[str, Any]) -> None:
    _verify(instruction, "instruction_digest")
    expected_keys = {
        "schema_version", "instruction_id", "requirement_digest",
        "superseded_frame_set_id", "superseded_frame_set_digest",
        "manifest_digest", "lease_digest", "adapter_binding_trace_digest",
        "adapter_result_digest", "waiting_source_digest", "waiting_frame_digest",
        "session_generation", "request_revision", "ordered_steps", "issued_at",
        "expires_at", "execution_enabled", "source_read_executed", "returns_data",
        "read_only", "command_authority", "provider_authority", "instruction_digest",
    }
    if set(instruction) != expected_keys:
        raise RayleenInvalidationReassemblyViolation(
            "instruction_shape_invalid"
        )
    if type(instruction["session_generation"]) is not int or type(
        instruction["request_revision"]
    ) is not int:
        raise RayleenInvalidationReassemblyViolation(
            "instruction_integer_type_invalid"
        )
    if instruction["ordered_steps"] != INSTRUCTION_STEPS:
        raise RayleenInvalidationReassemblyViolation(
            "instruction_steps_invalid"
        )
    if (
        instruction["execution_enabled"] is not False
        or instruction["source_read_executed"] is not False
        or instruction["returns_data"] is not False
        or instruction["read_only"] is not True
        or instruction["command_authority"] is not False
        or instruction["provider_authority"] is not False
    ):
        raise RayleenInvalidationReassemblyViolation(
            "instruction_authority_invalid"
        )


def build_invalidation_reassembly_candidate(
    parent: dict[str, Any],
    source_frame: dict[str, Any],
    alias_manifest: dict[str, Any],
    adapter_result: dict[str, Any],
    *,
    assembled_at: str = ASSEMBLED_AT,
    observed_at: str = OBSERVED_AT,
) -> dict[str, Any]:
    """Reconstruct one closed pre-proof candidate from authoritative inputs."""

    parent_before = canonical_json(parent["frame_set"])
    adapted, extracted, parent_proofreader = _build_adapted_parent(
        parent,
        source_frame,
        alias_manifest,
        adapter_result,
        assembled_at=assembled_at,
    )
    manifest = derive_dependency_manifest(adapted)
    lease = derive_watch_lease(adapted, manifest)
    binding_trace = _binding_trace(
        parent=parent,
        adapted_parent=adapted,
        source_frame=source_frame,
        alias_manifest=alias_manifest,
        adapter_result=adapter_result,
        extracted=extracted,
        manifest=manifest,
    )
    signal = make_signal(
        signal_id="synthetic:signal:rayleen-waiting-101",
        event_type="diary.waiting_state_changed",
        aggregate_ref="synthetic:appointment:one",
        aggregate_revision=12,
        previous_transaction_position=100,
        transaction_position=101,
        location_refs=["synthetic:location:brisbane-one"],
        practitioner_refs=["synthetic:practitioner:one"],
        frame_types=[WAITING_FRAME_TYPE],
        practice_binding_digest=manifest["practice_binding_digest"],
        occurred_at="2026-08-06T03:00:10Z",
        received_at="2026-08-06T03:00:11Z",
    )
    state, requirement, checkpoint, decisions, transitions, temporal_trace = (
        process_signals(
            adapted,
            manifest,
            lease,
            [signal],
            observed_at=observed_at,
        )
    )
    if requirement is None:
        raise RayleenInvalidationReassemblyViolation(
            "reassembly_requirement_missing"
        )
    if canonical_json(parent["frame_set"]) != parent_before:
        raise RayleenInvalidationReassemblyViolation(
            "original_frame_set_mutated"
        )
    instruction = _fresh_instruction(requirement, binding_trace)
    _validate_instruction(instruction)
    stale = assess_reassembly_result(
        requirement,
        result_session_generation=requirement["session_generation"],
        result_request_revision=requirement["request_revision"],
        current_session_generation=requirement["session_generation"],
        current_request_revision=requirement["request_revision"] + 1,
    )
    if stale["decision"] != "REJECT_SUPERSEDED_REQUEST":
        raise RayleenInvalidationReassemblyViolation(
            "stale_request_not_rejected"
        )
    waiting_dependency = binding_trace["waiting_dependency_id"]
    if waiting_dependency not in requirement["required_dependency_ids"]:
        raise RayleenInvalidationReassemblyViolation(
            "waiting_dependency_not_required"
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "data_class": DATA_CLASS,
        "adapter_binding_trace": binding_trace,
        "dependency_manifest": manifest,
        "watch_lease": lease,
        "signal": signal,
        "invalidation_decisions": decisions,
        "watcher_transitions": transitions,
        "committed_checkpoint": checkpoint,
        "frame_set_state": state,
        "reassembly_requirement": requirement,
        "fresh_reassembly_instruction": instruction,
        "stale_reassembly_decision": stale,
        "temporal_trace": temporal_trace,
        "parent_proofreader_trace": parent_proofreader,
        "new_frame_set_admitted": False,
        "read_only": True,
        "command_authority": False,
        "provider_authority": False,
    }


def _proofreader_trace(
    candidate: dict[str, Any],
    expected: dict[str, Any] | None,
    *,
    checked_at: str,
    reasons: list[str],
) -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_digest": canonical_sha256(candidate),
            "trusted_reconstruction_digest": (
                canonical_sha256(expected) if expected is not None else None
            ),
            "checked_at": checked_at,
            "reason_codes": sorted(set(reasons)) if reasons else ["ALL_CHECKS_PASSED"],
            "release_decision": "BLOCK" if reasons else "RELEASE",
            "reconstructs_complete_candidate": True,
            "releases_trusted_deep_copy_only": True,
            "event_payload_used_as_truth": False,
            "source_read_executed": False,
            "new_frame_set_admitted": False,
            "read_only": True,
            "command_authority": False,
            "provider_authority": False,
        },
        "proofreader_trace_digest",
    )


def proofread_invalidation_reassembly_candidate(
    parent: dict[str, Any],
    source_frame: dict[str, Any],
    alias_manifest: dict[str, Any],
    adapter_result: dict[str, Any],
    candidate: dict[str, Any],
    *,
    assembled_at: str = ASSEMBLED_AT,
    observed_at: str = OBSERVED_AT,
    checked_at: str = CHECKED_AT,
) -> dict[str, Any]:
    """Release only a deep copy of complete trusted reconstruction."""

    reasons: list[str] = []
    expected: dict[str, Any] | None = None
    try:
        expected = build_invalidation_reassembly_candidate(
            parent,
            source_frame,
            alias_manifest,
            adapter_result,
            assembled_at=assembled_at,
            observed_at=observed_at,
        )
        _validate_closed_typed(candidate, expected)
        if canonical_json(candidate) != canonical_json(expected):
            reasons.append("CANDIDATE_RECONSTRUCTION_MISMATCH")
        if _instant(checked_at) >= _instant(expected["watch_lease"]["expires_at"]):
            reasons.append("CANDIDATE_EXPIRED")
        _validate_instruction(expected["fresh_reassembly_instruction"])
        if candidate.get("signal", {}).get("payload") is not None:
            reasons.append("SIGNAL_PAYLOAD_FORBIDDEN")
        if candidate.get("frame_set_state", {}).get("state") != (
            "REASSEMBLY_REQUIRED"
        ):
            reasons.append("STATE_NOT_MONOTONIC")
        if candidate.get("temporal_trace", {}).get(
            "parent_frame_set_unchanged"
        ) is not True:
            reasons.append("PARENT_FRAME_SET_MUTATED")
        if candidate.get("fresh_reassembly_instruction", {}).get(
            "execution_enabled"
        ) is not False:
            reasons.append("EXECUTABLE_INSTRUCTION_FORBIDDEN")
        if candidate.get("stale_reassembly_decision", {}).get("decision") != (
            "REJECT_SUPERSEDED_REQUEST"
        ):
            reasons.append("STALE_REQUEST_NOT_REJECTED")
    except (KeyError, TypeError, ValueError, ContractViolation) as error:
        reasons.append(f"CANDIDATE_INVALID:{type(error).__name__}")
    trace = _proofreader_trace(
        candidate, expected, checked_at=checked_at, reasons=reasons
    )
    released = None
    if not reasons and expected is not None:
        released = deepcopy(expected)
        released["proofreader_trace"] = deepcopy(trace)
    result = seal(
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
    return result


def build_authored_synthetic_invalidation_reassembly_packet() -> dict[str, Any]:
    """Build and proofread the sole authored-synthetic nominal packet."""

    parent = build_authored_synthetic_packet()
    source_frame = build_authored_synthetic_waiting_room_frame()
    alias_manifest = build_authored_synthetic_alias_manifest(
        source_frame, parent["authority_binding"], parent["scope_grant"]
    )
    adapter_result = adapt_waiting_room_source(
        source_frame,
        parent["authority_binding"],
        parent["scope_grant"],
        alias_manifest,
        assembled_at=ASSEMBLED_AT,
    )
    candidate = build_invalidation_reassembly_candidate(
        parent, source_frame, alias_manifest, adapter_result
    )
    result = proofread_invalidation_reassembly_candidate(
        parent, source_frame, alias_manifest, adapter_result, candidate
    )
    if result["release_decision"] != "RELEASE" or result["released_packet"] is None:
        raise RayleenInvalidationReassemblyViolation(
            "authored_synthetic_packet_not_released"
        )
    return deepcopy(result["released_packet"])


def validate_invalidation_reassembly_packet(packet: dict[str, Any]) -> None:
    """Validate the complete released packet against trusted reconstruction."""

    trusted = build_authored_synthetic_invalidation_reassembly_packet()
    _validate_closed_typed(packet, trusted)
    if canonical_json(packet) != canonical_json(trusted):
        raise InvalidationReassemblyViolation(
            "released_packet_reconstruction_mismatch"
        )
    _verify(packet["adapter_binding_trace"], "adapter_binding_trace_digest")
    _verify(packet["dependency_manifest"], "manifest_digest")
    _verify(packet["watch_lease"], "lease_digest")
    _verify(packet["signal"], "signal_digest")
    _verify(packet["frame_set_state"], "state_digest")
    _verify(packet["reassembly_requirement"], "requirement_digest")
    _verify(packet["stale_reassembly_decision"], "reassembly_decision_digest")
    _verify(packet["temporal_trace"], "temporal_trace_digest")
    _verify(packet["proofreader_trace"], "proofreader_trace_digest")
    _validate_instruction(packet["fresh_reassembly_instruction"])
    if packet["proofreader_trace"]["release_decision"] != "RELEASE":
        raise InvalidationReassemblyViolation("packet_not_released")


def proofread_invalidation_reassembly_packet(
    packet: dict[str, Any], *, checked_at: str = CHECKED_AT
) -> dict[str, Any]:
    """Reconstruct the full packet and release only the trusted deep copy."""

    reasons: list[str] = []
    expected: dict[str, Any] | None = None
    try:
        parent = build_authored_synthetic_packet()
        source_frame = build_authored_synthetic_waiting_room_frame()
        alias_manifest = build_authored_synthetic_alias_manifest(
            source_frame, parent["authority_binding"], parent["scope_grant"]
        )
        adapter_result = adapt_waiting_room_source(
            source_frame,
            parent["authority_binding"],
            parent["scope_grant"],
            alias_manifest,
            assembled_at=ASSEMBLED_AT,
        )
        candidate = build_invalidation_reassembly_candidate(
            parent, source_frame, alias_manifest, adapter_result
        )
        inner = proofread_invalidation_reassembly_candidate(
            parent,
            source_frame,
            alias_manifest,
            adapter_result,
            candidate,
            checked_at=checked_at,
        )
        expected = inner["released_packet"]
        if inner["release_decision"] != "RELEASE" or expected is None:
            reasons.append("TRUSTED_RECONSTRUCTION_NOT_RELEASED")
        else:
            _validate_closed_typed(packet, expected)
            if canonical_json(packet) != canonical_json(expected):
                reasons.append("PACKET_RECONSTRUCTION_MISMATCH")
            if _instant(checked_at) >= _instant(
                expected["watch_lease"]["expires_at"]
            ):
                reasons.append("PACKET_EXPIRED")
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


# Exact-instance JSON Schema: the canonical packet is itself the complete,
# recursively closed schema for this authored-synthetic seam.  The public
# validator additionally performs exact Python type checks before equality.
SEAM_PACKET_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Rayleen invalidation/reassembly seam packet",
    "const": build_authored_synthetic_invalidation_reassembly_packet(),
}


__all__ = [
    "ASSEMBLED_AT",
    "CHECKED_AT",
    "DATA_CLASS",
    "EVIDENCE_LABEL",
    "INSTRUCTION_STEPS",
    "InvalidationReassemblyViolation",
    "OBSERVED_AT",
    "RayleenInvalidationReassemblyViolation",
    "SCHEMA_VERSION",
    "SEAM_PACKET_SCHEMA",
    "build_authored_synthetic_invalidation_reassembly_packet",
    "build_invalidation_reassembly_candidate",
    "proofread_invalidation_reassembly_packet",
    "proofread_invalidation_reassembly_candidate",
    "validate_invalidation_reassembly_packet",
]
