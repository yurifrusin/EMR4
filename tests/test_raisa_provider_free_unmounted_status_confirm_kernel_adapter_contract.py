import ast
import json
from pathlib import Path

from scripts.raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract import (
    CONTRACT_PATH,
    EVIDENCE_PATH,
    LOCKS,
    SCHEMA_PATH,
    SOURCES,
    adapt,
    base_input,
    mutations,
    report,
    result_mappings,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_generated_contract_and_hostile_evidence_pass() -> None:
    contract, schema, evidence = load(CONTRACT_PATH), load(SCHEMA_PATH), load(EVIDENCE_PATH)
    assert validate(contract, schema) == []
    assert report(contract, schema) == evidence
    assert evidence == {
        "schema_version": "raisa.status_confirm_kernel_adapter_evidence.v1",
        "status": "passed",
        "canonical_errors": [],
        "case_count": 15,
        "result_mapping_count": 8,
        "hostile_mutation_count": 37,
        "admitted_hostile_mutations": [],
        "runtime_or_command_authority_granted": False,
    }


def test_ready_request_uses_only_server_authority_and_has_no_effect_authority() -> None:
    result = adapt(base_input())
    request = result["kernel_request"]
    assert result["kind"] == "kernel_request_ready"
    assert request["lock_plan"] == LOCKS
    assert request["practice_id"] == "practice-synthetic-001"
    assert request["actor_id"] == "actor-synthetic-001"
    assert request["session_id"] == "session-synthetic-001"
    assert request["source_version"] == 7
    assert request["effect_authority"] is False
    assert result["effect_authority"] is False


def test_revoked_authority_precedes_confirmation_and_evidence_disclosure() -> None:
    value = base_input()
    value["server"]["authority_current"] = False
    value["transport"]["confirmed"] = False
    value["server"]["evidence_status"] = "invalid"
    result = adapt(value)
    assert result["outcome"] == "authority_revoked"
    assert result["reason"] == "current_authority_revoked"
    assert result["kernel_request"] is None


def test_waiting_area_union_variant_and_terminal_retransition_stop() -> None:
    waiting = base_input()
    waiting["transport"]["proposal_intent"] = "update_appointment_waiting_area"
    assert adapt(waiting)["reason"] == "unsupported_status_confirm_variant"
    terminal = base_input()
    terminal["server"]["current_state"]["status"] = "Completed"
    assert adapt(terminal) == {
        "kind": "stopped",
        "outcome": "validation_rejected",
        "reason": "transition_policy_deferred",
        "kernel_request": None,
        "effect_authority": False,
    }


def test_warning_acknowledgement_is_exact_not_subset_or_superset() -> None:
    value = base_input()
    value["transport"]["proposal_warning_codes"] = ["waiting_area_cleared"]
    assert adapt(value)["outcome"] == "confirmation_required"
    value["transport"]["confirmed_warning_codes"] = ["waiting_area_cleared"]
    assert adapt(value)["kind"] == "kernel_request_ready"
    value["transport"]["confirmed_warning_codes"].append("unknown")
    assert adapt(value)["reason"] == "warning_acknowledgement_mismatch"


def test_signed_evidence_freshness_target_and_session_fail_closed() -> None:
    paths = (
        (("server", "session_id"), ""),
        (("server", "evidence_binding"), "mismatch"),
        (("transport", "freshness_id"), "stale"),
        (("server", "current_state", "appointment_id"), "apt-other"),
    )
    for path, changed in paths:
        value = base_input()
        cursor = value
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = changed
        assert adapt(value)["kernel_request"] is None


def test_result_mapping_uses_stored_receipt_and_rejects_status_schedule_conflict() -> None:
    mappings = {row["outcome"]: row for row in result_mappings()}
    assert mappings["committed"]["transport"] == "stored_receipt"
    assert mappings["idempotent_replay"]["transport"] == "stored_receipt_exact"
    assert mappings["schedule_conflict"] == {
        "outcome": "schedule_conflict",
        "transport": "internal_contract_error",
        "status": None,
        "release": False,
    }


def test_delivery_failure_keeps_receipt_digest_and_retry_identity() -> None:
    delivery = load(CONTRACT_PATH)["delivery_recovery"]
    assert delivery["delivery_failure_changes_receipt"] is False
    assert delivery["retry_uses_stored_receipt"] is True
    assert delivery["duplicate_kernel_request"] is False


def test_every_hostile_mutation_fails_closed() -> None:
    contract, schema = load(CONTRACT_PATH), load(SCHEMA_PATH)
    for name, candidate in mutations(contract):
        assert validate(candidate, schema), name


def test_source_allowlist_and_script_imports_remain_unmounted() -> None:
    assert load(CONTRACT_PATH)["source_bindings"] == SOURCES
    assert all(row["path"] in {source["path"] for source in SOURCES} for row in SOURCES)
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert imported.isdisjoint({"app", "sqlalchemy", "requests", "httpx", "google"})


def test_plan_design_and_threat_keep_runtime_closed() -> None:
    paths = (
        ROOT / "docs/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-plan.md",
        ROOT / "docs/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-design.md",
        ROOT / "docs/security/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-threat-model-delta.md",
    )
    text = " ".join(path.read_text(encoding="utf-8") for path in paths).lower()
    for phrase in (
        "server context alone supplies",
        "waiting-area union variant stops",
        "transition_policy_deferred",
        "stored receipt",
        "no application import/edit/route execution",
        "exact non-protected file allowlists",
    ):
        assert phrase in text
