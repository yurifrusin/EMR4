from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/ariadne-provider-free-verification-envelope-phase-and-runner-admission-repair-plan.md"
THREAT = ROOT / "docs/security/ariadne-provider-free-verification-envelope-phase-and-runner-admission-repair-threat-model-delta.md"


def test_plan_freezes_typed_provider_free_scope_and_parallelism() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")

    assert "Status: `frozen`" in plan
    assert "database_authority" in plan
    assert "verification_phase" in plan
    assert "prepublication" in plan and "postpublication" in plan
    assert "scripts.ariadne_serial_pytest" in plan
    assert "scripts.ariadne_provider_free_pytest" in plan
    assert "No existing test may be run through ordinary or serial pytest" in plan
    assert "DeepSeek native Harness:** `declined`" in plan
    assert "Gemini:** `declined`" in plan
    assert "Native subagents:** `declined`" in plan
    assert all(f"VE-{index:03d}" in threat for index in range(1, 16))
