from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.ai.evals.bernie_shadow_corpus import load_shadow_corpus


CORPUS = Path("tests/fixtures/bernie_shadow_eval/t1_t2_authored_cases.json")
KNOWN_SOURCES = {
    "booking_seeded_exact_duplicate",
    "booking_overlap_not_exact_duplicate",
    "booking_roster_unavailable_distinct_from_no_slots",
    "same_day_past_window_clarify",
}


def read_payload() -> dict:
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def write_payload(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "corpus.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_authored_t1_t2_projection_loads_as_shadow_cases():
    cases = load_shadow_corpus(CORPUS, known_source_ids=KNOWN_SOURCES)

    assert len(cases) == 4
    assert len({case.case_id for case in cases}) == 4
    assert all(case.source.startswith("authored_synthetic:t1_t2:") for case in cases)
    assert all("Margaret" not in case.instruction for case in cases)
    assert cases[0].expected.tool_name == "search_available_slots"
    assert cases[-1].expected.requires_clarification is True


def test_every_projection_cites_an_existing_scenario_fixture():
    fixture_ids = {
        path.stem
        for path in Path("tests/fixtures/bernie_scenarios").glob("*.yaml")
    }
    assert KNOWN_SOURCES <= fixture_ids
    load_shadow_corpus(CORPUS, known_source_ids=fixture_ids)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda payload: payload.update(source="generated"), "authored_synthetic"),
        (
            lambda payload: payload["cases"][0].update(source_scenario_id="unknown"),
            "known T1/T2",
        ),
        (
            lambda payload: payload["cases"][0]["expected"].update(authorship="generated"),
            "must be manual",
        ),
        (
            lambda payload: payload["cases"][0].update(initial_state={"appointments": []}),
            "unsupported fields",
        ),
        (
            lambda payload: payload["cases"][0]["expected"]["entities"].update(
                patient_ref="Margaret Thompson"
            ),
            "synthetic- alias",
        ),
        (
            lambda payload: payload["cases"][0]["expected"].update(
                patient_id="fixture-patient-id"
            ),
            "unsupported fields",
        ),
        (
            lambda payload: payload["cases"][0].update(
                allowed_tools=["confirm_appointment"]
            ),
            "unsupported tool",
        ),
    ],
)
def test_loader_rejects_boundary_drift(tmp_path, mutate, message):
    payload = read_payload()
    mutate(payload)
    with pytest.raises(ValueError, match=message):
        load_shadow_corpus(write_payload(tmp_path, payload), known_source_ids=KNOWN_SOURCES)


def test_loader_rejects_expected_tool_missing_from_allowlist(tmp_path):
    payload = read_payload()
    payload["cases"][0]["allowed_tools"] = []
    with pytest.raises(ValueError, match="expected tool"):
        load_shadow_corpus(write_payload(tmp_path, payload), known_source_ids=KNOWN_SOURCES)


def test_loader_rejects_duplicate_case_ids(tmp_path):
    payload = read_payload()
    payload["cases"][1]["id"] = payload["cases"][0]["id"]
    with pytest.raises(ValueError, match="duplicate shadow case"):
        load_shadow_corpus(write_payload(tmp_path, payload), known_source_ids=KNOWN_SOURCES)


def test_loader_rejects_invalid_json(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("not-json", encoding="utf-8")
    with pytest.raises(ValueError, match="Unable to load"):
        load_shadow_corpus(path, known_source_ids=KNOWN_SOURCES)
