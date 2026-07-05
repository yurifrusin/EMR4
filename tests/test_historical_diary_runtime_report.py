import json

from scripts.historical_diary_output_safety import validate_historical_diary_output
from scripts.historical_diary_runtime_report import build_runtime_report, main


def probe_payload():
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
        "generated_at_utc": "2026-07-05T22:42:00Z",
        "roots": [
            {
                "root_label": "synthetic_pilot",
                "dense_candidate_count": 80,
                "requested_sample_size": 40,
                "sampled_count": 40,
                "opened_count": 40,
                "error_count": 0,
            },
            {
                "root_label": "synthetic_pilot_01",
                "dense_candidate_count": 90,
                "requested_sample_size": 40,
                "sampled_count": 40,
                "opened_count": 39,
                "error_count": 1,
            },
        ],
    }


def test_builds_safe_runtime_report():
    output = build_runtime_report(
        probe_payload(),
        elapsed_seconds=12.3456,
        output_byte_count=2048,
    )

    validate_historical_diary_output(output)

    assert output["runtime_report"]["elapsed_seconds"] == 12.346
    assert output["runtime_report"]["output_byte_count"] == 2048
    assert output["runtime_report"]["root_count"] == 2
    assert output["runtime_report"]["total_sampled_count"] == 80
    assert output["runtime_report"]["total_opened_count"] == 79
    assert output["runtime_report"]["total_error_count"] == 1


def test_cli_writes_safe_runtime_report(tmp_path, monkeypatch):
    probe_path = tmp_path / "probe.json"
    output_path = tmp_path / "runtime.json"
    probe_path.write_text(json.dumps(probe_payload()), encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "historical_diary_runtime_report.py",
            str(probe_path),
            "--elapsed-seconds",
            "9.5",
            "--output",
            str(output_path),
        ],
    )

    assert main() == 0

    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_historical_diary_output(output)
    assert output["classifier"]["output_class"] == "runtime_report"
