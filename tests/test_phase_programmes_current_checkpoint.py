"""Guards for current programme-planning guidance."""

from pathlib import Path


PHASE_PROGRAMMES = Path("orchestration/phase_programmes.md")


def test_phase_programmes_recommended_move_is_current_after_sprint_127():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "Current position after Sprint 127" in text
    assert "default recommendation after Sprint 127 is **Programme 2G**" in text
    assert "appointment idempotency model/migration preflight" in text
    assert "provider-boundary guard stack has been consolidated" in text
    assert (
        "Status | Sprint 127 appointment idempotency storage artifact guard "
        "completed; model/migration preflight selected next" in text
    )
    assert "Sprint 110-118 provider-boundary guard consolidation" in text
    assert (
        "Next Candidate Sprints | Sprint 128 appointment idempotency "
        "model/migration preflight" in text
    )


def test_phase_programmes_no_longer_points_to_stale_h69_or_sprint97_next_move():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "Current next move after H69" not in text
    assert "default recommendation after Sprint 97" not in text
