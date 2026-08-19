from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from pathlib import Path

import pytest

from orchestration_harness.governance_clockwork_tick import (
    CommittedClockworkTick,
    ClockworkTickRejection,
    PREDECESSOR_METADATA_NAMES,
    build_tick_generation,
    publish_tick_generation,
    rollback_tick_generation,
    validate_tick_intent,
    validate_tick_live_state,
)
from orchestration_harness.governance_live_adoption import (
    CANONICAL_KEYS,
    METADATA_NAMES,
    validate_contract,
    validate_live_state,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-adoption-retirement/contract.json"
TOPIC = ROOT / "orchestration/continuity/raisa-provider-free-clockwork-governed-check-in-successor-resolution"
INTENT_PATH = TOPIC / "closeout-intent.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def _worktree(path: Path):
    source = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    branch = f"codex/clockwork-tick-test-{path.name[-12:]}"
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


def _paths(worktree: Path, contract: dict) -> tuple[dict[str, Path], dict[str, Path], Path]:
    canonical = {
        key: worktree / relative for key, relative in contract["canonical_paths"].items()
    }
    root = worktree / contract["clockwork_root"]
    metadata = {name: root / name for name in PREDECESSOR_METADATA_NAMES}
    return canonical, metadata, root / "current.json"


def test_plan_and_intent_freeze_the_unrepeated_successor() -> None:
    plan = (ROOT / "docs/raisa-provider-free-clockwork-governed-check-in-successor-resolution-plan.md").read_text(encoding="utf-8")
    report = (TOPIC / "successor-resolution-report.md").read_text(encoding="utf-8")
    threat = (ROOT / "docs/security/raisa-provider-free-clockwork-governed-check-in-successor-resolution-threat-model-delta.md").read_text(encoding="utf-8")
    contract = validate_contract(_json(CONTRACT_PATH))
    intent = validate_tick_intent(_json(INTENT_PATH), contract)
    manifest = intent["transaction_manifest"]
    assert "Timestamp: 2026-08-19T" in plan
    assert "+10:00 (Australia/Brisbane)" in plan
    assert "Timestamp: 2026-08-19T" in threat
    assert "environment-manifest posture is first" in report
    assert manifest["node"]["relationships"] == [{
        "node_id": "ariadne-provider-free-clockwork-live-canonical-adoption-retirement",
        "relation": "builds_on",
    }]
    assert manifest["next_operation"]["operation_id"] == "raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture"
    assert "no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting" in intent["next_operation_protected_boundaries"]


def test_intent_rejects_derived_unsafe_and_underbounded_input() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    baseline = _json(INTENT_PATH)
    derived = json.loads(json.dumps(baseline))
    derived["transaction_manifest"]["source_commit"] = "a" * 40
    with pytest.raises(ClockworkTickRejection, match="caller_authored_derived_binding"):
        validate_tick_intent(derived, contract)
    unsafe = json.loads(json.dumps(baseline))
    unsafe["baton_acceptance"]["paths"][0] = "docs/branding/escape.md"
    with pytest.raises(ClockworkTickRejection, match="tick_baton_path"):
        validate_tick_intent(unsafe, contract)
    shell = json.loads(json.dumps(baseline))
    shell["command_manifest"]["commands"][0]["arguments"].append("value;unsafe")
    with pytest.raises(ClockworkTickRejection, match="tick_command_contract"):
        validate_tick_intent(shell, contract)
    underbounded = json.loads(json.dumps(baseline))
    underbounded["next_operation_protected_boundaries"].remove(
        "explicit_path_staging_only"
    )
    with pytest.raises(ClockworkTickRejection, match="tick_next_boundaries_floor"):
        validate_tick_intent(underbounded, contract)


def test_current_live_generation_is_preparable_or_exactly_selected() -> None:
    contract = validate_contract(_json(CONTRACT_PATH))
    before = validate_live_state(ROOT, contract)
    transaction = _json(ROOT / contract["clockwork_root"] / "transaction.json")
    if transaction["operation_id"] == "raisa-provider-free-clockwork-governed-check-in-successor-resolution":
        selected = validate_tick_live_state(ROOT, contract)
        graph = _json(ROOT / contract["canonical_paths"]["continuity"])
        compass = _json(ROOT / contract["canonical_paths"]["compass"])
        latch = _json(ROOT / contract["canonical_paths"]["active_latch"])
        assert selected["source_commit"] == "f98baaa5c57cfcf00f8d2e6cd0d1113d4a59ed6e"
        assert selected["previous_generation_id"] == "gen-f3b629e6cbe28061d1340c8ee75fb11e46847a9343338608a780ff3b4240885c"
        assert graph["graph_revision"] == 332
        assert compass["map_revision"] == 314
        assert latch["operation_id"] == "raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture"
        return
    prepared = build_tick_generation(ROOT, contract, _json(INTENT_PATH))
    graph = json.loads(prepared["canonical"]["continuity"].decode("utf-8"))
    compass = json.loads(prepared["canonical"]["compass"].decode("utf-8"))
    latch = json.loads(prepared["canonical"]["active_latch"].decode("utf-8"))
    assert prepared["pointer"]["previous_generation_id"] == before["generation_id"]
    assert prepared["pointer"]["lease_sequence"] == before["lease_sequence"] + 1
    assert graph["graph_revision"] == 332
    assert compass["map_revision"] == 314
    assert latch["operation_id"] == "raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture"
    assert latch["protected_boundaries"] == prepared["intent"]["next_operation_protected_boundaries"]
    assert prepared["generation_manifest"]["source_commit"] == subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True,
        text=True, encoding="utf-8",
    ).stdout.strip()


def test_git_clean_line_ending_variation_does_not_change_tick(tmp_path: Path) -> None:
    with _worktree(tmp_path / "line-endings") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent_path = worktree / INTENT_PATH.relative_to(ROOT)
        expected = build_tick_generation(worktree, contract, _json(intent_path))
        baton = worktree / contract["canonical_paths"]["current_baton"]
        baton.write_bytes(baton.read_bytes().replace(b"\n", b"\r\n"))
        assert subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(baton)], cwd=worktree
        ).returncode == 0
        observed = build_tick_generation(worktree, contract, _json(intent_path))
        assert observed["generation_manifest"] == expected["generation_manifest"]
        assert observed["canonical"] == expected["canonical"]


def test_all_pre_pointer_faults_restore_and_rollback_is_exact(tmp_path: Path) -> None:
    with _worktree(tmp_path / "faults") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        intent = _json(worktree / INTENT_PATH.relative_to(ROOT))
        prepared = build_tick_generation(worktree, contract, intent)
        canonical_paths, metadata_paths, pointer_path = _paths(worktree, contract)
        before_canonical = {key: path.read_bytes() for key, path in canonical_paths.items()}
        before_metadata = {key: path.read_bytes() for key, path in metadata_paths.items()}
        before_pointer = pointer_path.read_bytes()
        checkpoints = [
            point
            for key in CANONICAL_KEYS
            for point in (f"before:{key}", f"after:{key}")
        ] + [
            point
            for name in (*METADATA_NAMES, "generation-manifest.json")
            for point in (f"before:{name}", f"after:{name}")
        ] + ["before_pointer_replace"]
        for checkpoint in checkpoints:
            with pytest.raises(OSError, match="injected_tick_precommit_failure"):
                publish_tick_generation(
                    worktree,
                    prepared,
                    writer_id="clockwork",
                    fail_at=checkpoint,
                )
            assert {key: path.read_bytes() for key, path in canonical_paths.items()} == before_canonical
            assert {key: path.read_bytes() for key, path in metadata_paths.items()} == before_metadata
            assert pointer_path.read_bytes() == before_pointer
            assert not (pointer_path.parent / "writer.lock").exists()
        active = publish_tick_generation(worktree, prepared, writer_id="clockwork")
        assert active["operation_id"] == "raisa-provider-free-clockwork-governed-check-in-successor-resolution"
        assert publish_tick_generation(worktree, prepared, writer_id="clockwork")["generation_id"] == active["generation_id"]
        rolled_back = rollback_tick_generation(
            worktree, contract, writer_id="clockwork"
        )
        assert rolled_back["byte_exact"] is True
        assert {key: path.read_bytes() for key, path in canonical_paths.items()} == before_canonical
        assert {key: path.read_bytes() for key, path in metadata_paths.items()} == before_metadata
        assert validate_live_state(worktree, contract)["generation_id"] == prepared["base_pointer"]["selected_generation_id"]


def test_post_pointer_failure_is_committed_and_stale_predecessor_fails(tmp_path: Path) -> None:
    with _worktree(tmp_path / "post-pointer") as worktree:
        contract = validate_contract(_json(worktree / CONTRACT_PATH.relative_to(ROOT)))
        prepared = build_tick_generation(
            worktree, contract, _json(worktree / INTENT_PATH.relative_to(ROOT))
        )
        stale = json.loads(json.dumps(prepared["base_pointer"]))
        pointer_path = worktree / contract["clockwork_root"] / "current.json"
        stale["lease_sequence"] += 1
        pointer_path.write_text(json.dumps(stale, indent=2) + "\n", encoding="utf-8", newline="\n")
        with pytest.raises(ClockworkTickRejection, match="tick_stale_predecessor"):
            publish_tick_generation(worktree, prepared, writer_id="clockwork")
        pointer_path.write_text(json.dumps(prepared["base_pointer"], indent=2) + "\n", encoding="utf-8", newline="\n")
        with pytest.raises(ClockworkTickRejection, match="tick_writer_not_clockwork"):
            publish_tick_generation(worktree, prepared, writer_id="legacy", fail_at=None)
        with pytest.raises(CommittedClockworkTick, match="injected_tick_postcommit_failure"):
            publish_tick_generation(
                worktree,
                prepared,
                writer_id="clockwork",
                fail_at="after_pointer_replace",
            )
        assert validate_tick_live_state(worktree, contract)["status"] == "passed"
