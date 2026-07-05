import pytest

from scripts.historical_diary_output_safety import (
    HistoricalDiaryOutputSafetyError,
    validate_historical_diary_output,
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


def test_accepts_safe_aggregate_classifier_payload():
    validate_historical_diary_output(safe_payload())


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
