"""Provider-free Bernie interpretation harness tests."""

import inspect
import json
from pathlib import Path

import pytest

from app.services.bernie.interpretation_harness import (
    INTERPRETATION_HARNESS_SCHEMA_VERSION,
    InterpretationDispatch,
    InterpretationResult,
    assert_interpretation_result_consistency,
    interpret_receptionist_utterance,
)
from app.services.diary.action_grammar import DiaryActionVerb
from app.services.diary.action_route_contract import RouteAuthority


FIXTURE_DIR = (
    Path(__file__).parent
    / "fixtures"
    / "bernie_interpretation_harness"
)


def _cases():
    cases = []
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for case in payload["cases"]:
            cases.append({**case, "_fixture": path.name})
    return cases


def test_interpretation_harness_schema_version_pinned():
    assert INTERPRETATION_HARNESS_SCHEMA_VERSION == "bernie.interpretation_harness.v1"


def test_fixture_schema_is_authored_synthetic():
    paths = sorted(FIXTURE_DIR.glob("*.json"))
    assert paths
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == INTERPRETATION_HARNESS_SCHEMA_VERSION
        assert payload["source"] == "authored_synthetic"
        assert payload["cases"]


@pytest.mark.parametrize("case", _cases(), ids=lambda case: case["id"])
def test_authored_utterances_map_to_expected_grammar_actions(case):
    result = interpret_receptionist_utterance(case["utterance"])
    assert_interpretation_result_consistency(result)

    expected_verb = case["expected_verb"]
    expected_authority = case["expected_authority"]

    assert result.verb == (None if expected_verb is None else DiaryActionVerb(expected_verb))
    assert result.dispatch is InterpretationDispatch(case["expected_dispatch"])
    assert result.authority == (
        None if expected_authority is None else RouteAuthority(expected_authority)
    )


def test_empty_utterance_refuses_unknown():
    result = interpret_receptionist_utterance("   ")
    assert_interpretation_result_consistency(result)
    assert result.verb is None
    assert result.authority is None
    assert result.dispatch is InterpretationDispatch.refuse_unknown_utterance


def test_planned_actions_refuse_rather_than_route_to_confirm():
    for utterance in (
        "Check in the patient at reception.",
        "Move the patient to the waiting area.",
        "Link patient to the appointment.",
    ):
        result = interpret_receptionist_utterance(utterance)
        assert_interpretation_result_consistency(result)
        assert result.verb in {
            DiaryActionVerb.check_in,
            DiaryActionVerb.waiting_area_move,
            DiaryActionVerb.link_patient,
        }
        assert result.authority is RouteAuthority.planned_not_implemented
        assert result.dispatch is InterpretationDispatch.refuse_planned_not_implemented


def test_result_consistency_rejects_confirm_dispatch_without_signed_authority():
    bad = InterpretationResult(
        utterance="synthetic impossible result",
        verb=DiaryActionVerb.create,
        authority=RouteAuthority.read_only,
        dispatch=InterpretationDispatch.route_to_confirm,
        rationale="negative test",
    )
    with pytest.raises(AssertionError):
        assert_interpretation_result_consistency(bad)


def test_result_consistency_rejects_refusal_with_route_authority():
    bad = InterpretationResult(
        utterance="synthetic impossible result",
        verb=DiaryActionVerb.create,
        authority=RouteAuthority.signed_confirm,
        dispatch=InterpretationDispatch.refuse_unsafe_instruction,
        rationale="negative test",
    )
    with pytest.raises(AssertionError):
        assert_interpretation_result_consistency(bad)


def test_interpretation_harness_has_no_provider_route_db_memory_or_h15_coupling():
    import app.services.bernie.interpretation_harness as harness_module

    source = inspect.getsource(harness_module)
    forbidden = [
        "app.routers",
        "app.models",
        "SessionLocal",
        "get_db",
        "TestClient",
        "import google.genai",
        "import google.generativeai",
        "import vertexai",
        "import openai",
        "import anthropic",
        "from google",
        "from vertexai",
        "from openai",
        "from anthropic",
        "local_data",
        "historical_diary_semantic_candidate_builder",
        "h15_semantic_candidates",
        "h_series",
        "app.services.bernie.memory",
        "app.services.access_ai",
    ]
    for fragment in forbidden:
        assert fragment not in source


def test_interpretation_fixtures_contain_no_payload_or_route_fields():
    serialized = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in sorted(FIXTURE_DIR.glob("*.json"))
    )
    forbidden = [
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "payload",
        "/api/",
        "local_data",
        "h15",
        "h_series",
    ]
    for fragment in forbidden:
        assert fragment not in serialized
