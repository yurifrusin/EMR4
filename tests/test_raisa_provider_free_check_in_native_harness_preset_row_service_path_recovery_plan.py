from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-check-in-native-harness-preset-row-service-path-recovery-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-check-in-native-harness-preset-row-service-path-recovery-threat-model-delta.md"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"


def test_plan_is_frozen_and_matches_active_operation() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    latch = LATCH.read_text(encoding="utf-8")

    assert "Status: `frozen`" in plan
    assert "raisa-provider-free-check-in-native-harness-preset-row-service-path-recovery" in plan
    assert "raisa-provider-free-check-in-native-harness-preset-row-service-path-recovery" in latch
    assert "configured `roots` value with the Harness's shipped preset root" in plan
    assert "`includeUserRoot: false`" in plan
    assert "`user` trust" in plan


def test_plan_requires_deterministic_proof_before_native_process() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "Before that checkpoint, the new native Harness process count is zero." in plan
    assert "one provider-disabled native service-row confirmation" in plan
    assert "one-process/zero-retry allowance" in plan
    assert "The runner contains no `agents.create`" in plan
    assert "First process creation consumes" in plan


def test_plan_and_threat_keep_closed_surfaces_exact() -> None:
    combined = PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")

    for phrase in (
        "no DeepSeek request",
        "no attempt 006",
        "no agent creation",
        "no installed-package",
        "no network",
        "no product",
        "no production",
        "no protected-ref movement",
        "`docs/branding/`",
        "never use `git add .` or `git add -A`",
    ):
        assert phrase in combined


def test_parallelism_assessment_is_explicit() -> None:
    plan = PLAN.read_text(encoding="utf-8")

    assert "**DeepSeek Flash:** declined" in plan
    assert "**Gemini 3.7 Flash/high:** declined at planning" in plan
    assert "required later for one fresh" in plan
    assert "**Native subagents:** declined" in plan
    assert "Current developer policy prohibits proactive" in plan
