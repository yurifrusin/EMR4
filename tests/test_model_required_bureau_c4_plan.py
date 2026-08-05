from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-plan.md"
THREAT = (
    ROOT
    / "docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-threat-model-delta.md"
)


def test_c4_plan_freezes_one_pure_in_memory_runbook() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "`restart-api-synthetic.v1`" in plan
    assert "`restore-api-synthetic-lkg.v1`" in plan
    assert "pure state transition" in plan
    assert "exact empty object" in plan
    assert "zero mounted FastAPI" in plan
    assert "No dynamic import" in plan


def test_c4_plan_preserves_every_closed_surface() -> None:
    combined = (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).lower()
    for phrase in (
        "zero provider",
        "patient",
        "product-derived",
        "real database",
        "shell",
        "sql",
        "cloud",
        "iam",
        "c5",
        "deployment",
        "production",
        "release",
        "pages",
        "protected-ref",
        "docs/branding/",
    ):
        assert phrase in combined


def test_c4_plan_requires_fresh_readback_and_fail_closed_rollback() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "distinct fresh readback" in plan
    assert "SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED" in plan
    assert "SIMULATED_ROLLBACK_UNVERIFIED" in plan
    assert "neither is success" in THREAT.read_text(encoding="utf-8").lower()
