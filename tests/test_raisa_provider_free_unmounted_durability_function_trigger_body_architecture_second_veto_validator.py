"""Focused R5 semantic-validator attacks with resealed hostile candidates."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Iterator

import pytest

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder import (
    build_contract,
)
from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator import (
    validate_contract,
)


PRODUCER = "emr4_context_fabric.project_update_confirm_reschedule_v1"
CHECKPOINT = "emr4_context_fabric.context_durability_checkpoint"
GENERATION = "emr4_context_fabric.context_observer_generation"


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _reseal(candidate: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(candidate)
    payload.pop("contract_sha256", None)
    candidate["contract_sha256"] = "sha256:" + _canonical_sha256(payload)
    return candidate


def _issue_codes(candidate: dict[str, Any]) -> set[str]:
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


def _expression(
    candidate: dict[str, Any], op: str, *, source_relation: str | None = None
) -> dict[str, Any]:
    return next(
        expression
        for expression in _expressions(candidate["body_programs"])
        if expression.get("op") == op
        and (
            source_relation is None
            or expression.get("source_relation") == source_relation
        )
    )


def _producer_signature(candidate: dict[str, Any]) -> dict[str, Any]:
    return next(
        signature
        for signature in candidate["effective_parent_summary"][
            "effective_signatures"
        ]["entry_points"]
        if signature["id"] == PRODUCER
    )


@pytest.fixture(scope="module")
def contract() -> dict[str, Any]:
    candidate = build_contract()
    assert validate_contract(candidate).issues == ()
    return candidate


@pytest.mark.parametrize(
    ("field_name", "hostile_value", "expected_code"),
    [
        (
            "owner",
            "emr4_context_fabric.context_admission_receiver",
            "signature_owner_mismatch",
        ),
        ("security_definer", False, "signature_security_definer_mismatch"),
        ("volatility", "STABLE", "signature_volatility_mismatch"),
    ],
)
def test_resealed_signature_field_mutations_have_specific_semantic_findings(
    contract: dict[str, Any],
    field_name: str,
    hostile_value: Any,
    expected_code: str,
) -> None:
    candidate = deepcopy(contract)
    _producer_signature(candidate)[field_name] = hostile_value
    _reseal(candidate)

    codes = _issue_codes(candidate)
    assert expected_code in codes
    assert codes - {"normative_section_mismatch"}


@pytest.mark.parametrize(
    ("field_name", "hostile_value", "expected_code"),
    [
        ("timing", "AFTER", "trigger_declaration_timing_mismatch"),
        (
            "deferrable",
            True,
            "trigger_declaration_deferrable_mismatch",
        ),
    ],
)
def test_resealed_trigger_field_mutations_have_specific_semantic_findings(
    contract: dict[str, Any],
    field_name: str,
    hostile_value: Any,
    expected_code: str,
) -> None:
    candidate = deepcopy(contract)
    declaration = candidate["effective_parent_summary"]["trigger_declarations"][0]
    declaration[field_name] = hostile_value
    _reseal(candidate)

    codes = _issue_codes(candidate)
    assert expected_code in codes
    assert codes - {"normative_section_mismatch"}


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("operand_shape", "set_operand_shape"),
        ("scalar_type", "set_operand_relation_array_type"),
        ("source_relation", "set_contains_source_relation_mismatch"),
        ("partial_identity", "set_contains_generation_identity_mismatch"),
        ("unknown_key", "set_source_column_unknown"),
        ("mismatched_types", "set_key_pair_type_mismatch"),
        ("empty_pairs", "set_key_pairs_empty"),
    ],
)
def test_set_contains_key_rejects_shape_type_key_and_relation_substitutions(
    contract: dict[str, Any], mutation: str, expected_code: str
) -> None:
    candidate = deepcopy(contract)
    expression = _expression(
        candidate, "SET_CONTAINS_KEY", source_relation=CHECKPOINT
    )
    if mutation == "operand_shape":
        expression["set"]["op"] = "REF"
    elif mutation == "scalar_type":
        expression["set"]["type"] = "pg_catalog.bigint"
    elif mutation == "source_relation":
        expression["source_relation"] = (
            "emr4_context_fabric.context_recovery_anchor"
        )
    elif mutation == "partial_identity":
        expression["key_pairs"].pop()
    elif mutation == "unknown_key":
        expression["key_pairs"][0]["source_column"] = "unknown_key"
    elif mutation == "mismatched_types":
        expression["key_pairs"][0]["source_column"] = (
            "last_contiguous_position"
        )
    else:
        expression["key_pairs"] = []
    _reseal(candidate)

    assert expected_code in _issue_codes(candidate)


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("operand_shape", "set_operand_shape"),
        ("scalar_type", "set_operand_relation_array_type"),
        (
            "relation_substitution",
            "set_coverage_evidence_relation_mismatch",
        ),
        ("partial_identity", "set_coverage_generation_identity_mismatch"),
        ("unknown_key", "set_evidence_column_unknown"),
        ("mismatched_types", "set_key_pair_type_mismatch"),
        ("empty_pairs", "set_key_pairs_empty"),
    ],
)
def test_set_covers_keys_rejects_shape_type_key_and_relation_substitutions(
    contract: dict[str, Any], mutation: str, expected_code: str
) -> None:
    candidate = deepcopy(contract)
    expression = _expression(candidate, "SET_COVERS_KEYS")
    if mutation == "operand_shape":
        expression["evidence"]["op"] = "REF"
    elif mutation == "scalar_type":
        expression["required"]["type"] = "pg_catalog.bigint"
    elif mutation == "relation_substitution":
        expression["evidence"] = {
            "kind": "LOCAL",
            "symbol": "generation_set",
            "type": GENERATION + "[]",
        }
    elif mutation == "partial_identity":
        expression["key_pairs"].pop()
    elif mutation == "unknown_key":
        expression["key_pairs"][0]["evidence_column"] = "unknown_key"
    elif mutation == "mismatched_types":
        expression["key_pairs"][0]["evidence_column"] = "interval_start"
    else:
        expression["key_pairs"] = []
    _reseal(candidate)

    assert expected_code in _issue_codes(candidate)
