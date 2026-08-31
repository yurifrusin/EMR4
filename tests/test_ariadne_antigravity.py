import ast
import copy
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import orchestration_harness.programme_admission as programme_admission
from orchestration_harness import trusted_git
from orchestration_harness.verdict import ReviewVerdict
from scripts import ariadne_antigravity
from scripts.ariadne_antigravity import WorktreeState, build_command
from scripts.raisa_ariadne_recovery_preflight import build_task_manifest


TEST_HEAD = "a" * 40
TEST_TREE = "b" * 40
TEST_COMPLETE_DIGEST = "sha256:" + "c" * 64
TEST_IDENTITY_DIGEST = "sha256:" + "d" * 64
_REAL_ATTEST_REPOSITORY = trusted_git.attest_repository
_REAL_RUN_GIT = trusted_git.run_git
_REAL_RUN_GIT_BYTES = trusted_git.run_git_bytes
_REAL_SUBPROCESS_RUN = subprocess.run


@pytest.fixture(autouse=True)
def _admit_direct_worker_unit_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ariadne_antigravity, "require_programme_admission", lambda **_kwargs: None
    )

    def _attest(root, *, expected_commit=None, **_kwargs):
        head = expected_commit or TEST_HEAD
        return {
            "worktree": {"resolved_path": str(Path(root).resolve())},
            "head": head,
            "head_tree": TEST_TREE,
            "index_tree": TEST_TREE,
            "trusted_git_identity_sha256": TEST_IDENTITY_DIGEST,
            "complete_tracked_tree_attestation": {
                "head": head,
                "head_tree": TEST_TREE,
                "index_tree": TEST_TREE,
                "complete_tracked_tree_sha256": TEST_COMPLETE_DIGEST,
                "complete_tracked_path_count": 1,
            },
        }

    monkeypatch.setattr(trusted_git, "attest_repository", _attest)
    monkeypatch.setattr(
        trusted_git,
        "run_git",
        lambda *_args: "codex/verifier-candidate",
    )
    monkeypatch.setattr(trusted_git, "run_git_bytes", lambda *_args: b"")


def _state(branch: str = "antigravity/bounded") -> WorktreeState:
    return WorktreeState(
        root=Path("C:/worktrees/bounded"),
        branch=branch,
        head=TEST_HEAD,
        dirty=False,
    )


def _assessment(decision: str) -> dict[str, object]:
    integration_authorized = decision == "pass"
    return {
        "artifact_kind": "decision",
        "artifact_valid": True,
        "review_verdict": decision,
        "integration_authorized": integration_authorized,
        "canonical_marker": f"DECISION: {decision.upper()}",
        "reason_code": "terminal_marker_observed",
    }


def _command_manifest() -> dict[str, object]:
    return {
        "schema_version": "ariadne.verifier-command-manifest.v1",
        "commands": [
            {"id": "LINT", "argv": ["python", "-m", "ruff", "check", "."]},
            {"id": "TEST", "argv": ["python", "-m", "pytest", "-q"]},
        ],
    }


def _command_results(*exit_codes: int) -> list[dict[str, object]]:
    manifest = _command_manifest()
    commands = manifest["commands"]
    assert isinstance(commands, list)
    return [
        {
            "id": command["id"],
            "argv": command["argv"],
            "exit_code": exit_code,
        }
        for command, exit_code in zip(commands, exit_codes, strict=True)
    ]


def _mock_completed_worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    stdout: str,
) -> tuple[Path, Path, Path]:
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head=TEST_HEAD,
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
            stdout=stdout,
            stderr="",
        ),
    )
    return packet, output, orchestrator_receipt


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


def _new_real_candidate_repository(tmp_path: Path) -> Path:
    candidate = tmp_path / "candidate"
    candidate.mkdir()

    def _git(*argv: str) -> None:
        _REAL_SUBPROCESS_RUN(
            ["git", *argv],
            cwd=candidate,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    _git("init", "-b", "codex/verifier-candidate")
    _git("config", "user.email", "tests@example.invalid")
    _git("config", "user.name", "G1A3 R1 Trusted Git Tests")
    _git("config", "core.autocrlf", "false")
    (candidate / "AGENTS.md").write_bytes(b"trusted-git-first\n")
    _git("add", "AGENTS.md")
    _git("commit", "-m", "seed trusted Git candidate")
    return candidate


def _real_git_or_synthetic_provider(
    provider_result: SimpleNamespace,
    provider_calls: list[list[str]],
):
    def _run(command, *args, **kwargs):
        if command and command[0] == "agy":
            provider_calls.append(command)
            return provider_result
        return _REAL_SUBPROCESS_RUN(command, *args, **kwargs)

    return _run


def test_command_always_binds_a_fresh_project_and_exact_worktree():
    command = build_command(
        packet="Review the change.",
        state=_state(),
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )

    assert command[:2] == ["agy", "-p"]
    assert "--new-project" in command
    assert command[command.index("--add-dir") + 1] == "C:\\worktrees\\bounded"
    assert command[command.index("--model") + 1] == "gemini-3.7-flash-high"
    assert command[command.index("--effort") + 1] == "high"
    assert command[command.index("--mode") + 1] == "plan"
    assert command[command.index("--print-timeout") + 1] == "45m"
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
        head=TEST_HEAD,
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
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )

    assert receipt["model"] == "gemini-3.7-flash-high"
    assert receipt["reasoning_effort"] == "high"
    assert receipt["decision"] == "pass"
    assert receipt["decision_contract"] == "schema_constrained_json_v1"
    assert receipt["decision_envelope"] == {
        "decision": "pass",
        "review": "No material findings; focused checks passed.",
        "verdict_assessment": _assessment("pass"),
    }
    assert receipt["transport"] == ("antigravity_new_project_bound_readonly_worktree")
    assert output.is_file()
    assert len(receipt["orchestrator_receipt_sha256"]) == 64
    assert (
        receipt["complete_review_attestation_before"]
        == receipt["complete_review_attestation_after"]
        == {
            "head": TEST_HEAD,
            "head_tree": TEST_TREE,
            "index_tree": TEST_TREE,
            "complete_tracked_tree_sha256": TEST_COMPLETE_DIGEST,
            "complete_tracked_path_count": 1,
            "trusted_git_identity_sha256": TEST_IDENTITY_DIGEST,
        }
    )
    assert (
        receipt["nontracked_inventory_before"]
        == receipt["nontracked_inventory_after"]
        == {
            "ordinary_count": 0,
            "ordinary_paths_sha256": (
                "sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
            ),
            "ignored_count": 0,
            "ignored_paths_sha256": (
                "sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
            ),
        }
    )


def test_run_worker_admission_is_first_and_denial_has_zero_other_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    observed: list[str] = []

    def _deny(**_kwargs) -> None:
        observed.append("admission")
        raise RuntimeError("active profile denies provider invocation")

    monkeypatch.setattr(ariadne_antigravity, "require_programme_admission", _deny)
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: pytest.fail("provider or Git access occurred"),
    )
    output = tmp_path / "must-not-exist.json"

    with pytest.raises(RuntimeError, match="active profile denies"):
        ariadne_antigravity.run_worker(
            packet_path=tmp_path / "missing-packet.md",
            cwd=tmp_path / "missing-worktree",
            output_path=output,
            orchestrator_receipt_path=tmp_path / "missing-orchestrator.json",
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    assert observed == ["admission"]
    assert not output.exists()


def test_run_worker_source_has_no_legacy_or_caller_path_git_observation() -> None:
    source = Path(ariadne_antigravity.__file__).read_text(encoding="utf-8")
    module = ast.parse(source)
    run_worker = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "run_worker"
    )
    calls = [node for node in ast.walk(run_worker) if isinstance(node, ast.Call)]

    direct_names = {call.func.id for call in calls if isinstance(call.func, ast.Name)}
    assert direct_names.isdisjoint({"inspect_worktree", "_git"})

    subprocess_calls = [
        call
        for call in calls
        if isinstance(call.func, ast.Attribute)
        and call.func.attr == "run"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "subprocess"
    ]
    assert len(subprocess_calls) == 1
    assert isinstance(subprocess_calls[0].args[0], ast.Name)
    assert subprocess_calls[0].args[0].id == "provider_command"

    literal_git_commands = []
    for call in subprocess_calls:
        if not call.args or not isinstance(call.args[0], (ast.List, ast.Tuple)):
            continue
        elements = call.args[0].elts
        if (
            elements
            and isinstance(elements[0], ast.Constant)
            and str(elements[0].value).lower() in {"git", "git.exe"}
        ):
            literal_git_commands.append(call)
    assert literal_git_commands == []


@pytest.mark.parametrize(
    "mode",
    [
        "success",
        "pre_attestation_failure",
        "post_attestation_failure",
        "nonzero_provider",
        "structured_rejection",
    ],
)
def test_run_worker_never_reaches_legacy_git_observers_on_any_exit_class(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    legacy_calls: list[str] = []

    def _legacy_tripwire(*_args, **_kwargs):
        legacy_calls.append("legacy")
        raise AssertionError("legacy Git observation executed")

    monkeypatch.setattr(ariadne_antigravity, "inspect_worktree", _legacy_tripwire)
    monkeypatch.setattr(ariadne_antigravity, "_git", _legacy_tripwire)
    attest_calls = 0

    def _attest(root, *, expected_commit=None, **_kwargs):
        nonlocal attest_calls
        attest_calls += 1
        if mode == "pre_attestation_failure" and attest_calls == 2:
            raise trusted_git.TrustedGitError("synthetic_pre_attestation_failure")
        if mode == "post_attestation_failure" and attest_calls == 3:
            raise trusted_git.TrustedGitError("synthetic_post_attestation_failure")
        head = expected_commit or TEST_HEAD
        return {
            "worktree": {"resolved_path": str(Path(root).resolve())},
            "head": head,
            "head_tree": TEST_TREE,
            "index_tree": TEST_TREE,
            "trusted_git_identity_sha256": TEST_IDENTITY_DIGEST,
            "complete_tracked_tree_attestation": {
                "head": head,
                "head_tree": TEST_TREE,
                "index_tree": TEST_TREE,
                "complete_tracked_tree_sha256": TEST_COMPLETE_DIGEST,
                "complete_tracked_path_count": 1,
            },
        }

    def _run_git(root, *argv):
        if argv == ("rev-parse", "--show-toplevel"):
            return str(Path(root).resolve())
        if argv == ("symbolic-ref", "--quiet", "--short", "HEAD"):
            return "codex/verifier-candidate"
        if argv == ("rev-parse", "HEAD"):
            return TEST_HEAD
        raise AssertionError(f"unexpected trusted Git command: {argv!r}")

    monkeypatch.setattr(trusted_git, "attest_repository", _attest)
    monkeypatch.setattr(trusted_git, "run_git", _run_git)
    provider_calls = 0

    def _provider(*_args, **_kwargs):
        nonlocal provider_calls
        provider_calls += 1
        if mode == "nonzero_provider":
            return SimpleNamespace(returncode=7, stdout="", stderr="transport")
        if mode == "structured_rejection":
            stdout = json.dumps({"result": "not structured"})
        else:
            stdout = json.dumps(
                {"decision": "pass", "review": "Trusted Git boundary passed."}
            )
        return SimpleNamespace(returncode=0, stdout=stdout, stderr="")

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _provider)
    invocation = lambda: ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=tmp_path,
        output_path=output,
        orchestrator_receipt_path=orchestrator_receipt,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )

    if mode == "success":
        assert invocation()["decision"] == "pass"
    elif mode == "pre_attestation_failure":
        with pytest.raises(
            trusted_git.TrustedGitError, match="synthetic_pre_attestation_failure"
        ):
            invocation()
    else:
        with pytest.raises(RuntimeError):
            invocation()

    assert legacy_calls == []
    assert provider_calls == (0 if mode == "pre_attestation_failure" else 1)
    assert output.exists() is (mode != "pre_attestation_failure")


@pytest.mark.parametrize("branch", ["", "master", "handoff/current"])
def test_run_worker_rejects_detached_or_protected_branch_before_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    branch: str,
) -> None:
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "must-not-exist.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    monkeypatch.setattr(trusted_git, "run_git", lambda *_args: branch)
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: pytest.fail("legacy inspect_worktree executed"),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: pytest.fail("provider executed"),
    )

    with pytest.raises(ValueError, match="protected or detached branch"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    assert not output.exists()


def test_run_worker_rejects_fsmonitor_before_hook_or_provider_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = _new_real_candidate_repository(tmp_path)
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "must-not-exist.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    sentinel = tmp_path / "fsmonitor-executed.txt"
    hook = tmp_path / "fsmonitor.cmd"
    hook.write_text(
        f'@echo off\r\necho executed>"{sentinel}"\r\necho token\r\n',
        encoding="utf-8",
    )
    _REAL_SUBPROCESS_RUN(
        ["git", "config", "--local", "core.fsmonitor", str(hook)],
        cwd=candidate,
        check=True,
        capture_output=True,
    )
    _REAL_SUBPROCESS_RUN(
        ["git", "config", "--local", "core.fsmonitorHookVersion", "2"],
        cwd=candidate,
        check=True,
        capture_output=True,
    )
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: pytest.fail("legacy inspect_worktree executed"),
    )
    provider_calls: list[list[str]] = []
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        _real_git_or_synthetic_provider(
            SimpleNamespace(returncode=0, stdout="", stderr=""), provider_calls
        ),
    )

    with pytest.raises(
        trusted_git.TrustedGitError, match="trusted_git_configuration_forbidden"
    ):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=candidate,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    assert provider_calls == []
    assert not sentinel.exists()
    assert not output.exists()


def test_run_worker_ignores_caller_path_git_on_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = _new_real_candidate_repository(tmp_path)
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    sentinel = tmp_path / "caller-path-git-executed.txt"
    (fake_bin / "git.cmd").write_text(
        f'@echo off\r\necho executed>"{sentinel}"\r\nexit /b 99\r\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("PATH", str(fake_bin) + os.pathsep + os.environ["PATH"])
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: pytest.fail("legacy inspect_worktree executed"),
    )
    provider_calls: list[list[str]] = []
    provider_result = SimpleNamespace(
        returncode=0,
        stdout=json.dumps(
            {"decision": "pass", "review": "Caller PATH Git was not used."}
        ),
        stderr="",
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        _real_git_or_synthetic_provider(provider_result, provider_calls),
    )

    receipt = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=candidate,
        output_path=output,
        orchestrator_receipt_path=orchestrator_receipt,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )

    assert receipt["decision"] == "pass"
    assert len(provider_calls) == 1
    assert not sentinel.exists()


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("core.ignoreStat", "true"),
        ("core.checkStat", "minimal"),
        ("core.trustctime", "false"),
    ],
)
def test_run_worker_rejects_visibility_weakening_before_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    key: str,
    value: str,
) -> None:
    candidate = _new_real_candidate_repository(tmp_path)
    _REAL_SUBPROCESS_RUN(
        ["git", "config", "--local", key, value],
        cwd=candidate,
        check=True,
        capture_output=True,
    )
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "must-not-exist.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)
    provider_calls: list[list[str]] = []
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        _real_git_or_synthetic_provider(
            SimpleNamespace(returncode=0, stdout="", stderr=""), provider_calls
        ),
    )

    with pytest.raises(
        trusted_git.TrustedGitError, match="trusted_git_configuration_forbidden"
    ):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=candidate,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    assert provider_calls == []
    assert not output.exists()


def test_run_worker_rejects_high_risk_git_environment_before_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = _new_real_candidate_repository(tmp_path)
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "must-not-exist.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "attacker-selected-git-dir"))
    provider_calls: list[list[str]] = []
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        _real_git_or_synthetic_provider(
            SimpleNamespace(returncode=0, stdout="", stderr=""), provider_calls
        ),
    )

    with pytest.raises(
        trusted_git.TrustedGitError, match="trusted_git_environment_forbidden"
    ):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=candidate,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    assert provider_calls == []
    assert not output.exists()


@pytest.mark.parametrize("failure_surface", ["attestation", "ordinary", "ignored"])
def test_pre_provider_complete_review_failure_starts_no_provider_and_writes_no_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_surface: str,
) -> None:
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "must-not-exist.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head=TEST_HEAD,
        dirty=False,
    )
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: state,
    )
    if failure_surface == "attestation":
        monkeypatch.setattr(
            trusted_git,
            "attest_repository",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                trusted_git.TrustedGitError("synthetic_complete_tree_failure")
            ),
        )
    else:

        def _inventory(_root, *argv):
            ignored = "--ignored" in argv
            if (failure_surface == "ignored") == ignored:
                return b"synthetic-path\x00"
            return b""

        monkeypatch.setattr(trusted_git, "run_git_bytes", _inventory)
    provider_calls = 0

    def _provider(*_args, **_kwargs):
        nonlocal provider_calls
        provider_calls += 1
        raise AssertionError("provider must not run")

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _provider)

    with pytest.raises((ValueError, trusted_git.TrustedGitError)):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    assert provider_calls == 0
    assert not output.exists()


@pytest.mark.parametrize(
    "drift_surface",
    [
        "head",
        "tree",
        "index",
        "identity",
        "tracked_digest",
        "ordinary",
        "ignored",
        "branch",
    ],
)
def test_post_provider_boundary_rejects_every_bound_identity_or_inventory_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    drift_surface: str,
) -> None:
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "failure.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head=TEST_HEAD,
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    attestation_calls = 0

    def _attest(_root, *, expected_commit, **_kwargs):
        nonlocal attestation_calls
        attestation_calls += 1
        head = expected_commit or TEST_HEAD
        tree = TEST_TREE
        index_tree = TEST_TREE
        identity_digest = TEST_IDENTITY_DIGEST
        complete_digest = TEST_COMPLETE_DIGEST
        if attestation_calls == 3:
            if drift_surface == "head":
                head = "e" * 40
            elif drift_surface == "tree":
                tree = "e" * 40
                index_tree = tree
            elif drift_surface == "index":
                index_tree = "e" * 40
            elif drift_surface == "identity":
                identity_digest = "sha256:" + "e" * 64
            elif drift_surface == "tracked_digest":
                complete_digest = "sha256:" + "e" * 64
        return {
            "worktree": {"resolved_path": str(Path(_root).resolve())},
            "head": head,
            "head_tree": tree,
            "index_tree": index_tree,
            "trusted_git_identity_sha256": identity_digest,
            "complete_tracked_tree_attestation": {
                "head": head,
                "head_tree": tree,
                "index_tree": index_tree,
                "complete_tracked_tree_sha256": complete_digest,
                "complete_tracked_path_count": 1,
            },
        }

    monkeypatch.setattr(trusted_git, "attest_repository", _attest)
    branch_calls = 0

    def _branch(*_args):
        nonlocal branch_calls
        branch_calls += 1
        if drift_surface == "branch" and branch_calls == 3:
            return "codex/escaped"
        return state.branch

    monkeypatch.setattr(trusted_git, "run_git", _branch)
    ordinary_calls = 0
    ignored_calls = 0

    def _inventory(_root, *argv):
        nonlocal ordinary_calls, ignored_calls
        if "--ignored" in argv:
            ignored_calls += 1
            if drift_surface == "ignored" and ignored_calls == 3:
                return b"ignored.tmp\x00"
        else:
            ordinary_calls += 1
            if drift_surface == "ordinary" and ordinary_calls == 3:
                return b"ordinary.tmp\x00"
        return b""

    monkeypatch.setattr(trusted_git, "run_git_bytes", _inventory)
    provider_calls = 0

    def _provider(*_args, **_kwargs):
        nonlocal provider_calls
        provider_calls += 1
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"decision": "pass", "review": "Synthetic pass."}),
            stderr="",
        )

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _provider)

    with pytest.raises(RuntimeError, match="complete review attestation failed"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert provider_calls == 1
    assert failure["candidate_review_admitted"] is False
    assert failure["reason_code"] == "complete_review_attestation_postcondition_failed"


def test_nonzero_provider_return_still_requires_post_provider_complete_attestation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "failure.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(tmp_path, "codex/verifier-candidate", TEST_HEAD, False)
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    calls = 0

    def _attest(_root, *, expected_commit, **_kwargs):
        nonlocal calls
        calls += 1
        head = expected_commit or TEST_HEAD
        digest = TEST_COMPLETE_DIGEST if calls < 3 else "sha256:" + "e" * 64
        return {
            "worktree": {"resolved_path": str(Path(_root).resolve())},
            "head": head,
            "head_tree": TEST_TREE,
            "index_tree": TEST_TREE,
            "trusted_git_identity_sha256": TEST_IDENTITY_DIGEST,
            "complete_tracked_tree_attestation": {
                "head": head,
                "head_tree": TEST_TREE,
                "index_tree": TEST_TREE,
                "complete_tracked_tree_sha256": digest,
                "complete_tracked_path_count": 1,
            },
        }

    monkeypatch.setattr(trusted_git, "attest_repository", _attest)
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=9, stdout="transport output", stderr="transport error"
        ),
    )

    with pytest.raises(RuntimeError, match="complete review attestation failed"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert calls == 3
    assert failure["exit_code"] == 9
    assert failure["candidate_review_admitted"] is False


def test_complete_attestation_detects_same_size_restored_mtime_provider_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()

    def _git(*argv: str) -> str:
        completed = _REAL_SUBPROCESS_RUN(
            ["git", *argv],
            cwd=candidate,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()

    _git("init", "-b", "codex/verifier-candidate")
    _git("config", "user.email", "tests@example.invalid")
    _git("config", "user.name", "G1A3 R1 Tests")
    _git("config", "core.autocrlf", "false")
    tracked = candidate / "AGENTS.md"
    tracked.write_bytes(b"reviewed-bytes\n")
    _git("add", "AGENTS.md")
    _git("commit", "-m", "seed candidate")
    original_stat = tracked.stat()

    evidence = tmp_path / "evidence"
    evidence.mkdir()
    packet = evidence / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = evidence / "failure.json"
    orchestrator_receipt = _passed_orchestrator_receipt(evidence)
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)

    def _provider_or_git(command, *args, **kwargs):
        if command and command[0] == "agy":
            tracked.write_bytes(b"mutated-bytes!\n")
            assert tracked.stat().st_size == original_stat.st_size
            os.utime(
                tracked,
                ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns),
            )
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps({"decision": "pass", "review": "Synthetic pass."}),
                stderr="",
            )
        return _REAL_SUBPROCESS_RUN(command, *args, **kwargs)

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _provider_or_git)

    with pytest.raises(RuntimeError, match="complete review attestation failed"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=candidate,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["candidate_review_admitted"] is False
    assert failure["reason_code"] == "complete_review_attestation_postcondition_failed"


def test_same_size_restored_mtime_drift_before_attestation_starts_no_provider(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()

    def _git(*argv: str) -> str:
        completed = _REAL_SUBPROCESS_RUN(
            ["git", *argv],
            cwd=candidate,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()

    _git("init", "-b", "codex/verifier-candidate")
    _git("config", "user.email", "tests@example.invalid")
    _git("config", "user.name", "G1A3 R1 Tests")
    _git("config", "core.autocrlf", "false")
    tracked = candidate / "AGENTS.md"
    tracked.write_bytes(b"reviewed-bytes\n")
    _git("add", "AGENTS.md")
    _git("commit", "-m", "seed candidate")
    original_stat = tracked.stat()
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    packet = evidence / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = evidence / "must-not-exist.json"
    orchestrator_receipt = _passed_orchestrator_receipt(evidence)
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)
    real_build_command = ariadne_antigravity.build_command

    def _build_then_mutate(**kwargs):
        command = real_build_command(**kwargs)
        tracked.write_bytes(b"mutated-bytes!\n")
        assert tracked.stat().st_size == original_stat.st_size
        os.utime(
            tracked,
            ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns),
        )
        return command

    monkeypatch.setattr(ariadne_antigravity, "build_command", _build_then_mutate)
    provider_calls = 0

    def _provider_or_git(command, *args, **kwargs):
        nonlocal provider_calls
        if command and command[0] == "agy":
            provider_calls += 1
            raise AssertionError("provider must not run")
        return _REAL_SUBPROCESS_RUN(command, *args, **kwargs)

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _provider_or_git)

    with pytest.raises(trusted_git.TrustedGitError):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=candidate,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    assert provider_calls == 0
    assert not output.exists()


@pytest.mark.parametrize(
    ("config_key", "config_value"),
    [("core.checkStat", "minimal"), ("core.trustctime", "false")],
)
def test_provider_created_repository_configuration_drift_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    config_key: str,
    config_value: str,
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()

    def _git(*argv: str) -> str:
        completed = _REAL_SUBPROCESS_RUN(
            ["git", *argv],
            cwd=candidate,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()

    _git("init", "-b", "codex/verifier-candidate")
    _git("config", "user.email", "tests@example.invalid")
    _git("config", "user.name", "G1A3 R1 Tests")
    _git("config", "core.autocrlf", "false")
    (candidate / "AGENTS.md").write_bytes(b"reviewed-bytes\n")
    _git("add", "AGENTS.md")
    _git("commit", "-m", "seed candidate")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    packet = evidence / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = evidence / "failure.json"
    orchestrator_receipt = _passed_orchestrator_receipt(evidence)
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)

    def _provider_or_git(command, *args, **kwargs):
        if command and command[0] == "agy":
            _git("config", config_key, config_value)
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps({"decision": "pass", "review": "Synthetic pass."}),
                stderr="",
            )
        return _REAL_SUBPROCESS_RUN(command, *args, **kwargs)

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _provider_or_git)

    with pytest.raises(RuntimeError, match="complete review attestation failed"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=candidate,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["candidate_review_admitted"] is False


def test_nonzero_transport_writes_digest_only_failure_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "transport-failure.json"
    orchestrator_receipt = _passed_orchestrator_receipt(tmp_path)
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head=TEST_HEAD,
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
            returncode=1,
            stdout="bounded diagnostic on stdout",
            stderr="",
        ),
    )
    times = iter([10.0, 2710.0])
    monkeypatch.setattr(ariadne_antigravity.time, "monotonic", lambda: next(times))

    with pytest.raises(RuntimeError, match="digest-only diagnostics written"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.7-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["schema_version"] == "ariadne.transport-failure-receipt.v1"
    assert failure["status"] == "transport_failed_without_terminal_decision"
    assert failure["exit_code"] == 1
    assert failure["elapsed_ms"] == 2_700_000
    assert failure["print_timeout_seconds"] == 2_700
    assert failure["print_timeout_boundary_reached"] is True
    assert failure["stdout"]["bytes"] == len("bounded diagnostic on stdout")
    assert failure["stderr"]["empty"] is True
    assert failure["worktree_identity_unchanged"] is True
    assert failure["terminal_decision_returned"] is False
    assert failure["candidate_review_admitted"] is False
    assert "bounded diagnostic on stdout" not in output.read_text(encoding="utf-8")


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
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: pytest.fail("legacy inspect_worktree executed"),
    )
    attestation_calls = 0

    def _attest(root, *, expected_commit=None, **_kwargs):
        nonlocal attestation_calls
        attestation_calls += 1
        head = expected_commit or TEST_HEAD
        digest = TEST_COMPLETE_DIGEST if attestation_calls < 3 else "sha256:" + "e" * 64
        return {
            "worktree": {"resolved_path": str(Path(root).resolve())},
            "head": head,
            "head_tree": TEST_TREE,
            "index_tree": TEST_TREE,
            "trusted_git_identity_sha256": TEST_IDENTITY_DIGEST,
            "complete_tracked_tree_attestation": {
                "head": head,
                "head_tree": TEST_TREE,
                "index_tree": TEST_TREE,
                "complete_tracked_tree_sha256": digest,
                "complete_tracked_path_count": 1,
            },
        }

    def _run_git(root, *argv):
        if "--show-toplevel" in argv:
            return str(Path(root).resolve())
        if "symbolic-ref" in argv:
            return "codex/verifier-candidate"
        if argv == ("rev-parse", "HEAD"):
            return TEST_HEAD
        raise AssertionError(f"unexpected trusted Git command: {argv!r}")

    monkeypatch.setattr(trusted_git, "attest_repository", _attest)
    monkeypatch.setattr(trusted_git, "run_git", _run_git)
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

    with pytest.raises(RuntimeError, match="complete review attestation failed"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            orchestrator_receipt_path=orchestrator_receipt,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
        )

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["schema_version"] == "ariadne.egress-failure-receipt.v1"
    assert failure["status"] == ("egress_failed_without_admitted_terminal_decision")
    assert failure["exit_code"] == 0
    assert failure["head_before"] == failure["head_after"] == TEST_HEAD
    assert failure["dirty_after"] is True
    assert failure["worktree_identity_unchanged"] is False
    assert failure["reason_code"] == "complete_review_attestation_postcondition_failed"
    assert failure["terminal_decision_admitted"] is False
    assert failure["candidate_review_admitted"] is False
    assert failure["stdout"]["bytes"] > 0
    assert "Candidate remained unchanged" not in output.read_text(encoding="utf-8")


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
        head=TEST_HEAD,
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

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["schema_version"] == "ariadne.egress-failure-receipt.v1"
    assert failure["decision_contract"] == "legacy_terminal_line_v1"
    assert failure["reason_code"] == "legacy_terminal_decision_not_admitted"
    assert failure["terminal_decision_admitted"] is False
    assert failure["candidate_review_admitted"] is False
    assert failure["stdout"]["bytes"] == len(stdout.encode("utf-8"))
    assert stdout not in output.read_text(encoding="utf-8")


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
        head=TEST_HEAD,
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

    failure = json.loads(output.read_text(encoding="utf-8"))
    assert failure["schema_version"] == "ariadne.egress-failure-receipt.v1"
    assert failure["status"] == ("egress_failed_without_admitted_terminal_decision")
    assert failure["exit_code"] == 0
    assert failure["worktree_identity_unchanged"] is True
    assert failure["decision_contract"] == "schema_constrained_json_v1"
    assert failure["reason_code"] == ("structured_decision_envelope_not_admitted")
    assert failure["terminal_decision_admitted"] is False
    assert failure["candidate_review_admitted"] is False
    assert failure["stdout"]["bytes"] == len(stdout.encode("utf-8"))
    assert stdout not in output.read_text(encoding="utf-8")


def test_structured_decision_rejects_embedded_legacy_terminal_marker() -> None:
    stdout = json.dumps(
        {
            "decision": "pass",
            "review": "Review complete.\nDECISION: pass",
        }
    )

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout)


def test_structured_schema_uses_exact_canonical_review_verdict_enum() -> None:
    schema = ariadne_antigravity.structured_decision_schema()

    assert schema["properties"]["decision"]["enum"] == [
        verdict.value for verdict in ReviewVerdict
    ]
    assert schema["required"] == ["decision", "review"]
    assert set(schema["properties"]) == {"decision", "review"}
    assert schema["additionalProperties"] is False


def test_structured_schema_adds_only_exact_command_results_contract() -> None:
    schema = ariadne_antigravity.structured_decision_schema(_command_manifest())
    command_schema = schema["properties"]["command_results"]

    assert schema["required"] == ["decision", "review", "command_results"]
    assert set(schema["properties"]) == {"decision", "review", "command_results"}
    assert command_schema["minItems"] == command_schema["maxItems"] == 2
    assert command_schema["items"]["required"] == ["id", "argv", "exit_code"]
    assert command_schema["items"]["additionalProperties"] is False
    assert command_schema["items"]["properties"]["id"]["enum"] == [
        "LINT",
        "TEST",
    ]


def test_structured_schema_calls_return_independent_objects() -> None:
    first = ariadne_antigravity.structured_decision_schema(_command_manifest())
    second = ariadne_antigravity.structured_decision_schema(_command_manifest())

    first["required"].append("forged")
    first["properties"]["decision"]["enum"].append("forged")
    first["properties"]["command_results"]["items"]["required"].append("forged")

    assert second["required"] == ["decision", "review", "command_results"]
    assert second["properties"]["decision"]["enum"] == [
        "pass",
        "revision_required",
    ]
    assert second["properties"]["command_results"]["items"]["required"] == [
        "id",
        "argv",
        "exit_code",
    ]


def test_provider_supplied_verdict_assessment_is_rejected() -> None:
    stdout = json.dumps(
        {
            "decision": "pass",
            "review": "No material findings.",
            "verdict_assessment": _assessment("pass"),
        }
    )

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout)


@pytest.mark.parametrize("decision", ["pass", "revision_required"])
def test_exact_decision_produces_exact_locally_derived_assessment(
    decision: str,
) -> None:
    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps({"decision": decision, "review": "  Bounded review complete.  "})
    )

    assert envelope == {
        "decision": decision,
        "review": "Bounded review complete.",
        "verdict_assessment": _assessment(decision),
    }


@pytest.mark.parametrize(
    "wrapper",
    ["structured_output", "result", "response", "output"],
)
def test_supported_wrappers_preserve_the_canonical_envelope(wrapper: str) -> None:
    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps(
            {
                wrapper: {
                    "decision": "pass",
                    "review": "No material findings.",
                },
                "usage": {"input_tokens": 10},
            }
        )
    )

    assert envelope["verdict_assessment"] == _assessment("pass")


@pytest.mark.parametrize(
    "decision",
    ["PASS", " pass", "pass ", True, None, "approved"],
)
def test_non_exact_structured_decisions_are_rejected(decision: object) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps({"decision": decision, "review": "Bounded review."})
        )


@pytest.mark.parametrize(
    "review",
    [
        pytest.param("", id="empty"),
        pytest.param("   ", id="whitespace"),
        pytest.param(None, id="null"),
        pytest.param(7, id="non-string"),
        pytest.param("x" * 40001, id="over-length"),
    ],
)
def test_invalid_structured_review_fields_are_rejected(review: object) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps({"decision": "pass", "review": review})
        )


@pytest.mark.parametrize(
    "review",
    [
        "Review complete.\nDECISION: PASS",
        "## DECISION: PASS",
        "**DECISION: PASS**",
        "| DECISION: PASS |",
        "VERDICT: PASS",
        "DECISION: APPROVED",
        "DECISION: PASS\nDECISION: REVISION_REQUIRED",
        "<!-- DECISION: PASS -->",
        "> DECISION: PASS",
    ],
)
def test_review_text_cannot_supply_marker_authority(review: str) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps({"decision": "pass", "review": review})
        )


def test_ordinary_prose_discussing_a_future_marker_is_admitted() -> None:
    review = "A future external review may emit DECISION: PASS after this tranche."

    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps({"decision": "revision_required", "review": review})
    )

    assert envelope["review"] == review
    assert envelope["verdict_assessment"] == _assessment("revision_required")


def test_no_valid_structured_candidate_is_rejected() -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps({"result": {"decision": "pass"}})
        )


def test_conflicting_direct_and_wrapped_candidates_are_rejected() -> None:
    stdout = json.dumps(
        {
            "decision": "pass",
            "review": "First result.",
            "result": {
                "decision": "revision_required",
                "review": "Second result.",
            },
        }
    )

    with pytest.raises(RuntimeError, match="observed 2"):
        ariadne_antigravity.parse_structured_decision(stdout)


def test_identical_direct_and_wrapped_candidates_collapse_to_one() -> None:
    decision = {"decision": "pass", "review": "One canonical result."}

    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps({**decision, "result": copy.deepcopy(decision)})
    )

    assert envelope["verdict_assessment"] == _assessment("pass")


@pytest.mark.parametrize(
    "stdout, command_manifest",
    [
        pytest.param(
            '{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}',
            None,
            id="root-decision-revision-required-then-pass",
        ),
        pytest.param(
            '{"decision":"pass","decision":"revision_required",'
            '"review":"Bounded review."}',
            None,
            id="root-decision-pass-then-revision-required",
        ),
        pytest.param(
            '{"decision":"pass","review":"First review.","review":"Second review."}',
            None,
            id="root-review",
        ),
        pytest.param(
            '{"structured_output":{"decision":"pass","review":"First."},'
            '"structured_output":{"decision":"pass","review":"Second."}}',
            None,
            id="structured-output-wrapper",
        ),
        pytest.param(
            '{"result":{"decision":"pass","review":"First."},'
            '"result":{"decision":"pass","review":"Second."}}',
            None,
            id="result-wrapper",
        ),
        pytest.param(
            '{"response":{"decision":"pass","review":"First."},'
            '"response":{"decision":"pass","review":"Second."}}',
            None,
            id="response-wrapper",
        ),
        pytest.param(
            '{"output":{"decision":"pass","review":"First."},'
            '"output":{"decision":"pass","review":"Second."}}',
            None,
            id="output-wrapper",
        ),
        pytest.param(
            '{"structured_output":{"decision":"revision_required",'
            '"decision":"pass","review":"Bounded review."}}',
            None,
            id="decision-inside-structured-output",
        ),
        pytest.param(
            '{"result":{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}}',
            None,
            id="decision-inside-result",
        ),
        pytest.param(
            '{"response":{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}}',
            None,
            id="decision-inside-response",
        ),
        pytest.param(
            '{"output":{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}}',
            None,
            id="decision-inside-output",
        ),
        pytest.param(
            '{"decision":"revision_required","review":"Bounded review.",'
            '"command_results":['
            '{"id":"LINT","id":"LINT","argv":'
            '["python","-m","ruff","check","."],"exit_code":0},'
            '{"id":"TEST","argv":["python","-m","pytest","-q"],'
            '"exit_code":0}]}',
            _command_manifest(),
            id="command-result-id",
        ),
        pytest.param(
            '{"decision":"revision_required","review":"Bounded review.",'
            '"command_results":['
            '{"id":"LINT","argv":["python","-m","ruff","check","."],'
            '"argv":["python","-m","ruff","check","."],"exit_code":0},'
            '{"id":"TEST","argv":["python","-m","pytest","-q"],'
            '"exit_code":0}]}',
            _command_manifest(),
            id="command-result-argv",
        ),
        pytest.param(
            '{"decision":"revision_required","review":"Bounded review.",'
            '"command_results":['
            '{"id":"LINT","argv":["python","-m","ruff","check","."],'
            '"exit_code":0,"exit_code":1},'
            '{"id":"TEST","argv":["python","-m","pytest","-q"],'
            '"exit_code":0}]}',
            _command_manifest(),
            id="command-result-exit-code",
        ),
        pytest.param(
            '{"result":{"decision":"pass","review":"Bounded review."},'
            '"usage":{"input_tokens":10,"input_tokens":11}}',
            None,
            id="arbitrary-nested-member",
        ),
        pytest.param(
            r'"{\"decision\":\"revision_required\",'
            r'\"decision\":\"pass\",\"review\":\"Bounded review.\"}"',
            None,
            id="json-string-compatibility-candidate",
        ),
        pytest.param(
            r'{"dec\u0069sion":"pass","decision":"revision_required",'
            r'"review":"Bounded review."}',
            None,
            id="escaped-and-literal-member-name",
        ),
    ],
)
def test_duplicate_json_members_admit_zero_envelopes(
    stdout: str,
    command_manifest: dict[str, object] | None,
) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout, command_manifest)


@pytest.mark.parametrize(
    "stdout",
    [
        pytest.param(
            '{"decision":"revision_required","decision":"pass",'
            '"review":"Bounded review."}',
            id="duplicate-root-decision",
        ),
        pytest.param(
            r'"{\"decision\":\"revision_required\",'
            r'\"decision\":\"pass\",\"review\":\"Bounded review.\"}"',
            id="duplicate-json-string-candidate",
        ),
    ],
)
def test_duplicate_json_worker_failure_is_digest_only_and_main_returns_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout: str,
) -> None:
    packet, output, orchestrator_receipt = _mock_completed_worker(
        tmp_path,
        monkeypatch,
        stdout=stdout,
    )
    monkeypatch.setattr(
        ariadne_antigravity.sys,
        "argv",
        [
            "ariadne_antigravity.py",
            "--packet",
            str(packet),
            "--cwd",
            str(tmp_path),
            "--output",
            str(output),
            "--orchestrator-receipt",
            str(orchestrator_receipt),
            "--model",
            "gemini-3.7-flash-high",
        ],
    )

    assert ariadne_antigravity.main() == 2

    rendered_failure = output.read_text(encoding="utf-8")
    failure = json.loads(rendered_failure)
    assert failure["schema_version"] == "ariadne.egress-failure-receipt.v1"
    assert failure["status"] == "egress_failed_without_admitted_terminal_decision"
    assert failure["decision_contract"] == "schema_constrained_json_v1"
    assert failure["reason_code"] == "structured_decision_envelope_not_admitted"
    assert failure["exit_code"] == 0
    assert failure["terminal_decision_admitted"] is False
    assert failure["candidate_review_admitted"] is False
    assert failure["stdout"]["bytes"] == len(stdout.encode("utf-8"))
    assert set(failure["stdout"]) == {"bytes", "sha256", "empty"}
    assert stdout not in rendered_failure


@pytest.mark.parametrize(
    "direct_decision, wrapped_decision",
    [
        ("revision_required", "pass"),
        ("pass", "revision_required"),
    ],
)
def test_direct_wrapper_conflict_with_metadata_rejects_the_whole_output(
    direct_decision: str,
    wrapped_decision: str,
) -> None:
    stdout = json.dumps(
        {
            "decision": direct_decision,
            "review": "Direct decision.",
            "result": {
                "decision": wrapped_decision,
                "review": "Wrapped decision.",
            },
            "usage": {"input_tokens": 10},
        }
    )

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(stdout)


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {
                "decision": "pass",
                "review": "Direct decision.",
                "usage": {"input_tokens": 10},
            },
            id="direct-metadata-without-wrapper",
        ),
        pytest.param(
            {
                "decision": "pass",
                "review": "One canonical result.",
                "result": {
                    "decision": "pass",
                    "review": "One canonical result.",
                },
                "usage": {"input_tokens": 10},
            },
            id="direct-identical-wrapper-and-metadata",
        ),
        pytest.param(
            {
                "decision": "pass",
                "review": "Direct decision.",
                "response": {
                    "decision": "pass",
                    "review": "Wrapped decision.",
                },
                "usage": {"input_tokens": 10},
            },
            id="direct-another-wrapper-and-metadata",
        ),
    ],
)
def test_complete_direct_candidate_with_unknown_metadata_is_rejected(
    payload: dict[str, object],
) -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(json.dumps(payload))


def test_arbitrary_nested_and_unlisted_wrapper_keys_are_not_searched() -> None:
    decision = {"decision": "pass", "review": "Nested result."}

    for value in ({"payload": decision}, {"result": {"payload": decision}}):
        with pytest.raises(RuntimeError, match="observed 0"):
            ariadne_antigravity.parse_structured_decision(json.dumps(value))


def test_pass_with_exact_all_zero_command_results_is_admitted() -> None:
    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps(
            {
                "decision": "pass",
                "review": "Both checks passed.",
                "command_results": _command_results(0, 0),
            }
        ),
        _command_manifest(),
    )

    assert envelope["command_results"] == _command_results(0, 0)
    assert envelope["verdict_assessment"]["integration_authorized"] is True


def test_pass_with_nonzero_command_result_is_rejected() -> None:
    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps(
                {
                    "decision": "pass",
                    "review": "One check failed.",
                    "command_results": _command_results(0, 1),
                }
            ),
            _command_manifest(),
        )


def test_revision_required_with_nonzero_command_result_is_non_authorizing() -> None:
    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps(
            {
                "decision": "revision_required",
                "review": "One check failed.",
                "command_results": _command_results(0, 1),
            }
        ),
        _command_manifest(),
    )

    assert envelope["command_results"] == _command_results(0, 1)
    assert envelope["verdict_assessment"] == _assessment("revision_required")


@pytest.mark.parametrize(
    "mutation",
    ["id", "argv", "order", "length", "container_type", "exit_type", "extra"],
)
def test_malformed_or_substituted_command_results_are_rejected(
    mutation: str,
) -> None:
    results: object = _command_results(0, 0)
    assert isinstance(results, list)
    if mutation == "id":
        results[0]["id"] = "OTHER"
    elif mutation == "argv":
        results[0]["argv"] = ["python", "-m", "ruff", "format", "."]
    elif mutation == "order":
        results.reverse()
    elif mutation == "length":
        results.pop()
    elif mutation == "container_type":
        results = {"results": results}
    elif mutation == "exit_type":
        results[0]["exit_code"] = True
    else:
        results[0]["extra"] = "forbidden"

    with pytest.raises(RuntimeError, match="observed 0"):
        ariadne_antigravity.parse_structured_decision(
            json.dumps(
                {
                    "decision": "revision_required",
                    "review": "Bounded check result.",
                    "command_results": results,
                }
            ),
            _command_manifest(),
        )


def test_command_admission_receives_only_the_canonical_decision_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[str] = []

    def _admit(**kwargs):
        observed.append(kwargs["decision"])
        return kwargs["results"]

    monkeypatch.setattr(ariadne_antigravity, "admit_command_results", _admit)

    envelope = ariadne_antigravity.parse_structured_decision(
        json.dumps(
            {
                "decision": "revision_required",
                "review": "Bounded check result.",
                "command_results": _command_results(0, 1),
            }
        ),
        _command_manifest(),
    )

    assert observed == ["revision_required"]
    assert envelope["decision"] == "revision_required"


def test_run_worker_revision_required_is_completed_but_non_authorizing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, output, orchestrator_receipt = _mock_completed_worker(
        tmp_path,
        monkeypatch,
        stdout=json.dumps(
            {
                "decision": "revision_required",
                "review": "A bounded correction is required.",
            }
        ),
    )

    receipt = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=tmp_path,
        output_path=output,
        orchestrator_receipt_path=orchestrator_receipt,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )

    assert receipt["status"] == "completed"
    assert receipt["decision"] == "revision_required"
    assert receipt["decision_envelope"]["verdict_assessment"] == _assessment(
        "revision_required"
    )


def test_legacy_text_mode_remains_transport_compatibility_without_assessment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, output, orchestrator_receipt = _mock_completed_worker(
        tmp_path,
        monkeypatch,
        stdout="Legacy review text.\nDECISION: pass",
    )

    receipt = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=tmp_path,
        output_path=output,
        orchestrator_receipt_path=orchestrator_receipt,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
        structured_decision=False,
    )

    assert receipt["status"] == "completed"
    assert receipt["decision_contract"] == "legacy_terminal_line_v1"
    assert "decision_envelope" not in receipt
    assert "verdict_assessment" not in receipt


def test_current_programme_admits_only_the_exact_g1a3_r1_task_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)
    manifest = build_task_manifest(Path(__file__).resolve().parents[1])
    decision = programme_admission.evaluate_programme_admission(
        repo_root=Path(__file__).resolve().parents[1],
        manifest=manifest,
        entrypoint="recovery_preflight",
    )

    assert decision.admitted is True
    assert set(manifest["allowed_path_roots"]) == {
        "scripts/agent_worktrees.py",
        "scripts/ariadne_antigravity.py",
        "tests/test_agent_worktrees.py",
        "tests/test_ariadne_antigravity.py",
    }
    for widened_paths in (
        ["scripts/ariadne_antigravity.py"],
        [*manifest["allowed_path_roots"], "scripts/forbidden.py"],
    ):
        widened = dict(manifest)
        widened["allowed_path_roots"] = widened_paths
        rejected = programme_admission.evaluate_programme_admission(
            repo_root=Path(__file__).resolve().parents[1],
            manifest=widened,
            entrypoint="recovery_preflight",
        )
        assert rejected.admitted is False


def test_current_programme_denies_provider_invocation_and_later_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(trusted_git, "attest_repository", _REAL_ATTEST_REPOSITORY)
    monkeypatch.setattr(trusted_git, "run_git", _REAL_RUN_GIT)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _REAL_RUN_GIT_BYTES)
    root = Path(__file__).resolve().parents[1]
    manifest = build_task_manifest(root)
    provider = programme_admission.evaluate_programme_admission(
        repo_root=root,
        manifest=manifest,
        entrypoint="provider_invocation",
    )
    policy = programme_admission.load_programme_policy(root)
    profile = policy.overlay["profiles"][programme_admission.G1A3_R1_ACTIVE_PROFILE]

    assert provider.admitted is False
    assert provider.reason_codes == ["provider_invocation_closed_in_active_profile"]
    assert programme_admission.g1a3_review_producer_contract_reasons(root) == []
    assert programme_admission.g1a3_integration_contract_reasons(root) == []
    assert set(profile["allowed_paths"]) == {
        "scripts/agent_worktrees.py",
        "scripts/ariadne_antigravity.py",
        "tests/test_agent_worktrees.py",
        "tests/test_ariadne_antigravity.py",
    }
    assert {
        "g1b_work",
        "integration",
        "product_behavior_change",
        "deployment",
        "pages",
        "protected_ref_movement",
        "provider_invocation",
    }.issubset(profile["forbidden_effects"])
