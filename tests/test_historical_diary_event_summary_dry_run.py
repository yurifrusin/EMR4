import json

from scripts.historical_diary_event_summary_dry_run import (
    main,
    summarize_aggregate_timeline,
)
from scripts.historical_diary_output_safety import validate_historical_diary_output


def aggregate_payload():
    return {
        "classifier": {
            "output_class": "aggregate_neutral_layout_facts",
            "version": 1,
            "sample_only": True,
        },
        "privacy": {
            "emits_patient_or_staff_labels": False,
            "opens_documents_read_only": True,
            "emits_document_text": False,
            "emits_exact_document_timestamps": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "macro_security_forced_disabled": True,
        },
        "generated_at_utc": "2026-07-05T22:15:34Z",
        "roots": [
            {
                "root_label": "synthetic_pilot",
                "opened_count": 4,
                "sampled_count": 4,
                "requested_sample_size": 4,
                "error_count": 0,
                "char_count_range": {"min": 4800, "max": 4900},
                "table_count_range": {"min": 2, "max": 2},
                "table_cell_count_range": {"min": 14, "max": 14},
                "paragraph_count_range": {"min": 252, "max": 255},
                "non_empty_line_count_range": {"min": 181, "max": 185},
                "time_like_token_count_range": {"min": 85, "max": 86},
                "unique_time_like_token_count_range": {"min": 39, "max": 39},
                "date_like_token_count_range": {"min": 11, "max": 11},
                "paragraph_length_range": {"min": 1, "max": 246},
                "dense_candidate_count": 20,
                "inferred_time_interval_mode_minutes_distribution": [
                    {"value": "10", "count": 4}
                ],
                "table_dimension_signature_distribution": [
                    {"value": "1x11+1x3", "count": 4}
                ],
                "structure_class_distribution": [
                    {"value": "strong_diary_grid", "count": 4}
                ],
                "neutral_signature_distribution": [
                    {
                        "value": "tables=2;cells=14;paragraphs=252;lines=181;times=85;dates=11;dims=1x11+1x3;mode=10",
                        "count": 2,
                    },
                    {
                        "value": "tables=2;cells=14;paragraphs=255;lines=185;times=86;dates=11;dims=1x11+1x3;mode=10",
                        "count": 2,
                    },
                ],
            }
        ],
    }


def test_summarizes_safe_aggregate_timeline_events():
    output = summarize_aggregate_timeline(aggregate_payload())

    validate_historical_diary_output(output)
    root = output["roots"][0]

    assert root["root_label"] == "synthetic_pilot"
    assert root["snapshot_count"] == 4
    assert root["transition_count"] == 3
    assert root["event_class_distribution"] == [
        {"value": "no_structural_change", "count": 2},
        {"value": "small_content_delta", "count": 1},
    ]


def test_prefers_ordered_neutral_snapshots_when_present():
    payload = aggregate_payload()
    payload["roots"][0]["ordered_neutral_snapshots"] = [
        {
            "sequence_index": 1,
            "char_count": 4900,
            "paragraph_count": 252,
            "non_empty_paragraph_count": 184,
            "non_empty_line_count": 181,
            "table_count": 2,
            "table_cell_count": 14,
            "table_dimension_signature": "1x11+1x3",
            "time_like_token_count": 85,
            "unique_time_like_token_count": 39,
            "date_like_token_count": 11,
            "inferred_time_interval_mode_minutes": 10,
            "paragraph_length_range": {"min": 1, "max": 246},
            "structure_class": "strong_diary_grid",
            "neutral_signature": "tables=2;cells=14;paragraphs=252;lines=181;times=85;dates=11;dims=1x11+1x3;mode=10",
        },
        {
            "sequence_index": 0,
            "char_count": 4800,
            "paragraph_count": 252,
            "non_empty_paragraph_count": 184,
            "non_empty_line_count": 181,
            "table_count": 2,
            "table_cell_count": 14,
            "table_dimension_signature": "1x11+1x3",
            "time_like_token_count": 85,
            "unique_time_like_token_count": 39,
            "date_like_token_count": 11,
            "inferred_time_interval_mode_minutes": 10,
            "paragraph_length_range": {"min": 1, "max": 246},
            "structure_class": "strong_diary_grid",
            "neutral_signature": "tables=2;cells=14;paragraphs=252;lines=181;times=85;dates=11;dims=1x11+1x3;mode=10",
        },
    ]

    output = summarize_aggregate_timeline(payload)

    validate_historical_diary_output(output)
    assert output["roots"][0]["adjacent_neutral_delta_ranges"][
        "char_count_abs_delta_range"
    ] == {"min": 100, "max": 100}


def test_cli_writes_safe_ignored_style_output(tmp_path, monkeypatch):
    input_path = tmp_path / "aggregate.json"
    output_path = tmp_path / "event_summary.json"
    input_path.write_text(json.dumps(aggregate_payload()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "historical_diary_event_summary_dry_run.py",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    assert main() == 0

    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_historical_diary_output(output)
    assert output["classifier"]["output_class"] == "aggregate_neutral_timeline_events"
