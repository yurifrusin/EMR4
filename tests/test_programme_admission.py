import json
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import orchestration_harness.programme_admission as pa
from orchestration_harness.programme_admission import (
    ENTRYPOINTS,
    GitPathChange,
    ProgrammeAdmissionError,
    ProgrammeDecision,
    evaluate_committed_scope,
    evaluate_programme_admission,
    git_change_inventory,
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
                'next_eligible_tranche: "G0.2"',
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


def _changes(path: str = "AGENTS.md") -> tuple[list[GitPathChange], list[GitPathChange]]:
    rows = [GitPathChange("M", path, "100644", "100644")]
    return rows, rows


def test_committed_product_path_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = load_programme_policy(ROOT)
    manifest = _manifest()
    monkeypatch.setattr(pa, "load_programme_policy", lambda _root: policy)
    monkeypatch.setattr(pa, "evaluate_programme_admission", lambda **_kwargs: _admitted(policy))
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(pa, "_run_git", _scope_git_stub(manifest, changed="app/main.py"))
    monkeypatch.setattr(
        pa,
        "_scope_change_inventories",
        lambda *_args, **_kwargs: _changes("app/main.py"),
    )

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
    monkeypatch.setattr(pa, "_scope_change_inventories", lambda *_args, **_kwargs: _changes())

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
    monkeypatch.setattr(pa, "_scope_change_inventories", lambda *_args, **_kwargs: _changes())

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
    assert policy.state["g0_2_correction"]["g1a_authorized"] is False
    assert policy.state["g0_2_correction"]["external_review_status"] in {
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


def _git(root: Path, *args: str, input_text: str | None = None) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_text,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def _new_inventory_repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "inventory-repo"
    root.mkdir()
    _git(root, "init", "-b", "inventory")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G0.2 Tests")
    _git(root, "config", "core.autocrlf", "false")
    (root / "app").mkdir()
    (root / "orchestration/programme").mkdir(parents=True)
    (root / "app/product.txt").write_text("product\n", encoding="utf-8")
    (root / "orchestration/programme/current-state.json").write_text(
        "{}\n", encoding="utf-8"
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "seed")
    return root, _git(root, "rev-parse", "HEAD")


def test_raw_inventory_exposes_unauthorised_source_of_pure_rename(
    tmp_path: Path,
) -> None:
    root, base = _new_inventory_repo(tmp_path)
    _git(
        root,
        "mv",
        "app/product.txt",
        "orchestration/programme/review.json",
    )

    changes = git_change_inventory(root, f"{base}..HEAD") + git_change_inventory(
        root, "--cached"
    )

    assert {(row.status, row.path) for row in changes} >= {
        ("D", "app/product.txt"),
        ("A", "orchestration/programme/review.json"),
    }
    assert {row.path for row in changes} - {"orchestration/programme/review.json"}


def test_raw_inventory_exposes_both_sides_of_modified_rename(tmp_path: Path) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    _git(
        root,
        "mv",
        "app/product.txt",
        "orchestration/programme/review.json",
    )
    with (root / "orchestration/programme/review.json").open(
        "a", encoding="utf-8"
    ) as stream:
        stream.write("modified\n")
    _git(root, "add", "-A")

    changes = git_change_inventory(root, "--cached")

    assert {(row.status, row.path) for row in changes} == {
        ("D", "app/product.txt"),
        ("A", "orchestration/programme/review.json"),
    }


def test_raw_inventory_exposes_unauthorised_deletion(tmp_path: Path) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    _git(root, "rm", "app/product.txt")

    changes = git_change_inventory(root, "--cached")

    assert [(row.status, row.path) for row in changes] == [("D", "app/product.txt")]


def test_raw_inventory_rejects_symlink_substitution(tmp_path: Path) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    blob = _git(root, "hash-object", "-w", "--stdin", input_text="target\n")
    _git(
        root,
        "update-index",
        "--cacheinfo",
        f"120000,{blob},orchestration/programme/current-state.json",
    )

    changes = git_change_inventory(root, "--cached")

    assert "scope_symlink_mode_forbidden" in pa._change_inventory_reasons(changes)


def test_raw_inventory_rejects_gitlink_substitution(tmp_path: Path) -> None:
    root, base = _new_inventory_repo(tmp_path)
    _git(
        root,
        "update-index",
        "--cacheinfo",
        f"160000,{base},orchestration/programme/current-state.json",
    )

    changes = git_change_inventory(root, "--cached")

    assert "scope_gitlink_mode_forbidden" in pa._change_inventory_reasons(changes)


def test_raw_inventory_preserves_windows_relevant_path_case_change(
    tmp_path: Path,
) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    path = root / "orchestration/programme/Policy.json"
    path.write_text("{}\n", encoding="utf-8")
    _git(root, "add", "orchestration/programme/Policy.json")
    _git(root, "commit", "-m", "add case source")
    _git(
        root,
        "mv",
        "orchestration/programme/Policy.json",
        "orchestration/programme/case-hop.json",
    )
    _git(
        root,
        "mv",
        "orchestration/programme/case-hop.json",
        "orchestration/programme/policy.json",
    )

    changes = git_change_inventory(root, "--cached")

    assert {row.path for row in changes} == {
        "orchestration/programme/Policy.json",
        "orchestration/programme/policy.json",
    }


def test_raw_inventory_allows_ordinary_regular_file_modification(
    tmp_path: Path,
) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    (root / "orchestration/programme/current-state.json").write_text(
        '{"changed": true}\n', encoding="utf-8"
    )

    changes = git_change_inventory(root)

    assert [(row.status, row.path, row.old_mode, row.new_mode) for row in changes] == [
        (
            "M",
            "orchestration/programme/current-state.json",
            "100644",
            "100644",
        )
    ]
    assert pa._change_inventory_reasons(changes) == []


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _write_yaml(path: Path, value: dict) -> None:
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def _build_transition_repository(tmp_path: Path) -> tuple[Path, dict]:
    root = _policy_sandbox(tmp_path)
    branch = "codex/raisa-ariadne-recovery-g0"
    _git(root, "init", "-b", branch)
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G0.2 Tests")
    _git(root, "config", "core.autocrlf", "false")
    (root / "app").mkdir(exist_ok=True)
    (root / "app/main.py").write_text("# unchanged product path\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "protected seed")
    protected = _git(root, "rev-parse", "HEAD")
    _git(root, "branch", "master", protected)
    _git(root, "branch", "handoff/current", protected)
    _git(root, "branch", "safety/ariadne-clockwork-pre-g0-20260825", protected)

    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["protected_refs"]["expected_sha"] = protected
    state["protected_refs"]["refs"] = [
        "refs/heads/master",
        "refs/heads/handoff/current",
        "refs/remotes/origin/master",
        "refs/remotes/origin/handoff/current",
    ]
    state["recovery_baton"]["base_sha"] = protected
    state["recovery_baton"]["protected_baton_sha"] = protected
    state["clockwork_snapshot"]["frozen_sha"] = protected
    state["g0_2_correction"]["authorized_parent_commit"] = protected
    state["g0_2_correction"]["status"] = "review_pending"
    state["g0_2_correction"]["external_review_status"] = "pending"
    _write_json(state_path, state)

    gates_path = root / pa.GATES_PATH
    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    next(row for row in gates["gates"] if row["id"] == "G0.2")[
        "status"
    ] = "review_pending"
    _write_yaml(gates_path, gates)

    inventory_path = root / pa.INVENTORY_PATH
    inventory = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))
    inventory["authoritative_refs"]["protected_master"] = protected
    inventory["authoritative_refs"]["protected_handoff_current"] = protected
    inventory["authoritative_refs"]["recovery_base"] = protected
    _write_yaml(inventory_path, inventory)

    overlay_path = root / pa.OVERLAY_PATH
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["scope_policy"]["frozen_recovery_base"] = protected
    overlay["scope_policy"]["authorized_parent_commit"] = protected
    _write_yaml(overlay_path, overlay)
    from orchestration_harness.settings_fingerprint import settings_fingerprint

    latch_path = root / pa.LATCH_PATH
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "G0.2 reviewed candidate")
    reviewed = _git(root, "rev-parse", "HEAD")
    reviewed_tree = _git(root, "rev-parse", f"{reviewed}^{{tree}}")

    origin = tmp_path / "origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare")
    _git(root, "remote", "add", "origin", str(origin))
    _git(root, "push", "origin", f"{protected}:refs/heads/master")
    _git(root, "push", "origin", f"{protected}:refs/heads/handoff/current")
    _git(root, "push", "-u", "origin", branch)
    _git(root, "fetch", "origin")

    before_policy = load_programme_policy(root)
    transition_id = "g0-to-g1a-synthetic-pass"
    reviewer_surface = "external_native_review"
    review_path = (
        root / pa.TRANSITION_REVIEW_ROOT / f"{transition_id}.json"
    )
    record = {
        "schema_version": "raisa-ariadne.external-g0-review.v1",
        "review_id": transition_id,
        "recorded_at": "2026-08-25T20:00:26+10:00",
        "reviewed_commit": reviewed,
        "reviewed_tree": reviewed_tree,
        "verdict": "PASS",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
    }
    _write_json(review_path, record)

    agents_path = root / pa.AGENTS_PATH
    agents_text = agents_path.read_text(encoding="utf-8")
    agents_path.write_text(
        agents_text.replace(
            "Gate G0.2 is the only authorised correction; G1A is\nclosed.",
            "The reviewed state-only G0 to G1A transition is complete; Gate G1A is\nnext eligible but not started.",
            1,
        ),
        encoding="utf-8",
    )

    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["current_gate"] = "G1A"
    state["current_gate_status"] = "gate_transition"
    state["active_correction"] = "gate_transition"
    state["task_selection"]["allowed_task_kinds"] = [pa.TRANSITION_TASK_CLASS]
    state["task_selection"]["next_eligible_tranche"] = "G1A"
    state["task_selection"]["next_tranche_started"] = False
    state["task_selection"]["next_tranche_admission_requires_state_transition"] = False
    state["g0_2_correction"]["status"] = "external_review_passed"
    state["g0_2_correction"]["external_review_status"] = "pass"
    state["g0_2_correction"]["g1a_authorized"] = True
    state["gate_transition"] = {
        "status": "gate_transition",
        "transition_id": transition_id,
        "from_gate": "G0",
        "to_gate": "G1A",
        "reviewed_commit": reviewed,
        "reviewed_tree": reviewed_tree,
        "external_review_status": "pass",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "g1a_authorized": True,
        "next_action": "G1A_only",
    }
    _write_json(state_path, state)

    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    gates["programme"]["current_gate"] = "G1A"
    gates["programme"]["current_gate_status"] = "gate_transition"
    gates["programme"]["next_eligible_tranche"] = "G1A"
    statuses = {
        "G0": "passed",
        "G0.1": "superseded_revision_required",
        "G0.2": "external_review_passed",
        "G1A": "gate_transition_open",
    }
    for row in gates["gates"]:
        if row["id"] in statuses:
            row["status"] = statuses[row["id"]]
    _write_yaml(gates_path, gates)

    review_relative = review_path.relative_to(root).as_posix()
    transition_paths = sorted(pa.TRANSITION_FIXED_ALLOWED_PATHS | {review_relative})
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    recovery = overlay["recovery_mode"]
    recovery["expected_current_gate"] = "G1A"
    recovery["expected_gate_status"] = "gate_transition"
    recovery["active_correction"] = "gate_transition"
    recovery["admitted_task_classes"] = [pa.TRANSITION_TASK_CLASS]
    recovery["g1a_eligible"] = True
    overlay["scope_policy"]["authorized_parent_commit"] = reviewed
    overlay["scope_policy"]["allowed_paths"] = transition_paths
    _write_yaml(overlay_path, overlay)
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)
    _git(root, "add", *transition_paths)
    _git(root, "commit", "-m", "state-only G0 to G1A transition")

    manifest = {
        "schema_version": pa.TRANSITION_MANIFEST_VERSION,
        "transition_id": transition_id,
        "from_gate": "G0",
        "to_gate": "G1A",
        "reviewed_commit": reviewed,
        "reviewed_tree": reviewed_tree,
        "transition_parent": reviewed,
        "external_review_verdict": "PASS",
        "external_review_record_sha256": "sha256:"
        + hashlib.sha256(review_path.read_bytes()).hexdigest(),
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "state_digest_before": before_policy.state_digest,
        "policy_digest_before": before_policy.policy_digest,
        "allowed_transition_paths": transition_paths,
        "forbidden_effect_classes": sorted(pa.TRANSITION_FORBIDDEN_EFFECTS),
    }
    return root, manifest


def test_valid_synthetic_state_only_transition_is_admitted(tmp_path: Path) -> None:
    root, manifest = _build_transition_repository(tmp_path)

    decision = evaluate_committed_scope(
        repo_root=root, manifest=manifest, phase="pre-push"
    )

    assert decision.admitted is True
    assert decision.reason_codes == []
    assert decision.candidate_commit_count == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("transition_parent", "0" * 40),
        ("reviewed_commit", "0" * 40),
        ("reviewed_tree", "0" * 40),
        ("external_review_verdict", "REVISION_REQUIRED"),
        ("external_review_record_sha256", "sha256:" + "0" * 64),
        ("blocking_finding_count", 1),
        ("state_digest_before", "sha256:" + "0" * 64),
        ("policy_digest_before", "sha256:" + "0" * 64),
    ],
)
def test_transition_rejects_wrong_binding(
    tmp_path: Path, field: str, value: object
) -> None:
    root, manifest = _build_transition_repository(tmp_path)
    manifest[field] = value

    decision = evaluate_committed_scope(
        repo_root=root, manifest=manifest, phase="pre-push"
    )

    assert decision.admitted is False
    assert decision.reason_codes


def test_transition_rejects_changed_implementation_path(tmp_path: Path) -> None:
    root, manifest = _build_transition_repository(tmp_path)
    with (root / "orchestration_harness/programme_admission.py").open(
        "a", encoding="utf-8"
    ) as stream:
        stream.write("# forbidden transition drift\n")

    decision = evaluate_committed_scope(
        repo_root=root, manifest=manifest, phase="pre-push"
    )

    assert decision.admitted is False
    assert "scope_tranche_path_outside_policy" in decision.reason_codes
    assert "transition_python_implementation_forbidden" in decision.reason_codes


def test_direct_antigravity_runner_rechecks_admission_before_forged_receipt(
    tmp_path: Path,
) -> None:
    from scripts import ariadne_antigravity

    packet = tmp_path / "packet.md"
    packet.write_text("forged launch", encoding="utf-8")
    forged = tmp_path / "historical-receipt.json"
    forged.write_text(
        json.dumps(
            {
                "schema_version": "ariadne.orchestrator_receipt.v1",
                "status": "passed",
                "worker_dispatch_permitted": True,
                "rehydration_sources": sorted(
                    ariadne_antigravity.REHYDRATION_SOURCES
                ),
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "provider-output.json"

    with pytest.raises(ProgrammeAdmissionError, match="task_manifest_missing"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=ROOT,
            output_path=output,
            orchestrator_receipt_path=forged,
            model=ariadne_antigravity.DEFAULT_MODEL,
            os_sandbox=False,
        )

    assert not output.exists()


def test_direct_deepseek_runner_rechecks_admission_before_subprocess(
    tmp_path: Path,
) -> None:
    from scripts import ariadne_deepseek_claude

    packet = tmp_path / "packet.md"
    packet.write_text("forged launch", encoding="utf-8")
    output = tmp_path / "provider-output.json"

    with pytest.raises(ProgrammeAdmissionError, match="task_manifest_missing"):
        ariadne_deepseek_claude.run_worker(
            packet_path=packet,
            cwd=ROOT,
            output_path=output,
            model="deepseek-v4-flash",
            effort="high",
        )

    assert not output.exists()


def test_direct_clockwork_closeout_rechecks_admission_before_read_or_write(
    tmp_path: Path,
) -> None:
    from scripts import ariadne_governance_clockwork_closeout as closeout

    with pytest.raises(ProgrammeAdmissionError, match="task_manifest_missing"):
        closeout.run_bound_closeout(
            ROOT,
            intent_raw=tmp_path / "missing.json",
            mode="publish",
        )


def test_agent_worktree_mutator_rechecks_admission_before_mutation() -> None:
    from scripts import agent_worktrees

    args = SimpleNamespace(programme_task_manifest=None)

    with pytest.raises(ProgrammeAdmissionError, match="task_manifest_missing"):
        agent_worktrees.setup(args)


def test_nested_closeout_forwards_programme_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import ariadne_governance_clockwork_closeout as closeout

    intent = tmp_path / "closeout-intent.json"
    intent.write_text(
        json.dumps({"schema_version": closeout.SEMANTIC_TICK_INTENT_VERSION}),
        encoding="utf-8",
    )
    manifest = tmp_path / "transition-manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(closeout, "require_programme_admission", lambda **_kwargs: None)
    monkeypatch.setattr(closeout, "validate_contract", lambda value: value)
    monkeypatch.setattr(
        closeout,
        "admit_tick_intent",
        lambda *_args: {"command_manifest": {"commands": []}},
    )
    monkeypatch.setattr(closeout, "resolve_full_head", lambda *_args, **_kwargs: "1" * 40)
    monkeypatch.setattr(
        closeout,
        "resolve_repository_interpreter",
        lambda *_args, **_kwargs: (Path(sys.executable), Path(sys.executable)),
    )
    monkeypatch.setattr(closeout, "_git_paths", lambda *_args, **_kwargs: set())
    monkeypatch.setattr(closeout, "_publication_surface", lambda *_args, **_kwargs: {})

    def stop_after_capture(command, **_kwargs):
        calls.append(command)
        raise RuntimeError("captured nested tick")

    monkeypatch.setattr(closeout, "_run_text", stop_after_capture)

    with pytest.raises(RuntimeError, match="captured nested tick"):
        closeout.run_bound_closeout(
            tmp_path,
            intent_raw=Path("closeout-intent.json"),
            mode="publish",
            programme_task_manifest=manifest,
        )

    assert calls
    assert "--programme-task-manifest" in calls[0]
    assert calls[0][calls[0].index("--programme-task-manifest") + 1] == str(
        manifest.resolve()
    )


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
