import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import ariadne_antigravity
from scripts.ariadne_antigravity import WorktreeState, build_command


def _state(branch: str = "antigravity/bounded") -> WorktreeState:
    return WorktreeState(
        root=Path("C:/worktrees/bounded"),
        branch=branch,
        head="abc123",
        dirty=False,
    )


def _passed_orchestrator_receipt(tmp_path: Path) -> Path:
    path = tmp_path / "orchestrator-receipt.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "ariadne.orchestrator_receipt.v1",
                "status": "passed",
                "worker_dispatch_permitted": True,
                "rehydration_sources": sorted(ariadne_antigravity.REHYDRATION_SOURCES),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_command_always_binds_a_fresh_project_and_exact_worktree():
    command = build_command(
        packet="Review the change.",
        state=_state(),
        model="gemini-3.6-flash-high",
        os_sandbox=False,
    )

    assert command[:2] == ["agy", "-p"]
    assert "--new-project" in command
    assert command[command.index("--add-dir") + 1] == "C:\\worktrees\\bounded"
    assert command[command.index("--model") + 1] == "gemini-3.6-flash-high"
    assert command[command.index("--effort") + 1] == "high"
    assert command[command.index("--mode") + 1] == "plan"
    assert command[command.index("--output-format") + 1] == "json"
    schema = json.loads(command[command.index("--json-schema") + 1])
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["decision", "review"]
    assert "BOUND BRANCH: antigravity/bounded" in command[2]
    assert "STRUCTURED OUTPUT OVERRIDE" in command[2]
    assert "--sandbox" not in command


def test_os_sandbox_is_explicit_and_never_the_unattended_default():
    command = build_command(
        packet="Review.",
        state=_state(),
        model="gemini-3.6-flash-medium",
        os_sandbox=True,
    )

    assert command[-1] == "--sandbox"


def test_legacy_model_alias_is_canonicalized_with_explicit_effort():
    command = build_command(
        packet="Review.",
        state=_state(),
        model="Gemini 3.5 Flash (High)",
        os_sandbox=False,
    )

    assert command[command.index("--model") + 1] == "gemini-3.5-flash-high"
    assert command[command.index("--effort") + 1] == "high"


def test_command_rejects_non_gemini_flash_model():
    with pytest.raises(ValueError, match="unsupported Antigravity model"):
        build_command(
            packet="Review.",
            state=_state(),
            model="Claude Opus 4.6 (Thinking)",
            os_sandbox=False,
        )


def test_run_worker_records_canonical_high_model_and_read_only_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {
                    "result": {
                        "decision": "pass",
                        "review": "No material findings; focused checks passed.",
                    },
                    "usage": {"input_tokens": 10, "output_tokens": 8},
                }
            ),
            stderr="",
        ),
    )

    receipt = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=tmp_path,
        output_path=output,
        orchestrator_receipt_path=orchestrator_receipt,
        model="gemini-3.6-flash-high",
        os_sandbox=False,
    )

    assert receipt["model"] == "gemini-3.6-flash-high"
    assert receipt["reasoning_effort"] == "high"
    assert receipt["decision"] == "pass"
    assert receipt["decision_contract"] == "schema_constrained_json_v1"
    assert receipt["decision_envelope"] == {
        "decision": "pass",
        "review": "No material findings; focused checks passed.",
    }
    assert receipt["transport"] == ("antigravity_new_project_bound_readonly_worktree")
    assert output.is_file()
    assert len(receipt["orchestrator_receipt_sha256"]) == 64


def test_run_worker_rejects_revision_required_orchestrator_receipt_before_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    rejected = json.loads(orchestrator_receipt.read_text(encoding="utf-8"))
    rejected["status"] = "revision_required"
    rejected["worker_dispatch_permitted"] = False
    orchestrator_receipt.write_text(json.dumps(rejected) + "\n", encoding="utf-8")
    invoked = False

    def _unexpected_dispatch(*_args, **_kwargs):
        nonlocal invoked
        invoked = True
        raise AssertionError("provider transport must not run")

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _unexpected_dispatch)

    with pytest.raises(ValueError, match="did not pass"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
        )

    assert invoked is False
    assert not output.exists()


def test_run_worker_fails_if_verifier_modifies_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    before = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    after = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=True,
    )
    states = iter([before, after])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout=json.dumps(
                {"decision": "pass", "review": "Candidate remained unchanged."}
            ),
            stderr="",
        ),
    )

    with pytest.raises(RuntimeError, match="modified its read-only candidate"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
        )

    assert not output.exists()


@pytest.mark.parametrize(
    "stdout, decision_count",
    [
        ("No decision.", 0),
        ("DECISION: pass\nDECISION: pass", 2),
    ],
)
def test_run_worker_rejects_missing_or_duplicate_terminal_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
    decision_count: int,
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout=stdout, stderr=""
        ),
    )

    with pytest.raises(
        RuntimeError,
        match=f"exactly one terminal decision; observed {decision_count}",
    ):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
            structured_decision=False,
        )

    assert not output.exists()


@pytest.mark.parametrize(
    "stdout, envelope_count",
    [
        (json.dumps({"result": "not structured"}), 0),
        (
            json.dumps(
                {
                    "structured_output": {
                        "decision": "pass",
                        "review": "First result.",
                    },
                    "result": {
                        "decision": "revision_required",
                        "review": "Conflicting result.",
                    },
                }
            ),
            2,
        ),
    ],
)
def test_run_worker_rejects_missing_or_conflicting_structured_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
    envelope_count: int,
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout=stdout, stderr=""
        ),
    )

    with pytest.raises(
        RuntimeError,
        match=(
            f"exactly one schema-valid decision envelope; observed {envelope_count}"
        ),
    ):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
        )

    assert not output.exists()


def test_structured_decision_rejects_embedded_legacy_terminal_marker() -> None:
    stdout = json.dumps(
        {
            "decision": "pass",
            "review": "Review complete.\nDECISION: pass",
        }
    )

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout)
