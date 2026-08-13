from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import validate


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-threat-model-delta.md"
ADAPTER = ROOT / "app/services/appointment_status_product_adapter.py"
ROUTER = ROOT / "app/routers/appointments.py"
SCRIPT = ROOT / "scripts/raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal.py"
EVIDENCE_DIR = ROOT / "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal"
CONTRACT = EVIDENCE_DIR / "product-adapter-rehearsal-contract.json"
SCHEMA = EVIDENCE_DIR / "product-adapter-rehearsal-evidence.schema.json"
EVIDENCE = EVIDENCE_DIR / "product-adapter-rehearsal-evidence.json"
RECEIPT = ROOT / "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-postcompaction-receipt.json"
EXPECTED_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_plan_and_threat_delta_have_timestamped_fail_closed_boundaries() -> None:
    for path in (PLAN, THREAT):
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-13" in text
        assert "Timestamp: 2026-08-13T" in text
        assert "+10:00 (Australia/Brisbane)" in text
    plan = PLAN.read_text(encoding="utf-8")
    for phrase in (
        "Revision: 2",
        "proposal-time version binding",
        "response-loss replay",
        "At least 80 hostile contract mutations",
        "No route edit/mount/call",
        "product/patient data",
        "protected-ref movement",
    ):
        assert phrase in plan


def test_frozen_inputs_and_router_nonmounting_are_exact() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert len(contract["frozen_inputs"]) == 13
    assert {
        relative: _sha256(ROOT / relative)
        for relative in contract["frozen_inputs"]
    } == contract["frozen_inputs"]
    router_text = ROUTER.read_text(encoding="utf-8")
    assert "appointment_status_product_adapter" not in router_text
    assert _sha256(ROUTER) == contract["frozen_inputs"]["app/routers/appointments.py"]


def test_generated_evidence_is_schema_valid_current_and_side_effect_free() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    validate(instance=evidence, schema=schema)
    assert evidence["contract_sha256"] == _sha256(CONTRACT)
    assert evidence["input_hashes"] == contract["frozen_inputs"]
    assert evidence["hostile_mutations"] == {
        "attempted": 84,
        "minimum_required": 80,
        "rejected": 84,
    }
    assert all(evidence["scenario_results"].values())
    assert set(evidence["side_effects"].values()) == {0}
    for relative, expected in evidence["implementation_hashes"].items():
        assert _sha256(ROOT / relative) == expected


def test_rehearsal_check_is_deterministic() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal_pass" in completed.stdout


def test_owned_adapter_and_rehearsal_contain_no_forbidden_runtime_imports() -> None:
    combined = ADAPTER.read_text(encoding="utf-8") + SCRIPT.read_text(encoding="utf-8")
    for forbidden in (
        "SessionLocal",
        "create_engine",
        "requests.",
        "httpx.",
        "socket.",
        "subprocess.",
        "google.auth",
        "google.cloud",
    ):
        assert forbidden not in combined


def test_postcompaction_receipt_names_all_five_sources() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == EXPECTED_SOURCES
    assert set(receipt["source_evidence"]) == EXPECTED_SOURCES
    assert receipt["terminal_handback_permitted"] is False
