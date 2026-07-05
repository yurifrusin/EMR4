import json

from scripts.historical_diary_event_summary_compare import compare_event_summaries, main
from scripts.historical_diary_output_safety import validate_historical_diary_output


def summary_payload(root_label, no_change, small_delta):
    return {
        "classifier": {
            "output_class": "aggregate_neutral_timeline_events",
            "version": 1,
            "sample_only": True,
        },
        "privacy": {
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
        },
        "generated_at_utc": "2026-07-05T22:42:00Z",
        "event_model": {
            "version": 1,
            "sample_only": True,
            "output_class": "aggregate_neutral_timeline_events",
        },
        "roots": [
            {
                "root_label": root_label,
                "snapshot_count": 40,
                "transition_count": 39,
                "event_class_distribution": [
                    {"value": "no_structural_change", "count": no_change},
                    {"value": "small_content_delta", "count": small_delta},
                ],
                "adjacent_neutral_delta_ranges": {
                    "char_count_abs_delta_range": {"min": 0, "max": 100},
                    "paragraph_count_abs_delta_range": {"min": 0, "max": 7},
                    "non_empty_line_count_abs_delta_range": {"min": 0, "max": 4},
                    "time_like_token_count_abs_delta_range": {"min": 0, "max": 1},
                    "date_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                },
            }
        ],
    }


def test_compares_event_summary_distributions_safely():
    output = compare_event_summaries(
        summary_payload("synthetic_pilot", no_change=29, small_delta=10),
        summary_payload("synthetic_pilot", no_change=21, small_delta=18),
    )

    validate_historical_diary_output(output)
    root = output["roots"][0]

    assert output["summary_comparison"]["root_match_count"] == 1
    assert root["snapshot_count_delta"] == 0
    assert root["transition_count_delta"] == 0
    assert root["comparison"] == [
        {"value": "no_structural_change", "count": -8},
        {"value": "small_content_delta", "count": 8},
    ]


def test_cli_writes_safe_comparison(tmp_path, monkeypatch):
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    output_path = tmp_path / "comparison.json"
    baseline_path.write_text(
        json.dumps(summary_payload("synthetic_pilot", no_change=29, small_delta=10)),
        encoding="utf-8",
    )
    candidate_path.write_text(
        json.dumps(summary_payload("synthetic_pilot", no_change=21, small_delta=18)),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "historical_diary_event_summary_compare.py",
            str(baseline_path),
            str(candidate_path),
            "--output",
            str(output_path),
        ],
    )

    assert main() == 0

    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_historical_diary_output(output)
    assert output["classifier"]["output_class"] == "summary_comparison"
