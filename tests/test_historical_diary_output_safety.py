import pytest

from scripts.historical_diary_output_safety import (
    HistoricalDiaryOutputSafetyError,
    validate_historical_diary_output,
    validate_historical_diary_semantic_fixture_output,
)


def safe_payload():
    return {
        "generated_at_utc": "2026-07-05T22:03:06.2441153Z",
        "privacy": {
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
            "opens_documents_read_only": True,
            "macro_security_forced_disabled": True,
        },
        "classifier": {
            "version": 1,
            "sample_only": True,
            "output_class": "aggregate_neutral_layout_facts",
        },
        "roots": [
            {
                "root_label": "pilot_01",
                "dense_candidate_count": 305,
                "requested_sample_size": 8,
                "sampled_count": 8,
                "opened_count": 8,
                "error_count": 0,
                "structure_class_distribution": [
                    {"value": "strong_diary_grid", "count": 8}
                ],
                "neutral_signature_distribution": [
                    {
                        "value": "tables=2;cells=14;paragraphs=238;lines=167;times=78;dates=13;dims=1x11+1x3;mode=10",
                        "count": 3,
                    }
                ],
                "table_dimension_signature_distribution": [
                    {"value": "1x11+1x3", "count": 8}
                ],
                "inferred_time_interval_mode_minutes_distribution": [
                    {"value": "10", "count": 8}
                ],
                "char_count_range": {"min": 3118, "max": 3251},
                "paragraph_count_range": {"min": 232, "max": 238},
                "non_empty_paragraph_count_range": {"min": 165, "max": 169},
                "non_empty_line_count_range": {"min": 162, "max": 167},
                "table_count_range": {"min": 2, "max": 2},
                "table_cell_count_range": {"min": 14, "max": 14},
                "time_like_token_count_range": {"min": 78, "max": 78},
                "unique_time_like_token_count_range": {"min": 37, "max": 37},
                "date_like_token_count_range": {"min": 13, "max": 13},
                "paragraph_length_range": {"min": 1, "max": 91},
                "adjacent_neutral_delta_ranges": {
                    "char_count_abs_delta_range": {"min": 0, "max": 109},
                    "paragraph_count_abs_delta_range": {"min": 0, "max": 5},
                    "non_empty_line_count_abs_delta_range": {"min": 0, "max": 4},
                    "time_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                    "date_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                },
            }
        ],
    }


def assert_unsafe(payload, reason_fragment):
    with pytest.raises(HistoricalDiaryOutputSafetyError) as error:
        validate_historical_diary_output(payload)
    reasons = " ".join(issue.reason for issue in error.value.issues)
    assert reason_fragment in reasons


def safe_semantic_payload():
    return {
        "schema_version": "historical_diary.semantic_fixture.v1",
        "source": "approved_h15_review_payload",
        "privacy": {
            "local_raw_processing_only": True,
            "raw_data_external_provider_allowed": False,
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
        },
        "semantic_scope": {
            "fixture_family": "action_grammar_candidates",
            "date_policy": "relative_day_index_only",
            "allowed_action_names": ["create", "move", "status_change"],
            "approval_expires_on": "2027-01-01",
        },
        "fixtures": [
            {
                "synthetic_event_id": "event_001",
                "relative_day_index": 0,
                "time_of_day": "time_bucket_001",
                "duration_minutes": 10,
                "synthetic_resource_id": "resource_001",
                "action_name": "create",
                "status_categories": ["candidate"],
                "transition_label": "candidate_create",
                "confidence_label": "low",
                "bucket_flags": ["has_time_bucket"],
            }
        ],
    }


def assert_semantic_unsafe(payload, reason_fragment):
    with pytest.raises(HistoricalDiaryOutputSafetyError) as error:
        validate_historical_diary_semantic_fixture_output(payload)
    reasons = " ".join(issue.reason for issue in error.value.issues)
    assert reason_fragment in reasons


def test_accepts_safe_aggregate_classifier_payload():
    validate_historical_diary_output(safe_payload())


def test_accepts_safe_ordered_neutral_snapshot_payload():
    payload = safe_payload()
    payload["roots"][0]["ordered_neutral_snapshots"] = [
        {
            "sequence_index": 0,
            "char_count": 3118,
            "paragraph_count": 232,
            "non_empty_paragraph_count": 165,
            "non_empty_line_count": 162,
            "table_count": 2,
            "table_cell_count": 14,
            "time_like_token_count": 78,
            "unique_time_like_token_count": 37,
            "date_like_token_count": 13,
            "inferred_time_interval_mode_minutes": 10,
            "paragraph_length_range": {"min": 1, "max": 91},
            "table_dimension_signature": "1x11+1x3",
            "structure_class": "strong_diary_grid",
            "neutral_signature": "tables=2;cells=14;paragraphs=232;lines=162;times=78;dates=13;dims=1x11+1x3;mode=10",
        }
    ]

    validate_historical_diary_output(payload)


def test_rejects_unknown_keys_that_could_bypass_the_allowlist():
    payload = safe_payload()
    payload["roots"][0]["unexpected"] = "strong_diary_grid"

    assert_unsafe(payload, "key is not in the committed-output allowlist")


def test_rejects_raw_filename_fields():
    payload = safe_payload()
    payload["roots"][0]["filename"] = "diary.doc"

    assert_unsafe(payload, "key is not in the committed-output allowlist")


def test_rejects_raw_path_values():
    payload = safe_payload()
    payload["roots"][0]["value"] = r"C:\Users\sarashera\emr4\local_data\raw\diary.doc"

    assert_unsafe(payload, "string looks like a raw file path")


def test_rejects_document_text_fields():
    payload = safe_payload()
    payload["roots"][0]["document_text"] = "free text"

    assert_unsafe(payload, "key is not in the committed-output allowlist")


def test_rejects_exact_document_timestamp_fields():
    payload = safe_payload()
    payload["roots"][0]["last_write_time_utc"] = "2021-03-05T12:34:56Z"

    assert_unsafe(payload, "key is not in the committed-output allowlist")


def test_rejects_likely_person_or_staff_labels():
    payload = safe_payload()
    payload["roots"][0]["value"] = "Jane Smith"

    assert_unsafe(payload, "string looks like a person or staff label")


def test_rejects_long_text_snippets_even_under_allowed_value_key():
    payload = safe_payload()
    payload["roots"][0]["value"] = "x" * 161

    assert_unsafe(payload, "string is too long")


def test_accepts_safe_semantic_fixture_payload_after_h15_review_shape():
    validate_historical_diary_semantic_fixture_output(safe_semantic_payload())


def test_semantic_fixture_rejects_external_provider_permission():
    payload = safe_semantic_payload()
    payload["privacy"]["raw_data_external_provider_allowed"] = True

    assert_semantic_unsafe(payload, "must be False")


def test_semantic_fixture_rejects_unsupported_action_name():
    payload = safe_semantic_payload()
    payload["fixtures"][0]["action_name"] = "invent_booking"

    assert_semantic_unsafe(payload, "unsupported action name")


def test_semantic_fixture_rejects_raw_booking_phrasing():
    payload = safe_semantic_payload()
    payload["fixtures"][0]["transition_label"] = "patient arrived"

    assert_semantic_unsafe(payload, "raw booking semantics")


def test_semantic_fixture_requires_approval_expiry():
    payload = safe_semantic_payload()
    del payload["semantic_scope"]["approval_expires_on"]

    assert_semantic_unsafe(payload, "approval expiry is required")
