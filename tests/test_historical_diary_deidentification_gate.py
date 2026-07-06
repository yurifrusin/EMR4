import json

import pytest

from scripts.historical_diary_deidentification_gate import (
    DeidentificationGateError,
    validate_deidentification_gate,
    main,
)


def safe_gate(**overrides):
    payload = {
        "gate": "historical_diary_deidentification_gate",
        "version": 1,
        "decision": "blocked",
        "privacy": {
            "local_raw_processing_only": True,
            "raw_data_external_provider_allowed": False,
            "commit_raw_or_extracted_text_allowed": False,
            "commit_identifying_labels_allowed": False,
        },
        "deidentification_policy": {
            "date_policy": "relative_day_index_only",
            "resource_policy": "synthetic_resource_ids_only",
            "text_policy": "bucket_flags_only",
        },
        "allowed_committed_fields": [
            "synthetic_event_ids",
            "relative_sequence_indexes",
            "relative_day_indexes",
            "time_of_day",
            "duration_minutes",
            "synthetic_resource_ids",
            "status_categories",
            "transition_labels",
            "confidence_labels",
            "count_distributions",
            "bucket_flags",
        ],
        "forbidden_committed_categories": [
            "names",
            "phone_numbers",
            "medicare_numbers",
            "addresses",
            "free_text_notes",
            "staff_labels",
            "original_filenames",
            "exact_source_timestamps",
            "external_raw_uploads",
        ],
        "approval": {
            "reviewer": "",
            "semantic_labelling_acknowledged": False,
        },
    }
    payload.update(overrides)
    return payload


def assert_gate_unsafe(payload, reason_fragment):
    with pytest.raises(DeidentificationGateError) as error:
        validate_deidentification_gate(payload)
    reasons = " ".join(issue.reason for issue in error.value.issues)
    assert reason_fragment in reasons


def test_accepts_blocked_safe_gate():
    validate_deidentification_gate(safe_gate())


def test_rejects_raw_external_provider_permission():
    payload = safe_gate()
    payload["privacy"]["raw_data_external_provider_allowed"] = True

    assert_gate_unsafe(payload, "must be false")


def test_rejects_unknown_allowed_committed_field():
    payload = safe_gate()
    payload["allowed_committed_fields"].append("patient_names")

    assert_gate_unsafe(payload, "unsafe or unknown committed fields")


def test_rejects_missing_forbidden_category():
    payload = safe_gate()
    payload["forbidden_committed_categories"].remove("medicare_numbers")

    assert_gate_unsafe(payload, "missing required forbidden categories")


def test_rejects_person_like_gate_values():
    payload = safe_gate()
    payload["approval"]["reviewer"] = "Jane Smith"

    assert_gate_unsafe(payload, "person or staff label")


def test_semantic_approval_requires_acknowledgement():
    payload = safe_gate(decision="approved_for_semantic_fixture_promotion")
    payload["approval"]["reviewer"] = "reviewer_1"

    assert_gate_unsafe(payload, "explicit acknowledgement")


def test_accepts_semantic_approval_with_safe_reviewer_and_acknowledgement():
    payload = safe_gate(decision="approved_for_semantic_fixture_promotion")
    payload["approval"]["reviewer"] = "reviewer_1"
    payload["approval"]["semantic_labelling_acknowledged"] = True

    validate_deidentification_gate(payload)


def test_cli_accepts_safe_gate(tmp_path, monkeypatch):
    gate_path = tmp_path / "gate.json"
    gate_path.write_text(json.dumps(safe_gate()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["historical_diary_deidentification_gate.py", str(gate_path)],
    )

    assert main() == 0
