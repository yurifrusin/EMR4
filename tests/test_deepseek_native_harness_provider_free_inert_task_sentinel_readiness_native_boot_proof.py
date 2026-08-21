from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_inert_task_sentinel_readiness_native_boot_proof
    as subject,
)


def test_contract_freezes_one_inert_task_and_fresh_attempt() -> None:
    contract = subject._load_contract()

    assert contract["attempt"] == {
        "attempt_id": subject.ATTEMPT_ID,
        "native_process_limit": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
        "fallback": False,
        "reclassification": False,
    }
    assert contract["launch"]["task_arguments"] == [subject.TASK_ARGUMENT]
    assert contract["launch"]["argument_count"] == 6
    assert contract["profile"]["runner_row_count"] == 0
    assert contract["profile"]["runner_file_count"] == 0


def test_deterministic_check_binds_exact_six_argument_command_without_node(
    monkeypatch: Any,
) -> None:
    original_popen = subject.engine.subprocess.Popen

    def guarded_popen(command: Any, *args: Any, **kwargs: Any) -> Any:
        executable = Path(str(command[0])).name.lower()
        if executable in {"node", "node.exe"}:
            raise AssertionError("deterministic check launched Node")
        return original_popen(command, *args, **kwargs)

    monkeypatch.setattr(subject.engine.subprocess, "Popen", guarded_popen)
    projection = subject.deterministic_check()

    assert projection["native_process_count"] == 0
    assert projection["command"][-3:] == [
        "--profile",
        "headless",
        subject.TASK_ARGUMENT,
    ]
    assert len(projection["command"]) == 6
    assert projection["task_argument_count"] == 1
    assert projection["profile"]["runner_row_count"] == 0
    assert projection["disposable_root_prefix"] == subject.DISPOSABLE_PREFIX


def test_lineage_binds_diagnosis_prior_terminal_and_components() -> None:
    subject.configure_engine()
    contract = subject.engine.load_contract()
    lineage = subject._validate_lineage(contract)

    assert len(lineage["sources"]) == 4
    assert len(lineage["components"]) == 9


def test_generalized_launch_accounting_preserves_historical_zero_task_contract() -> None:
    historical_contract = subject.engine._load_json(
        subject.REPO_ROOT
        / "orchestration/continuity/deepseek-native-harness-provider-free-source-repaired-sentinel-native-boot-proof/contract.json"
    )
    command = subject.engine.build_launch_command(
        node_executable="node.exe",
        package_root=Path("C:/fixed/node_modules/@deepseek-ai/dsh"),
        contract=historical_contract,
    )

    assert len(command) == 5
    assert command[-2:] == ["--profile", "headless"]
    assert historical_contract["launch"]["argument_count"] == 5
    assert historical_contract["launch"]["task_arguments"] == []


def test_controller_remains_single_popen_no_retry_and_no_runner() -> None:
    subject.configure_engine()
    checks = subject.engine.validate_controller_source()

    assert all(checks.values())


def test_direct_script_check_bootstraps_and_starts_no_native_process() -> None:
    completed = subprocess.run(  # noqa: S603
        [sys.executable, str(Path(subject.__file__).resolve()), "--check"],
        cwd=subject.REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["status"] == "passed"
    assert output["native_processes"] == 0
    assert output["task_arguments"] == 1


def test_simulated_success_records_one_task_then_cleans(
    tmp_path: Path, monkeypatch: Any
) -> None:
    disposable_parent = tmp_path / "disposable"
    output_root = tmp_path / "evidence"
    disposable_parent.mkdir()
    output_root.mkdir()
    subject.configure_engine()
    engine = subject.engine
    contract = engine.load_contract()
    candidate = contract["planning_source"]

    monkeypatch.setattr(engine, "DISPOSABLE_PARENT", disposable_parent)
    monkeypatch.setattr(engine, "CONSUMED_PATH", output_root / "consumed.json")
    monkeypatch.setattr(engine, "EVIDENCE_PATH", output_root / "terminal.json")
    monkeypatch.setattr(engine, "REPORT_PATH", output_root / "report.md")
    monkeypatch.setattr(engine, "_git_commit_is_ancestor", lambda _source: True)
    monkeypatch.setattr(
        engine,
        "deterministic_check",
        lambda _source=None: {"contract": contract, "native_process_count": 0},
    )
    monkeypatch.setattr(engine.shutil, "which", lambda _name: "C:/node.exe")

    def fake_materialize(
        root: Path, _contract: dict[str, Any]
    ) -> tuple[Path, dict[str, Any]]:
        package_root = root / "installation/node_modules/@deepseek-ai/dsh"
        (package_root / "lib").mkdir(parents=True)
        (package_root / "lib/bin.js").write_bytes(b"fixture")
        return package_root, {
            "package_json_sha256": "0" * 64,
            "profile_sha256": "1" * 64,
            "sentinel_sha256": "2" * 64,
            "sentinel_relative_name": "../../../installation/proof/sentinel.mjs",
        }

    monkeypatch.setattr(engine, "materialize_profile", fake_materialize)

    class FakeProcess:
        def __init__(
            self,
            command: list[str],
            *,
            cwd: Path,
            env: dict[str, str],
            stdout: Any,
            stderr: Any,
        ) -> None:
            assert len(command) == 6
            assert command[-3:] == ["--profile", "headless", subject.TASK_ARGUMENT]
            assert Path(cwd).is_dir()
            assert "DSH_EMR4_BROKER_TOKEN" not in env
            assert stdout is not None and stderr is not None
            root = Path(env["EMR4_HMR_NETWORK_LEDGER"]).parent
            rows = [
                {
                    "schema_version": engine.EVENT_SCHEMA,
                    "sequence": index,
                    "event": event,
                }
                for index, event in enumerate(engine.EXPECTED_EVENTS, start=1)
            ]
            (root / "hmr-events.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
                newline="\n",
            )
            self.returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            self.returncode = 0

        def wait(self, timeout: float | None = None) -> int:
            assert timeout is None or timeout > 0
            self.returncode = 0 if self.returncode is None else self.returncode
            return self.returncode

        def kill(self) -> None:
            self.returncode = 1

    monkeypatch.setattr(engine.subprocess, "Popen", FakeProcess)
    evidence = engine.execute_boot(candidate)

    assert evidence["result"] == "pass"
    assert evidence["hmr_events"] == engine.EXPECTED_EVENTS
    assert evidence["launch"]["native_process_count"] == 1
    assert evidence["launch"]["argument_count"] == 6
    assert evidence["launch"]["task_argument_count"] == 1
    assert evidence["launch"]["controller_terminated_after_readiness"] is True
    assert evidence["provider_boundary"]["network_attempts"] == 0
    assert evidence["cleanup"] == {
        "process_absent": True,
        "disposable_root_absent": True,
        "raw_streams_retained": False,
        "raw_environment_retained": False,
        "copied_package_tree_retained": False,
    }
    assert not any(disposable_parent.iterdir())
    retained = json.loads((output_root / "terminal.json").read_text(encoding="utf-8"))
    jsonschema.validate(retained, engine._load_json(engine.EVIDENCE_SCHEMA_PATH))
    assert retained["streams"]["raw_retained"] is False


def test_retained_pass_terminal_is_exact_consumed_and_cleaned() -> None:
    consumed = subject.engine._load_json(subject.CONSUMED_PATH)
    terminal = subject.engine._load_json(subject.EVIDENCE_PATH)

    jsonschema.validate(
        terminal,
        subject.engine._load_json(subject.EVIDENCE_SCHEMA_PATH),
    )
    assert consumed["state"] == "consumed"
    assert consumed["attempt_id"] == subject.ATTEMPT_ID
    assert consumed["candidate_source"] == terminal["candidate_source"]
    assert len(terminal["candidate_source"]) == 40
    assert terminal["result"] == "pass"
    assert terminal["failure_coordinate"] is None
    assert terminal["hmr_events"] == subject.engine.EXPECTED_EVENTS
    assert terminal["launch"]["launch_attempt_count"] == 1
    assert terminal["launch"]["native_process_count"] == 1
    assert terminal["launch"]["retry_count"] == 0
    assert terminal["launch"]["argument_count"] == 6
    assert terminal["launch"]["task_argument_count"] == 1
    assert terminal["launch"]["readiness_observed"] is True
    assert terminal["launch"]["controller_terminated_after_readiness"] is True
    assert all(
        terminal["provider_boundary"][key] == 0
        for key in (
            "changed_runner_processes",
            "broker_processes",
            "worker_sessions",
            "prompts",
            "tool_executions",
            "model_requests",
            "provider_requests",
            "network_attempts",
            "docker_invocations",
            "database_invocations",
        )
    )
    assert terminal["streams"]["raw_retained"] is False
    assert terminal["cleanup"] == {
        "process_absent": True,
        "disposable_root_absent": True,
        "raw_streams_retained": False,
        "raw_environment_retained": False,
        "copied_package_tree_retained": False,
    }
    assert not any(
        subject.engine.DISPOSABLE_PARENT.glob(subject.DISPOSABLE_PREFIX + "*")
    )
    report = subject.REPORT_PATH.read_text(encoding="utf-8")
    assert "stock-headless HMR reached readiness" in report
    assert "model/provider" in report
    assert "product-runtime or reliability result" in report


def test_plan_and_threat_delta_freeze_closed_surfaces() -> None:
    plan = (
        subject.REPO_ROOT
        / "docs/deepseek-native-harness-provider-free-inert-task-sentinel-readiness-native-boot-proof-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        subject.REPO_ROOT
        / "docs/security/deepseek-native-harness-provider-free-inert-task-sentinel-readiness-native-boot-proof-threat-model-delta.md"
    ).read_text(encoding="utf-8")

    assert "Status: `frozen`" in plan
    assert "process limit: one" in plan
    assert "no second process" in plan
    assert "DeepSeek Flash: declined" in plan
    assert "Gemini 3.7 Flash/high: declined" in plan
    assert "Native subagents: declined" in plan
    assert "complete six-element argv" in threat
    assert "headless runner stays disabled" in threat
