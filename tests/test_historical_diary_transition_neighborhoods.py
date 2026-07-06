import json

from scripts.historical_diary_output_safety import validate_historical_diary_output
from scripts.historical_diary_transition_neighborhoods import (
    build_transition_neighborhoods,
    main,
)


def ordered_payload():
    return {
        "classifier": {
            "output_class": "aggregate_neutral_layout_facts",
            "version": 1,
            "sample_only": True,
        },
        "privacy": {
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
            "opens_documents_read_only": True,
            "macro_security_forced_disabled": True,
        },
        "generated_at_utc": "2026-07-06T00:00:00Z",
        "roots": [
            {
                "root_label": "synthetic_pilot",
                "dense_candidate_count": 4,
                "requested_sample_size": 4,
                "sampled_count": 4,
                "opened_count": 4,
                "error_count": 0,
                "ordered_neutral_snapshots": [
                    snapshot(0, char_count=3000, time_like_token_count=80),
                    snapshot(1, char_count=3050, time_like_token_count=80),
                    snapshot(2, char_count=3601, time_like_token_count=80),
                    snapshot(3, char_count=3610, time_like_token_count=84),
                ],
            }
        ],
    }


def snapshot(sequence_index, **overrides):
    values = {
        "sequence_index": sequence_index,
        "char_count": 3000,
        "paragraph_count": 200,
        "non_empty_paragraph_count": 180,
        "non_empty_line_count": 160,
        "table_count": 2,
        "table_cell_count": 14,
        "time_like_token_count": 80,
        "unique_time_like_token_count": 38,
        "date_like_token_count": 12,
        "inferred_time_interval_mode_minutes": 10,
        "paragraph_length_range": {"min": 1, "max": 120},
        "table_dimension_signature": "1x11+1x3",
        "structure_class": "strong_diary_grid",
        "neutral_signature": "tables=2;cells=14;paragraphs=200;lines=160;times=80;dates=12;dims=1x11+1x3;mode=10",
    }
    values.update(overrides)
    return values


def test_builds_safe_transition_neighborhoods():
    output = build_transition_neighborhoods(ordered_payload(), radius=1)

    validate_historical_diary_output(output)
    root = output["roots"][0]

    assert root["neighborhood_count"] == 2
    large_neighborhood = root["transition_neighborhoods"][0]
    assert large_neighborhood["center_transition_index"] == 1
    assert large_neighborhood["event_class"] == "large_unexplained_delta"
    assert large_neighborhood["center_transition"]["relative_offset"] == 0
    assert [
        item["relative_offset"]
        for item in large_neighborhood["neighbor_transitions"]
    ] == [-1, 1]

    time_neighborhood = root["transition_neighborhoods"][1]
    assert time_neighborhood["center_transition_index"] == 2
    assert time_neighborhood["event_class"] == "time_grid_delta"


def test_cli_writes_safe_transition_neighborhoods(tmp_path, monkeypatch):
    input_path = tmp_path / "ordered.json"
    output_path = tmp_path / "neighborhoods.json"
    input_path.write_text(json.dumps(ordered_payload()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "historical_diary_transition_neighborhoods.py",
            str(input_path),
            "--output",
            str(output_path),
            "--radius",
            "1",
        ],
    )

    assert main() == 0

    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_historical_diary_output(output)
    assert output["classifier"]["output_class"] == "transition_neighborhoods"
