from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic
from scripts import (
    deepseek_native_harness_provider_free_custom_runner_pre_request_failure_coordinate_diagnosis
    as rehearsal,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_runner,
)


FULL_OID = "a" * 40
OPERATION_ID = (
    "deepseek-native-harness-provider-free-custom-runner-pre-request-failure-"
    "coordinate-diagnosis"
)
ATTEMPT_ID = "future-post-hmr-diagnostic-fixture-001"


def _diagnostic(**overrides):
    value = diagnostic.build_diagnostic_from_fixture(
        {"name": "PresetMountError", "message": "secret C:/patient/path"},
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=FULL_OID,
        stage="agent_create_setup_publish",
    )
    value.update(overrides)
    return value


def test_closed_vocabulary_is_single_ordered_contract() -> None:
    contract = json.loads(rehearsal.CONTRACT_PATH.read_bytes())
    assert contract["closed_vocabulary"] == {
        "stages": list(diagnostic.PRE_REQUEST_STAGES),
        "cause_coordinates": list(diagnostic.CAUSE_COORDINATES),
        "error_kinds": list(diagnostic.ERROR_KINDS),
    }
    assert len(set(diagnostic.PRE_REQUEST_STAGES)) == 7
    assert len(set(diagnostic.CAUSE_COORDINATES)) == 3
    assert len(set(diagnostic.ERROR_KINDS)) == 7


def test_every_stage_and_error_kind_is_admitted_without_raw_text() -> None:
    fixtures = {
        "AggregateError": "aggregate_error",
        "Error": "error",
        "InvalidPresetIdError": "invalid_preset_id_error",
        "PresetMountError": "preset_mount_error",
        "TypeError": "type_error",
        "UnknownPresetError": "unknown_preset_error",
        "C:/secret/patient.txt": "unknown",
    }
    for stage in diagnostic.PRE_REQUEST_STAGES:
        for name, expected_kind in fixtures.items():
            value = diagnostic.build_diagnostic_from_fixture(
                {"name": name, "message": "never retained", "stack": "never retained"},
                operation_id=OPERATION_ID,
                attempt_id=ATTEMPT_ID,
                candidate_source=FULL_OID,
                stage=stage,
            )
            assert value["error_kind"] == expected_kind
            payload = diagnostic.diagnostic_bytes(value)
            assert b"never retained" not in payload
            assert b"secret" not in payload


def test_specific_constructor_identity_precedes_inherited_generic_name() -> None:
    value = diagnostic.build_diagnostic_from_fixture(
        {
            "constructor_name": "PresetMountError",
            "name": "Error",
            "message": "never retained",
        },
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=FULL_OID,
        stage="agent_create_setup_publish",
    )
    assert value["error_kind"] == "preset_mount_error"
    assert b"never retained" not in diagnostic.diagnostic_bytes(value)


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"stage": "agent setup failed"}, "stage_invalid"),
        ({"cause_coordinate": "service acquisition failed"}, "cause_coordinate_invalid"),
        ({"error_kind": "preset error"}, "error_kind_invalid"),
        ({"candidate_source": "a" * 7}, "candidate_source_invalid"),
        ({"raw_stack_retained": True}, "raw_retention_invalid"),
        (
            {
                "stage": "initial_idle_wait",
                "cause_coordinate": "required_service_missing",
            },
            "service_cause_stage_mismatch",
        ),
        (
            {
                "stage": "agent_create_setup_publish",
                "cause_coordinate": "preset_root_roster_mismatch",
            },
            "roster_cause_stage_mismatch",
        ),
    ],
)
def test_descriptive_or_relationship_drift_fails_closed(overrides, error) -> None:
    with pytest.raises(diagnostic.PostHmrDiagnosticError, match=error):
        diagnostic.validate_diagnostic(_diagnostic(**overrides))


def test_extra_or_missing_keys_fail_closed() -> None:
    extra = _diagnostic(extra="not admitted")
    with pytest.raises(diagnostic.PostHmrDiagnosticError, match="diagnostic_keys_invalid"):
        diagnostic.validate_diagnostic(extra)
    missing = _diagnostic()
    missing.pop("stage")
    with pytest.raises(diagnostic.PostHmrDiagnosticError, match="diagnostic_keys_invalid"):
        diagnostic.validate_diagnostic(missing)


def test_canonical_sidecar_identity_and_containment(tmp_path: Path) -> None:
    root = tmp_path / "attempt"
    root.mkdir()
    path = root / "post-hmr-diagnostic.json"
    value = _diagnostic()
    path.write_bytes(diagnostic.diagnostic_bytes(value))
    assert diagnostic.read_diagnostic(
        path,
        disposable_root=root,
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=FULL_OID,
    ) == value

    path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    with pytest.raises(
        diagnostic.PostHmrDiagnosticError,
        match="diagnostic_canonical_bytes_required",
    ):
        diagnostic.read_diagnostic(
            path,
            disposable_root=root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=FULL_OID,
        )


def test_sidecar_outside_root_and_identity_mismatch_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "attempt"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_bytes(diagnostic.diagnostic_bytes(_diagnostic()))
    with pytest.raises(
        diagnostic.PostHmrDiagnosticError,
        match="diagnostic_path_outside_disposable_root",
    ):
        diagnostic.read_diagnostic(
            outside,
            disposable_root=root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=FULL_OID,
        )

    inside = root / "inside.json"
    inside.write_bytes(diagnostic.diagnostic_bytes(_diagnostic()))
    with pytest.raises(
        diagnostic.PostHmrDiagnosticError,
        match="diagnostic_runtime_identity_mismatch",
    ):
        diagnostic.read_diagnostic(
            inside,
            disposable_root=root,
            operation_id=OPERATION_ID,
            attempt_id="different-attempt",
            candidate_source=FULL_OID,
        )


def test_helper_has_one_safe_writer_and_no_raw_or_execution_surface() -> None:
    payload = diagnostic.build_helper_source(
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=FULL_OID,
    )
    result = diagnostic.validate_helper_source(payload)
    assert all(result["checks"].values())
    source = payload.decode()
    assert ".message" not in source
    assert ".stack" not in source
    assert ".cause" not in source
    assert "process.env" not in source


def test_future_runner_envelope_owns_every_stage_before_exact_operation() -> None:
    payload = diagnostic.future_runner_instrumentation_envelope_source()
    result = diagnostic.validate_future_runner_instrumentation_envelope(payload)
    assert all(result["checks"].values())
    assert list(result["stage_positions"]) == list(diagnostic.PRE_REQUEST_STAGES)
    assert payload.startswith(b"let agent;\nlet sessions;\n")


def test_accepted_runner_and_cached_rc7_sources_are_exact() -> None:
    payload = accepted_runner.runner_source(rehearsal.TARGET_PATH)
    binding = diagnostic.validate_accepted_runner_source(
        payload, expected_sha256=rehearsal.ACCEPTED_RUNNER_SHA256
    )
    assert binding["operation_order_exact"] is True
    sources = rehearsal.source_bindings()
    assert set(sources) == {
        "dsh_agent",
        "dsh_agent_loop",
        "dsh_agent_presets",
        "dsh_session",
    }
    assert all(row["package_version"] == "0.1.0-rc.7" for row in sources.values())


def test_source_binding_rejects_substitution() -> None:
    with pytest.raises(diagnostic.PostHmrDiagnosticError, match="source_sha256_mismatch"):
        diagnostic.validate_source_binding(
            b"substituted",
            expected_sha256="0" * 64,
            required_fragments=(b"substituted",),
        )


def test_generated_evidence_and_schemas_pass() -> None:
    contract = json.loads(rehearsal.CONTRACT_PATH.read_bytes())
    contract_schema = json.loads(
        (rehearsal.EVIDENCE_ROOT / "contract.schema.json").read_bytes()
    )
    evidence_schema = json.loads(
        (rehearsal.EVIDENCE_ROOT / "diagnosis-evidence.schema.json").read_bytes()
    )
    diagnostic_schema = json.loads(
        (
            rehearsal.EVIDENCE_ROOT
            / "post-hmr-pre-request-diagnostic.schema.json"
        ).read_bytes()
    )
    evidence = rehearsal.build_evidence()
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
    valid_diagnostic = _diagnostic()
    jsonschema.Draft202012Validator(diagnostic_schema).validate(valid_diagnostic)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(diagnostic_schema).validate(
            {**valid_diagnostic, "stage": "agent setup failed"}
        )
    assert evidence["result"] == "pass"
    assert evidence["fixture_matrix"]["scenario_count"] == 51
    assert all(
        value == 0
        for key, value in evidence["proof_boundary"].items()
        if key != "python_process_count"
    )


def test_plan_preserves_provider_free_and_no_retry_boundaries() -> None:
    plan = (
        Path("docs")
        / "deepseek-native-harness-provider-free-custom-runner-pre-request-failure-coordinate-diagnosis-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        Path("docs/security")
        / "deepseek-native-harness-provider-free-custom-runner-pre-request-failure-coordinate-diagnosis-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for stage in diagnostic.PRE_REQUEST_STAGES:
        assert f"`{stage}`" in plan
    assert "No occupied retry" in plan
    assert "process counts remain zero" in plan
    assert "LLM invents a plausible stage or state label" in threat
