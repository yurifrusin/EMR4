"""LC4V4D5E1 deterministic development-exit tests."""

from __future__ import annotations

import json
import pathlib

import pytest

from app.services.bernie.lc4v4d5e1_development_exit import (
    D4_PATH,
    D5_PATH,
    D5R1_ACCEPTANCE_PATH,
    D5R1_PATH,
    EXPECTED_D4_HASH,
    EXPECTED_D5_HASH,
    EXPECTED_D5R1_HASH,
    run_d5e1_exit,
)


def test_valid_development_exit_requires_user_holdout_decision() -> None:
    report = run_d5e1_exit("test-source")
    assert report["decision"] == "development_exit_valid_holdout_decision_required"
    assert report["requires_user_decision"] is True
    assert report["certification_claimed"] is False
    assert report["recommendation"] == "authorize_genuinely_fresh_certification_holdout"
    assert len(report["gates"]) == 17
    assert all(report["gates"].values())


def test_exact_input_hashes_and_closed_taxonomy() -> None:
    report = run_d5e1_exit("test-source")
    assert report["input_report_hashes"] == {
        "d4": EXPECTED_D4_HASH,
        "d5": EXPECTED_D5_HASH,
        "d5r1": EXPECTED_D5R1_HASH,
    }
    assert report["development_taxonomy"] == {
        "legacy_equivalent": 37,
        "accepted_d4_versioned_change": 20,
        "expected_versioned_relation": 3,
        "remaining_blockers": 0,
    }


def test_report_is_deterministic() -> None:
    first = run_d5e1_exit("test-source")
    second = run_d5e1_exit("test-source")
    assert first == second


@pytest.mark.parametrize(
    ("source", "field"),
    [
        (D4_PATH, "total_cases"),
        (D5_PATH, "total_probes"),
        (D5R1_PATH, "total_probes"),
    ],
)
def test_tampered_report_fails_closed(
    tmp_path: pathlib.Path,
    source: pathlib.Path,
    field: str,
) -> None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload[field] = -1
    tampered = tmp_path / source.name
    tampered.write_text(json.dumps(payload), encoding="utf-8")
    paths = {
        "d4_path": D4_PATH,
        "d5_path": D5_PATH,
        "d5r1_path": D5R1_PATH,
    }
    if source == D4_PATH:
        paths["d4_path"] = tampered
    elif source == D5_PATH:
        paths["d5_path"] = tampered
    else:
        paths["d5r1_path"] = tampered
    report = run_d5e1_exit("tampered", **paths)
    assert report["decision"] == "reassessment_invalid"
    assert not all(report["gates"].values())


def test_missing_or_malformed_input_fails_closed(tmp_path: pathlib.Path) -> None:
    missing = tmp_path / "missing.json"
    malformed = tmp_path / "malformed.json"
    malformed.write_text("not-json", encoding="utf-8")
    assert run_d5e1_exit("missing", d4_path=missing)["decision"] == "reassessment_invalid"
    assert run_d5e1_exit("malformed", d5_path=malformed)["decision"] == "reassessment_invalid"


def test_acceptance_drift_fails_closed(tmp_path: pathlib.Path) -> None:
    altered = tmp_path / "acceptance.md"
    altered.write_text(
        D5R1_ACCEPTANCE_PATH.read_text(encoding="utf-8").replace(
            "exact_four_remediation_accepted", "changed",
        ),
        encoding="utf-8",
    )
    report = run_d5e1_exit("altered", acceptance_path=altered)
    assert report["decision"] == "reassessment_invalid"
    assert report["gates"]["d5r1_acceptance_exact"] is False


def test_binder_does_not_import_parser_or_fixture_authoring() -> None:
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "app" / "services" / "bernie" / "lc4v4d5e1_development_exit.py"
    )
    source = module_path.read_text(encoding="utf-8")
    assert "semantic_extraction" not in source
    assert "author_all_probes" not in source
    assert "dict_to_spec" not in source
