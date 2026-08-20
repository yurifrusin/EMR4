import json
from pathlib import Path

import jsonschema
import pytest

from scripts.raisa_provider_free_check_in_native_harness_preset_validation_subcoordinate_recovery import (
    CANONICAL_PRESET_PATH,
    CONTRACT_PATH,
    CONTINUITY_ROOT,
    PACKAGE_RUNNER,
    PRESET_SHA256,
    PresetSubcoordinateError,
    _validate_package_runner,
    build_static_evidence,
    load_contract,
    run_package_only_characterization,
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
