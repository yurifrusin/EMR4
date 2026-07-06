"""Release-gate documentation checks for the interpretation readiness command."""

from pathlib import Path


RELEASE_GATES = Path("orchestration/bernie_release_gates.md")


def test_release_gates_require_interpretation_readiness_command_before_wiring():
    text = RELEASE_GATES.read_text(encoding="utf-8")

    assert "Provider-Free Interpretation Harness Gate" in text
    assert "scripts\\bernie_interpretation_readiness_check.py" in text
    assert "runtime_or_provider_wiring_ready=false" in text
    assert "raw_trove_access_ready=false" in text
    assert "runtime_gate_decision=blocked" in text


def test_release_gates_pause_if_interpretation_readiness_changes():
    text = RELEASE_GATES.read_text(encoding="utf-8")

    assert "sprint engine must pause" in text
    assert "explicit review" in text
    for forbidden_surface in [
        "runtime route wiring",
        "provider prompt wiring",
        "provider dry-run wiring",
        "memory/RAG/GraphRAG use",
        "historical diary material access",
    ]:
        assert forbidden_surface in text
