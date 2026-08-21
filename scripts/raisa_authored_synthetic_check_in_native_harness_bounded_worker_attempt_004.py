"""One-shot attempt-004 runner using the converged structured diagnostic gear."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import queue
import secrets
import subprocess
import threading
import time
from typing import Any, Iterator

import jsonschema

from orchestration_harness import (
    bounded_worker_structured_diagnostic_controller as converged_controller,
)
from orchestration_harness import native_startup_terminal as startup_terminal
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_controller,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-004"
)
ATTEMPT_ID = "deepseek-native-synthetic-window-worker-004"
WORK_ORDER_ID = "wo-synthetic-native-window-worker-004"
LEASE_ID = "lease-synthetic-native-window-worker-004"
EVIDENCE_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "monitored-development-rehearsal"
    / "attempt-004"
)
ATTEMPT_ROOT = Path(f"C:/Users/sarashera/EMR4-worktrees/{ATTEMPT_ID}")
TERMINAL_SCHEMA_PATH = EVIDENCE_ROOT / "occupied-terminal.schema.json"

PATH_BINDINGS = {
    "CHECKPOINT_PATH": EVIDENCE_ROOT / "occupied-preexecution-checkpoint.json",
    "PREPARATION_PATH": EVIDENCE_ROOT / "occupied-attempt-preparation.json",
    "WORK_ORDER_PATH": EVIDENCE_ROOT / "work-order-v2.json",
    "AUTHORITY_PATH": EVIDENCE_ROOT / "worker-authority.json",
    "FORBIDDEN_PATH": EVIDENCE_ROOT / "forbidden-surfaces.json",
    "COMMAND_MANIFEST_PATH": EVIDENCE_ROOT / "command-manifest.json",
    "NO_DATABASE_ADMISSION_PATH": (
        EVIDENCE_ROOT / "provider-free-no-database-admission.json"
    ),
    "CONSUMED_PATH": EVIDENCE_ROOT / "occupied-attempt-consumed.json",
    "TERMINAL_PATH": EVIDENCE_ROOT / "occupied-terminal.json",
    "TERMINAL_SCHEMA_PATH": TERMINAL_SCHEMA_PATH,
    "NATIVE_REPORT_PATH": EVIDENCE_ROOT / "occupied-report.md",
    "PRE_HMR_TERMINAL_PATH": EVIDENCE_ROOT / "pre-hmr-startup-terminal.json",
}


def attempt_configuration() -> dict[str, Any]:
    return {
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "work_order_id": WORK_ORDER_ID,
        "lease_id": LEASE_ID,
        "attempt_root": ATTEMPT_ROOT,
        "evidence_root": EVIDENCE_ROOT,
        **{name.lower(): path for name, path in PATH_BINDINGS.items()},
    }


@contextmanager
def configured_accepted_controller() -> Iterator[None]:
    """Temporarily bind the accepted base lifecycle to the fresh identity."""

    bindings: dict[str, Any] = {
        "EXECUTION_OPERATION_ID": OPERATION_ID,
        "ATTEMPT_ROOT": ATTEMPT_ROOT,
        "ATTEMPT_ID": ATTEMPT_ID,
        "WORK_ORDER_ID": WORK_ORDER_ID,
        "LEASE_ID": LEASE_ID,
        **PATH_BINDINGS,
    }
    prior = {name: getattr(accepted_controller, name) for name in bindings}
    for name, value in bindings.items():
        setattr(accepted_controller, name, value)
    try:
        yield
    finally:
        for name, value in prior.items():
            setattr(accepted_controller, name, value)


def provider_free_check() -> dict[str, Any]:
    schema = accepted_controller.load_json(TERMINAL_SCHEMA_PATH)
    if (
        schema.get("additionalProperties") is not False
        or schema.get("properties", {}).get("operation_id", {}).get("const")
        != OPERATION_ID
        or schema.get("properties", {}).get("attempt_id", {}).get("const")
        != ATTEMPT_ID
    ):
        raise accepted_controller.RehearsalError("attempt_004_terminal_schema_invalid")
    lifecycle = converged_controller.validate_lifecycle_envelope(
        converged_controller.lifecycle_envelope_source()
    )
    if not all(lifecycle["checks"].values()):
        raise accepted_controller.RehearsalError(
            "structured_diagnostic_lifecycle_invalid"
        )
    with configured_accepted_controller():
        accepted_controller.deterministic_evidence()
        accepted_controller.validate_authority_boundary()
    return {
        "schema_version": "ariadne.synthetic_native_worker_attempt_004_check.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "attempt_id": ATTEMPT_ID,
        "work_order_id": WORK_ORDER_ID,
        "lease_id": LEASE_ID,
        "attempt_root": ATTEMPT_ROOT.resolve().as_posix(),
        "structured_diagnostic_lifecycle": lifecycle,
        "native_process_count": 0,
        "provider_request_count": 0,
    }


def prepare_attempt(review_receipt_path: Path) -> dict[str, Any]:
    with configured_accepted_controller():
        return accepted_controller.prepare_attempt(review_receipt_path)


def execute_native() -> dict[str, Any]:
    """Consume exactly one prepared identity and retain a bounded terminal."""

    with configured_accepted_controller():
        return _execute_configured_native()


def _execute_configured_native() -> dict[str, Any]:
    checkpoint = accepted_controller.load_checkpoint()
    accepted_controller.validate_authority_boundary()
    if any(
        path.exists()
        for path in (
            accepted_controller.CONSUMED_PATH,
            accepted_controller.TERMINAL_PATH,
            accepted_controller.PRE_HMR_TERMINAL_PATH,
        )
    ):
        raise accepted_controller.RehearsalError("occupied_attempt_already_consumed")
    root = ATTEMPT_ROOT.resolve()
    parent = Path("C:/Users/sarashera/EMR4-worktrees").resolve()
    if root.parent != parent or not root.is_dir() or root.is_symlink():
        raise accepted_controller.RehearsalError("prepared_attempt_root_invalid")
    preparation = accepted_controller.load_json(accepted_controller.PREPARATION_PATH)
    if preparation.get("candidate_source") != checkpoint["candidate_source"]:
        raise accepted_controller.RehearsalError("prepared_candidate_mismatch")
    work_order = accepted_controller.load_json(accepted_controller.WORK_ORDER_PATH)
    if work_order.get("source_commit") != checkpoint["candidate_source"]:
        raise accepted_controller.RehearsalError("work_order_candidate_mismatch")
    consumed = {
        "schema_version": "ariadne.synthetic_native_worker_consumed.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "state": "consumed",
        "candidate_source": checkpoint["candidate_source"],
        "automatic_retry_count": 0,
        "resume_permitted": False,
    }
    accepted_controller.write_json_exclusive(
        accepted_controller.CONSUMED_PATH, consumed
    )

    broker: subprocess.Popen[str] | None = None
    harness: subprocess.Popen[bytes] | None = None
    broker_lines: list[str] = []
    broker_queue: queue.Queue[str] = queue.Queue()
    broker_thread: threading.Thread | None = None
    failure: str | None = None
    broker_ready: dict[str, Any] = {}
    runner: dict[str, Any] = {}
    hmr_names: list[str] = []
    harness_exit: int | None = None
    native_started = False
    native_launch_attempted = False
    controller_coordinate: str | None = None
    selected_pre_hmr_terminal: dict[str, Any] | None = None
    pre_hmr_terminal_sha256: str | None = None
    hmr_observation_valid = True
    start = time.monotonic()
    raw_readings: dict[str, Any] = {}
    runtime_profiles: dict[str, str] = {}
    workspace = root / "workspace"
    target = workspace / accepted_controller.SYNTHETIC_PATH
    stdout_path = root / "harness-stdout.raw"
    stderr_path = root / "harness-stderr.raw"
    broker_stderr_path = root / "broker-stderr.raw"
    runner_terminal_path = root / "runner-terminal.json"
    event_path = root / "hmr-events.jsonl"
    binding: dict[str, Any] = {}
    stream_readings: dict[str, dict[str, Any]] = {}
    try:
        token = secrets.token_urlsafe(48)
        with broker_stderr_path.open("wb") as broker_stderr:
            broker = subprocess.Popen(
                ["node", str(accepted_controller.BROKER_PATH)],
                cwd=REPO_ROOT,
                env=accepted_controller._broker_environment(token),
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=broker_stderr,
            )
            if broker.stdout is None:
                raise accepted_controller.RehearsalError("broker_stdout_missing")
            broker_thread = threading.Thread(
                target=accepted_controller._collect_lines,
                args=(broker.stdout, broker_queue, broker_lines),
                daemon=True,
            )
            broker_thread.start()
            broker_ready = accepted_controller._wait_json_line(broker_queue, 15)
            if (
                broker_ready.get("event") != "broker-ready"
                or broker_ready.get("allowed_tool_names")
                != accepted_controller.EXPECTED_TOOLS
                or broker_ready.get("maximum_provider_calls") != 1
                or broker_ready.get("model_id") != "deepseek-v4-flash"
            ):
                raise accepted_controller.RehearsalError(
                    "broker_ready_contract_mismatch"
                )
            port = broker_ready.get("listen_port")
            if not isinstance(port, int) or not 1 <= port <= 65535:
                raise accepted_controller.RehearsalError("broker_port_invalid")
            profile_path = root / "home" / "profiles" / "headless" / "cordis.patch.yml"
            initial = accepted_controller.profile_patch(root, port, changed=False)
            changed = accepted_controller.profile_patch(root, port, changed=True)
            accepted_controller.validate_profile_patch(initial, changed=False)
            accepted_controller.validate_profile_patch(changed, changed=True)
            profile_path.write_bytes(initial)
            package_root = (
                root / "installation" / "node_modules" / "@deepseek-ai" / "dsh"
            )
            binding = converged_controller.build_launch_binding(
                disposable_root=root,
                package_root=package_root,
                operation_id=OPERATION_ID,
                attempt_id=ATTEMPT_ID,
                candidate_source=checkpoint["candidate_source"],
                target_path=target.resolve().as_posix(),
                node_executable="node",
            )
            authority = accepted_controller.load_json(accepted_controller.AUTHORITY_PATH)
            if binding["task_sha256"] != authority.get("prompt_sha256"):
                raise accepted_controller.RehearsalError("launch_task_digest_mismatch")
            runtime_profiles = {
                "initial_sha256": accepted_controller.sha256_bytes(initial),
                "changed_sha256": accepted_controller.sha256_bytes(changed),
                "wrapper_sha256": binding["wrapper_sha256"],
            }
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                native_launch_attempted = True
                try:
                    harness = subprocess.Popen(
                        binding["command"],
                        cwd=workspace,
                        env=accepted_controller._worker_environment(root, port, token),
                        stdout=stdout,
                        stderr=stderr,
                    )
                except OSError as error:
                    controller_coordinate = "native_process_creation_failed"
                    raise accepted_controller.RehearsalError(
                        "native_process_creation_failed"
                    ) from error
                native_started = True
                deadline = time.monotonic() + 420
                mutated = False
                while harness.poll() is None:
                    hmr_names = accepted_controller._hmr_events(event_path)
                    if "stock_headless_hmr_ready" in hmr_names and not mutated:
                        profile_path.write_bytes(changed)
                        mutated = True
                    if time.monotonic() >= deadline:
                        controller_coordinate = "native_worker_timeout"
                        raise accepted_controller.RehearsalError(
                            "native_worker_timeout"
                        )
                    time.sleep(0.05)
                harness_exit = harness.wait(timeout=10)
            if broker_thread is not None:
                time.sleep(0.25)
            hmr_names = accepted_controller._hmr_events(event_path)
            if runner_terminal_path.is_file():
                runner = accepted_controller.load_json(runner_terminal_path)
            if harness_exit != 0:
                controller_coordinate = "native_process_exited_nonzero"
                raise accepted_controller.RehearsalError(
                    "native_harness_terminal_failure"
                )
    except accepted_controller.RehearsalError as error:
        failure = str(error)
        if native_started and controller_coordinate is None:
            controller_coordinate = "unexpected_controller_failure"
    except (
        converged_controller.ControllerConvergenceError,
        OSError,
        subprocess.SubprocessError,
        ValueError,
        json.JSONDecodeError,
    ):
        failure = "unexpected_controller_failure"
        if native_started:
            controller_coordinate = "unexpected_controller_failure"
    finally:
        if harness is not None and harness.poll() is None:
            accepted_controller._terminate(harness)
        if harness is not None and harness_exit is None:
            harness_exit = harness.poll()
        if native_launch_attempted:
            try:
                hmr_names = accepted_controller._hmr_events(event_path)
            except (
                accepted_controller.RehearsalError,
                OSError,
                UnicodeError,
                json.JSONDecodeError,
            ):
                hmr_observation_valid = False
                failure = (
                    "hmr_observation_invalid"
                    if failure is None
                    else f"{failure}+hmr_observation_invalid"
                )
            for label, path in (("stdout", stdout_path), ("stderr", stderr_path)):
                try:
                    stream_readings[label] = startup_terminal.read_startup_stream(path)
                except startup_terminal.StartupTerminalError:
                    failure = (
                        "pre_hmr_startup_stream_read_failed"
                        if failure is None
                        else f"{failure}+pre_hmr_startup_stream_read_failed"
                    )
            if (
                failure is not None
                and hmr_observation_valid
                and not hmr_names
                and controller_coordinate is not None
                and set(stream_readings) == {"stdout", "stderr"}
            ):
                try:
                    selection = converged_controller.select_pre_hmr_terminal(
                        operation_id=OPERATION_ID,
                        attempt_id=ATTEMPT_ID,
                        candidate_source=checkpoint["candidate_source"],
                        native_process_started=native_started,
                        exit_code=harness_exit,
                        controller_coordinate=controller_coordinate,
                        hmr_events=hmr_names,
                        stdout=stream_readings["stdout"],
                        stderr=stream_readings["stderr"],
                        diagnostic_path=binding.get(
                            "diagnostic_path",
                            root / converged_controller.DIAGNOSTIC_LEAF,
                        ),
                        disposable_root=root,
                    )
                    selected_pre_hmr_terminal = selection["terminal"]
                    if (
                        controller_coordinate == "native_process_exited_nonzero"
                        and not selection["structured_accepted"]
                    ):
                        failure += "+" + str(selection["failure_coordinate"])
                except (
                    converged_controller.ControllerConvergenceError,
                    startup_terminal.StartupTerminalError,
                    OSError,
                    ValueError,
                ):
                    failure += "+pre_hmr_terminal_derivation_failed"
        accepted_controller._terminate(harness)
        accepted_controller._terminate(broker)
        if broker_thread is not None:
            broker_thread.join(timeout=10)
        for label, path in (
            ("stdout", stdout_path),
            ("stderr", stderr_path),
            ("broker_stderr", broker_stderr_path),
        ):
            reading = stream_readings.get(label)
            if reading is None:
                try:
                    reading = startup_terminal.read_startup_stream(path)
                except startup_terminal.StartupTerminalError:
                    reading = None
            raw_readings[f"{label}_bytes"] = (
                reading["byte_count"] if reading is not None else 0
            )
            raw_readings[f"{label}_sha256"] = (
                reading["sha256"]
                if reading is not None
                else accepted_controller.sha256_bytes(b"")
            )

    changed_paths = sorted(
        line[3:].replace("\\", "/")
        for line in accepted_controller.git_at(
            workspace, "status", "--porcelain=v1"
        ).splitlines()
        if len(line) >= 4
    )
    exact_expected = target.is_file() and accepted_controller.file_sha256(
        target
    ) == accepted_controller.sha256_bytes(
        accepted_controller.EXPECTED_SOURCE.encode("utf-8")
    )
    final_digest = accepted_controller.file_sha256(target) if target.is_file() else None
    cases = accepted_controller._run_synthetic_cases(target)
    broker_events: list[dict[str, Any]] = []
    for line in broker_lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            broker_events.append(value)
    broker_counts = {
        "provider_call_started": sum(
            row.get("event") == "provider-call-started" for row in broker_events
        ),
        "provider_call_completed": sum(
            row.get("event") == "provider-call-completed" for row in broker_events
        ),
        "provider_call_failed": sum(
            row.get("event") == "provider-call-failed" for row in broker_events
        ),
        "request_rejected": sum(
            row.get("event") == "broker-request-rejected" for row in broker_events
        ),
    }
    runner_passed = (
        runner.get("status") == "completed"
        and runner.get("request_count") == 1
        and runner.get("tool_names") == ["edit"]
        and runner.get("tool_result_count") == 1
        and runner.get("turn_kind") == "completed"
        and runner.get("conclusion_marked") is True
        and runner.get("allowed_tool_names") == accepted_controller.EXPECTED_TOOLS
    )
    success = (
        failure is None
        and native_started
        and harness_exit == 0
        and hmr_names == ["sentinel_activated", "stock_headless_hmr_ready"]
        and runner_passed
        and broker_counts
        == {
            "provider_call_started": 1,
            "provider_call_completed": 1,
            "provider_call_failed": 0,
            "request_rejected": 0,
        }
        and changed_paths == [accepted_controller.SYNTHETIC_PATH]
        and exact_expected
        and cases == {"executed": True, "public_passed": 4, "holdback_passed": 3}
    )
    if not success and failure is None:
        failure = "occupied_acceptance_mismatch"

    if selected_pre_hmr_terminal is not None:
        try:
            pre_hmr_terminal_sha256 = (
                converged_controller.write_selected_terminal_exclusive(
                    path=accepted_controller.PRE_HMR_TERMINAL_PATH.resolve(),
                    terminal=selected_pre_hmr_terminal,
                    evidence_root=EVIDENCE_ROOT.resolve(),
                    disposable_root=root,
                )
            )
        except (
            converged_controller.ControllerConvergenceError,
            startup_terminal.StartupTerminalError,
            OSError,
            ValueError,
        ):
            success = False
            failure = (
                "pre_hmr_terminalization_failed"
                if failure is None
                else f"{failure}+pre_hmr_terminalization_failed"
            )
    cleanup_passed = accepted_controller.remove_exact_attempt_root(root, parent)
    root_absent = not root.exists()
    if not cleanup_passed or not root_absent:
        success = False
        failure = (
            "attempt_root_cleanup_failed"
            if failure is None
            else f"{failure}+attempt_root_cleanup_failed"
        )
    terminal = {
        "schema_version": accepted_controller.TERMINAL_SCHEMA,
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "candidate_source": checkpoint["candidate_source"],
        "result": "pass" if success else "failed_closed",
        "failure_coordinate": None if success else failure,
        "pre_hmr_startup_terminal_sha256": pre_hmr_terminal_sha256,
        "work_order_sha256": accepted_controller.file_sha256(
            accepted_controller.WORK_ORDER_PATH
        ),
        "process": {
            "native_process_count": 1 if native_started else 0,
            "harness_exit_code": harness_exit,
            "wall_clock_ms": round((time.monotonic() - start) * 1000),
            **raw_readings,
        },
        "profile": runtime_profiles,
        "hmr_events": hmr_names,
        "runner": runner,
        "broker": broker_counts,
        "candidate": {
            "changed_paths": changed_paths,
            "exact_expected_bytes": exact_expected,
            "final_sha256": final_digest,
            "cases": cases,
        },
        "automatic_retry_count": 0,
        "fallback_count": 0,
        "auxiliary_model_call_count": 0,
        "cleanup": {
            "harness_absent": harness is None or harness.poll() is not None,
            "broker_absent": broker is None or broker.poll() is not None,
            "attempt_root_absent": root_absent,
            "raw_logs_retained": False,
            "raw_session_retained": False,
            "provider_key_present_in_worker_environment": False,
        },
    }
    jsonschema.Draft202012Validator(
        accepted_controller.load_json(TERMINAL_SCHEMA_PATH)
    ).validate(terminal)
    accepted_controller.write_json_exclusive(accepted_controller.TERMINAL_PATH, terminal)
    accepted_controller.NATIVE_REPORT_PATH.write_text(
        accepted_controller.render_native_report(terminal),
        encoding="utf-8",
        newline="\n",
    )
    if not success:
        raise accepted_controller.RehearsalError(
            "occupied_attempt_failed_closed:" + str(failure)
        )
    return terminal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--prepare-attempt", action="store_true")
    action.add_argument("--native", action="store_true")
    parser.add_argument("--review-receipt", type=Path)
    args = parser.parse_args()
    try:
        if args.check:
            if args.review_receipt is not None:
                raise accepted_controller.RehearsalError(
                    "review_receipt_only_valid_for_preparation"
                )
            value = provider_free_check()
        elif args.prepare_attempt:
            if args.review_receipt is None:
                raise accepted_controller.RehearsalError("review_receipt_required")
            value = prepare_attempt(args.review_receipt)
        else:
            if args.review_receipt is not None:
                raise accepted_controller.RehearsalError(
                    "review_receipt_only_valid_for_preparation"
                )
            value = execute_native()
        print(json.dumps({"result": value.get("result", value.get("status")), "operation_id": OPERATION_ID}))
        return 0
    except (
        accepted_controller.RehearsalError,
        converged_controller.ControllerConvergenceError,
        jsonschema.ValidationError,
        OSError,
    ) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
