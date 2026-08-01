"""Regression contract for the bounded PR 69 security/CI repair."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs" / "security" / "security-finding-register.json"
SCHEMA = ROOT / "docs" / "security" / "security-finding-register.schema.json"
TRIAGE = (
    ROOT / "docs" / "security" / "pr69-codeql-alerts-500-507-triage-2026-08-01.md"
)
HOST_PROOF = (
    ROOT / "scripts" / "reception_one_bureau_post_admission_runtime_hardening.py"
)
PARSER = ROOT / "app" / "services" / "bernie" / "semantic_extraction.py"
NATIVE_EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "pr69-security-ci-repair"
    / "native-alert-reconciliation-evidence.json"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_seven_pr69_security_alerts_are_registered_exactly() -> None:
    schema = _json(SCHEMA)
    register = _json(REGISTER)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(register)

    rows = {
        row["native_id"]: row
        for row in register["native_findings"]
        if row["source"] == "codeql" and 500 <= row["native_id"] <= 507
    }
    assert register["register_revision"] == 3
    assert set(rows) == {500, 501, 503, 504, 505, 506, 507}
    assert {native_id: rows[native_id]["finding_id"] for native_id in rows} == {
        500: "SF-0013",
        501: "SF-0014",
        503: "SF-0015",
        504: "SF-0016",
        505: "SF-0017",
        506: "SF-0018",
        507: "SF-0019",
    }
    assert all(row["owner"] == "@yurifrusin" for row in rows.values())
    assert {rows[native_id]["observed_native_state"] for native_id in (500, 501)} == {
        "dismissed"
    }
    assert {rows[native_id]["observed_native_state"] for native_id in range(503, 508)} == {
        "fixed"
    }
    assert {rows[native_id]["desired_native_state"] for native_id in (500, 501)} == {
        "dismissed"
    }
    assert {rows[native_id]["desired_native_state"] for native_id in range(503, 508)} == {
        "fixed"
    }
    assert {rows[native_id]["native_disposition_reason"] for native_id in (500, 501)} == {
        "tolerable_risk"
    }
    assert {rows[native_id]["native_disposition_reason"] for native_id in range(503, 508)} == {
        "fixed"
    }


def test_triage_inventory_names_every_alert_and_preserves_closed_boundaries() -> None:
    triage = " ".join(TRIAGE.read_text(encoding="utf-8").split())
    for native_id in (500, 501, 503, 504, 505, 506, 507):
        assert f"| {native_id} |" in triage
    for boundary in (
        "no provider call",
        "credential read",
        "product-data access",
        "deployment",
        "movement of `master`",
    ):
        assert boundary in triage


def test_host_and_parser_repairs_remove_flagged_constructs() -> None:
    host_source = HOST_PROOF.read_text(encoding="utf-8")
    parser_source = PARSER.read_text(encoding="utf-8")

    assert 'if item["hostname"] in PROVIDER_HOST_ALLOWLIST' in host_source
    assert '"aiplatform.googleapis.com" in item["hostname"]' not in host_source
    assert '"generativelanguage.googleapis.com" in item["hostname"]' not in host_source
    assert '"api.openai.com" in item["hostname"]' not in host_source
    assert 'or_later_text = " ".join(text.split())' in parser_source
    assert 'after_target = " ".join(all_text[target_m.end():].split())' in parser_source


def test_final_native_readback_matches_register_and_records_correction() -> None:
    register = _json(REGISTER)
    evidence = _json(NATIVE_EVIDENCE)
    rows = {
        row["native_id"]: row
        for row in register["native_findings"]
        if row["source"] == "codeql" and row["native_id"] in {500, 501, 503, 504, 505, 506, 507}
    }
    final = {row["number"]: row for row in evidence["final_alerts"]}

    assert evidence["result"] == "pr69_security_ci_repair_pass"
    assert evidence["final_query"]["open_security_severity_alert_count"] == 0
    assert evidence["github_checks"]["all_required_checks_successful"] is True
    assert evidence["manual_disposition_audit"]["comment_correction"] == {
        "required": True,
        "detected_by_immediate_readback": True,
        "interim_stored_comment": "System.Collections.Hashtable.comment",
        "cause": "PowerShell property interpolation passed a literal hashtable representation to gh api.",
        "repair": "Each alert was reopened and immediately re-dismissed with the already-durable exact rationale.",
        "successful_native_mutation_requests": 6,
        "failed_comment_update_requests_with_no_state_change": 1,
        "final_readback_exact": True,
    }
    for native_id, row in rows.items():
        assert final[native_id]["state"] == row["observed_native_state"]
    for native_id in (500, 501):
        assert final[native_id]["reason"] == "won't fix"
        assert final[native_id]["dismissed_at"] == rows[native_id]["native_disposition_at"]
