"""Synthetic-only privacy mechanics for future local Diary snapshot research.

The module is intentionally incapable of filesystem or provider access.  It
accepts strict in-memory authored-synthetic snapshots, replaces identity-bearing
values with keyed stand-ins, censors relative observation timing, reconstructs
adjacent changes, and measures explicitly scoped linkage risk.

A successful rehearsal means the mechanics are ready to measure one later,
separately authorised local slice.  It is not a claim of anonymity or a grant
of real-data access.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections import Counter, defaultdict
from enum import Enum
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


TOKEN_PATTERN = r"^[a-z][a-z0-9_-]{2,63}$"
RELEASE_PATTERN = r"^[a-z][a-z0-9_-]{2,31}$"
POLL_INTERVAL_SECONDS = 30
MIN_EPHEMERAL_KEY_BYTES = 32

PHONE_RE = re.compile(r"^(?:\+?61|0)[2-478](?:[ -]?\d){8}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
EMBEDDED_PHONE_RE = re.compile(r"(?<!\d)(?:\+?61|0)[2-478](?:[ -]?\d){8}(?!\d)")
EMBEDDED_EMAIL_RE = re.compile(r"(?<!\S)[^\s@]+@[^\s@]+\.[^\s@]+(?!\S)")
MEDICARE_LIKE_RE = re.compile(r"(?<!\d)\d{4}[ -]?\d{5}[ -]?\d(?!\d)")
PATH_RE = re.compile(r"(?:[A-Za-z]:\\|(?:^|\s)/[^\s]+|\.docx?\b)", re.IGNORECASE)
EXACT_TIMESTAMP_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")
ADDRESS_LIKE_RE = re.compile(
    r"\b\d{1,5}\s+[A-Za-z][A-Za-z -]{1,40}\s+"
    r"(?:street|st|road|rd|avenue|ave|drive|dr|lane|ln|court|ct)\b",
    re.IGNORECASE,
)


class PrivacyGateError(ValueError):
    """Fail-closed privacy gate error containing a reason code, never source data."""


class StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class LifecycleState(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ResourceRole(str, Enum):
    GENERAL_PRACTICE = "general_practice"
    NURSING = "nursing"
    ALLIED_HEALTH = "allied_health"
    ROOM_ONLY = "room_only"


class PrivacyClass(str, Enum):
    DIRECT_IDENTIFIER = "direct_identifier"
    CONTACT_IDENTIFIER = "contact_identifier"
    EXTERNAL_IDENTIFIER = "external_identifier"
    FREE_TEXT = "free_text"
    RELATIVE_OBSERVATION = "relative_observation"
    SCHEDULING_MECHANIC = "scheduling_mechanic"
    CONTROL_METADATA = "control_metadata"


class FieldTreatment(str, Enum):
    STABLE_STAND_IN = "stable_stand_in"
    DROP = "drop"
    CLOSED_BUCKET = "closed_bucket"
    INTERVAL_CENSOR = "interval_censor"
    PRESERVE = "preserve"


class NoteBucket(str, Enum):
    ABSENT = "absent"
    PRESENT = "present"
    SENSITIVE_PATTERN = "sensitive_pattern"


class ChangeKind(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    SCHEDULING_CHANGED = "scheduling_changed"
    LIFECYCLE_CHANGED = "lifecycle_changed"
    RESOURCE_CHANGED = "resource_changed"
    COMPOSITE_CHANGED = "composite_changed"


class SyntheticGateDecision(str, Enum):
    REVISION_REQUIRED = "revision_required"
    READY_FOR_BOUNDED_LOCAL_MEASUREMENT = "ready_for_bounded_local_measurement"


class RealAccessDecision(str, Enum):
    BLOCKED = "blocked"
    REVISION_REQUIRED = "revision_required"
    LOCALLY_RESTRICTED_CANDIDATE = "locally_restricted_candidate"


class SyntheticRecord(StrictFrozenModel):
    record_id: str = Field(pattern=TOKEN_PATTERN)
    person_label: str = Field(min_length=3, max_length=80)
    contact_value: str = Field(min_length=5, max_length=100)
    external_record_id: str = Field(min_length=6, max_length=64)
    resource_label: str = Field(min_length=3, max_length=80)
    resource_role: ResourceRole
    start_minute: int = Field(ge=0, lt=1440)
    duration_minutes: int = Field(gt=0, le=480)
    lifecycle_state: LifecycleState
    note_text: str = Field(max_length=160)

    @field_validator(
        "person_label",
        "contact_value",
        "external_record_id",
        "resource_label",
        "note_text",
    )
    @classmethod
    def reject_unsafe_source_shapes(cls, value: str) -> str:
        if "\n" in value or "\r" in value:
            raise ValueError("source_string_line_break_forbidden")
        if PATH_RE.search(value):
            raise ValueError("source_path_or_filename_forbidden")
        if EXACT_TIMESTAMP_RE.search(value):
            raise ValueError("exact_source_timestamp_forbidden")
        return value

    @field_validator("contact_value")
    @classmethod
    def require_contact_detector_target(cls, value: str) -> str:
        if not (PHONE_RE.fullmatch(value) or EMAIL_RE.fullmatch(value)):
            raise ValueError("contact_detector_target_invalid")
        return value

    @field_validator("external_record_id")
    @classmethod
    def require_external_identifier_shape(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{5,63}", value):
            raise ValueError("external_identifier_shape_invalid")
        return value


class SyntheticSnapshot(StrictFrozenModel):
    sequence_index: int = Field(ge=0)
    relative_day_index: int = Field(ge=0)
    observation_offset_seconds: int = Field(ge=0)
    records: tuple[SyntheticRecord, ...]

    @model_validator(mode="after")
    def require_unique_records(self) -> "SyntheticSnapshot":
        record_ids = [record.record_id for record in self.records]
        if len(record_ids) != len(set(record_ids)):
            raise ValueError("snapshot_record_ids_not_unique")
        return self


class SyntheticSnapshotSeries(StrictFrozenModel):
    schema_version: Literal["historical_diary.synthetic_snapshot_series.v1"]
    evidence_label: Literal["wholly_authored_synthetic"]
    nominal_poll_seconds: Literal[30]
    snapshots: tuple[SyntheticSnapshot, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def require_one_ordered_day(self) -> "SyntheticSnapshotSeries":
        indexes = [snapshot.sequence_index for snapshot in self.snapshots]
        if indexes != list(range(len(self.snapshots))):
            raise ValueError("snapshot_sequence_must_be_contiguous")
        days = {snapshot.relative_day_index for snapshot in self.snapshots}
        if len(days) != 1:
            raise ValueError("synthetic_rehearsal_requires_one_relative_day")
        offsets = [snapshot.observation_offset_seconds for snapshot in self.snapshots]
        if any(current <= previous for previous, current in zip(offsets, offsets[1:])):
            raise ValueError("observation_offsets_must_increase")
        return self


class FieldRule(StrictFrozenModel):
    owner: Literal["series", "snapshot", "record"]
    field_name: str = Field(pattern=r"^[a-z][a-z0-9_]{1,63}$")
    privacy_class: PrivacyClass
    treatment: FieldTreatment


class FieldInventoryReport(StrictFrozenModel):
    schema_version: Literal["historical_diary.field_inventory.v1"]
    complete: bool
    admitted_field_count: int = Field(ge=1)
    classified_field_count: int = Field(ge=0)
    class_counts: Mapping[PrivacyClass, int]
    treatment_counts: Mapping[FieldTreatment, int]
    unknown_field_count: int = Field(ge=0)


class DetectorReport(StrictFrozenModel):
    schema_version: Literal["historical_diary.detector_report.v1"]
    record_observation_count: int = Field(ge=0)
    direct_identifier_value_count: int = Field(ge=0)
    contact_identifier_value_count: int = Field(ge=0)
    external_identifier_value_count: int = Field(ge=0)
    resource_identifier_value_count: int = Field(ge=0)
    free_text_present_count: int = Field(ge=0)
    sensitive_pattern_note_count: int = Field(ge=0)
    source_values_emitted: Literal[False]


class ProjectedRecord(StrictFrozenModel):
    record_token: str = Field(pattern=r"^rec_[0-9a-f]{24}$")
    person_token: str = Field(pattern=r"^per_[0-9a-f]{24}$")
    external_token: str = Field(pattern=r"^ext_[0-9a-f]{24}$")
    resource_token: str = Field(pattern=r"^res_[0-9a-f]{24}$")
    resource_role: ResourceRole
    start_minute: int = Field(ge=0, lt=1440)
    duration_minutes: int = Field(gt=0, le=480)
    lifecycle_state: LifecycleState
    note_bucket: NoteBucket


class ProjectedSnapshot(StrictFrozenModel):
    sequence_index: int = Field(ge=0)
    relative_day_index: int = Field(ge=0)
    observation_interval_start_seconds: int = Field(ge=0)
    observation_interval_end_seconds: int = Field(gt=0)
    records: tuple[ProjectedRecord, ...]

    @model_validator(mode="after")
    def require_exact_interval(self) -> "ProjectedSnapshot":
        if (
            self.observation_interval_end_seconds
            - self.observation_interval_start_seconds
            != POLL_INTERVAL_SECONDS
        ):
            raise ValueError("observation_interval_width_invalid")
        return self


class ProjectedSeries(StrictFrozenModel):
    schema_version: Literal["historical_diary.private_projection.v1"]
    evidence_label: Literal["synthetic_gate_rehearsal"]
    release_id: str = Field(pattern=RELEASE_PATTERN)
    nominal_poll_seconds: Literal[30]
    key_persisted: Literal[False]
    deidentification_claimed: Literal[False]
    direct_identifiers_emitted: Literal[False]
    free_text_emitted: Literal[False]
    exact_source_timestamps_emitted: Literal[False]
    snapshots: tuple[ProjectedSnapshot, ...]


class TransitionChange(StrictFrozenModel):
    record_token: str = Field(pattern=r"^rec_[0-9a-f]{24}$")
    change_kind: ChangeKind
    changed_fields: tuple[
        Literal[
            "start_minute",
            "duration_minutes",
            "lifecycle_state",
            "resource_role",
            "resource_token",
            "person_token",
            "external_token",
            "note_bucket",
        ],
        ...,
    ] = ()

    @model_validator(mode="after")
    def require_change_shape(self) -> "TransitionChange":
        membership = {ChangeKind.ADDED, ChangeKind.REMOVED}
        if self.change_kind in membership and self.changed_fields:
            raise ValueError("membership_change_cannot_name_fields")
        if self.change_kind not in membership and not self.changed_fields:
            raise ValueError("field_change_requires_fields")
        return self


class SnapshotTransition(StrictFrozenModel):
    transition_index: int = Field(ge=0)
    from_sequence_index: int = Field(ge=0)
    to_sequence_index: int = Field(ge=1)
    occurred_after_seconds: int = Field(ge=0)
    occurred_by_seconds: int = Field(gt=0)
    changes: tuple[TransitionChange, ...]

    @model_validator(mode="after")
    def require_valid_bounds(self) -> "SnapshotTransition":
        if self.occurred_by_seconds <= self.occurred_after_seconds:
            raise ValueError("transition_interval_invalid")
        if self.to_sequence_index != self.from_sequence_index + 1:
            raise ValueError("transition_must_be_adjacent")
        return self


class RatioMetric(StrictFrozenModel):
    successes: int = Field(ge=0)
    trials: int = Field(gt=0)
    rate: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def require_exact_rate(self) -> "RatioMetric":
        if abs(self.rate - (self.successes / self.trials)) > 1e-12:
            raise ValueError("ratio_rate_not_exact")
        return self


class RecordLinkageClue(StrictFrozenModel):
    clue_id: str = Field(pattern=TOKEN_PATTERN)
    target_record_id: str = Field(pattern=TOKEN_PATTERN)
    relative_day_index: int = Field(ge=0)
    start_minute_bucket: int = Field(ge=0, lt=48)
    duration_minutes: int = Field(gt=0, le=480)
    lifecycle_state: LifecycleState
    resource_role: ResourceRole


class TrajectoryLinkageClue(StrictFrozenModel):
    clue_id: str = Field(pattern=TOKEN_PATTERN)
    target_record_id: str = Field(pattern=TOKEN_PATTERN)
    presence_pattern: tuple[bool, ...] = Field(min_length=2)
    lifecycle_sequence: tuple[LifecycleState, ...] = Field(min_length=1)


class ContextualRiskReport(StrictFrozenModel):
    schema_version: Literal["historical_diary.contextual_risk.v1"]
    population_record_count: int = Field(gt=0)
    quasi_identifier_definition: Literal[
        "relative_day_start_30m_duration_state_resource_role"
    ]
    trajectory_definition: Literal[
        "presence_sequence_start_30m_duration_state_resource_role"
    ]
    minimum_sequence_frequency: int = Field(ge=2)
    equivalence_class_sizes: tuple[int, ...] = Field(min_length=1)
    unique_records: RatioMetric
    unique_trajectories: RatioMetric
    rare_trajectories: RatioMetric
    record_linkage_attack: RatioMetric
    trajectory_linkage_attack: RatioMetric
    multi_release_differencing_attack: RatioMetric
    scope_statement: Literal[
        "conditional_empirical_reading_not_universal_reidentification_probability"
    ]


class UtilityReading(StrictFrozenModel):
    schema_version: Literal["historical_diary.utility_reading.v1"]
    snapshot_count: int = Field(ge=2)
    source_record_observation_count: int = Field(ge=1)
    projected_record_observation_count: int = Field(ge=1)
    expected_change_count: int = Field(ge=0)
    projected_change_count: int = Field(ge=0)
    scheduling_fields_preserved: bool
    stable_linkage_preserved: bool
    interval_censoring_valid: bool
    exact_transition_recovery: bool
    invented_intragap_ordering: Literal[False]


class SyntheticGateReading(StrictFrozenModel):
    schema_version: Literal["historical_diary.synthetic_gate_reading.v1"]
    decision: SyntheticGateDecision
    reason_codes: tuple[str, ...]
    field_inventory: FieldInventoryReport
    detector_report: DetectorReport
    utility: UtilityReading
    contextual_risk: ContextualRiskReport
    serialized_projection_contains_source_values: bool
    real_archive_accessed: Literal[False]
    deidentification_claimed: Literal[False]


class AccessScope(StrictFrozenModel):
    explicitly_nominated_leaf_root_count: Literal[1]
    nominated_dense_day_count: Literal[1]
    recursive_access_allowed: Literal[False]
    maximum_file_count: Literal[80]
    maximum_total_bytes: Literal[134217728]
    maximum_per_file_bytes: Literal[8388608]
    symlink_or_reparse_traversal_allowed: Literal[False]
    exact_ignored_local_readback_required: Literal[True]


class CapabilityBoundary(StrictFrozenModel):
    provider_allowed: Literal[False]
    network_allowed: Literal[False]
    model_prompt_allowed: Literal[False]
    telemetry_allowed: Literal[False]
    clipboard_allowed: Literal[False]
    product_runtime_allowed: Literal[False]
    memory_or_rag_allowed: Literal[False]
    committed_raw_or_extracted_text_allowed: Literal[False]
    committed_identifiers_or_mappings_allowed: Literal[False]


class RetentionBoundary(StrictFrozenModel):
    ignored_new_output_root_required: Literal[True]
    ephemeral_in_memory_key_required: Literal[True]
    key_or_mapping_persistence_allowed: Literal[False]
    automatic_failure_cleanup_required: Literal[True]
    aggregate_non_phi_commit_only: Literal[True]


class RealAccessSubgateContract(StrictFrozenModel):
    schema_version: Literal["historical_diary.real_access_subgate.v1"]
    operation: Literal["raisa-local-only-historical-diary-snapshot-privacy-feasibility-review"]
    executable_in_this_tranche: Literal[False]
    actual_path_bound: Literal[False]
    discovers_or_enumerates_source: Literal[False]
    decision_vocabulary: tuple[
        Literal["blocked"],
        Literal["revision_required"],
        Literal["locally_restricted_candidate"],
    ]
    scope: AccessScope
    capabilities: CapabilityBoundary
    retention: RetentionBoundary
    required_ignored_runtime_bindings: tuple[str, ...]
    required_checks: tuple[str, ...]
    strongest_decision_meaning: Literal[
        "ignored_local_research_retention_only_no_downstream_authority"
    ]
    existing_h5_h15_controls_changed: Literal[False]
    real_archive_accessed: Literal[False]


FIELD_RULES = (
    FieldRule(owner="series", field_name="schema_version", privacy_class=PrivacyClass.CONTROL_METADATA, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="series", field_name="evidence_label", privacy_class=PrivacyClass.CONTROL_METADATA, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="series", field_name="nominal_poll_seconds", privacy_class=PrivacyClass.RELATIVE_OBSERVATION, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="series", field_name="snapshots", privacy_class=PrivacyClass.CONTROL_METADATA, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="snapshot", field_name="sequence_index", privacy_class=PrivacyClass.RELATIVE_OBSERVATION, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="snapshot", field_name="relative_day_index", privacy_class=PrivacyClass.RELATIVE_OBSERVATION, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="snapshot", field_name="observation_offset_seconds", privacy_class=PrivacyClass.RELATIVE_OBSERVATION, treatment=FieldTreatment.INTERVAL_CENSOR),
    FieldRule(owner="snapshot", field_name="records", privacy_class=PrivacyClass.CONTROL_METADATA, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="record", field_name="record_id", privacy_class=PrivacyClass.EXTERNAL_IDENTIFIER, treatment=FieldTreatment.STABLE_STAND_IN),
    FieldRule(owner="record", field_name="person_label", privacy_class=PrivacyClass.DIRECT_IDENTIFIER, treatment=FieldTreatment.STABLE_STAND_IN),
    FieldRule(owner="record", field_name="contact_value", privacy_class=PrivacyClass.CONTACT_IDENTIFIER, treatment=FieldTreatment.DROP),
    FieldRule(owner="record", field_name="external_record_id", privacy_class=PrivacyClass.EXTERNAL_IDENTIFIER, treatment=FieldTreatment.STABLE_STAND_IN),
    FieldRule(owner="record", field_name="resource_label", privacy_class=PrivacyClass.DIRECT_IDENTIFIER, treatment=FieldTreatment.STABLE_STAND_IN),
    FieldRule(owner="record", field_name="resource_role", privacy_class=PrivacyClass.SCHEDULING_MECHANIC, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="record", field_name="start_minute", privacy_class=PrivacyClass.SCHEDULING_MECHANIC, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="record", field_name="duration_minutes", privacy_class=PrivacyClass.SCHEDULING_MECHANIC, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="record", field_name="lifecycle_state", privacy_class=PrivacyClass.SCHEDULING_MECHANIC, treatment=FieldTreatment.PRESERVE),
    FieldRule(owner="record", field_name="note_text", privacy_class=PrivacyClass.FREE_TEXT, treatment=FieldTreatment.CLOSED_BUCKET),
)

PROJECTED_RECORD_COMPARE_FIELDS = (
    "start_minute",
    "duration_minutes",
    "lifecycle_state",
    "resource_role",
    "resource_token",
    "person_token",
    "external_token",
    "note_bucket",
)


def parse_synthetic_series(payload: Any) -> SyntheticSnapshotSeries:
    """Validate without allowing Pydantic to echo private-looking input values."""
    try:
        return SyntheticSnapshotSeries.model_validate(payload)
    except ValidationError as error:
        codes = sorted({str(item["type"]) for item in error.errors(include_input=False)})
        suffix = "_".join(codes[:4]) if codes else "unknown"
        raise PrivacyGateError(f"synthetic_series_invalid_{suffix}") from None


def input_field_inventory() -> FieldInventoryReport:
    owners = {
        "series": set(SyntheticSnapshotSeries.model_fields),
        "snapshot": set(SyntheticSnapshot.model_fields),
        "record": set(SyntheticRecord.model_fields),
    }
    classified = {(rule.owner, rule.field_name) for rule in FIELD_RULES}
    admitted = {(owner, field) for owner, fields in owners.items() for field in fields}
    unknown = admitted - classified
    extra = classified - admitted
    class_counts = Counter(rule.privacy_class for rule in FIELD_RULES)
    treatment_counts = Counter(rule.treatment for rule in FIELD_RULES)
    return FieldInventoryReport(
        schema_version="historical_diary.field_inventory.v1",
        complete=not unknown and not extra,
        admitted_field_count=len(admitted),
        classified_field_count=len(classified & admitted),
        class_counts=dict(class_counts),
        treatment_counts=dict(treatment_counts),
        unknown_field_count=len(unknown | extra),
    )


def detector_report(series: SyntheticSnapshotSeries) -> DetectorReport:
    observations = [record for snapshot in series.snapshots for record in snapshot.records]
    return DetectorReport(
        schema_version="historical_diary.detector_report.v1",
        record_observation_count=len(observations),
        direct_identifier_value_count=len(observations),
        contact_identifier_value_count=len(observations),
        external_identifier_value_count=len(observations) * 2,
        resource_identifier_value_count=len(observations),
        free_text_present_count=sum(bool(record.note_text) for record in observations),
        sensitive_pattern_note_count=sum(
            _note_bucket(record.note_text) is NoteBucket.SENSITIVE_PATTERN
            for record in observations
        ),
        source_values_emitted=False,
    )


def _note_bucket(value: str) -> NoteBucket:
    if not value:
        return NoteBucket.ABSENT
    if any(
        pattern.search(value)
        for pattern in (
            EMBEDDED_PHONE_RE,
            EMBEDDED_EMAIL_RE,
            MEDICARE_LIKE_RE,
            ADDRESS_LIKE_RE,
            PATH_RE,
            EXACT_TIMESTAMP_RE,
        )
    ):
        return NoteBucket.SENSITIVE_PATTERN
    return NoteBucket.PRESENT


def _validate_ephemeral_key(key: bytes) -> None:
    if not isinstance(key, bytes) or len(key) < MIN_EPHEMERAL_KEY_BYTES:
        raise PrivacyGateError("ephemeral_key_too_short")
    if len(set(key)) == 1:
        raise PrivacyGateError("ephemeral_key_low_diversity")


def _stand_in(prefix: str, domain: str, value: str, key: bytes) -> str:
    digest = hmac.new(
        key,
        f"historical-diary-v1\x00{domain}\x00{value}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:24]
    return f"{prefix}_{digest}"


def project_series(
    series: SyntheticSnapshotSeries,
    *,
    ephemeral_key: bytes,
    release_id: str,
) -> ProjectedSeries:
    _validate_ephemeral_key(ephemeral_key)
    snapshots: list[ProjectedSnapshot] = []
    for snapshot in series.snapshots:
        start = (
            snapshot.observation_offset_seconds // POLL_INTERVAL_SECONDS
        ) * POLL_INTERVAL_SECONDS
        records = tuple(
            ProjectedRecord(
                record_token=_stand_in("rec", "record", record.record_id, ephemeral_key),
                person_token=_stand_in("per", "person", record.person_label.casefold(), ephemeral_key),
                external_token=_stand_in("ext", "external", record.external_record_id, ephemeral_key),
                resource_token=_stand_in("res", "resource", record.resource_label.casefold(), ephemeral_key),
                resource_role=record.resource_role,
                start_minute=record.start_minute,
                duration_minutes=record.duration_minutes,
                lifecycle_state=record.lifecycle_state,
                note_bucket=_note_bucket(record.note_text),
            )
            for record in snapshot.records
        )
        snapshots.append(
            ProjectedSnapshot(
                sequence_index=snapshot.sequence_index,
                relative_day_index=snapshot.relative_day_index,
                observation_interval_start_seconds=start,
                observation_interval_end_seconds=start + POLL_INTERVAL_SECONDS,
                records=records,
            )
        )
    return ProjectedSeries(
        schema_version="historical_diary.private_projection.v1",
        evidence_label="synthetic_gate_rehearsal",
        release_id=release_id,
        nominal_poll_seconds=30,
        key_persisted=False,
        deidentification_claimed=False,
        direct_identifiers_emitted=False,
        free_text_emitted=False,
        exact_source_timestamps_emitted=False,
        snapshots=tuple(snapshots),
    )


def diff_adjacent_snapshots(series: ProjectedSeries) -> tuple[SnapshotTransition, ...]:
    transitions = []
    for index, (previous, current) in enumerate(zip(series.snapshots, series.snapshots[1:])):
        before = {record.record_token: record for record in previous.records}
        after = {record.record_token: record for record in current.records}
        changes: list[TransitionChange] = []
        for token in sorted(before.keys() - after.keys()):
            changes.append(TransitionChange(record_token=token, change_kind=ChangeKind.REMOVED))
        for token in sorted(after.keys() - before.keys()):
            changes.append(TransitionChange(record_token=token, change_kind=ChangeKind.ADDED))
        for token in sorted(before.keys() & after.keys()):
            changed = tuple(
                field
                for field in PROJECTED_RECORD_COMPARE_FIELDS
                if getattr(before[token], field) != getattr(after[token], field)
            )
            if not changed:
                continue
            changes.append(
                TransitionChange(
                    record_token=token,
                    change_kind=_classify_changed_fields(changed),
                    changed_fields=changed,
                )
            )
        transitions.append(
            SnapshotTransition(
                transition_index=index,
                from_sequence_index=previous.sequence_index,
                to_sequence_index=current.sequence_index,
                occurred_after_seconds=previous.observation_interval_start_seconds,
                occurred_by_seconds=current.observation_interval_end_seconds,
                changes=tuple(changes),
            )
        )
    return tuple(transitions)


def _classify_changed_fields(changed: tuple[str, ...]) -> ChangeKind:
    changed_set = set(changed)
    if changed_set == {"lifecycle_state"}:
        return ChangeKind.LIFECYCLE_CHANGED
    if changed_set <= {"start_minute", "duration_minutes"}:
        return ChangeKind.SCHEDULING_CHANGED
    if changed_set <= {"resource_role", "resource_token"}:
        return ChangeKind.RESOURCE_CHANGED
    return ChangeKind.COMPOSITE_CHANGED


def _raw_changes(series: SyntheticSnapshotSeries) -> list[tuple[str, str, tuple[str, ...]]]:
    changes: list[tuple[str, str, tuple[str, ...]]] = []
    raw_fields = (
        "person_label",
        "external_record_id",
        "resource_label",
        "resource_role",
        "start_minute",
        "duration_minutes",
        "lifecycle_state",
        "note_text",
    )
    for previous, current in zip(series.snapshots, series.snapshots[1:]):
        before = {record.record_id: record for record in previous.records}
        after = {record.record_id: record for record in current.records}
        changes.extend((record_id, "removed", ()) for record_id in sorted(before.keys() - after.keys()))
        changes.extend((record_id, "added", ()) for record_id in sorted(after.keys() - before.keys()))
        for record_id in sorted(before.keys() & after.keys()):
            changed = tuple(
                field for field in raw_fields if getattr(before[record_id], field) != getattr(after[record_id], field)
            )
            if changed:
                changes.append((record_id, "changed", changed))
    return changes


def utility_reading(
    source: SyntheticSnapshotSeries,
    projected: ProjectedSeries,
) -> UtilityReading:
    transitions = diff_adjacent_snapshots(projected)
    source_observations = sum(len(snapshot.records) for snapshot in source.snapshots)
    projected_observations = sum(len(snapshot.records) for snapshot in projected.snapshots)
    keyless_source_shapes = [
        sorted(
            (
                record.resource_role.value,
                record.start_minute,
                record.duration_minutes,
                record.lifecycle_state.value,
                _note_bucket(record.note_text).value,
            )
            for record in snapshot.records
        )
        for snapshot in source.snapshots
    ]
    projected_shapes = [
        sorted(
            (
                record.resource_role.value,
                record.start_minute,
                record.duration_minutes,
                record.lifecycle_state.value,
                record.note_bucket.value,
            )
            for record in snapshot.records
        )
        for snapshot in projected.snapshots
    ]
    raw_changes = _raw_changes(source)
    projected_change_count = sum(len(transition.changes) for transition in transitions)
    record_occurrences: dict[str, set[str]] = defaultdict(set)
    for snapshot in projected.snapshots:
        for record in snapshot.records:
            record_occurrences[record.record_token].add(record.person_token)
    stable = all(len(person_tokens) == 1 for person_tokens in record_occurrences.values())
    intervals_valid = all(
        transition.occurred_after_seconds < transition.occurred_by_seconds
        for transition in transitions
    )
    return UtilityReading(
        schema_version="historical_diary.utility_reading.v1",
        snapshot_count=len(source.snapshots),
        source_record_observation_count=source_observations,
        projected_record_observation_count=projected_observations,
        expected_change_count=len(raw_changes),
        projected_change_count=projected_change_count,
        scheduling_fields_preserved=keyless_source_shapes == projected_shapes,
        stable_linkage_preserved=stable,
        interval_censoring_valid=intervals_valid,
        exact_transition_recovery=len(raw_changes) == projected_change_count,
        invented_intragap_ordering=False,
    )


def _ratio(successes: int, trials: int) -> RatioMetric:
    if trials <= 0:
        raise PrivacyGateError("risk_metric_empty_denominator")
    return RatioMetric(successes=successes, trials=trials, rate=successes / trials)


def _final_records(series: ProjectedSeries) -> dict[str, tuple[int, ProjectedRecord]]:
    final: dict[str, tuple[int, ProjectedRecord]] = {}
    for snapshot in series.snapshots:
        for record in snapshot.records:
            final[record.record_token] = (snapshot.relative_day_index, record)
    return final


def _quasi_signature(day: int, record: ProjectedRecord) -> tuple[Any, ...]:
    return (
        day,
        record.start_minute // 30,
        record.duration_minutes,
        record.lifecycle_state.value,
        record.resource_role.value,
    )


def _trajectories(series: ProjectedSeries) -> dict[str, tuple[tuple[Any, ...], ...]]:
    tokens = {
        record.record_token
        for snapshot in series.snapshots
        for record in snapshot.records
    }
    result: dict[str, tuple[tuple[Any, ...], ...]] = {}
    for token in tokens:
        events: list[tuple[Any, ...]] = []
        for snapshot in series.snapshots:
            matches = [record for record in snapshot.records if record.record_token == token]
            if not matches:
                events.append((snapshot.sequence_index, False))
                continue
            record = matches[0]
            events.append(
                (
                    snapshot.sequence_index,
                    True,
                    record.start_minute // 30,
                    record.duration_minutes,
                    record.lifecycle_state.value,
                    record.resource_role.value,
                )
            )
        result[token] = tuple(events)
    return result


def _target_token(record_id: str, key: bytes) -> str:
    return _stand_in("rec", "record", record_id, key)


def measure_contextual_risk(
    source: SyntheticSnapshotSeries,
    release_a: ProjectedSeries,
    release_b: ProjectedSeries,
    *,
    key_a: bytes,
    key_b: bytes,
    record_clues: tuple[RecordLinkageClue, ...],
    trajectory_clues: tuple[TrajectoryLinkageClue, ...],
    minimum_sequence_frequency: int = 2,
) -> ContextualRiskReport:
    _validate_ephemeral_key(key_a)
    _validate_ephemeral_key(key_b)
    if key_a == key_b or release_a.release_id == release_b.release_id:
        raise PrivacyGateError("independent_release_required")
    if minimum_sequence_frequency < 2:
        raise PrivacyGateError("minimum_sequence_frequency_too_low")
    source_record_ids = {
        record.record_id for snapshot in source.snapshots for record in snapshot.records
    }
    if not record_clues or not trajectory_clues:
        raise PrivacyGateError("adversary_clues_required")
    if any(clue.target_record_id not in source_record_ids for clue in (*record_clues, *trajectory_clues)):
        raise PrivacyGateError("adversary_target_unknown")

    final_a = _final_records(release_a)
    final_b = _final_records(release_b)
    quasi_a = {token: _quasi_signature(day, record) for token, (day, record) in final_a.items()}
    quasi_counts = Counter(quasi_a.values())
    population = len(quasi_a)
    unique_records = sum(count == 1 for count in quasi_counts.values())

    trajectory_a = _trajectories(release_a)
    trajectory_b = _trajectories(release_b)
    trajectory_counts = Counter(trajectory_a.values())
    unique_trajectories = sum(count == 1 for count in trajectory_counts.values())
    rare_trajectories = sum(
        count for count in trajectory_counts.values() if count < minimum_sequence_frequency
    )

    record_successes = 0
    for clue in record_clues:
        expected = _target_token(clue.target_record_id, key_a)
        signature = (
            clue.relative_day_index,
            clue.start_minute_bucket,
            clue.duration_minutes,
            clue.lifecycle_state.value,
            clue.resource_role.value,
        )
        matches = [token for token, candidate in quasi_a.items() if candidate == signature]
        record_successes += len(matches) == 1 and matches[0] == expected

    trajectory_successes = 0
    for clue in trajectory_clues:
        expected = _target_token(clue.target_record_id, key_a)
        matches = []
        for token, events in trajectory_a.items():
            presence = tuple(bool(event[1]) for event in events)
            states = tuple(LifecycleState(event[4]) for event in events if event[1])
            if presence == clue.presence_pattern and states == clue.lifecycle_sequence:
                matches.append(token)
        trajectory_successes += len(matches) == 1 and matches[0] == expected

    reverse_b: dict[tuple[tuple[Any, ...], ...], list[str]] = defaultdict(list)
    for token, signature in trajectory_b.items():
        reverse_b[signature].append(token)
    differencing_successes = sum(
        trajectory_counts[signature] == 1 and len(reverse_b.get(signature, [])) == 1
        for signature in trajectory_a.values()
    )

    return ContextualRiskReport(
        schema_version="historical_diary.contextual_risk.v1",
        population_record_count=population,
        quasi_identifier_definition="relative_day_start_30m_duration_state_resource_role",
        trajectory_definition="presence_sequence_start_30m_duration_state_resource_role",
        minimum_sequence_frequency=minimum_sequence_frequency,
        equivalence_class_sizes=tuple(sorted(quasi_counts.values())),
        unique_records=_ratio(unique_records, population),
        unique_trajectories=_ratio(unique_trajectories, population),
        rare_trajectories=_ratio(rare_trajectories, population),
        record_linkage_attack=_ratio(record_successes, len(record_clues)),
        trajectory_linkage_attack=_ratio(trajectory_successes, len(trajectory_clues)),
        multi_release_differencing_attack=_ratio(differencing_successes, population),
        scope_statement="conditional_empirical_reading_not_universal_reidentification_probability",
    )


def projection_contains_source_values(
    source: SyntheticSnapshotSeries,
    projected: ProjectedSeries,
) -> bool:
    serialized = projected.model_dump_json()
    sensitive_values = {
        value
        for snapshot in source.snapshots
        for record in snapshot.records
        for value in (
            record.record_id,
            record.person_label,
            record.contact_value,
            record.external_record_id,
            record.resource_label,
            record.note_text,
        )
        if len(value) >= 3
    }
    return any(value in serialized for value in sensitive_values)


def evaluate_synthetic_gate(
    source: SyntheticSnapshotSeries,
    *,
    key_a: bytes,
    key_b: bytes,
    record_clues: tuple[RecordLinkageClue, ...],
    trajectory_clues: tuple[TrajectoryLinkageClue, ...],
) -> SyntheticGateReading:
    inventory = input_field_inventory()
    detector = detector_report(source)
    release_a = project_series(source, ephemeral_key=key_a, release_id="synthetic_release_a")
    release_b = project_series(source, ephemeral_key=key_b, release_id="synthetic_release_b")
    utility = utility_reading(source, release_a)
    risk = measure_contextual_risk(
        source,
        release_a,
        release_b,
        key_a=key_a,
        key_b=key_b,
        record_clues=record_clues,
        trajectory_clues=trajectory_clues,
    )
    contains_source = projection_contains_source_values(source, release_a)
    checks = {
        "field_inventory_incomplete": inventory.complete,
        "projection_contains_source_values": not contains_source,
        "scheduling_fields_not_preserved": utility.scheduling_fields_preserved,
        "stable_linkage_not_preserved": utility.stable_linkage_preserved,
        "interval_censoring_invalid": utility.interval_censoring_valid,
        "transition_recovery_inexact": utility.exact_transition_recovery,
    }
    reasons = tuple(reason for reason, passed in checks.items() if not passed)
    decision = (
        SyntheticGateDecision.READY_FOR_BOUNDED_LOCAL_MEASUREMENT
        if not reasons
        else SyntheticGateDecision.REVISION_REQUIRED
    )
    return SyntheticGateReading(
        schema_version="historical_diary.synthetic_gate_reading.v1",
        decision=decision,
        reason_codes=reasons,
        field_inventory=inventory,
        detector_report=detector,
        utility=utility,
        contextual_risk=risk,
        serialized_projection_contains_source_values=contains_source,
        real_archive_accessed=False,
        deidentification_claimed=False,
    )


def build_real_access_subgate_contract() -> RealAccessSubgateContract:
    return RealAccessSubgateContract(
        schema_version="historical_diary.real_access_subgate.v1",
        operation="raisa-local-only-historical-diary-snapshot-privacy-feasibility-review",
        executable_in_this_tranche=False,
        actual_path_bound=False,
        discovers_or_enumerates_source=False,
        decision_vocabulary=(
            RealAccessDecision.BLOCKED.value,
            RealAccessDecision.REVISION_REQUIRED.value,
            RealAccessDecision.LOCALLY_RESTRICTED_CANDIDATE.value,
        ),
        scope=AccessScope(
            explicitly_nominated_leaf_root_count=1,
            nominated_dense_day_count=1,
            recursive_access_allowed=False,
            maximum_file_count=80,
            maximum_total_bytes=134217728,
            maximum_per_file_bytes=8388608,
            symlink_or_reparse_traversal_allowed=False,
            exact_ignored_local_readback_required=True,
        ),
        capabilities=CapabilityBoundary(
            provider_allowed=False,
            network_allowed=False,
            model_prompt_allowed=False,
            telemetry_allowed=False,
            clipboard_allowed=False,
            product_runtime_allowed=False,
            memory_or_rag_allowed=False,
            committed_raw_or_extracted_text_allowed=False,
            committed_identifiers_or_mappings_allowed=False,
        ),
        retention=RetentionBoundary(
            ignored_new_output_root_required=True,
            ephemeral_in_memory_key_required=True,
            key_or_mapping_persistence_allowed=False,
            automatic_failure_cleanup_required=True,
            aggregate_non_phi_commit_only=True,
        ),
        required_ignored_runtime_bindings=(
            "exact_leaf_root",
            "exact_dense_day_selector",
            "exact_input_file_manifest",
            "exact_input_byte_readback",
            "exact_parser_identity_and_digest",
            "new_ignored_output_root",
            "cleanup_receipt",
        ),
        required_checks=(
            "complete_field_inventory",
            "direct_identifier_detector",
            "closed_projection_allowlist",
            "free_text_non_export",
            "adjacent_interval_differencing",
            "stable_linkage_and_utility",
            "equivalence_and_uniqueness",
            "rare_sequence_frequency",
            "record_linkage_attack",
            "trajectory_linkage_attack",
            "multi_release_differencing_attack",
            "aggregate_output_leakage_scan",
        ),
        strongest_decision_meaning="ignored_local_research_retention_only_no_downstream_authority",
        existing_h5_h15_controls_changed=False,
        real_archive_accessed=False,
    )


def generate_authored_synthetic_series() -> SyntheticSnapshotSeries:
    """Return one invented day with duplicate and rare longitudinal patterns."""

    def record(
        record_id: str,
        person: str,
        contact: str,
        external: str,
        resource: str,
        role: ResourceRole,
        start: int,
        duration: int,
        state: LifecycleState,
        note: str,
    ) -> SyntheticRecord:
        return SyntheticRecord(
            record_id=record_id,
            person_label=person,
            contact_value=contact,
            external_record_id=external,
            resource_label=resource,
            resource_role=role,
            start_minute=start,
            duration_minutes=duration,
            lifecycle_state=state,
            note_text=note,
        )

    base = (
        record("rec_alpha", "Invented Person Alpha", "+61412000001", "EXT-A00001", "Invented Resource North", ResourceRole.GENERAL_PRACTICE, 540, 20, LifecycleState.SCHEDULED, ""),
        record("rec_beta", "Invented Person Beta", "beta@example.invalid", "EXT-B00002", "Invented Resource North", ResourceRole.GENERAL_PRACTICE, 540, 20, LifecycleState.SCHEDULED, "routine reminder"),
        record("rec_gamma", "Invented Person Gamma", "+61412000003", "EXT-C00003", "Invented Resource East", ResourceRole.GENERAL_PRACTICE, 600, 30, LifecycleState.CONFIRMED, "contact +61412000999"),
        record("rec_delta", "Invented Person Delta", "delta@example.invalid", "EXT-D00004", "Invented Resource East", ResourceRole.GENERAL_PRACTICE, 600, 30, LifecycleState.CONFIRMED, ""),
    )
    added = (
        record("rec_epsilon", "Invented Person Epsilon", "+61412000005", "EXT-E00005", "Invented Resource South", ResourceRole.NURSING, 660, 15, LifecycleState.SCHEDULED, ""),
        record("rec_zeta", "Invented Person Zeta", "zeta@example.invalid", "EXT-Z00006", "Invented Resource South", ResourceRole.NURSING, 660, 15, LifecycleState.SCHEDULED, ""),
        record("rec_eta", "Invented Person Eta", "+61412000007", "EXT-H00007", "Invented Resource West", ResourceRole.ALLIED_HEALTH, 720, 10, LifecycleState.SCHEDULED, "one-off pattern"),
    )
    second = base + added
    third = (
        *(item.model_copy(update={"lifecycle_state": LifecycleState.CHECKED_IN}) for item in base[:2]),
        *base[2:],
        *(item.model_copy(update={"duration_minutes": 30}) for item in added[:2]),
    )
    fourth = (
        *(item.model_copy(update={"lifecycle_state": LifecycleState.COMPLETED}) for item in third[:2]),
        *(item.model_copy(update={"lifecycle_state": LifecycleState.CANCELLED}) for item in third[4:]),
    )
    return SyntheticSnapshotSeries(
        schema_version="historical_diary.synthetic_snapshot_series.v1",
        evidence_label="wholly_authored_synthetic",
        nominal_poll_seconds=30,
        snapshots=(
            SyntheticSnapshot(sequence_index=0, relative_day_index=0, observation_offset_seconds=0, records=base),
            SyntheticSnapshot(sequence_index=1, relative_day_index=0, observation_offset_seconds=31, records=second),
            SyntheticSnapshot(sequence_index=2, relative_day_index=0, observation_offset_seconds=68, records=third),
            SyntheticSnapshot(sequence_index=3, relative_day_index=0, observation_offset_seconds=145, records=fourth),
        ),
    )


def authored_adversary_clues() -> tuple[
    tuple[RecordLinkageClue, ...], tuple[TrajectoryLinkageClue, ...]
]:
    record_clues = (
        RecordLinkageClue(
            clue_id="record_eta_unique",
            target_record_id="rec_eta",
            relative_day_index=0,
            start_minute_bucket=24,
            duration_minutes=10,
            lifecycle_state=LifecycleState.SCHEDULED,
            resource_role=ResourceRole.ALLIED_HEALTH,
        ),
        RecordLinkageClue(
            clue_id="record_alpha_ambiguous",
            target_record_id="rec_alpha",
            relative_day_index=0,
            start_minute_bucket=18,
            duration_minutes=20,
            lifecycle_state=LifecycleState.COMPLETED,
            resource_role=ResourceRole.GENERAL_PRACTICE,
        ),
    )
    trajectory_clues = (
        TrajectoryLinkageClue(
            clue_id="trajectory_eta_unique",
            target_record_id="rec_eta",
            presence_pattern=(False, True, False, False),
            lifecycle_sequence=(LifecycleState.SCHEDULED,),
        ),
        TrajectoryLinkageClue(
            clue_id="trajectory_alpha_ambiguous",
            target_record_id="rec_alpha",
            presence_pattern=(True, True, True, True),
            lifecycle_sequence=(
                LifecycleState.SCHEDULED,
                LifecycleState.SCHEDULED,
                LifecycleState.CHECKED_IN,
                LifecycleState.COMPLETED,
            ),
        ),
    )
    return record_clues, trajectory_clues


def render_data_free_contract() -> str:
    """Canonical JSON for the committed, deliberately non-executable policy."""
    return json.dumps(
        build_real_access_subgate_contract().model_dump(mode="json"),
        indent=2,
        sort_keys=True,
    ) + "\n"
