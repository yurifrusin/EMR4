import json
from pathlib import Path

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


def add_safe_semantic_scope(payload):
    payload["approval"]["semantic_scope"] = {
        "fixture_families": ["action_grammar_candidates"],
        "prototype_slice": "single_root_single_dense_day_max_80",
        "memory_use": "prohibited",
    }
    payload["approval"]["approval_expires_on"] = "2027-01-01"
    return payload


def test_semantic_approval_requires_bounded_scope():
    payload = safe_gate(decision="approved_for_semantic_fixture_promotion")
    payload["approval"]["reviewer"] = "reviewer_1"
    payload["approval"]["semantic_labelling_acknowledged"] = True

    assert_gate_unsafe(payload, "semantic approval requires scope")


def test_semantic_approval_requires_date_shaped_expiry():
    payload = safe_gate(decision="approved_for_semantic_fixture_promotion")
    payload["approval"]["reviewer"] = "reviewer_1"
    payload["approval"]["semantic_labelling_acknowledged"] = True
    payload["approval"]["semantic_scope"] = {
        "fixture_families": ["action_grammar_candidates"],
        "prototype_slice": "single_root_single_dense_day_max_80",
        "memory_use": "prohibited",
    }
    payload["approval"]["approval_expires_on"] = "later"

    assert_gate_unsafe(payload, "YYYY-MM-DD expiry")


def test_accepts_semantic_approval_with_safe_reviewer_ack_scope_and_expiry():
    payload = safe_gate(decision="approved_for_semantic_fixture_promotion")
    payload["approval"]["reviewer"] = "reviewer_1"
    payload["approval"]["semantic_labelling_acknowledged"] = True
    add_safe_semantic_scope(payload)

    validate_deidentification_gate(payload)


def test_cli_accepts_safe_gate(tmp_path, monkeypatch):
    gate_path = tmp_path / "gate.json"
    gate_path.write_text(json.dumps(safe_gate()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["historical_diary_deidentification_gate.py", str(gate_path)],
    )

    assert main() == 0


def test_committed_h15_approval_payload_draft_remains_blocked():
    path = Path("docs/historical-diary-trove-h15-approval-payload-draft.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    validate_deidentification_gate(payload)
    assert payload["decision"] == "blocked"
    assert payload["approval"]["reviewer"] == ""
    assert payload["approval"]["semantic_labelling_acknowledged"] is False
    assert payload["draft_review"]["not_approved_until"] == "explicit_yuri_decision"


def test_committed_h15_approved_gate_payload_passes_with_bounded_scope():
    path = Path("docs/historical-diary-trove-h15-approved-gate.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    validate_deidentification_gate(payload)
    assert payload["decision"] == "approved_for_semantic_fixture_promotion"
    assert payload["approval"]["reviewer"] == "yuri"
    assert payload["approval"]["semantic_labelling_acknowledged"] is True
    assert payload["approval"]["semantic_scope"]["prototype_slice"] == (
        "single_root_single_dense_day_max_80"
    )
    assert payload["approval"]["semantic_scope"]["memory_use"] == "prohibited"
