import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import orchestration_harness.programme_admission as pa
import orchestration_harness.pinned_programme_gatekeeper as pg
import scripts.raisa_ariadne_gatekeeper_bootstrap as bootstrap
from scripts.raisa_ariadne_recovery_preflight import build_task_manifest
from tests.test_programme_admission import (
    _build_g1a3_r0_transition_repository,
    _build_g1a3_transition_repository,
    _git,
    _write_json,
    _write_yaml,
)


ROOT = Path(__file__).resolve().parents[1]


_TRUSTED_GIT_OVERRIDES = (
    "-c",
    "core.fsmonitor=false",
    "-c",
    "core.ignoreStat=false",
)


def test_retained_g08_recovery_push_binding_tracks_its_external_review() -> None:
    policy = pa.load_programme_policy(ROOT)
    state = policy.state
    correction = state[pg.G0_CORRECTION_STATE_KEY]
    correction_review = next(
        review
        for review in state["g0_acceptance"]["external_review_history"]
        if review["reviewed_commit"] == correction["authorized_parent_commit"]
        and review["reviewed_tree"] == correction[pg.G0_REVIEWED_TREE_FIELD]
    )

    assert pg.G0_CORRECTION_STATE_KEY == "g0_8_correction"
    assert pg.G0_REVIEWED_TREE_FIELD == "reviewed_g0_7_tree"
    assert (
        correction_review["reviewed_commit"] == correction["authorized_parent_commit"]
    )
    assert correction_review["reviewed_tree"] == correction[pg.G0_REVIEWED_TREE_FIELD]
    assert (
        correction_review["blocking_finding_count"]
        == correction["review_finding_count"]
    )


def _new_fsmonitor_repository(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "fsmonitor-repository"
    root.mkdir()
    _git(root, "init", "-b", "fsmonitor-test")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G0.8 Fsmonitor Tests")
    _git(root, "config", "core.autocrlf", "false")
    tracked = root / "tracked.py"
    safe = root / "safe.py"
    tracked.write_text("TRACKED = 'reviewed'\n", encoding="utf-8")
    safe.write_text("SAFE = True\n", encoding="utf-8")
    _git(root, "add", "tracked.py", "safe.py")
    _git(root, "commit", "-m", "seed fsmonitor repository")
    hook = tmp_path / "external-fsmonitor-hook.sh"
    hook.write_bytes(b"#!/bin/sh\nprintf 'g0-8-token\\0'\n")
    hook.chmod(hook.stat().st_mode | 0o111)
    return root, tracked, hook


def _prime_external_fsmonitor(root: Path, hook: Path) -> None:
    _git(root, "config", "core.fsmonitor", hook.as_posix())
    _git(root, "config", "core.fsmonitorHookVersion", "2")
    assert _git(root, "status", "--porcelain") == ""


def _hide_tracked_modification(root: Path, tracked: Path, hook: Path) -> None:
    _prime_external_fsmonitor(root, hook)
    tracked.write_text("TRACKED = 'unreviewed'\n", encoding="utf-8")
    assert _git(root, "status", "--porcelain") == ""
    assert _git(root, "diff", "--name-only") == ""
    assert _git(root, "ls-files", "-f", "--", tracked.name).startswith("h ")
    assert tracked.name in _git(
        root,
        *_TRUSTED_GIT_OVERRIDES,
        "status",
        "--porcelain",
    )


def test_parent_fsmonitor_bypass_is_reproduced_with_an_external_hook(
    tmp_path: Path,
) -> None:
    root, tracked, hook = _new_fsmonitor_repository(tmp_path)

    _hide_tracked_modification(root, tracked, hook)


def test_trusted_repository_attestation_rejects_configured_fsmonitor(
    tmp_path: Path,
) -> None:
    root, tracked, hook = _new_fsmonitor_repository(tmp_path)
    _hide_tracked_modification(root, tracked, hook)

    with pytest.raises(
        pa.trusted_git.TrustedGitError,
        match="trusted_git_configuration_forbidden",
    ):
        pa.trusted_git.attest_repository(
            root,
            attested_paths=["safe.py"],
            expected_commit=_git(root, "rev-parse", "HEAD"),
        )


def test_trusted_repository_attestation_rejects_fsmonitor_valid_index_entries(
    tmp_path: Path,
) -> None:
    root, tracked, hook = _new_fsmonitor_repository(tmp_path)
    _prime_external_fsmonitor(root, hook)
    _git(root, "update-index", "--fsmonitor-valid", tracked.name)
    assert _git(root, "ls-files", "-f", "--", tracked.name).startswith("h ")

    with pytest.raises(
        pa.trusted_git.TrustedGitError,
        match="trusted_git_configuration_forbidden",
    ):
        pa.trusted_git.attest_repository(
            root,
            attested_paths=["safe.py"],
            expected_commit=_git(root, "rev-parse", "HEAD"),
        )


@pytest.mark.parametrize(
    "scope,key",
    [
        ("--local", "core.fsmonitor"),
        ("--local", "core.fsmonitorHookVersion"),
        ("--local", "core.ignoreStat"),
        ("--worktree", "core.fsmonitor"),
        ("--worktree", "core.fsmonitorHookVersion"),
        ("--worktree", "core.ignoreStat"),
    ],
)
def test_trusted_repository_configuration_allows_only_explicit_false(
    tmp_path: Path, scope: str, key: str
) -> None:
    root, _tracked, _hook = _new_fsmonitor_repository(tmp_path)
    if scope == "--worktree":
        _git(root, "config", "extensions.worktreeConfig", "true")
    _git(root, "config", scope, key, "false")

    identity = pa.trusted_git.attest_repository(
        root,
        attested_paths=["safe.py"],
        expected_commit=_git(root, "rev-parse", "HEAD"),
    )

    assert identity["command_overrides"] == [
        "core.fsmonitor=false",
        "core.ignoreStat=false",
    ]
    assert identity["index_visibility"]["fsmonitor_valid_count"] == 0
    observed = identity["repository_configuration"][scope[2:]][key]
    assert observed["values"] == ["false"]
    assert observed["admitted"] is True


def test_clean_trusted_git_identity_records_closed_visibility_controls(
    tmp_path: Path,
) -> None:
    root, _tracked, _hook = _new_fsmonitor_repository(tmp_path)

    identity = pa.trusted_git.attest_repository(
        root,
        attested_paths=["safe.py"],
        expected_commit=_git(root, "rev-parse", "HEAD"),
    )

    assert identity["command_overrides"] == [
        "core.fsmonitor=false",
        "core.ignoreStat=false",
    ]
    assert identity["index_visibility"]["fsmonitor_valid_count"] == 0
    assert (
        identity["repository_configuration"]["worktree_configuration_active"] is False
    )
    for scope in ("local", "worktree"):
        for key in (
            "core.fsmonitor",
            "core.fsmonitorHookVersion",
            "core.ignoreStat",
        ):
            assert identity["repository_configuration"][scope][key] == {
                "values": [],
                "normalised_boolean_values": [],
                "admitted": True,
            }


def test_bootstrap_and_imported_trusted_runner_use_identical_git_overrides() -> None:
    assert bootstrap._TRUSTED_GIT_COMMAND_OVERRIDES == (
        pa.trusted_git.TRUSTED_GIT_COMMAND_OVERRIDES
    )
    assert bootstrap._SOURCE_MODULES == pg.PINNED_SOURCE_PATHS


@pytest.mark.parametrize(
    "key,value",
    [
        ("core.fsmonitor", "true"),
        ("core.fsmonitor", "../external-hook"),
        ("core.fsmonitorHookVersion", "2"),
        ("core.ignoreStat", "definitely-not-a-boolean"),
    ],
)
def test_trusted_repository_configuration_rejects_nonfalse_or_malformed_values(
    tmp_path: Path, key: str, value: str
) -> None:
    root, _tracked, _hook = _new_fsmonitor_repository(tmp_path)
    expected_commit = _git(root, "rev-parse", "HEAD")
    _git(root, "config", "--local", key, value)

    with pytest.raises(
        pa.trusted_git.TrustedGitError,
        match="trusted_git_configuration_forbidden",
    ):
        pa.trusted_git.attest_repository(
            root,
            attested_paths=["safe.py"],
            expected_commit=expected_commit,
        )


def test_trusted_repository_configuration_rejects_mixed_duplicate_values(
    tmp_path: Path,
) -> None:
    root, _tracked, _hook = _new_fsmonitor_repository(tmp_path)
    _git(root, "config", "--local", "--add", "core.fsmonitor", "false")
    _git(root, "config", "--local", "--add", "core.fsmonitor", "true")

    with pytest.raises(
        pa.trusted_git.TrustedGitError,
        match="trusted_git_configuration_forbidden",
    ):
        pa.trusted_git.attest_repository(
            root,
            attested_paths=["safe.py"],
            expected_commit=_git(root, "rev-parse", "HEAD"),
        )


def test_trusted_repository_configuration_rejects_included_local_value(
    tmp_path: Path,
) -> None:
    root, _tracked, hook = _new_fsmonitor_repository(tmp_path)
    included = tmp_path / "included-git-config"
    included.write_text(
        f"[core]\n\tfsmonitor = {hook.as_posix()}\n",
        encoding="utf-8",
    )
    _git(root, "config", "--local", "include.path", included.as_posix())

    with pytest.raises(
        pa.trusted_git.TrustedGitError,
        match="trusted_git_configuration_forbidden",
    ):
        pa.trusted_git.attest_repository(
            root,
            attested_paths=["safe.py"],
            expected_commit=_git(root, "rev-parse", "HEAD"),
        )


def _manifest_path(root: Path, manifest: dict, name: str) -> Path:
    path = root.parent / name
    _write_json(path, manifest)
    return path


def _gatekeeper_cli(
    *,
    gatekeeper: Path,
    target: Path,
    manifest_path: Path,
    phase: str,
) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(gatekeeper / "scripts/raisa_ariadne_gatekeeper_bootstrap.py"),
            "--expected-source-commit",
            _git(gatekeeper, "rev-parse", "HEAD"),
            "--expected-source-tree",
            _git(gatekeeper, "rev-parse", "HEAD^{tree}"),
            "evaluate",
            "--target-repo",
            str(target),
            "--task-manifest",
            str(manifest_path),
            "--entrypoint",
            "task_branch_push" if phase != "development" else "task_branch_commit",
            "--phase",
            phase,
            "--format",
            "json",
        ],
        cwd=gatekeeper,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert completed.stdout.strip(), completed.stderr
    return completed, json.loads(completed.stdout)


def _gatekeeper_operation(
    *,
    operation: str,
    gatekeeper: Path,
    target: Path,
    manifest_path: Path,
    receipt_directory: Path,
    message: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict]:
    receipt_directory.mkdir(parents=True, exist_ok=True)
    argv = [
        sys.executable,
        "-I",
        "-B",
        str(gatekeeper / "scripts/raisa_ariadne_gatekeeper_bootstrap.py"),
        "--expected-source-commit",
        _git(gatekeeper, "rev-parse", "HEAD"),
        "--expected-source-tree",
        _git(gatekeeper, "rev-parse", "HEAD^{tree}"),
        operation,
        "--target-repo",
        str(target),
        "--task-manifest",
        str(manifest_path),
        "--receipt-directory",
        str(receipt_directory),
        "--format",
        "json",
    ]
    if message is not None:
        argv.extend(["--message", message])
    completed = subprocess.run(
        argv,
        cwd=target,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert completed.stdout.strip(), completed.stderr
    return completed, json.loads(completed.stdout)


def _transition_fixture(tmp_path: Path) -> tuple[Path, Path, dict]:
    target, gatekeeper, transition_manifest, _enablement = (
        _build_g1a3_transition_repository(tmp_path)
    )
    _git(target, "commit", "--no-verify", "-m", "synthetic G1A.3 state transition")
    return target, gatekeeper, transition_manifest


def test_real_bare_origin_transition_compatibility_lifecycle_passes(
    tmp_path: Path,
) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    transition_manifest_path = _manifest_path(
        target, transition_manifest, "transition-manifest.json"
    )

    pre_transition, pre_transition_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        phase="pre-push",
    )
    assert pre_transition.returncode == 0
    assert pre_transition_payload["admitted"] is True
    transition_binding = pre_transition_payload["operation_binding"]
    transition_push, transition_receipt = _gatekeeper_operation(
        operation="push",
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        receipt_directory=target.parent / "transition-receipts",
    )
    assert transition_push.returncode == 0
    assert transition_receipt["operation"] == "exact_sha_push"
    assert transition_receipt["post_push_decision_admitted"] is True
    assert (
        transition_receipt["remote_identity"]["normalized_push_url"]
        == (transition_binding["explicit_destination"])
    )
    post_transition, post_transition_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        phase="post-push",
    )
    assert post_transition.returncode == 0
    assert post_transition_payload["admitted"] is True

    activation_manifest = build_task_manifest(target)
    activation_scope = pa.evaluate_committed_scope(
        repo_root=target, manifest=activation_manifest, phase="development"
    )
    assert activation_scope.admitted is True
    assert activation_scope.target_cleanliness["activation_clean"] is True
    assert activation_scope.target_cleanliness["preserved_legacy_worktree"] is False

    policy = pa.load_programme_policy(target)
    dynamic_paths = {
        f"{pa.G1A3_TRANSITION_REVIEW_ROOT}/{transition_manifest['enablement_review_id']}.json",
        f"{pa.SUBGATE_TRANSITION_ARTIFACT_ROOT}/{transition_manifest['transition_id']}.json",
    }
    assert dynamic_paths.issubset(policy.full_range_allowed_paths)
    assert all("*" not in path for path in policy.full_range_allowed_paths)

    product_path = target / "app/main.py"
    product_path.parent.mkdir(parents=True, exist_ok=True)
    product_path.write_text("# unrelated product drift\n", encoding="utf-8")
    product_manifest = activation_manifest
    product_manifest_path = _manifest_path(
        target, product_manifest, "product-drift-manifest.json"
    )
    for phase in ("development", "pre-push", "post-push"):
        completed, payload = _gatekeeper_cli(
            gatekeeper=gatekeeper,
            target=target,
            manifest_path=product_manifest_path,
            phase=phase,
        )
        assert completed.returncode == 2
        assert payload["admitted"] is False
        assert "scope_tranche_path_outside_policy" in payload["reason_codes"]


def test_real_g1a3_transition_and_exact_consumer_lifecycle_passes(
    tmp_path: Path,
) -> None:
    target, gatekeeper, transition_manifest, enablement = (
        _build_g1a3_transition_repository(tmp_path)
    )
    transition_manifest_path = _manifest_path(
        target, transition_manifest, "g1a3-transition-manifest.json"
    )

    development, development_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        phase="development",
    )
    assert development.returncode == 0, development_payload
    assert development_payload["admitted"] is True
    assert development_payload["gatekeeper_commit"] == enablement
    assert set(development_payload["scope_decision"]["changed_paths"]) >= set(
        transition_manifest["allowed_transition_paths"]
    )

    transition_commit, transition_commit_receipt = _gatekeeper_operation(
        operation="commit",
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        receipt_directory=tmp_path / "g1a3-transition-commit-receipts",
        message="synthetic state-only G1A.2 to G1A.3 transition",
    )
    assert transition_commit.returncode == 0, transition_commit_receipt
    transition_sha = transition_commit_receipt["result_sha"]
    assert (
        _git(target, "rev-list", "--parents", "-n", "1", transition_sha).split()[1]
        == enablement
    )

    pre_transition, pre_transition_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        phase="pre-push",
    )
    assert pre_transition.returncode == 0, pre_transition_payload
    transition_push, transition_push_receipt = _gatekeeper_operation(
        operation="push",
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        receipt_directory=tmp_path / "g1a3-transition-push-receipts",
    )
    assert transition_push.returncode == 0, transition_push_receipt
    assert transition_push_receipt["post_push_readback_sha"] == transition_sha
    post_transition, post_transition_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        phase="post-push",
    )
    assert post_transition.returncode == 0, post_transition_payload
    assert post_transition_payload["admitted"] is True

    policy = pa.load_programme_policy(target)
    assert policy.state["current_gate"] == "G1A.3"
    assert policy.overlay["active_profile"] == pa.G1A3_ACTIVE_PROFILE
    assert (
        policy.state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "provider_invocation_authorized"
        ]
        is False
    )
    assert (
        policy.state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "integration_execution_authorized"
        ]
        is False
    )
    exact_manifest = build_task_manifest(target)
    narrowed_manifest = dict(exact_manifest)
    narrowed_manifest["allowed_path_roots"] = ["scripts/agent_worktrees.py"]
    narrowed = pa.evaluate_programme_admission(
        repo_root=target,
        manifest=narrowed_manifest,
        entrypoint="recovery_preflight",
    )
    assert narrowed.admitted is False
    assert narrowed.reason_codes == ["g1a_3_task_manifest_paths_not_exact"]
    reopened_manifest = dict(exact_manifest)
    reopened_manifest["allowed_path_roots"] = [
        *exact_manifest["allowed_path_roots"],
        "scripts/ariadne_antigravity.py",
    ]
    reopened = pa.evaluate_programme_admission(
        repo_root=target,
        manifest=reopened_manifest,
        entrypoint="recovery_preflight",
    )
    assert reopened.admitted is False
    assert reopened.reason_codes == ["task_manifest_path_outside_policy"]

    candidate_gatekeeper_path = (
        target / "orchestration_harness/pinned_programme_gatekeeper.py"
    )
    candidate_gatekeeper_bytes = candidate_gatekeeper_path.read_bytes()
    candidate_gatekeeper_path.write_text(
        "print('FORGED_G1A3_CANDIDATE_ACCEPT')\n", encoding="utf-8"
    )
    _git(
        target,
        "add",
        "--",
        "orchestration_harness/pinned_programme_gatekeeper.py",
    )
    forged_manifest = build_task_manifest(target)
    forged_manifest_path = _manifest_path(
        target, forged_manifest, "g1a3-forged-gatekeeper-manifest.json"
    )
    forged, forged_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=forged_manifest_path,
        phase="development",
    )
    assert forged.returncode == 2
    assert forged_payload["admitted"] is False
    assert "FORGED_G1A3_CANDIDATE_ACCEPT" not in forged.stdout
    candidate_gatekeeper_path.write_bytes(candidate_gatekeeper_bytes)
    _git(
        target,
        "add",
        "--",
        "orchestration_harness/pinned_programme_gatekeeper.py",
    )

    consumer_path = target / "scripts/agent_worktrees.py"
    consumer = consumer_path.read_text(encoding="utf-8")
    consumer_path.write_text(
        consumer.replace(
            "def record_integration(args: argparse.Namespace) -> None:\n"
            '    _require_command_admission(args, entrypoint="integration")\n',
            "def record_integration(args: argparse.Namespace) -> None:\n"
            '    _require_command_admission(args, entrypoint="integration")\n'
            '    """Consume only validated immutable integration authority."""\n',
            1,
        ),
        encoding="utf-8",
    )
    assert consumer_path.read_text(encoding="utf-8") != consumer
    consumer_test_path = target / "tests/test_agent_worktrees.py"
    consumer_test_path.write_text(
        consumer_test_path.read_text(encoding="utf-8")
        + "\n\ndef test_synthetic_g1a3_consumer_contract_marker():\n"
        + "    assert 'ariadne.worker_receipt.v1'.startswith('ariadne.')\n",
        encoding="utf-8",
    )
    _git(
        target,
        "add",
        "--",
        "scripts/agent_worktrees.py",
        "tests/test_agent_worktrees.py",
    )
    task_manifest = build_task_manifest(target)
    assert set(task_manifest["allowed_path_roots"]) == pa.G1A3_ALLOWED_PATHS
    assert set(task_manifest["intended_side_effect_classes"]) == (
        pa.G1A3_ALLOWED_EFFECTS
    )
    provider_denial = pa.evaluate_programme_admission(
        repo_root=target,
        manifest=task_manifest,
        entrypoint="provider_invocation",
    )
    assert provider_denial.admitted is False
    assert provider_denial.reason_codes == [
        "provider_invocation_closed_in_active_profile"
    ]
    integration_denial = pa.evaluate_programme_admission(
        repo_root=target,
        manifest=task_manifest,
        entrypoint="integration",
    )
    assert integration_denial.admitted is False
    assert integration_denial.reason_codes == ["integration_closed_in_active_profile"]
    assert pa.g1a3_integration_contract_reasons(target) == []

    local_decision = pa.evaluate_programme_operation_admission(
        repo_root=target,
        manifest=task_manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert local_decision.admitted is False
    assert local_decision.reason_codes == ["pinned_gatekeeper_required"]
    task_manifest_path = _manifest_path(
        target, task_manifest, "g1a3-development-manifest.json"
    )
    task_development, task_development_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=task_manifest_path,
        phase="development",
    )
    assert task_development.returncode == 0, task_development_payload
    assert task_development_payload["admitted"] is True

    task_commit, task_commit_receipt = _gatekeeper_operation(
        operation="commit",
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=task_manifest_path,
        receipt_directory=tmp_path / "g1a3-task-commit-receipts",
        message="synthetic bounded G1A.3 consumer",
    )
    assert task_commit.returncode == 0, task_commit_receipt
    task_sha = task_commit_receipt["result_sha"]
    task_manifest = build_task_manifest(target)
    task_manifest_path = _manifest_path(
        target, task_manifest, "g1a3-pre-push-manifest.json"
    )
    pre_task, pre_task_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=task_manifest_path,
        phase="pre-push",
    )
    assert pre_task.returncode == 0, pre_task_payload
    task_push, task_push_receipt = _gatekeeper_operation(
        operation="push",
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=task_manifest_path,
        receipt_directory=tmp_path / "g1a3-task-push-receipts",
    )
    assert task_push.returncode == 0, task_push_receipt
    assert task_push_receipt["post_push_readback_sha"] == task_sha
    post_task, post_task_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=task_manifest_path,
        phase="post-push",
    )
    assert post_task.returncode == 0, post_task_payload
    assert post_task_payload["admitted"] is True
    assert (
        _git(
            target,
            "ls-remote",
            "--refs",
            str(tmp_path / "g1a3-origin.git"),
            "refs/heads/codex/raisa-ariadne-recovery-g0",
        ).split()[0]
        == task_sha
    )


@pytest.mark.parametrize(
    "relative_path",
    [
        "orchestration_harness/programme_admission.py",
        "scripts/raisa_ariadne_pinned_gatekeeper.py",
        "orchestration/harness_settings/programme_recovery.yaml",
        "orchestration/programme/current-state.json",
        "orchestration/programme/gates.yaml",
        "orchestration/continuity/ariadne-active-operation-latch/current.json",
    ],
)
def test_g1a_candidate_cannot_modify_reference_monitor_or_state(
    tmp_path: Path, relative_path: str
) -> None:
    target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(target)
    path = target / relative_path
    path.write_text(
        path.read_text(encoding="utf-8") + "\n# forbidden drift\n", encoding="utf-8"
    )
    manifest_path = _manifest_path(target, manifest, "candidate-manifest.json")
    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )
    assert completed.returncode == 2
    assert payload["admitted"] is False


def test_candidate_local_gatekeeper_replacement_is_ignored(tmp_path: Path) -> None:
    target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    candidate_cli = target / "scripts/raisa_ariadne_pinned_gatekeeper.py"
    candidate_cli.write_text("print('FORGED_CANDIDATE_ACCEPT')\n", encoding="utf-8")
    manifest = build_task_manifest(target)
    manifest_path = _manifest_path(target, manifest, "candidate-manifest.json")

    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )
    assert completed.returncode == 2
    assert payload["admitted"] is False
    assert "FORGED_CANDIDATE_ACCEPT" not in completed.stdout


def test_dirty_or_wrongly_pinned_gatekeeper_fails_closed(tmp_path: Path) -> None:
    target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(target)
    manifest_path = _manifest_path(target, manifest, "candidate-manifest.json")

    agents = gatekeeper / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8") + "\n# dirty\n", encoding="utf-8"
    )
    dirty, dirty_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )
    assert dirty.returncode == 2
    assert "gatekeeper_bootstrap_source_not_clean" in dirty_payload["reason_codes"]

    wrong = tmp_path / "wrong-gatekeeper"
    _git(
        target,
        "worktree",
        "add",
        "--detach",
        str(wrong),
        _git(target, "rev-parse", "HEAD"),
    )
    wrongly_pinned, wrong_payload = _gatekeeper_cli(
        gatekeeper=wrong,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )
    assert wrongly_pinned.returncode == 2
    assert (
        "gatekeeper_source_not_g1a3_transition_pinned"
        in (wrong_payload["reason_codes"])
    )


def test_preserved_legacy_worktree_cannot_use_unpinned_gatekeeper(
    tmp_path: Path,
) -> None:
    _target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = {
        "schema_version": pa.TASK_MANIFEST_VERSION,
        "task_id": "preserved-legacy-probe",
        "task_class": pa.G1A3_TASK_CLASS,
        "programme_gate": "G1A.3",
        "objective": "Prove the preserved legacy target remains closed.",
        "base_commit": _git(ROOT, "rev-parse", "HEAD"),
        "candidate_or_current_head": _git(ROOT, "rev-parse", "HEAD"),
        "allowed_path_roots": sorted(pa.G1A3_ALLOWED_PATHS),
        "intended_side_effect_classes": sorted(pa.G1A3_ALLOWED_EFFECTS),
        "forbidden_side_effect_classes": sorted(pa.G1A_FORBIDDEN_EFFECTS),
        "state_digest": pa.load_programme_policy(ROOT).state_digest,
        "policy_digest": pa.load_programme_policy(ROOT).policy_digest,
    }
    manifest_path = tmp_path / "legacy-target-manifest.json"
    _write_json(manifest_path, manifest)

    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=ROOT,
        manifest_path=manifest_path,
        phase="development",
    )

    assert completed.returncode == 2
    assert "gatekeeper_source_not_transition_pinned" in payload["reason_codes"]


def test_operation_binding_revalidation_rejects_post_admission_index_drift(
    tmp_path: Path,
) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    transition_push = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )
    assert transition_push.admitted is True
    subprocess.run(
        pg.exact_push_argv(transition_push),
        cwd=target,
        check=True,
        capture_output=True,
        text=True,
    )
    consumer = target / "scripts/agent_worktrees.py"
    consumer.write_text(
        consumer.read_text(encoding="utf-8").replace(
            '    _require_command_admission(args, entrypoint="integration")\n',
            '    _require_command_admission(args, entrypoint="integration")\n'
            '    """Synthetic receipt consumer."""\n',
            1,
        ),
        encoding="utf-8",
    )
    _git(target, "add", "scripts/agent_worktrees.py")
    manifest = build_task_manifest(target)

    prior = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert prior.admitted is True

    consumer.write_text(
        consumer.read_text(encoding="utf-8").replace(
            "Synthetic receipt consumer.", "Changed after admission."
        ),
        encoding="utf-8",
    )
    _git(target, "add", "scripts/agent_worktrees.py")
    fresh = pg.revalidate_pinned_operation_binding(
        prior_decision=prior,
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=manifest,
    )

    assert fresh.admitted is False
    assert "gatekeeper_operation_binding_drift" in fresh.reason_codes


def test_operation_binding_revalidation_rejects_remote_drift(tmp_path: Path) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    admitted = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )
    assert admitted.admitted is True
    fake = tmp_path / "remote-drift.git"
    fake.mkdir()
    _git(fake, "init", "--bare")
    _git(target, "remote", "set-url", "origin", str(fake))

    fresh = pg.revalidate_pinned_operation_binding(
        prior_decision=admitted,
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
    )

    assert fresh.admitted is False
    assert "gatekeeper_operation_binding_drift" in fresh.reason_codes
    assert any(code.startswith("remote_identity") for code in fresh.reason_codes)


@pytest.mark.parametrize(
    "relative_path",
    [
        ".env",
        "sitecustomize.py",
        "usercustomize.py",
        "module.pyc",
        "__pycache__/module.pyc",
        ".pytest_cache/v/cache/nodeids",
        ".venv/Lib/site-packages/runtime.py",
    ],
)
def test_isolated_bootstrap_rejects_ignored_gatekeeper_material_without_execution(
    tmp_path: Path, relative_path: str
) -> None:
    target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(target)
    manifest_path = _manifest_path(target, manifest, "ignored-source-manifest.json")
    git_exclude = Path(_git(gatekeeper, "rev-parse", "--git-path", "info/exclude"))
    if not git_exclude.is_absolute():
        git_exclude = gatekeeper / git_exclude
    git_exclude.parent.mkdir(parents=True, exist_ok=True)
    git_exclude.write_text(f"/{relative_path}\n", encoding="utf-8")
    material = gatekeeper / relative_path
    material.parent.mkdir(parents=True, exist_ok=True)
    marker = tmp_path / "startup-hook-executed"
    if relative_path in {"sitecustomize.py", "usercustomize.py"}:
        material.write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n",
            encoding="utf-8",
        )
    else:
        material.write_text("synthetic\n", encoding="utf-8")

    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )

    assert completed.returncode == 2
    assert payload["reason_codes"] == ["gatekeeper_bootstrap_source_not_clean"]
    assert marker.exists() is False


@pytest.mark.parametrize("case", ["widen_scope", "rewrite_review", "closeout"])
def test_g1a_cannot_widen_scope_rewrite_evidence_or_inline_closeout(
    tmp_path: Path, case: str
) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(target)
    if case == "widen_scope":
        path = target / pa.OVERLAY_PATH
        overlay = pa._strict_yaml(path)
        overlay["profiles"][pa.G1A3_ACTIVE_PROFILE]["allowed_paths"].append(
            "app/main.py"
        )
        _write_yaml(path, overlay)
    elif case == "rewrite_review":
        path = (
            target
            / pa.G1A3_TRANSITION_REVIEW_ROOT
            / f"{transition_manifest['enablement_review_id']}.json"
        )
        review = json.loads(path.read_text(encoding="utf-8"))
        review["blocking_finding_count"] = 1
        _write_json(path, review)
    else:
        path = target / pa.STATE_PATH
        state = json.loads(path.read_text(encoding="utf-8"))
        state["current_gate_status"] = "complete"
        _write_json(path, state)
    manifest_path = _manifest_path(target, manifest, "candidate-manifest.json")
    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )
    assert completed.returncode == 2
    assert payload["admitted"] is False


def test_candidate_local_combined_api_is_not_an_accepted_g1a_gatekeeper(
    tmp_path: Path,
) -> None:
    target, _gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(target)
    decision = pa.evaluate_programme_operation_admission(
        repo_root=target,
        manifest=manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert decision.admitted is False
    assert decision.reason_codes == ["pinned_gatekeeper_required"]


_HIGH_RISK_GIT_ENVIRONMENT = (
    "GIT_DIR",
    "GIT_COMMON_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_REPLACE_REF_BASE",
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_KEY_0",
    "GIT_CONFIG_VALUE_0",
    "GIT_CONFIG_PARAMETERS",
    "GIT_EXEC_PATH",
    "GIT_SHALLOW_FILE",
    "GIT_SSL_NO_VERIFY",
)


@pytest.mark.parametrize("variable", _HIGH_RISK_GIT_ENVIRONMENT)
def test_bootstrap_rejects_high_risk_git_environment_before_controller_import(
    tmp_path: Path, variable: str
) -> None:
    target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(target)
    manifest_path = _manifest_path(target, manifest, "environment-manifest.json")
    marker = tmp_path / "controller-imported"
    controller = gatekeeper / "scripts/raisa_ariadne_pinned_gatekeeper.py"
    controller.write_text(
        controller.read_text(encoding="utf-8")
        + f"\nPath({str(marker)!r}).write_text('imported', encoding='utf-8')\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment[variable] = "1"
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(gatekeeper / "scripts/raisa_ariadne_gatekeeper_bootstrap.py"),
            "--expected-source-commit",
            _git(gatekeeper, "rev-parse", "HEAD"),
            "--expected-source-tree",
            _git(gatekeeper, "rev-parse", "HEAD^{tree}"),
            "evaluate",
            "--target-repo",
            str(target),
            "--task-manifest",
            str(manifest_path),
            "--entrypoint",
            "task_branch_commit",
            "--phase",
            "development",
            "--format",
            "json",
        ],
        cwd=gatekeeper,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert completed.returncode == 2
    assert json.loads(completed.stdout)["reason_codes"] == [
        "trusted_git_environment_forbidden"
    ]
    assert marker.exists() is False


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_bootstrap_rejects_index_visibility_flags_before_controller_import(
    tmp_path: Path, flag: str
) -> None:
    target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(target)
    manifest_path = _manifest_path(target, manifest, "index-flag-manifest.json")
    marker = tmp_path / "controller-imported"
    controller_relative = "scripts/raisa_ariadne_pinned_gatekeeper.py"
    controller = gatekeeper / controller_relative
    controller.write_text(
        controller.read_text(encoding="utf-8")
        + f"\nPath({str(marker)!r}).write_text('imported', encoding='utf-8')\n",
        encoding="utf-8",
    )
    _git(gatekeeper, "update-index", flag, controller_relative)

    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )

    assert completed.returncode == 2
    assert payload["reason_codes"] == ["trusted_git_index_flags_forbidden"]
    assert marker.exists() is False


@pytest.mark.parametrize(
    "relative_path",
    [
        "orchestration_harness/models.py",
        "orchestration_harness/allocation.py",
        "orchestration_harness/allocator.py",
        "orchestration_harness/settings_fingerprint.py",
        "orchestration_harness/active_operation.py",
    ],
)
def test_bootstrap_rejects_fsmonitor_hidden_import_source_before_execution(
    tmp_path: Path, relative_path: str
) -> None:
    target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(target)
    manifest_path = _manifest_path(target, manifest, "fsmonitor-source-manifest.json")
    marker = tmp_path / f"{Path(relative_path).stem}-executed"
    source = gatekeeper / relative_path
    hook = tmp_path / "external-source-fsmonitor-hook.sh"
    hook.write_bytes(b"#!/bin/sh\nprintf 'g0-8-source-token\\0'\n")
    hook.chmod(hook.stat().st_mode | 0o111)
    _prime_external_fsmonitor(gatekeeper, hook)
    source.write_text(
        source.read_text(encoding="utf-8")
        + "\n__import__('pathlib').Path("
        + repr(str(marker))
        + ").write_text('executed', encoding='utf-8')\n",
        encoding="utf-8",
    )
    assert _git(gatekeeper, "status", "--porcelain") == ""
    assert relative_path in _git(
        gatekeeper,
        *_TRUSTED_GIT_OVERRIDES,
        "status",
        "--porcelain",
    )

    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )

    assert completed.returncode == 2
    assert payload["reason_codes"] == ["trusted_git_configuration_forbidden"]
    assert marker.exists() is False


@pytest.mark.parametrize("phase", ["development", "pre-push", "post-push"])
def test_target_fsmonitor_configuration_fails_closed_in_each_lifecycle_phase(
    tmp_path: Path, phase: str
) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    manifest_path = _manifest_path(
        target, transition_manifest, f"fsmonitor-target-{phase}-manifest.json"
    )
    hook = tmp_path / "external-target-fsmonitor-hook.sh"
    hook.write_bytes(b"#!/bin/sh\nprintf 'g0-8-target-token\\0'\n")
    hook.chmod(hook.stat().st_mode | 0o111)
    _prime_external_fsmonitor(target, hook)
    out_of_scope = target / "orchestration_harness/models.py"
    out_of_scope.write_text(
        out_of_scope.read_text(encoding="utf-8") + "\nUnreviewed hidden drift.\n",
        encoding="utf-8",
    )
    assert _git(target, "status", "--porcelain") == ""
    assert "orchestration_harness/models.py" in _git(
        target,
        *_TRUSTED_GIT_OVERRIDES,
        "status",
        "--porcelain",
    )

    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=manifest_path,
        phase=phase,
    )

    assert completed.returncode == 2
    assert "trusted_git_configuration_forbidden" in payload["reason_codes"]


@pytest.mark.parametrize("flag", ["--assume-unchanged", "--skip-worktree"])
def test_target_policy_rejects_index_visibility_flags(
    flag: str, tmp_path: Path
) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    _git(
        target,
        "update-index",
        flag,
        "orchestration/programme/current-state.json",
    )

    decision = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )

    assert decision.admitted is False
    assert "trusted_git_index_flags_forbidden" in decision.reason_codes


def test_target_authority_physical_bytes_must_match_the_bound_index(
    tmp_path: Path,
) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    state_path = target / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["observed_at"] = "2026-08-26T23:59:59+10:00"
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    decision = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )

    assert decision.admitted is False
    assert "trusted_git_physical_bytes_mismatch" in decision.reason_codes


def test_operation_cli_accepts_only_a_receipt_directory(tmp_path: Path) -> None:
    target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest_path = _manifest_path(
        target, build_task_manifest(target), "receipt-argument-manifest.json"
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(gatekeeper / "scripts/raisa_ariadne_gatekeeper_bootstrap.py"),
            "--expected-source-commit",
            _git(gatekeeper, "rev-parse", "HEAD"),
            "--expected-source-tree",
            _git(gatekeeper, "rev-parse", "HEAD^{tree}"),
            "push",
            "--target-repo",
            str(target),
            "--task-manifest",
            str(manifest_path),
            "--receipt",
            str(tmp_path / "arbitrary.json"),
        ],
        cwd=gatekeeper,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert completed.returncode != 0
    assert (tmp_path / "arbitrary.json").exists() is False


@pytest.mark.parametrize("location", ["target", "gatekeeper", "gitdir"])
def test_receipt_sink_rejects_repository_and_git_administration_locations(
    tmp_path: Path, location: str
) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    decision = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )
    assert decision.admitted is True
    locations = {
        "target": target / "receipts",
        "gatekeeper": gatekeeper / "receipts",
        "gitdir": Path(_git(target, "rev-parse", "--absolute-git-dir")) / "receipts",
    }
    locations[location].mkdir(parents=True)

    with pytest.raises(pa.ProgrammeAdmissionError, match="receipt_directory_forbidden"):
        pg.reserve_operation_receipt(
            receipt_directory=locations[location],
            operation="exact_sha_push",
            decision=decision,
            gatekeeper_root=gatekeeper,
            target_repo_root=target,
        )


def test_receipt_sink_reserves_exclusively_and_never_overwrites(tmp_path: Path) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    decision = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )
    receipt_directory = tmp_path / "closed-receipts"
    receipt_directory.mkdir()
    first = pg.reserve_operation_receipt(
        receipt_directory=receipt_directory,
        operation="exact_sha_push",
        decision=decision,
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
    )
    try:
        assert first.path.parent == receipt_directory.resolve()
        assert first.path.exists()
        with pytest.raises(pa.ProgrammeAdmissionError, match="receipt_collision"):
            pg.reserve_operation_receipt(
                receipt_directory=receipt_directory,
                operation="exact_sha_push",
                decision=decision,
                gatekeeper_root=gatekeeper,
                target_repo_root=target,
            )
    finally:
        first.close_unfinalized()


def test_receipt_sink_rejects_symlink_or_junction_substitution(tmp_path: Path) -> None:
    target, gatekeeper, transition_manifest = _transition_fixture(tmp_path)
    decision = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )
    real_directory = tmp_path / "real-receipts"
    real_directory.mkdir()
    substituted = tmp_path / "substituted-receipts"
    try:
        substituted.symlink_to(real_directory, target_is_directory=True)
    except OSError:
        completed = subprocess.run(
            [
                "cmd.exe",
                "/d",
                "/c",
                "mklink",
                "/J",
                str(substituted),
                str(real_directory),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            pytest.skip(f"reparse creation unavailable: {completed.stderr}")

    with pytest.raises(pa.ProgrammeAdmissionError, match="receipt_directory_invalid"):
        pg.reserve_operation_receipt(
            receipt_directory=substituted,
            operation="exact_sha_push",
            decision=decision,
            gatekeeper_root=gatekeeper,
            target_repo_root=target,
        )


def test_g1a3_r0_transition_and_exact_r1_joint_lifecycle_passes(
    tmp_path: Path,
) -> None:
    target, gatekeeper, transition_manifest, r0_candidate = (
        _build_g1a3_r0_transition_repository(tmp_path)
    )
    development = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert development.admitted is True, development.reason_codes
    assert development.gatekeeper_commit == r0_candidate

    candidate_local = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=target,
        target_repo_root=target,
        manifest=transition_manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert candidate_local.admitted is False
    assert "gatekeeper_target_not_isolated" in candidate_local.reason_codes

    transition_commit_receipts = tmp_path / "g1a3-r0-transition-commit-receipts"
    transition_commit_receipts.mkdir()
    transition_commit_receipt = pg.execute_exact_index_commit(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        receipt_directory=transition_commit_receipts,
        message="synthetic external PASS G1A.3-R0 to R1 transition",
    )
    transition_sha = transition_commit_receipt["result_sha"]
    assert _git(target, "rev-list", "--parents", "-n", "1", transition_sha) == (
        f"{transition_sha} {r0_candidate}"
    )

    transition_push_receipts = tmp_path / "g1a3-r0-transition-push-receipts"
    transition_push_receipts.mkdir()
    transition_push_receipt = pg.execute_exact_sha_push(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=transition_manifest,
        receipt_directory=transition_push_receipts,
    )
    assert transition_push_receipt["post_push_readback_sha"] == transition_sha

    policy = pa.load_programme_policy(target)
    assert policy.state["active_profile"] == pa.G1A3_R1_ACTIVE_PROFILE
    assert set(policy.allowed_paths) == pa.G1A3_R1_ALLOWED_PATHS
    assert (
        set(policy.overlay["profiles"][pa.G1A3_R1_ACTIVE_PROFILE]["allowed_effects"])
        == pa.G1A3_R1_ALLOWED_EFFECTS
    )
    assert policy.overlay["profiles"][pa.G1A3_R1_ACTIVE_PROFILE]["source_contract"] == {
        "antigravity_allowed_mutation": "run_worker_body_only",
        "antigravity_runtime_source_parsing_contract": pa.G1A3_RUNTIME_SOURCE_PARSING_CONTRACT,
        "run_worker_first_admission_contract": pa.G1A3_RUN_WORKER_FIRST_ADMISSION_CONTRACT,
        "integration_allowed_mutation": "record_integration_body_only",
        "record_integration_first_admission_contract": pa.G1A3_RECORD_INTEGRATION_FIRST_ADMISSION_CONTRACT,
    }

    forged_path = target / "orchestration_harness/pinned_programme_gatekeeper.py"
    accepted_gatekeeper = forged_path.read_bytes()
    forged_path.write_text(
        "raise SystemExit('forged candidate controller')\n", encoding="utf-8"
    )
    _git(target, "add", "--", forged_path.relative_to(target).as_posix())
    forged_manifest = build_task_manifest(target)
    forged_decision = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=forged_manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert forged_decision.admitted is False
    assert "scope_tranche_path_outside_policy" in forged_decision.reason_codes
    forged_path.write_bytes(accepted_gatekeeper)
    _git(target, "add", "--", forged_path.relative_to(target).as_posix())

    antigravity_path = target / "scripts/ariadne_antigravity.py"
    antigravity = antigravity_path.read_text(encoding="utf-8")
    antigravity_path.write_text(
        antigravity.replace(
            '        entrypoint="provider_invocation",\n    )\n',
            '        entrypoint="provider_invocation",\n'
            "    )\n"
            "    complete_review_binding_enabled = True\n",
            1,
        ),
        encoding="utf-8",
    )
    assert antigravity_path.read_text(encoding="utf-8") != antigravity

    consumer_path = target / "scripts/agent_worktrees.py"
    consumer = consumer_path.read_text(encoding="utf-8")
    consumer_path.write_text(
        consumer.replace(
            "def record_integration(args: argparse.Namespace) -> None:\n"
            '    _require_command_admission(args, entrypoint="integration")\n',
            "def record_integration(args: argparse.Namespace) -> None:\n"
            '    _require_command_admission(args, entrypoint="integration")\n'
            "    complete_review_binding_required = True\n",
            1,
        ),
        encoding="utf-8",
    )
    assert consumer_path.read_text(encoding="utf-8") != consumer

    producer_test = target / "tests/test_ariadne_antigravity.py"
    producer_test.write_text(
        producer_test.read_text(encoding="utf-8")
        + "\n\ndef test_synthetic_complete_review_binding_marker():\n"
        + "    assert 'complete_tracked_tree'.startswith('complete_')\n",
        encoding="utf-8",
    )
    consumer_test = target / "tests/test_agent_worktrees.py"
    consumer_test.write_text(
        consumer_test.read_text(encoding="utf-8")
        + "\n\ndef test_synthetic_integration_binding_marker():\n"
        + "    assert 'review_attestation'.endswith('attestation')\n",
        encoding="utf-8",
    )
    _git(target, "add", "--", *sorted(pa.G1A3_R1_ALLOWED_PATHS))

    task_manifest = build_task_manifest(target)
    assert set(task_manifest["allowed_path_roots"]) == pa.G1A3_R1_ALLOWED_PATHS
    assert set(task_manifest["intended_side_effect_classes"]) == (
        pa.G1A3_R1_ALLOWED_EFFECTS
    )
    narrowed_manifest = dict(task_manifest)
    narrowed_manifest["allowed_path_roots"] = sorted(pa.G1A3_R1_ALLOWED_PATHS)[1:]
    narrowed = pa.evaluate_programme_admission(
        repo_root=target,
        manifest=narrowed_manifest,
        entrypoint="recovery_preflight",
    )
    assert narrowed.admitted is False
    assert narrowed.reason_codes == ["g1a_3_r1_task_manifest_paths_not_exact"]
    widened_manifest = dict(task_manifest)
    widened_manifest["allowed_path_roots"] = [
        *task_manifest["allowed_path_roots"],
        "app/main.py",
    ]
    widened = pa.evaluate_programme_admission(
        repo_root=target,
        manifest=widened_manifest,
        entrypoint="recovery_preflight",
    )
    assert widened.admitted is False
    assert widened.reason_codes == ["task_manifest_path_outside_policy"]
    assert pa.g1a3_review_producer_contract_reasons(target) == []
    assert pa.g1a3_integration_contract_reasons(target) == []
    for entrypoint in ("provider_invocation", "integration"):
        denied = pa.evaluate_programme_admission(
            repo_root=target,
            manifest=task_manifest,
            entrypoint=entrypoint,
        )
        assert denied.admitted is False

    task_development = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=task_manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert task_development.admitted is True, task_development.reason_codes

    task_commit_receipts = tmp_path / "g1a3-r1-commit-receipts"
    task_commit_receipts.mkdir()
    task_commit_receipt = pg.execute_exact_index_commit(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=task_manifest,
        receipt_directory=task_commit_receipts,
        message="synthetic exact four-path G1A.3-R1 implementation",
    )
    task_sha = task_commit_receipt["result_sha"]

    task_manifest = build_task_manifest(target)
    task_push_receipts = tmp_path / "g1a3-r1-push-receipts"
    task_push_receipts.mkdir()
    task_push_receipt = pg.execute_exact_sha_push(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=task_manifest,
        receipt_directory=task_push_receipts,
    )
    assert task_push_receipt["post_push_readback_sha"] == task_sha

    post_push = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=task_manifest,
        entrypoint="task_branch_push",
        phase="post-push",
    )
    assert post_push.admitted is True, post_push.reason_codes
    assert (
        _git(target, "rev-parse", "master")
        == policy.state["protected_refs"]["expected_sha"]
    )
    assert (
        _git(target, "rev-parse", "handoff/current")
        == policy.state["protected_refs"]["expected_sha"]
    )
