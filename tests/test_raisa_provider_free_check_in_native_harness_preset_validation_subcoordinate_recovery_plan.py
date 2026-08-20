from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-provider-free-check-in-native-harness-preset-validation-subcoordinate-recovery-plan.md"
THREAT = ROOT / "docs" / "security" / "raisa-provider-free-check-in-native-harness-preset-validation-subcoordinate-recovery-threat-model-delta.md"


def test_plan_freezes_three_subcoordinates_and_separate_native_checkpoint() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "Status: `frozen`" in text
    assert "row_discovery" in text
    assert "byte_read_and_parse" in text
    assert "digest_and_length_binding" in text
    assert "Before the checkpoint, native Harness process count must remain zero" in text
    assert "must contain\nno `agents.create`" in text
    assert "Failure writes\none sanitized terminal" in text
    assert "forbids retry" in text


def test_plan_keeps_product_provider_database_and_protected_surfaces_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")

    for phrase in (
        "no DeepSeek, Gemini or other\nprovider request",
        "no attempt 006",
        "no agent creation, preset mount or occupied\nworker",
        "no Docker, PostgreSQL, SQL or transaction execution",
        "no ordinary-practice\nenablement or generic-status `Arrived`",
        "no production runtime, deployment,\nrelease, Pages or protected-ref movement",
        "never use `git add .` or `git add -A`",
    ):
        assert phrase in text


def test_threat_delta_keeps_claim_narrow() -> None:
    text = THREAT.read_text(encoding="utf-8")

    assert "Status: `frozen`" in text
    assert "Full IDs are forbidden in the narrative Git evidence field" in text
    assert "does not prove preset mount" in text
    assert "production suitability or deployment authority" in text
