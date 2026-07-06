import json

from scripts.historical_diary_large_delta_triage import build_large_delta_triage, main
from scripts.historical_diary_output_safety import validate_historical_diary_output


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
        "generated_at_utc": "2026-07-05T22:56:41Z",
        "roots": [
            {
                "root_label": "synthetic_pilot",
                "dense_candidate_count": 3,
                "requested_sample_size": 3,
                "sampled_count": 3,
                "opened_count": 3,
                "error_count": 0,
                "ordered_neutral_snapshots": [
                    snapshot(0, char_count=3000, paragraph_count=200),
                    snapshot(1, char_count=3050, paragraph_count=200),
                    snapshot(2, char_count=3600, paragraph_count=200),
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


def test_builds_safe_large_delta_triage():
    output = build_large_delta_triage(ordered_payload())

    validate_historical_diary_output(output)
    root = output["roots"][0]

    assert root["triaged_transition_count"] == 1
    triage_item = root["large_delta_triage"][0]
    assert triage_item["transition_index"] == 1
    assert triage_item["event_class"] == "large_unexplained_delta"
    assert triage_item["before_counts"]["sequence_index"] == 1
    assert triage_item["after_counts"]["sequence_index"] == 2
    assert triage_item["adjacent_neutral_delta_ranges"][
        "char_count_abs_delta_range"
    ] == {"min": 550, "max": 550}


def test_cli_writes_safe_large_delta_triage(tmp_path, monkeypatch):
    input_path = tmp_path / "ordered.json"
    output_path = tmp_path / "triage.json"
    input_path.write_text(json.dumps(ordered_payload()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "historical_diary_large_delta_triage.py",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    assert main() == 0

    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_historical_diary_output(output)
    assert output["classifier"]["output_class"] == "large_delta_triage"
