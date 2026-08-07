"""R4 normative closure attacks independent of whole-baseline equality."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterator

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema import (
    build_schema,
)
from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator import (
    ContractValidationError,
    EXACT_ENTRY_POINTS,
    EXACT_ENUM_VALUES,
    EXACT_NORMATIVE_SECTION_SHA256,
    EXACT_PARENT_BINDING,
    EXACT_TRIGGER_FUNCTIONS,
    assert_contract_valid,
    derive_contract_semantics,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "function-trigger-body-architecture/function-trigger-body-architecture-"
    "contract.json"
)
OUTBOX = "emr4_context_fabric.diary_context_observation_outbox_v1"
OWNER = "emr4_context_fabric.context_schema_owner"
PRODUCER = "emr4_context_fabric.project_update_confirm_reschedule_v1"
RETENTION_REASON = "emr4_context_fabric.source_retention_reason"


def _load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _reseal(candidate: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(candidate)
    payload.pop("contract_sha256", None)
    candidate["contract_sha256"] = "sha256:" + _canonical_sha256(payload)
    return candidate


def _issues(candidate: dict[str, Any]) -> set[str]:
    return {issue.code for issue in validate_contract(candidate).issues}


def _expressions(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        if "op" in value and "node_id" not in value:
            yield value
        for child in value.values():
            yield from _expressions(child)
    elif isinstance(value, list):
        for child in value:
            yield from _expressions(child)


def _assert_normative_schema_regeneration_rejects(
    candidate: dict[str, Any],
) -> None:
    with pytest.raises(ContractValidationError):
        build_schema(candidate)


@pytest.fixture(scope="module")
def contract() -> dict[str, Any]:
    return _load_contract()


def test_exact_candidate_has_independent_normative_and_derived_closure(
    contract: dict[str, Any],
) -> None:
    assert contract["parent_binding"] == EXACT_PARENT_BINDING
    assert [
        operation["id"]
        for operation in contract["structural_feasibility_recovery_v1"][
            "operations"
        ]
    ] == [f"REC{index:02d}" for index in range(1, 27)]
    for section, expected_digest in EXACT_NORMATIVE_SECTION_SHA256.items():
        assert _canonical_sha256(contract[section]) == expected_digest
    signatures = contract["effective_parent_summary"]["effective_signatures"]
    full_signatures = [
        signatures["support"],
        *signatures["entry_points"],
        *signatures["trigger_functions"],
    ]
    assert len(full_signatures) == 23
    assert all(signature["public_execute"] is False for signature in full_signatures)
    assert [row["id"] for row in signatures["entry_points"]] == list(
        EXACT_ENTRY_POINTS
    )
    assert [row["id"] for row in signatures["trigger_functions"]] == list(
        EXACT_TRIGGER_FUNCTIONS
    )
    assert [
        row["function"]
        for row in contract["effective_parent_summary"]["trigger_declarations"]
    ] == list(EXACT_TRIGGER_FUNCTIONS)

    report = assert_contract_valid(contract)
    derived = derive_contract_semantics(contract)
    assert report.issues == ()
    assert derived["call_graph"] == contract["call_graph"]
    assert derived["body_summaries"] == {
        program["id"]: program["derived_effect_summary"]
        for program in contract["body_programs"]
    }


def test_schema_freezes_normative_scalars_without_whole_body_consts(
    contract: dict[str, Any],
) -> None:
    schema = build_schema(contract)
    Draft202012Validator.check_schema(schema)
    assert list(Draft202012Validator(schema).iter_errors(contract)) == []
    for section in (
        "parent_binding",
        "structural_feasibility_recovery_v1",
        "effective_parent_summary",
        "typed_ir_contract",
        "trigger_applicability_return_matrix",
        "renderer_order",
        "artifact_boundary",
    ):
        encoded = json.dumps(schema["properties"][section], sort_keys=True)
        assert '"const"' in encoded
    assert "prefixItems" in schema["properties"]["renderer_order"]
    assert "prefixItems" in schema["properties"][
        "structural_feasibility_recovery_v1"
    ]["properties"]["operations"]
    body_schema = json.dumps(schema["$defs"]["body_program"], sort_keys=True)
    assert '"ast": {"const"' not in body_schema
    assert '"derived_effect_summary": {"const"' not in body_schema


def test_resealed_owner_outbox_delete_is_independently_rejected(
    contract: dict[str, Any],
) -> None:
    candidate = deepcopy(contract)
    owner = next(
        role
        for role in candidate["effective_parent_summary"]["effective_roles"]
        if role["role"] == OWNER
    )
    owner["direct_table_dml"].append(
        {"relation": OUTBOX, "privileges": ["DELETE"]}
    )
    _reseal(candidate)

    codes = _issues(candidate)
    assert "outbox_delete_privilege" in codes
    assert "normative_section_mismatch" in codes
    _assert_normative_schema_regeneration_rejects(candidate)


def test_resealed_rec19_widening_is_independently_rejected(
    contract: dict[str, Any],
) -> None:
    candidate = deepcopy(contract)
    rec19 = candidate["structural_feasibility_recovery_v1"]["operations"][18]
    rec19["values"].append("OWNER_SELECTED_EXTRA_REASON")
    _reseal(candidate)

    codes = _issues(candidate)
    assert "retention_reason_vocabulary" in codes
    assert "normative_section_mismatch" in codes
    _assert_normative_schema_regeneration_rejects(candidate)


def test_resealed_invalid_retention_enum_const_fails_semantics_and_regenerated_schema(
    contract: dict[str, Any],
) -> None:
    candidate = deepcopy(contract)
    retention_constants = [
        expression
        for expression in _expressions(candidate["body_programs"])
        if expression.get("op") == "CONST"
        and expression.get("type") == RETENTION_REASON
    ]
    assert retention_constants
    retention_constants[0]["value"] = "NOT_A_RETENTION_REASON"
    _reseal(candidate)

    assert "enum_constant_membership" in _issues(candidate)
    regenerated = build_schema(candidate)
    schema_errors = list(Draft202012Validator(regenerated).iter_errors(candidate))
    assert schema_errors
    assert "NOT_A_RETENTION_REASON" not in EXACT_ENUM_VALUES[RETENTION_REASON]


def test_resealed_producer_owner_swap_is_independently_rejected(
    contract: dict[str, Any],
) -> None:
    candidate = deepcopy(contract)
    producer = next(
        signature
        for signature in candidate["effective_parent_summary"][
            "effective_signatures"
        ]["entry_points"]
        if signature["id"] == PRODUCER
    )
    producer["owner"] = "emr4_context_fabric.context_admission_receiver"
    _reseal(candidate)

    assert "normative_section_mismatch" in _issues(candidate)
    _assert_normative_schema_regeneration_rejects(candidate)


def test_resealed_central_event_proof_removal_is_independently_rejected(
    contract: dict[str, Any],
) -> None:
    candidate = deepcopy(contract)
    producer = next(
        program for program in candidate["body_programs"] if program["id"] == PRODUCER
    )
    producer["ast"]["nodes"] = [
        node
        for node in producer["ast"]["nodes"]
        if node["node_id"] != f"{PRODUCER}.p12"
    ]
    _reseal(candidate)

    assert "producer_event_membership_proof" in _issues(candidate)
    _assert_normative_schema_regeneration_rejects(candidate)
