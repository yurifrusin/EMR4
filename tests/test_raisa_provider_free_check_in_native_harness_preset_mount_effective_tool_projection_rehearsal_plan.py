from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-provider-free-check-in-native-harness-preset-mount-effective-tool-projection-rehearsal-plan.md"
THREAT = ROOT / "docs" / "security" / "raisa-provider-free-check-in-native-harness-preset-mount-effective-tool-projection-rehearsal-threat-model-delta.md"


def test_plan_freezes_exact_mount_and_tool_projection_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in text
    assert "`emr4-bounded-worker`" in text
    assert "`edit`, `glob` and `read`" in text
    assert "No native process is authorised by candidate construction" in text
    assert "one new attempt identity;" in text
    assert "zero automatic retries" in text
    assert "no DeepSeek\nor other model request" in text
    assert "no agent creation or agent session" in text


def test_plan_preserves_product_and_protected_boundaries() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for phrase in (
        "no ordinary-practice",
        "no product, patient, appointment",
        "no production runtime, deployment",
        "protected-ref movement",
        "Preserve `docs/branding/`",
        "never use\n`git add .` or `git add -A`",
    ):
        assert phrase in text


def test_threat_delta_keeps_provider_and_agent_surfaces_closed() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "No DeepSeek/model/provider/broker/network request" in text
    assert "agent session" in text
    assert "First process creation consumes the checkpoint allowance" in text
    assert "one provider-disabled disposable preset mount" in text
