from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_repaired_sentinel_native_boot_proof
    as boot,
)


def test_contract_and_initial_profile_are_exact() -> None:
    contract = boot.load_contract()
    projection = boot.initial_profile_projection(
        Path("C:/deterministic/repaired-sentinel-test")
    )

    assert contract["attempt"] == {
        "attempt_id": boot.ATTEMPT_ID,
        "native_process_limit": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
        "fallback": False,
        "reclassification": False,
    }
    assert contract["profile"]["sentinel_name"] == (
        "../../../installation/proof/sentinel.mjs"
    )
    assert projection["sentinel_row_count"] == 1
    assert projection["runner_row_count"] == 0
    assert b"runner.mjs" not in projection["payload"]


def test_launch_has_no_task_and_controller_has_one_popen() -> None:
    contract = boot.load_contract()
    command = boot.build_launch_command(
        node_executable="node.exe",
        package_root=Path("C:/fixed/node_modules/@deepseek-ai/dsh"),
        contract=contract,
    )

    assert command == [
        "node.exe",
        "--expose-internals",
        str(Path("C:/fixed/node_modules/@deepseek-ai/dsh/lib/bin.js")),
        "--profile",
        "headless",
    ]
    assert all(boot.validate_controller_source().values())


def test_deterministic_check_never_launches_native_process(monkeypatch: Any) -> None:
    original_popen = boot.subprocess.Popen

    def guarded_popen(command: Any, *args: Any, **kwargs: Any) -> Any:
        executable = Path(str(command[0])).name.lower()
        if executable in {"node", "node.exe"}:
            raise AssertionError("deterministic check launched Node")
        return original_popen(command, *args, **kwargs)

    monkeypatch.setattr(boot.subprocess, "Popen", guarded_popen)
    projection = boot.deterministic_check()

    assert projection["native_process_count"] == 0
    assert projection["command"][-2:] == ["--profile", "headless"]
    assert projection["profile"]["runner_row_count"] == 0


def test_direct_script_check_bootstraps_repository_imports() -> None:
    completed = subprocess.run(  # noqa: S603
        [sys.executable, str(Path(boot.__file__).resolve()), "--check"],
        cwd=boot.REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["status"] == "passed"


def test_simulated_success_terminalizes_and_cleans(
    tmp_path: Path, monkeypatch: Any
) -> None:
    disposable_parent = tmp_path / "disposable"
    output_root = tmp_path / "evidence"
    disposable_parent.mkdir()
    output_root.mkdir()
    contract = boot.load_contract()
    candidate = contract["planning_source"]

    monkeypatch.setattr(boot, "DISPOSABLE_PARENT", disposable_parent)
    monkeypatch.setattr(boot, "CONSUMED_PATH", output_root / "consumed.json")
    monkeypatch.setattr(boot, "EVIDENCE_PATH", output_root / "terminal.json")
    monkeypatch.setattr(boot, "REPORT_PATH", output_root / "report.md")
    monkeypatch.setattr(boot, "_git_commit_is_ancestor", lambda _source: True)
    monkeypatch.setattr(
        boot,
        "deterministic_check",
        lambda _source=None: {"contract": contract, "native_process_count": 0},
    )
    monkeypatch.setattr(boot.shutil, "which", lambda _name: "C:/node.exe")

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

    monkeypatch.setattr(boot, "materialize_profile", fake_materialize)

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
            assert len(command) == 5
            assert command[-2:] == ["--profile", "headless"]
            assert Path(cwd).is_dir()
            assert "DSH_EMR4_BROKER_TOKEN" not in env
            assert stdout is not None and stderr is not None
            root = Path(env["EMR4_HMR_NETWORK_LEDGER"]).parent
            rows = [
                {
                    "schema_version": boot.EVENT_SCHEMA,
                    "sequence": index,
                    "event": event,
                }
                for index, event in enumerate(boot.EXPECTED_EVENTS, start=1)
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

    monkeypatch.setattr(boot.subprocess, "Popen", FakeProcess)

    evidence = boot.execute_boot(candidate)

    assert evidence["result"] == "pass"
    assert evidence["hmr_events"] == boot.EXPECTED_EVENTS
    assert evidence["launch"]["native_process_count"] == 1
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
    jsonschema.validate(retained, boot._load_json(boot.EVIDENCE_SCHEMA_PATH))
    assert retained["streams"]["raw_retained"] is False


def test_plan_freezes_one_process_and_no_retry() -> None:
    plan = (
        boot.REPO_ROOT
        / "docs/deepseek-native-harness-provider-free-repaired-sentinel-native-boot-proof-plan.md"
    ).read_text(encoding="utf-8")

    assert "Status: `frozen`" in plan
    assert "native Node/Harness process limit: one" in plan
    assert "automatic retry: false" in plan
    assert "manual retry: false" in plan
    assert "changed profile writes: zero" in plan
    assert "DeepSeek Flash:** declined" in plan
    assert "Gemini 3.7 Flash/high:** declined" in plan
    assert "Native subagents:** declined" in plan
