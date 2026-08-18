from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration/continuity/"
    "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal"
)
PLAN = ROOT / "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal-plan.md"
THREAT = ROOT / "docs/security/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal-threat-model-delta.md"
CONTRACT = BASE / "contract.json"
SCHEMA = BASE / "contract.schema.json"
GAUGES = BASE / "frozen-failure-gauges.json"
PREPLANNING_RECEIPT = ROOT / "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-gear-rehearsal-preplanning-receipt.json"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_plan_freezes_the_narrow_provider_free_shadow_scope() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "f6cbd33fd3322754e06ac6dafa1503f5200e0803" in text
    assert "159301c3ef84c3f274971df9ef0776312b99f7af" in text
    assert "2e34bdad732fdab32fbf778280b3d3c70d66d602" in text
    assert "fourteen failure-induced reruns" in text
    assert "at most `7`" in text
    assert "No live clockwork adoption" in text
    assert "docs/branding/" in text
    assert "explicit-path" in text


def test_contract_and_schema_freeze_full_oids_and_zero_caller_bindings() -> None:
    contract = _json(CONTRACT)
    schema = _json(SCHEMA)
    assert contract["caller_supplied_binding_fields"] == []
    assert len(contract["engine_owned_fields"]) == 15
    assert contract["efficacy"]["comparator_failure_induced_reruns"] == 14
    assert contract["efficacy"]["maximum_candidate_failure_induced_reruns"] == 7
    assert contract["policy"]["provider_calls"] == 0
    assert contract["policy"]["live_adoption"] is False
    assert schema["$defs"]["git_oid"]["pattern"] == "^[0-9a-f]{40}$"
    assert len(contract["source_bindings"]) == 11


def test_failure_gauges_are_immutable_not_live_current_fixtures() -> None:
    ledger = _json(GAUGES)
    gauges = ledger["gauges"]
    assert ledger["comparator_failure_induced_reruns"] == 14
    assert len(gauges) == 14
    assert len({item["id"] for item in gauges}) == 14
    assert len({item["rejection_rule"] for item in gauges}) == 14
    serialized = json.dumps(ledger, sort_keys=True)
    assert "next_executable_stage" not in serialized
    assert "retry_counters" not in serialized
    assert "terminal_response" not in serialized


def test_threat_delta_keeps_timing_presets_provider_and_publication_non_authoritative() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "Preset or tool selection silently changes authority" in text
    assert "Timing becomes an authority shortcut" in text
    assert "provider-free" in text
    assert "partial generation" in text
    assert "does not prove the installed DeepSeek Harness" in text


def test_preplanning_receipt_names_all_five_authority_sources_and_parallel_lanes() -> None:
    receipt = _json(PREPLANNING_RECEIPT)
    serialized = json.dumps(receipt, sort_keys=True)
    for source in (
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ):
        assert source in serialized
    for lane in ("deepseek", "gemini", "native_subagents"):
        assert lane in serialized


def test_no_product_or_predecessor_engine_source_is_changed_by_the_plan() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "orchestration_harness/transactional_closeout.py` remain read-only" in text
    assert "No live clockwork adoption" in text
    assert "product configuration, API, route, database, client" in text

