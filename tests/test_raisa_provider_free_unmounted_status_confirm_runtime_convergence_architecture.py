from __future__ import annotations

import ast
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_unmounted_status_confirm_runtime_convergence_architecture
    as architecture,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-"
    "architecture-plan.md"
)
DESIGN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-"
    "architecture.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-status-confirm-runtime-"
    "convergence-architecture-threat-model-delta.md"
)
SCRIPT = (
    ROOT
    / "scripts/raisa_provider_free_unmounted_status_confirm_runtime_"
    "convergence_architecture.py"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_and_schema_are_closed_and_non_executing() -> None:
    contract = _load(architecture.CONTRACT_PATH)
    schema = _load(architecture.SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    assert schema["additionalProperties"] is False
    assert schema["$defs"]["architecture"]["additionalProperties"] is False
    for key in architecture.ARCHITECTURE_KEYS:
        assert schema["$defs"][key]["additionalProperties"] is False
    assert contract["implementation_authorized"] is False
    assert set(contract["forbidden"].values()) == {False}


def test_all_nine_source_bindings_match() -> None:
    contract = _load(architecture.CONTRACT_PATH)
    observed = architecture.verify_source_bindings(contract)
    assert len(observed) == 9
    assert observed == {
        item["path"]: item["sha256"] for item in contract["source_bindings"]
    }


def test_nine_architecture_decisions_are_exact() -> None:
    contract = _load(architecture.CONTRACT_PATH)
    architecture.validate_contract_semantics(contract)
    assert list(contract["architecture"])[:9] == architecture.ARCHITECTURE_KEYS


def test_all_twenty_scenarios_match_generated_evidence() -> None:
    contract = _load(architecture.CONTRACT_PATH)
    expected = architecture.build_evidence()
    stored = _load(architecture.EVIDENCE_PATH)
    assert stored == expected
    assert stored["scenario_count"] == 20
    assert len(stored["scenarios"]) == 20


def test_status_discrimination_and_authority_precede_disclosure() -> None:
    evidence = _load(architecture.EVIDENCE_PATH)
    scenarios = {item["id"]: item for item in evidence["scenarios"]}
    waiting = scenarios["sca-002-waiting-area-discriminated"]
    replay = scenarios["sca-015-same-digest-replay"]
    revoked = scenarios["sca-006-authority-revoked"]

    assert waiting["trace"] == ["discriminate:status_only"]
    assert replay["trace"].index("recheck:current_authority") < replay[
        "trace"
    ].index("inspect:idempotency")
    assert replay["trace"][-1] == "render:stored_canonical_receipt"
    assert revoked["receipt_disclosed"] is False
    assert "inspect:idempotency" not in revoked["trace"]


def test_version_warning_session_and_terminal_stops_are_effect_free() -> None:
    evidence = _load(architecture.EVIDENCE_PATH)
    scenarios = {item["id"]: item for item in evidence["scenarios"]}
    ids = [
        "sca-008-session-binding-stale",
        "sca-009-source-version-stale",
        "sca-010-warning-missing",
        "sca-011-warning-extra",
        "sca-012-warning-duplicate",
        "sca-013-warning-unknown",
        "sca-014-terminal-transition-deferred",
    ]
    assert scenarios[ids[-1]]["outcome"] == "transition_policy_deferred"
    for scenario_id in ids:
        assert scenarios[scenario_id]["effect_planned"] is False
        assert scenarios[scenario_id]["invocation_write_set"] == "none"
        assert scenarios[scenario_id]["receipt_disclosed"] is False


def test_atomic_write_set_and_delivery_recovery_are_exact() -> None:
    evidence = _load(architecture.EVIDENCE_PATH)
    scenarios = {item["id"]: item for item in evidence["scenarios"]}
    clean = scenarios["sca-001-clean-commit"]
    lost = scenarios["sca-017-post-commit-delivery-loss"]
    retry = scenarios["sca-018-retry-after-delivery-loss"]

    assert clean["invocation_write_set"] == "all"
    assert clean["response_source"] == "stored_canonical_receipt"
    assert lost["invocation_write_set"] == "all"
    assert lost["delivery_state"] == "delivery_unknown"
    assert lost["receipt_disclosed"] is False
    assert retry["outcome"] == "idempotent_replay"
    assert retry["invocation_write_set"] == "none"
    assert retry["response_source"] == "stored_canonical_receipt"
    for scenario_id in (
        "sca-019-audit-stage-failure",
        "sca-020-receipt-stage-failure",
    ):
        scenario = scenarios[scenario_id]
        assert scenario["outcome"] == "transaction_rolled_back"
        assert scenario["invocation_write_set"] == "none"


def test_all_hostile_mutations_are_rejected() -> None:
    evidence = _load(architecture.EVIDENCE_PATH)
    assert evidence["hostile_mutations"] == {"attempted": 56, "rejected": 56}


def test_validator_imports_no_application_or_database_package() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any(name == "app" or name.startswith("app.") for name in imported)
    assert not any(name.startswith("sqlalchemy") for name in imported)


def test_plan_and_threat_model_preserve_closed_boundaries() -> None:
    plan = " ".join(PLAN.read_text(encoding="utf-8").split())
    threat = " ".join(THREAT.read_text(encoding="utf-8").split())
    for phrase in (
        "Only these non-protected artifacts may be read or content-searched",
        "does not edit/import or execute an application route or database",
        "at least eighteen scenarios and forty hostile mutations",
        "No application edit/import, route or database execution",
        "`docs/branding/`",
    ):
        assert phrase in plan
    assert "implementation_authorized: false" in threat
    assert "AER-0291" in threat


def test_design_keeps_api_spine_and_physical_implementation_closed() -> None:
    design = " ".join(DESIGN.read_text(encoding="utf-8").split())
    for phrase in (
        "GraphQL remains read-only",
        "committed events remain cues for fresh authorized reads",
        "REST/OpenAPI command owned by the backend",
        "does not select a physical column, migration",
        "Physical implementation remains closed",
    ):
        assert phrase in design


def test_next_candidate_is_an_unmounted_rehearsal() -> None:
    evidence = _load(architecture.EVIDENCE_PATH)
    assert evidence["next_candidate"] == (
        "provider_free_unmounted_status_confirm_runtime_convergence_rehearsal"
    )
