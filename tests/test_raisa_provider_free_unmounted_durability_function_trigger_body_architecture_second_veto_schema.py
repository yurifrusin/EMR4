"""Focused R5 structural-schema vetoes for the two exact set expressions."""

from __future__ import annotations

from collections.abc import Iterator
from copy import deepcopy
import hashlib
import json
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder import (
    build_contract,
)
from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema import (
    build_schema,
)


JsonPath = tuple[str | int, ...]
SET_OPS = ("SET_CONTAINS_KEY", "SET_COVERS_KEYS")
MUTATIONS = (
    "unknown_property",
    "missing_required_property",
    "extra_property",
    "empty_key_pairs",
    "malformed_local_set_reference",
    "swapped_pair_field_names",
    "non_boolean_result_type",
)


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _reseal(candidate: dict[str, Any]) -> None:
    payload = deepcopy(candidate)
    payload.pop("contract_sha256", None)
    candidate["contract_sha256"] = "sha256:" + _canonical_sha256(payload)


def _expressions(
    value: Any,
    path: JsonPath = (),
) -> Iterator[tuple[JsonPath, dict[str, Any]]]:
    if isinstance(value, dict):
        if value.get("op") in SET_OPS:
            yield path, value
        for key, child in value.items():
            yield from _expressions(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _expressions(child, (*path, index))


def _set_expression(
    candidate: dict[str, Any],
    op: str,
) -> tuple[JsonPath, dict[str, Any]]:
    matches = [item for item in _expressions(candidate) if item[1]["op"] == op]
    assert matches
    return matches[0]


def _nested_errors(error: ValidationError) -> Iterator[ValidationError]:
    yield error
    for child in error.context:
        yield from _nested_errors(child)


def _mutate(expression: dict[str, Any], op: str, mutation: str) -> None:
    if mutation == "unknown_property":
        property_name = (
            "source_relation" if op == "SET_CONTAINS_KEY" else "evidence"
        )
        expression["unknown_property"] = expression.pop(property_name)
    elif mutation == "missing_required_property":
        expression.pop("source_relation" if op == "SET_CONTAINS_KEY" else "evidence")
    elif mutation == "extra_property":
        expression["unexpected"] = True
    elif mutation == "empty_key_pairs":
        expression["key_pairs"] = []
    elif mutation == "malformed_local_set_reference":
        operand = "set" if op == "SET_CONTAINS_KEY" else "required"
        expression[operand]["op"] = "REF"
    elif mutation == "swapped_pair_field_names":
        if op == "SET_CONTAINS_KEY":
            expression["key_pairs"][0] = {
                "required_column": "practice_id",
                "evidence_column": "practice_id",
            }
        else:
            expression["key_pairs"][0] = {
                "source_column": "practice_id",
                "set_column": "practice_id",
            }
    elif mutation == "non_boolean_result_type":
        expression["type"] = "pg_catalog.text"
    else:  # pragma: no cover - the parametrized population is frozen above
        raise AssertionError(f"unknown mutation {mutation}")


@pytest.fixture(scope="module")
def canonical_candidate_and_schema() -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = build_contract()
    schema = build_schema(candidate)
    Draft202012Validator.check_schema(schema)
    assert list(Draft202012Validator(schema).iter_errors(candidate)) == []
    assert {expression["op"] for _, expression in _expressions(candidate)} == set(
        SET_OPS
    )
    return candidate, schema


@pytest.mark.parametrize("op", SET_OPS)
@pytest.mark.parametrize("mutation", MUTATIONS)
def test_resealed_r5_set_expression_mutations_are_structurally_rejected(
    canonical_candidate_and_schema: tuple[dict[str, Any], dict[str, Any]],
    op: str,
    mutation: str,
) -> None:
    canonical, schema = canonical_candidate_and_schema
    candidate = deepcopy(canonical)
    expression_path, expression = _set_expression(candidate, op)
    _mutate(expression, op, mutation)
    _reseal(candidate)

    resealed_schema = deepcopy(schema)
    digest_schema = resealed_schema["properties"]["contract_sha256"]
    assert isinstance(digest_schema, dict)
    digest_schema["const"] = candidate["contract_sha256"]
    errors = list(Draft202012Validator(resealed_schema).iter_errors(candidate))

    assert errors
    nested = [child for error in errors for child in _nested_errors(error)]
    assert any(
        tuple(error.absolute_path)[: len(expression_path)] == expression_path
        for error in nested
    )
