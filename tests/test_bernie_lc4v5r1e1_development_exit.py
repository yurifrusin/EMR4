"""LC4V5R1E1 deterministic development-exit tests."""

from __future__ import annotations

import json
import pathlib

import pytest

from app.services.bernie.lc4v5r1e1_development_exit import (
    EXPECTED_R1_FILE_HASH,
    EXPECTED_R1_PROBE_HASH,
    EXPECTED_V5_FILE_HASH,
    R1_ACCEPTANCE_PATH,
    R1_REPORT_PATH,
    V5_ACCEPTANCE_PATH,
    V5_REPORT_PATH,
    generate_report_json,
    generate_report_markdown,
    run_development_exit,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
JSON_REPORT = ROOT / "docs" / "bernie-lc4v5r1e1-development-exit.json"
MARKDOWN_REPORT = ROOT / "docs" / "bernie-lc4v5r1e1-development-exit.md"
SOURCE_COMMIT = "af8dc8dfb2750b291c2f750dc9c4598b3dc4f228"
EXPECTED_REPORT_HASH = (
    "sha256:488e3478eab1c9451f5d78c33c16a2d06be1fc89117f8da8fc6a24fdc2f001ed"
)


def test_valid_development_exit_requires_user_holdout_decision() -> None:
    report = run_development_exit("test-source")
    assert report["decision"] == "development_exit_valid_holdout_decision_required"
    assert report["requires_user_decision"] is True
    assert report["certification_claimed"] is False
    assert report["recommendation"] == (
        "authorize_genuinely_fresh_certification_holdout_v6"
    )
    assert len(report["gates"]) == 13
    assert all(report["gates"].values())


def test_exact_input_hashes_and_development_result() -> None:
    report = run_development_exit("test-source")
    assert report["input_file_hashes"]["lc4v5_aggregate"] == EXPECTED_V5_FILE_HASH
    assert report["input_file_hashes"]["lc4v5r1_development"] == (
        EXPECTED_R1_FILE_HASH
    )
    assert report["development_result"] == {
        "families": 3,
        "probes": 18,
        "baseline_complete": 4,
        "repaired_complete": 18,
        "baseline_safe": 14,
        "repaired_safe": 18,
        "repeat_variance": 0,
    }
    assert EXPECTED_R1_PROBE_HASH.startswith("sha256:e4488591")


def test_report_is_deterministic() -> None:
    first = run_development_exit("test-source")
    second = run_development_exit("test-source")
    assert first == second


def test_committed_report_matches_source() -> None:
    report = run_development_exit(SOURCE_COMMIT)
    assert report["report_hash"] == EXPECTED_REPORT_HASH
    assert JSON_REPORT.read_text(encoding="utf-8") == generate_report_json(report)
    assert MARKDOWN_REPORT.read_text(encoding="utf-8") == generate_report_markdown(
        report
    )


@pytest.mark.parametrize(
    ("source", "argument"),
    [
        (V5_REPORT_PATH, "v5_report_path"),
        (V5_ACCEPTANCE_PATH, "v5_acceptance_path"),
        (R1_REPORT_PATH, "r1_report_path"),
        (R1_ACCEPTANCE_PATH, "r1_acceptance_path"),
    ],
)
def test_tampered_input_fails_closed(
    tmp_path: pathlib.Path,
    source: pathlib.Path,
    argument: str,
) -> None:
    tampered = tmp_path / source.name
    tampered.write_bytes(source.read_bytes() + b"\n")
    report = run_development_exit("tampered", **{argument: tampered})
    assert report["decision"] == "reassessment_invalid"
    assert not all(report["gates"].values())


def test_missing_or_malformed_report_fails_closed(tmp_path: pathlib.Path) -> None:
    missing = tmp_path / "missing.json"
    malformed = tmp_path / "malformed.json"
    malformed.write_text("not-json", encoding="utf-8")
    assert run_development_exit(
        "missing", v5_report_path=missing
    )["decision"] == "reassessment_invalid"
    assert run_development_exit(
        "malformed", r1_report_path=malformed
    )["decision"] == "reassessment_invalid"


def test_semantically_altered_report_fails_closed(tmp_path: pathlib.Path) -> None:
    payload = json.loads(R1_REPORT_PATH.read_text(encoding="utf-8"))
    payload["repaired"]["safe"] = 17
    altered = tmp_path / R1_REPORT_PATH.name
    altered.write_text(json.dumps(payload), encoding="utf-8")
    report = run_development_exit("altered", r1_report_path=altered)
    assert report["decision"] == "reassessment_invalid"
    assert report["gates"]["r1_repaired_exact"] is False


def test_binder_does_not_import_parser_or_fixture_authoring() -> None:
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "app"
        / "services"
        / "bernie"
        / "lc4v5r1e1_development_exit.py"
    )
    source = module_path.read_text(encoding="utf-8")
    assert "semantic_extraction" not in source
    assert "author_all" not in source
    assert "fixture" not in "\n".join(
        line for line in source.splitlines() if line.startswith("from ")
    )
