from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / (
    "raisa-provider-free-disposable-postgresql-delete-confirm-"
    "behavior-transaction-rehearsal-plan.md"
)
THREAT = ROOT / "docs" / "security" / (
    "raisa-provider-free-disposable-postgresql-delete-confirm-"
    "behavior-transaction-rehearsal-threat-model-delta.md"
)
CONTRACT = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "delete-confirm-behavior-transaction-rehearsal/rehearsal-contract.json"
)
CONTRACT_SCHEMA = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "delete-confirm-behavior-transaction-rehearsal/rehearsal-contract.schema.json"
)
EVIDENCE_SCHEMA = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "delete-confirm-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-evidence.schema.json"
)

PLAN_HASH = "4fde7121a548f7f574e56506e0e3a4f3303b8cc0b18a7fd80948b84b9c99498c"
THREAT_HASH = "30830f56eee984b4e0f1c04791dc2a624d3015daaaafeba941f1485cde36620f"
SOURCE_HEAD = "2a5042f80941e2bd191999c430ff2517ba7e8cb2"

OWNED_PATHS = (
    "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal.py",
    "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal.py",
    "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal_plan.py",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal/rehearsal-contract.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _plan_source_bindings(text: str) -> dict[str, str]:
    bindings: dict[str, str] = {}
    pattern = re.compile(r"\|\s*`([0-9a-f]{64})`\s*\|\s*`([^`]+)`\s*\|")
    for match in pattern.finditer(text):
        bindings[match.group(2)] = match.group(1)
    return bindings


def test_plan_and_threat_delta_are_frozen_and_bound() -> None:
    assert _sha256(PLAN) == PLAN_HASH
    assert _sha256(THREAT) == THREAT_HASH


def test_contract_binds_plan_source_hashes_and_exact_head() -> None:
    plan_text = PLAN.read_text(encoding="utf-8")
    plan_bindings = _plan_source_bindings(plan_text)
    assert len(plan_bindings) == 16
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["source_head"] == SOURCE_HEAD
    assert contract["source_hash_mode"] == "utf8_text_crlf_to_lf_reject_bare_cr"
    contract_bindings = {
        item["path"]: item["sha256"] for item in contract["source_bindings"]
    }
    assert contract_bindings == plan_bindings
    assert len(contract_bindings) == 16


def test_plan_freezes_owned_paths_risk_tier_and_api_spine() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for path in OWNED_PATHS:
        assert path in text
    assert "its whole-document JSON schema" in text
    assert "one minimized behavior/transaction evidence schema" in text
    assert "frozen_for_tier_2_provider_free_disposable_postgresql_execution" in text
    assert "Risk classification: Tier 2" in text
    assert "database_runtime" in text
    assert "authority_or_security_contract" in text
    assert "migration_execution" in text
    assert "executable_tool" in text
    assert "private evidence beneath the dedicated REST/OpenAPI command" in text
    assert "confirmAppointmentDeleteProposal" in text
    assert "GraphQL remains read-only" in text
    assert "non-authoritative acceleration hints" in text


def test_plan_freezes_authority_and_transaction_case_groups() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for index in range(1, 10):
        assert f"`AUTH-S{index:02d}`" in text
    for index in range(1, 12):
        assert f"`TX-S{index:02d}`" in text
    assert "Frozen authority/trigger case groups" in text
    assert "Frozen transaction case groups" in text
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    auth_ids = [item["id"] for item in contract["authority_groups"]]
    tx_ids = [item["id"] for item in contract["transaction_groups"]]
    assert auth_ids == [f"AUTH-S{index:02d}" for index in range(1, 10)]
    assert tx_ids == [f"TX-S{index:02d}" for index in range(1, 12)]
    assert contract["scenario_categories"] == {"authority": 9, "transaction": 11}


def test_plan_freezes_containment_and_transaction_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "docker.exe" in text
    assert "postgres:16-bookworm" in text
    assert "--pull=never" in text
    assert "--internal" in text
    assert "tmpfs" in text
    assert "one CPU" in text
    assert "512 MiB" in text
    assert "128 processes" in text
    assert "shell=False" in text
    assert "/dev/tcp/127.0.0.1/5432" in text
    assert "delete_confirm_locked_transaction" in text
    assert "READ COMMITTED" in text
    assert "2000 ms" in text
    assert "w2x3y4z5a6b7:x3y4z5a6b7c8" in text
    assert "ON_ERROR_STOP=1" in text
    assert "--single-transaction" in text


def test_plan_freezes_cleanup_and_forbidden_surfaces() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Cleanup runs in `finally`" in text
    assert "exact ID/name/image/labels/network/tmpfs/" in text
    assert "Ownership ambiguity refuses destructive cleanup" in text
    assert "product/historical-diary/protected data" in text
    assert "No existing or product database" in text
    assert "concurrency, restart, unknown commit" in text
    assert "provider/ADC/credential/IAM/browser" in text
    assert "protected-ref movement" in text
    assert "explicit paths only" in text
    assert "route-convergence admission review" in text


def test_contract_schemas_are_closed_whole_documents() -> None:
    contract_schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
    evidence_schema = json.loads(EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    assert contract_schema["additionalProperties"] is False
    assert evidence_schema["additionalProperties"] is False
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert sorted(contract["evidence_allowlist"]) == sorted(
        [
            "source_digests",
            "environment_digests",
            "containment_booleans",
            "case_ids",
            "decision_error_labels",
            "counts",
            "state_versions",
            "statement_class_tokens",
            "cleanup_results",
        ]
    )
    assert contract["next_candidate"] == (
        "provider_free_read_only_delete_confirm_route_convergence_admission_review"
    )


def test_threat_delta_preserves_fail_closed_controls() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "Timestamp: 2026-08-16T11:52:20+10:00 (Australia/Brisbane)" in text
    assert "x3y4z5a6b7c8" in text
    assert "--internal" in text
    assert "--pull=never" in text
    assert "Reverify exact captured IDs" in text
    assert "Both complete current-authority checks" in text
    assert "value-free statement classes" in text
    assert "2000 ms" in text
    assert "Evidence is schema-closed" in text
    assert "exactly one final independent veto" in text
    assert "No existing/product database" in text
    assert "patient/clinical/product/protected data" in text
