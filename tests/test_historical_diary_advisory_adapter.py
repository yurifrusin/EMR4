import json
from datetime import date
from pathlib import Path

from app.services.diary.frames import BernieAdvisoryWarningFrame
from app.services.practice_knowledge.boundary import to_advisory_frame
from tests.h15_advisory_adapter import candidates_to_practice_knowledge_result


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "h15_semantic_candidates"
    / "read_only_explain_schedule_candidates.json"
)


def _payload():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_h15_candidates_map_to_advisory_only_practice_knowledge_result():
    result = candidates_to_practice_knowledge_result(_payload())

    assert result.advisory_only is True
    assert result.cannot_affect_slots is True
    assert result.cannot_affect_policy is True
    assert result.cannot_affect_confirm is True
    assert result.retrieval_basis == "h15_authored_synthetic_test_adapter"
    assert len(result.items) == 2
    for item in result.items:
        assert item.fact.authority_tier == "advisory"
        assert item.fact.contains_phi is False
        assert "appointment" not in item.fact.body.lower()
        assert "booking" not in item.fact.body.lower()
        assert item.score == 0.1


def test_h15_candidates_exit_only_as_bernie_advisory_warning_frame():
    result = candidates_to_practice_knowledge_result(_payload())
    frame = to_advisory_frame(
        result,
        reference_date=date(2026, 7, 6),
        reason_code="h15_synthetic_candidate_advisory",
    )

    assert isinstance(frame, BernieAdvisoryWarningFrame)
    assert frame.frame_type == "advisory_warning"
    assert frame.status == "advisory"
    assert frame.reason_code == "h15_synthetic_candidate_advisory"
    assert frame.payload["advisory_only"] is True
    assert frame.payload["cannot_affect_slots"] is True
    assert frame.payload["cannot_affect_policy"] is True
    assert frame.payload["cannot_affect_confirm"] is True
    assert "confirm_grade_allowed" not in frame.payload
    assert "slot_candidates" not in frame.payload
    assert "write" not in json.dumps(frame.payload, sort_keys=True).lower()
