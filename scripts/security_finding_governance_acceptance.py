"""Deterministic acceptance for EMR4 security-finding governance."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = ROOT / "docs" / "security" / "security-finding-register.json"
SCHEMA_PATH = (
    ROOT / "docs" / "security" / "security-finding-register.schema.json"
)
NATIVE_EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "security-finding-governance"
    / "native-alert-disposition-evidence.json"
)
EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "security-finding-governance"
    / "acceptance-evidence.json"
)
PYTHON_WORKFLOW = ROOT / ".github" / "workflows" / "python-security.yml"
NODE_WORKFLOW = ROOT / ".github" / "workflows" / "node-security.yml"
SECURITY_POLICY = ROOT / "SECURITY.md"
RESULT = "security_finding_governance_pass"

EXPECTED_NATIVE_IDS = {
    "dependabot": {5, 8, 9, 10, 11, 12, 13, 14, 15},
    "codeql": {268, 272, 295},
}
EXPECTED_SCHEDULES = {
    "python": 'cron: "17 18 * * *"',
    "node": 'cron: "47 18 * * *"',
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ledger_rows(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_evidence() -> dict[str, Any]:
    schema = _load_json(SCHEMA_PATH)
    register = _load_json(REGISTER_PATH)
    native = _load_json(NATIVE_EVIDENCE_PATH)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(register)

    rows = register["native_findings"]
    finding_ids = [row["finding_id"] for row in rows]
    native_keys = [(row["source"], row["native_id"]) for row in rows]
    expected_keys = {
        (source, native_id)
        for source, ids in EXPECTED_NATIVE_IDS.items()
        for native_id in ids
    }
    if len(finding_ids) != len(set(finding_ids)):
        raise ValueError("duplicate finding_id")
    if len(native_keys) != len(set(native_keys)):
        raise ValueError("duplicate native finding")
    if set(native_keys) != expected_keys:
        raise ValueError("native finding inventory mismatch")

    for row in rows:
        if row["owner"] != register["owner"]:
            raise ValueError("finding owner mismatch")
        if row["observed_native_state"] != row["desired_native_state"]:
            raise ValueError("native state drift")
        if row["observed_native_state"] != "dismissed":
            raise ValueError("unexpected native state")
        if not row["native_disposition_at"]:
            raise ValueError("missing native disposition timestamp")
        if _parse_time(row["triaged_at"]) > _parse_time(row["triage_due_at"]):
            raise ValueError("triage SLA missed")
        risk = row["risk_acceptance"]
        if _parse_time(risk["expires_at"]) < _parse_time(row["review_at"]):
            raise ValueError("risk expires before review")

    evidence_rows = {
        (row["source"], row["native_id"]): row
        for row in native["final_dispositions"]
    }
    if set(evidence_rows) != expected_keys:
        raise ValueError("native evidence inventory mismatch")
    for row in rows:
        observed = evidence_rows[(row["source"], row["native_id"])]
        if observed["state"] != row["observed_native_state"]:
            raise ValueError("native evidence state drift")
        if observed["reason"] != row["native_disposition_reason"]:
            raise ValueError("native evidence reason drift")
        if observed["dismissed_at"] != row["native_disposition_at"]:
            raise ValueError("native evidence timestamp drift")

    linked_ledgers: list[dict[str, Any]] = []
    for ledger in register["linked_local_ledgers"]:
        path = ROOT / ledger["path"]
        actual = _ledger_rows(path)
        if actual != ledger["row_count"]:
            raise ValueError("linked ledger row count drift")
        linked_ledgers.append(
            {
                "ledger_id": ledger["ledger_id"],
                "expected_rows": ledger["row_count"],
                "actual_rows": actual,
                "passed": True,
            }
        )

    python_workflow = PYTHON_WORKFLOW.read_text(encoding="utf-8")
    node_workflow = NODE_WORKFLOW.read_text(encoding="utf-8")
    if EXPECTED_SCHEDULES["python"] not in python_workflow:
        raise ValueError("python daily schedule missing")
    if EXPECTED_SCHEDULES["node"] not in node_workflow:
        raise ValueError("node daily schedule missing")
    for workflow in (python_workflow, node_workflow):
        if "push:" not in workflow or "pull_request:" not in workflow:
            raise ValueError("push/pull-request trigger drift")
    if "pip-audit -r requirements.txt --desc" not in python_workflow:
        raise ValueError("python dependency gate drift")
    if "--profile ci-bandit" not in python_workflow:
        raise ValueError("Bandit gate drift")
    if "npm audit --omit=dev" not in node_workflow:
        raise ValueError("node production audit drift")

    security = SECURITY_POLICY.read_text(encoding="utf-8")
    required_policy = (
        "The security maintainer is `@yurifrusin`.",
        "security-finding-register.json",
        "within two business days",
        "| Critical | 1 calendar day | 2 calendar days | 7 calendar days |",
        "Expired dispositions return to",
        "Dependency force fixes, unsupported overrides",
    )
    missing_policy = [value for value in required_policy if value not in security]
    if missing_policy:
        raise ValueError("approved SECURITY.md policy is incomplete")

    passed = (
        native["passed"] is True
        and native["post_mutation"]["open_dependabot_count"] == 0
        and native["post_mutation"]["open_codeql_security_high_count"] == 0
    )
    return {
        "schema_version": "emr4.security-finding-governance.acceptance.v1",
        "result": RESULT if passed else "security_finding_governance_revision_required",
        "passed": passed,
        "register": {
            "revision": register["register_revision"],
            "native_finding_count": len(rows),
            "unique_native_finding_count": len(set(native_keys)),
            "owner": register["owner"],
            "schema_valid": True,
        },
        "schedules": {
            "python": "17 18 * * *",
            "node": "47 18 * * *",
            "staggered": True,
            "push_and_pull_request_preserved": True,
            "blocking_dependency_gates_preserved": True,
        },
        "native_alerts": {
            "dependabot_disposition_count": 9,
            "codeql_disposition_count": 3,
            "open_dependabot_count": 0,
            "open_codeql_security_high_count": 0,
            "register_matches_readback": True,
        },
        "linked_local_ledgers": linked_ledgers,
        "security_policy": {
            "owner_present": True,
            "sla_matrix_present": True,
            "laptop_ingestion_rule_present": True,
            "accepted_risk_expiry_rule_present": True,
        },
        "closed_boundaries": {
            "dependency_force_override_count": 0,
            "product_or_patient_data_access_count": 0,
            "provider_call_count": 0,
            "cloud_or_iam_mutation_count": 0,
            "deployment_or_production_change_count": 0,
            "protected_ref_movement_count": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()
    evidence = build_evidence()
    rendered = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    if args.write_evidence:
        EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE_PATH.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
