"""Guards for current programme-planning guidance."""

from pathlib import Path


PHASE_PROGRAMMES = Path("orchestration/phase_programmes.md")


def test_phase_programmes_recommended_move_is_current_after_s25_s27():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "## Recommended Next Planning Move" in text
    assert "docs/bernie-consultant-triage-implementation-roadmap.md" in text
    assert "default next tranche after S25-S27 is T1 Stateful Diary Scenario Laboratory" in text
    assert "live-model diary shadow evaluation with writes disabled" in text
    assert "clinician-facing cited GP-assistant consultation" in text
    assert "do not treat GP-assistant success as sufficient evidence for" in text
    assert "reception triage" in text
    assert "## Historical Planning Record Through Sprint 159" in text
    assert "superseded for next-tranche selection" in text


def test_phase_programmes_no_longer_points_to_stale_h69_or_sprint97_next_move():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "Current next move after H69" not in text
    assert "default recommendation after Sprint 97" not in text


def test_phase_programmes_keeps_clinical_authority_gates_closed():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "Do not begin patient-specific consultant runtime before T4" in text
    assert "separately validated, protocol-bound reception triage assistance" in text
