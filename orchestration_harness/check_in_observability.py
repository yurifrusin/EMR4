"""Pure unmounted default-off check-in observability intent adapter.

The only constructible adapter generation is disabled. Future-shaped builders
return immutable in-memory intents only; this module has no emitter, transport,
registry, filesystem, environment, application, database, or command port.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from math import isfinite

from orchestration_harness.check_in_admission_control import (
    AdmissionDecision,
    AdmissionLane,
    ControlOperation,
    DECISION_SCHEMA_VERSION,
    DecisionReason,
    DecisionValue,
    KillSwitchState,
    UnknownCommitResult,
)


class ClosedTextEnum(str, Enum):
    """A closed string-valued vocabulary for immutable intent fields."""


class Environment(ClosedTextEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class MetricName(ClosedTextEnum):
    ADMISSION_DECISIONS = "emr4_check_in_admission_decisions_total"
    SNAPSHOT_AGE = "emr4_check_in_admission_snapshot_age_seconds"
    KILL_SWITCH = "emr4_check_in_admission_kill_switch"
    UNKNOWN_COMMIT = "emr4_check_in_unknown_commit_total"
    CONTROL_COMMANDS = "emr4_check_in_control_commands_total"


class MetricKind(ClosedTextEnum):
    COUNTER = "counter"
    GAUGE = "gauge"


class ControlOutcome(ClosedTextEnum):
    ACCEPTED = "accepted"
    REPLAYED = "replayed"
    DENIED = "denied"
    CONFLICT = "conflict"
    UNCERTAIN = "uncertain"
    FAILED = "failed"


class AlertId(ClosedTextEnum):
    KILL_SWITCH_ENGAGED = "check_in_kill_switch_engaged"
    SNAPSHOT_INVALID_OR_STALE = "check_in_admission_snapshot_invalid_or_stale"
    UNKNOWN_COMMIT = "check_in_unknown_commit"
    ACTIVE_RECORD_REJECTED = "check_in_active_record_rejected"
    CONTROL_AUDIT_FAILURE = "check_in_control_audit_failure"
    ROLLBACK_FAILURE = "check_in_rollback_failure"


ENVIRONMENT_VALUES = tuple(item.value for item in Environment)
LANE_VALUES = tuple(item.value for item in AdmissionLane)
OUTCOME_VALUES = tuple(item.value for item in DecisionValue)
CONTROL_OUTCOME_VALUES = tuple(item.value for item in ControlOutcome)
ALERT_ID_VALUES = tuple(item.value for item in AlertId)

MANIFEST_DECISION_REASON_VALUES = (
    "feature_disabled",
    "kill_switch_engaged",
    "snapshot_missing",
    "snapshot_invalid",
    "snapshot_stale",
    "snapshot_ambiguous",
    "no_matching_lane",
    "lane_ambiguous",
    "ordinary_record_missing",
    "ordinary_state_not_active",
    "ordinary_binding_mismatch",
    "ordinary_evidence_missing",
    "ordinary_evidence_invalid",
    "admitted_synthetic",
    "admitted_ordinary",
)
REHEARSAL_ONLY_DECISION_REASON_VALUES = ("ordinary_activation_closed",)
FUTURE_ONLY_DECISION_REASON_VALUES = (
    "ordinary_record_missing",
    "ordinary_evidence_invalid",
    "admitted_ordinary",
)

CONTROL_OPERATION_LABELS = {
    ControlOperation.PREPARE: "prepare",
    ControlOperation.ACTIVATE: "activate",
    ControlOperation.SUSPEND: "suspend",
    ControlOperation.WITHDRAW: "withdraw",
    ControlOperation.ENGAGE_KILL_SWITCH: "engage_kill_switch",
}

METRIC_KINDS = {
    MetricName.ADMISSION_DECISIONS: MetricKind.COUNTER,
    MetricName.SNAPSHOT_AGE: MetricKind.GAUGE,
    MetricName.KILL_SWITCH: MetricKind.GAUGE,
    MetricName.UNKNOWN_COMMIT: MetricKind.COUNTER,
    MetricName.CONTROL_COMMANDS: MetricKind.COUNTER,
}

METRIC_LABEL_DOMAINS = {
    MetricName.ADMISSION_DECISIONS: (
        ("environment", ENVIRONMENT_VALUES),
        ("lane", LANE_VALUES),
        ("outcome", OUTCOME_VALUES),
        ("reason_code", MANIFEST_DECISION_REASON_VALUES),
    ),
    MetricName.SNAPSHOT_AGE: (("environment", ENVIRONMENT_VALUES),),
    MetricName.KILL_SWITCH: (("environment", ENVIRONMENT_VALUES),),
    MetricName.UNKNOWN_COMMIT: (("environment", ENVIRONMENT_VALUES),),
    MetricName.CONTROL_COMMANDS: (
        ("environment", ENVIRONMENT_VALUES),
        ("operation", tuple(CONTROL_OPERATION_LABELS.values())),
        ("outcome", CONTROL_OUTCOME_VALUES),
    ),
}

_SNAPSHOT_ALERT_REASONS = frozenset(
    {
        DecisionReason.SNAPSHOT_MISSING,
        DecisionReason.SNAPSHOT_INVALID,
        DecisionReason.SNAPSHOT_STALE,
        DecisionReason.SNAPSHOT_AMBIGUOUS,
    }
)
_ACTIVE_RECORD_ALERT_REASONS = frozenset(
    {
        DecisionReason.ORDINARY_BINDING_MISMATCH,
        DecisionReason.ORDINARY_EVIDENCE_MISSING,
    }
)
_DECISION_SHAPES = {
    DecisionReason.SNAPSHOT_MISSING: (DecisionValue.DENIED, AdmissionLane.NONE),
    DecisionReason.SNAPSHOT_INVALID: (DecisionValue.DENIED, AdmissionLane.NONE),
    DecisionReason.SNAPSHOT_STALE: (DecisionValue.DENIED, AdmissionLane.NONE),
    DecisionReason.SNAPSHOT_AMBIGUOUS: (DecisionValue.DENIED, AdmissionLane.NONE),
    DecisionReason.FEATURE_DISABLED: (DecisionValue.DENIED, AdmissionLane.NONE),
    DecisionReason.KILL_SWITCH_ENGAGED: (DecisionValue.DENIED, AdmissionLane.NONE),
    DecisionReason.NO_MATCHING_LANE: (DecisionValue.DENIED, AdmissionLane.NONE),
    DecisionReason.LANE_AMBIGUOUS: (
        DecisionValue.DENIED,
        AdmissionLane.AMBIGUOUS,
    ),
    DecisionReason.ADMITTED_SYNTHETIC: (
        DecisionValue.ADMITTED,
        AdmissionLane.AUTHORED_SYNTHETIC,
    ),
    DecisionReason.ORDINARY_BINDING_MISMATCH: (
        DecisionValue.DENIED,
        AdmissionLane.ORDINARY_PRACTICE,
    ),
    DecisionReason.ORDINARY_STATE_NOT_ACTIVE: (
        DecisionValue.DENIED,
        AdmissionLane.ORDINARY_PRACTICE,
    ),
    DecisionReason.ORDINARY_EVIDENCE_MISSING: (
        DecisionValue.DENIED,
        AdmissionLane.ORDINARY_PRACTICE,
    ),
    DecisionReason.ORDINARY_ACTIVATION_CLOSED: (
        DecisionValue.DENIED,
        AdmissionLane.ORDINARY_PRACTICE,
    ),
}


class ObserverInputRejected(ValueError):
    """A future-shaped material value is outside the frozen closed contract."""


@dataclass(frozen=True, slots=True)
class MetricIntent:
    """One immutable metric update description with no emission capability."""

    name: MetricName
    kind: MetricKind
    labels: tuple[tuple[str, str], ...]
    value: int | float

    def __post_init__(self) -> None:
        if not isinstance(self.name, MetricName):
            raise ObserverInputRejected("metric_name_invalid")
        if self.kind is not METRIC_KINDS[self.name]:
            raise ObserverInputRejected("metric_kind_invalid")
        expected = METRIC_LABEL_DOMAINS[self.name]
        if tuple(label for label, _ in self.labels) != tuple(
            label for label, _ in expected
        ):
            raise ObserverInputRejected("metric_label_shape_invalid")
        for (_, value), (_, domain) in zip(self.labels, expected, strict=True):
            if value not in domain:
                raise ObserverInputRejected("metric_label_value_invalid")
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise ObserverInputRejected("metric_value_invalid")
        if not isfinite(float(self.value)) or self.value < 0:
            raise ObserverInputRejected("metric_value_invalid")
        if self.kind is MetricKind.COUNTER and self.value != 1:
            raise ObserverInputRejected("counter_increment_invalid")
        if self.name is MetricName.KILL_SWITCH and self.value not in {0, 1}:
            raise ObserverInputRejected("kill_switch_gauge_invalid")


@dataclass(frozen=True, slots=True)
class AlertIntent:
    """One closed critical alert description with no action or delivery port."""

    alert_id: AlertId
    severity: str = "critical"
    contains_identifier: bool = False
    automatic_control_action: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.alert_id, AlertId):
            raise ObserverInputRejected("alert_id_invalid")
        if self.severity != "critical":
            raise ObserverInputRejected("alert_severity_invalid")
        if self.contains_identifier is not False:
            raise ObserverInputRejected("alert_identifier_forbidden")
        if self.automatic_control_action is not False:
            raise ObserverInputRejected("alert_action_forbidden")


@dataclass(frozen=True, slots=True)
class ObservationBatch:
    """A complete atomic in-memory reading; it cannot emit itself."""

    metrics: tuple[MetricIntent, ...] = ()
    alerts: tuple[AlertIntent, ...] = ()


EMPTY_OBSERVATION_BATCH = ObservationBatch()


@dataclass(frozen=True, slots=True)
class ObservationMaterial:
    """Closed non-PHI inputs for the pure future-shaped intent builder."""

    environment: Environment
    admission_decision: AdmissionDecision | None = None
    snapshot_age_seconds: int | float | None = None
    snapshot_age_over_bound: bool = False
    kill_switch: KillSwitchState | None = None
    unknown_commit: UnknownCommitResult | None = None
    control_operation: ControlOperation | None = None
    control_outcome: ControlOutcome | None = None
    active_record_rejected: bool = False
    control_audit_failure: bool = False
    rollback_failure: bool = False


def _validate_material(material: ObservationMaterial) -> None:
    if not isinstance(material, ObservationMaterial):
        raise ObserverInputRejected("observation_material_invalid")
    if not isinstance(material.environment, Environment):
        raise ObserverInputRejected("environment_invalid")
    for value in (
        material.snapshot_age_over_bound,
        material.active_record_rejected,
        material.control_audit_failure,
        material.rollback_failure,
    ):
        if type(value) is not bool:
            raise ObserverInputRejected("observation_boolean_invalid")

    decision = material.admission_decision
    if decision is not None:
        if (
            not isinstance(decision, AdmissionDecision)
            or decision.schema_version != DECISION_SCHEMA_VERSION
            or not isinstance(decision.decision, DecisionValue)
            or not isinstance(decision.lane, AdmissionLane)
            or not isinstance(decision.reason_code, DecisionReason)
        ):
            raise ObserverInputRejected("admission_decision_invalid")
        if decision.reason_code.value not in MANIFEST_DECISION_REASON_VALUES:
            raise ObserverInputRejected("reason_not_in_manifest_domain")
        if (decision.decision, decision.lane) != _DECISION_SHAPES[
            decision.reason_code
        ]:
            raise ObserverInputRejected("admission_decision_shape_invalid")

    age = material.snapshot_age_seconds
    if age is not None:
        if isinstance(age, bool) or not isinstance(age, (int, float)):
            raise ObserverInputRejected("snapshot_age_invalid")
        if not isfinite(float(age)) or age < 0:
            raise ObserverInputRejected("snapshot_age_invalid")
    if material.snapshot_age_over_bound and age is None:
        raise ObserverInputRejected("snapshot_age_bound_without_age")

    if material.kill_switch is not None and not isinstance(
        material.kill_switch, KillSwitchState
    ):
        raise ObserverInputRejected("kill_switch_invalid")
    if (
        material.unknown_commit is not None
        and material.unknown_commit != UnknownCommitResult()
    ):
        raise ObserverInputRejected("unknown_commit_posture_invalid")

    operation_supplied = material.control_operation is not None
    outcome_supplied = material.control_outcome is not None
    if operation_supplied != outcome_supplied:
        raise ObserverInputRejected("control_operation_outcome_pair_required")
    if operation_supplied and (
        not isinstance(material.control_operation, ControlOperation)
        or not isinstance(material.control_outcome, ControlOutcome)
    ):
        raise ObserverInputRejected("control_operation_or_outcome_invalid")

    if material.active_record_rejected and (
        decision is None
        or decision.lane is not AdmissionLane.ORDINARY_PRACTICE
        or decision.reason_code not in _ACTIVE_RECORD_ALERT_REASONS
    ):
        raise ObserverInputRejected("active_record_rejection_unproved")
    if material.control_audit_failure and not operation_supplied:
        raise ObserverInputRejected("control_audit_failure_without_operation")
    if (
        material.rollback_failure
        and material.control_operation is not ControlOperation.WITHDRAW
    ):
        raise ObserverInputRejected("rollback_failure_without_withdraw")


def _metric(
    name: MetricName,
    labels: tuple[tuple[str, str], ...],
    value: int | float,
) -> MetricIntent:
    return MetricIntent(name=name, kind=METRIC_KINDS[name], labels=labels, value=value)


def build_observation_batch(material: ObservationMaterial) -> ObservationBatch:
    """Build one immutable intent batch after complete fail-closed validation."""

    _validate_material(material)
    environment_label = (("environment", material.environment.value),)
    metrics: list[MetricIntent] = []
    alerts: set[AlertId] = set()

    decision = material.admission_decision
    if decision is not None:
        metrics.append(
            _metric(
                MetricName.ADMISSION_DECISIONS,
                environment_label
                + (
                    ("lane", decision.lane.value),
                    ("outcome", decision.decision.value),
                    ("reason_code", decision.reason_code.value),
                ),
                1,
            )
        )
        if decision.reason_code in _SNAPSHOT_ALERT_REASONS:
            alerts.add(AlertId.SNAPSHOT_INVALID_OR_STALE)

    if material.snapshot_age_seconds is not None:
        metrics.append(
            _metric(
                MetricName.SNAPSHOT_AGE,
                environment_label,
                material.snapshot_age_seconds,
            )
        )
    if material.snapshot_age_over_bound:
        alerts.add(AlertId.SNAPSHOT_INVALID_OR_STALE)

    if material.kill_switch is not None:
        engaged = material.kill_switch is KillSwitchState.ENGAGED
        metrics.append(
            _metric(MetricName.KILL_SWITCH, environment_label, int(engaged))
        )
        if engaged:
            alerts.add(AlertId.KILL_SWITCH_ENGAGED)

    if material.unknown_commit is not None:
        metrics.append(_metric(MetricName.UNKNOWN_COMMIT, environment_label, 1))
        alerts.add(AlertId.UNKNOWN_COMMIT)

    if material.control_operation is not None:
        metrics.append(
            _metric(
                MetricName.CONTROL_COMMANDS,
                environment_label
                + (
                    (
                        "operation",
                        CONTROL_OPERATION_LABELS[material.control_operation],
                    ),
                    ("outcome", material.control_outcome.value),
                ),
                1,
            )
        )

    if material.active_record_rejected:
        alerts.add(AlertId.ACTIVE_RECORD_REJECTED)
    if material.control_audit_failure:
        alerts.add(AlertId.CONTROL_AUDIT_FAILURE)
    if material.rollback_failure:
        alerts.add(AlertId.ROLLBACK_FAILURE)

    ordered_alerts = tuple(
        AlertIntent(AlertId(value))
        for value in ALERT_ID_VALUES
        if AlertId(value) in alerts
    )
    return ObservationBatch(metrics=tuple(metrics), alerts=ordered_alerts)


@dataclass(frozen=True, slots=True)
class ObserverGeneration:
    """The only admitted adapter generation is globally disabled."""

    enabled: bool = False

    def __post_init__(self) -> None:
        if self.enabled is not False:
            raise ObserverInputRejected("enabled_generation_not_admitted")


DEFAULT_DISABLED_OBSERVER_GENERATION = ObserverGeneration()


@dataclass(frozen=True, slots=True)
class CheckInObserverAdapter:
    """Unmounted adapter whose disabled path performs no material access."""

    generation: ObserverGeneration = DEFAULT_DISABLED_OBSERVER_GENERATION

    def __post_init__(self) -> None:
        if not isinstance(self.generation, ObserverGeneration):
            raise ObserverInputRejected("observer_generation_invalid")

    def observe(
        self,
        material_supplier: Callable[[], ObservationMaterial],
    ) -> ObservationBatch:
        """Return empty before supplier access; no enabled branch is admitted."""

        if self.generation.enabled is False:
            return EMPTY_OBSERVATION_BATCH
        raise AssertionError("enabled observer generation is structurally unreachable")


DEFAULT_CHECK_IN_OBSERVER_ADAPTER = CheckInObserverAdapter()
