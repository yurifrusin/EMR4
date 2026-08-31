import argparse
import ast
import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import orchestration_harness.programme_admission as programme_admission
from orchestration_harness import trusted_git
from scripts import agent_worktrees, ariadne_antigravity
from scripts.agent_worktrees import (
    HANDOFF_REF,
    build_parser,
    create_codex_review_packet,
    read_task_status,
    task_completion_notes,
)


BASE_COMMIT = "29b07cc8c70dd5813d59d99fb2be113a88dd55e2"
_REAL_SUBPROCESS_RUN = subprocess.run


def test_review_packet_copies_worker_completion_notes(tmp_path):
    task = tmp_path / "worker-task.md"
    task.write_text(
        """# worker-task

## Completion Notes

- Files changed:
  - `seed.py`
- Verification run:
  - `pytest tests/test_diary_roster.py` -> 18 passed
- Remaining risks:
  - Test DB teardown can deadlock under rapid reruns.
""",
        encoding="utf-8",
    )

    notes = task_completion_notes(task)
    path = create_codex_review_packet(
        "claude",
        "worker-task",
        "claude/current",
        "Ready for review",
        notes,
        tmp_path,
    )

    text = path.read_text(encoding="utf-8")
    assert "## Worker Completion Notes" in text
    assert "`seed.py`" in text
    assert "18 passed" in text
    assert "teardown can deadlock" in text


def test_placeholder_completion_notes_are_treated_as_empty(tmp_path):
    task = tmp_path / "worker-task.md"
    task.write_text(
        """# worker-task

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
""",
        encoding="utf-8",
    )

    assert task_completion_notes(task) == ""


def test_read_task_status_tolerates_legacy_non_utf8_bytes(tmp_path):
    task = tmp_path / "legacy-packet.md"
    task.write_bytes(
        b"""# legacy-packet

| Item | Value |
|---|---|
| Status | queued |

Legacy smart dash byte: \x97
"""
    )

    assert read_task_status(task) == "queued"


def test_realign_defaults_to_handoff_ref():
    parser = build_parser()

    args = parser.parse_args(["realign", "--agent", "claude"])

    assert args.ref == HANDOFF_REF
    assert args.no_push is False


def test_realign_accepts_explicit_ref_override():
    parser = build_parser()

    args = parser.parse_args(
        ["realign", "--agent", "claude", "--ref", "custom/ref", "--no-push"]
    )

    assert args.ref == "custom/ref"
    assert args.no_push is True


def _git(root: Path, *argv: str) -> str:
    completed = _REAL_SUBPROCESS_RUN(
        ["git", *argv],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def _candidate_repository(tmp_path: Path, name: str = "candidate") -> tuple[Path, str]:
    root = tmp_path / name
    root.mkdir()
    _git(root, "init", "-b", "codex/integration-candidate")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G1A3 R1 Tests")
    _git(root, "config", "core.autocrlf", "false")
    (root / "AGENTS.md").write_bytes(b"synthetic candidate authority\n")
    (root / "seed.py").write_bytes(b"VALUE = 'reviewed'\n")
    (root / ".gitignore").write_bytes(b"*.ignored\n")
    _git(root, "add", "AGENTS.md", "seed.py", ".gitignore")
    _git(root, "commit", "-m", "seed candidate")
    return root, _git(root, "rev-parse", "HEAD")


def _canonical_digest(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _candidate_projections(root: Path, commit: str) -> tuple[dict, dict]:
    identity = trusted_git.attest_repository(
        root,
        attested_paths=["AGENTS.md"],
        expected_commit=commit,
        complete_tracked_tree=True,
    )
    complete = identity["complete_tracked_tree_attestation"]
    attestation = {
        "head": identity["head"],
        "head_tree": identity["head_tree"],
        "index_tree": identity["index_tree"],
        "complete_tracked_tree_sha256": complete["complete_tracked_tree_sha256"],
        "complete_tracked_path_count": complete["complete_tracked_path_count"],
        "trusted_git_identity_sha256": identity["trusted_git_identity_sha256"],
    }
    inventory = {
        "ordinary_count": 0,
        "ordinary_paths_sha256": _canonical_digest([]),
        "ignored_count": 0,
        "ignored_paths_sha256": _canonical_digest([]),
    }
    return attestation, inventory


def _assessment() -> dict[str, object]:
    return {
        "artifact_kind": "decision",
        "artifact_valid": True,
        "review_verdict": "pass",
        "integration_authorized": True,
        "canonical_marker": "DECISION: PASS",
        "reason_code": "terminal_marker_observed",
    }


def _worker_receipt(root: Path, commit: str, *, commands: bool = False) -> dict:
    attestation, inventory = _candidate_projections(root, commit)
    review = "Synthetic complete review passed."
    receipt = {
        "schema_version": "ariadne.worker_receipt.v1",
        "status": "completed",
        "transport": "antigravity_new_project_bound_readonly_worktree",
        "model": "gemini-3.7-flash-high",
        "requested_model": "gemini-3.7-flash-high",
        "reasoning_effort": "high",
        "decision": "pass",
        "decision_contract": "schema_constrained_json_v1",
        "worktree": str(root.resolve()),
        "branch": "codex/integration-candidate",
        "head_before": commit,
        "head_after": commit,
        "dirty_after": False,
        "os_sandbox": False,
        "orchestrator_receipt_sha256": "1" * 64,
        "result": review,
        "decision_envelope": {
            "decision": "pass",
            "review": review,
            "verdict_assessment": _assessment(),
        },
        "complete_review_attestation_before": copy.deepcopy(attestation),
        "complete_review_attestation_after": copy.deepcopy(attestation),
        "nontracked_inventory_before": copy.deepcopy(inventory),
        "nontracked_inventory_after": copy.deepcopy(inventory),
    }
    if commands:
        command_results = [
            {"id": "TEST", "argv": ["python", "-m", "pytest"], "exit_code": 0}
        ]
        receipt["command_manifest_sha256"] = "2" * 64
        receipt["command_results"] = command_results
        receipt["decision_envelope"]["command_results"] = copy.deepcopy(command_results)
    return receipt


def _write_receipt(path: Path, receipt: dict) -> None:
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def _integration_args(receipt_path: Path, commit: str) -> argparse.Namespace:
    return argparse.Namespace(
        agent="codex",
        task="synthetic-g1a3-r1",
        branch="codex/integration-candidate",
        review=str(receipt_path.resolve()),
        integration_commit=commit,
        result="integrated",
        follow_up="external G1A.3-R1 review",
        programme_task_manifest=None,
    )


def _admit_consumer_without_real_log(
    monkeypatch: pytest.MonkeyPatch,
) -> list[dict[str, object]]:
    appended: list[dict[str, object]] = []
    monkeypatch.setattr(
        agent_worktrees,
        "_require_command_admission",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        agent_worktrees,
        "append_integration_log",
        lambda **kwargs: appended.append(kwargs),
    )
    return appended


def test_record_integration_admission_is_first_and_denial_reads_no_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    observed: list[str] = []

    def _deny(*_args, **_kwargs) -> None:
        observed.append("admission")
        raise RuntimeError("integration closed")

    monkeypatch.setattr(agent_worktrees, "_require_command_admission", _deny)
    monkeypatch.setattr(
        agent_worktrees,
        "append_integration_log",
        lambda **_kwargs: pytest.fail("ledger must not be touched"),
    )
    args = _integration_args(tmp_path / "missing-receipt.json", "a" * 40)

    with pytest.raises(RuntimeError, match="integration closed"):
        agent_worktrees.record_integration(args)

    assert observed == ["admission"]


@pytest.mark.parametrize("commands", [False, True])
def test_record_integration_accepts_only_fresh_complete_bound_receipt_and_derives_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, commands: bool
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt_path = tmp_path / "external-worker-receipt.json"
    receipt = _worker_receipt(root, commit, commands=commands)
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)
    observed_git: list[tuple[str, ...]] = []
    real_run_git = trusted_git.run_git
    real_run_git_bytes = trusted_git.run_git_bytes

    def _observed_run_git(candidate_root: Path, *argv: str, **kwargs):
        observed_git.append(argv)
        return real_run_git(candidate_root, *argv, **kwargs)

    def _observed_run_git_bytes(candidate_root: Path, *argv: str, **kwargs):
        observed_git.append(argv)
        return real_run_git_bytes(candidate_root, *argv, **kwargs)

    monkeypatch.setattr(trusted_git, "run_git", _observed_run_git)
    monkeypatch.setattr(trusted_git, "run_git_bytes", _observed_run_git_bytes)

    agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert len(appended) == 1
    row = appended[0]
    assert row["result"] == "integrated"
    assert row["integration_commit"] == commit
    audit = json.loads(row["review"])
    assert audit["authority_contract"] == (
        "canonical_g1a3_r1_complete_review_binding_v1"
    )
    assert audit["candidate_tree"] == _git(root, "rev-parse", "HEAD^{tree}")
    assert audit["complete_tracked_path_count"] == 3
    assert audit["ordinary_untracked_count"] == 0
    assert audit["ignored_untracked_count"] == 0
    assert audit["worker_receipt_sha256"].startswith("sha256:")
    assert str(receipt_path) not in row["review"]
    assert (audit["command_manifest_sha256"] is not None) is commands
    assert (audit["command_results_sha256"] is not None) is commands
    forbidden = {
        "add",
        "branch",
        "checkout",
        "clean",
        "commit",
        "merge",
        "push",
        "reset",
        "update-ref",
        "worktree",
    }
    assert all(not forbidden.intersection(argv) for argv in observed_git)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_complete",
        "extra_top_level",
        "attestation_extra",
        "uppercase_digest",
        "boolean_path_count",
        "before_after_attestation",
        "boolean_inventory_count",
        "raw_inventory_digest",
        "before_after_inventory",
        "legacy_receipt",
        "negative_decision",
        "head_mismatch",
        "branch_mismatch",
        "nonzero_command",
        "duplicate_key",
        "nan",
    ],
)
def test_record_integration_rejects_malformed_noncanonical_or_nonpass_receipts_without_log(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt_path = tmp_path / "external-worker-receipt.json"
    receipt = _worker_receipt(root, commit, commands=mutation == "nonzero_command")
    args = _integration_args(receipt_path, commit)
    if mutation == "missing_complete":
        del receipt["complete_review_attestation_after"]
    elif mutation == "extra_top_level":
        receipt["unexpected"] = True
    elif mutation == "attestation_extra":
        receipt["complete_review_attestation_before"]["paths"] = []
    elif mutation == "uppercase_digest":
        receipt["complete_review_attestation_before"][
            "complete_tracked_tree_sha256"
        ] = "sha256:" + "A" * 64
    elif mutation == "boolean_path_count":
        receipt["complete_review_attestation_before"]["complete_tracked_path_count"] = (
            True
        )
    elif mutation == "before_after_attestation":
        receipt["complete_review_attestation_after"]["trusted_git_identity_sha256"] = (
            "sha256:" + "e" * 64
        )
    elif mutation == "boolean_inventory_count":
        receipt["nontracked_inventory_before"]["ordinary_count"] = False
    elif mutation == "raw_inventory_digest":
        receipt["nontracked_inventory_before"]["ordinary_paths_sha256"] = "4" * 64
    elif mutation == "before_after_inventory":
        receipt["nontracked_inventory_after"]["ordinary_count"] = 1
    elif mutation == "legacy_receipt":
        for key in (
            "complete_review_attestation_before",
            "complete_review_attestation_after",
            "nontracked_inventory_before",
            "nontracked_inventory_after",
        ):
            del receipt[key]
    elif mutation == "negative_decision":
        receipt["decision"] = "revision_required"
    elif mutation == "head_mismatch":
        receipt["head_after"] = "e" * 40
    elif mutation == "branch_mismatch":
        args.branch = "codex/other"
    elif mutation == "nonzero_command":
        receipt["command_results"][0]["exit_code"] = 1
        receipt["decision_envelope"]["command_results"][0]["exit_code"] = 1
    if mutation == "duplicate_key":
        rendered = json.dumps(receipt)
        receipt_path.write_text(
            '{"status":"completed",' + rendered[1:], encoding="utf-8"
        )
    elif mutation == "nan":
        rendered = json.dumps(receipt)
        receipt_path.write_text(
            rendered.replace('"os_sandbox": false', '"os_sandbox": NaN'),
            encoding="utf-8",
        )
    else:
        _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit) as error:
        agent_worktrees.record_integration(args)

    assert error.value.code == 1
    assert appended == []


@pytest.mark.parametrize(
    "missing_key",
    [
        "complete_review_attestation_before",
        "complete_review_attestation_after",
        "nontracked_inventory_before",
        "nontracked_inventory_after",
    ],
)
def test_record_integration_rejects_each_missing_complete_review_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, missing_key: str
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt = _worker_receipt(root, commit)
    del receipt[missing_key]
    receipt_path = tmp_path / "external-worker-receipt.json"
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit):
        agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert appended == []


@pytest.mark.parametrize(
    "object_key",
    [
        "complete_review_attestation_before",
        "complete_review_attestation_after",
        "nontracked_inventory_before",
        "nontracked_inventory_after",
    ],
)
def test_record_integration_rejects_extra_key_in_each_complete_review_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, object_key: str
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt = _worker_receipt(root, commit)
    receipt[object_key]["forbidden_extra"] = True
    receipt_path = tmp_path / "external-worker-receipt.json"
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit):
        agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert appended == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("head", "short"),
        ("head_tree", 7),
        ("index_tree", "e" * 40),
        ("complete_tracked_tree_sha256", "3" * 64),
        ("complete_tracked_tree_sha256", "sha256:" + "A" * 64),
        ("complete_tracked_path_count", True),
        ("complete_tracked_path_count", 0),
        ("complete_tracked_path_count", -1),
        ("complete_tracked_path_count", "3"),
        ("trusted_git_identity_sha256", "sha256:" + "A" * 64),
    ],
)
def test_record_integration_rejects_each_malformed_attestation_field_type_or_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt = _worker_receipt(root, commit)
    receipt["complete_review_attestation_before"][field] = value
    receipt_path = tmp_path / "external-worker-receipt.json"
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit):
        agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert appended == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("head", "e" * 40),
        ("head_tree", "e" * 40),
        ("index_tree", "e" * 40),
        ("complete_tracked_tree_sha256", "sha256:" + "e" * 64),
        ("complete_tracked_path_count", 4),
        ("trusted_git_identity_sha256", "sha256:" + "e" * 64),
    ],
)
def test_record_integration_rejects_before_after_inequality_for_each_attestation_field(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt = _worker_receipt(root, commit)
    receipt["complete_review_attestation_after"][field] = value
    receipt_path = tmp_path / "external-worker-receipt.json"
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit):
        agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert appended == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ordinary_count", 1),
        ("ignored_count", 1),
        ("ordinary_count", True),
        ("ignored_count", False),
        ("ordinary_paths_sha256", "sha256:" + "e" * 64),
        ("ignored_paths_sha256", "sha256:" + "e" * 64),
    ],
)
def test_record_integration_rejects_nonempty_or_noncanonical_review_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt = _worker_receipt(root, commit)
    receipt["nontracked_inventory_before"][field] = value
    receipt["nontracked_inventory_after"][field] = value
    receipt_path = tmp_path / "external-worker-receipt.json"
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit):
        agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert appended == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("head_tree", "e" * 40),
        ("complete_tracked_tree_sha256", "sha256:" + "e" * 64),
        ("complete_tracked_path_count", 4),
        ("trusted_git_identity_sha256", "sha256:" + "e" * 64),
    ],
)
def test_record_integration_rejects_valid_looking_review_projection_that_differs_fresh(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt = _worker_receipt(root, commit)
    for key in (
        "complete_review_attestation_before",
        "complete_review_attestation_after",
    ):
        receipt[key][field] = value
        if field == "head_tree":
            receipt[key]["index_tree"] = value
    receipt_path = tmp_path / "external-worker-receipt.json"
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit):
        agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert appended == []


def test_record_integration_detects_same_size_restored_mtime_physical_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt = _worker_receipt(root, commit)
    tracked = root / "seed.py"
    original = tracked.stat()
    tracked.write_bytes(b"VALUE = 'mutated!'\n")
    assert tracked.stat().st_size == original.st_size
    tracked.touch()
    os.utime(tracked, ns=(original.st_atime_ns, original.st_mtime_ns))
    receipt_path = tmp_path / "external-worker-receipt.json"
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit):
        agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert appended == []


@pytest.mark.parametrize(
    "drift_surface",
    [
        "tracked",
        "index",
        "config",
        "trustctime",
        "branch",
        "ordinary",
        "ignored",
        "copied_worktree",
        "copied_commit",
    ],
)
def test_record_integration_rejects_every_fresh_candidate_or_inventory_drift_without_log(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    drift_surface: str,
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt_path = tmp_path / "external-worker-receipt.json"
    receipt = _worker_receipt(root, commit)
    if drift_surface == "tracked":
        (root / "seed.py").write_bytes(b"VALUE = 'mutated'\n")
    elif drift_surface == "index":
        (root / "seed.py").write_bytes(b"VALUE = 'indexed'\n")
        _git(root, "add", "seed.py")
    elif drift_surface == "config":
        _git(root, "config", "core.checkStat", "minimal")
    elif drift_surface == "trustctime":
        _git(root, "config", "core.trustctime", "false")
    elif drift_surface == "branch":
        _git(root, "checkout", "-b", "codex/other-branch")
    elif drift_surface == "ordinary":
        (root / "ordinary.tmp").write_bytes(b"ordinary\n")
    elif drift_surface == "ignored":
        (root / "secret.ignored").write_bytes(b"ignored\n")
    elif drift_surface == "copied_worktree":
        other, _other_commit = _candidate_repository(tmp_path, "other-candidate")
        receipt["worktree"] = str(other.resolve())
    elif drift_surface == "copied_commit":
        (root / "second.py").write_bytes(b"SECOND = True\n")
        _git(root, "add", "second.py")
        _git(root, "commit", "-m", "advance candidate")
    _write_receipt(receipt_path, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit) as error:
        agent_worktrees.record_integration(_integration_args(receipt_path, commit))

    assert error.value.code == 1
    assert appended == []


def test_record_integration_rejects_relative_or_candidate_local_receipt_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, commit = _candidate_repository(tmp_path)
    receipt = _worker_receipt(root, commit)
    candidate_receipt = root / "receipt.json"
    _write_receipt(candidate_receipt, receipt)
    appended = _admit_consumer_without_real_log(monkeypatch)
    relative_args = _integration_args(tmp_path / "placeholder.json", commit)
    relative_args.review = "relative.json"

    for args in (relative_args, _integration_args(candidate_receipt, commit)):
        with pytest.raises(SystemExit):
            agent_worktrees.record_integration(args)

    assert appended == []


def test_mocked_producer_receipt_is_consumed_end_to_end_with_both_admissions_mocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, commit = _candidate_repository(tmp_path)
    evidence = tmp_path / "external-evidence"
    evidence.mkdir()
    packet = evidence / "packet.md"
    packet.write_text("Synthetic review only.", encoding="utf-8")
    orchestrator = evidence / "orchestrator.json"
    orchestrator.write_text(
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
    worker_receipt = evidence / "worker.json"
    admissions: list[str] = []
    monkeypatch.setattr(
        ariadne_antigravity,
        "require_programme_admission",
        lambda **_kwargs: admissions.append("provider"),
    )

    def _provider_or_git(command, *args, **kwargs):
        if command and command[0] == "agy":
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps(
                    {"decision": "pass", "review": "Synthetic end-to-end pass."}
                ),
                stderr="",
            )
        return _REAL_SUBPROCESS_RUN(command, *args, **kwargs)

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _provider_or_git)
    produced = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=root,
        output_path=worker_receipt,
        orchestrator_receipt_path=orchestrator,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )
    appended: list[dict[str, object]] = []
    monkeypatch.setattr(
        agent_worktrees,
        "_require_command_admission",
        lambda *_args, **_kwargs: admissions.append("integration"),
    )
    monkeypatch.setattr(
        agent_worktrees,
        "append_integration_log",
        lambda **kwargs: appended.append(kwargs),
    )

    agent_worktrees.record_integration(_integration_args(worker_receipt, commit))

    assert (
        produced["complete_review_attestation_before"]
        == produced["complete_review_attestation_after"]
    )
    assert (
        produced["nontracked_inventory_before"]
        == produced["nontracked_inventory_after"]
    )
    assert admissions == ["provider", "integration"]
    assert len(appended) == 1
    assert appended[0]["result"] == "integrated"


@pytest.mark.parametrize("mutation", ["receipt", "physical"])
def test_mutation_between_mocked_producer_and_consumer_prevents_end_to_end_append(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    root, commit = _candidate_repository(tmp_path)
    evidence = tmp_path / "external-evidence"
    evidence.mkdir()
    packet = evidence / "packet.md"
    packet.write_text("Synthetic review only.", encoding="utf-8")
    orchestrator = evidence / "orchestrator.json"
    orchestrator.write_text(
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
    worker_receipt = evidence / "worker.json"
    monkeypatch.setattr(
        ariadne_antigravity,
        "require_programme_admission",
        lambda **_kwargs: None,
    )

    def _provider_or_git(command, *args, **kwargs):
        if command and command[0] == "agy":
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps(
                    {"decision": "pass", "review": "Synthetic mutation test."}
                ),
                stderr="",
            )
        return _REAL_SUBPROCESS_RUN(command, *args, **kwargs)

    monkeypatch.setattr(ariadne_antigravity.subprocess, "run", _provider_or_git)
    ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=root,
        output_path=worker_receipt,
        orchestrator_receipt_path=orchestrator,
        model="gemini-3.7-flash-high",
        os_sandbox=False,
    )
    if mutation == "receipt":
        receipt = json.loads(worker_receipt.read_text(encoding="utf-8"))
        receipt["result"] = "Tampered review."
        _write_receipt(worker_receipt, receipt)
    else:
        (root / "seed.py").write_bytes(b"VALUE = 'mutated'\n")
    appended = _admit_consumer_without_real_log(monkeypatch)

    with pytest.raises(SystemExit):
        agent_worktrees.record_integration(_integration_args(worker_receipt, commit))

    assert appended == []


def _function(module: ast.Module, name: str) -> ast.FunctionDef:
    return next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


@pytest.mark.parametrize(
    ("path", "function_name", "first_call"),
    [
        (
            "scripts/ariadne_antigravity.py",
            "run_worker",
            "require_programme_admission",
        ),
        (
            "scripts/agent_worktrees.py",
            "record_integration",
            "_require_command_admission",
        ),
    ],
)
def test_production_change_is_body_only_and_admission_remains_first(
    path: str, function_name: str, first_call: str
) -> None:
    root = Path(__file__).resolve().parents[1]
    baseline_source = _git(root, "show", f"{BASE_COMMIT}:{path}")
    current_source = (root / path).read_text(encoding="utf-8")
    baseline = ast.parse(baseline_source)
    current = ast.parse(current_source)
    baseline_function = _function(baseline, function_name)
    current_function = _function(current, function_name)
    assert ast.dump(baseline_function.args, include_attributes=False) == ast.dump(
        current_function.args, include_attributes=False
    )
    baseline_function.body = [ast.Pass()]
    current_function.body = [ast.Pass()]
    assert ast.dump(baseline, include_attributes=False) == ast.dump(
        current, include_attributes=False
    )
    actual_function = _function(ast.parse(current_source), function_name)
    first = actual_function.body[0]
    assert isinstance(first, ast.Expr)
    assert isinstance(first.value, ast.Call)
    assert isinstance(first.value.func, ast.Name)
    assert first.value.func.id == first_call


def test_current_g1a3_r1_source_contracts_accept_both_producer_and_consumer() -> None:
    root = Path(__file__).resolve().parents[1]

    assert programme_admission.g1a3_review_producer_contract_reasons(root) == []
    assert programme_admission.g1a3_integration_contract_reasons(root) == []
