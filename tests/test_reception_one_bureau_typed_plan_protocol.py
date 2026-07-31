"""Focused guards for the provider-free Bureau Typed Plan Protocol."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import reception_one_bureau_typed_plan_protocol as protocol


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "bernie-reception-one-bureau-typed-plan-protocol-plan.md"
ARTIFACTS = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-typed-plan-protocol"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _expanded_case(case_id: str) -> tuple[dict, dict]:
    cases = _json(protocol.CASES_PATH)
    case = next(item for item in cases["cases"] if item["case_id"] == case_id)
    return protocol.expand_case(cases, case), case


def test_plan_freezes_provider_free_typed_dialogue_and_executor_boundaries() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for required in (
        "reception_one_bureau_typed_plan_protocol_provider_free_pass",
        "`admit`",
        "`revision_required`",
        "`clarification_required`",
        "`reject`",
        "at most twelve ordered steps",
        "`write_performed=false`",
        "`provider_calls=0`",
        "`runtime_or_provider_wiring_ready=false`",
        "`raw_trove_access_ready=false`",
        "`runtime_gate_decision=blocked`",
        "No occupied provider call is authorised by this plan.",
    ):
        assert required in text


def test_all_protocol_schemas_are_valid_draft_2020_12() -> None:
    for path in protocol.SCHEMA_PATHS.values():
        schema = _json(path)
        Draft202012Validator.check_schema(schema)


def test_catalogue_is_closed_and_maps_only_to_existing_proposal_operations() -> None:
    catalog = _json(protocol.CATALOG_PATH)
    operators = protocol.operator_map(catalog)
    assert len(operators) == 14
    assert {item["effect"] for item in operators.values()} == {
        "pure",
        "authorised_read",
        "proposal_only",
    }
    assert {
        item["api_spine_operation_id"]
        for item in operators.values()
        if item["api_spine_operation_id"]
    } == {
        "proposeSlotSearch",
        "proposeAppointmentCreate",
        "proposeAppointmentUpdate",
        "proposeAppointmentDelete",
        "proposeAppointmentStatus",
    }
    openapi = OPENAPI.read_text(encoding="utf-8")
    for operation_id in {
        "proposeSlotSearch",
        "proposeAppointmentCreate",
        "proposeAppointmentUpdate",
        "proposeAppointmentDelete",
        "proposeAppointmentStatus",
    }:
        assert f"operationId: {operation_id}" in openapi
    for forbidden in (
        "confirmAppointment",
        "database",
        "provider",
        "network",
        "shell",
        "command",
    ):
        assert all(forbidden not in operator_id for operator_id in operators)


def test_computed_evidence_matches_persisted_evidence() -> None:
    computed = protocol.build_evidence()
    persisted = _json(ARTIFACTS / "evidence.json")
    assert computed == persisted
    assert computed["status"] == "pass"
    assert computed["catalogue"]["operator_count"] == 14
    assert len(computed["positive_cases"]) == 6
    assert len(computed["negative_cases"]) == 6


def test_known_actions_reuse_deterministic_semantic_extraction() -> None:
    evidence = protocol.build_evidence()
    known = [
        item
        for item in evidence["positive_cases"]
        if item["planner_class"] == "deterministic_semantic_adapter"
    ]
    assert {item["goal"] for item in known} == {
        "create",
        "move",
        "resize",
        "cancel",
        "status_change",
    }
    assert all(item["review_disposition"] == "admit" for item in known)
    assert all(item["boundary"] == protocol.BOUNDARY for item in known)


def test_create_without_spoken_duration_uses_typed_backend_default() -> None:
    frame, _ = _expanded_case("known-create")
    frame["utterances"] = [
        (
            "Make an appointment for Margaret Thompson with Dr Shera "
            "tomorrow at 2:30 pm."
        )
    ]
    plan = protocol.deterministic_plan(frame)
    duration_bindings = [
        step["args"]["duration_minutes"]
        for step in plan["steps"]
        if "duration_minutes" in step["args"]
    ]
    assert duration_bindings == [
        {"kind": "context_ref", "field": "default_duration_minutes"},
        {"kind": "context_ref", "field": "default_duration_minutes"},
    ]
    review, normalized = protocol.proofread_plan(frame, plan)
    assert review["disposition"] == "admit"
    execution = protocol.execute_plan(frame, normalized, review)
    assert execution["final_output"]["duration_minutes"] == 15


def test_novel_squeeze_in_composes_known_primitives_without_overbook_authority() -> None:
    evidence = protocol.build_evidence()
    squeeze = next(
        item
        for item in evidence["positive_cases"]
        if item["case_id"] == "novel-squeeze-in"
    )
    assert squeeze["planner_class"] == "untrusted_model_candidate"
    assert squeeze["operator_trace"] == [
        "resolve_patient_reference",
        "resolve_practitioner_reference",
        "resolve_date_expression",
        "read_practitioner_schedule",
        "assess_squeeze_in_options",
    ]
    assert squeeze["final_output"]["kind"] == "squeeze_in_assessment"
    assert squeeze["final_output"]["api_spine_operation_id"] is None
    assert squeeze["final_output"]["candidate_slot_ids"] == [
        "synthetic-slot-july27-1215"
    ]
    assert squeeze["final_output"]["write_performed"] is False
    assert squeeze["final_output"]["requires_human_confirmation"] is True
    assert "manual_squeeze_in_review" in squeeze["final_output"]["warning_codes"]


def test_typed_plan_review_dialogue_is_one_revision_and_hash_bound() -> None:
    evidence = protocol.build_evidence()
    dialogue = evidence["typed_dialogue"]
    assert dialogue["revision_count"] == 1
    assert dialogue["revision_limit"] == 2
    assert dialogue["first_attempt"] == {
        "attempt": 1,
        "disposition": "revision_required",
        "violation_codes": ["signature_mismatch"],
        "execution_authorized": False,
    }
    assert dialogue["second_attempt"]["attempt"] == 2
    assert dialogue["second_attempt"]["disposition"] == "admit"
    assert dialogue["second_attempt"]["execution_authorized"] is True
    assert len(dialogue["second_attempt"]["plan_sha256"]) == 64


def test_unknown_stale_fabricated_forward_write_and_exhausted_cases_fail_closed() -> None:
    evidence = protocol.build_evidence()
    negatives = {item["case_id"]: item for item in evidence["negative_cases"]}
    assert set(negatives) == {
        "unknown-forbidden-operator",
        "fabricated-entity-reference",
        "forward-dataflow-reference",
        "stale-context-revision",
        "write-effect-escalation",
        "revision-budget-exhausted",
    }
    assert all(item["disposition"] == "reject" for item in negatives.values())
    assert all(item["execution_blocked"] is True for item in negatives.values())
    assert "stale_context" in negatives["stale-context-revision"]["violation_codes"]
    assert "effect_escalation" in negatives["write-effect-escalation"]["violation_codes"]
    assert (
        "revision_budget_exhausted"
        in negatives["revision-budget-exhausted"]["violation_codes"]
    )


def test_executor_rechecks_review_hash_and_context_revision() -> None:
    frame, _ = _expanded_case("known-create")
    plan = protocol.deterministic_plan(frame)
    review, normalized = protocol.proofread_plan(frame, plan)
    assert review["disposition"] == "admit"

    changed_review = copy.deepcopy(review)
    changed_review["normalized_plan_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="reviewed plan hash mismatch"):
        protocol.execute_plan(frame, normalized, changed_review)

    changed_frame = copy.deepcopy(frame)
    changed_frame["context_revision"] += 1
    with pytest.raises(ValueError, match="context revision changed"):
        protocol.execute_plan(changed_frame, normalized, review)


def test_non_admitted_plan_cannot_reach_executor() -> None:
    frame, _ = _expanded_case("known-create")
    plan = protocol.deterministic_plan(frame)
    del plan["steps"][-1]["args"]["duration_minutes"]
    review, normalized = protocol.proofread_plan(frame, plan)
    assert review["disposition"] == "revision_required"
    with pytest.raises(ValueError, match="non-admitted plan cannot execute"):
        protocol.execute_plan(frame, normalized, review)


def test_watcher_seam_rejects_superseded_context_without_touching_event_runtime() -> None:
    evidence = protocol.build_evidence()["watcher_supersession_seam"]
    assert evidence == {
        "context_revision_required": True,
        "stale_plan_disposition": "reject",
        "fresh_read_performed": False,
        "event_runtime_changed": False,
    }


def test_protocol_script_has_no_provider_network_database_or_command_actuator() -> None:
    source = (
        ROOT / "scripts" / "reception_one_bureau_typed_plan_protocol.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "import google",
        "from google",
        "import requests",
        "from requests",
        "import socket",
        "from socket",
        "import subprocess",
        "from subprocess",
        "import sqlalchemy",
        "from sqlalchemy",
        "os.environ",
        "access_token",
        "api_key",
        "http://",
        "https://australia-southeast1-aiplatform",
    ):
        assert forbidden not in source


def test_provider_and_product_boundaries_remain_zero_and_closed() -> None:
    evidence = protocol.build_evidence()
    assert evidence["provider_boundary"] == {
        "execution_enabled": False,
        "provider_calls": 0,
        "credentials_requested": False,
        "network_access": False,
        "raw_prompt_persisted": False,
        "raw_response_persisted": False,
    }
    assert evidence["product_boundary"] == {
        "database_access": False,
        "product_data_access": False,
        "appointment_write": False,
        "confirmation": False,
        "product_delivery": False,
        "new_api_route": False,
        "new_event_family": False,
    }


def test_continuity_and_compass_bind_typed_plan_descendant_when_accepted() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    nodes = {
        node["id"]: node
        for node in graph["nodes"]
        if node["id"]
        in {
            "reception-one-integrated-bureau",
            "reception-one-bureau-typed-plan-protocol",
        }
    }
    assert set(nodes) == {
        "reception-one-integrated-bureau",
        "reception-one-bureau-typed-plan-protocol",
    }
    assert nodes["reception-one-bureau-typed-plan-protocol"]["relationships"] == [
        {
            "node_id": "reception-one-integrated-bureau",
            "relation": "builds_on",
        }
    ]
    assert graph["graph_revision"] >= 63
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["map_revision"] >= 50
