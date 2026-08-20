from __future__ import annotations

import inspect
import json
from pathlib import Path
import subprocess
import sys

import jsonschema
import pytest

from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as subject,
)


def test_contract_binds_one_request_exact_tools_and_full_planning_source() -> None:
    contract = subject.load_contract()
    assert contract["planning_source"] == subject.git(
        "log",
        "-1",
        "--format=%H",
        "--",
        subject.PLAN_PATH.relative_to(subject.REPO_ROOT).as_posix(),
    )
    assert subject.FULL_OID.fullmatch(contract["planning_source"])
    assert contract["allowed_tool_names"] == ["edit", "glob", "read"]
    assert contract["maximum_parallel_tool_calls"] == 1
    assert contract["maximum_provider_calls"] == 1
    assert contract["automatic_retries"] == 0
    assert contract["fallbacks"] == 0
    assert contract["auxiliary_model_calls"] == 0


def test_predecessor_bindings_are_exact() -> None:
    bound = subject.bind_predecessors(subject.load_contract())
    assert len(bound) == 5
    assert {row["role"] for row in bound} == {
        "frozen_plan",
        "frozen_threat_delta",
        "accepted_preset_mount_projection_controller",
        "accepted_effective_tool_guard_controller",
        "native_harness_broker",
    }


def test_work_package_has_one_exact_edit_success_shape(tmp_path: Path) -> None:
    target = tmp_path / subject.SYNTHETIC_PATH
    target.write_text(subject.EXPECTED_SOURCE, encoding="utf-8", newline="\n")
    completed = subprocess.run(
        [sys.executable, str(target)],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert completed.returncode == 0
    assert subject.BASELINE_SOURCE.count("current[1] = end") == 1
    assert subject.EXPECTED_SOURCE.count("current[1] = max(current[1], end)") == 1
    assert '"nested": ([(0, 10), (2, 3)], [(0, 10)])' in subject.EXPECTED_SOURCE
    assert subject.EXPECTED_SOURCE.count('"nested":') == 1


def test_tool_batch_fixture_matrix_is_fail_closed() -> None:
    matrix = subject.fixture_matrix()
    assert len(matrix) == 9
    assert matrix[0] == {
        "scenario": "success",
        "coordinate": subject.SUCCESS_COORDINATE,
    }
    assert {row["coordinate"] for row in matrix[1:]} == set(
        subject.FAILURE_COORDINATES
    )


def test_pinned_source_proves_in_process_turn_conclusion() -> None:
    proof = subject.source_semantics()
    assert all(proof["checks"].values())
    assert proof["checks"]["official_edit_is_atomic"]
    assert proof["checks"]["runtime_has_conclusion_method"]
    assert proof["checks"]["loop_stops_after_concluded_result"]
    assert proof["checks"]["broker_has_optional_one_request_allowance"]


def test_runner_marks_only_one_successful_exact_edit_terminal() -> None:
    target = "C:/synthetic-native-worker/synthetic_window_coalescer.py"
    source = subject.runner_source(target)
    proof = subject.validate_runner_source(source)
    assert all(value is True for key, value in proof.items() if key not in {"sha256", "bytes"})
    text = source.decode("utf-8")
    assert "observedCalls === 1" in text
    assert "exec.parent === undefined" in text
    assert "args.file_path === TARGET_PATH" in text
    assert "result.isError === false" in text
    assert 'decision.kind === "accept"' in text
    assert text.index("const decision = await next()") < text.index("exec.concludeTurn()")


def test_task_supplies_context_and_forbids_inspection_turn() -> None:
    prompt = subject.task_text("C:/synthetic/native.py")
    assert subject.BASELINE_SOURCE in prompt
    assert "exactly one model-requested tool call" in prompt
    assert "Do not call read or glob" in prompt
    assert "do not provide a later summary" in prompt
    assert "patient" not in prompt.lower()
    assert "appointment" not in prompt.lower()


def test_deterministic_evidence_has_zero_occupied_counts() -> None:
    value = subject.deterministic_evidence()
    assert value["result"] == "pass"
    assert len(value["fixture_matrix"]) == 9
    assert all(count == 0 for count in value["boundary"].values())
    assert value["work_package"]["public_case_count"] == 4
    assert value["work_package"]["holdback_case_count"] == 3


def test_evidence_schema_rejects_provider_or_unknown_field() -> None:
    value = subject.deterministic_evidence()
    schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    value["boundary"]["provider_request_count"] = 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(value)
    value = subject.deterministic_evidence()
    value["unexpected"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(value)


def test_occupied_cli_is_structurally_behind_separate_checkpoint() -> None:
    source = inspect.getsource(subject.main)
    assert 'action.add_argument("--check"' in source
    assert 'action.add_argument("--build"' in source
    assert 'action.add_argument("--prepare-attempt"' in source
    assert 'action.add_argument("--native"' in source
    native = inspect.getsource(subject.execute_native)
    assert native.index("checkpoint = load_checkpoint()") < native.index(
        "write_json_exclusive(CONSUMED_PATH"
    )
    assert native.index("checkpoint = load_checkpoint()") < native.index(
        "subprocess.Popen("
    )


def test_profile_candidate_is_exact_no_retry_and_one_parallel_tool() -> None:
    root = Path("C:/synthetic-native-worker")
    initial = subject.validate_profile_patch(
        subject.profile_patch(root, 43123, changed=False), changed=False
    )
    changed = subject.validate_profile_patch(
        subject.profile_patch(root, 43123, changed=True), changed=True
    )
    assert initial["runner_presence_exact"]
    assert changed["runner_presence_exact"]
    assert initial["retry_plugin_disabled"]
    assert initial["retry_count_zero"]
    assert initial["parallel_width_one"]
    assert initial["derived_user_root_enabled"]


def test_worker_environment_cannot_receive_provider_credential(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "must-not-propagate")
    environment = subject._worker_environment(tmp_path, 43123, "synthetic-token")
    assert "DEEPSEEK_API_KEY" not in environment
    assert environment["DSH_EMR4_BROKER_TOKEN"] == "synthetic-token"
    assert environment["DSH_TELEMETRY_DISABLED"] == "1"


def test_occupied_terminal_schema_rejects_second_provider_request() -> None:
    schema = json.loads(subject.TERMINAL_SCHEMA_PATH.read_text(encoding="utf-8"))
    broker = schema["properties"]["broker"]
    assert broker["properties"]["provider_call_started"]["maximum"] == 1
    assert schema["properties"]["automatic_retry_count"]["const"] == 0
    assert schema["properties"]["fallback_count"]["const"] == 0
    assert schema["properties"]["auxiliary_model_call_count"]["const"] == 0
