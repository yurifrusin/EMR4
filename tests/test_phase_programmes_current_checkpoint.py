"""Guards for current programme-planning guidance."""

from pathlib import Path


PHASE_PROGRAMMES = Path("orchestration/phase_programmes.md")


def test_phase_programmes_recommended_move_is_current_after_sprint_148():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "Current position after Sprint 148" in text
    assert "default recommendation after Sprint 148 is **Programme 2G**" in text
    assert "focused create-proposal replay-model decision" in text
    assert "provider-boundary guard stack has been consolidated" in text
    assert (
        "Status | Sprint 148 guarded create-proposal idempotency route-test contract "
        "completed; sprint engine continuing" in text
    )
    assert "Sprint 110-118 provider-boundary guard consolidation" in text
    assert (
        "Next Candidate Sprints | Sprint 149 focused create-proposal "
        "replay-model decision before proposal-route enforcement wiring" in text
    )


def test_phase_programmes_no_longer_points_to_stale_h69_or_sprint97_next_move():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "Current next move after H69" not in text
    assert "default recommendation after Sprint 97" not in text
