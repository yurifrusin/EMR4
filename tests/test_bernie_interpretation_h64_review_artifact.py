"""Guard the H64 independent review artifact and triage."""

from pathlib import Path


REVIEW = Path("docs/adversarial/h64_interpretation_readiness_independent_review.md")


def test_h64_review_records_independent_worker_and_blocked_verdict():
    text = REVIEW.read_text(encoding="utf-8")

    assert "Shen, DeepSeek Flash worker" in text
    assert "read-only adversarial review" in text
    assert "No critical or high findings" in text
    assert "blocked-by-default preflight" in text
    assert "Sprint engine state: continuing" in text


def test_h64_review_preserves_runtime_provider_trove_blocks():
    text = REVIEW.read_text(encoding="utf-8")

    for phrase in [
        "runtime route wiring",
        "provider prompts or dry-runs",
        "memory/RAG/GraphRAG",
        "H15/H-series runtime imports",
        "historical diary material access",
        "raw-trove access remain blocked",
    ]:
        assert phrase in text


def test_h64_review_tracks_follow_up_findings():
    text = REVIEW.read_text(encoding="utf-8")

    for finding_id in [
        "H64-M1",
        "H64-M2",
        "H64-M3",
        "H64-L1",
        "H64-L2",
        "H64-L3",
        "H64-L4",
    ]:
        assert finding_id in text

    assert "H65: derive combined readiness booleans" in text
    assert "H66: make interpretation result/frame projection self-validating" in text
    assert "H67: derive forbidden report text from fixture utterances" in text
