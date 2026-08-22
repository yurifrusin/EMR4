from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-prospective-success-redaction-and-typed-cleanup-projection-conformance-repair-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-check-in-prospective-success-redaction-and-typed-cleanup-projection-conformance-repair-threat-model-delta.md"
RUNTIME = ROOT / "orchestration/agent_inbox/codex/raisa-check-in-prospective-success-redaction-and-typed-cleanup-projection-repair-preplanning-runtime-state.json"
RECEIPT = ROOT / "orchestration/agent_inbox/codex/raisa-check-in-prospective-success-redaction-and-typed-cleanup-projection-repair-preplanning-receipt.json"


def test_plan_freezes_exact_sources_gears_and_closed_scope() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in text
    for source in (
        "5d93380060f31bab21bddc9ffdd5580754eb4fc6",
        "ca7970b3520b2c38e9abd6fee3462ebb743792e0",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
    ):
        assert source in text
        assert re.fullmatch(r"[0-9a-f]{40}", source)
    assert "_prospective_success_evidence_projection" in text
    assert "PostFinalizationTerminal" in text
    assert "live_sensitive_material_existing_hosted_or_product_database_used" in text
    assert (
        "forbidden-field vocabulary and matching algorithm remain byte-for-byte unchanged"
        in " ".join(text.split())
    )
    for denied in (
        "No Docker object",
        "attempt 008",
        "DeepSeek",
        "ordinary practice",
        "protected-ref movement",
    ):
        assert denied in text


def test_threat_delta_keeps_database_and_success_claims_closed() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "Status: `frozen`" in text
    assert "prospective_projection_shape_mismatch" in text
    assert "It cannot prove attempt 007's" in text
    assert "A later attempt-008 plan" in text


def test_fresh_receipt_names_all_five_sources_and_parallel_lanes() -> None:
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    required = [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == required
    assert set(runtime["source_evidence"]) == set(required)
    lanes = runtime["parallelism_assessment"]["lanes"]
    assert [lane["lane_id"] for lane in lanes] == [
        "deepseek_flash",
        "gemini_verifier",
        "native_subagents",
    ]
    assert all(lane["disposition"] == "declined" for lane in lanes)
    assert receipt["git_refs_snapshot"]["protected_refs_aligned"] is True
    assert receipt["git_refs_snapshot"]["preserved_untracked_paths"]["docs/branding"] is True
