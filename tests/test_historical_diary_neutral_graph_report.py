import json

from scripts.historical_diary_neutral_graph_report import (
    build_neutral_graph_report,
    main,
)
from scripts.historical_diary_output_safety import validate_historical_diary_output


def graph_payload():
    return {
        "classifier": {
            "output_class": "neutral_derived_graph",
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
        "graph": {
            "version": 1,
            "sample_only": True,
            "output_class": "neutral_derived_graph",
            "root_count": 1,
            "node_count": 4,
            "edge_count": 2,
            "transition_count": 3,
        },
        "nodes": [
            {
                "node_id": "root:synthetic_alpha",
                "node_kind": "root",
                "root_label": "synthetic_alpha",
                "snapshot_count": 4,
                "transition_count": 3,
            },
            {
                "node_id": "event_class:time_grid_delta",
                "node_kind": "event_class",
                "event_class": "time_grid_delta",
            },
            {
                "node_id": "event_class:large_unexplained_delta",
                "node_kind": "event_class",
                "event_class": "large_unexplained_delta",
            },
            {
                "node_id": "delta_bucket:char_count_abs_delta_range:large",
                "node_kind": "delta_bucket",
                "value": "char_count_abs_delta_range:large",
            },
        ],
        "edges": [
            {
                "edge_id": "edge:synthetic_alpha:time_grid_delta",
                "edge_kind": "has_event_class_count",
                "source_node_id": "root:synthetic_alpha",
                "target_node_id": "event_class:time_grid_delta",
                "count": 1,
            },
            {
                "edge_id": "edge:synthetic_alpha:char_count_abs_delta_range:large",
                "edge_kind": "has_delta_bucket",
                "source_node_id": "root:synthetic_alpha",
                "target_node_id": "delta_bucket:char_count_abs_delta_range:large",
                "min": 0,
                "max": 214,
            },
        ],
    }


def test_builds_safe_predefined_graph_report():
    output = build_neutral_graph_report(graph_payload())

    validate_historical_diary_output(output)
    assert output["classifier"]["output_class"] == "neutral_graph_query_report"
    assert output["queries"][0] == {
        "query_id": "roots_by_notable_event_class",
        "event_class": "large_unexplained_delta",
        "result_count": 0,
        "roots": [],
    }
    assert output["queries"][1] == {
        "query_id": "roots_by_notable_event_class",
        "event_class": "time_grid_delta",
        "result_count": 1,
        "roots": [
            {
                "root_label": "synthetic_alpha",
                "event_class": "time_grid_delta",
                "count": 1,
            }
        ],
    }
    assert output["queries"][2]["query_id"] == "roots_by_delta_bucket"
    assert output["queries"][2]["roots"][0]["max"] == 214


def test_cli_writes_safe_output(tmp_path, monkeypatch):
    input_path = tmp_path / "graph.json"
    output_path = tmp_path / "report.json"
    input_path.write_text(json.dumps(graph_payload()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "historical_diary_neutral_graph_report.py",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    assert main() == 0
    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_historical_diary_output(output)
    assert output["graph"]["output_class"] == "neutral_graph_query_report"
