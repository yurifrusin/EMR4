import json
import subprocess
import sys
from pathlib import Path

from scripts.practitioner_directory_consumer_contract_report import (
    assert_consumer_contract_report,
    build_report,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_practitioner_directory"
    / "consumer_contract_report.json"
)
DOC = ROOT / "docs" / "api-spine" / "practitioner-directory-consumer-contract-check.md"


def test_consumer_contract_report_matches_fastapi_openapi_snapshot():
    expected = json.loads(FIXTURE.read_text(encoding="utf-8"))
    actual = build_report()

    assert actual == expected


def test_consumer_contract_report_assertion_rejects_sensitive_field_drift():
    report = build_report()
    report["response"]["fields"].append("provider_number")
    report["response"]["sensitive_fields_present"].append("provider_number")

    try:
        assert_consumer_contract_report(report)
    except AssertionError:
        return
    raise AssertionError("sensitive field drift was not rejected")


def test_consumer_contract_report_assertion_rejects_detail_route_drift():
    report = build_report()
    report["detail_route_present"] = True

    try:
        assert_consumer_contract_report(report)
    except AssertionError:
        return
    raise AssertionError("detail route drift was not rejected")


def test_consumer_contract_report_cli_emits_fixture_snapshot():
    result = subprocess.run(
        [sys.executable, "scripts/practitioner_directory_consumer_contract_report.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert json.loads(result.stdout) == json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_consumer_contract_markdown_records_boundary():
    folded = " ".join(DOC.read_text(encoding="utf-8").split())

    assert "Decision: `consumer_contract_checked_readiness_blocked`" in folded
    assert "`GET /api/v1/practice/practitioners`" in folded
    assert "`PractitionerOut` fields: `id`, `displayName`, `roleLabel`, `active`, `defaultLocation`" in folded
    assert "Sensitive practitioner fields are absent" in folded
    assert "No practitioner detail route is present" in folded
    assert "does not approve GraphQL delivery" in folded
