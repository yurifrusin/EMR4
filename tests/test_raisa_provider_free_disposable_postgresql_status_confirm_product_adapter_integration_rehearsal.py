from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_contract_is_closed_and_all_hostile_mutations_fail() -> None:
    contract = json.loads(rehearsal.CONTRACT_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(
        json.loads(rehearsal.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    ).validate(contract)
    rehearsal._validate_contract(contract, exact=True)  # noqa: SLF001
    assert rehearsal.hostile_mutations_rejected(contract) == 104
    assert [item["id"] for item in contract["scenarios"]] == [
        f"PGA-S{index:02d}" for index in range(1, 13)
    ]
    assert contract["tenant_contract"]["transaction_local"] is True
    assert len(contract["tenant_contract"]["forced_rls_tables"]) == 5


def test_frozen_read_only_sources_and_route_nonmounting_are_exact() -> None:
    contract = json.loads(rehearsal.CONTRACT_PATH.read_text(encoding="utf-8"))
    for binding in contract["source_bindings"]:
        assert _sha256(ROOT / binding["path"]) == binding["sha256"]
    router = (ROOT / "app/routers/appointments.py").read_text(encoding="utf-8")
    assert "appointment_status_product_adapter" not in router


def test_released_evidence_is_current_closed_and_complete() -> None:
    evidence = json.loads(rehearsal.EVIDENCE_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(
        json.loads(rehearsal.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    ).validate(evidence)
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["contract_sha256"] == _sha256(rehearsal.CONTRACT_PATH)
    assert evidence["hostile_mutations"] == {
        "attempted": 104,
        "rejected": 104,
        "minimum_required": 100,
    }
    assert len(evidence["scenarios"]) == 12
    assert {item["status"] for item in evidence["scenarios"]} == {"passed"}
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    assert evidence["environment"]["provider_calls"] == 0
    assert evidence["environment"]["product_rows"] == 0
    assert evidence["catalogue"]["forced_rls_tables"] == 5
    assert evidence["catalogue"]["application_role_restricted"] is True
    for relative, expected in evidence["implementation_hashes"].items():
        assert _sha256(ROOT / relative) == expected


def test_released_evidence_retains_no_forbidden_values() -> None:
    serialized = rehearsal.EVIDENCE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in (
        "postgresql+",
        "status-adapter-authored-synthetic-only",
        "status-confirm-behavior-authored-synthetic-only",
        "authorization:",
        "bearer ",
        "select ",
        "insert ",
        "update ",
        "delete ",
        "patient_name",
    ):
        assert forbidden not in serialized
