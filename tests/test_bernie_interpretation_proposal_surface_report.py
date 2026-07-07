import json
import subprocess

import pytest

from scripts.bernie_interpretation_proposal_surface_report import (
    REPORT_SCHEMA_VERSION,
    assert_proposal_surface_report_safety,
    build_proposal_surface_report,
)


def test_proposal_surface_report_is_safe_aggregate(tmp_path):
    clean = tmp_path / "clean.md"
    missing = tmp_path / "missing.md"
    unreadable = tmp_path / "unreadable.md"
    clean.write_text("Ordinary note.", encoding="utf-8")
    missing.write_text(
        "This provider integration proposal discusses live provider enablement.",
        encoding="utf-8",
    )
    unreadable.write_bytes(b"\xff")

    report = build_proposal_surface_report((tmp_path,))

    assert report == {
        "schema_version": REPORT_SCHEMA_VERSION,
        "source": "proposal_surface_aggregate",
        "scanned_markdown_count": 3,
        "trigger_phrase_hit_count": 1,
        "missing_readiness_count": 1,
        "unreadable_markdown_count": 1,
        "total_fail_closed_findings_count": 2,
        "readiness_command_name": (
            ".venv\\Scripts\\python.exe "
            "scripts\\bernie_interpretation_readiness_check.py"
        ),
        "provider_boundary_command_name": (
            ".venv\\Scripts\\python.exe "
            "scripts\\bernie_provider_boundary_readiness_report.py"
        ),
        "boundaries": {
            "provider_calls": "prohibited",
            "route_calls": "prohibited",
            "database_access": "prohibited",
            "raw_trove_access": "prohibited",
            "runtime_memory": "prohibited",
        },
        "omitted_fields": [
            "paths",
            "filenames",
            "decode_error_text",
            "trigger_phrase_text",
        ],
        "runtime_or_provider_wiring_ready": False,
        "provider_calls_performed": False,
        "database_access_performed": False,
        "historical_diary_material_access_performed": False,
    }
    assert_proposal_surface_report_safety(report)


@pytest.mark.parametrize(
    ("field", "unsafe_value"),
    [
        ("boundaries", {}),
        ("omitted_fields", []),
        ("runtime_or_provider_wiring_ready", True),
        ("provider_calls_performed", True),
        ("database_access_performed", True),
        ("historical_diary_material_access_performed", True),
    ],
)
def test_proposal_surface_report_rejects_unsafe_posture(
    tmp_path,
    field,
    unsafe_value,
):
    report = build_proposal_surface_report((tmp_path,))
    report[field] = unsafe_value

    with pytest.raises(AssertionError):
        assert_proposal_surface_report_safety(report)


def test_proposal_surface_report_rejects_path_or_text_fields(tmp_path):
    report = build_proposal_surface_report((tmp_path,))
    report["paths"] = ["docs/example.md"]

    with pytest.raises(AssertionError):
        assert_proposal_surface_report_safety(report)


def test_proposal_surface_report_rejects_negative_or_inconsistent_counts(tmp_path):
    report = build_proposal_surface_report((tmp_path,))
    report["missing_readiness_count"] = -1

    with pytest.raises(AssertionError):
        assert_proposal_surface_report_safety(report)

    report = build_proposal_surface_report((tmp_path,))
    report["total_fail_closed_findings_count"] += 1

    with pytest.raises(AssertionError):
        assert_proposal_surface_report_safety(report)


def test_proposal_surface_report_cli_outputs_json_without_paths(tmp_path):
    missing = tmp_path / "missing.md"
    missing.write_text(
        "This provider integration proposal discusses live provider enablement.",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            ".venv\\Scripts\\python.exe",
            "scripts\\bernie_interpretation_proposal_surface_report.py",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)

    assert report["missing_readiness_count"] == 1
    assert "missing.md" not in result.stdout
    assert_proposal_surface_report_safety(report)
