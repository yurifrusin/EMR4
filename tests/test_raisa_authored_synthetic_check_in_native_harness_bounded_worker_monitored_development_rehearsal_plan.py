from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal-plan.md"
THREAT = ROOT / "docs" / "security" / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-monitored-development-rehearsal-threat-model-delta.md"


def test_plan_is_frozen_timestamped_and_one_request() -> None:
    text = PLAN.read_text(encoding="utf-8")
    compact = " ".join(text.split())
    assert "Date: 2026-08-20" in text
    assert "Timestamp: 2026-08-20T20:46:14.4461645+10:00" in text
    assert "Status: `frozen`" in text
    assert "one provider-admitted model request" in compact
    assert "`concludesTurn`" in text
    assert "without a second model request" in compact
    assert "zero automatic retry, fallback, auxiliary model call or second worker" in compact


def test_plan_freezes_exact_synthetic_package_and_mechanical_judgment() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "`synthetic_window_coalescer.py`" in text
    assert "one literal edit" in text
    assert "nested-window regression row" in text
    assert "private\nauthored-synthetic holdback cases" in text
    assert "Deterministic controller evidence, rather than\nmodel prose" in text


def test_plan_records_all_parallelism_lanes() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "**DeepSeek Flash:** planned with positive leverage" in text
    assert "**Gemini 3.7 Flash/high:** reserved with required independence" in text
    assert "**Native subagents:** declined with negative leverage" in text
    assert "**GPT Sol:** owns plan" in text


def test_plan_and_threat_preserve_every_closed_boundary() -> None:
    combined = " ".join(
        (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).split()
    )
    for phrase in (
        "No second worker",
        "no attempt 006",
        "no Docker, PostgreSQL, SQL",
        "no product source",
        "generic-status `Arrived`",
        "no product, patient, appointment, clinical",
        "no production runtime, deployment, release, Pages",
        "protected-ref",
        "Preserve `docs/branding/`",
        "never use `git add .` or `git add -A`",
    ):
        assert phrase in combined


def test_threat_delta_requires_in_process_not_timing_conclusion() -> None:
    text = " ".join(THREAT.read_text(encoding="utf-8").split())
    assert "in-process rc.7 conclusion marker" in text
    assert "never on an outer file watcher or kill race" in text
    assert "ordinal two" in text or "ordinal-two" in text
    assert "before provider I/O" in text
