"""Bounded policy regressions; synthetic observations are not operational admission."""

import ast
import copy
import json
import subprocess
from pathlib import Path

import pytest

import orchestration_harness.pinned_programme_gatekeeper as pg
import orchestration_harness.programme_admission as pa


ROOT = Path(__file__).resolve().parents[1]
BASE = "f726021a71e08f81529d3eecd807a695f7ba7e3a"
PIN = "9334903cbdc7fe04e1c58759ca4babf0fd6d453b"
PIN_TREE = "b78dd45caadad2bee651aaec6601a9072a7edeaa"
REVIEW_PATH = (
    "orchestration/programme/subgate-transition-enablement-reviews/"
    "g1b1-closeout-g1b2-review-9334903-independent-20260904-pass.json"
)
TRANSITION_PATH = (
    "orchestration/programme/subgate-transitions/g1b1-to-g1b2-9334903-pass.json"
)
HISTORY_PATHS = {REVIEW_PATH, TRANSITION_PATH}
UNRELATED_PATH = "orchestration/programme/subgate-transitions/unapproved-history.json"


def _git_bytes(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], check=True, capture_output=True
    ).stdout


@pytest.fixture(scope="module")
def policy() -> pa.ProgrammePolicy:
    return pa.load_programme_policy(ROOT)


def test_exact_seven_path_transition_retains_only_its_two_authority_records(
    policy: pa.ProgrammePolicy,
) -> None:
    artifact = json.loads(_git_bytes("show", f"{BASE}:{TRANSITION_PATH}"))
    manifest = artifact["transition_manifest"]
    paths = set(
        _git_bytes("diff-tree", "--no-commit-id", "--name-only", "-r", PIN, BASE)
        .decode()
        .splitlines()
    )
    assert paths == set(manifest["allowed_transition_paths"])
    assert paths == pa.G1B1_TO_G1B2_TRANSITION_FIXED_ALLOWED_PATHS | HISTORY_PATHS
    assert len(paths) == 7
    assert (
        policy.overlay["g1b1_to_g1b2_transition_policy"]["exact_transition_path_count"]
        == 7
    )
    assert manifest["enablement_candidate_commit"] == PIN
    assert manifest["enablement_candidate_tree"] == PIN_TREE
    assert _git_bytes("rev-parse", f"{BASE}^").decode().strip() == PIN
    assert paths <= set(policy.full_range_allowed_paths)
    assert set(policy.allowed_paths) == pa.G1B2_ALLOWED_PATHS
    assert HISTORY_PATHS.isdisjoint(policy.allowed_paths)
    assert UNRELATED_PATH not in policy.full_range_allowed_paths


def test_earlier_transition_history_and_current_effect_boundaries_remain(
    policy: pa.ProgrammePolicy,
) -> None:
    state = policy.state
    g0_id = state["gate_transition"]["transition_id"]
    g1a2_id = state["g1a_subgate_authority"]["decisive_transition_enablement_review_id"]
    g1b1 = state["g1b"]["state_transition"]
    earlier = {
        f"{pa.TRANSITION_REVIEW_ROOT}/{g0_id}.json",
        f"{pa.TRANSITION_ARTIFACT_ROOT}/{g0_id}.json",
        f"{pa.SUBGATE_REVIEW_ROOT}/{g1a2_id}.json",
        f"{pa.SUBGATE_TRANSITION_ARTIFACT_ROOT}/{g1a2_id}.json",
        f"{pa.G1A_CLOSEOUT_REVIEW_ROOT}/{g1b1['enablement_review_id']}.json",
        f"{pa.G1A_TO_G1B1_TRANSITION_ARTIFACT_ROOT}/{g1b1['transition_id']}.json",
        *pa.ACCEPTED_CUMULATIVE_HISTORY_PATHS,
    }
    assert earlier <= set(policy.full_range_allowed_paths)
    profile = policy.overlay["profiles"][pa.G1B2_ACTIVE_PROFILE]
    assert set(profile["allowed_effects"]) == pa.G1B2_ALLOWED_EFFECTS
    assert set(profile["forbidden_effects"]) == pa.G1B2_FORBIDDEN_EFFECTS
    assert "controller_policy_change" in profile["forbidden_effects"]


@pytest.mark.parametrize(
    "field,value", [("status", "pending"), ("external_review_status", "fail")]
)
def test_unaccepted_transition_state_still_fails_closed(
    policy: pa.ProgrammePolicy, field: str, value: str
) -> None:
    state = copy.deepcopy(policy.state)
    state["g1b"]["subgates"]["G1B.2"]["state_transition"][field] = value
    with pytest.raises(
        pa.ProgrammeAdmissionError, match="g1b1_to_g1b2_transition_state_invalid"
    ):
        pa._validate_state(state, ROOT)


@pytest.fixture
def synthetic_operation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, policy: pa.ProgrammePolicy
) -> dict:
    """Use real policy, contracts and decisions with explicit synthetic Git observations.

    No source or target is an executable Git worktree and no network operation is
    possible through this fixture. Source attestation and Git/remote identities
    are test doubles; this tests wrapper propagation, not pin installation.
    """
    target = tmp_path / "synthetic-target"
    source = tmp_path / "synthetic-source"
    target.mkdir()
    source.mkdir()
    for relative in [REVIEW_PATH, TRANSITION_PATH, *pa.G1B1_ALLOWED_PATHS]:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(_git_bytes("show", f"{BASE}:{relative}"))
    template = ast.parse(
        _git_bytes("show", f"{PIN}:tests/test_programme_admission.py").decode()
    )
    for name, relative in (
        ("_valid_g1b2_runtime_source", pa.G1B2_RUNTIME_PATH),
        ("_valid_g1b2_test_source", pa.G1B2_TEST_PATH),
    ):
        function = next(
            node
            for node in template.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        )
        assert len(function.body) == 1 and isinstance(function.body[0], ast.Return)
        payload = ast.literal_eval(function.body[0].value)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload.encode())
    assert pa.g1b1_kernel_contract_reasons(target) == []
    assert pa.g1b2_journal_contract_reasons(target) == []
    manifest = {
        "schema_version": pa.TASK_MANIFEST_VERSION,
        "task_id": "synthetic-g1b2-history-regression",
        "task_class": pa.G1B2_TASK_CLASS,
        "programme_gate": "G1B.2",
        "objective": "Exercise exact historical scope without granting implementation authority.",
        "base_commit": BASE,
        "candidate_or_current_head": BASE,
        "allowed_path_roots": sorted(pa.G1B2_ALLOWED_PATHS),
        "intended_side_effect_classes": sorted(pa.G1B2_ALLOWED_EFFECTS),
        "forbidden_side_effect_classes": sorted(pa.G1B2_FORBIDDEN_EFFECTS),
        "state_digest": policy.state_digest,
        "policy_digest": policy.policy_digest,
    }
    branch = "codex/raisa-ariadne-recovery-g0"
    journal_changes = [
        pa.GitPathChange("A", path, "000000", "100644")
        for path in sorted(pa.G1B2_ALLOWED_PATHS)
    ]
    history_changes = [
        pa.GitPathChange("A", path, "000000", "100644")
        for path in sorted(HISTORY_PATHS)
    ]
    observation = {
        "history": history_changes,
        "candidate": journal_changes,
        "manifest": manifest,
        "target": target,
        "source": source,
    }

    def git(root: Path, *args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return PIN if root == source else BASE
        if args == ("rev-parse", "HEAD^{tree}"):
            return (
                PIN_TREE
                if root == source
                else "e2d41bc658e836587c34bbff201462f45beca8c3"
            )
        if args == ("branch", "--show-current"):
            return "" if root == source else branch
        if args[:2] == ("rev-list", "--reverse"):
            return BASE
        if args[:2] == ("rev-list", "--count"):
            return "0"
        if args == ("status", "--porcelain", "--untracked-files=no"):
            return "A  orchestration_harness/clockwork_journal.py"
        if args == ("write-tree",):
            return "1" * 40
        raise AssertionError((root, args))

    monkeypatch.setattr(pa, "load_programme_policy", lambda _root: policy)
    monkeypatch.setattr(pa, "_run_git", git)
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(pa, "_fresh_remote_head", lambda *_args: BASE)
    monkeypatch.setattr(
        pa,
        "observe_remote_identity",
        lambda *_args: {
            "normalized_push_url": "https://example.invalid/synthetic.git",
            "remote_identity_sha256": "sha256:" + "2" * 64,
        },
    )
    monkeypatch.setattr(
        pa,
        "observe_git_administrative_identity",
        lambda *_args: {
            "git_administrative_identity_sha256": "sha256:" + "3" * 64,
        },
    )
    monkeypatch.setattr(
        pa,
        "_scope_change_inventories",
        lambda *_args, **_kwargs: (
            [*observation["history"], *observation["candidate"]],
            list(observation["candidate"]),
            [],
        ),
    )
    monkeypatch.setattr(pa, "git_change_inventory", lambda *_args: [])
    monkeypatch.setattr(pa, "git_untracked_inventory", lambda *_args: [])
    monkeypatch.setattr(
        pa.trusted_git,
        "attest_repository",
        lambda *_args, **_kwargs: {
            "trusted_git_identity_sha256": "sha256:" + "4" * 64,
        },
    )
    return observation


def _core(operation: dict) -> pa.ScopeDecision:
    return pa._evaluate_programme_operation_admission_core(
        repo_root=operation["target"],
        manifest=operation["manifest"],
        entrypoint="task_branch_commit",
        phase="development",
    )


def _wrapper(operation: dict) -> pg.PinnedGatekeeperDecision:
    return pg.evaluate_pinned_programme_operation(
        gatekeeper_root=operation["source"],
        target_repo_root=operation["target"],
        manifest=operation["manifest"],
        entrypoint="task_branch_commit",
        phase="development",
    )


@pytest.mark.parametrize("outside_history", [False, True])
def test_core_and_unchanged_wrapper_agree_on_specific_cumulative_scope(
    synthetic_operation: dict, outside_history: bool
) -> None:
    if outside_history:
        synthetic_operation["history"].append(
            pa.GitPathChange("A", UNRELATED_PATH, "000000", "100644")
        )
    expected = ["scope_path_outside_policy"] if outside_history else []
    core = _core(synthetic_operation)
    wrapper = _wrapper(synthetic_operation)
    assert core.reason_codes == expected
    assert core.admitted is (not outside_history)
    assert wrapper.reason_codes == core.reason_codes
    assert wrapper.admitted is core.admitted
    assert wrapper.scope_decision is not None
    assert wrapper.scope_decision["reason_codes"] == expected


@pytest.mark.parametrize("path", sorted(HISTORY_PATHS))
def test_historical_records_are_rejected_as_current_candidate_edits(
    synthetic_operation: dict, path: str
) -> None:
    destination = synthetic_operation["target"] / path
    destination.write_bytes(destination.read_bytes() + b"\n")
    synthetic_operation["candidate"].append(
        pa.GitPathChange("M", path, "100644", "100644")
    )
    decision = _core(synthetic_operation)
    assert decision.admitted is False
    assert decision.reason_codes == [
        "scope_tranche_path_outside_policy",
        "scope_tranche_path_outside_task_manifest",
    ]
    assert _wrapper(synthetic_operation).reason_codes == decision.reason_codes


@pytest.mark.parametrize("path", sorted(HISTORY_PATHS))
def test_historical_records_cannot_be_added_to_the_implementation_manifest(
    synthetic_operation: dict, path: str
) -> None:
    synthetic_operation["manifest"]["allowed_path_roots"].append(path)
    decision = _core(synthetic_operation)
    assert decision.admitted is False
    assert decision.reason_codes == ["task_manifest_path_outside_policy"]


def test_nonpassing_historical_review_is_rejected_before_wrapper_core(
    synthetic_operation: dict,
) -> None:
    path = synthetic_operation["target"] / REVIEW_PATH
    review = json.loads(path.read_bytes())
    review["verdict"] = "REVISION_REQUIRED"
    path.write_text(json.dumps(review), encoding="utf-8")
    decision = _wrapper(synthetic_operation)
    assert decision.admitted is False
    assert decision.reason_codes == [
        "gatekeeper_g1b1_closeout_decisive_review_not_pass"
    ]
    assert decision.scope_decision is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("enablement_review_id", "synthetic-unaccepted-review"),
        ("transition_id", "synthetic-unaccepted-transition"),
        ("reviewer_surface", "synthetic-unaccepted-reviewer"),
        ("enablement_candidate_commit", "1" * 40),
        ("enablement_candidate_tree", "2" * 40),
        ("blocking_finding_count", False),
        ("enablement_review_id", None),
        ("transition_id", []),
        ("enablement_candidate_commit", None),
        ("enablement_candidate_tree", []),
    ],
)
def test_loader_rejects_transition_provenance_disagreement(
    monkeypatch: pytest.MonkeyPatch, field: str, value: object
) -> None:
    """Exercise the real loader with one inconsistent in-memory input only."""
    original = pa._strict_json
    state = original(ROOT / pa.STATE_PATH)
    state["g1b"]["subgates"]["G1B.2"]["state_transition"][field] = value

    def read(path: Path) -> dict:
        return copy.deepcopy(state) if path == ROOT / pa.STATE_PATH else original(path)

    monkeypatch.setattr(pa, "_strict_json", read)
    with pytest.raises(
        pa.ProgrammeAdmissionError,
        match="g1b2_transition_history_state_mismatch|g1b1_to_g1b2_transition_state_invalid",
    ):
        pa.load_programme_policy(ROOT)


@pytest.mark.parametrize("path", sorted(HISTORY_PATHS))
@pytest.mark.parametrize("missing", [False, True])
def test_committed_authority_records_require_exact_accepted_bytes(
    monkeypatch: pytest.MonkeyPatch,
    policy: pa.ProgrammePolicy,
    path: str,
    missing: bool,
) -> None:
    original = Path.read_bytes

    def read(candidate: Path) -> bytes:
        if candidate == ROOT / path:
            if missing:
                raise FileNotFoundError(path)
            return original(candidate) + b"\n"
        return original(candidate)

    monkeypatch.setattr(Path, "read_bytes", read)
    reason = (
        "g1b2_transition_history_missing"
        if missing
        else "g1b2_transition_history_bytes_mismatch"
    )
    with pytest.raises(pa.ProgrammeAdmissionError, match=reason):
        pa._g1b2_committed_transition_history(
            ROOT, policy.state["g1b"]["subgates"]["G1B.2"]["state_transition"]
        )


def test_unrelated_history_source_is_rejected(
    monkeypatch: pytest.MonkeyPatch, policy: pa.ProgrammePolicy
) -> None:
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: False)
    with pytest.raises(
        pa.ProgrammeAdmissionError, match="g1b2_transition_history_source_invalid"
    ):
        pa._g1b2_committed_transition_history(
            ROOT, policy.state["g1b"]["subgates"]["G1B.2"]["state_transition"]
        )


def test_prospective_transition_loads_without_granting_historical_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_git = pa._run_git

    def git(root: Path, *args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return PIN
        return original_git(root, *args)

    monkeypatch.setattr(pa, "_run_git", git)
    result = pa.load_programme_policy(ROOT)
    assert set(result.allowed_paths) == pa.G1B2_ALLOWED_PATHS
    assert HISTORY_PATHS.isdisjoint(result.full_range_allowed_paths)
