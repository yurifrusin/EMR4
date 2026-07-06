"""Independent review brief guard for Bernie interpretation readiness."""

from pathlib import Path


BRIEF = Path("docs/adversarial/h63_interpretation_independent_review_brief.md")


def test_h63_review_brief_requires_readiness_preflight():
    text = BRIEF.read_text(encoding="utf-8")

    assert ".venv\\Scripts\\python.exe scripts\\bernie_interpretation_readiness_check.py" in text
    assert "`runtime_or_provider_wiring_ready: false`" in text
    assert "`raw_trove_access_ready: false`" in text
    assert "`runtime_gate_decision: blocked`" in text
    assert "`sprint_engine_state: continuing`" in text
    assert "pause the sprint engine for explicit review" in text


def test_h63_review_brief_keeps_runtime_provider_trove_out_of_scope():
    text = BRIEF.read_text(encoding="utf-8")

    for forbidden_surface in [
        "Runtime route wiring.",
        "Frontend or taskpane changes.",
        "Provider prompts",
        "Database reads",
        "Memory, RAG, GraphRAG",
        "H15/H-series runtime imports",
        "Historical diary trove processing",
        "raw diary reads",
        "ignored local-data reads",
    ]:
        assert forbidden_surface in text


def test_h63_review_brief_requires_review_artifact_only():
    text = BRIEF.read_text(encoding="utf-8")

    assert "Produce a review artifact" in text
    assert "review artifact only" in text
    assert "Any code change beyond a review artifact" in text
    assert "requires Yuri approval" in text
