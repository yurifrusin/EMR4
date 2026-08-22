from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import native_edit_argument_result_coordinate as coordinate
from scripts import (
    deepseek_native_harness_provider_free_edit_argument_result_coordinate_diagnostic_recovery
    as diagnostic,
)


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict[str, object]:
    return json.loads(diagnostic.CONTRACT_PATH.read_bytes())


def test_contract_and_all_schemas_are_closed_and_valid() -> None:
    contract = diagnostic.validate_contract()
    assert contract == _contract()
    assert contract["coordinates"] == list(coordinate.COORDINATES)
    assert [row["variant_id"] for row in contract["variants"]] == list(
        diagnostic.VARIANT_IDS
    )
    for path in (
        diagnostic.CONTRACT_SCHEMA_PATH,
        diagnostic.COORDINATE_SCHEMA_PATH,
        diagnostic.EVIDENCE_SCHEMA_PATH,
        diagnostic.FAILURE_SCHEMA_PATH,
    ):
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_bytes()))


def test_all_nine_variants_release_the_exact_closed_coordinate() -> None:
    contract = diagnostic.validate_contract()
    released = []
    for row in contract["variants"]:
        success = row["expected_coordinate"].startswith("edit_success_")
        observation = {
            "result_kind": "success" if success else "error",
            "structured_error_code": row["structured_error_code"],
            "success_class": row["success_class"],
            "target_changed": success,
        }
        value = coordinate.classify_observation(observation)
        assert value["coordinate"] == row["expected_coordinate"]
        assert coordinate.validate_coordinate(value) == value
        released.append(value["coordinate"])
    assert set(released) == set(coordinate.COORDINATES)
    assert released.count("edit_error_untyped_argument_constraint") == 3


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("result_kind", "maybe", "result_kind_invalid"),
        ("structured_error_code", "ENOENT", "structured_error_code_invalid"),
        ("success_class", "partial", "success_class_invalid"),
        ("target_changed", "false", "target_changed_invalid"),
    ],
)
def test_unknown_vocabulary_fails_closed(
    field: str, value: object, message: str
) -> None:
    observation: dict[str, object] = {
        "result_kind": "success",
        "structured_error_code": None,
        "success_class": "unique_match",
        "target_changed": True,
    }
    observation[field] = value
    with pytest.raises(coordinate.NativeEditCoordinateError, match=message):
        coordinate.classify_observation(observation)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("result_kind", "error"),
        ("structured_error_code", "FS_EDIT_NOT_FOUND"),
        ("success_class", None),
        ("target_changed", False),
    ],
)
def test_success_error_and_mutation_contradictions_fail_closed(
    field: str, value: object
) -> None:
    observation: dict[str, object] = {
        "result_kind": "success",
        "structured_error_code": None,
        "success_class": "unique_match",
        "target_changed": True,
    }
    observation[field] = value
    with pytest.raises(
        coordinate.NativeEditCoordinateError,
        match="observation_combination_invalid",
    ):
        coordinate.classify_observation(observation)


def test_unknown_key_and_wrong_coordinate_fail_closed() -> None:
    observation: dict[str, object] = {
        "result_kind": "error",
        "structured_error_code": "INVALID_ARGS",
        "success_class": None,
        "target_changed": False,
    }
    unknown = {**observation, "reason": "free form"}
    with pytest.raises(
        coordinate.NativeEditCoordinateError, match="observation_keys_invalid"
    ):
        coordinate.classify_observation(unknown)
    released = coordinate.classify_observation(observation)
    released["coordinate"] = "edit_error_fs_edit_not_found"
    with pytest.raises(
        coordinate.NativeEditCoordinateError, match="coordinate_mismatch"
    ):
        coordinate.validate_coordinate(released)


def test_package_sources_runner_and_consumed_attempts_are_machine_bound() -> None:
    preflight = diagnostic.provider_free_check()
    assert preflight["status"] == "passed"
    assert set(preflight["package_source"]) == {
        "dsh_tools",
        "dsh_tool_fs",
        "dsh_fs",
        "dsh_fs_local",
        "third_party_source_text_retained",
    }
    assert all(preflight["source_checks"].values())
    assert preflight["accepted_future_runner"]["source_commit_resolved"] is True
    assert preflight["accepted_future_runner"]["source_is_ancestor_of_head"] is True
    assert len(preflight["accepted_future_runner"]["source_commit"]) == 40
    assert set(preflight["consumed_attempt_bindings"]) == {
        "attempt_001_preparation",
        "attempt_001_rejection",
        "attempt_002_terminal",
        "attempt_002_consumed",
    }


def test_fixture_source_mounts_real_edit_and_registers_no_synthetic_tool() -> None:
    preflight = diagnostic.provider_free_check()
    source = diagnostic._fixture_source(
        diagnostic.validate_contract()["variants"], preflight["packages_root"]
    ).decode("utf-8")
    assert source.count("new ToolRuntime(ctx)") == 1
    assert source.count("new LocalFileSystem(ctx,") == 1
    assert source.count("applyToolFs(ctx,") == 1
    assert "tools.register(" not in source
    assert "dsh-llm-deepseek" not in source
    assert "api.deepseek" not in source.lower()
    assert "fetch(" not in source


def test_real_rc7_edit_fixture_exercises_every_variant_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "deepseek-edit-argument-coordinate-fixture-001"
    monkeypatch.setattr(diagnostic, "DISPOSABLE_PARENT", tmp_path)
    monkeypatch.setattr(diagnostic, "DISPOSABLE_ROOT", root)
    preflight = diagnostic.provider_free_check()
    rows, fixture = diagnostic.run_node_fixture(
        diagnostic.validate_contract(), preflight["packages_root"]
    )
    assert [row["variant_id"] for row in rows] == list(diagnostic.VARIANT_IDS)
    assert {row["coordinate"] for row in rows} == set(coordinate.COORDINATES)
    assert fixture["actual_dsh_tools_runtime_imported"] is True
    assert fixture["actual_dsh_tool_fs_edit_imported"] is True
    assert fixture["actual_dsh_fs_local_imported"] is True
    assert fixture["synthetic_edit_registration_count"] == 0
    assert fixture["tool_runtime_execution_count"] == 9
    assert fixture["stderr_bytes"] == 0
    assert fixture["cordis_disposed"] is True
    assert fixture["disposable_root_absent"] is True
    assert not root.exists()


def test_persisted_evidence_is_canonical_schema_valid_and_provider_free() -> None:
    evidence = json.loads(diagnostic.EVIDENCE_PATH.read_bytes())
    schema = json.loads(diagnostic.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert diagnostic.EVIDENCE_PATH.read_bytes() == diagnostic.canonical_bytes(evidence)
    assert evidence["fixture"]["tool_runtime_execution_count"] == 9
    assert evidence["fixture"]["synthetic_edit_registration_count"] == 0
    assert evidence["process_counts"] == diagnostic.validate_contract()[
        "process_limits"
    ]
    assert all(
        evidence["process_counts"][key] == 0
        for key in evidence["process_counts"]
        if key != "node_fixture_process_count"
    )
    assert evidence["cleanup"] == {
        "owned_process_absent": True,
        "disposable_root_absent": True,
        "credentials_present_in_fixture_environment": False,
        "raw_arguments_content_error_stack_retained": False,
        "raw_prompt_response_reasoning_session_environment_retained": False,
    }
    forbidden = {"arguments", "content", "message", "stack", "environment"}
    assert not any(forbidden & set(row) for row in evidence["variants"])


def test_success_hashes_change_and_failure_hashes_do_not() -> None:
    evidence = json.loads(diagnostic.EVIDENCE_PATH.read_bytes())
    for row in evidence["variants"]:
        if row["result_kind"] == "success":
            assert row["target_changed"] is True
            assert row["before"] != row["after"]
        else:
            assert row["target_changed"] is False
            assert row["before"] == row["after"]


def test_failure_writer_has_only_closed_coordinates_and_no_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    terminal = tmp_path / "failure-terminal.json"
    disposable = tmp_path / "deepseek-edit-argument-coordinate-fixture-001"
    monkeypatch.setattr(diagnostic, "FAILURE_PATH", terminal)
    monkeypatch.setattr(diagnostic, "DISPOSABLE_ROOT", disposable)
    value = diagnostic.write_failure_terminal("free_form_failure")
    assert value["failure_coordinate"] == "unexpected_provider_free_failure"
    assert value["retry_count"] == 0
    assert value["resume_count"] == 0
    assert value["fallback_count"] == 0
    jsonschema.Draft202012Validator(
        json.loads(diagnostic.FAILURE_SCHEMA_PATH.read_bytes())
    ).validate(json.loads(terminal.read_bytes()))


def test_mutated_contract_variant_and_consumed_binding_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = copy.deepcopy(_contract())
    contract["variants"][0]["expected_coordinate"] = "edit_error_invalid_args"
    path = tmp_path / "contract.json"
    path.write_bytes(diagnostic.canonical_bytes(contract))
    with pytest.raises(diagnostic.EditArgumentDiagnosticError, match="contract_rejected"):
        diagnostic.validate_contract(path)

    valid = diagnostic.validate_contract()
    changed = copy.deepcopy(valid)
    changed["consumed_attempt_bindings"]["attempt_002_terminal"]["sha256"] = "0" * 64
    with pytest.raises(
        diagnostic.EditArgumentDiagnosticError, match="consumed_attempt_drift"
    ):
        diagnostic.validate_accepted_runner_and_attempts(changed)
