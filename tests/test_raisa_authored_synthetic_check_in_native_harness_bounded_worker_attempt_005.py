from __future__ import annotations

import inspect
import json

from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_004
    as accepted_attempt,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_005
    as subject,
)


def test_attempt_five_identity_and_paths_are_exact_and_isolated() -> None:
    value = subject.attempt_configuration()
    assert value["operation_id"] == (
        "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-005"
    )
    assert value["attempt_id"] == "deepseek-native-synthetic-window-worker-005"
    assert value["work_order_id"] == "wo-synthetic-native-window-worker-005"
    assert value["lease_id"] == "lease-synthetic-native-window-worker-005"
    assert value["attempt_root"].as_posix().endswith(
        "/EMR4-worktrees/deepseek-native-synthetic-window-worker-005"
    )
    bound_paths = [value[name.lower()] for name in subject.PATH_BINDINGS]
    assert all(path.parent == subject.EVIDENCE_ROOT for path in bound_paths)
    assert subject.EVIDENCE_ROOT.name == "attempt-005"


def test_attempt_five_binding_restores_the_accepted_attempt_controller() -> None:
    original = {
        "operation": accepted_attempt.OPERATION_ID,
        "attempt": accepted_attempt.ATTEMPT_ID,
        "root": accepted_attempt.ATTEMPT_ROOT,
        "paths": accepted_attempt.PATH_BINDINGS,
    }
    with subject.configured_accepted_attempt():
        assert accepted_attempt.OPERATION_ID == subject.OPERATION_ID
        assert accepted_attempt.ATTEMPT_ID == subject.ATTEMPT_ID
        assert accepted_attempt.ATTEMPT_ROOT == subject.ATTEMPT_ROOT
        assert accepted_attempt.PATH_BINDINGS == subject.PATH_BINDINGS
    assert accepted_attempt.OPERATION_ID == original["operation"]
    assert accepted_attempt.ATTEMPT_ID == original["attempt"]
    assert accepted_attempt.ATTEMPT_ROOT == original["root"]
    assert accepted_attempt.PATH_BINDINGS == original["paths"]


def test_attempt_five_terminal_schema_is_closed_and_one_call_bounded() -> None:
    schema = json.loads(subject.TERMINAL_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["operation_id"]["const"] == subject.OPERATION_ID
    assert schema["properties"]["attempt_id"]["const"] == subject.ATTEMPT_ID
    assert schema["properties"]["broker"]["properties"]["provider_call_started"][
        "maximum"
    ] == 1
    assert schema["properties"]["automatic_retry_count"]["const"] == 0
    assert schema["properties"]["fallback_count"]["const"] == 0


def test_attempt_five_adapter_adds_no_launcher_retry_or_fallback() -> None:
    source = inspect.getsource(subject)
    accepted_source = inspect.getsource(accepted_attempt._execute_configured_native)
    assert "subprocess.Popen" not in source
    assert "while True" not in source
    assert accepted_source.count("harness = subprocess.Popen(") == 1
    assert accepted_source.count("converged_controller.build_launch_binding(") == 1
    assert '"automatic_retry_count": 0' in accepted_source
    assert '"fallback_count": 0' in accepted_source


def test_attempt_five_accepted_controller_terminalizes_before_cleanup() -> None:
    source = inspect.getsource(accepted_attempt._execute_configured_native)
    launch = source.index("harness = subprocess.Popen(")
    selection = source.index("converged_controller.select_pre_hmr_terminal(")
    terminal = source.index("converged_controller.write_selected_terminal_exclusive(")
    cleanup = source.index("accepted_controller.remove_exact_attempt_root(root, parent)")
    outer = source.index(
        "accepted_controller.write_json_exclusive(accepted_controller.TERMINAL_PATH"
    )
    assert launch < selection < terminal < cleanup < outer


def test_attempt_five_provider_free_check_reports_zero_activity() -> None:
    value = subject.provider_free_check()
    assert value == {
        "schema_version": "ariadne.synthetic_native_worker_attempt_005_check.v1",
        "operation_id": subject.OPERATION_ID,
        "result": "pass",
        "attempt_id": subject.ATTEMPT_ID,
        "work_order_id": subject.WORK_ORDER_ID,
        "lease_id": subject.LEASE_ID,
        "attempt_root": subject.ATTEMPT_ROOT.resolve().as_posix(),
        "structured_diagnostic_lifecycle": value[
            "structured_diagnostic_lifecycle"
        ],
        "native_process_count": 0,
        "provider_request_count": 0,
    }
    assert all(value["structured_diagnostic_lifecycle"]["checks"].values())


def test_attempt_five_plan_preserves_the_one_shot_and_closed_product_boundary() -> None:
    plan = (
        subject.REPO_ROOT
        / "docs"
        / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-005-plan.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "exactly one fresh attempt-005 Node/native-Harness process",
        "at most one DeepSeek request",
        "no retry, resume, fallback, auxiliary model or second worker",
        "no product, patient",
        "explicit-path staging only",
    ):
        assert phrase in plan
