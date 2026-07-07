"""Guards for current programme-planning guidance."""

from pathlib import Path


PHASE_PROGRAMMES = Path("orchestration/phase_programmes.md")


def test_phase_programmes_recommended_move_is_current_after_sprint_155():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "Current position after Sprint 155" in text
    assert "default recommendation after Sprint 155 is **Programme 2G**" in text
    assert "OpenAPI/FastAPI header alignment guard for create-proposal" in text
    assert "Sprint 152 then made that client-readiness decision" in text
    assert "runtime" in text
    assert "`minLength: 8` enforcement remains deferred" in text
    assert "Sprint 153 then closed the first concrete client-readiness gap" in text
    assert "Sprint 154 then mapped the remaining diary/API header gap" in text
    assert "Sprint 155 then wired the first already-enforced confirmation client gap" in text
    assert "propose_waiting_area_update" in text
    assert "confirmIdempotencyKey" in text
    assert "Sprint 156" in text
    assert "next bounded confirm client-header family" in text
    assert "provider-boundary guard stack has been consolidated" in text
    assert (
        "Status | Sprint 155 create-confirm client header emission "
        "completed; sprint engine continuing" in text
    )
    assert "Sprint 110-118 provider-boundary guard consolidation" in text
    assert (
        "Next Candidate Sprints | Sprint 156 should choose the next bounded "
        "confirm client header family" in text
    )


def test_phase_programmes_no_longer_points_to_stale_h69_or_sprint97_next_move():
    text = PHASE_PROGRAMMES.read_text(encoding="utf-8")

    assert "Current next move after H69" not in text
    assert "default recommendation after Sprint 97" not in text
