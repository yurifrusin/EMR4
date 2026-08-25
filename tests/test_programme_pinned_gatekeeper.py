import json
import subprocess
import sys
from pathlib import Path

import pytest

import orchestration_harness.programme_admission as pa
from scripts.raisa_ariadne_recovery_preflight import build_task_manifest
from tests.test_programme_admission import (
    _build_transition_repository,
    _git,
    _write_json,
    _write_yaml,
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
            "-B",
            "-m",
            "scripts.raisa_ariadne_pinned_gatekeeper",
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
    _git(target, "push", "origin", "codex/raisa-ariadne-recovery-g0")
    post_transition, post_transition_payload = _gatekeeper_cli(
        gatekeeper=gatekeeper,
        target=target,
        manifest_path=transition_manifest_path,
        phase="post-push",
    )
    assert post_transition.returncode == 0
    assert post_transition_payload["admitted"] is True

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
    g1a_manifest = build_task_manifest(target)
    assert pa.AGENTS_PATH.as_posix() not in g1a_manifest["allowed_path_roots"]
    g1a_development_path = _manifest_path(
        target, g1a_manifest, "g1a-development-manifest.json"
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

    _git(target, "add", "orchestration_harness/verdict.py")
    _git(target, "commit", "-m", "synthetic G1A verdict kernel change")
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
    _git(target, "push", "origin", "codex/raisa-ariadne-recovery-g0")
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
    assert "gatekeeper_worktree_not_clean" in dirty_payload["reason_codes"]

    wrong = tmp_path / "wrong-gatekeeper"
    _git(
        target,
        "worktree",
        "add",
        "--detach",
        str(wrong),
        _transition_manifest["reviewed_commit"] + "^",
    )
    wrongly_pinned, wrong_payload = _gatekeeper_cli(
        gatekeeper=wrong,
        target=target,
        manifest_path=manifest_path,
        phase="development",
    )
    assert wrongly_pinned.returncode == 2
    assert "gatekeeper_source_not_transition_pinned" in wrong_payload["reason_codes"]


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
