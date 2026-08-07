"""R7A rotation-anchor fence structure and ordering attacks."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder import (
    build_contract,
)
from tests.test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor import (
    _expressions,
    _node,
    _nodes,
    _program,
    _reseal,
)


BODY_ID = "emr4_context_fabric.rotate_observation_key_v1"
ANCHOR = "emr4_context_fabric.context_recovery_anchor"
CHECKPOINT = "emr4_context_fabric.context_durability_checkpoint"
GENERATION = "emr4_context_fabric.context_observer_generation"
KEY = "emr4_context_fabric.context_observation_key_interval"
FENCE_ID = BODY_ID + ".anchor_fence_exact"
EFFECT_OPS = {"INSERT", "INSERT_OR_RELOAD_COMPARE", "UPDATE", "DELETE_SOURCE"}

EXPECTED_EQ_PAIRS = (
    (("anchor", ANCHOR, "checkpoint_state"), ("checkpoint", CHECKPOINT, "checkpoint_state")),
    (("anchor", ANCHOR, "last_contiguous_position"), ("checkpoint", CHECKPOINT, "last_contiguous_position")),
    (("anchor", ANCHOR, "last_observation_digest"), ("checkpoint", CHECKPOINT, "last_observation_digest")),
    (("anchor", ANCHOR, "checkpoint_integrity_digest"), ("checkpoint", CHECKPOINT, "checkpoint_integrity_digest")),
    (("anchor", ANCHOR, "policy_digest"), ("generation", GENERATION, "policy_digest")),
    (("anchor", ANCHOR, "principal_digest"), ("generation", GENERATION, "principal_digest")),
    (("anchor", ANCHOR, "binding_digest"), ("generation", GENERATION, "binding_digest")),
    (("anchor", ANCHOR, "source_digest"), ("generation", GENERATION, "source_digest")),
    (("anchor", ANCHOR, "registry_digest"), ("generation", GENERATION, "registry_digest")),
    (("anchor", ANCHOR, "impact_digest"), ("generation", GENERATION, "impact_digest")),
    (("anchor", ANCHOR, "key_schedule_digest"), ("generation", GENERATION, "key_schedule_digest")),
)


@pytest.fixture(scope="module")
def contract() -> dict[str, Any]:
    return build_contract()


def _branch(program: dict[str, Any], name: str) -> list[dict[str, Any]]:
    return _node(program, ".replay")["operands"][name]


def _ref_key(expression: dict[str, Any]) -> tuple[str, str, str]:
    assert expression.get("op") == "REF"
    assert expression.get("kind") == "ROW_COLUMN"
    return (
        str(expression.get("symbol")),
        str(expression.get("relation")),
        str(expression.get("column")),
    )


def _uses_canonical_digest(node: dict[str, Any]) -> bool:
    return any(
        expression.get("op") == "CANONICAL_DIGEST"
        for expression in _expressions(node)
    )


def _assert_rotation_anchor_fence(candidate: dict[str, Any]) -> None:
    program = _program(candidate, BODY_ID)
    fence_nodes = [node for node in _nodes(program) if node["node_id"] == FENCE_ID]
    assert len(fence_nodes) == 1
    fence = fence_nodes[0]
    assert fence["op"] == "ASSERT"
    assert fence["operands"]["failure_id"] == "F_ANCHOR"

    predicate = fence["operands"]["predicate"]
    assert set(predicate) == {"op", "operands", "type"}
    assert predicate["op"] == "AND"
    assert predicate["type"] == "pg_catalog.boolean"
    comparisons = predicate["operands"]
    assert len(comparisons) == len(EXPECTED_EQ_PAIRS)
    assert all(
        set(comparison) == {"op", "left", "right", "type"}
        and comparison["op"] == "EQ"
        and comparison["type"] == "pg_catalog.boolean"
        for comparison in comparisons
    )
    actual_pairs = tuple(
        (_ref_key(comparison["left"]), _ref_key(comparison["right"]))
        for comparison in comparisons
    )
    assert actual_pairs == EXPECTED_EQ_PAIRS

    new_effect = _branch(program, "else")
    fence_index = new_effect.index(fence)
    anchor_index = next(
        index
        for index, node in enumerate(new_effect)
        if node["node_id"].endswith(".lock_anchor")
    )
    prior_key_index = next(
        index
        for index, node in enumerate(new_effect)
        if node["node_id"].endswith(".lock_prior_key")
    )
    assert fence_index == anchor_index + 1
    assert fence_index < prior_key_index

    digest_use_indices = [
        index
        for index, node in enumerate(new_effect)
        if _uses_canonical_digest(node)
    ]
    effect_indices = [
        index
        for index, node in enumerate(new_effect)
        if node["op"] in EFFECT_OPS
    ]
    assert digest_use_indices and effect_indices
    assert all(fence_index < index for index in digest_use_indices)
    assert all(fence_index < index for index in effect_indices)

    replay_nodes = list(_nodes(_branch(program, "then")))
    assert all(node["node_id"] != FENCE_ID for node in replay_nodes)
    assert all(node["op"] not in EFFECT_OPS for node in replay_nodes)
    assert all(
        not (
            node["op"] == "LOCK_EXACT"
            and node["operands"].get("relation") in {ANCHOR, KEY}
        )
        for node in replay_nodes
    )


def _hostile(contract: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = deepcopy(contract)
    return candidate, _program(candidate, BODY_ID)


def test_rotation_anchor_fence_is_exact_and_precedes_new_effects(
    contract: dict[str, Any],
) -> None:
    _assert_rotation_anchor_fence(contract)


@pytest.mark.parametrize("pair_index", range(len(EXPECTED_EQ_PAIRS)))
@pytest.mark.parametrize("mutation", ["remove", "substitute"])
def test_resealed_candidate_rejects_each_removed_or_substituted_equality(
    contract: dict[str, Any], pair_index: int, mutation: str
) -> None:
    candidate, program = _hostile(contract)
    comparisons = _node(program, ".anchor_fence_exact")["operands"]["predicate"][
        "operands"
    ]
    if mutation == "remove":
        comparisons.pop(pair_index)
    else:
        comparisons[pair_index] = deepcopy(
            comparisons[(pair_index + 1) % len(comparisons)]
        )
    _reseal(candidate)

    with pytest.raises(AssertionError):
        _assert_rotation_anchor_fence(candidate)


@pytest.mark.parametrize("role", ["anchor", "checkpoint", "generation"])
@pytest.mark.parametrize("mutation", ["relation", "symbol"])
def test_resealed_candidate_rejects_wrong_row_identity(
    contract: dict[str, Any], role: str, mutation: str
) -> None:
    candidate, program = _hostile(contract)
    comparisons = _node(program, ".anchor_fence_exact")["operands"]["predicate"][
        "operands"
    ]
    if role == "anchor":
        reference = comparisons[0]["left"]
    elif role == "checkpoint":
        reference = comparisons[0]["right"]
    else:
        reference = comparisons[4]["right"]
    if mutation == "relation":
        reference["relation"] = KEY
    else:
        reference["symbol"] = "wrong_row"
    _reseal(candidate)

    with pytest.raises(AssertionError):
        _assert_rotation_anchor_fence(candidate)


@pytest.mark.parametrize("mutation", ["comparison", "failure"])
def test_resealed_candidate_rejects_ne_or_wrong_failure_family(
    contract: dict[str, Any], mutation: str
) -> None:
    candidate, program = _hostile(contract)
    fence = _node(program, ".anchor_fence_exact")
    if mutation == "comparison":
        fence["operands"]["predicate"]["operands"][0]["op"] = "NE"
    else:
        fence["operands"]["failure_id"] = "F_STATE"
    _reseal(candidate)

    with pytest.raises(AssertionError):
        _assert_rotation_anchor_fence(candidate)


@pytest.mark.parametrize("target", ["prior_key", "first_effect"])
def test_resealed_candidate_rejects_late_anchor_fence(
    contract: dict[str, Any], target: str
) -> None:
    candidate, program = _hostile(contract)
    new_effect = _branch(program, "else")
    fence = _node(program, ".anchor_fence_exact")
    new_effect.remove(fence)
    if target == "prior_key":
        target_index = next(
            index
            for index, node in enumerate(new_effect)
            if node["node_id"].endswith(".lock_prior_key")
        )
    else:
        target_index = next(
            index
            for index, node in enumerate(new_effect)
            if node["op"] in EFFECT_OPS
        )
    new_effect.insert(target_index + 1, fence)
    _reseal(candidate)

    with pytest.raises(AssertionError):
        _assert_rotation_anchor_fence(candidate)


def test_resealed_candidate_rejects_digest_use_before_anchor_fence(
    contract: dict[str, Any],
) -> None:
    candidate, program = _hostile(contract)
    new_effect = _branch(program, "else")
    digest = next(
        expression
        for expression in _expressions(new_effect)
        if expression.get("op") == "CANONICAL_DIGEST"
    )
    anchor_index = new_effect.index(_node(program, ".lock_anchor"))
    new_effect.insert(
        anchor_index,
        {
            "node_id": BODY_ID + ".hostile_early_digest",
            "op": "LET",
            "operands": {
                "output_symbol": "hostile_early_digest",
                "expression": deepcopy(digest),
            },
        },
    )
    _reseal(candidate)

    with pytest.raises(AssertionError):
        _assert_rotation_anchor_fence(candidate)
