from __future__ import annotations

from dataclasses import fields, replace

import pytest

from app.services.appointment_check_in_environment_evidence_gate import (
    EVIDENCE_GATE_READING_SCHEMA_VERSION,
    EnvironmentEvidenceGateReading,
)
from orchestration_harness.check_in_admission_control import (
    SCHEMA_VERSION,
    AdmissionLane,
    AdmissionRequest,
    AdmissionSnapshot,
    AdmissionState,
    DecisionReason,
    KillSwitchState,
    OrdinaryAdmissionRecord,
)
from orchestration_harness.check_in_environment_evidence_admission import (
    evaluate_admission_with_environment_evidence,
)


ENVIRONMENT_IDENTIFIER = "env:authored-reference"
MANIFEST_DIGEST = "c" * 64


def _record(
    *,
    state: AdmissionState = AdmissionState.ACTIVE,
    operational_evidence_valid: bool = True,
) -> OrdinaryAdmissionRecord:
    return OrdinaryAdmissionRecord(
        state=state,
        practice_id="synthetic-practice-001",
        environment="test",
        operation_family="canonical_check_in",
        record_version=1,
        snapshot_generation=7,
        operational_evidence_valid=operational_evidence_valid,
    )


def _snapshot(
    *,
    record: OrdinaryAdmissionRecord | None = None,
    kill_switch: KillSwitchState = KillSwitchState.CLEAR,
    identifier: str | None = ENVIRONMENT_IDENTIFIER,
    manifest_digest: str | None = MANIFEST_DIGEST,
) -> AdmissionSnapshot:
    return AdmissionSnapshot(
        schema_version=SCHEMA_VERSION,
        signature_valid=True,
        authority_git_object="4204ec6348abb0f92b1a30314699d4a469fa860a",
        authority_git_object_resolved=True,
        fresh=True,
        environment="test",
        snapshot_generation=7,
        snapshot_digest="a" * 64,
        current_record_count=0 if record is None else 1,
        kill_switch=kill_switch,
        ordinary_record=record,
        environment_evidence_identifier=identifier,
        environment_evidence_manifest_digest=manifest_digest,
    )


def _request(*, synthetic: bool = False, feature: bool = True) -> AdmissionRequest:
    return AdmissionRequest(
        feature_enabled=feature,
        authored_synthetic_admitted=synthetic,
        practice_id="synthetic-practice-001",
        environment="test",
    )


def _reading() -> EnvironmentEvidenceGateReading:
    return EnvironmentEvidenceGateReading(
        schema_version=EVIDENCE_GATE_READING_SCHEMA_VERSION,
        outcome="satisfied",
        reason_code="evidence_gate_satisfied",
        environment_identifier=ENVIRONMENT_IDENTIFIER,
        admission_snapshot_generation=7,
        manifest_digest=MANIFEST_DIGEST,
    )


def _evaluate(
    reading: object,
    *,
    snapshot: AdmissionSnapshot | None = None,
    request: AdmissionRequest | None = None,
):
    return evaluate_admission_with_environment_evidence(
        _snapshot(record=_record()) if snapshot is None else snapshot,
        _request() if request is None else request,
        reading,
    )


def test_exact_satisfied_reading_still_ends_at_activation_closed() -> None:
    decision = _evaluate(_reading())
    assert decision.admitted is False
    assert decision.lane is AdmissionLane.ORDINARY_PRACTICE
    assert decision.reason_code is DecisionReason.ORDINARY_ACTIVATION_CLOSED


def test_authored_synthetic_lane_is_unchanged_without_a_reading() -> None:
    decision = evaluate_admission_with_environment_evidence(
        _snapshot(), _request(synthetic=True), None
    )
    assert decision.admitted is True
    assert decision.lane is AdmissionLane.AUTHORED_SYNTHETIC
    assert decision.reason_code is DecisionReason.ADMITTED_SYNTHETIC


@pytest.mark.parametrize(
    "reading",
    [
        None,
        replace(_reading(), schema_version="v2"),
        replace(_reading(), outcome="denied"),
        replace(_reading(), reason_code="manifest_invalid"),
        replace(_reading(), environment_identifier="env:other"),
        replace(_reading(), admission_snapshot_generation=8),
        replace(_reading(), manifest_digest="d" * 64),
    ],
)
def test_missing_denied_or_mismatched_reading_denies(reading: object) -> None:
    decision = _evaluate(reading)
    assert decision.admitted is False
    assert decision.reason_code is DecisionReason.ORDINARY_EVIDENCE_MISSING


@pytest.mark.parametrize(
    "snapshot",
    [
        _snapshot(record=_record(), identifier=None),
        _snapshot(record=_record(), identifier="test"),
        _snapshot(record=_record(), manifest_digest=None),
        _snapshot(record=_record(), manifest_digest="short"),
    ],
)
def test_missing_or_malformed_snapshot_binding_denies(
    snapshot: AdmissionSnapshot,
) -> None:
    decision = _evaluate(_reading(), snapshot=snapshot)
    assert decision.reason_code is DecisionReason.ORDINARY_EVIDENCE_MISSING


def test_subclass_and_duck_type_cannot_substitute_for_exact_reading() -> None:
    class ReadingSubclass(EnvironmentEvidenceGateReading):
        pass

    class DuckReading:
        schema_version = EVIDENCE_GATE_READING_SCHEMA_VERSION
        outcome = "satisfied"
        reason_code = "evidence_gate_satisfied"
        environment_identifier = ENVIRONMENT_IDENTIFIER
        admission_snapshot_generation = 7
        manifest_digest = MANIFEST_DIGEST

    subclass = ReadingSubclass(
        EVIDENCE_GATE_READING_SCHEMA_VERSION,
        "satisfied",
        "evidence_gate_satisfied",
        ENVIRONMENT_IDENTIFIER,
        7,
        MANIFEST_DIGEST,
    )
    for reading in (subclass, DuckReading()):
        assert _evaluate(reading).reason_code is DecisionReason.ORDINARY_EVIDENCE_MISSING


def test_typed_reading_cannot_bypass_existing_operational_evidence_boolean() -> None:
    decision = _evaluate(
        _reading(),
        snapshot=_snapshot(
            record=_record(operational_evidence_valid=False),
        ),
    )
    assert decision.admitted is False
    assert decision.reason_code is DecisionReason.ORDINARY_EVIDENCE_MISSING


def test_existing_feature_kill_switch_lane_and_state_precedence_is_unchanged() -> None:
    cases = [
        (
            _snapshot(record=_record()),
            _request(feature=False),
            DecisionReason.FEATURE_DISABLED,
        ),
        (
            _snapshot(
                record=_record(),
                kill_switch=KillSwitchState.ENGAGED,
            ),
            _request(),
            DecisionReason.KILL_SWITCH_ENGAGED,
        ),
        (
            _snapshot(record=_record()),
            _request(synthetic=True),
            DecisionReason.LANE_AMBIGUOUS,
        ),
        (
            _snapshot(record=_record(state=AdmissionState.PREPARED)),
            _request(),
            DecisionReason.ORDINARY_STATE_NOT_ACTIVE,
        ),
    ]
    for snapshot, request, expected in cases:
        decision = _evaluate(_reading(), snapshot=snapshot, request=request)
        assert decision.reason_code is expected


def test_seam_preserves_the_six_field_decision_contract() -> None:
    assert [field.name for field in fields(_evaluate(_reading()))] == [
        "schema_version",
        "decision",
        "lane",
        "reason_code",
        "snapshot_generation",
        "snapshot_digest",
    ]


def test_no_ordinary_input_releases_admission() -> None:
    readings = [
        None,
        _reading(),
        replace(_reading(), outcome="denied"),
        replace(_reading(), admission_snapshot_generation=8),
    ]
    records = [
        _record(state=state, operational_evidence_valid=evidence)
        for state in AdmissionState
        for evidence in (False, True)
    ]
    for record in records:
        for reading in readings:
            decision = _evaluate(reading, snapshot=_snapshot(record=record))
            assert decision.admitted is False
