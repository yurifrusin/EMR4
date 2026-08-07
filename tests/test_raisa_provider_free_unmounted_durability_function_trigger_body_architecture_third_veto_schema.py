"""Focused R6 structural uniqueness vetoes for exact set-expression pairs."""

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


@pytest.fixture(scope="module")
def canonical_candidate_and_schema() -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = build_contract()
    schema = build_schema(candidate)
    Draft202012Validator.check_schema(schema)
    assert {expression["op"] for _, expression in _expressions(candidate)} == set(
        SET_OPS
    )
    return candidate, schema


def test_canonical_candidate_remains_structurally_valid(
    canonical_candidate_and_schema: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    candidate, schema = canonical_candidate_and_schema
    assert list(Draft202012Validator(schema).iter_errors(candidate)) == []


@pytest.mark.parametrize("op", SET_OPS)
def test_resealed_duplicate_set_key_pair_is_structurally_rejected(
    canonical_candidate_and_schema: tuple[dict[str, Any], dict[str, Any]],
    op: str,
) -> None:
    canonical, schema = canonical_candidate_and_schema
    candidate = deepcopy(canonical)
    expression_path, expression = _set_expression(candidate, op)
    expression["key_pairs"].append(deepcopy(expression["key_pairs"][0]))
    _reseal(candidate)

    resealed_schema = deepcopy(schema)
    resealed_schema["properties"]["contract_sha256"]["const"] = candidate[
        "contract_sha256"
    ]
    errors = list(Draft202012Validator(resealed_schema).iter_errors(candidate))
    nested = [child for error in errors for child in _nested_errors(error)]

    assert any(
        error.validator == "uniqueItems"
        and tuple(error.absolute_path) == (*expression_path, "key_pairs")
        for error in nested
    )
