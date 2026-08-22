from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import native_tool_result_conclusion_coordinate as coordinate
from scripts import (
    deepseek_native_harness_provider_free_tool_result_conclusion_coordinate_diagnostic_recovery as diagnostic,
)


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict[str, object]:
    return json.loads(diagnostic.CONTRACT_PATH.read_bytes())


def _accepted_and_derived() -> tuple[bytes, bytes]:
    contract = diagnostic.validate_contract()
    runner = contract["accepted_runner"]
    accepted = diagnostic.accepted_worker.runner_source(runner["fixture_target"])
    derived = diagnostic.derive_future_runner_source(
        accepted,
        target_path=runner["fixture_target"],
        expected_sha256=runner["sha256"],
    )
    return accepted, derived


def test_contract_and_all_schemas_are_closed_and_valid() -> None:
    contract = diagnostic.validate_contract()
    assert contract == _contract()
    assert contract["coordinates"] == list(coordinate.COORDINATES)
    assert len(contract["variants"]) == 5
    for path in (
        diagnostic.CONTRACT_SCHEMA_PATH,
        diagnostic.COORDINATE_SCHEMA_PATH,
        diagnostic.EVIDENCE_SCHEMA_PATH,
        diagnostic.FAILURE_SCHEMA_PATH,
    ):
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_bytes()))


def test_all_five_observations_release_one_exact_unique_coordinate() -> None:
    contract = diagnostic.validate_contract()
    released = []
    for row in contract["variants"]:
        value = coordinate.classify_observation(row["observation"])
        assert value["coordinate"] == row["coordinate"]
        assert coordinate.validate_coordinate(value) == value
        released.append(value["coordinate"])
    assert tuple(released) == coordinate.COORDINATES
    assert len(set(released)) == 5


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("input_result_kind", "timeout"),
        ("post_execute_decision_kind", "permit"),
        ("conclusion_request_stage", "eventually"),
        ("authoritative_final_result_kind", "maybe"),
        ("turn_kind", "stopped"),
    ],
)
def test_unknown_vocabulary_fails_closed(field: str, value: str) -> None:
    observation = copy.deepcopy(_contract()["variants"][0]["observation"])
    observation[field] = value
    with pytest.raises(
        coordinate.ToolResultConclusionCoordinateError,
        match=f"{field}_invalid",
    ):
        coordinate.classify_observation(observation)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authoritative_final_result_kind", "success_concluding"),
        ("turn_kind", "completed"),
        ("post_execute_decision_kind", "block"),
    ],
)
def test_contradictory_or_mislabeled_success_states_fail_closed(
    field: str, value: str
) -> None:
    observation = copy.deepcopy(_contract()["variants"][1]["observation"])
    observation[field] = value
    with pytest.raises(
        coordinate.ToolResultConclusionCoordinateError,
        match="observation_combination_unadmitted",
    ):
        coordinate.classify_observation(observation)


def test_unknown_key_wrong_coordinate_error_conclusion_and_block_success_fail_closed() -> (
    None
):
    contract = _contract()
    unknown = copy.deepcopy(contract["variants"][0]["observation"])
    unknown["explanation"] = "free form"
    with pytest.raises(
        coordinate.ToolResultConclusionCoordinateError,
        match="observation_keys_invalid",
    ):
        coordinate.classify_observation(unknown)

    wrong_coordinate = coordinate.classify_observation(
        contract["variants"][0]["observation"]
    )
    wrong_coordinate["coordinate"] = "edit_success_accept_late_marker"
    with pytest.raises(
        coordinate.ToolResultConclusionCoordinateError,
        match="coordinate_mismatch",
    ):
        coordinate.validate_coordinate(wrong_coordinate)

    for index, field, value in (
        (2, "authoritative_final_result_kind", "success_concluding"),
        (3, "authoritative_final_result_kind", "success_concluding"),
    ):
        observation = copy.deepcopy(contract["variants"][index]["observation"])
        observation[field] = value
        with pytest.raises(
            coordinate.ToolResultConclusionCoordinateError,
            match="observation_combination_unadmitted",
        ):
            coordinate.classify_observation(observation)


def test_package_source_and_full_git_object_are_machine_resolved() -> None:
    preflight = diagnostic.provider_free_check()
    assert preflight["status"] == "passed"
    assert preflight["package"]["name"] == "@deepseek-ai/dsh-tools"
    assert preflight["package"]["version"] == "0.1.0-rc.7"
    assert all(preflight["package"]["lifecycle_checks"].values())
    assert preflight["accepted_runner"]["source_commit_resolved"] is True
    assert preflight["accepted_runner"]["source_is_ancestor_of_head"] is True
    assert len(preflight["accepted_runner"]["source_commit"]) == 40
    assert preflight["native_harness_process_count"] == 0
    assert preflight["provider_request_count"] == 0


def test_future_runner_is_exactly_derived_and_moves_the_marker_before_dispatch() -> (
    None
):
    accepted, derived = _accepted_and_derived()
    contract = diagnostic.validate_contract()
    runner = contract["accepted_runner"]
    reading = diagnostic.validate_future_runner_source(
        derived,
        accepted_payload=accepted,
        target_path=runner["fixture_target"],
        expected_accepted_sha256=runner["sha256"],
    )
    assert all(reading["checks"].values())
    assert diagnostic.DERIVED_RUNNER_PATH.read_bytes() == derived
    source = derived.decode("utf-8")
    pre = source[
        source.index('agentCtx.on("tools/pre-execute"') : source.index(
            'agentCtx.on("tools/post-execute"'
        )
    ]
    post = source[
        source.index('agentCtx.on("tools/post-execute"') : source.index(
            'agentCtx.on("tools/result"'
        )
    ]
    assert pre.count("exec.concludeTurn()") == 1
    assert pre.index("exec.concludeTurn()") < pre.index("return next();")
    assert "exec.concludeTurn()" not in post
    assert "result.concludesTurn === true" in source


def test_real_rc7_tool_runtime_fixture_exercises_all_variants_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    accepted, derived = _accepted_and_derived()
    del accepted
    root = tmp_path / "deepseek-tool-result-coordinate-fixture-001"
    monkeypatch.setattr(diagnostic, "DISPOSABLE_PARENT", tmp_path)
    monkeypatch.setattr(diagnostic, "DISPOSABLE_ROOT", root)
    rows, fixture = diagnostic.run_node_fixture(diagnostic.validate_contract(), derived)
    assert [row["coordinate"] for row in rows] == list(coordinate.COORDINATES)
    assert fixture["node_fixture_process_count"] == 1
    assert fixture["actual_dsh_tools_runtime_imported"] is True
    assert fixture["tool_runtime_execution_count"] == 5
    assert fixture["exit_code"] == 0
    assert fixture["stderr_bytes"] == 0
    assert fixture["disposable_root_absent"] is True
    assert not root.exists()


def test_persisted_evidence_is_canonical_schema_valid_and_provider_free() -> None:
    evidence = json.loads(diagnostic.EVIDENCE_PATH.read_bytes())
    schema = json.loads(diagnostic.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert diagnostic.EVIDENCE_PATH.read_bytes() == diagnostic.canonical_bytes(evidence)
    assert evidence["fixture"]["actual_dsh_tools_runtime_imported"] is True
    assert evidence["fixture"]["tool_runtime_execution_count"] == 5
    assert (
        evidence["process_counts"] == diagnostic.validate_contract()["process_limits"]
    )
    assert all(
        evidence["process_counts"][key] == 0
        for key in evidence["process_counts"]
        if key != "node_fixture_process_count"
    )
    assert evidence["cleanup"] == {
        "owned_process_absent": True,
        "disposable_root_absent": True,
        "raw_argument_content_value_error_retained": False,
        "raw_prompt_response_reasoning_session_environment_retained": False,
    }


def test_historical_terminal_is_byte_immutable() -> None:
    contract = diagnostic.validate_contract()
    terminal = ROOT / contract["historical_terminal"]["path"]
    assert diagnostic.sha256_file(terminal) == contract["historical_terminal"]["sha256"]
    assert (
        contract["historical_terminal"]["classification"]
        == "immutable_unresolved_observation"
    )


def test_rejected_fixture_terminal_and_failure_schema_are_closed() -> None:
    path = (
        diagnostic.OPERATION_ROOT / "attempt-001-fixture-output-rejected-terminal.json"
    )
    value = json.loads(path.read_bytes())
    schema = json.loads(diagnostic.FAILURE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(value)
    assert value["failure_coordinate"] == "fixture_output_rejected"
    assert value["disposable_root_absent"] is True
    assert value["provider_request_count"] == 0
    assert value["raw_sensitive_material_retained"] is False
    assert not diagnostic.FAILURE_PATH.exists()


def test_failure_writer_has_only_closed_coordinates_and_no_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    terminal = tmp_path / "failure-terminal.json"
    disposable = tmp_path / "deepseek-tool-result-coordinate-fixture-001"
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
