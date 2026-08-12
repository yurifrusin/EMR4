from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any, Callable

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface import (
    CONTRACT_PATH,
    EXPECTED_DEPENDENCIES,
    EXPECTED_FAMILIES,
    EXPECTED_LOCK_ORDER,
    EXPECTED_MIGRATION_STEPS,
    EXPECTED_OUTCOMES,
    EXPECTED_PRECEDENCE,
    EXPECTED_SOURCE_HEAD,
    EXPECTED_SOURCES,
    SCHEMA_PATH,
    build_report,
    load_contract,
    load_schema,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-design.md"
THREAT = ROOT / "docs/security/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-threat-model-delta.md"
SCRIPT = ROOT / "scripts/raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface.py"


def _copy() -> dict[str, Any]:
    return copy.deepcopy(load_contract())


def _family(contract: dict[str, Any], family_id: str) -> dict[str, Any]:
    return next(
        row for row in contract["route_families"] if row["family_id"] == family_id
    )


def test_contract_schema_and_exact_report_pass() -> None:
    contract = load_contract()
    Draft202012Validator(load_schema()).validate(contract)

    assert validate_contract(contract) == []
    assert build_report(contract) == {
        "schema_version": "emr4.legacy-route-convergence-kernel-interface-report.v1",
        "status": "passed",
        "reasons": [],
        "source_head": EXPECTED_SOURCE_HEAD,
        "source_binding_count": 7,
        "route_family_count": 4,
        "raw_route_count": 4,
        "proposal_route_count": 6,
        "confirm_route_count": 5,
        "migration_step_count": 11,
        "route_behavior_changed": False,
        "command_or_write_performed": False,
    }


def test_source_bindings_are_exact_and_current() -> None:
    contract = load_contract()
    observed = {row["path"]: row["sha256"] for row in contract["source_bindings"]}

    assert observed == EXPECTED_SOURCES
    assert contract["source_head"] == EXPECTED_SOURCE_HEAD
    assert validate_contract(contract, verify_source_files=True) == []


def test_one_kernel_preserves_authority_confirmation_and_lock_order() -> None:
    kernel = load_contract()["kernel_interface"]

    assert kernel["outcomes"] == EXPECTED_OUTCOMES
    assert kernel["precedence"] == EXPECTED_PRECEDENCE
    assert kernel["canonical_lock_order"] == EXPECTED_LOCK_ORDER
    assert kernel["precedence"].index(
        "current_authority_before_receipt_disclosure"
    ) < kernel["precedence"].index("idempotency_replay_or_conflict")
    assert kernel["precedence"].index("separate_confirmation_validation") < kernel[
        "precedence"
    ].index("idempotency_replay_or_conflict")
    assert kernel["only_first_effect_outcome"] == "committed"
    assert kernel["event_authority"] == "never"
    assert kernel["context_frame_authority"] == "never"


def test_all_raw_routes_are_mapped_but_not_grandfathered() -> None:
    contract = load_contract()
    families = {row["family_id"]: row for row in contract["route_families"]}

    assert set(families) == set(EXPECTED_FAMILIES)
    for family_id, family in families.items():
        raw = family["raw_route"]
        target = family["kernel_target"]
        assert raw["kernel_execution_eligible_now"] is False
        assert raw["current_confirmation"] == "absent_or_unproven_backend_evidence"
        assert raw["current_precondition"] == "no_echoed_backend_precondition"
        assert raw["current_idempotency"] == "not_uniformly_command_enforced"
        assert raw["current_audit_signal"] == raw["adapter_id"]
        assert target["confirmation"].startswith("separate_")
        assert target["freshness"].startswith("backend_minted_expected_source")
        assert target["idempotency"] == (
            "durable_same_operation_key_and_command_digest_required"
        )
        assert target["raw_convergence_gate"].startswith("blocked_until_")
        assert all(
            route["mutates_appointment"] is False
            for route in family["proposal_routes"]
        ), family_id


def test_create_fence_and_existing_target_lock_profiles_are_exact() -> None:
    contract = load_contract()
    create = _family(contract, "appointment_create")["kernel_target"]
    update = _family(contract, "appointment_update")["kernel_target"]
    status = _family(contract, "appointment_status")["kernel_target"]
    delete = _family(contract, "appointment_delete")["kernel_target"]

    assert create["target_shape"] == "null_appointment_target"
    assert create["required_lock_plan"] == [
        "practice",
        "schedule_domain",
        "idempotency_record",
    ]
    assert create["schedule_fence"] == (
        "required_separate_reviewed_database_owned_primitive"
    )
    assert update["required_lock_plan"] == EXPECTED_LOCK_ORDER
    assert status["required_lock_plan"] == [
        "practice",
        "appointment",
        "idempotency_record",
    ]
    assert delete["required_lock_plan"] == status["required_lock_plan"]
    assert delete["confirmation"] == "separate_destructive_confirmation_required"


def test_migration_dag_delays_convergence_deprecation_and_retirement() -> None:
    steps = load_contract()["migration"]["steps"]

    assert [row["step_id"] for row in steps] == EXPECTED_MIGRATION_STEPS
    assert [row["order"] for row in steps] == list(range(1, 12))
    assert {row["step_id"]: row["depends_on"] for row in steps} == (
        EXPECTED_DEPENDENCIES
    )
    assert all(row["behavior_change"] is False for row in steps[:3])
    assert steps[7]["step_id"] == "create_schedule_fence_selection_and_proof"
    assert steps[7]["behavior_change"] is False
    assert set(steps[8]["depends_on"]) == {
        "raw_update_kernel_convergence",
        "create_schedule_fence_selection_and_proof",
    }
    assert set(steps[9]["depends_on"]) == {
        "raw_status_kernel_convergence",
        "raw_delete_kernel_convergence",
        "raw_update_kernel_convergence",
        "raw_create_kernel_convergence",
    }
    assert steps[10]["depends_on"] == ["raw_compat_header_rollout_decision"]


def test_validator_has_no_application_database_network_or_provider_imports() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert imported_roots <= {
        "__future__",
        "hashlib",
        "json",
        "jsonschema",
        "pathlib",
        "typing",
    }
    assert imported_roots.isdisjoint(
        {"app", "sqlalchemy", "psycopg", "requests", "httpx", "google"}
    )


def test_schema_closes_every_declared_object() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and "properties" in node:
                assert node.get("additionalProperties") is False
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)


def _hostile_mutants() -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("source_head", lambda c: c.__setitem__("source_head", "0" * 40)),
        (
            "source_digest",
            lambda c: c["source_bindings"][0].__setitem__("sha256", "0" * 64),
        ),
        ("source_removed", lambda c: c["source_bindings"].pop()),
        ("top_level_extra", lambda c: c.__setitem__("runtime_enabled", True)),
        (
            "route_behavior",
            lambda c: c["claim_boundary"].__setitem__("route_behavior_changed", True),
        ),
        (
            "provider_used",
            lambda c: c["claim_boundary"].__setitem__(
                "provider_or_network_used", True
            ),
        ),
        (
            "write_performed",
            lambda c: c["claim_boundary"].__setitem__(
                "command_or_write_performed", True
            ),
        ),
        (
            "request_field_removed",
            lambda c: c["kernel_interface"]["required_fields"].pop(),
        ),
        (
            "request_field_added",
            lambda c: c["kernel_interface"]["required_fields"].append(
                "ambient_authority"
            ),
        ),
        (
            "outcome_reordered",
            lambda c: c["kernel_interface"]["outcomes"].reverse(),
        ),
        (
            "outcome_added",
            lambda c: c["kernel_interface"]["outcomes"].append("implicit_success"),
        ),
        (
            "precedence_swapped",
            lambda c: c["kernel_interface"]["precedence"].__setitem__(
                slice(1, 4),
                [
                    "idempotency_replay_or_conflict",
                    "separate_confirmation_validation",
                    "current_authority_before_receipt_disclosure",
                ],
            ),
        ),
        (
            "lock_order_swapped",
            lambda c: c["kernel_interface"].__setitem__(
                "canonical_lock_order",
                ["practice", "appointment", "schedule_domain", "idempotency_record"],
            ),
        ),
        (
            "event_authority",
            lambda c: c["kernel_interface"].__setitem__("event_authority", "write"),
        ),
        (
            "frame_authority",
            lambda c: c["kernel_interface"].__setitem__(
                "context_frame_authority", "write"
            ),
        ),
        (
            "replay_first_effect",
            lambda c: c["kernel_interface"].__setitem__(
                "only_first_effect_outcome", "idempotent_replay"
            ),
        ),
        (
            "replay_second_audit",
            lambda c: c["kernel_interface"].__setitem__(
                "replay_effect", "create_second_mutation_audit"
            ),
        ),
        (
            "audit_field_removed",
            lambda c: c["kernel_interface"]["audit_fields"].pop(),
        ),
        (
            "audit_raw_body_allowed",
            lambda c: c["kernel_interface"]["audit_forbidden_material"].remove(
                "raw_request_body"
            ),
        ),
        ("family_removed", lambda c: c["route_families"].pop()),
        (
            "family_duplicate",
            lambda c: c["route_families"][1].__setitem__(
                "family_id", "appointment_create"
            ),
        ),
        (
            "create_operation_changed",
            lambda c: _family(c, "appointment_create").__setitem__(
                "canonical_operation_id", "rawCompatAppointmentCreate"
            ),
        ),
        (
            "raw_path_changed",
            lambda c: _family(c, "appointment_update")["raw_route"].__setitem__(
                "path", "/api/v1/appointments/update-any"
            ),
        ),
        (
            "raw_eligible",
            lambda c: _family(c, "appointment_status")["raw_route"].__setitem__(
                "kernel_execution_eligible_now", True
            ),
        ),
        (
            "raw_request_is_confirmation",
            lambda c: _family(c, "appointment_create")["raw_route"].__setitem__(
                "current_confirmation", "authenticated_request_is_confirmation"
            ),
        ),
        (
            "raw_same_read_is_freshness",
            lambda c: _family(c, "appointment_update")["raw_route"].__setitem__(
                "current_precondition", "same_transaction_read_is_freshness"
            ),
        ),
        (
            "raw_optional_idempotency",
            lambda c: _family(c, "appointment_delete")["raw_route"].__setitem__(
                "current_idempotency", "optional"
            ),
        ),
        (
            "proposal_mutates",
            lambda c: _family(c, "appointment_create")["proposal_routes"][
                0
            ].__setitem__("mutates_appointment", True),
        ),
        (
            "confirm_alias_scope_changed",
            lambda c: _family(c, "appointment_create")["confirm_routes"][
                1
            ].__setitem__("canonical_operation_id", "confirmBernieCreate"),
        ),
        (
            "create_target_row_invented",
            lambda c: _family(c, "appointment_create")["kernel_target"].__setitem__(
                "target_shape", "existing_appointment_target"
            ),
        ),
        (
            "create_schedule_lock_removed",
            lambda c: _family(c, "appointment_create")["kernel_target"].__setitem__(
                "required_lock_plan", ["practice", "idempotency_record"]
            ),
        ),
        (
            "create_fence_bypassed",
            lambda c: _family(c, "appointment_create")["kernel_target"].__setitem__(
                "schedule_fence", "not_required"
            ),
        ),
        (
            "delete_confirmation_weakened",
            lambda c: _family(c, "appointment_delete")["kernel_target"].__setitem__(
                "confirmation", "separate_confirmation_required"
            ),
        ),
        (
            "freshness_weakened",
            lambda c: _family(c, "appointment_status")["kernel_target"].__setitem__(
                "freshness", "same_transaction_read_only"
            ),
        ),
        (
            "idempotency_weakened",
            lambda c: _family(c, "appointment_update")["kernel_target"].__setitem__(
                "idempotency", "best_effort"
            ),
        ),
        (
            "audit_weakened",
            lambda c: _family(c, "appointment_update")["kernel_target"].__setitem__(
                "audit", "optional"
            ),
        ),
        (
            "convergence_gate_opened",
            lambda c: _family(c, "appointment_status")["kernel_target"].__setitem__(
                "raw_convergence_gate", "open"
            ),
        ),
        (
            "raw_mode_header",
            lambda c: c["migration"].__setitem__("current_raw_compat_mode", "header"),
        ),
        (
            "header_gate_open",
            lambda c: c["migration"].__setitem__("header_mode_decision", "allowed"),
        ),
        (
            "migration_reordered",
            lambda c: c["migration"]["steps"].reverse(),
        ),
        (
            "status_dependency_removed",
            lambda c: c["migration"]["steps"][4].__setitem__("depends_on", []),
        ),
        (
            "create_fence_dependency_removed",
            lambda c: c["migration"]["steps"][8].__setitem__(
                "depends_on", ["raw_update_kernel_convergence"]
            ),
        ),
        (
            "header_dependency_removed",
            lambda c: c["migration"]["steps"][9]["depends_on"].pop(),
        ),
        (
            "retirement_dependency_removed",
            lambda c: c["migration"]["steps"][10].__setitem__("depends_on", []),
        ),
        (
            "contract_step_changes_behavior",
            lambda c: c["migration"]["steps"][0].__setitem__(
                "behavior_change", True
            ),
        ),
        (
            "shadow_step_changes_behavior",
            lambda c: c["migration"]["steps"][2].__setitem__(
                "behavior_change", True
            ),
        ),
        (
            "fence_step_claims_route_change",
            lambda c: c["migration"]["steps"][7].__setitem__(
                "behavior_change", True
            ),
        ),
        (
            "future_dependency_cycle",
            lambda c: c["migration"]["steps"][0].__setitem__(
                "depends_on", ["raw_route_retirement_decision"]
            ),
        ),
    ]

    result: list[tuple[str, dict[str, Any]]] = []
    for name, mutate in mutations:
        candidate = _copy()
        mutate(candidate)
        result.append((name, candidate))
    return result


@pytest.mark.parametrize("name,candidate", _hostile_mutants())
def test_hostile_mutations_fail_closed(
    name: str, candidate: dict[str, Any]
) -> None:
    reasons = validate_contract(candidate, verify_source_files=False)
    assert reasons, name


def test_plan_design_and_threat_boundary_are_explicit() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, DESIGN, THREAT)
    )

    for phrase in (
        "not_kernel_eligible_now",
        "separate confirmation",
        "schedule-domain fence",
        "provider-free unmounted",
        "no application imports",
        "no route",
        "no database",
        "no provider",
        "no command",
        "protected-ref movement",
    ):
        assert phrase.lower() in combined.lower()

    assert CONTRACT_PATH.is_file()
