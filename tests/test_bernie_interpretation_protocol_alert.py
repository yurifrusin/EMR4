"""Protocol alert guard for Bernie interpretation readiness gating."""

from pathlib import Path


ALERTS = Path("orchestration/protocol_alerts.md")


def test_protocol_alerts_name_interpretation_readiness_gate():
    text = ALERTS.read_text(encoding="utf-8")

    assert "Bernie Interpretation Harness readiness gate" in text
    assert "scripts\\bernie_interpretation_readiness_check.py" in text
    assert "runtime_or_provider_wiring_ready=false" in text
    assert "raw_trove_access_ready=false" in text
    assert "runtime_gate_decision=blocked" in text


def test_protocol_alerts_pause_on_interpretation_readiness_change():
    text = ALERTS.read_text(encoding="utf-8")

    assert "pause the sprint engine for explicit" in text
    for phrase in [
        "runtime route wiring",
        "provider prompt/dry-run wiring",
        "memory/RAG/GraphRAG use",
        "H15/H-series runtime imports",
        "historical diary material access",
    ]:
        assert phrase in text


def test_protocol_alerts_prevent_ariadne_only_sprint_drift():
    text = ALERTS.read_text(encoding="utf-8")

    assert "Avoid Ariadne-only sprint drift" in text
    assert "tiny, tightly coupled guardrail increments" in text
    assert "Substantial, separable, judgment-heavy" in text
    assert "independent worker/reviewer lane by default" in text
    assert "use the H63 independent review brief" in text
