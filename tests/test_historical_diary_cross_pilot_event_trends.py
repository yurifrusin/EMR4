import json

import pytest

from scripts.historical_diary_cross_pilot_event_trends import (
    build_cross_pilot_event_trends,
    main,
)
from scripts.historical_diary_output_safety import validate_historical_diary_output


def event_summary(root_label, events):
    transition_count = sum(events.values())
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
        "generated_at_utc": "2026-07-06T00:00:00Z",
        "event_model": {
            "version": 1,
            "sample_only": True,
            "output_class": "aggregate_neutral_timeline_events",
        },
        "roots": [
            {
                "root_label": root_label,
                "snapshot_count": transition_count + 1,
                "transition_count": transition_count,
                "event_class_distribution": [
                    {"value": value, "count": count}
                    for value, count in sorted(events.items())
                ],
                "adjacent_neutral_delta_ranges": {
                    "char_count_abs_delta_range": {"min": 0, "max": 100},
                    "paragraph_count_abs_delta_range": {"min": 0, "max": 2},
                    "non_empty_line_count_abs_delta_range": {"min": 0, "max": 1},
                    "time_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                    "date_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                },
            }
        ],
    }


def test_builds_safe_cross_pilot_trend_table():
    output = build_cross_pilot_event_trends(
        [
            event_summary("synthetic_beta", {"no_structural_change": 2}),
            event_summary(
                "synthetic_alpha",
                {
                    "large_unexplained_delta": 1,
                    "no_structural_change": 1,
                    "time_grid_delta": 1,
                },
            ),
        ]
    )

    validate_historical_diary_output(output)
    assert output["classifier"]["output_class"] == "cross_pilot_event_trends"
    assert output["summary_comparison"]["root_count"] == 2
    assert output["roots"][0]["root_label"] == "synthetic_alpha"
    assert output["roots"][0]["large_delta_triage"] == [
        {"event_class": "large_unexplained_delta", "count": 1},
        {"event_class": "time_grid_delta", "count": 1},
    ]
    assert output["roots"][1]["large_delta_triage"] == [
        {"event_class": "large_unexplained_delta", "count": 0},
        {"event_class": "time_grid_delta", "count": 0},
    ]


def test_rejects_duplicate_root_labels():
    with pytest.raises(ValueError, match="duplicate root_label"):
        build_cross_pilot_event_trends(
            [
                event_summary("synthetic_alpha", {"no_structural_change": 1}),
                event_summary("synthetic_alpha", {"small_content_delta": 1}),
            ]
        )


def test_cli_writes_safe_output(tmp_path, monkeypatch):
    input_a = tmp_path / "event_summary_a.json"
    input_b = tmp_path / "event_summary_b.json"
    output_path = tmp_path / "cross_pilot_event_trends.json"
    input_a.write_text(
        json.dumps(event_summary("synthetic_alpha", {"no_structural_change": 2})),
        encoding="utf-8",
    )
    input_b.write_text(
        json.dumps(event_summary("synthetic_beta", {"small_content_delta": 1})),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "historical_diary_cross_pilot_event_trends.py",
            str(input_a),
            str(input_b),
            "--output",
            str(output_path),
        ],
    )

    assert main() == 0
    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_historical_diary_output(output)
    assert output["summary_comparison"]["total_sampled_count"] == 5
