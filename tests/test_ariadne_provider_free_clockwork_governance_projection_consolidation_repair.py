from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from unittest.mock import patch

import pytest

from orchestration_harness.governance_clockwork import (
    GovernanceRejection, build_bundle, digest,
    load_object, publish_private_shadow, validate_bundle,
    validate_contract, validate_probes,
)
from scripts.ariadne_provider_free_clockwork_governance_projection_consolidation_repair import _observation, main as runner_main


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-governance-projection-consolidation-repair"
CONTRACT = TOPIC / "contract.json"
PROBES = TOPIC / "rerun-probes.json"
REGISTER = ROOT / "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
SCHEMA = REGISTER.with_name("agent-error-register.schema.json")
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
PREPLAN = ROOT / "orchestration/agent_inbox/codex/ariadne-clockwork-governance-projection-consolidation-repair-preplanning-runtime-state.json"


def _bundle(observations: list[object] | None = None) -> tuple[dict[str, object], dict[str, object]]:
    contract = validate_contract(load_object(CONTRACT))
    construction_latch = load_object(PREPLAN)["active_operation"]
    with patch("orchestration_harness.governance_clockwork.load_object", side_effect=lambda path: construction_latch if path == LATCH else load_object(path)):
        bundle = build_bundle(
            ROOT,
            CONTRACT,
            PROBES,
            REGISTER,
            SCHEMA,
            LATCH,
            observations or [_observation()],
            gate_result="rejected",
        )
    return bundle, contract


def _reseal(bundle: dict[str, object]) -> None:
    clock = bundle["clock"]
    clock["projections_sha256"] = digest(bundle["projections"])
    clock["efficacy_sha256"] = digest(bundle["efficacy"])
    clock.pop("acknowledged_tip_sha256", None)
    clock["acknowledged_tip_sha256"] = digest(clock)
    bundle.pop("bundle_sha256", None)
    bundle["bundle_sha256"] = digest(bundle)


def test_plan_receipt_latch_and_boundaries_are_frozen() -> None:
    plan = (ROOT / "docs/ariadne-provider-free-clockwork-governance-projection-consolidation-repair-plan.md").read_text(encoding="utf-8")
    threat = (ROOT / "docs/security/ariadne-provider-free-clockwork-governance-projection-consolidation-repair-threat-model-delta.md").read_text(encoding="utf-8")
    receipt = load_object(ROOT / "orchestration/agent_inbox/codex/ariadne-clockwork-governance-projection-consolidation-repair-preplanning-receipt.json")
    historical_latch = load_object(PREPLAN)["active_operation"]
    live_latch = load_object(LATCH)
    assert "Timestamp:" in plan and "Australia/Brisbane" in plan
    assert "Timestamp:" in threat and "Australia/Brisbane" in threat
    assert receipt["status"] == "passed"
    assert set(receipt["rehydration_sources"]) == {
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    }
    assert historical_latch["operation_id"] == receipt["active_operation"]["operation_id"]
    assert historical_latch["source_head"] == receipt["active_operation"]["source_head"]
    assert live_latch["status"] == "in_progress" and not live_latch["terminal_response"]["permitted"]
    for lane in ("deepseek_flash", "gemini_verifier", "native_subagents"):
        assert lane in {row["lane_id"] for row in receipt["parallelism_assessment"]["lanes"]}


def test_contract_and_replay_population_are_closed() -> None:
    contract = validate_contract(load_object(CONTRACT))
    probes = validate_probes(load_object(PROBES))
    assert len(probes) == contract["predecessor_sunk_reruns"]
    assert sum(row["classification"] == "surrounding_governance" for row in probes) == contract["baseline_surrounding_reruns"]
    assert not set(contract["baseline_maintained_surfaces"]) & set(contract["candidate_maintained_surfaces"])
    assert all("*" not in arg and "?" not in arg for command in contract["commands"] for arg in [command["executable"], *command["arguments"]])


def test_bundle_derives_every_governance_binding_and_cost_reading() -> None:
    bundle, contract = _bundle()
    validate_bundle(copy.deepcopy(bundle), contract)
    projections = bundle["projections"]
    efficacy = bundle["efficacy"]
    register = projections["incident_projection"]
    base = load_object(REGISTER)
    assert re.fullmatch(r"[0-9a-f]{40}", bundle["clock"]["source_commit"])
    assert register["register_revision"] == base["register_revision"] + 1
    assert len(register["incidents"]) == len(base["incidents"]) + 1
    assert projections["continuity_projection"] == {"node_status": "rejected", "decision_status": "rejected"}
    assert projections["latch_projection"]["status"] == "blocked"
    assert efficacy["caller_authored_derived_fields"] == 0
    assert efficacy["steady_state_surrounding_reruns"] <= contract["maximum_steady_state_surrounding_reruns"]
    assert efficacy["incremental_line_growth"] <= efficacy["line_budget"]
    assert efficacy["maintained_surface_reduction_percent"] >= contract["minimum_surface_reduction_percent"]
    assert efficacy["retirement_ready"] and not bundle["live_adoption"] and not bundle["current_controls_retired"]


def test_caller_cannot_supply_a_derived_binding() -> None:
    observation = _observation()
    observation["source_commit"] = "0" * 40
    with pytest.raises(GovernanceRejection, match="observation_keys"):
        _bundle([observation])


def test_attempt_and_peer_identity_derive_from_resource_and_evidence() -> None:
    first = _observation()
    second = copy.deepcopy(first)
    second["observed_error"] = "A second fact from the same exact execution envelope."
    bundle, _ = _bundle([first, second])
    generated = bundle["projections"]["incident_projection"]["incidents"][-2:]
    assert generated[0]["attempt_id"] == generated[1]["attempt_id"]
    assert generated[0]["related_incident_ids"] == [generated[1]["incident_id"]]
    split = copy.deepcopy(second)
    split["resource_id"] = "different-resource"
    bundle, _ = _bundle([first, split])
    generated = bundle["projections"]["incident_projection"]["incidents"][-2:]
    assert generated[0]["attempt_id"] != generated[1]["attempt_id"]
    assert generated[0]["related_incident_ids"] == generated[1]["related_incident_ids"] == []


def test_all_thirteen_preserved_reruns_have_hostile_replay() -> None:
    canonical, contract = _bundle()
    probes = validate_probes(load_object(PROBES))
    for probe in probes:
        candidate = copy.deepcopy(canonical)
        owner = probe["control_owner"]
        if owner == "clock_tip_binding":
            candidate["clock"]["previous_acknowledged_tip_sha256"] = "0" * 64
        elif owner == "efficacy_binding":
            candidate["efficacy"]["probe_coverage"] = 12
        elif owner == "incident_projection":
            candidate["projections"]["incident_projection"]["incidents"][-1]["category"] = "not-a-category"
        elif owner == "command_projection":
            candidate["projections"]["command_projection"]["commands"][0]["arguments"].append("*.json")
        elif owner == "continuity_projection":
            candidate["projections"]["continuity_projection"]["decision_status"] = "revision_required"
        elif owner == "atomic_projection_binding":
            candidate["projections"]["baton_projection"]["register_revision"] += 1
        elif owner == "baton_projection":
            candidate["projections"]["baton_projection"]["inherited_boundaries"].pop()
        else:
            raise AssertionError(f"unexercised owner: {owner}")
        _reseal(candidate)
        with pytest.raises(GovernanceRejection):
            validate_bundle(candidate, contract)


def test_private_publication_is_atomic_and_fail_closed(tmp_path: Path) -> None:
    bundle, contract = _bundle()
    failed = tmp_path / "private-shadow-failed"
    with pytest.raises(OSError, match="injected_private_shadow_write_failure"):
        publish_private_shadow(bundle, contract, failed, fail_after_write=1)
    assert not failed.exists() and not list(tmp_path.glob(".*.staging-*"))
    target = publish_private_shadow(bundle, contract, tmp_path / "private-shadow-success")
    assert json.loads((target / "bundle.json").read_text(encoding="utf-8")) == bundle


def test_runner_without_publish_is_read_only(monkeypatch: pytest.MonkeyPatch) -> None:
    targets = [TOPIC / "provider-free-repair-evidence.json", TOPIC / "repair-report.md"]
    before = [path.read_bytes() for path in targets]
    monkeypatch.setattr("sys.argv", ["clockwork-repair"])
    with pytest.raises(GovernanceRejection, match="active_latch"):
        runner_main()
    assert [path.read_bytes() for path in targets] == before
