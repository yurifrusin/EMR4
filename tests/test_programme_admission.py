import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import orchestration_harness.programme_admission as pa
from orchestration_harness.programme_admission import (
    ENTRYPOINTS,
    ProgrammeAdmissionError,
    ProgrammeDecision,
    evaluate_committed_scope,
    evaluate_programme_admission,
    load_programme_policy,
)
from scripts.ariadne_orchestrator_preflight import build_receipt
from scripts.raisa_ariadne_recovery_preflight import build_task_manifest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_STATE = (
    ROOT / "tests/fixtures/ariadne_harness/orchestrator_runtime_state.json"
)


def _policy_sandbox(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "orchestration/programme").mkdir(parents=True)
    (root / "orchestration/continuity/ariadne-active-operation-latch").mkdir(
        parents=True
    )
    shutil.copytree(
        ROOT / "orchestration/harness_settings",
        root / "orchestration/harness_settings",
    )
    for relative in (
        pa.STATE_PATH,
        pa.GATES_PATH,
        pa.RISK_PATH,
        pa.INVENTORY_PATH,
        pa.LATCH_PATH,
        pa.AGENTS_PATH,
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    for relative_text in pa.G0_G01_ALLOWED_PATHS:
        source = ROOT / relative_text
        if not source.is_file():
            continue
        target = root / relative_text
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return root


def _manifest() -> dict:
    return build_task_manifest(ROOT)


def test_canonical_orchestrator_cannot_dispatch_with_current_fingerprint() -> None:
    receipt = build_receipt(runtime_state_path=RUNTIME_STATE)

    assert receipt["status"] == "passed"
    assert receipt["worker_dispatch_permitted"] is False
    assert receipt["admission_usable"] is False
    assert receipt["programme_admission"]["admitted"] is False


def test_mislabeled_product_task_cannot_enter_g0_1() -> None:
    manifest = _manifest()
    manifest["task_class"] = "product_feature"

    decision = evaluate_programme_admission(
        repo_root=ROOT, manifest=manifest, entrypoint="task_selection"
    )

    assert decision.admitted is False
    assert decision.reason_codes == ["task_class_not_admitted"]


@pytest.mark.parametrize("entrypoint", sorted(ENTRYPOINTS))
def test_missing_manifest_blocks_every_gated_entrypoint(entrypoint: str) -> None:
    decision = evaluate_programme_admission(
        repo_root=ROOT, manifest=None, entrypoint=entrypoint
    )

    assert decision.admitted is False
    assert decision.reason_codes == ["task_manifest_missing"]


@pytest.mark.parametrize("field", ["state_digest", "policy_digest"])
def test_stale_manifest_digests_fail_closed(field: str) -> None:
    manifest = _manifest()
    manifest[field] = "sha256:" + "0" * 64

    decision = evaluate_programme_admission(
        repo_root=ROOT, manifest=manifest, entrypoint="task_selection"
    )

    assert decision.admitted is False
    assert decision.reason_codes == [f"task_manifest_{field}_stale"]


@pytest.mark.parametrize("failure", ["missing", "malformed", "contradictory"])
def test_missing_malformed_or_contradictory_policy_fails_closed(
    tmp_path: Path, failure: str
) -> None:
    root = _policy_sandbox(tmp_path)
    if failure == "missing":
        (root / pa.STATE_PATH).unlink()
    elif failure == "malformed":
        (root / pa.STATE_PATH).write_text("{", encoding="utf-8")
    else:
        gates = (root / pa.GATES_PATH).read_text(encoding="utf-8")
        (root / pa.GATES_PATH).write_text(
            gates.replace(
                'current_gate_status: "revision_required"',
                'current_gate_status: "passed"',
                1,
            ),
            encoding="utf-8",
        )

    with pytest.raises(ProgrammeAdmissionError):
        load_programme_policy(root)


def test_duplicate_yaml_key_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.GATES_PATH
    path.write_text(
        'schema_version: "duplicate"\n' + path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    with pytest.raises(ProgrammeAdmissionError, match="yaml_duplicate_key"):
        load_programme_policy(root)


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.STATE_PATH
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "{\n", '{\n  "schema_version": "duplicate",\n', 1
        ),
        encoding="utf-8",
    )

    with pytest.raises(ProgrammeAdmissionError, match="json_duplicate_key"):
        load_programme_policy(root)


def test_unknown_policy_field_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.STATE_PATH
    state = json.loads(path.read_text(encoding="utf-8"))
    state["permissive_unknown"] = True
    path.write_text(json.dumps(state), encoding="utf-8")

    with pytest.raises(ProgrammeAdmissionError, match="programme_state_schema_invalid"):
        load_programme_policy(root)


def test_state_and_gate_disagreement_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.GATES_PATH
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            'next_eligible_tranche: "G0.1"',
            'next_eligible_tranche: "G1A"',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ProgrammeAdmissionError, match="programme_state_gate_disagreement"
    ):
        load_programme_policy(root)


def test_duplicate_risk_id_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.RISK_PATH
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '- id: "R-002"', '- id: "R-001"', 1
        ),
        encoding="utf-8",
    )

    with pytest.raises(ProgrammeAdmissionError, match="risk_id_duplicate"):
        load_programme_policy(root)


def _scope_git_stub(
    manifest: dict, *, commit_count: int = 1, changed: str = "AGENTS.md", remote: str | None = None
):
    head = manifest["candidate_or_current_head"]
    branch = "codex/raisa-ariadne-recovery-g0"

    def run(_root: Path, *args: str) -> str:
        if args == ("branch", "--show-current"):
            return branch
        if args == ("rev-parse", "HEAD"):
            return head
        if args == ("rev-parse", f"origin/{branch}"):
            return manifest["base_commit"]
        if args[:2] == ("rev-list", "--count"):
            return str(commit_count)
        if args[:2] == ("diff", "--name-only"):
            return changed if "..HEAD" in args[-1] else ""
        if args == ("diff", "--cached", "--name-only"):
            return ""
        if args == ("status", "--porcelain", "--untracked-files=no"):
            return ""
        if args[:3] == ("ls-remote", "--heads", "origin"):
            return "" if remote is None else f"{remote}\trefs/heads/{branch}"
        raise AssertionError(args)

    return run


def _admitted(policy: pa.ProgrammePolicy) -> ProgrammeDecision:
    return ProgrammeDecision(
        pa.DECISION_VERSION,
        True,
        [],
        "recovery",
        "G0",
        pa.ADMITTED_TASK_CLASS,
        policy.state_digest,
        policy.policy_digest,
    )


def test_committed_product_path_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = load_programme_policy(ROOT)
    manifest = _manifest()
    monkeypatch.setattr(pa, "load_programme_policy", lambda _root: policy)
    monkeypatch.setattr(pa, "evaluate_programme_admission", lambda **_kwargs: _admitted(policy))
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(pa, "_run_git", _scope_git_stub(manifest, changed="app/main.py"))

    decision = evaluate_committed_scope(
        repo_root=ROOT, manifest=manifest, phase="pre-push"
    )

    assert decision.admitted is False
    assert "scope_path_outside_policy" in decision.reason_codes


def test_later_commit_after_candidate_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = load_programme_policy(ROOT)
    manifest = _manifest()
    monkeypatch.setattr(pa, "load_programme_policy", lambda _root: policy)
    monkeypatch.setattr(pa, "evaluate_programme_admission", lambda **_kwargs: _admitted(policy))
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(pa, "_run_git", _scope_git_stub(manifest, commit_count=2))

    decision = evaluate_committed_scope(
        repo_root=ROOT, manifest=manifest, phase="pre-push"
    )

    assert decision.admitted is False
    assert "scope_candidate_commit_count_invalid" in decision.reason_codes


@pytest.mark.parametrize("remote", [None, "0" * 40])
def test_post_push_missing_or_mismatched_origin_is_rejected(
    monkeypatch: pytest.MonkeyPatch, remote: str | None
) -> None:
    policy = load_programme_policy(ROOT)
    manifest = _manifest()
    monkeypatch.setattr(pa, "load_programme_policy", lambda _root: policy)
    monkeypatch.setattr(pa, "evaluate_programme_admission", lambda **_kwargs: _admitted(policy))
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(pa, "_run_git", _scope_git_stub(manifest, remote=remote))

    decision = evaluate_committed_scope(
        repo_root=ROOT, manifest=manifest, phase="post-push"
    )

    assert decision.admitted is False
    assert any(reason.startswith("scope_fresh_origin") or reason == "scope_origin_head_mismatch" for reason in decision.reason_codes)


def test_historical_latch_cannot_resume(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.LATCH_PATH
    latch = json.loads(path.read_text(encoding="utf-8"))
    latch["status"] = "paused"
    path.write_text(json.dumps(latch), encoding="utf-8")

    with pytest.raises(
        ProgrammeAdmissionError, match="historical_latch_not_terminally_replaced"
    ):
        load_programme_policy(root)


def test_agents_emergency_header_has_machine_precedence(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.AGENTS_PATH
    text = path.read_text(encoding="utf-8")
    path.write_text(text.split("# EMR4 Centaur", 1)[1], encoding="utf-8")

    with pytest.raises(
        ProgrammeAdmissionError, match="agents_recovery_precedence_missing"
    ):
        load_programme_policy(root)


@pytest.mark.parametrize("entrypoint", sorted(pa.ENTRYPOINTS_CLOSED_IN_G0))
def test_forbidden_side_effect_entrypoints_remain_closed(entrypoint: str) -> None:
    decision = evaluate_programme_admission(
        repo_root=ROOT, manifest=_manifest(), entrypoint=entrypoint
    )

    assert decision.admitted is False
    assert decision.reason_codes == [f"{entrypoint}_closed_in_g0"]


def test_machine_state_does_not_claim_stale_review_acceptance() -> None:
    policy = load_programme_policy(ROOT)

    assert policy.state["g0_acceptance"]["status"] == "superseded_revision_required"
    assert policy.state["g0_1_correction"]["g1a_authorized"] is False
    assert policy.state["g0_1_correction"]["external_review_status"] in {
        "not_started",
        "pending",
    }


def test_gated_executable_sources_require_programme_admission() -> None:
    sources = {
        "scripts/ariadne_antigravity.py": "provider_invocation",
        "scripts/ariadne_deepseek_claude.py": "provider_invocation",
        "scripts/drive_agent_headless.py": "provider_invocation",
        "scripts/ariadne_governance_clockwork_tick.py": "clockwork_tick_mutation",
        "scripts/ariadne_governance_clockwork_closeout.py": "clockwork_closeout_mutation",
        "scripts/agent_worktrees.py": "worker_dispatch",
    }
    for relative, entrypoint in sources.items():
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "require_programme_admission(" in source
        assert f'"{entrypoint}"' in source


@pytest.mark.parametrize(
    "arguments",
    [
        [
            "scripts/ariadne_antigravity.py",
            "--packet",
            "missing",
            "--cwd",
            ".",
            "--output",
            "missing",
            "--orchestrator-receipt",
            "missing",
        ],
        [
            "scripts/ariadne_deepseek_claude.py",
            "--packet",
            "missing",
            "--cwd",
            ".",
            "--output",
            "missing",
        ],
        ["scripts/drive_agent_headless.py", "--cwd", ".", "--prompt", "none"],
        [
            "scripts/ariadne_governance_clockwork_tick.py",
            "--publish",
            "--intent",
            "missing",
        ],
        [
            "scripts/ariadne_governance_clockwork_closeout.py",
            "--publish",
            "--intent",
            "missing",
        ],
        ["scripts/agent_worktrees.py", "dispatch", "--agent", "claude", "--title", "x", "--mission", "x", "--in-scope", "x", "--out-of-scope", "x", "--verification", "x", "--merge-criteria", "x"],
        ["scripts/agent_worktrees.py", "submit"],
        ["scripts/agent_worktrees.py", "handoff"],
    ],
)
def test_gated_cli_entrypoints_reject_missing_manifest_before_effects(
    arguments: list[str],
) -> None:
    completed = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 2
    assert "task_manifest_missing" in (completed.stdout + completed.stderr).lower()
