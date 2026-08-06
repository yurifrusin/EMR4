"""Pure authored-synthetic rehearsal of the Context Fabric durability algebra.

This module has no application, database, source, network, provider, runtime,
command, persistence or deployment integration.  Values are immutable and all
transitions return a sealed copy only after their complete staged transaction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import hmac
import json
import re
from typing import Any, Literal


SCHEMA_VERSION = "emr4.context-fabric.durability-state-machine-rehearsal.v1"
EVIDENCE_LABEL = (
    "provider_free_unmounted_authored_synthetic_"
    "durability_state_machine_rehearsal"
)
RESULT = (
    "raisa_provider_free_unmounted_authored_synthetic_"
    "durability_state_machine_rehearsal_pass"
)
SOURCE_SYSTEM = "emr4-diary"
EVENT_TYPE = "diary.appointment_rescheduled"
EVENT_SCHEMA_VERSION = "diary.appointment_rescheduled.v1"
AGGREGATE_CLASS = "APPOINTMENT"
STREAM_ID = "emr4:diary:appointment-rescheduled:v1"
FRAME_TYPES = (
    "current_diary_projection",
    "current_waiting_room_projection",
)
DECISIONS = (
    "CONTIGUOUS_ADMIT",
    "CONTIGUOUS_NO_INTERSECTION",
    "CONTIGUOUS_FULL_INVALIDATION",
)
REASONS = ("RELEVANT", "NO_INTERSECTION", "CONSERVATIVE_FULL_INVALIDATION")
FAULT_MEMBERS = (
    "classified_observation_receipt",
    "monotonic_invalidation_watermark",
    "coalesced_reassembly_obligation",
    "privacy_safe_audit",
    "positive_checkpoint_advance_or_hold",
)
COUNT_BUCKETS = ("ONE", "TWO_TO_FOUR", "FIVE_PLUS")
CHECKPOINT_STATES = ("ACTIVE", "REBASE_REQUIRED", "CONSUMED", "REVOKED")
GENERATION_STATES = CHECKPOINT_STATES
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


class DurabilityViolation(ValueError):
    """A closed rehearsal contract was not satisfied."""


def canonical_bytes(value: Any) -> bytes:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def digest_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def synthetic_digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _opaque(value: object) -> bool:
    return (
        isinstance(value, str)
        and 3 <= len(value) <= 160
        and re.fullmatch(r"[a-z0-9][a-z0-9:._-]*", value) is not None
    )


@dataclass(frozen=True)
class KeyInterval:
    key_id: str
    start_position: int
    end_position: int | None


@dataclass(frozen=True)
class FrameGeneration:
    frame_generation_id: str
    frame_type: str
    assembled_through_position: int
    lifecycle: Literal["CURRENT", "RETIRED"]


@dataclass(frozen=True)
class ReassemblyObligation:
    frame_generation_id: str
    frame_type: str
    first_position: int
    latest_position: int
    rolling_cause_digest: str
    count_bucket: Literal["ONE", "TWO_TO_FOUR", "FIVE_PLUS"]


@dataclass(frozen=True)
class ClassifiedReceipt:
    position: int
    observation_digest: str
    decision: str
    reason: str
    affected_frame_types: tuple[str, ...]
    checkpoint_disposition: str


@dataclass(frozen=True)
class AuditRecord:
    audit_schema_version: str
    opaque_audit_id: str
    practice_binding_digest: str
    principal_digest: str
    policy_digest: str
    observer_binding_digest: str
    source_contract_digest: str
    registry_digest: str
    impact_policy_digest: str
    key_schedule_digest: str
    observer_id: str
    observer_generation: int
    stream_id: str
    stream_epoch: int
    position: int
    predecessor_position: int
    aggregate_class: str
    aggregate_revision: int
    observation_digest: str
    key_id: str
    decision: str
    reason: str
    affected_frame_types: tuple[str, ...]
    retired_count_bucket: str
    coalesced_count_bucket: str
    checkpoint_disposition: str
    lifecycle_revision: int
    prior_audit_digest: str


@dataclass(frozen=True)
class GenerationCensusMember:
    observer_generation: int
    checkpoint_position: int
    state: str


@dataclass(frozen=True)
class GenerationCensus:
    registry_digest: str
    members: tuple[GenerationCensusMember, ...]
    census_digest: str


@dataclass(frozen=True)
class DurabilityState:
    practice_binding_digest: str
    source_contract_digest: str
    stream_id: str
    stream_epoch: int
    observer_id: str
    observer_generation: int
    principal_digest: str
    policy_digest: str
    observer_binding_digest: str
    registry_digest: str
    impact_policy_digest: str
    key_schedule_digest: str
    checkpoint_state: str
    last_classified_position: int
    last_observation_digest: str
    lifecycle_revision: int
    frames: tuple[FrameGeneration, ...]
    watermarks: tuple[tuple[str, int], ...]
    obligations: tuple[ReassemblyObligation, ...]
    receipts: tuple[ClassifiedReceipt, ...]
    audits: tuple[AuditRecord, ...]
    key_schedule: tuple[KeyInterval, ...]
    generation_census: GenerationCensus
    integrity_digest: str


@dataclass(frozen=True)
class Candidate:
    practice_binding_digest: str
    source_contract_digest: str
    stream_id: str
    stream_epoch: int
    observer_id: str
    observer_generation: int
    policy_digest: str
    observer_binding_digest: str
    registry_digest: str
    impact_policy_digest: str
    key_schedule_digest: str
    position: int
    predecessor_position: int
    observation_digest: str
    aggregate_revision: int
    key_id: str
    decision: str
    reason: str
    affected_frame_types: tuple[str, ...]


@dataclass(frozen=True)
class TransitionResult:
    disposition: str
    state: DurabilityState
    receipt: ClassifiedReceipt | None
    mutation_committed: bool


@dataclass(frozen=True)
class RecoveryAnchor:
    practice_binding_digest: str
    source_contract_digest: str
    stream_id: str
    stream_epoch: int
    observer_id: str
    observer_generation: int
    principal_digest: str
    policy_digest: str
    observer_binding_digest: str
    registry_digest: str
    impact_policy_digest: str
    key_schedule_digest: str
    last_classified_position: int
    last_observation_digest: str


@dataclass(frozen=True)
class RetainedRow:
    available: bool
    position: int
    predecessor_position: int
    observation_digest: str
    key_id: str


@dataclass(frozen=True)
class RestartResult:
    disposition: Literal["RESUME", "REBASE_REQUIRED", "NEW_GENERATION_REQUIRED"]
    state: DurabilityState | None


@dataclass(frozen=True)
class KeyScheduleTransition:
    predecessor_schedule_digest: str
    successor_schedule: tuple[KeyInterval, ...]
    activation_position: int
    predecessor_key_id: str
    successor_key_id: str
    maximum_dependent_position: int
    predecessor_key_available_through_position: int
    safety_overlap_positions: int


@dataclass(frozen=True)
class RotationResult:
    disposition: Literal["ROTATION_COMMITTED", "REBASE_REQUIRED"]
    state: DurabilityState


@dataclass(frozen=True)
class RetentionResult:
    disposition: Literal["ELIGIBLE", "DENIED"]
    reasons: tuple[str, ...]
    deletion_executed: Literal[False] = False


def _census_body(census: GenerationCensus) -> dict[str, Any]:
    return {
        "registry_digest": census.registry_digest,
        "members": [asdict(member) for member in census.members],
    }


def seal_census(census: GenerationCensus) -> GenerationCensus:
    return replace(census, census_digest=digest_value(_census_body(census)))


def verify_census(census: GenerationCensus) -> bool:
    if not _is_digest(census.registry_digest):
        return False
    if not hmac.compare_digest(census.census_digest, digest_value(_census_body(census))):
        return False
    generations = [member.observer_generation for member in census.members]
    if generations != sorted(generations) or len(generations) != len(set(generations)):
        return False
    return all(
        type(member.observer_generation) is int
        and member.observer_generation > 0
        and type(member.checkpoint_position) is int
        and member.checkpoint_position >= 0
        and member.state in GENERATION_STATES
        for member in census.members
    )


def _state_body(state: DurabilityState) -> dict[str, Any]:
    body = asdict(state)
    body.pop("integrity_digest")
    return body


def seal_state(state: DurabilityState) -> DurabilityState:
    return replace(state, integrity_digest=digest_value(_state_body(state)))


def verify_state(state: DurabilityState) -> bool:
    if not _is_digest(state.integrity_digest):
        return False
    if not hmac.compare_digest(state.integrity_digest, digest_value(_state_body(state))):
        return False
    if not verify_census(state.generation_census):
        return False
    if state.generation_census.registry_digest != state.registry_digest:
        return False
    controlling_digests = (
        state.practice_binding_digest,
        state.source_contract_digest,
        state.principal_digest,
        state.policy_digest,
        state.observer_binding_digest,
        state.registry_digest,
        state.impact_policy_digest,
        state.key_schedule_digest,
        state.last_observation_digest,
    )
    if not all(_is_digest(item) for item in controlling_digests):
        return False
    if not _opaque(state.stream_id) or not _opaque(state.observer_id):
        return False
    if (
        type(state.stream_epoch) is not int
        or state.stream_epoch < 1
        or type(state.observer_generation) is not int
        or state.observer_generation < 1
        or type(state.last_classified_position) is not int
        or state.last_classified_position < 0
        or type(state.lifecycle_revision) is not int
        or state.lifecycle_revision < 1
    ):
        return False
    if state.checkpoint_state not in CHECKPOINT_STATES:
        return False
    if tuple(frame_type for frame_type, _ in state.watermarks) != FRAME_TYPES:
        return False
    if len({frame.frame_generation_id for frame in state.frames}) != len(state.frames):
        return False
    if len({item.frame_generation_id for item in state.obligations}) != len(state.obligations):
        return False
    if len({item.position for item in state.receipts}) != len(state.receipts):
        return False
    if not validate_key_schedule(state.key_schedule):
        return False
    if not hmac.compare_digest(
        state.key_schedule_digest,
        digest_value([asdict(item) for item in state.key_schedule]),
    ):
        return False
    watermarks = dict(state.watermarks)
    if any(type(value) is not int or value < 0 for value in watermarks.values()):
        return False
    for frame in state.frames:
        if (
            not _opaque(frame.frame_generation_id)
            or frame.frame_type not in FRAME_TYPES
            or type(frame.assembled_through_position) is not int
            or frame.assembled_through_position < 0
            or frame.lifecycle not in ("CURRENT", "RETIRED")
        ):
            return False
        if (
            watermarks[frame.frame_type] > frame.assembled_through_position
            and frame.lifecycle != "RETIRED"
        ):
            return False
    frames_by_id = {frame.frame_generation_id: frame for frame in state.frames}
    for obligation in state.obligations:
        frame = frames_by_id.get(obligation.frame_generation_id)
        if (
            frame is None
            or frame.lifecycle != "RETIRED"
            or obligation.frame_type != frame.frame_type
            or obligation.count_bucket not in COUNT_BUCKETS
            or not _is_digest(obligation.rolling_cause_digest)
            or type(obligation.first_position) is not int
            or type(obligation.latest_position) is not int
            or obligation.first_position < 1
            or obligation.latest_position < obligation.first_position
        ):
            return False
    for receipt in state.receipts:
        if (
            type(receipt.position) is not int
            or receipt.position < 1
            or receipt.position > state.last_classified_position
            or not _is_digest(receipt.observation_digest)
            or receipt.decision not in DECISIONS
            or receipt.reason not in REASONS
            or any(item not in FRAME_TYPES for item in receipt.affected_frame_types)
            or receipt.checkpoint_disposition
            not in (
                "ADVANCE_AFTER_ATOMIC_COMMIT",
                "ADVANCE_AFTER_RECEIPT_AND_AUDIT",
            )
        ):
            return False
        if receipt.decision == "CONTIGUOUS_ADMIT" and (
            receipt.reason != "RELEVANT" or not receipt.affected_frame_types
        ):
            return False
        if receipt.decision == "CONTIGUOUS_NO_INTERSECTION" and (
            receipt.reason != "NO_INTERSECTION" or receipt.affected_frame_types
        ):
            return False
        if receipt.decision == "CONTIGUOUS_FULL_INVALIDATION" and (
            receipt.reason != "CONSERVATIVE_FULL_INVALIDATION"
            or receipt.affected_frame_types != FRAME_TYPES
        ):
            return False
    last_receipt = next(
        (item for item in state.receipts if item.position == state.last_classified_position),
        None,
    )
    if last_receipt is None or not hmac.compare_digest(
        last_receipt.observation_digest, state.last_observation_digest
    ):
        return False
    census_current = [
        member
        for member in state.generation_census.members
        if member.observer_generation == state.observer_generation
    ]
    if (
        len(census_current) != 1
        or census_current[0].checkpoint_position != state.last_classified_position
        or census_current[0].state != state.checkpoint_state
    ):
        return False
    return all(_audit_valid(item, state) for item in state.audits)


def _audit_valid(audit: AuditRecord, state: DurabilityState) -> bool:
    return (
        audit.audit_schema_version == "emr4.context-fabric.durability-audit.v1"
        and _opaque(audit.opaque_audit_id)
        and audit.practice_binding_digest == state.practice_binding_digest
        and audit.principal_digest == state.principal_digest
        and audit.source_contract_digest == state.source_contract_digest
        and audit.observer_id == state.observer_id
        and audit.observer_generation == state.observer_generation
        and audit.stream_id == state.stream_id
        and audit.stream_epoch == state.stream_epoch
        and type(audit.position) is int
        and audit.position >= 1
        and type(audit.predecessor_position) is int
        and audit.predecessor_position >= 0
        and audit.aggregate_class == AGGREGATE_CLASS
        and type(audit.aggregate_revision) is int
        and audit.aggregate_revision >= 1
        and _is_digest(audit.observation_digest)
        and _opaque(audit.key_id)
        and audit.decision in (*DECISIONS, "FULL_INVALIDATION_REQUIRED")
        and audit.reason
        in (
            *REASONS,
            "SAME_POSITION_IDENTITY_MISMATCH",
            "OBSERVATION_DIGEST_REUSED",
            "COVERAGE_GAP",
            "RESTART_CONTINUITY_UNCERTAIN",
            "KEY_SCHEDULE_UNVERIFIABLE",
        )
        and all(
            _is_digest(item)
            for item in (
                audit.policy_digest,
                audit.observer_binding_digest,
                audit.registry_digest,
                audit.impact_policy_digest,
                audit.key_schedule_digest,
                audit.prior_audit_digest,
            )
        )
        and all(item in FRAME_TYPES for item in audit.affected_frame_types)
        and audit.retired_count_bucket in ("ZERO", *COUNT_BUCKETS)
        and audit.coalesced_count_bucket in ("ZERO", *COUNT_BUCKETS)
        and type(audit.lifecycle_revision) is int
        and audit.lifecycle_revision >= 1
    )


def validate_key_schedule(schedule: tuple[KeyInterval, ...]) -> bool:
    if not schedule or schedule[0].start_position != 0:
        return False
    for index, interval in enumerate(schedule):
        if not _opaque(interval.key_id) or type(interval.start_position) is not int:
            return False
        if interval.start_position < 0:
            return False
        final = index == len(schedule) - 1
        if final != (interval.end_position is None):
            return False
        if interval.end_position is not None:
            if type(interval.end_position) is not int or interval.end_position <= interval.start_position:
                return False
            if schedule[index + 1].start_position != interval.end_position:
                return False
    return True


def key_for_position(schedule: tuple[KeyInterval, ...], position: int) -> str | None:
    if not validate_key_schedule(schedule) or type(position) is not int or position < 0:
        return None
    matches = [
        item.key_id
        for item in schedule
        if item.start_position <= position
        and (item.end_position is None or position < item.end_position)
    ]
    return matches[0] if len(matches) == 1 else None


def _watermarks(state: DurabilityState) -> dict[str, int]:
    return dict(state.watermarks)


def _binding_matches(state: DurabilityState, candidate: Candidate) -> bool:
    return (
        candidate.practice_binding_digest == state.practice_binding_digest
        and candidate.source_contract_digest == state.source_contract_digest
        and candidate.stream_id == state.stream_id
        and candidate.observer_id == state.observer_id
        and candidate.observer_generation == state.observer_generation
        and candidate.policy_digest == state.policy_digest
        and candidate.observer_binding_digest == state.observer_binding_digest
        and candidate.registry_digest == state.registry_digest
        and candidate.impact_policy_digest == state.impact_policy_digest
        and candidate.key_schedule_digest == state.key_schedule_digest
    )


def _candidate_valid(candidate: Candidate) -> bool:
    digests = (
        candidate.practice_binding_digest,
        candidate.source_contract_digest,
        candidate.policy_digest,
        candidate.observer_binding_digest,
        candidate.registry_digest,
        candidate.impact_policy_digest,
        candidate.key_schedule_digest,
        candidate.observation_digest,
    )
    if not all(_is_digest(item) for item in digests):
        return False
    if not _opaque(candidate.stream_id) or not _opaque(candidate.observer_id):
        return False
    integers = (
        candidate.stream_epoch,
        candidate.observer_generation,
        candidate.position,
        candidate.predecessor_position,
        candidate.aggregate_revision,
    )
    if not all(type(item) is int for item in integers):
        return False
    if candidate.stream_epoch < 1 or candidate.observer_generation < 1:
        return False
    if candidate.position < 1 or candidate.predecessor_position < 0:
        return False
    if candidate.aggregate_revision < 1 or not _opaque(candidate.key_id):
        return False
    if candidate.decision not in DECISIONS or candidate.reason not in REASONS:
        return False
    if len(set(candidate.affected_frame_types)) != len(candidate.affected_frame_types):
        return False
    if any(item not in FRAME_TYPES for item in candidate.affected_frame_types):
        return False
    expected = {
        "CONTIGUOUS_ADMIT": ("RELEVANT", True),
        "CONTIGUOUS_NO_INTERSECTION": ("NO_INTERSECTION", False),
        "CONTIGUOUS_FULL_INVALIDATION": ("CONSERVATIVE_FULL_INVALIDATION", True),
    }[candidate.decision]
    if candidate.reason != expected[0]:
        return False
    if candidate.decision == "CONTIGUOUS_ADMIT":
        return bool(candidate.affected_frame_types)
    if candidate.decision == "CONTIGUOUS_NO_INTERSECTION":
        return not candidate.affected_frame_types
    return candidate.affected_frame_types == FRAME_TYPES


def _next_bucket(bucket: str) -> str:
    if bucket == "ONE":
        return "TWO_TO_FOUR"
    return "FIVE_PLUS"


def _bucket_count(value: int) -> str:
    if value == 0:
        return "ZERO"
    if value == 1:
        return "ONE"
    if value <= 4:
        return "TWO_TO_FOUR"
    return "FIVE_PLUS"


def _retire_and_obligate(
    state: DurabilityState,
    *,
    affected: tuple[str, ...],
    position: int,
    cause_digest: str,
    force_all: bool,
) -> tuple[tuple[FrameGeneration, ...], tuple[tuple[str, int], ...], tuple[ReassemblyObligation, ...], int, int]:
    watermarks = _watermarks(state)
    for frame_type in affected:
        watermarks[frame_type] = max(watermarks[frame_type], position)
    prior_obligations = {item.frame_generation_id: item for item in state.obligations}
    frames: list[FrameGeneration] = []
    retired = 0
    coalesced = 0
    for frame in state.frames:
        should_retire = frame.frame_type in affected and (
            force_all or watermarks[frame.frame_type] > frame.assembled_through_position
        )
        updated = frame
        if frame.lifecycle == "CURRENT" and should_retire:
            updated = replace(frame, lifecycle="RETIRED")
            retired += 1
        frames.append(updated)
        if updated.lifecycle != "RETIRED" or not should_retire:
            continue
        existing = prior_obligations.get(frame.frame_generation_id)
        if existing is None:
            prior_obligations[frame.frame_generation_id] = ReassemblyObligation(
                frame_generation_id=frame.frame_generation_id,
                frame_type=frame.frame_type,
                first_position=position,
                latest_position=position,
                rolling_cause_digest=digest_value(
                    ["obligation", frame.frame_generation_id, cause_digest, position]
                ),
                count_bucket="ONE",
            )
        elif position > existing.latest_position:
            prior_obligations[frame.frame_generation_id] = replace(
                existing,
                latest_position=position,
                rolling_cause_digest=digest_value(
                    [existing.rolling_cause_digest, cause_digest, position]
                ),
                count_bucket=_next_bucket(existing.count_bucket),
            )
            coalesced += 1
    return (
        tuple(frames),
        tuple((frame_type, watermarks[frame_type]) for frame_type in FRAME_TYPES),
        tuple(sorted(prior_obligations.values(), key=lambda item: item.frame_generation_id)),
        retired,
        coalesced,
    )


def _audit(
    state: DurabilityState,
    *,
    position: int,
    predecessor: int,
    observation_digest: str,
    aggregate_revision: int,
    key_id: str,
    decision: str,
    reason: str,
    affected: tuple[str, ...],
    retired: int,
    coalesced: int,
    checkpoint_disposition: str,
) -> AuditRecord:
    prior = digest_value(asdict(state.audits[-1])) if state.audits else synthetic_digest("audit:genesis")
    return AuditRecord(
        audit_schema_version="emr4.context-fabric.durability-audit.v1",
        opaque_audit_id="audit:" + digest_value([state.observer_generation, position, observation_digest])[7:31],
        practice_binding_digest=state.practice_binding_digest,
        principal_digest=state.principal_digest,
        policy_digest=state.policy_digest,
        observer_binding_digest=state.observer_binding_digest,
        source_contract_digest=state.source_contract_digest,
        registry_digest=state.registry_digest,
        impact_policy_digest=state.impact_policy_digest,
        key_schedule_digest=state.key_schedule_digest,
        observer_id=state.observer_id,
        observer_generation=state.observer_generation,
        stream_id=state.stream_id,
        stream_epoch=state.stream_epoch,
        position=position,
        predecessor_position=predecessor,
        aggregate_class=AGGREGATE_CLASS,
        aggregate_revision=aggregate_revision,
        observation_digest=observation_digest,
        key_id=key_id,
        decision=decision,
        reason=reason,
        affected_frame_types=affected,
        retired_count_bucket=_bucket_count(retired),
        coalesced_count_bucket=_bucket_count(coalesced),
        checkpoint_disposition=checkpoint_disposition,
        lifecycle_revision=state.lifecycle_revision + 1,
        prior_audit_digest=prior,
    )


def _force_rebase(
    state: DurabilityState,
    *,
    unsafe_position: int,
    predecessor: int,
    cause_digest: str,
    aggregate_revision: int,
    key_id: str,
    reason: str,
) -> DurabilityState:
    position = max(state.last_classified_position + 1, unsafe_position)
    frames, watermarks, obligations, retired, coalesced = _retire_and_obligate(
        state,
        affected=FRAME_TYPES,
        position=position,
        cause_digest=cause_digest,
        force_all=True,
    )
    audit = _audit(
        state,
        position=position,
        predecessor=predecessor,
        observation_digest=cause_digest,
        aggregate_revision=max(1, aggregate_revision),
        key_id=key_id if _opaque(key_id) else "key:unavailable",
        decision="FULL_INVALIDATION_REQUIRED",
        reason=reason,
        affected=FRAME_TYPES,
        retired=retired,
        coalesced=coalesced,
        checkpoint_disposition="HOLD_AND_REBASE",
    )
    census = seal_census(
        replace(
            state.generation_census,
            members=tuple(
                replace(member, state="REBASE_REQUIRED")
                if member.observer_generation == state.observer_generation
                else member
                for member in state.generation_census.members
            ),
            census_digest="",
        )
    )
    return seal_state(
        replace(
            state,
            checkpoint_state="REBASE_REQUIRED",
            lifecycle_revision=state.lifecycle_revision + 1,
            frames=frames,
            watermarks=watermarks,
            obligations=obligations,
            audits=state.audits + (audit,),
            generation_census=census,
            integrity_digest="",
        )
    )


def transition(
    state: DurabilityState,
    candidate: Candidate,
    *,
    fail_before: str | None = None,
) -> TransitionResult:
    if fail_before is not None and fail_before not in FAULT_MEMBERS:
        raise DurabilityViolation("unknown_fault_member")
    if not verify_state(state) or not _candidate_valid(candidate):
        return TransitionResult("STOP_GENERATION", state, None, False)
    if not _binding_matches(state, candidate) or state.checkpoint_state != "ACTIVE":
        return TransitionResult("STOP_GENERATION", state, None, False)

    receipts_by_position = {item.position: item for item in state.receipts}
    if candidate.position <= state.last_classified_position:
        receipt = receipts_by_position.get(candidate.position)
        if receipt is not None and hmac.compare_digest(
            receipt.observation_digest, candidate.observation_digest
        ):
            return TransitionResult("EXACT_REDELIVERY", state, receipt, False)
        rebased = _force_rebase(
            state,
            unsafe_position=candidate.position,
            predecessor=candidate.predecessor_position,
            cause_digest=candidate.observation_digest,
            aggregate_revision=candidate.aggregate_revision,
            key_id=candidate.key_id,
            reason="SAME_POSITION_IDENTITY_MISMATCH",
        )
        return TransitionResult("REBASE_REQUIRED", rebased, None, True)

    digest_reused = any(
        hmac.compare_digest(item.observation_digest, candidate.observation_digest)
        for item in state.receipts
    )
    continuity_invalid = (
        candidate.stream_epoch != state.stream_epoch
        or candidate.position != state.last_classified_position + 1
        or candidate.predecessor_position != state.last_classified_position
        or key_for_position(state.key_schedule, candidate.position) != candidate.key_id
    )
    if digest_reused or continuity_invalid:
        reason = "OBSERVATION_DIGEST_REUSED" if digest_reused else "COVERAGE_GAP"
        rebased = _force_rebase(
            state,
            unsafe_position=candidate.position,
            predecessor=candidate.predecessor_position,
            cause_digest=candidate.observation_digest,
            aggregate_revision=candidate.aggregate_revision,
            key_id=candidate.key_id,
            reason=reason,
        )
        return TransitionResult("REBASE_REQUIRED", rebased, None, True)

    if fail_before == FAULT_MEMBERS[0]:
        return TransitionResult("ROLLED_BACK", state, None, False)
    checkpoint_disposition = (
        "ADVANCE_AFTER_RECEIPT_AND_AUDIT"
        if candidate.decision == "CONTIGUOUS_NO_INTERSECTION"
        else "ADVANCE_AFTER_ATOMIC_COMMIT"
    )
    receipt = ClassifiedReceipt(
        position=candidate.position,
        observation_digest=candidate.observation_digest,
        decision=candidate.decision,
        reason=candidate.reason,
        affected_frame_types=candidate.affected_frame_types,
        checkpoint_disposition=checkpoint_disposition,
    )
    receipts = state.receipts + (receipt,)

    if fail_before == FAULT_MEMBERS[1]:
        return TransitionResult("ROLLED_BACK", state, None, False)
    force_all = candidate.decision == "CONTIGUOUS_FULL_INVALIDATION"
    frames, watermarks, obligations, retired, coalesced = _retire_and_obligate(
        state,
        affected=candidate.affected_frame_types,
        position=candidate.position,
        cause_digest=candidate.observation_digest,
        force_all=force_all,
    )

    if fail_before == FAULT_MEMBERS[2]:
        return TransitionResult("ROLLED_BACK", state, None, False)
    if fail_before == FAULT_MEMBERS[3]:
        return TransitionResult("ROLLED_BACK", state, None, False)
    audit = _audit(
        state,
        position=candidate.position,
        predecessor=candidate.predecessor_position,
        observation_digest=candidate.observation_digest,
        aggregate_revision=candidate.aggregate_revision,
        key_id=candidate.key_id,
        decision=candidate.decision,
        reason=candidate.reason,
        affected=candidate.affected_frame_types,
        retired=retired,
        coalesced=coalesced,
        checkpoint_disposition=checkpoint_disposition,
    )

    if fail_before == FAULT_MEMBERS[4]:
        return TransitionResult("ROLLED_BACK", state, None, False)
    census_members = tuple(
        replace(
            member,
            checkpoint_position=candidate.position,
            state="ACTIVE",
        )
        if member.observer_generation == state.observer_generation
        else member
        for member in state.generation_census.members
    )
    census = seal_census(replace(state.generation_census, members=census_members, census_digest=""))
    successor = seal_state(
        replace(
            state,
            last_classified_position=candidate.position,
            last_observation_digest=candidate.observation_digest,
            lifecycle_revision=state.lifecycle_revision + 1,
            frames=frames,
            watermarks=watermarks,
            obligations=obligations,
            receipts=receipts,
            audits=state.audits + (audit,),
            generation_census=census,
            integrity_digest="",
        )
    )
    return TransitionResult(checkpoint_disposition, successor, receipt, True)


def recovery_anchor(state: DurabilityState) -> RecoveryAnchor:
    return RecoveryAnchor(
        practice_binding_digest=state.practice_binding_digest,
        source_contract_digest=state.source_contract_digest,
        stream_id=state.stream_id,
        stream_epoch=state.stream_epoch,
        observer_id=state.observer_id,
        observer_generation=state.observer_generation,
        principal_digest=state.principal_digest,
        policy_digest=state.policy_digest,
        observer_binding_digest=state.observer_binding_digest,
        registry_digest=state.registry_digest,
        impact_policy_digest=state.impact_policy_digest,
        key_schedule_digest=state.key_schedule_digest,
        last_classified_position=state.last_classified_position,
        last_observation_digest=state.last_observation_digest,
    )


def restart(
    state: DurabilityState | None,
    anchor: RecoveryAnchor,
    row: RetainedRow | None,
) -> RestartResult:
    if state is None or not verify_state(state):
        return RestartResult("NEW_GENERATION_REQUIRED", None)
    if recovery_anchor(state) != anchor or state.checkpoint_state != "ACTIVE":
        return RestartResult("NEW_GENERATION_REQUIRED", None)
    invalid = (
        row is None
        or not row.available
        or row.position != anchor.last_classified_position + 1
        or row.predecessor_position != anchor.last_classified_position
        or not _is_digest(row.observation_digest)
        or key_for_position(state.key_schedule, row.position) != row.key_id
    )
    if invalid:
        unsafe = row.position if row is not None and type(row.position) is int else anchor.last_classified_position + 1
        digest = row.observation_digest if row is not None and _is_digest(row.observation_digest) else synthetic_digest("restart:retention-loss")
        key_id = row.key_id if row is not None else "key:unavailable"
        rebased = _force_rebase(
            state,
            unsafe_position=unsafe,
            predecessor=anchor.last_classified_position,
            cause_digest=digest,
            aggregate_revision=1,
            key_id=key_id,
            reason="RESTART_CONTINUITY_UNCERTAIN",
        )
        return RestartResult("REBASE_REQUIRED", rebased)
    return RestartResult("RESUME", state)


def apply_key_rotation(
    state: DurabilityState,
    rotation: KeyScheduleTransition,
) -> RotationResult:
    integer_fields = (
        rotation.activation_position,
        rotation.maximum_dependent_position,
        rotation.predecessor_key_available_through_position,
        rotation.safety_overlap_positions,
    )
    valid = all(type(item) is int and item >= 0 for item in integer_fields)
    valid = (
        valid
        and _is_digest(rotation.predecessor_schedule_digest)
        and _opaque(rotation.predecessor_key_id)
        and _opaque(rotation.successor_key_id)
    )
    valid = valid and verify_state(state) and validate_key_schedule(rotation.successor_schedule)
    valid = valid and hmac.compare_digest(
        rotation.predecessor_schedule_digest, digest_value([asdict(item) for item in state.key_schedule])
    )
    valid = valid and rotation.activation_position > state.last_classified_position
    valid = valid and rotation.safety_overlap_positions >= 0
    valid = valid and key_for_position(state.key_schedule, rotation.activation_position - 1) == rotation.predecessor_key_id
    valid = valid and key_for_position(rotation.successor_schedule, rotation.activation_position) == rotation.successor_key_id
    if valid:
        for position in range(rotation.activation_position):
            if key_for_position(state.key_schedule, position) != key_for_position(rotation.successor_schedule, position):
                valid = False
                break
    if valid:
        required_availability = max(
            rotation.maximum_dependent_position,
            rotation.activation_position - 1,
        ) + rotation.safety_overlap_positions
        valid = (
            rotation.predecessor_key_available_through_position
            >= required_availability
        )
    if not valid:
        activation = (
            rotation.activation_position
            if type(rotation.activation_position) is int
            else state.last_classified_position + 1
        )
        rebased = _force_rebase(
            state,
            unsafe_position=max(state.last_classified_position + 1, activation),
            predecessor=state.last_classified_position,
            cause_digest=synthetic_digest("key-rotation:invalid"),
            aggregate_revision=1,
            key_id="key:unavailable",
            reason="KEY_SCHEDULE_UNVERIFIABLE",
        )
        return RotationResult("REBASE_REQUIRED", rebased)
    successor_digest = digest_value([asdict(item) for item in rotation.successor_schedule])
    return RotationResult(
        "ROTATION_COMMITTED",
        seal_state(
            replace(
                state,
                key_schedule=rotation.successor_schedule,
                key_schedule_digest=successor_digest,
                lifecycle_revision=state.lifecycle_revision + 1,
                integrity_digest="",
            )
        ),
    )


def retention_eligibility(
    state: DurabilityState,
    *,
    source_row_position: int,
    expected_census_digest: str,
    expected_registry_digest: str,
    recovery_pin: bool,
    audit_pin: bool,
    key_overlap_closed: bool,
    safety_grace_elapsed: bool,
) -> RetentionResult:
    reasons: list[str] = []
    census = state.generation_census
    if type(source_row_position) is not int or source_row_position < 0:
        reasons.append("SOURCE_ROW_POSITION_INVALID")
    if not verify_state(state) or not verify_census(census):
        reasons.append("STATE_OR_CENSUS_INTEGRITY_INVALID")
    if not hmac.compare_digest(census.census_digest, expected_census_digest):
        reasons.append("COMPLETE_CENSUS_DIGEST_MISMATCH")
    if not hmac.compare_digest(census.registry_digest, expected_registry_digest):
        reasons.append("REGISTRY_DIGEST_MISMATCH")
    active = [member for member in census.members if member.state != "CONSUMED"]
    if not active:
        reasons.append("NO_NON_CONSUMED_GENERATION")
    elif (
        type(source_row_position) is int
        and min(member.checkpoint_position for member in active) < source_row_position
    ):
        reasons.append("MINIMUM_CHECKPOINT_BEHIND_ROW")
    if recovery_pin:
        reasons.append("RECOVERY_PIN_PRESENT")
    if audit_pin:
        reasons.append("AUDIT_PIN_PRESENT")
    if not key_overlap_closed:
        reasons.append("KEY_OVERLAP_OPEN")
    if not safety_grace_elapsed:
        reasons.append("SAFETY_GRACE_PENDING")
    return RetentionResult("DENIED" if reasons else "ELIGIBLE", tuple(reasons))


def build_initial_state() -> DurabilityState:
    registry = synthetic_digest("registry:v1")
    schedule = (KeyInterval("key:alpha", 0, None),)
    census = seal_census(
        GenerationCensus(
            registry_digest=registry,
            members=(
                GenerationCensusMember(1, 0, "ACTIVE"),
                GenerationCensusMember(2, 4, "ACTIVE"),
            ),
            census_digest="",
        )
    )
    state = DurabilityState(
        practice_binding_digest=synthetic_digest("practice:synthetic"),
        source_contract_digest=synthetic_digest("source-contract:v1"),
        stream_id=STREAM_ID,
        stream_epoch=1,
        observer_id="observer:synthetic",
        observer_generation=2,
        principal_digest=synthetic_digest("principal:durability-coordinator"),
        policy_digest=synthetic_digest("policy:v1"),
        observer_binding_digest=synthetic_digest("observer-binding:v1"),
        registry_digest=registry,
        impact_policy_digest=synthetic_digest("impact:v1"),
        key_schedule_digest=digest_value([asdict(item) for item in schedule]),
        checkpoint_state="ACTIVE",
        last_classified_position=4,
        last_observation_digest=synthetic_digest("observation:4"),
        lifecycle_revision=1,
        frames=(
            FrameGeneration("frame:diary:1", FRAME_TYPES[0], 4, "CURRENT"),
            FrameGeneration("frame:waiting:1", FRAME_TYPES[1], 4, "CURRENT"),
        ),
        watermarks=((FRAME_TYPES[0], 0), (FRAME_TYPES[1], 0)),
        obligations=(),
        receipts=(
            ClassifiedReceipt(
                4,
                synthetic_digest("observation:4"),
                "CONTIGUOUS_NO_INTERSECTION",
                "NO_INTERSECTION",
                (),
                "ADVANCE_AFTER_RECEIPT_AND_AUDIT",
            ),
        ),
        audits=(),
        key_schedule=schedule,
        generation_census=census,
        integrity_digest="",
    )
    return seal_state(state)


def candidate_for(
    state: DurabilityState,
    *,
    position: int,
    decision: str = "CONTIGUOUS_ADMIT",
    affected_frame_types: tuple[str, ...] = (FRAME_TYPES[0],),
    digest_label: str | None = None,
) -> Candidate:
    reason = {
        "CONTIGUOUS_ADMIT": "RELEVANT",
        "CONTIGUOUS_NO_INTERSECTION": "NO_INTERSECTION",
        "CONTIGUOUS_FULL_INVALIDATION": "CONSERVATIVE_FULL_INVALIDATION",
    }[decision]
    if decision == "CONTIGUOUS_NO_INTERSECTION":
        affected_frame_types = ()
    elif decision == "CONTIGUOUS_FULL_INVALIDATION":
        affected_frame_types = FRAME_TYPES
    return Candidate(
        practice_binding_digest=state.practice_binding_digest,
        source_contract_digest=state.source_contract_digest,
        stream_id=state.stream_id,
        stream_epoch=state.stream_epoch,
        observer_id=state.observer_id,
        observer_generation=state.observer_generation,
        policy_digest=state.policy_digest,
        observer_binding_digest=state.observer_binding_digest,
        registry_digest=state.registry_digest,
        impact_policy_digest=state.impact_policy_digest,
        key_schedule_digest=state.key_schedule_digest,
        position=position,
        predecessor_position=state.last_classified_position,
        observation_digest=synthetic_digest(digest_label or f"observation:{position}"),
        aggregate_revision=position,
        key_id=key_for_position(state.key_schedule, position) or "key:unavailable",
        decision=decision,
        reason=reason,
        affected_frame_types=affected_frame_types,
    )


EFFECT_CEILINGS = {
    "database_or_source_contact": False,
    "migration_or_database_object": False,
    "operational_checkpoint_persisted": False,
    "product_read": False,
    "patient_or_product_data": False,
    "provider_called": False,
    "command_executed": False,
    "runtime_wired": False,
    "deployment_or_release": False,
    "pages_rebuilt": False,
    "protected_ref_moved": False,
}


__all__ = [
    "AGGREGATE_CLASS",
    "Candidate",
    "ClassifiedReceipt",
    "DurabilityState",
    "DurabilityViolation",
    "EFFECT_CEILINGS",
    "EVIDENCE_LABEL",
    "FAULT_MEMBERS",
    "FRAME_TYPES",
    "GenerationCensus",
    "GenerationCensusMember",
    "KeyInterval",
    "KeyScheduleTransition",
    "RESULT",
    "RecoveryAnchor",
    "RestartResult",
    "RetainedRow",
    "RotationResult",
    "SCHEMA_VERSION",
    "TransitionResult",
    "apply_key_rotation",
    "build_initial_state",
    "candidate_for",
    "canonical_bytes",
    "digest_value",
    "key_for_position",
    "recovery_anchor",
    "restart",
    "retention_eligibility",
    "seal_census",
    "seal_state",
    "synthetic_digest",
    "transition",
    "validate_key_schedule",
    "verify_census",
    "verify_state",
]
