from __future__ import annotations

import inspect
import json

from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_004
    as subject,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_controller,
)


def test_attempt_four_identity_and_paths_are_exact_and_isolated() -> None:
    value = subject.attempt_configuration()
    assert value["operation_id"] == (
        "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-004"
    )
    assert value["attempt_id"] == "deepseek-native-synthetic-window-worker-004"
    assert value["work_order_id"] == "wo-synthetic-native-window-worker-004"
    assert value["lease_id"] == "lease-synthetic-native-window-worker-004"
    assert value["attempt_root"].as_posix().endswith(
        "/EMR4-worktrees/deepseek-native-synthetic-window-worker-004"
    )
    bound_paths = [
        value[name.lower()] for name in subject.PATH_BINDINGS
    ]
    assert all(path.parent == subject.EVIDENCE_ROOT for path in bound_paths)
    assert subject.EVIDENCE_ROOT.name == "attempt-004"


def test_attempt_four_temporary_binding_restores_consumed_base_controller() -> None:
    original = {
        "operation": accepted_controller.EXECUTION_OPERATION_ID,
        "attempt": accepted_controller.ATTEMPT_ID,
        "root": accepted_controller.ATTEMPT_ROOT,
    }
    with subject.configured_accepted_controller():
        assert accepted_controller.EXECUTION_OPERATION_ID == subject.OPERATION_ID
        assert accepted_controller.ATTEMPT_ID == subject.ATTEMPT_ID
        assert accepted_controller.ATTEMPT_ROOT == subject.ATTEMPT_ROOT
    assert accepted_controller.EXECUTION_OPERATION_ID == original["operation"]
    assert accepted_controller.ATTEMPT_ID == original["attempt"]
    assert accepted_controller.ATTEMPT_ROOT == original["root"]


def test_attempt_four_terminal_schema_is_closed_and_one_call_bounded() -> None:
    schema = json.loads(subject.TERMINAL_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["operation_id"]["const"] == subject.OPERATION_ID
    assert schema["properties"]["attempt_id"]["const"] == subject.ATTEMPT_ID
    assert schema["properties"]["broker"]["properties"]["provider_call_started"][
        "maximum"
    ] == 1
    assert schema["properties"]["automatic_retry_count"]["const"] == 0
    assert schema["properties"]["fallback_count"]["const"] == 0


def test_attempt_four_uses_converged_wrapper_and_terminal_before_cleanup() -> None:
    source = inspect.getsource(subject._execute_configured_native)
    binding = source.index("converged_controller.build_launch_binding(")
    launch = source.index("harness = subprocess.Popen(")
    selection = source.index("converged_controller.select_pre_hmr_terminal(")
    terminal = source.index("converged_controller.write_selected_terminal_exclusive(")
    cleanup = source.index("accepted_controller.remove_exact_attempt_root(root, parent)")
    outer_terminal = source.index(
        "accepted_controller.write_json_exclusive(accepted_controller.TERMINAL_PATH"
    )
    assert binding < launch < selection < terminal < cleanup < outer_terminal
    assert source.count("harness = subprocess.Popen(") == 1
    assert source.count("converged_controller.build_launch_binding(") == 1
    assert source.count("converged_controller.write_selected_terminal_exclusive(") == 1


def test_attempt_four_consumes_before_launch_and_has_no_retry_loop() -> None:
    source = inspect.getsource(subject._execute_configured_native)
    consumed = source.index("accepted_controller.write_json_exclusive(")
    launch = source.index("harness = subprocess.Popen(")
    assert consumed < launch
    assert "while True" not in source
    assert source.count("harness = subprocess.Popen(") == 1
    assert '"automatic_retry_count": 0' in source
    assert '"resume_permitted": False' in source
    assert '"fallback_count": 0' in source


def test_attempt_four_provider_free_check_reports_zero_processes_and_requests() -> None:
    value = subject.provider_free_check()
    assert value["result"] == "pass"
    assert value["native_process_count"] == 0
    assert value["provider_request_count"] == 0
    assert all(value["structured_diagnostic_lifecycle"]["checks"].values())
