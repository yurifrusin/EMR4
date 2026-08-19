from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest

from orchestration_harness.governance_live_adoption import (
    AdoptionRejection,
    CANONICAL_KEYS,
    CommittedAdoption,
    build_generation,
    publish_live_generation,
    rollback_live_generation,
    validate_contract,
    validate_intent,
    validate_live_state,
    validate_writer_inventory,
)
from orchestration_harness.governance_writer_guard import (
    LegacyGovernanceWriterRetired,
    refuse_retired_legacy_writer,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-adoption-retirement"
CONTRACT_PATH = TOPIC / "contract.json"
INTENT_PATH = TOPIC / "closeout-intent.json"
POINTER = ROOT / "orchestration/continuity/ariadne-governance-clockwork/current.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_for_replay() -> str:
    if POINTER.is_file():
        return _json(POINTER)["previous_source_commit"]
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


@contextmanager
def _worktree(path: Path):
    source = _source_for_replay()
    branch = f"codex/clockwork-live-test-{path.name[-12:]}"
    subprocess.run(
        ["git", "worktree", "add", "-b", branch, str(path), source],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    try:
        yield path
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(path)],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "branch", "-D", branch],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )


def test_plan_and_contract_freeze_live_scope() -> None:
    plan = (ROOT / "docs/ariadne-provider-free-clockwork-live-canonical-adoption-retirement-plan.md").read_text(encoding="utf-8")
    threat = (ROOT / "docs/security/ariadne-provider-free-clockwork-live-canonical-adoption-retirement-threat-model-delta.md").read_text(encoding="utf-8")
    contract = validate_contract(_json(CONTRACT_PATH))
    intent = validate_intent(_json(INTENT_PATH), contract)
    assert "Timestamp: 2026-08-19T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    assert "Timestamp: 2026-08-19T" in threat
    assert "+10:00 (Australia/Brisbane)" in threat
    assert contract["required_ancestor"] == "a6129d9a0c391314691cb73b28a5f21f1e834654"
    assert contract["accepted_rehearsal_source"] == "d03cc6386fdf3e2714881089514380d93824e160"
    assert intent["transaction_manifest"]["node"]["relationships"] == [{
        "node_id": "ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal",
        "relation": "builds_on",
    }]
    assert not (ROOT / "scripts/ariadne_provider_free_clockwork_live_canonical_adoption_retirement_continuity_update.py").exists()


def test_contract_and_intent_reject_derived_or_unsafe_input() -> None:
    contract = _json(CONTRACT_PATH)
    bad_contract = json.loads(json.dumps(contract))
    bad_contract["required_ancestor"] = "a6129d9"
    with pytest.raises(AdoptionRejection, match="contract_oid"):
        validate_contract(bad_contract)
    bad_contract = json.loads(json.dumps(contract))
    bad_contract["canonical_paths"]["continuity"] = "docs/branding/escape.json"
    with pytest.raises(AdoptionRejection, match="contract_path"):
        validate_contract(bad_contract)
    good = validate_contract(contract)
    bad_intent = _json(INTENT_PATH)
    bad_intent["source_commit"] = "a" * 40
    with pytest.raises(AdoptionRejection, match="intent_keys"):
        validate_intent(bad_intent, good)


def test_writer_inventory_and_guard_coverage_are_complete() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    inventory = validate_writer_inventory(ROOT, contract)
    assert inventory["historical_updater_count"] == 145
    assert inventory["shared_compass_guard_count"] == 137
    assert len(inventory["explicit_entry_guard_paths"]) == 8
    assert len(inventory["legacy_writer_classes"]) == 4


def test_main_state_is_preparable_or_active() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    if POINTER.is_file():
        state = validate_live_state(ROOT, contract)
        assert state["status"] == "passed"
        assert state["clockwork_owned_surfaces"] == 10
        assert state["retired_legacy_writer_classes"] == 4
    else:
        prepared = build_generation(ROOT, contract, _json(INTENT_PATH))
        assert prepared["generation_manifest"]["generation_id"].startswith("gen-")
        assert prepared["pointer"]["phase"] == "clockwork_active"
        assert len(json.loads(prepared["metadata"]["ownership.json"])["surface_owners"]) == 10


def test_generation_is_stable_across_git_clean_line_endings(tmp_path: Path) -> None:
    with _worktree(tmp_path / "line-endings") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _json(worktree / INTENT_PATH.relative_to(ROOT))
        expected = build_generation(worktree, contract, intent)
        baton = worktree / contract["canonical_paths"]["current_baton"]
        normalized = baton.read_bytes().replace(b"\r\n", b"\n")
        baton.write_bytes(normalized.replace(b"\n", b"\r\n"))
        clean = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(baton)],
            cwd=worktree,
        )
        assert clean.returncode == 0
        observed = build_generation(worktree, contract, intent)
        assert observed["generation_manifest"] == expected["generation_manifest"]
        assert observed["canonical"] == expected["canonical"]


def test_all_pre_pointer_faults_restore_and_disposable_rollback_is_exact(
    tmp_path: Path,
) -> None:
    with _worktree(tmp_path / "fault-and-rollback") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _json(worktree / INTENT_PATH.relative_to(ROOT))
        prepared = build_generation(worktree, contract, intent)
        canonical_before = {
            key: (worktree / relative).read_bytes()
            for key, relative in contract["canonical_paths"].items()
        }
        checkpoints = [
            point
            for key in CANONICAL_KEYS
            for point in (f"before:{key}", f"after:{key}")
        ] + ["before_pointer_replace"]
        for checkpoint in checkpoints:
            with pytest.raises(OSError, match="injected_precommit_failure"):
                publish_live_generation(
                    worktree,
                    prepared,
                    writer_id="clockwork",
                    fail_at=checkpoint,
                )
            assert {
                key: (worktree / relative).read_bytes()
                for key, relative in contract["canonical_paths"].items()
            } == canonical_before
            clockwork_root = worktree / contract["clockwork_root"]
            assert not (clockwork_root / "current.json").exists()
            assert not (clockwork_root / "writer.lock").exists()
        active = publish_live_generation(worktree, prepared, writer_id="clockwork")
        assert active["clockwork_owned_surfaces"] == 10
        rolled_back = rollback_live_generation(
            worktree, contract, writer_id="clockwork"
        )
        assert rolled_back["byte_exact"] is True
        assert {
            key: (worktree / relative).read_bytes()
            for key, relative in contract["canonical_paths"].items()
        } == canonical_before
        restored = publish_live_generation(worktree, prepared, writer_id="clockwork")
        assert restored["generation_id"] == active["generation_id"]
        assert restored["canonical_drift"] == 0


def test_post_pointer_commit_guard_and_manual_drift_detection(tmp_path: Path) -> None:
    with _worktree(tmp_path / "post-pointer") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        prepared = build_generation(
            worktree,
            contract,
            _json(worktree / INTENT_PATH.relative_to(ROOT)),
        )
        with pytest.raises(CommittedAdoption, match="injected_postcommit_failure"):
            publish_live_generation(
                worktree,
                prepared,
                writer_id="clockwork",
                fail_at="after_pointer_replace",
            )
        assert validate_live_state(worktree, contract)["status"] == "passed"
        with pytest.raises(LegacyGovernanceWriterRetired, match="legacy_governance_writer_retired"):
            refuse_retired_legacy_writer(worktree, "example_continuity_update.py")
        refuse_retired_legacy_writer(worktree, "read_only_probe.py")
        target = worktree / contract["canonical_paths"]["active_latch"]
        target.write_bytes(target.read_bytes() + b"\n")
        with pytest.raises(AdoptionRejection, match="canonical_drift"):
            validate_live_state(worktree, contract)
