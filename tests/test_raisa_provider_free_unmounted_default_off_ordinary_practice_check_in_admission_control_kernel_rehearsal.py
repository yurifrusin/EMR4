from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import jsonschema

from orchestration_harness.check_in_admission_control import (
    SCHEMA_VERSION,
    AdmissionLane,
    AdmissionRequest,
    AdmissionSnapshot,
    AdmissionState,
    CommandValidationReason,
    ControlCommandEnvelope,
    ControlOperation,
    DecisionReason,
    KillSwitchState,
    OrdinaryAdmissionRecord,
    REHEARSAL_PROFILE,
    engage_kill_switch,
    evaluate_admission,
    transition_record,
    unknown_commit_result,
    validate_command_envelope,
)
from scripts.raisa_provider_free_unmounted_default_off_ordinary_practice_check_in_admission_control_kernel_rehearsal import (
    CONTRACT,
    SCHEMA,
    build_evidence,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]


def _record(state: AdmissionState, *, evidence: bool = True) -> OrdinaryAdmissionRecord:
    return OrdinaryAdmissionRecord(
        state=state,
        practice_id="synthetic-practice-001",
        environment="test",
        operation_family="canonical_check_in",
        record_version=1,
        snapshot_generation=7,
        operational_evidence_valid=evidence,
    )


def _snapshot(
    *,
    record: OrdinaryAdmissionRecord | None = None,
    kill: KillSwitchState = KillSwitchState.CLEAR,
) -> AdmissionSnapshot:
    return AdmissionSnapshot(
        schema_version=SCHEMA_VERSION,
        signature_valid=True,
        authority_git_object="752b521c59f5b44bf46de0cf776a33ac74b8134d",
        authority_git_object_resolved=True,
        fresh=True,
        environment="test",
        snapshot_generation=7,
        snapshot_digest="a" * 64,
        current_record_count=0 if record is None else 1,
        kill_switch=kill,
        ordinary_record=record,
    )


def _request(*, synthetic: bool = False, feature: bool = True) -> AdmissionRequest:
    return AdmissionRequest(
        feature_enabled=feature,
        authored_synthetic_admitted=synthetic,
        practice_id="synthetic-practice-001",
        environment="test",
    )


def _command() -> ControlCommandEnvelope:
    return ControlCommandEnvelope(
        operation_id=ControlOperation.PREPARE.value,
        authenticated_current_human=True,
        dedicated_operator_role=True,
        server_owned_practice_scope=True,
        server_owned_environment_scope=True,
        correlation_id="correlation-001",
        idempotency_key="idempotency-001",
        complete_request_digest="b" * 64,
        idempotency_bound_to_complete_request_digest=True,
        expected_record_version=0,
        expected_snapshot_generation=7,
        closed_reason_code="planned_rehearsal",
        authority_git_object="752b521c59f5b44bf46de0cf776a33ac74b8134d",
        authority_git_object_resolved=True,
        fresh=True,
        append_only_audit_available=True,
        bounded_patient_free_receipt=True,
    )


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_rehearsal_profile_has_zero_active_records_and_no_activation_authority() -> None:
    assert REHEARSAL_PROFILE.canonical_active_ordinary_record_count == 0
    assert REHEARSAL_PROFILE.ordinary_activation_authority_granted is False


def test_missing_snapshot_denies() -> None:
    decision = evaluate_admission(None, _request())
    assert decision.admitted is False
    assert decision.reason_code is DecisionReason.SNAPSHOT_MISSING


def test_feature_disabled_precedes_lane_evaluation() -> None:
    decision = evaluate_admission(_snapshot(), _request(synthetic=True, feature=False))
    assert decision.admitted is False
    assert decision.reason_code is DecisionReason.FEATURE_DISABLED


def test_kill_switch_dominates_synthetic_lane() -> None:
    decision = evaluate_admission(
        _snapshot(kill=KillSwitchState.ENGAGED), _request(synthetic=True)
    )
    assert decision.admitted is False
    assert decision.reason_code is DecisionReason.KILL_SWITCH_ENGAGED


def test_kill_switch_dominates_ordinary_lane() -> None:
    decision = evaluate_admission(
        _snapshot(record=_record(AdmissionState.ACTIVE), kill=KillSwitchState.ENGAGED),
        _request(),
    )
    assert decision.admitted is False
    assert decision.reason_code is DecisionReason.KILL_SWITCH_ENGAGED


def test_lane_overlap_denies() -> None:
    decision = evaluate_admission(
        _snapshot(record=_record(AdmissionState.ACTIVE)), _request(synthetic=True)
    )
    assert decision.admitted is False
    assert decision.lane is AdmissionLane.AMBIGUOUS
    assert decision.reason_code is DecisionReason.LANE_AMBIGUOUS


def test_synthetic_only_lane_preserves_admission() -> None:
    decision = evaluate_admission(_snapshot(), _request(synthetic=True))
    assert decision.admitted is True
    assert decision.lane is AdmissionLane.AUTHORED_SYNTHETIC
    assert decision.reason_code is DecisionReason.ADMITTED_SYNTHETIC


def test_active_ordinary_record_cannot_release_admission() -> None:
    decision = evaluate_admission(
        _snapshot(record=_record(AdmissionState.ACTIVE)), _request()
    )
    assert decision.admitted is False
    assert decision.lane is AdmissionLane.ORDINARY_PRACTICE
    assert decision.reason_code is DecisionReason.ORDINARY_ACTIVATION_CLOSED


def test_abbreviated_snapshot_git_object_denies() -> None:
    decision = evaluate_admission(
        replace(_snapshot(), authority_git_object="752b521"), _request()
    )
    assert decision.reason_code is DecisionReason.SNAPSHOT_INVALID


def test_prepared_to_active_is_represented_but_denied() -> None:
    result = transition_record(AdmissionState.PREPARED, ControlOperation.ACTIVATE)
    assert result.accepted is False
    assert result.to_state is AdmissionState.PREPARED


def test_every_accepted_record_transition_is_non_admitting() -> None:
    for state in AdmissionState:
        for operation in ControlOperation:
            result = transition_record(state, operation)
            if result.accepted:
                assert result.to_state is not AdmissionState.ACTIVE


def test_suspend_and_withdraw_are_disable_only() -> None:
    suspended = transition_record(AdmissionState.ACTIVE, ControlOperation.SUSPEND)
    withdrawn = transition_record(AdmissionState.ACTIVE, ControlOperation.WITHDRAW)
    assert suspended.accepted and suspended.to_state is AdmissionState.SUSPENDED
    assert withdrawn.accepted and withdrawn.to_state is AdmissionState.WITHDRAWN


def test_withdrawn_is_terminal() -> None:
    for operation in ControlOperation:
        assert transition_record(AdmissionState.WITHDRAWN, operation).accepted is False


def test_kill_switch_has_no_in_place_clear() -> None:
    first = engage_kill_switch(KillSwitchState.CLEAR)
    second = engage_kill_switch(KillSwitchState.ENGAGED)
    assert first.accepted and first.to_state is KillSwitchState.ENGAGED
    assert second.accepted is False
    assert second.to_state is KillSwitchState.ENGAGED


def test_complete_command_envelope_validates_without_dispatch() -> None:
    result = validate_command_envelope(_command())
    assert result.accepted is True
    assert result.reason_code is CommandValidationReason.ACCEPTED


def test_seven_character_command_git_object_is_rejected() -> None:
    result = validate_command_envelope(
        replace(_command(), authority_git_object="752b521")
    )
    assert result.accepted is False
    assert result.reason_code is CommandValidationReason.AUTHORITY_GIT_OBJECT_INVALID


def test_unknown_commit_releases_no_success_and_forbids_retry() -> None:
    result = unknown_commit_result()
    assert result.success_released is False
    assert result.readback_required is True
    assert result.retry_allowed is False


def test_contract_is_closed_against_extra_top_level_field() -> None:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    hostile = dict(contract)
    hostile["unexpected"] = True
    try:
        validate_contract(hostile, schema, normative=contract)
    except (jsonschema.ValidationError, ValueError):
        pass
    else:
        raise AssertionError("extra contract field escaped")


def test_deterministic_evidence_exceeds_frozen_thresholds() -> None:
    evidence = build_evidence()
    assert evidence["status"] == "passed"
    assert evidence["source_binding_count"] == 7
    assert evidence["canonical_active_ordinary_record_count"] == 0
    assert evidence["ordinary_admission_release_count"] == 0
    assert evidence["total_scenario_count"] >= 24
    assert evidence["hostile_contract_mutations"]["count"] >= 192
    assert evidence["hostile_contract_mutations"]["escapes"] == 0
    assert evidence["product_or_configuration_changed"] is False
    assert evidence["provider_or_network_used"] is False
    assert evidence["live_clockwork_adopted"] is False
