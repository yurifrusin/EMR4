from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md"
THREAT = ROOT / "docs/security/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-threat-model-delta.md"


def test_plan_freezes_exact_client_only_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    joined = "\n".join((plan, threat))

    assert "Date: 2026-08-17" in plan
    assert "Timestamp:" in plan and "Australia/Brisbane" in plan
    assert "frozen_for_provider_free_client_only_execution" in plan
    assert "40e20981f3a4a14856f5dc4d127957ca791b06ad" in plan
    assert "raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition_pass" in plan
    assert "docs/diary/diary.js" in plan
    assert "docs/diary/diary.html" in plan
    assert "No backend, REST/OpenAPI, GraphQL, schema, service, migration or database file" in plan
    assert "Open Yuri decision: none" in plan
    assert "explicit-path staging only" in plan
    assert "docs/branding/" in joined


def test_plan_preserves_canonical_delete_and_reconciliation_contract() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    joined = "\n".join((plan, threat))

    assert "/appointments/proposals/delete/confirm" in plan
    assert "raisa.delete_confirm_public_envelope.v1" in plan
    assert "appointment read model" in plan
    assert "Remove the 404 string probe" in plan
    assert "exactly one fresh" in plan
    assert "refresh-required" in joined
    assert "No optimistic product truth" in plan
    assert "route_intercepted_browser" in plan
    assert "status cancellation fallback" in plan
    assert "raw compatibility DELETE" in plan


def test_plan_records_risk_weighted_worker_allocation() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "DeepSeek V4 Flash/high" in plan
    assert "separable focused source and" in plan
    assert "Gemini 3.7 Flash/high" in plan
    assert "exact-candidate read-only" in plan
    assert "Native subagents" in plan
    assert "current developer policy prohibits" in plan
    assert "repository pytest/browser execution remains serial" in plan
