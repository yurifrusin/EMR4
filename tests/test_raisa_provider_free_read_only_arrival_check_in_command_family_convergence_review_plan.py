from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review-threat-model-delta.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_freezes_exact_read_only_result_and_timestamp() -> None:
    plan = _text(PLAN)
    head = "\n".join(plan.splitlines()[:20])
    assert "Date: 2026-08-18" in head
    assert "Timestamp: 2026-08-18T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    assert "Status: `frozen_for_read_only_execution`" in head
    assert "fb39d235c5dc4de2440a5b0e4685ee5da5b4f4d0" in head
    assert "raisa_provider_free_read_only_arrival_check_in_command_family_convergence_review_pass" in head


def test_plan_requires_full_contract_and_static_drift_comparison() -> None:
    plan = " ".join(_text(PLAN).split())
    for phrase in (
        "general status, waiting-area and A5.1 check-in contracts",
        "signed evidence, freshness and replay posture",
        "transaction, audit, event, receipt and fresh-read behavior",
        "`{appointment_id}` versus `{appointment_id:uuid}`",
        "one canonical product-facing arrival meaning",
        "A5.1 default-off, uncalled and unmodified",
    ):
        assert phrase in plan


def test_plan_and_threat_keep_runtime_surfaces_closed() -> None:
    combined = " ".join(f"{_text(PLAN)}\n{_text(THREAT)}".lower().split())
    for phrase in (
        "no product behavior",
        "product/patient/clinical/historical/protected data",
        "provider/adc",
        "deployment, production, release, pages",
        "explicit-path staging only",
    ):
        assert phrase in combined


def test_plan_records_parallelism_efficacy() -> None:
    plan = _text(PLAN)
    assert "DeepSeek V4 Flash/high — declined" in plan
    assert "Gemini 3.7 Flash/high — reserved" in plan
    assert "Native subagents — declined" in plan
    assert "one fresh exact-candidate veto" in plan
