import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.ariadne_deepcode_pty import ensure_project_settings, shared_toolchain
from scripts.ariadne_deepcode_wait import wait_for_receipt


def test_live_prompt_injects_the_monitored_artifact_path() -> None:
    runner = Path("orchestration/deepcode_pty/runner.mjs").read_text(encoding="utf-8")

    assert "function liveCommand(packetRelative, artifactRelative, artifactKind, sharedPython, sharedNode)" in runner
    assert "Write the final durable artifact to exactly ${artifactPath}." in runner
    assert "Do not choose, infer, or substitute another artifact filename." in runner
    assert 'options["artifact-kind"]' in runner


def _run(
    tmp_path: Path, mode: str, timeout: int = 5, exit_timeout: int = 2,
    artifact_kind: str = "decision",
) -> tuple[subprocess.CompletedProcess[str], dict]:
    packet = tmp_path / "packet.md"
    packet.write_text("Synthetic packet.\n", encoding="utf-8")
    receipt = tmp_path / "receipt.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/ariadne_deepcode_pty.py",
            "--cwd",
            str(tmp_path),
            "--packet",
            "packet.md",
            "--artifact",
            "artifact.md",
            "--artifact-kind",
            artifact_kind,
            "--outbox",
            "outbox",
            "--receipt",
            "receipt.json",
            "--timeout",
            str(timeout),
            "--exit-timeout",
            str(exit_timeout),
            "--fixture",
            mode,
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    return result, json.loads(receipt.read_text(encoding="utf-8"))


@pytest.mark.parametrize("mode", ["completion", "markdown_completion", "bold_completion"])
def test_pty_adapter_accepts_worker_completion_artifact(tmp_path: Path, mode: str):
    result, receipt = _run(tmp_path, mode, artifact_kind="completion")

    assert result.returncode == 0
    assert receipt["status"] == "completed"
    assert receipt["artifact_kind"] == "completion"
    assert receipt["completion_signal"] == "artifact_marker"


def test_pty_adapter_uses_canonical_artifact_when_tui_status_is_absent(tmp_path: Path):
    result, receipt = _run(tmp_path, "artifact_only")

    assert result.returncode == 0
    assert receipt["status"] == "completed"
    assert receipt["completion_signal"] == "artifact_marker"
    assert receipt["exit_sent_after_artifact"] is True


def test_pty_adapter_allows_disabled_artifact_deadline(tmp_path: Path):
    result, receipt = _run(tmp_path, "success", timeout=0)

    assert result.returncode == 0
    assert receipt["artifact_deadline_active"] is False


def test_pty_adapter_exits_only_after_artifact_and_observes_mailbox(tmp_path: Path):
    result, receipt = _run(tmp_path, "success")

    assert result.returncode == 0
    assert receipt["status"] == "completed"
    assert receipt["artifact_observed"] is True
    assert receipt["turn_completion_observed"] is True
    assert receipt["completion_signal"] == "artifact_marker"
    assert receipt["exit_sent_after_artifact"] is True
    assert receipt["mailbox_event_count"] == 1
    assert receipt["terminal_output_persisted"] is True
    assert receipt["terminal_transcript"]["path"] == "outbox/receipt.json.terminal.jsonl"
    assert receipt["terminal_transcript"]["event_count"] > 0
    assert receipt["terminal_transcript"]["byte_count"] <= receipt["terminal_transcript"]["max_bytes"]
    assert receipt["process_cleanup_confirmed"] is True


def test_pty_adapter_accepts_markdown_bold_decision(tmp_path: Path):
    result, receipt = _run(tmp_path, "markdown_decision")

    assert result.returncode == 0
    assert receipt["status"] == "completed"
    assert receipt["artifact_observed"] is True


def test_pty_adapter_fails_closed_on_permission_prompt(tmp_path: Path):
    result, receipt = _run(tmp_path, "permission")

    assert result.returncode == 3
    assert receipt["status"] == "blocked"
    assert receipt["reason"] == "unexpected_permission_prompt"
    assert receipt["exit_sent_after_artifact"] is False


def test_pty_adapter_accepts_bounded_forced_cleanup_after_completed_turn(tmp_path: Path):
    result, receipt = _run(tmp_path, "ignore_exit", exit_timeout=1)

    assert result.returncode == 0
    assert receipt["status"] == "completed"
    assert receipt["reason"] == "artifact_and_adapter_event_observed_forced_cleanup"
    assert receipt["forced_cleanup"] is True
    assert receipt["mailbox_event_count"] == 1


def test_pty_adapter_times_out_without_artifact(tmp_path: Path):
    result, receipt = _run(tmp_path, "hang", timeout=1)

    assert result.returncode == 4
    assert receipt["status"] == "failed"
    assert receipt["reason"] == "artifact_timeout"


def test_pty_adapter_rejects_artifact_outside_worker_cwd(tmp_path: Path):
    packet = tmp_path / "packet.md"
    packet.write_text("Synthetic packet.\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/ariadne_deepcode_pty.py",
            "--cwd",
            str(tmp_path),
            "--packet",
            "packet.md",
            "--artifact",
            "../escaped.md",
            "--outbox",
            "outbox",
            "--receipt",
            "receipt.json",
            "--fixture",
            "success",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 2
    assert "artifact must resolve inside --cwd" in result.stderr


def test_pty_adapter_rejects_preexisting_artifact(tmp_path: Path):
    packet = tmp_path / "packet.md"
    packet.write_text("Synthetic packet.\n", encoding="utf-8")
    (tmp_path / "artifact.md").write_text("DECISION: pass\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/ariadne_deepcode_pty.py",
            "--cwd",
            str(tmp_path),
            "--packet",
            "packet.md",
            "--artifact",
            "artifact.md",
            "--outbox",
            "outbox",
            "--receipt",
            "receipt.json",
            "--fixture",
            "success",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 2
    assert "artifact must not exist before PTY launch" in result.stderr


def test_pty_adapter_rejects_second_owner_for_same_artifact(tmp_path: Path):
    packet = tmp_path / "packet.md"
    packet.write_text("Synthetic packet.\n", encoding="utf-8")
    (tmp_path / "artifact.md.ariadne-owner.lock").write_text(
        '{"pid": 1234}\n', encoding="utf-8"
    )
    result = subprocess.run(
        [
            sys.executable,
            "scripts/ariadne_deepcode_pty.py",
            "--cwd",
            str(tmp_path),
            "--packet",
            "packet.md",
            "--artifact",
            "artifact.md",
            "--outbox",
            "outbox",
            "--receipt",
            "receipt.json",
            "--fixture",
            "success",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 2
    assert "artifact owner lock already exists" in result.stderr


def test_project_settings_bootstrap_is_secret_free_and_pre_authorizes_bounded_writes(tmp_path: Path):
    ensure_project_settings(tmp_path)

    payload = json.loads((tmp_path / ".deepcode" / "settings.json").read_text(encoding="utf-8"))
    assert "env" not in payload
    assert payload["permissions"]["allow"] == [
        "read-in-cwd",
        "query-git-log",
        "write-in-cwd",
        "mutate-git-log",
    ]
    assert payload["permissions"]["ask"] == []
    assert "write-out-cwd" in payload["permissions"]["deny"]
    assert "network" in payload["permissions"]["deny"]
    assert "mutate-git-log" not in payload["permissions"]["deny"]


def test_shared_toolchain_resolves_integration_python_and_node() -> None:
    python, node = shared_toolchain()

    assert python is not None and python.is_file()
    assert ".venv" in str(python)
    assert node is not None and node.is_file()


def test_live_launcher_supports_detached_supervision_and_injects_toolchain() -> None:
    source = Path("scripts/ariadne_deepcode_pty.py").read_text(encoding="utf-8")
    runner = Path("orchestration/deepcode_pty/runner.mjs").read_text(encoding="utf-8")

    assert '"--detach"' in source
    assert "subprocess.DETACHED_PROCESS" in source
    assert '"--shared-python"' in source
    assert '"--shared-node"' in source
    assert "ARIADNE_SHARED_PYTHON" in runner
    assert "Do not claim Python or pytest is unavailable before trying it." in runner


def test_receipt_waiter_reads_completion_without_owning_worker(tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"status": "completed"}), encoding="utf-8")

    assert wait_for_receipt(receipt, timeout=0.1, interval=0.01) == {"status": "completed"}


def test_receipt_waiter_timeout_is_non_destructive(tmp_path: Path) -> None:
    with pytest.raises(TimeoutError, match="lifecycle is unchanged"):
        wait_for_receipt(tmp_path / "missing.json", timeout=0.02, interval=0.005)


def test_project_settings_can_select_pro_conductor_without_writing_secrets(tmp_path: Path):
    ensure_project_settings(tmp_path, model="deepseek-v4-pro", reasoning="high")

    payload = json.loads((tmp_path / ".deepcode" / "settings.json").read_text(encoding="utf-8"))
    assert payload["env"] == {"MODEL": "deepseek-v4-pro"}
    assert payload["reasoningEffort"] == "high"
    assert "API_KEY" not in payload["env"]
    assert "BASE_URL" not in payload["env"]


def test_project_settings_bootstrap_rejects_conflicting_write_prompt(tmp_path: Path):
    settings = tmp_path / ".deepcode" / "settings.json"
    settings.parent.mkdir()
    settings.write_text(
        json.dumps({"permissions": {"allow": [], "ask": ["write-in-cwd"]}}), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="required allowed capabilities"):
        ensure_project_settings(tmp_path)


def test_project_settings_bootstrap_rejects_git_mutation_prompt(tmp_path: Path):
    settings = tmp_path / ".deepcode" / "settings.json"
    settings.parent.mkdir()
    settings.write_text(
        json.dumps(
            {
                "permissions": {
                    "allow": ["read-in-cwd", "query-git-log", "write-in-cwd"],
                    "ask": ["mutate-git-log"],
                    "deny": [
                        "read-out-cwd",
                        "write-out-cwd",
                        "delete-in-cwd",
                        "delete-out-cwd",
                        "network",
                        "mcp",
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="required allowed capabilities"):
        ensure_project_settings(tmp_path)


def test_project_settings_bootstrap_rejects_missing_required_denies(tmp_path: Path):
    settings = tmp_path / ".deepcode" / "settings.json"
    settings.parent.mkdir()
    settings.write_text(
        json.dumps(
            {
                "permissions": {
                    "allow": [
                        "read-in-cwd",
                        "query-git-log",
                        "write-in-cwd",
                        "mutate-git-log",
                    ],
                    "ask": [],
                    "deny": [],
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="required denied capabilities"):
        ensure_project_settings(tmp_path)
