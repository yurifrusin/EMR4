import pytest

from scripts.historical_diary_semantic_candidate_builder import (
    build_semantic_candidates,
)


def approved_gate():
    return {
        "gate": "historical_diary_deidentification_gate",
        "version": 1,
        "decision": "approved_for_semantic_fixture_promotion",
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
            "reviewer": "yuri",
            "semantic_labelling_acknowledged": True,
            "approval_expires_on": "2027-01-01",
            "semantic_scope": {
                "fixture_families": ["action_grammar_candidates"],
                "prototype_slice": "single_root_single_dense_day_max_80",
                "memory_use": "prohibited",
            },
        },
    }


def neutral_aggregate():
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
                "dense_candidate_count": 80,
                "requested_sample_size": 2,
                "sampled_count": 2,
                "opened_count": 2,
                "error_count": 0,
                "structure_class_distribution": [
                    {"value": "strong_diary_grid", "count": 2}
                ],
                "neutral_signature_distribution": [
                    {
                        "value": "tables=2;cells=14;paragraphs=238;lines=167;times=78;dates=13;dims=1x11+1x3;mode=10",
                        "count": 2,
                    }
                ],
                "table_dimension_signature_distribution": [
                    {"value": "1x11+1x3", "count": 2}
                ],
                "inferred_time_interval_mode_minutes_distribution": [
                    {"value": "10", "count": 2}
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
                "ordered_neutral_snapshots": [
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
                    },
                    {
                        "sequence_index": 1,
                        "char_count": 3251,
                        "paragraph_count": 238,
                        "non_empty_paragraph_count": 169,
                        "non_empty_line_count": 167,
                        "table_count": 2,
                        "table_cell_count": 14,
                        "time_like_token_count": 78,
                        "unique_time_like_token_count": 37,
                        "date_like_token_count": 13,
                        "inferred_time_interval_mode_minutes": 10,
                        "paragraph_length_range": {"min": 1, "max": 91},
                        "table_dimension_signature": "1x11+1x3",
                        "structure_class": "strong_diary_grid",
                        "neutral_signature": "tables=2;cells=14;paragraphs=238;lines=167;times=78;dates=13;dims=1x11+1x3;mode=10",
                    },
                ],
            }
        ],
    }


def test_builds_low_confidence_candidates_from_safe_neutral_aggregate():
    payload = build_semantic_candidates(neutral_aggregate(), approved_gate())

    assert payload["source"] == "approved_h15_review_payload"
    assert payload["semantic_scope"]["fixture_family"] == "action_grammar_candidates"
    assert len(payload["fixtures"]) == 2
    assert {fixture["action_name"] for fixture in payload["fixtures"]} == {"status_change"}
    assert {fixture["confidence_label"] for fixture in payload["fixtures"]} == {"low"}
    assert {fixture["status_categories"][0] for fixture in payload["fixtures"]} == {"unknown"}


def test_rejects_unapproved_gate():
    gate = approved_gate()
    gate["decision"] = "blocked"
    gate["approval"]["semantic_labelling_acknowledged"] = False

    with pytest.raises(ValueError, match="approved gate"):
        build_semantic_candidates(neutral_aggregate(), gate)


def test_rejects_sample_size_above_approved_cap():
    aggregate = neutral_aggregate()
    aggregate["roots"][0]["requested_sample_size"] = 81

    with pytest.raises(ValueError, match="sample size"):
        build_semantic_candidates(aggregate, approved_gate())


def test_rejects_missing_ordered_snapshots():
    aggregate = neutral_aggregate()
    del aggregate["roots"][0]["ordered_neutral_snapshots"]

    with pytest.raises(ValueError, match="ordered neutral snapshots"):
        build_semantic_candidates(aggregate, approved_gate())


def test_rejects_aggregate_with_raw_path_key():
    aggregate = neutral_aggregate()
    aggregate["roots"][0]["raw_path"] = r"C:\raw\diary.doc"

    with pytest.raises(Exception, match="allowlist|path"):
        build_semantic_candidates(aggregate, approved_gate())
