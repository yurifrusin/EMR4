import json
from pathlib import Path

from app.services.diary.action_grammar import action_verb_for_envelope, get_verb_descriptor
from app.services.diary.capabilities import BernieCapabilityTier
from tests.action_grammar_replay import replay


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "h15_semantic_candidates"
SCHEMA_VERSION = "h15.semantic_candidate_fixture.v1"
FORBIDDEN_FRAGMENTS = {
    "local_data",
    "historical-diary-trove",
    "h_series",
    "h-series",
    "status_change",
    "create",
    "move",
    "resize",
    "cancel",
    "check_in",
    "waiting_area_move",
    "link_patient",
    "patient arrived",
    "booking",
    "appointment",
}


def _load_fixtures():
    paths = sorted(FIXTURE_DIR.glob("*.json"))
    assert paths, "expected committed H15 semantic candidate fixtures"
    return [(path, json.loads(path.read_text(encoding="utf-8"))) for path in paths]


def test_h15_semantic_candidate_fixtures_are_authored_synthetic():
    for path, payload in _load_fixtures():
        assert payload["schema_version"] == SCHEMA_VERSION, path.name
        assert payload["source"] == "authored_synthetic", path.name
        assert payload["fixture_family"] == "action_grammar_candidates", path.name
        assert len(payload["candidates"]) <= 5, path.name
        assert payload["privacy"] == {
            "local_raw_processing_only": False,
            "raw_data_external_provider_allowed": False,
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
        }


def test_h15_semantic_candidate_fixtures_are_read_only_explain_schedule_only():
    for path, payload in _load_fixtures():
        for candidate in payload["candidates"]:
            assert candidate["action_name"] == "explain_schedule", path.name
            verb = action_verb_for_envelope(candidate["action_name"])
            assert verb is not None
            descriptor = get_verb_descriptor(verb)
            assert descriptor.tier is BernieCapabilityTier.read_only
            assert descriptor.mutating is False
            assert descriptor.requires_staff_confirmation is False
            assert descriptor.confirm_actions == ()
            assert candidate["status_categories"] == ["unknown"]
            assert candidate["confidence_label"] == "low"


def test_h15_semantic_candidate_fixtures_do_not_reference_local_or_mutating_material():
    for path, payload in _load_fixtures():
        serialized = json.dumps(payload, sort_keys=True).lower()
        leaked = sorted(fragment for fragment in FORBIDDEN_FRAGMENTS if fragment in serialized)
        assert not leaked, f"{path.name}: forbidden fragment(s) {leaked}"


def test_h15_semantic_candidate_fixtures_replay_as_read_only_actions():
    for path, payload in _load_fixtures():
        script = {
            "id": f"h15-{path.stem}",
            "actions": [
                {
                    "raw_name": candidate["action_name"],
                    "expected_verb": "explain_schedule",
                    "expected_dispatch": "route_read_only",
                    "expected_mutating": False,
                    "expected_implemented": True,
                    "requires_staff_confirmation": False,
                    "confirm_actions_non_empty": False,
                    "expected_affordance_allowed": None,
                    "expected_affordance_gate": None,
                }
                for candidate in payload["candidates"]
            ],
        }

        result = replay.run_day_script(script)
        assert result.passed, "\n".join(result.failures)
