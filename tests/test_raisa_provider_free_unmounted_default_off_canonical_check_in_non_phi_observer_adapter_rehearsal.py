"""Admission for the unmounted default-off check-in observer adapter."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

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
from orchestration_harness.check_in_observability import (
    ALERT_ID_VALUES,
    CONTROL_OPERATION_LABELS,
    CONTROL_OUTCOME_VALUES,
    DEFAULT_CHECK_IN_OBSERVER_ADAPTER,
    EMPTY_OBSERVATION_BATCH,
    ENVIRONMENT_VALUES,
    FUTURE_ONLY_DECISION_REASON_VALUES,
    LANE_VALUES,
    MANIFEST_DECISION_REASON_VALUES,
    METRIC_KINDS,
    METRIC_LABEL_DOMAINS,
    OUTCOME_VALUES,
    REHEARSAL_ONLY_DECISION_REASON_VALUES,
    AlertId,
    CheckInObserverAdapter,
    ControlOutcome,
    Environment,
    MetricKind,
    MetricName,
    ObservationMaterial,
    ObserverGeneration,
    ObserverInputRejected,
    build_observation_batch,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "orchestration_harness/check_in_observability.py"
MANIFEST = ROOT / "docs/api-spine/manifests/canonical-check-in-non-phi-observability.json"
PLAN = ROOT / (
    "docs/raisa-provider-free-unmounted-default-off-canonical-check-in-non-phi-"
    "observer-adapter-rehearsal-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-unmounted-default-off-canonical-check-in-"
    "non-phi-observer-adapter-rehearsal-threat-model-delta.md"
)


DECISION_SHAPES = {
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
}


def _manifest() -> dict[str, object]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _decision(reason: DecisionReason) -> AdmissionDecision:
    outcome, lane = DECISION_SHAPES[reason]
    return AdmissionDecision(
        schema_version=DECISION_SCHEMA_VERSION,
        decision=outcome,
        lane=lane,
        reason_code=reason,
        snapshot_generation=None,
        snapshot_digest=None,
    )


def _manifest_metric(name: MetricName) -> dict[str, object]:
    metrics = _manifest()["observability"]["metric_families"]
    return next(item for item in metrics if item["name"] == name.value)


def test_module_constants_equal_the_exact_manifest_vocabulary() -> None:
    manifest = _manifest()["observability"]

    assert tuple(item["name"] for item in manifest["metric_families"]) == tuple(
        item.value for item in MetricName
    )
    for name in MetricName:
        source = _manifest_metric(name)
        assert source["kind"] == METRIC_KINDS[name].value
        assert tuple(
            (domain["label"], tuple(domain["values"]))
            for domain in source["label_domains"]
        ) == METRIC_LABEL_DOMAINS[name]
    assert tuple(item["alert_id"] for item in manifest["alerts"]) == ALERT_ID_VALUES
    assert all(item["severity"] == "critical" for item in manifest["alerts"])
    assert all(item["contains_identifier"] is False for item in manifest["alerts"])
    assert all(
        item["automatic_control_action"] is False for item in manifest["alerts"]
    )
    assert manifest["raw_request_or_response_allowed"] is False
    assert manifest["audit_record_used_as_metric"] is False
    assert manifest["telemetry_feedback_to_admission"] is False
    assert manifest["automatic_retry_or_control_action"] is False
    assert ENVIRONMENT_VALUES == ("development", "test", "staging", "production")
    assert LANE_VALUES == tuple(item.value for item in AdmissionLane)
    assert OUTCOME_VALUES == tuple(item.value for item in DecisionValue)


def test_shared_reasons_map_exactly_and_asymmetric_reasons_fail_closed() -> None:
    kernel_reasons = {item.value for item in DecisionReason}
    manifest_reasons = set(MANIFEST_DECISION_REASON_VALUES)
    shared = kernel_reasons & manifest_reasons

    assert shared == {item.value for item in DECISION_SHAPES}
    assert kernel_reasons - manifest_reasons == set(
        REHEARSAL_ONLY_DECISION_REASON_VALUES
    )
    assert manifest_reasons - kernel_reasons == set(FUTURE_ONLY_DECISION_REASON_VALUES)

    for reason in DECISION_SHAPES:
        batch = build_observation_batch(
            ObservationMaterial(
                environment=Environment.TEST,
                admission_decision=_decision(reason),
            )
        )
        assert len(batch.metrics) == 1
        metric = batch.metrics[0]
        assert metric.name is MetricName.ADMISSION_DECISIONS
        assert metric.kind is MetricKind.COUNTER
        assert metric.labels == (
            ("environment", "test"),
            ("lane", DECISION_SHAPES[reason][1].value),
            ("outcome", DECISION_SHAPES[reason][0].value),
            ("reason_code", reason.value),
        )
        assert metric.value == 1

    rehearsal_only = AdmissionDecision(
        schema_version=DECISION_SCHEMA_VERSION,
        decision=DecisionValue.DENIED,
        lane=AdmissionLane.ORDINARY_PRACTICE,
        reason_code=DecisionReason.ORDINARY_ACTIVATION_CLOSED,
        snapshot_generation=1,
        snapshot_digest="0" * 64,
    )
    with pytest.raises(ObserverInputRejected, match="reason_not_in_manifest_domain"):
        build_observation_batch(
            ObservationMaterial(
                environment=Environment.TEST,
                admission_decision=rehearsal_only,
            )
        )


def test_one_closed_material_can_produce_all_five_metrics_and_six_alerts() -> None:
    material = ObservationMaterial(
        environment=Environment.STAGING,
        admission_decision=_decision(DecisionReason.ORDINARY_BINDING_MISMATCH),
        snapshot_age_seconds=61.5,
        snapshot_age_over_bound=True,
        kill_switch=KillSwitchState.ENGAGED,
        unknown_commit=UnknownCommitResult(),
        control_operation=ControlOperation.WITHDRAW,
        control_outcome=ControlOutcome.FAILED,
        active_record_rejected=True,
        control_audit_failure=True,
        rollback_failure=True,
    )

    batch = build_observation_batch(material)

    assert tuple(item.name for item in batch.metrics) == tuple(MetricName)
    assert tuple(item.alert_id for item in batch.alerts) == tuple(AlertId)
    assert all(item.severity == "critical" for item in batch.alerts)
    assert all(item.contains_identifier is False for item in batch.alerts)
    assert all(item.automatic_control_action is False for item in batch.alerts)
    assert batch.metrics[1].value == 61.5
    assert batch.metrics[2].value == 1
    assert batch.metrics[3].value == 1
    assert batch.metrics[4].labels == (
        ("environment", "staging"),
        ("operation", "withdraw"),
        ("outcome", "failed"),
    )


def test_control_operation_and_outcome_domains_are_exhaustive() -> None:
    assert set(CONTROL_OPERATION_LABELS) == set(ControlOperation)
    assert tuple(CONTROL_OPERATION_LABELS.values()) == (
        "prepare",
        "activate",
        "suspend",
        "withdraw",
        "engage_kill_switch",
    )
    assert CONTROL_OUTCOME_VALUES == (
        "accepted",
        "replayed",
        "denied",
        "conflict",
        "uncertain",
        "failed",
    )
    for operation, short_label in CONTROL_OPERATION_LABELS.items():
        for outcome in ControlOutcome:
            batch = build_observation_batch(
                ObservationMaterial(
                    environment=Environment.DEVELOPMENT,
                    control_operation=operation,
                    control_outcome=outcome,
                )
            )
            assert batch.metrics[0].labels == (
                ("environment", "development"),
                ("operation", short_label),
                ("outcome", outcome.value),
            )


def test_globally_disabled_adapter_returns_empty_before_supplier_access() -> None:
    calls = 0

    def supplier() -> ObservationMaterial:
        nonlocal calls
        calls += 1
        raise AssertionError("disabled adapter accessed observation material")

    assert DEFAULT_CHECK_IN_OBSERVER_ADAPTER.observe(supplier) is (
        EMPTY_OBSERVATION_BATCH
    )
    assert CheckInObserverAdapter().observe(supplier) is EMPTY_OBSERVATION_BATCH
    assert calls == 0
    with pytest.raises(ObserverInputRejected, match="enabled_generation_not_admitted"):
        ObserverGeneration(enabled=True)
    with pytest.raises(ObserverInputRejected, match="enabled_generation_not_admitted"):
        ObserverGeneration(enabled=1)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("material", "reason"),
    [
        (
            ObservationMaterial(
                environment=Environment.TEST,
                snapshot_age_seconds=-1,
            ),
            "snapshot_age_invalid",
        ),
        (
            ObservationMaterial(
                environment=Environment.TEST,
                snapshot_age_seconds=float("inf"),
            ),
            "snapshot_age_invalid",
        ),
        (
            ObservationMaterial(
                environment=Environment.TEST,
                snapshot_age_over_bound=True,
            ),
            "snapshot_age_bound_without_age",
        ),
        (
            ObservationMaterial(
                environment=Environment.TEST,
                control_operation=ControlOperation.PREPARE,
            ),
            "control_operation_outcome_pair_required",
        ),
        (
            ObservationMaterial(
                environment=Environment.TEST,
                active_record_rejected=True,
            ),
            "active_record_rejection_unproved",
        ),
        (
            ObservationMaterial(
                environment=Environment.TEST,
                control_audit_failure=True,
            ),
            "control_audit_failure_without_operation",
        ),
        (
            ObservationMaterial(
                environment=Environment.TEST,
                control_operation=ControlOperation.SUSPEND,
                control_outcome=ControlOutcome.FAILED,
                rollback_failure=True,
            ),
            "rollback_failure_without_withdraw",
        ),
        (
            ObservationMaterial(
                environment=Environment.TEST,
                unknown_commit=UnknownCommitResult(retry_allowed=True),
            ),
            "unknown_commit_posture_invalid",
        ),
    ],
)
def test_contradictory_or_malformed_material_rejects_before_batch(
    material: ObservationMaterial,
    reason: str,
) -> None:
    with pytest.raises(ObserverInputRejected, match=reason):
        build_observation_batch(material)


def test_semantically_inconsistent_admission_decision_is_rejected() -> None:
    inconsistent = AdmissionDecision(
        schema_version=DECISION_SCHEMA_VERSION,
        decision=DecisionValue.ADMITTED,
        lane=AdmissionLane.AUTHORED_SYNTHETIC,
        reason_code=DecisionReason.FEATURE_DISABLED,
        snapshot_generation=None,
        snapshot_digest=None,
    )
    with pytest.raises(ObserverInputRejected, match="admission_decision_shape_invalid"):
        build_observation_batch(
            ObservationMaterial(
                environment=Environment.TEST,
                admission_decision=inconsistent,
            )
        )


def test_module_has_no_runtime_or_product_capability_and_docs_are_timestamped() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported_roots <= {
        "__future__",
        "collections",
        "dataclasses",
        "enum",
        "math",
        "orchestration_harness",
    }
    assert "app" not in imported_roots
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"open", "exec", "eval"}
        for node in ast.walk(tree)
    )
    for path in (PLAN, THREAT):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
        assert "Date: 2026-08-22" in head
        assert "Timestamp: 2026-08-22T23:59:22.8176645+10:00" in head
        assert "Australia/Brisbane" in head
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    assert "ordinary_activation_closed" in plan
    assert "must never be relabelled" in plan
    assert "zero-work disabled path" in plan
    assert "No `app/**`" in plan
    assert "automatic_control_action=false" in threat
