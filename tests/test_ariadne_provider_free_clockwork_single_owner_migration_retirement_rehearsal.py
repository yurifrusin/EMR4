from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest
from unittest.mock import patch

from orchestration_harness.governance_migration import (
    CommittedCutover, MigrationRejection, WRITER, assess_rehearsal,
    build_clockwork_generation, initialize_mirror, publish_generation,
    switch_generation, validate_contract, validate_intent, validate_mirror,
)
from scripts.ariadne_provider_free_clockwork_single_owner_migration_retirement_rehearsal import main as runner_main


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal"
CONTRACT_PATH = TOPIC / "contract.json"
INTENT_PATH = TOPIC / "closeout-intent.json"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
PREPLAN = ROOT / "orchestration/agent_inbox/codex/ariadne-clockwork-single-owner-migration-retirement-rehearsal-preplanning-runtime-state.json"
REVIEWED_HEAD = "d03cc6386fdf3e2714881089514380d93824e160"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _construction_snapshot(repo_root: Path, contract: dict) -> tuple[dict[str, str], dict[str, str]]:
    readings = {
        name: subprocess.run(
            ["git", "show", f"{REVIEWED_HEAD}:{path}"], cwd=repo_root,
            check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout
        for name, path in contract["oracle_paths"].items()
    }
    digests = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in readings.items()}
    return readings, digests


def _state(tmp_path: Path):
    contract = validate_contract(_load(CONTRACT_PATH))
    intent = validate_intent(_load(INTENT_PATH), contract)
    with patch("orchestration_harness.governance_migration._snapshot", side_effect=_construction_snapshot):
        initialized = initialize_mirror(ROOT, tmp_path / "mirror", contract)
        generation = build_clockwork_generation(ROOT, contract, intent, initialized["oracle"]["generation_id"])
    return contract, initialized, generation


def test_plan_receipt_latch_and_parallelism_are_frozen() -> None:
    plan = (ROOT / "docs/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal-plan.md").read_text(encoding="utf-8")
    threat = (ROOT / "docs/security/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal-threat-model-delta.md").read_text(encoding="utf-8")
    receipt = _load(ROOT / "orchestration/agent_inbox/codex/ariadne-clockwork-single-owner-migration-retirement-rehearsal-preplanning-receipt.json")
    historical_latch = _load(PREPLAN)["active_operation"]
    live_latch = _load(LATCH)
    assert "950 physical lines" in plan and "AER-0643 through AER-0651" in plan
    assert "zero dual-owned surfaces" in threat
    assert receipt["status"] == "passed" and receipt["rehydrated_from_receipt"]
    assert set(receipt["rehydration_sources"]) == {"live_handover_current_baton", "current_authority_allocation", "active_plan_and_acceptance", "protected_evidence_boundaries", "git_refs_and_worktree"}
    assert historical_latch["operation_id"] == receipt["active_operation"]["operation_id"]
    assert historical_latch["status"] == "in_progress" and not historical_latch["terminal_response"]["permitted"]
    assert live_latch["status"] == "blocked" and live_latch["terminal_response"]["permitted"]
    lanes = {item["lane_id"]: item["disposition"] for item in receipt["parallelism_assessment"]["lanes"]}
    assert lanes == {"deepseek_flash": "declined", "gemini_verifier": "reserved", "native_subagents": "declined"}


def test_contract_and_intent_exclude_all_derived_bindings() -> None:
    contract = validate_contract(_load(CONTRACT_PATH))
    intent = validate_intent(_load(INTENT_PATH), contract)
    assert contract["observed_incident_ids"] == [f"AER-{number:04d}" for number in range(643, 652)]
    assert "source_commit" not in json.dumps(intent) and "register_revision" not in json.dumps(intent)
    hostile = copy.deepcopy(_load(INTENT_PATH))
    hostile["source_commit"] = "0" * 40
    with pytest.raises(MigrationRejection, match="intent_keys"):
        validate_intent(hostile, contract)
    abbreviated = copy.deepcopy(_load(CONTRACT_PATH))
    abbreviated["required_ancestor"] = abbreviated["required_ancestor"][:7]
    with pytest.raises(MigrationRejection, match="contract_oid"):
        validate_contract(abbreviated)


def test_clean_closeout_derives_full_source_and_preserves_register_bytes(tmp_path: Path) -> None:
    contract, initialized, generation = _state(tmp_path)
    assert re.fullmatch(r"[0-9a-f]{40}", generation["source_commit"])
    assert generation["previous_generation_id"] == initialized["oracle"]["generation_id"]
    oracle_files = initialized["oracle"]["files"]
    assert generation["files"]["error-register.json"] == oracle_files["error-register.json"]
    assert generation["files"]["pattern-report.json"] == oracle_files["pattern-report.json"]
    baton = json.loads(generation["files"]["current-baton.json"])
    graph = json.loads(generation["files"]["continuity.json"])
    compass = json.loads(generation["files"]["compass.json"])
    assert baton["continuity_revision"] == graph["graph_revision"]
    assert baton["compass_revision"] == compass["map_revision"]
    assert baton["source_commit"] == generation["source_commit"]
    assert contract["surfaces"] == list(json.loads(generation["files"]["ownership.json"])["surface_owners"])


def test_cutover_has_one_owner_and_rejects_legacy_stale_or_occupied_writers(tmp_path: Path) -> None:
    contract, initialized, generation = _state(tmp_path)
    mirror = tmp_path / "mirror"
    with pytest.raises(MigrationRejection, match="writer_not_clockwork"):
        publish_generation(ROOT, mirror, contract, generation, writer_id="legacy")
    (mirror / "lease.json").write_text("{}", encoding="utf-8")
    with pytest.raises(MigrationRejection, match="lease_occupied"):
        publish_generation(ROOT, mirror, contract, generation, writer_id=WRITER)
    (mirror / "lease.json").unlink()
    pointer = publish_generation(ROOT, mirror, contract, generation, writer_id=WRITER)
    assert pointer["phase"] == "clockwork_active"
    ownership = json.loads(validate_mirror(mirror)["files"]["ownership.json"])
    assert set(ownership["surface_owners"].values()) == {WRITER}
    assert set(ownership["legacy_writers"].values()) == {"retired_in_mirror"}
    with pytest.raises(MigrationRejection, match="stale_generation_or_source"):
        publish_generation(ROOT, mirror, contract, generation, writer_id=WRITER)
    assert initialized["oracle"]["generation_id"] == pointer["previous_generation_id"]


def test_path_source_and_protected_ref_drift_fail_before_publication(tmp_path: Path) -> None:
    contract, _, generation = _state(tmp_path)
    with pytest.raises(MigrationRejection, match="mirror_target"):
        initialize_mirror(ROOT, ROOT / "forbidden-migration-mirror", contract)
    stale = copy.deepcopy(generation)
    stale["source_commit"] = "0" * 40
    with pytest.raises(MigrationRejection, match="source_or_protected_refs"):
        publish_generation(ROOT, tmp_path / "mirror", contract, stale, writer_id=WRITER)
    original = __import__("orchestration_harness.governance_migration", fromlist=["_git"])._git
    def drift(root: Path, *args: str) -> str:
        return "0" * 40 if args == ("rev-parse", "master") else original(root, *args)
    with patch("orchestration_harness.governance_migration._git", side_effect=drift):
        with pytest.raises(MigrationRejection, match="source_or_protected_refs"):
            publish_generation(ROOT, tmp_path / "mirror", contract, generation, writer_id=WRITER)


def test_precommit_faults_preserve_old_generation_and_postcommit_is_explicit(tmp_path: Path) -> None:
    contract, initialized, generation = _state(tmp_path)
    mirror = tmp_path / "mirror"
    with pytest.raises(OSError, match="injected_precommit_failure"):
        publish_generation(ROOT, mirror, contract, generation, writer_id=WRITER, fail_at="after:continuity.json")
    assert validate_mirror(mirror)["pointer"]["selected_generation_id"] == initialized["oracle"]["generation_id"]
    assert not (mirror / "lease.json").exists()
    with patch("orchestration_harness.governance_migration._snapshot", side_effect=_construction_snapshot):
        generation = build_clockwork_generation(ROOT, contract, validate_intent(_load(INTENT_PATH), contract), initialized["oracle"]["generation_id"])
    with pytest.raises(CommittedCutover, match="injected_postcommit_failure"):
        publish_generation(ROOT, mirror, contract, generation, writer_id=WRITER, fail_at="after_pointer_replace")
    assert validate_mirror(mirror)["pointer"]["selected_generation_id"] == generation["generation_id"]


def test_rollback_and_restore_select_exact_immutable_generations(tmp_path: Path) -> None:
    contract, initialized, generation = _state(tmp_path)
    mirror = tmp_path / "mirror"
    publish_generation(ROOT, mirror, contract, generation, writer_id=WRITER)
    rollback = switch_generation(mirror, initialized["oracle"]["generation_id"], writer_id=WRITER)
    assert rollback["selected_generation_id"] == initialized["oracle"]["generation_id"]
    assert rollback["phase"] == "rolled_back"
    restore = switch_generation(mirror, generation["generation_id"], writer_id=WRITER)
    assert restore["selected_generation_id"] == generation["generation_id"]
    assert validate_mirror(mirror)["pointer"] == restore


def test_complete_efficacy_packet_passes_all_observed_controls_and_faults() -> None:
    with patch("orchestration_harness.governance_migration._snapshot", side_effect=_construction_snapshot):
        evidence = assess_rehearsal(ROOT, CONTRACT_PATH, INTENT_PATH, construction_reruns=0)
    assert evidence["status"] == "passed"
    assert evidence["ownership"]["dual_owned"] == 0
    assert evidence["fault_injection"]["passed"] == evidence["fault_injection"]["checkpoints"] == 23
    assert evidence["rollback"] == {"byte_exact_generation_selected": True, "restored_clockwork_generation": True}
    assert set(evidence["post_review_controls"]) == {f"AER-{number:04d}" for number in range(643, 652)}
    assert evidence["probe_coverage"] == {"predecessor": 13, "surrounding": 9}
    assert evidence["canonical_oracles_unchanged"] and evidence["caller_authored_derived_fields"] == 0
    assert evidence["projected_steady_state_corrective_reruns"] == 0
    assert not evidence["live_canonical_adoption"] and not evidence["actual_controls_retired"]


def test_runner_defaults_to_read_only(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    before = {path.relative_to(TOPIC): path.read_bytes() for path in TOPIC.rglob("*") if path.is_file()}
    monkeypatch.setattr("sys.argv", ["migration-rehearsal"])
    with patch("orchestration_harness.governance_migration._snapshot", side_effect=_construction_snapshot):
        assert runner_main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "passed"
    assert before == {path.relative_to(TOPIC): path.read_bytes() for path in TOPIC.rglob("*") if path.is_file()}


def test_frozen_implementation_line_budget_is_exact() -> None:
    contract = validate_contract(_load(CONTRACT_PATH))
    actual = sum(len((ROOT / path).read_text(encoding="utf-8").splitlines()) for path in contract["line_budget_files"])
    assert actual <= contract["line_budget"]
