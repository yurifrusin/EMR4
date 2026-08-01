"""Acceptance contract for durable EMR4 security-finding governance."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from scripts.security_finding_governance_acceptance import build_evidence


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs" / "security" / "security-finding-register.json"
SCHEMA = ROOT / "docs" / "security" / "security-finding-register.schema.json"
NATIVE_EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "security-finding-governance"
    / "native-alert-disposition-evidence.json"
)
RECORDED_EVIDENCE = NATIVE_EVIDENCE.with_name("acceptance-evidence.json")
PREACCEPTANCE_RECEIPT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "security-finding-governance-preacceptance-receipt.json"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_register_schema_inventory_owners_and_slas() -> None:
    schema = _load(SCHEMA)
    register = _load(REGISTER)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(register)
    all_rows = register["native_findings"]
    assert len({row["finding_id"] for row in all_rows}) == len(all_rows)
    assert len({(row["source"], row["native_id"]) for row in all_rows}) == len(all_rows)
    baseline_keys = {
        ("dependabot", native_id) for native_id in {5, 8, 9, 10, 11, 12, 13, 14, 15}
    } | {("codeql", native_id) for native_id in {268, 272, 295}}
    rows = [
        row
        for row in all_rows
        if (row["source"], row["native_id"]) in baseline_keys
    ]
    assert len(rows) == 12
    assert {row["native_id"] for row in rows if row["source"] == "dependabot"} == {
        5,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
    }
    assert {row["native_id"] for row in rows if row["source"] == "codeql"} == {
        268,
        272,
        295,
    }
    for row in rows:
        assert row["owner"] == "@yurifrusin"
        assert row["triage_verdict"] == "not_actionable"
        assert _time(row["triaged_at"]) <= _time(row["triage_due_at"])
        assert _time(row["review_at"]) <= _time(row["risk_acceptance"]["expires_at"])

    new_alert = next(row for row in all_rows if row["finding_id"] == "SF-0020")
    assert (new_alert["source"], new_alert["native_id"]) == ("dependabot", 17)
    assert new_alert["severity"] == "high"
    assert new_alert["owner"] == "@yurifrusin"
    assert new_alert["triage_verdict"] == "not_actionable"
    assert new_alert["status"] == "needs_review"
    assert new_alert["observed_native_state"] == "open"
    assert new_alert["desired_native_state"] == "open"
    assert new_alert["native_disposition_at"] is None
    assert new_alert["risk_acceptance"] is None
    assert _time(new_alert["triaged_at"]) <= _time(new_alert["triage_due_at"])

    pr70_alert = next(row for row in all_rows if row["finding_id"] == "SF-0021")
    assert (pr70_alert["source"], pr70_alert["native_id"]) == ("codeql", 544)
    assert pr70_alert["severity"] == "high"
    assert pr70_alert["triage_verdict"] == "confirmed"
    assert pr70_alert["status"] == "open"
    assert pr70_alert["observed_native_state"] == "open"
    assert pr70_alert["desired_native_state"] == "fixed"
    assert pr70_alert["native_disposition_at"] is None
    assert pr70_alert["risk_acceptance"] is None


def test_pr70_codeql_candidates_are_instance_preserving_and_pending_readback() -> None:
    ledger_path = (
        ROOT
        / "docs"
        / "security"
        / "pr70-codeql-alerts-543-544-validation-ledger.jsonl"
    )
    rows = [json.loads(line) for line in ledger_path.read_text().splitlines()]
    assert [row["candidate_id"] for row in rows] == ["codeql-543", "codeql-544"]
    assert len({row["instance_key"] for row in rows}) == 2
    assert {row["disposition"] for row in rows} == {
        "patched_pending_codeql_readback"
    }
    assert {row["survives"] for row in rows} == {
        "yes_quality_only",
        "yes_confirmed_narrow_test_boundary",
    }


def test_post_snapshot_alert_17_triage_and_readback_remain_open_and_zero_mutation() -> None:
    triage_path = (
        ROOT / "docs" / "security" / "dependabot-alert-17-triage-2026-08-01.json"
    )
    readback_path = (
        ROOT
        / "orchestration"
        / "continuity"
        / "shared-application-auth-office-cookie-compatibility"
        / "dependabot-alert-17-readback.json"
    )
    triage = _load(triage_path)
    readback = _load(readback_path)
    finding = triage["findings"][0]
    assert triage["schema_version"] == "triage-finding/v0"
    assert finding["input_id"] == "dependabot-alert-17"
    assert finding["verdict"] == "not_actionable"
    assert finding["confidence"] == "high"
    assert finding["boundary_assessment"]["boundary_crossed"] is False
    assert finding["exploitability_stack_rank"]["rank"] is None
    assert readback["alert"] == {
        "number": 17,
        "state": "open",
        "package": "brace-expansion",
        "manifest_path": "EMR4 Sidebar/package-lock.json",
        "dependency_scope": "development",
        "relationship": "transitive",
        "severity": "high",
        "ghsa_id": "GHSA-3jxr-9vmj-r5cp",
        "cve_id": "CVE-2026-13149",
        "vulnerable_version_range": ">= 2.0.0, < 2.1.2",
        "first_patched_version": "2.1.2",
        "created_at": "2026-08-01T06:05:44Z",
    }
    assert readback["repository_tracking"]["status"] == "needs_review"
    assert readback["repository_tracking"]["desired_native_state"] == "open"
    assert set(readback["external_side_effects"].values()) == {0}


def test_native_alert_readback_matches_register_exactly() -> None:
    register = _load(REGISTER)
    native = _load(NATIVE_EVIDENCE)
    evidence = {
        (row["source"], row["native_id"]): row
        for row in native["final_dispositions"]
    }
    baseline_keys = {
        ("dependabot", native_id) for native_id in {5, 8, 9, 10, 11, 12, 13, 14, 15}
    } | {("codeql", native_id) for native_id in {268, 272, 295}}
    for row in register["native_findings"]:
        if (row["source"], row["native_id"]) not in baseline_keys:
            continue
        observed = evidence[(row["source"], row["native_id"])]
        assert row["observed_native_state"] == "dismissed"
        assert row["desired_native_state"] == "dismissed"
        assert observed["state"] == row["observed_native_state"]
        assert observed["reason"] == row["native_disposition_reason"]
        assert observed["dismissed_at"] == row["native_disposition_at"]
    assert native["post_mutation"] == {
        "open_dependabot_count": 0,
        "open_codeql_security_high_count": 0,
        "register_matches_final_state": True,
    }
    assert native["external_side_effects"]["native_alert_dispositions"] == 12
    assert native["external_side_effects"]["dependency_changes"] == 0


def test_linked_local_ledgers_are_instance_preserving() -> None:
    register = _load(REGISTER)
    ledgers = {row["ledger_id"]: row for row in register["linked_local_ledgers"]}
    assert ledgers["bandit-candidates-2026-08-01"]["row_count"] == 14
    assert ledgers["codeql-high-candidates-2026-07-17"]["row_count"] == 10
    for ledger in ledgers.values():
        lines = [
            line
            for line in (ROOT / ledger["path"]).read_text(encoding="utf-8").splitlines()
            if line
        ]
        assert len(lines) == ledger["row_count"]
        for line in lines:
            json.loads(line)


def test_python_and_node_security_jobs_are_staggered_daily_and_still_block() -> None:
    python = (ROOT / ".github/workflows/python-security.yml").read_text(
        encoding="utf-8"
    )
    node = (ROOT / ".github/workflows/node-security.yml").read_text(
        encoding="utf-8"
    )
    assert 'cron: "17 18 * * *"' in python
    assert 'cron: "47 18 * * *"' in node
    assert "push:" in python and "pull_request:" in python
    assert "push:" in node and "pull_request:" in node
    assert "pip-audit -r requirements.txt --desc" in python
    assert "python scripts/verify_repository.py --profile ci-bandit" in python
    assert "npm audit --omit=dev" in node
    assert "npm audit || true" in node


def test_security_policy_contains_approved_owner_sla_and_ingestion_contract() -> None:
    policy = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    for required in (
        "The security maintainer is `@yurifrusin`.",
        "security-finding-register.json",
        "within two business days",
        "| Critical | 1 calendar day | 2 calendar days | 7 calendar days |",
        "Expired dispositions return to",
        "Dependency force fixes, unsupported overrides",
    ):
        assert required in policy


def test_dependabot_triage_preserves_upstream_defects_and_product_boundary() -> None:
    triage = (
        ROOT
        / "docs"
        / "security"
        / "dependabot-alerts-8-15-triage-2026-08-01.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(triage.split())
    assert "genuine upstream defects" in normalized
    assert "None survives as an actionable EMR4 security finding" in normalized
    assert "Force audit fixes and dependency overrides remain prohibited" in normalized
    for alert in range(8, 16):
        assert f"| {alert} |" in triage


def test_deterministic_acceptance_matches_recorded_evidence() -> None:
    assert build_evidence() == _load(RECORDED_EVIDENCE)


def test_preacceptance_receipt_and_continuity_closeout() -> None:
    receipt = _load(PREACCEPTANCE_RECEIPT)
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == {
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    }
    assert receipt["worker_dispatch_permitted"] is False

    graph = _load(GRAPH)
    compass = _load(COMPASS)
    assert graph["graph_revision"] >= 186
    node = next(
        item for item in graph["nodes"] if item["id"] == "security-finding-governance"
    )
    assert node["status"] == "accepted"
    assert compass["map_revision"] >= 167
    assert compass["source_graph_revision"] >= 186
    assert "security-finding-governance" in {
        item["node_id"] for item in compass["journey"]
    }
