import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from scripts.raisa_provider_free_check_in_native_harness_preset_validation_subcoordinate_recovery import (
    CANONICAL_PRESET_PATH,
    CONTRACT_PATH,
    CONTINUITY_ROOT,
    NATIVE_EVIDENCE_SCHEMA_PATH,
    NATIVE_MARKERS,
    PACKAGE_RUNNER,
    PRESET_SHA256,
    PresetSubcoordinateError,
    _validate_package_runner,
    build_static_evidence,
    load_contract,
    native_profile_patch,
    native_runner_source,
    run_package_only_characterization,
    validate_native_profile,
    validate_native_runner_source,
    validate_preset,
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_is_closed_and_schema_valid() -> None:
    contract = _json(CONTRACT_PATH)
    schema = _json(CONTINUITY_ROOT / "contract.schema.json")

    jsonschema.validate(contract, schema)
    assert load_contract() == contract
    assert contract["native_processes_before_checkpoint"] == 0
    assert contract["deepseek_requests"] == 0
    assert contract["attempt_006_authorised"] is False


def test_static_source_and_byte_characterization_passes_closed_schema() -> None:
    evidence = build_static_evidence(load_contract())
    schema = _json(CONTINUITY_ROOT / "static-evidence.schema.json")

    jsonschema.validate(evidence, schema)
    assert evidence["result"] == "pass"
    assert evidence["native_process_checkpoint_admitted"] is False
    assert set(evidence["provider_boundary"].values()) == {0}
    assert all(evidence["characterization"]["source_checks"].values())
    assert evidence["characterization"]["preset"]["sha256"] == PRESET_SHA256


@pytest.mark.parametrize(
    "mutation",
    [
        lambda payload: payload[:-1],
        lambda payload: payload.replace(b"false", b"true "),
        lambda payload: b"\xef\xbb\xbf" + payload,
    ],
)
def test_hostile_preset_bytes_fail_closed(mutation) -> None:
    with pytest.raises(PresetSubcoordinateError):
        validate_preset(mutation(CANONICAL_PRESET_PATH.read_bytes()))


def test_package_runner_is_package_only_and_contains_no_harness_agent_path() -> None:
    assert "scanRoot" in PACKAGE_RUNNER
    assert "agents.create" not in PACKAGE_RUNNER
    assert "presets.mount" not in PACKAGE_RUNNER
    assert "model" not in PACKAGE_RUNNER
    assert "provider" not in PACKAGE_RUNNER
    assert "fetch(" not in PACKAGE_RUNNER


def test_package_runner_projection_rejects_a_broken_row() -> None:
    with pytest.raises(
        PresetSubcoordinateError,
        match="package_probe_failed:preset_row_broken",
    ):
        _validate_package_runner(
            {
                "schema_version": "ariadne.check_in_preset_package_runner.v1",
                "result": "failed_closed",
                "coordinate": "preset_row_broken",
            }
        )


def test_package_only_discovery_characterization_passes_closed_schema() -> None:
    evidence = run_package_only_characterization(load_contract())
    schema = _json(CONTINUITY_ROOT / "package-evidence.schema.json")

    jsonschema.validate(evidence, schema)
    assert evidence["result"] == "pass"
    assert evidence["subcoordinates"]["row_discovery"]["broken_absent"] is True
    assert evidence["subcoordinates"]["byte_read_and_parse"][
        "package_parse_shape_admitted"
    ] is True
    assert evidence["subcoordinates"]["digest_and_length_binding"] == {
        "bytes": 158,
        "sha256": PRESET_SHA256,
    }
    assert evidence["process_boundary"]["package_only_node_processes"] == 1
    assert evidence["process_boundary"]["native_harness_processes"] == 0
    assert set(
        value
        for key, value in evidence["process_boundary"].items()
        if key != "package_only_node_processes"
    ) == {0}
    assert set(evidence["cleanup"].values()) == {True}
    assert evidence["native_process_checkpoint_admitted"] is False


def test_schemas_reject_broadened_evidence() -> None:
    static = build_static_evidence(load_contract())
    static["provider_boundary"]["provider_requests"] = 1

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(static, _json(CONTINUITY_ROOT / "static-evidence.schema.json"))


def test_native_runner_stops_after_digest_without_agent_or_mount_path() -> None:
    payload = native_runner_source()
    reading = validate_native_runner_source(payload)
    source = payload.decode("utf-8")

    assert reading["single_preset_list"] is True
    assert reading["no_agents_create"] is True
    assert reading["no_preset_mount"] is True
    assert reading["no_session"] is True
    assert reading["no_turn"] is True
    assert "ctx.get(\"appExit\")(0)" in source
    assert source.index("PRESET_ROW_DISCOVERY_ENTERED") < source.index(
        "PRESET_DIGEST_BOUND_PASSED"
    )


def test_native_profile_injects_only_agent_presets(tmp_path: Path) -> None:
    payload = native_profile_patch(tmp_path.resolve())
    reading = validate_native_profile(payload)
    rows = yaml.safe_load(payload)
    inserted = next(row["insert"] for row in rows if "insert" in row)
    runner = inserted[1]

    assert reading["bytes"] == len(payload)
    assert runner["id"] == "emr4-provider-disabled-preset-validation-probe"
    assert runner["inject"] == ["agentPresets"]
    assert set(runner["config"]) == {"markerPath", "terminalPath", "presetPath"}


def test_native_pass_terminal_schema_is_closed() -> None:
    terminal = {
        "schema_version": "emr4.check-in-preset-validation-native-terminal.v1",
        "operation_id": "raisa-provider-free-check-in-native-harness-preset-validation-subcoordinate-recovery",
        "attempt_id": "check-in-preset-validation-native-probe-001",
        "result": "pass",
        "terminal_coordinate": NATIVE_MARKERS[-1],
        "markers": NATIVE_MARKERS,
        "package": {
            "name": "@deepseek-ai/dsh",
            "version": "0.1.0-rc.7",
            "installation_id": "deepseek-check-in-attachment-observability-native-001",
            "package_lock_sha256": "a" * 64,
        },
        "counts": {
            "native_processes": 1,
            "automatic_retries": 0,
            "agent_sessions": 0,
            "turns": 0,
            "broker_requests": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "network_attempts": 0,
            "docker_invocations": 0,
            "database_invocations": 0,
        },
        "launch": {
            "exit_code": 0,
            "duration_ms": 1,
            "stdout_sha256": "b" * 64,
            "stdout_bytes": 0,
            "stderr_sha256": "c" * 64,
            "stderr_bytes": 0,
            "raw_logs_retained": False,
            "credential_environment_names_removed_count": 1,
        },
        "cleanup": {"process_absent": True, "disposable_root_absent": True},
        "runner_terminal_valid": True,
        "network_ledger_valid": True,
        "claim_boundary": "provider_disabled_native_preset_validation_subcoordinates_only_no_agent_mount_deepseek_database_or_product_claim",
    }
    schema = _json(NATIVE_EVIDENCE_SCHEMA_PATH)

    jsonschema.validate(terminal, schema)
    terminal["counts"]["agent_sessions"] = 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(terminal, schema)
