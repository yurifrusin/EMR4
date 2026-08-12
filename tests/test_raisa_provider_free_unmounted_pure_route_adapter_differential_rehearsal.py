from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal import (
    CONTRACT_PATH,
    EXPECTED_ADAPTERS,
    EXPECTED_FAMILY_LOCKS,
    EXPECTED_GAP_CODES,
    EXPECTED_LOCK_ORDER,
    EXPECTED_OUTCOMES,
    EXPECTED_PRECEDENCE,
    EXPECTED_REQUIRED_FIELDS,
    EXPECTED_SOURCE_HEAD,
    EXPECTED_SOURCES,
    SCHEMA_PATH,
    adapt_envelope,
    build_envelope,
    build_report,
    evaluate_scenario,
    hostile_mutations,
    load_contract,
    load_schema,
    semantic_projection,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-design.md"
THREAT = ROOT / "docs/security/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-threat-model-delta.md"
SCRIPT = ROOT / "scripts/raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal.py"


def _scenario(packet: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    return next(
        row for row in packet["scenario_matrix"] if row["scenario_id"] == scenario_id
    )


def _intent(packet: dict[str, Any], intent_id: str) -> dict[str, Any]:
    return next(
        row
        for row in packet["authored_synthetic_intents"]
        if row["intent_id"] == intent_id
    )


def test_closed_contract_and_exact_report_pass() -> None:
    packet = load_contract()
    Draft202012Validator(load_schema()).validate(packet)
    assert validate_contract(packet, verify_source_files=True) == []
    assert build_report(packet) == {
        "schema_version": "emr4.pure-route-adapter-differential-rehearsal-report.v1",
        "status": "passed",
        "reasons": [],
        "source_head": EXPECTED_SOURCE_HEAD,
        "adapter_count": 9,
        "confirm_adapter_count": 5,
        "raw_adapter_count": 4,
        "scenario_count": 13,
        "mapped_candidate_count": 9,
        "rejected_current_raw_count": 4,
        "differential_group_count": 4,
        "hostile_mutation_count": 45,
        "hostile_mutation_escape_count": 0,
        "runtime_execution_authorized": False,
        "command_or_write_performed": False,
    }


def test_source_bindings_are_exact_and_current() -> None:
    packet = load_contract()
    assert packet["source_head"] == EXPECTED_SOURCE_HEAD
    assert {
        row["path"]: row["sha256"] for row in packet["source_bindings"]
    } == EXPECTED_SOURCES
    assert validate_contract(packet, verify_source_files=True) == []


def test_kernel_vocabulary_and_authority_order_match_parent_contract() -> None:
    kernel = load_contract()["kernel_binding"]
    assert kernel["required_fields"] == EXPECTED_REQUIRED_FIELDS
    assert len(kernel["required_fields"]) == 18
    assert kernel["outcomes_preserved_but_not_evaluated"] == EXPECTED_OUTCOMES
    assert kernel["precedence_preserved_but_not_evaluated"] == EXPECTED_PRECEDENCE
    assert kernel["canonical_lock_order"] == EXPECTED_LOCK_ORDER
    assert kernel["precedence_preserved_but_not_evaluated"].index(
        "current_authority_before_receipt_disclosure"
    ) < kernel["precedence_preserved_but_not_evaluated"].index(
        "idempotency_replay_or_conflict"
    )
    assert kernel["provenance_only_fields"] == ["route_adapter_id"]
    assert kernel["runtime_execution_authorized"] is False
    assert kernel["command_outcome_emitted"] is False


def test_nine_adapters_exactly_cover_four_raw_and_five_confirm_routes() -> None:
    packet = load_contract()
    specs = {row["adapter_id"]: row for row in packet["adapter_specs"]}
    observed = {
        adapter_id: (
            spec["family_id"],
            spec["ingress_kind"],
            spec["method"],
            spec["path"],
            spec["canonical_operation_id"],
            spec["parent_route_posture"],
        )
        for adapter_id, spec in specs.items()
    }
    assert observed == EXPECTED_ADAPTERS
    assert sum(row["ingress_kind"] == "confirm" for row in specs.values()) == 5
    assert sum(row["ingress_kind"] == "raw" for row in specs.values()) == 4
    for spec in specs.values():
        assert spec["lock_plan"] == EXPECTED_FAMILY_LOCKS[spec["family_id"]]


def test_current_raw_profiles_fail_with_only_the_three_exact_gap_codes() -> None:
    packet = load_contract()
    current_raw = [
        row for row in packet["scenario_matrix"] if row["envelope_profile"] == "raw_current"
    ]
    assert len(current_raw) == 4
    for scenario in current_raw:
        result = evaluate_scenario(packet, scenario)
        assert result == {
            "adapter_result": "adapter_rejected",
            "reason_codes": EXPECTED_GAP_CODES,
            "kernel_candidate": None,
            "lock_plan": None,
            "runtime_execution_authorized": False,
            "command_outcome": None,
            "effect_performed": False,
        }


def test_complete_confirm_and_future_raw_profiles_map_all_eighteen_fields() -> None:
    packet = load_contract()
    mapped = [
        row
        for row in packet["scenario_matrix"]
        if row["envelope_profile"] in {"confirm_complete", "raw_future_complete"}
    ]
    assert len(mapped) == 9
    for scenario in mapped:
        result = evaluate_scenario(packet, scenario)
        assert result["adapter_result"] == "candidate_mapped"
        assert list(result["kernel_candidate"]) == EXPECTED_REQUIRED_FIELDS
        assert result["reason_codes"] == []
        assert result["runtime_execution_authorized"] is False
        assert result["command_outcome"] is None
        assert result["effect_performed"] is False


def test_four_differential_groups_match_except_honest_adapter_provenance() -> None:
    packet = load_contract()
    scenarios = {row["scenario_id"]: row for row in packet["scenario_matrix"]}
    for group in packet["differential_groups"]:
        candidates = [
            evaluate_scenario(packet, scenarios[scenario_id])["kernel_candidate"]
            for scenario_id in group["scenario_ids"]
        ]
        assert all(candidate is not None for candidate in candidates)
        projections = [semantic_projection(packet, candidate) for candidate in candidates]
        assert all(projection == projections[0] for projection in projections[1:])
        provenances = {candidate["route_adapter_id"] for candidate in candidates}
        assert len(provenances) == len(candidates)
        assert group["excluded_fields"] == ["route_adapter_id"]


def test_adapter_injects_operation_and_provenance_and_rejects_caller_spoofing() -> None:
    packet = load_contract()
    scenario = _scenario(packet, "rad-003-update-confirm")
    intent = _intent(packet, scenario["intent_id"])
    envelope = build_envelope("confirm_complete", intent)
    envelope["canonical_operation_id"] = "confirmAppointmentDeleteProposal"
    envelope["route_adapter_id"] = "raw_compat_delete"

    result = adapt_envelope(packet, scenario["adapter_id"], envelope)

    assert result["adapter_result"] == "adapter_rejected"
    assert result["reason_codes"] == ["caller_authority_field_forbidden"]
    assert result["kernel_candidate"] is None


def test_incomplete_raw_groups_never_emit_a_partial_candidate() -> None:
    packet = load_contract()
    scenario = _scenario(packet, "rad-011-update-raw-future-complete")
    intent = _intent(packet, scenario["intent_id"])
    complete = build_envelope("raw_future_complete", intent)

    for section, reason in (
        ("conditional_controls", "backend_precondition_missing"),
        ("confirmation_evidence", "confirmation_evidence_missing"),
        ("command_identity", "idempotency_identity_missing"),
    ):
        envelope = copy.deepcopy(complete)
        del envelope[section]
        result = adapt_envelope(packet, scenario["adapter_id"], envelope)
        assert result["adapter_result"] == "adapter_rejected"
        assert result["reason_codes"] == [reason]
        assert result["kernel_candidate"] is None


def test_target_and_conflict_shapes_fail_closed_per_operation() -> None:
    packet = load_contract()
    create = _scenario(packet, "rad-001-create-confirm")
    create_envelope = build_envelope(
        "confirm_complete", _intent(packet, create["intent_id"])
    )
    create_envelope["command"]["target_appointment_id"] = "syn-unexpected-target"
    assert adapt_envelope(packet, create["adapter_id"], create_envelope)[
        "reason_codes"
    ] == ["target_or_conflict_shape_invalid"]

    status = _scenario(packet, "rad-004-status-confirm")
    status_envelope = build_envelope(
        "confirm_complete", _intent(packet, status["intent_id"])
    )
    status_envelope["command"]["conflict_domain_id"] = "syn-unexpected-domain"
    assert adapt_envelope(packet, status["adapter_id"], status_envelope)[
        "reason_codes"
    ] == ["target_or_conflict_shape_invalid"]


def test_future_raw_mapping_does_not_claim_current_route_eligibility() -> None:
    packet = load_contract()
    raw_specs = [row for row in packet["adapter_specs"] if row["ingress_kind"] == "raw"]
    assert all(
        row["parent_route_posture"] == "current_raw_not_kernel_eligible"
        for row in raw_specs
    )
    assert packet["effect_boundary"]["runtime_adapter"] is False
    assert packet["effect_boundary"]["runtime_execution_authority"] is False
    assert packet["claim_boundary"]["route_behavior_changed"] is False


def test_all_forty_five_hostile_mutations_fail_closed() -> None:
    packet = load_contract()
    mutants = hostile_mutations(packet)
    assert len(mutants) == 45
    escaped = [name for name, mutant in mutants if not validate_contract(mutant)]
    assert escaped == []


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


def test_evaluator_imports_no_application_database_network_provider_or_process() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert imported_roots <= {
        "__future__",
        "copy",
        "hashlib",
        "json",
        "jsonschema",
        "pathlib",
        "typing",
    }
    assert imported_roots.isdisjoint(
        {
            "app",
            "sqlalchemy",
            "psycopg",
            "requests",
            "httpx",
            "google",
            "socket",
            "subprocess",
        }
    )


def test_plan_design_and_threat_model_keep_blocked_surfaces_closed() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8").lower() for path in (PLAN, DESIGN, THREAT)
    )
    assert "provider-free" in text
    assert "unmounted" in text
    assert "authored-synthetic" in text
    assert "application route" in text
    assert "no import" in text
    assert "no command" in text
    assert "no provider" in text
    assert "no runtime eligibility" in text
    assert "backend_precondition_missing" in text
    assert "confirmation_evidence_missing" in text
    assert "idempotency_identity_missing" in text


def test_contract_paths_and_artifacts_exist() -> None:
    for path in (CONTRACT_PATH, SCHEMA_PATH, PLAN, DESIGN, THREAT, SCRIPT):
        assert path.is_file()
