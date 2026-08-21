from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import native_post_hmr_pre_request_controller as controller
from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic
from scripts import (
    deepseek_native_harness_provider_free_custom_runner_pre_request_failure_coordinate_diagnosis
    as accepted_diagnosis,
)
from scripts import (
    deepseek_native_harness_provider_free_post_hmr_pre_request_diagnostic_sidecar_integration_rehearsal
    as rehearsal,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_runner,
)


OPERATION_ID = rehearsal.OPERATION_ID
CONTRACT = json.loads(rehearsal.CONTRACT_PATH.read_bytes())
ATTEMPT_ID = CONTRACT["fixture_identity"]["attempt_id"]
CANDIDATE_SOURCE = CONTRACT["fixture_identity"]["candidate_source"]


def _sidecar(
    *,
    stage: str = "loader_readiness_wait",
    cause_coordinate: str = "operation_rejected",
    error_name: str = "Error",
    **identity_overrides: str,
) -> dict:
    return diagnostic.build_diagnostic_from_fixture(
        {"name": error_name, "constructor_name": error_name},
        operation_id=identity_overrides.get("operation_id", OPERATION_ID),
        attempt_id=identity_overrides.get("attempt_id", ATTEMPT_ID),
        candidate_source=identity_overrides.get("candidate_source", CANDIDATE_SOURCE),
        stage=stage,
        cause_coordinate=cause_coordinate,
    )


def _broker(**overrides: object) -> dict:
    value = controller.build_broker_reading(
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
    )
    value.update(overrides)
    return value


def _fixture_paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "disposable"
    root.mkdir()
    sidecar_path = root / "post-hmr-diagnostic.json"
    broker_path = root / "broker-reading.json"
    broker_path.write_bytes(controller.broker_reading_bytes(_broker()))
    return root, sidecar_path, broker_path


def _select(root: Path, sidecar_path: Path, broker_path: Path) -> dict:
    return controller.select_post_hmr_failure(
        diagnostic_path=sidecar_path,
        broker_reading_path=broker_path,
        disposable_root=root,
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
    )


def test_contract_schemas_and_full_source_bindings_are_exact() -> None:
    contract_schema = json.loads(rehearsal.CONTRACT_SCHEMA_PATH.read_bytes())
    broker_schema = json.loads(rehearsal.BROKER_SCHEMA_PATH.read_bytes())
    evidence_schema = json.loads(rehearsal.EVIDENCE_SCHEMA_PATH.read_bytes())
    for schema in (contract_schema, broker_schema, evidence_schema):
        jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(contract_schema).validate(CONTRACT)
    jsonschema.Draft202012Validator(broker_schema).validate(_broker())
    assert CONTRACT["planning_source"] == "cc75a9f8991120b66bf64ee12d415462f2cbfbb3"
    assert all(
        len(value) == 64
        for value in CONTRACT["source_bindings"].values()
    )
    assert len(CANDIDATE_SOURCE) == 40


def test_accepted_runner_is_unchanged_and_future_runner_is_exact_derivative() -> None:
    accepted_payload = accepted_runner.runner_source(accepted_diagnosis.TARGET_PATH)
    bindings = CONTRACT["source_bindings"]
    assert hashlib.sha256(accepted_payload).hexdigest() == bindings["accepted_runner_sha256"]
    future_payload = controller.derive_future_runner_source(
        accepted_payload,
        expected_accepted_sha256=bindings["accepted_runner_sha256"],
    )
    result = controller.validate_future_runner_source(
        future_payload,
        accepted_payload=accepted_payload,
        expected_accepted_sha256=bindings["accepted_runner_sha256"],
    )
    assert result["sha256"] == bindings["future_runner_sha256"]
    assert all(result["checks"].values())
    assert list(result["stage_positions"]) == list(diagnostic.PRE_REQUEST_STAGES)


def test_future_runner_closes_diagnostic_interval_before_flush_and_rethrows() -> None:
    accepted_payload = accepted_runner.runner_source(accepted_diagnosis.TARGET_PATH)
    source = controller.derive_future_runner_source(
        accepted_payload,
        expected_accepted_sha256=CONTRACT["source_bindings"]["accepted_runner_sha256"],
    ).decode()
    first_turn = source.index('failureStage = "first_turn_idle_wait"')
    close = source.index("diagnosticActive = false;")
    flush = source.index("await sessions.flush(agent.session);")
    assert first_turn < close < flush
    assert source.count("writePostHmrDiagnostic(") == 1
    assert source.count("throw error;") == 1
    assert 'failure_code: "CUSTOM_RUNNER_FAILURE"' in source
    assert all(word not in source.lower() for word in ("retry", "resume", "fallback"))


def test_future_runner_derivation_rejects_source_or_marker_substitution() -> None:
    accepted_payload = accepted_runner.runner_source(accepted_diagnosis.TARGET_PATH)
    with pytest.raises(diagnostic.PostHmrDiagnosticError, match="source_sha256_mismatch"):
        controller.derive_future_runner_source(
            accepted_payload + b"\n",
            expected_accepted_sha256=CONTRACT["source_bindings"]["accepted_runner_sha256"],
        )
    altered = accepted_payload.replace(
        b'const agents = ctx.get("agents");', b'const changed = ctx.get("agents");'
    )
    altered_sha = hashlib.sha256(altered).hexdigest()
    with pytest.raises(diagnostic.PostHmrDiagnosticError, match="source_fragment_missing"):
        controller.derive_future_runner_source(
            altered, expected_accepted_sha256=altered_sha
        )


def test_every_stage_and_error_kind_requires_broker_zero(tmp_path: Path) -> None:
    root, sidecar_path, broker_path = _fixture_paths(tmp_path)
    error_names = {
        "AggregateError": "aggregate_error",
        "Error": "error",
        "InvalidPresetIdError": "invalid_preset_id_error",
        "PresetMountError": "preset_mount_error",
        "TypeError": "type_error",
        "UnknownPresetError": "unknown_preset_error",
        "DescriptiveFailure": "unknown",
    }
    for stage in diagnostic.PRE_REQUEST_STAGES:
        for error_name, error_kind in error_names.items():
            sidecar_path.write_bytes(
                diagnostic.diagnostic_bytes(
                    _sidecar(stage=stage, error_name=error_name)
                )
            )
            selected = _select(root, sidecar_path, broker_path)
            assert selected["coordinate"] == "post_hmr_pre_request_failure"
            assert selected["broker_zero"] is True
            assert selected["pre_request_supported"] is True
            assert selected["stage"] == stage
            assert selected["error_kind"] == error_kind
            assert selected["raw_stream_read"] is False


@pytest.mark.parametrize(
    ("stage", "cause_coordinate"),
    [
        ("required_service_lookup", "required_service_missing"),
        ("preset_root_roster_admission", "preset_root_roster_mismatch"),
    ],
)
def test_special_causes_are_preserved_only_at_their_exact_stage(
    tmp_path: Path, stage: str, cause_coordinate: str
) -> None:
    root, sidecar_path, broker_path = _fixture_paths(tmp_path)
    sidecar_path.write_bytes(
        diagnostic.diagnostic_bytes(
            _sidecar(stage=stage, cause_coordinate=cause_coordinate)
        )
    )
    selected = _select(root, sidecar_path, broker_path)
    assert selected["coordinate"] == "post_hmr_pre_request_failure"
    assert selected["cause_coordinate"] == cause_coordinate


@pytest.mark.parametrize("counter", controller.BROKER_COUNTERS)
def test_each_nonzero_broker_counter_makes_request_boundary_unresolved(
    tmp_path: Path, counter: str
) -> None:
    root, sidecar_path, broker_path = _fixture_paths(tmp_path)
    sidecar_path.write_bytes(diagnostic.diagnostic_bytes(_sidecar()))
    reading = controller.build_broker_reading(
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
        counters={counter: 1},
    )
    broker_path.write_bytes(controller.broker_reading_bytes(reading))
    selected = _select(root, sidecar_path, broker_path)
    assert selected["coordinate"] == "post_hmr_request_boundary_unresolved"
    assert selected["diagnostic_accepted"] is True
    assert selected["broker_zero"] is False
    assert selected["pre_request_supported"] is False


def test_absent_malformed_noncanonical_and_mismatched_sidecars_fall_back(
    tmp_path: Path,
) -> None:
    root, sidecar_path, broker_path = _fixture_paths(tmp_path)
    assert _select(root, sidecar_path, broker_path)["coordinate"] == (
        "native_harness_terminal_failure"
    )

    sidecar_path.write_bytes(b"not-json")
    assert _select(root, sidecar_path, broker_path)["coordinate"] == (
        "native_harness_terminal_failure"
    )

    value = _sidecar()
    sidecar_path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    assert _select(root, sidecar_path, broker_path)["coordinate"] == (
        "native_harness_terminal_failure"
    )

    sidecar_path.write_bytes(
        diagnostic.diagnostic_bytes(_sidecar(attempt_id="different-attempt"))
    )
    selected = _select(root, sidecar_path, broker_path)
    assert selected["coordinate"] == "native_harness_terminal_failure"
    assert selected["diagnostic_accepted"] is False


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ({"request_count": True}, "broker_counter_invalid"),
        ({"request_count": -1}, "broker_counter_invalid"),
        ({"raw_broker_stream_retained": True}, "broker_raw_retention_invalid"),
        ({"candidate_source": "cc75a9f"}, "candidate_source_invalid"),
        ({"extra": "descriptive state"}, "broker_reading_keys_invalid"),
    ],
)
def test_broker_vocabulary_types_and_raw_retention_fail_closed(
    mutation: dict[str, object], error: str
) -> None:
    with pytest.raises(controller.PostHmrControllerError, match=error):
        controller.validate_broker_reading(_broker(**mutation))


def test_missing_broker_key_fails_closed() -> None:
    reading = _broker()
    reading.pop("request_rejected")
    with pytest.raises(
        controller.PostHmrControllerError, match="broker_reading_keys_invalid"
    ):
        controller.validate_broker_reading(reading)


def test_invalid_broker_file_rejects_join_instead_of_falling_back(tmp_path: Path) -> None:
    root, sidecar_path, broker_path = _fixture_paths(tmp_path)
    sidecar_path.write_bytes(diagnostic.diagnostic_bytes(_sidecar()))

    broker_path.write_bytes(b"not-json")
    with pytest.raises(controller.PostHmrControllerError, match="broker_json_invalid"):
        _select(root, sidecar_path, broker_path)

    broker_path.write_text(json.dumps(_broker()) + "\n", encoding="utf-8")
    with pytest.raises(
        controller.PostHmrControllerError, match="broker_canonical_bytes_required"
    ):
        _select(root, sidecar_path, broker_path)

    mismatched = _broker(attempt_id="different-attempt")
    broker_path.write_bytes(controller.broker_reading_bytes(mismatched))
    with pytest.raises(
        controller.PostHmrControllerError, match="broker_runtime_identity_mismatch"
    ):
        _select(root, sidecar_path, broker_path)


def test_escaped_and_symlinked_evidence_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, sidecar_path, broker_path = _fixture_paths(tmp_path)
    sidecar_path.write_bytes(diagnostic.diagnostic_bytes(_sidecar()))
    outside = tmp_path / "outside-broker.json"
    outside.write_bytes(controller.broker_reading_bytes(_broker()))
    with pytest.raises(
        controller.PostHmrControllerError,
        match="broker_path_outside_disposable_root",
    ):
        _select(root, sidecar_path, outside)

    linked_broker = root / "linked-broker.json"
    linked_sidecar = root / "linked-sidecar.json"
    original_is_symlink = Path.is_symlink
    declared_links = {linked_broker, linked_sidecar}
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda path: path in declared_links or original_is_symlink(path),
    )
    with pytest.raises(controller.PostHmrControllerError, match="broker_path_invalid"):
        _select(root, sidecar_path, linked_broker)

    selected = _select(root, linked_sidecar, broker_path)
    assert selected["coordinate"] == "native_harness_terminal_failure"
    assert selected["diagnostic_accepted"] is False


def test_oversized_sidecar_falls_back_and_oversized_broker_rejects(tmp_path: Path) -> None:
    root, sidecar_path, broker_path = _fixture_paths(tmp_path)
    sidecar_path.write_bytes(b"x" * (diagnostic.MAX_SIDECAR_BYTES + 1))
    assert _select(root, sidecar_path, broker_path)["coordinate"] == (
        "native_harness_terminal_failure"
    )
    sidecar_path.write_bytes(diagnostic.diagnostic_bytes(_sidecar()))
    broker_path.write_bytes(b"x" * (controller.MAX_BROKER_READING_BYTES + 1))
    with pytest.raises(controller.PostHmrControllerError, match="broker_file_invalid"):
        _select(root, sidecar_path, broker_path)


def test_generated_evidence_report_and_efficacy_are_canonical() -> None:
    expected = rehearsal._expected_outputs()
    assert all(path.read_bytes() == payload for path, payload in expected.items())
    evidence = json.loads(rehearsal.EVIDENCE_PATH.read_bytes())
    schema = json.loads(rehearsal.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["result"] == "pass"
    assert evidence["join_matrix"] == {
        "error_kind_count": 7,
        "invalid_sidecar_coordinate": "native_harness_terminal_failure",
        "nonzero_coordinate": "post_hmr_request_boundary_unresolved",
        "nonzero_counter_count": 5,
        "pre_request_requires_both": True,
        "special_cause_count": 2,
        "stage_count": 7,
        "valid_zero_coordinate": "post_hmr_pre_request_failure",
    }
    assert all(value == 0 for value in evidence["proof_boundary"].values())
    assert evidence["cleanup"]["disposable_fixture_root_absent"] is True


def test_plan_and_threat_preserve_provider_free_fail_closed_boundaries() -> None:
    plan = rehearsal.PLAN_PATH.read_text(encoding="utf-8")
    threat = (
        Path("docs/security")
        / f"{OPERATION_ID}-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    assert "seven accepted operations" in plan
    assert tuple(diagnostic.PRE_REQUEST_STAGES) == (
        "loader_readiness_wait",
        "required_service_lookup",
        "preset_root_roster_admission",
        "agent_create_setup_publish",
        "initial_idle_wait",
        "first_followup_dispatch",
        "first_turn_idle_wait",
    )
    for counter in controller.BROKER_COUNTERS:
        assert f"`{counter}`" in plan
    assert "No Node/Harness/broker/worker/model/provider process" in plan
    assert "full 40-character candidate identity" in plan
    assert "It opens no runtime, model, provider, product, data" in threat
    assert "every process, request, network, database and Docker count at zero" in threat
