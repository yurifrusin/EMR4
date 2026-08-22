from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPERATION = "raisa-native-harness-bounded-occupied-useful-worker-coordinate-recovery-rehearsal"


def test_plan_freezes_one_request_typed_coordinate_and_no_retry() -> None:
    text = (ROOT / "docs" / f"{OPERATION}-plan.md").read_text(encoding="utf-8")
    for phrase in (
        "Status: frozen",
        "exactly one separately named DeepSeek V4 Flash/high",
        "tool_lifecycle: null",
        "edit_success_accept_concluded",
        "provider requests and parallel tool calls: one each",
        "automatic retry, manual retry, resume, fallback, auxiliary model and Claude",
        "If no candidate is admitted, Gemini is not invoked",
        "Stage explicit paths only; never use `git add .` or",
    ):
        assert phrase in text

def test_plan_records_explicit_three_lane_serial_assessment() -> None:
    text = (ROOT / "docs" / f"{OPERATION}-plan.md").read_text(encoding="utf-8")
    assert "DeepSeek V4 Flash/high: **planned**" in text
    assert "Gemini 3.7 Flash/high: **reserved**" in text
    assert "Native subagents: **declined**" in text
    assert "Parallel work packages: none" in text


def test_threat_delta_closes_rerun_ambiguity_and_activation() -> None:
    text = (
        ROOT / "docs/security" / f"{OPERATION}-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "silently retries or overwrites the consumed attempt",
        "concludeTurn()",
        "tool_lifecycle: null",
        "Machine-resolve full 40-character Git object identities",
        "every activation, feature-flag, allowlist, route, runtime, data and protected-ref effect false",
        "preserve all repository untracked paths including `docs/branding/`",
    ):
        assert phrase in text
