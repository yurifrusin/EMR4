import json

from scripts.historical_diary_neutral_graph_export import (
    build_neutral_derived_graph,
    main,
)
from scripts.historical_diary_output_safety import validate_historical_diary_output


def trend_payload():
    return {
        "classifier": {
            "output_class": "cross_pilot_event_trends",
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
        "summary_comparison": {
            "version": 1,
            "sample_only": True,
            "output_class": "cross_pilot_event_trends",
            "root_count": 2,
            "total_sampled_count": 5,
        },
        "roots": [
            {
                "root_label": "synthetic_beta",
                "snapshot_count": 2,
                "transition_count": 1,
                "event_class_distribution": [
                    {"value": "small_content_delta", "count": 1}
                ],
                "large_delta_triage": [
                    {"event_class": "large_unexplained_delta", "count": 0},
                    {"event_class": "time_grid_delta", "count": 0},
                ],
                "adjacent_neutral_delta_ranges": {
                    "char_count_abs_delta_range": {"min": 0, "max": 10},
                    "paragraph_count_abs_delta_range": {"min": 0, "max": 1},
                    "non_empty_line_count_abs_delta_range": {"min": 0, "max": 1},
                    "time_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                    "date_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                },
            },
            {
                "root_label": "synthetic_alpha",
                "snapshot_count": 3,
                "transition_count": 2,
                "event_class_distribution": [
                    {"value": "no_structural_change", "count": 2}
                ],
                "large_delta_triage": [
                    {"event_class": "large_unexplained_delta", "count": 0},
                    {"event_class": "time_grid_delta", "count": 0},
                ],
                "adjacent_neutral_delta_ranges": {
                    "char_count_abs_delta_range": {"min": 0, "max": 0},
                    "paragraph_count_abs_delta_range": {"min": 0, "max": 0},
                    "non_empty_line_count_abs_delta_range": {"min": 0, "max": 0},
                    "time_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                    "date_like_token_count_abs_delta_range": {"min": 0, "max": 0},
                },
            },
        ],
    }


def test_builds_safe_neutral_graph():
    output = build_neutral_derived_graph(trend_payload())

    validate_historical_diary_output(output)
    assert output["classifier"]["output_class"] == "neutral_derived_graph"
    assert output["graph"] == {
        "version": 1,
        "sample_only": True,
        "output_class": "neutral_derived_graph",
        "root_count": 2,
        "node_count": 4,
        "edge_count": 2,
        "transition_count": 3,
    }
    assert output["nodes"][0]["node_id"] == "root:synthetic_alpha"
    assert output["edges"] == [
        {
            "edge_id": "edge:synthetic_alpha:no_structural_change",
            "edge_kind": "has_event_class_count",
            "source_node_id": "root:synthetic_alpha",
            "target_node_id": "event_class:no_structural_change",
            "count": 2,
        },
        {
            "edge_id": "edge:synthetic_beta:small_content_delta",
            "edge_kind": "has_event_class_count",
            "source_node_id": "root:synthetic_beta",
            "target_node_id": "event_class:small_content_delta",
            "count": 1,
        },
    ]


def test_cli_writes_safe_output(tmp_path, monkeypatch):
    input_path = tmp_path / "trend.json"
    output_path = tmp_path / "graph.json"
    input_path.write_text(json.dumps(trend_payload()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "historical_diary_neutral_graph_export.py",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    assert main() == 0
    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_historical_diary_output(output)
    assert output["graph"]["edge_count"] == 2
