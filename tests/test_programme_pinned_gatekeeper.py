import json
import subprocess
import sys
from pathlib import Path

import pytest

import orchestration_harness.programme_admission as pa
import orchestration_harness.pinned_programme_gatekeeper as pg
from scripts.raisa_ariadne_recovery_preflight import build_task_manifest
from tests.test_programme_admission import (
    _build_transition_repository,
    _git,
    _write_json,
    _write_yaml,
)


ROOT = Path(__file__).resolve().parents[1]


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
    receipt_path: Path,
    message: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict]:
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
        "--receipt",
        str(receipt_path),
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
    target, transition_manifest = _build_transition_repository(tmp_path)
    reviewed = transition_manifest["reviewed_commit"]
    gatekeeper = tmp_path / "pinned-gatekeeper"
    _git(target, "worktree", "add", "--detach", str(gatekeeper), reviewed)
    return target, gatekeeper, transition_manifest


def test_real_bare_origin_transition_and_g1a_lifecycle_passes(tmp_path: Path) -> None:
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
        receipt_path=target.parent / "transition-push-receipt.json",
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
        f"{pa.TRANSITION_REVIEW_ROOT}/{transition_manifest['transition_id']}.json",
        f"{pa.TRANSITION_ARTIFACT_ROOT}/{transition_manifest['transition_id']}.json",
    }
    assert dynamic_paths.issubset(policy.full_range_allowed_paths)
    assert all("*" not in path for path in policy.full_range_allowed_paths)

    verdict_path = target / "orchestration_harness/verdict.py"
    verdict_path.write_text(
        "# authored-synthetic G1A lifecycle change\n",
        encoding="utf-8",
    )
    verdict_test_path = target / "tests/test_ariadne_verdict.py"
    verdict_test_path.write_text(
        "def test_authored_synthetic_verdict_placeholder():\n    assert True\n",
        encoding="utf-8",
    )
    g1a_manifest = build_task_manifest(target)
    assert pa.AGENTS_PATH.as_posix() not in g1a_manifest["allowed_path_roots"]
    g1a_development_path = _manifest_path(
        target, g1a_manifest, "g1a-development-manifest.json"
    )
    scope_development = pa.evaluate_committed_scope(
        repo_root=target, manifest=g1a_manifest, phase="development"
    )
    assert scope_development.admitted is True
    assert set(scope_development.target_cleanliness["untracked_paths"]) == {
        "orchestration_harness/verdict.py",
        "tests/test_ariadne_verdict.py",
    }

    _git(
        target,
        "add",
        "orchestration_harness/verdict.py",
        "tests/test_ariadne_verdict.py",
    )
    development, development_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=g1a_development_path,
        phase="development",
    )
    assert development.returncode == 0
    assert development_payload["admitted"] is True
    assert (
        pa.AGENTS_PATH.as_posix()
        in development_payload["scope_decision"]["changed_paths"]
    )

    commit_completed, commit_receipt = _gatekeeper_operation(
        operation="commit",
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=g1a_development_path,
        receipt_path=target.parent / "g1a-commit-receipt.json",
        message="synthetic G1A verdict kernel change",
    )
    assert commit_completed.returncode == 0
    committed = commit_receipt["result_sha"]
    assert _git(target, "rev-parse", "HEAD") == committed
    assert (
        _git(target, "rev-parse", "HEAD^{tree}")
        == (development_payload["operation_binding"]["index_tree"])
    )
    g1a_manifest = build_task_manifest(target)
    g1a_manifest_path = _manifest_path(target, g1a_manifest, "g1a-manifest.json")
    pre_g1a, pre_g1a_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=g1a_manifest_path,
        phase="pre-push",
    )
    assert pre_g1a.returncode == 0
    assert pre_g1a_payload["admitted"] is True
    g1a_binding = pre_g1a_payload["operation_binding"]
    assert pg.exact_push_argv(pg.PinnedGatekeeperDecision(**pre_g1a_payload)) == [
        "git",
        "push",
        "--no-verify",
        f"--force-with-lease={g1a_binding['force_with_lease']}",
        g1a_binding["explicit_destination"],
        g1a_binding["exact_push_refspec"],
    ]
    g1a_push, g1a_push_receipt = _gatekeeper_operation(
        operation="push",
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=g1a_manifest_path,
        receipt_path=target.parent / "g1a-push-receipt.json",
    )
    assert g1a_push.returncode == 0
    assert g1a_push_receipt["post_push_readback_sha"] == committed
    assert g1a_push_receipt["schema_version"] == (
        "ariadne.pinned_programme_operation_receipt.v1"
    )
    assert (
        g1a_push_receipt["admitted_operation_binding"]["explicit_destination"]
        == g1a_push_receipt["remote_identity"]["normalized_push_url"]
    )
    post_g1a, post_g1a_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=g1a_manifest_path,
        phase="post-push",
    )
    assert post_g1a.returncode == 0
    assert post_g1a_payload["admitted"] is True

    product_path = target / "app/main.py"
    product_path.write_text("# unrelated product drift\n", encoding="utf-8")
    product_manifest = build_task_manifest(target)
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
    assert "gatekeeper_source_not_transition_pinned" in wrong_payload["reason_codes"]


def test_preserved_legacy_683_file_worktree_is_never_a_g1a_target(
    tmp_path: Path,
) -> None:
    _target, gatekeeper, _transition_manifest = _transition_fixture(tmp_path)
    manifest = build_task_manifest(ROOT)
    manifest_path = tmp_path / "legacy-target-manifest.json"
    _write_json(manifest_path, manifest)

    completed, payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=ROOT,
        manifest_path=manifest_path,
        phase="development",
    )

    assert completed.returncode == 2
    assert (
        "gatekeeper_target_preserved_legacy_worktree_forbidden"
        in payload["reason_codes"]
    )


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
    verdict = target / "orchestration_harness/verdict.py"
    verdict.write_text("# staged verdict\n", encoding="utf-8")
    _git(target, "add", "orchestration_harness/verdict.py")
    manifest = build_task_manifest(target)

    prior = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=target,
        manifest=manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert prior.admitted is True

    verdict.write_text("# changed after admission\n", encoding="utf-8")
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
        overlay["profiles"][pa.G1A_ACTIVE_PROFILE]["allowed_paths"].append(
            "app/main.py"
        )
        _write_yaml(path, overlay)
    elif case == "rewrite_review":
        path = (
            target
            / pa.TRANSITION_REVIEW_ROOT
            / f"{transition_manifest['transition_id']}.json"
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
