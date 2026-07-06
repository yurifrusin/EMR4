import json
from datetime import date
from pathlib import Path

from app.services.bernie import (
    BernieReceptionContextFrameSet,
    BernieRequestedAppointmentFrame,
    evaluate_reception_context,
)
from app.services.practice_knowledge.boundary import to_advisory_frame
from tests.h15_advisory_adapter import candidates_to_practice_knowledge_result


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "h15_semantic_candidates"
    / "read_only_explain_schedule_candidates.json"
)
ROUTER_FILES = [
    "app/routers/appointments.py",
    "app/routers/bernie_dev.py",
    "app/routers/diary.py",
]
FORBIDDEN_ROUTE_FRAGMENTS = {
    "h15_semantic_candidates",
    "h15_advisory_adapter",
    "historical_diary_semantic_candidate_builder",
    "semantic_h15_candidate_fixtures",
    "semantic_h15_prototype_neutral_aggregate",
    "historical-diary-trove-h15-approved-gate",
}
REFERENCE_DATE = date(2026, 7, 6)


def _h15_advisory_frame():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    result = candidates_to_practice_knowledge_result(payload)
    return to_advisory_frame(
        result,
        reference_date=REFERENCE_DATE,
        reason_code="h15_synthetic_candidate_advisory",
    )


def test_h15_advisory_frame_does_not_create_route_authority():
    context = BernieReceptionContextFrameSet(
        reference_date=REFERENCE_DATE,
        frames=[
            BernieRequestedAppointmentFrame(
                status="known",
                basis="Synthetic instruction has enough detail for ordinary routing.",
                reference_date=REFERENCE_DATE,
            ),
            _h15_advisory_frame(),
        ],
    )

    decision = evaluate_reception_context(context)

    assert decision.availability == "not_evaluated"
    assert decision.can_search_slots is True
    assert decision.can_offer_candidates is False
    assert decision.can_prepare_proposal is False
    assert decision.search_ran_no_candidates is False
    assert decision.roster_unavailable is False
    assert decision.must_block_confirmation is False
    assert decision.advisory_warnings_only is True
    assert decision.reason_codes == ["h15_synthetic_candidate_advisory"]


def test_api_routes_do_not_import_h15_historical_diary_candidate_material():
    repo_root = Path(__file__).resolve().parents[1]
    errors = []
    for rel_path in ROUTER_FILES:
        path = repo_root / rel_path
        text = path.read_text(encoding="utf-8").lower()
        leaked = sorted(fragment for fragment in FORBIDDEN_ROUTE_FRAGMENTS if fragment in text)
        if leaked:
            errors.append(f"{rel_path}: forbidden H15 route fragment(s) {leaked}")

    assert not errors, "\n".join(errors)
