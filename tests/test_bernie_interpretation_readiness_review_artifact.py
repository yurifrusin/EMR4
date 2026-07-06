"""Adversarial review artifact guard for interpretation readiness gates."""

from pathlib import Path


REVIEW_PATH = Path("docs/adversarial/h58_interpretation_readiness_gate_review.md")


def test_h58_readiness_review_preserves_blocked_verdict():
    text = REVIEW_PATH.read_text(encoding="utf-8")

    assert "blocked-by-default" in text
    assert "not evidence that runtime routes" in text
    assert "`runtime_or_provider_wiring_ready: false`" in text
    assert "`raw_trove_access_ready: false`" in text
    assert "runtime gate decision remains `blocked`" in text.casefold()


def test_h58_readiness_review_requires_pause_if_readiness_changes():
    text = REVIEW_PATH.read_text(encoding="utf-8")

    assert "pause the sprint engine for review" in text
    for forbidden_surface in [
        "provider prompts",
        "live provider",
        "memory/RAG/GraphRAG",
        "H15/H-series runtime imports",
        "historical diary material access",
    ]:
        assert forbidden_surface in text
