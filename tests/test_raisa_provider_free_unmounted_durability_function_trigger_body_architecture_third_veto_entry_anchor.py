"""Candidate-independent R6A/R6B entry-program path and evidence attacks."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Iterator

import pytest

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder import (
    build_contract,
)


SOURCE = "emr4_context_fabric.diary_context_observation_outbox_v1"
FRAME = "emr4_context_fabric.context_frame_generation"
WATERMARK = "emr4_context_fabric.context_invalidation_watermark"
OBLIGATION = "emr4_context_fabric.context_reassembly_obligation"
CHECKPOINT = "emr4_context_fabric.context_durability_checkpoint"
ANCHOR = "emr4_context_fabric.context_recovery_anchor"
LIFECYCLE = "emr4_context_fabric.context_durability_lifecycle"
AUDIT = "emr4_context_fabric.context_durability_audit"
ANCHOR_PROFILE = "emr4_context_fabric.recovery_anchor_digest_v1"
COORDINATOR = "emr4_context_fabric.apply_durability_transition_v1"
ANCHOR_BODY = "emr4_context_fabric.append_recovery_anchor_v1"
ROTATION_BODY = "emr4_context_fabric.rotate_observation_key_v1"
ANCHOR_COLUMNS = (
    "practice_id",
    "source_contract_id",
    "stream_id",
    "stream_epoch",
    "observer_id",
    "observer_generation",
    "lifecycle_revision",
    "checkpoint_state",
    "last_contiguous_position",
    "last_observation_digest",
    "policy_digest",
    "principal_digest",
    "binding_digest",
    "source_digest",
    "registry_digest",
    "impact_digest",
    "key_schedule_digest",
    "checkpoint_integrity_digest",
    "anchor_digest",
    "created_at",
)


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _reseal(candidate: dict[str, Any]) -> None:
    payload = deepcopy(candidate)
    payload.pop("contract_sha256", None)
    candidate["contract_sha256"] = "sha256:" + _canonical_sha256(payload)


def _program(contract: dict[str, Any], body_id: str) -> dict[str, Any]:
    return next(
        program for program in contract["body_programs"] if program["id"] == body_id
    )


@pytest.fixture(scope="module")
def contract() -> dict[str, Any]:
    return build_contract()


def _nodes(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        if {"node_id", "op", "operands"}.issubset(value):
            yield value
        for child in value.values():
            yield from _nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nodes(child)


def _expressions(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        if "op" in value and "node_id" not in value:
            yield value
        for child in value.values():
            yield from _expressions(child)
    elif isinstance(value, list):
        for child in value:
            yield from _expressions(child)


def _node(program: dict[str, Any], suffix: str) -> dict[str, Any]:
    return next(
        node for node in _nodes(program) if node["node_id"].endswith(suffix)
    )


def _delete_node(value: Any, suffix: str) -> bool:
    if isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, dict) and str(child.get("node_id", "")).endswith(
                suffix
            ):
                del value[index]
                return True
            if _delete_node(child, suffix):
                return True
    elif isinstance(value, dict):
        for child in value.values():
            if _delete_node(child, suffix):
                return True
    return False


def _paths(
    nodes: list[dict[str, Any]],
    node_ids: tuple[str, ...] = (),
    relations: frozenset[str] = frozenset(),
) -> Iterator[tuple[tuple[str, ...], frozenset[str]]]:
    if not nodes:
        yield node_ids, relations
        return
    node, *remaining = nodes
    operands = node.get("operands", {})
    relation = operands.get("relation")
    next_relations = (
        relations | {relation} if isinstance(relation, str) else relations
    )
    next_ids = (*node_ids, node["node_id"])
    if node["op"] == "IF":
        for branch_name in ("then", "else"):
            branch = operands.get(branch_name, [])
            yield from _paths([*branch, *remaining], next_ids, next_relations)
        return
    if node["op"] in {
        "RETURN_ROW",
        "RETURN_COMPOSITE",
        "RETURN_NEW",
        "RETURN_OLD",
        "RETURN_NULL",
        "RAISE",
        "PROPAGATE_RETRYABLE",
    }:
        yield next_ids, next_relations
        return
    yield from _paths(remaining, next_ids, next_relations)


def _assert_coordinator_path_locality(program: dict[str, Any]) -> None:
    paths = list(_paths(program["ast"]["nodes"]))
    replay_forbidden = {SOURCE, ANCHOR, FRAME, WATERMARK, OBLIGATION}
    rebase_forbidden = {SOURCE, FRAME, WATERMARK, OBLIGATION}
    replay_paths = [
        path for path in paths if any(node_id.endswith(".lock_receipt") for node_id in path[0])
    ]
    terminal_paths = [
        path
        for path in paths
        if any(node_id.endswith(".lock_terminal_lifecycle") for node_id in path[0])
    ]
    conflict_paths = [
        path
        for path in paths
        if any(node_id.endswith(".lock_conflict") for node_id in path[0])
    ]
    assert replay_paths and terminal_paths and conflict_paths
    for _, relations in [*replay_paths, *terminal_paths]:
        assert relations.isdisjoint(replay_forbidden)
    for _, relations in conflict_paths:
        assert relations.isdisjoint(rebase_forbidden)
        assert ANCHOR in relations

    assert _node(program, ".lock_anchor_for_proof")["operands"]["ordinal"] == 4
    assert _node(program, ".lock_primary")["operands"]["ordinal"] == 5
    assert _node(program, ".lock_conflict_anchor")["operands"]["ordinal"] == 4
    assert _node(program, ".lock_conflict")["operands"]["ordinal"] == 5

    source_paths = [path for path in paths if SOURCE in path[1]]
    assert source_paths
    assert all(
        any(node_id.endswith(".lock_primary") for node_id in node_ids)
        for node_ids, _ in source_paths
    )


def _binding_value(node: dict[str, Any], column: str) -> dict[str, Any]:
    bindings = node["operands"].get(
        "bindings", node["operands"].get("set_bindings", [])
    )
    return next(binding["value"] for binding in bindings if binding["column"] == column)


def _assert_rebase_parent_anchor(program: dict[str, Any]) -> None:
    primary_tags = {
        "gap",
        "dependent_state",
        "anchor_integrity",
        "key",
        "predecessor",
        "epoch",
        "source_ambiguous",
    }
    lifecycle_nodes = [
        node
        for node in _nodes(program)
        if node["op"] == "INSERT"
        and node["operands"].get("relation") == LIFECYCLE
        and ".rebase_lifecycle." in node["node_id"]
    ]
    assert lifecycle_nodes
    for lifecycle_node in lifecycle_nodes:
        tag = lifecycle_node["node_id"].rsplit(".", maxsplit=1)[-1]
        if tag in primary_tags:
            anchor_symbol = "anchor"
            lock = _node(program, ".lock_anchor_for_proof")
        elif tag == "conflict":
            anchor_symbol = "conflict_anchor"
            lock = _node(program, ".lock_conflict_anchor")
        else:
            anchor_symbol = f"rebase_anchor_{tag}"
            lock = _node(program, f".lock_rebase_anchor.{tag}")
        assert lock["op"] == "LOCK_EXACT"
        assert lock["operands"]["relation"] == ANCHOR
        assert lock["operands"]["output_symbol"] == anchor_symbol
        assert _node(program, f".rebase_anchor_exact.{tag}")["operands"][
            "failure_id"
        ] == "F_STATE"
        assert _binding_value(lifecycle_node, "prior_lifecycle_digest") == {
            "op": "REF",
            "kind": "ROW_COLUMN",
            "symbol": anchor_symbol,
            "relation": ANCHOR,
            "column": "anchor_digest",
            "type": "emr4_context_fabric.digest_sha256",
        }


def test_coordinator_replay_and_conflict_paths_have_branch_local_reads(
    contract: dict[str, Any],
) -> None:
    program = _program(contract, COORDINATOR)
    _assert_coordinator_path_locality(program)
    _assert_rebase_parent_anchor(program)


@pytest.mark.parametrize("hoisted_suffix", [".source_position_set", ".current_frame_set"])
def test_coordinator_path_walker_rejects_hostile_read_hoisting(
    contract: dict[str, Any],
    hoisted_suffix: str,
) -> None:
    candidate = deepcopy(contract)
    program = _program(candidate, COORDINATOR)
    hoisted = deepcopy(_node(program, hoisted_suffix))
    hoisted["node_id"] += ".hostile_hoist"
    program["ast"]["nodes"].insert(-1, hoisted)
    _reseal(candidate)

    with pytest.raises(AssertionError):
        _assert_coordinator_path_locality(program)


def _digest_profiles(program: dict[str, Any]) -> set[str]:
    return {
        expression["profile"]
        for expression in _expressions(program)
        if expression.get("op") == "CANONICAL_DIGEST"
        and isinstance(expression.get("profile"), str)
    }


def _row_columns(value: Any, symbol: str) -> set[str]:
    return {
        str(expression.get("column"))
        for expression in _expressions(value)
        if expression.get("op") == "REF"
        and expression.get("kind") == "ROW_COLUMN"
        and expression.get("symbol") == symbol
    }


def _is_const(expression: Any, value: Any, type_name: str) -> bool:
    return expression == {"op": "CONST", "type": type_name, "value": value}


def _is_row_ref(
    expression: Any, symbol: str, relation: str, column: str
) -> bool:
    return (
        isinstance(expression, dict)
        and expression.get("op") == "REF"
        and expression.get("kind") == "ROW_COLUMN"
        and expression.get("symbol") == symbol
        and expression.get("relation") == relation
        and expression.get("column") == column
    )


def _is_source_ref(expression: Any, relation: str, column: str) -> bool:
    return (
        isinstance(expression, dict)
        and expression.get("op") == "REF"
        and expression.get("kind") == "SOURCE_COLUMN"
        and expression.get("relation") == relation
        and expression.get("column") == column
    )


def _is_count(expression: Any, symbol: str) -> bool:
    return (
        isinstance(expression, dict)
        and expression.get("op") == "COUNT"
        and isinstance(expression.get("operand"), dict)
        and expression["operand"].get("op") == "REF"
        and expression["operand"].get("kind") == "LOCAL"
        and expression["operand"].get("symbol") == symbol
    )


def _assert_count_comparison(
    node: dict[str, Any], op: str, symbol: str, value: int
) -> None:
    predicate = node["operands"]["predicate"]
    assert predicate["op"] == op
    assert _is_count(predicate["left"], symbol)
    assert _is_const(predicate["right"], value, "pg_catalog.bigint")


def _assert_audit_chain(program: dict[str, Any], tag: str) -> None:
    matching_symbol = f"{tag}_matching_audit_set"
    earlier_symbol = f"{tag}_earlier_audit_set"
    prior_symbol = f"{tag}_prior_audit"
    later_symbol = f"{tag}_later_audit_set"
    matching = _node(program, f".{tag}_matching_audit_set")
    earlier = _node(program, f".{tag}_earlier_audit_set")
    prior = _node(program, f".{tag}_prior_audit")
    later = _node(program, f".{tag}_later_audit_set")
    assert matching["operands"]["cardinality"] == "COMPLETE_SET"
    assert earlier["operands"]["cardinality"] == "COMPLETE_SET"
    assert prior["operands"]["cardinality"] == "EXACTLY_ONE"
    assert later["operands"]["cardinality"] == "COMPLETE_SET"
    assert matching["operands"]["predicate"] == prior["operands"]["predicate"]

    matching_expressions = list(_expressions(matching["operands"]["predicate"]))
    assert any(
        expression.get("op") == "EQ"
        and _is_source_ref(expression.get("left"), AUDIT, "audit_head_digest")
        for expression in matching_expressions
    )
    expected_symbol = "decision_audit" if tag == "decision" else "checkpoint"
    expected_column = (
        "prior_audit_digest" if tag == "decision" else "audit_head_digest"
    )
    assert _row_columns(matching, expected_symbol) == {expected_column}
    assert any(
        expression.get("op") == "LT"
        and _is_source_ref(
            expression.get("left"), AUDIT, "lifecycle_revision"
        )
        for expression in matching_expressions
    )

    cardinality = _node(program, f".{tag}_prior_audit_cardinality")
    assert cardinality["operands"]["failure_id"] == "F_ANCHOR"
    _assert_count_comparison(cardinality, "LTE", matching_symbol, 1)
    route = _node(program, f".{tag}_prior_audit_route")
    assert route["operands"]["convergence"] == "REJOIN"
    route_condition = route["operands"]["condition"]
    assert route_condition["op"] == "EQ"
    assert _is_count(route_condition["left"], matching_symbol)
    assert _is_const(route_condition["right"], 1, "pg_catalog.bigint")

    later_expressions = list(_expressions(later["operands"]["predicate"]))
    assert any(
        expression.get("op") == "GT"
        and _is_source_ref(
            expression.get("left"), AUDIT, "lifecycle_revision"
        )
        and _is_row_ref(
            expression.get("right"), prior_symbol, AUDIT, "lifecycle_revision"
        )
        for expression in later_expressions
    )
    assert any(
        expression.get("op") == "LT"
        and _is_source_ref(
            expression.get("left"), AUDIT, "lifecycle_revision"
        )
        for expression in later_expressions
    )
    latest = _node(program, f".{tag}_latest_prior_audit")
    assert latest["operands"]["failure_id"] == "F_ANCHOR"
    _assert_count_comparison(latest, "EQ", later_symbol, 0)

    baseline = _node(program, f".{tag}_baseline_audit")
    assert baseline["operands"]["failure_id"] == "F_ANCHOR"
    baseline_expressions = list(
        _expressions(baseline["operands"]["predicate"])
    )
    assert any(
        expression.get("op") == "EQ"
        and _is_count(expression.get("left"), earlier_symbol)
        and _is_const(expression.get("right"), 0, "pg_catalog.bigint")
        for expression in baseline_expressions
    )
    assert _row_columns(baseline, "baseline_anchor") == {"anchor_digest"}
    assert _row_columns(baseline, expected_symbol) == {expected_column}


def _assert_prior_anchor_is_immediate(
    program: dict[str, Any], suffix: str
) -> None:
    predicate = _node(program, suffix)["operands"]["predicate"]
    subtract = next(
        expression
        for expression in _expressions(predicate)
        if expression.get("op") == "SUBTRACT"
    )
    assert _is_const(subtract["right"], 1, "pg_catalog.bigint")


def _assert_lifecycle_shapes(program: dict[str, Any]) -> None:
    timestamp = _node(program, ".checkpoint_lifecycle_timestamp")
    assert timestamp["operands"]["failure_id"] == "F_ANCHOR"
    predicate = timestamp["operands"]["predicate"]
    assert predicate["op"] == "EQ"
    assert _is_row_ref(
        predicate["left"], "checkpoint", CHECKPOINT, "updated_at"
    )
    assert _is_row_ref(
        predicate["right"], "anchor_lifecycle", LIFECYCLE, "created_at"
    )

    decision = _node(program, ".decision_lifecycle_shape")
    decision_expressions = list(_expressions(decision["operands"]["predicate"]))
    assert any(
        expression.get("op") == "IS_NOT_NULL"
        and _is_row_ref(
            expression.get("operand"),
            "anchor_lifecycle",
            LIFECYCLE,
            "source_position",
        )
        for expression in decision_expressions
    )
    assert any(
        expression.get("op") == "GT"
        and _is_row_ref(
            expression.get("left"),
            "anchor_lifecycle",
            LIFECYCLE,
            "source_position",
        )
        and _is_const(expression.get("right"), 0, "pg_catalog.bigint")
        for expression in decision_expressions
    )
    for column in ("key_interval_start", "key_interval_end"):
        assert any(
            expression.get("op") == "IS_NULL"
            and _is_row_ref(
                expression.get("operand"),
                "anchor_lifecycle",
                LIFECYCLE,
                column,
            )
            for expression in decision_expressions
        )

    key = _node(program, ".key_rotation_exact")
    key_expressions = list(_expressions(key["operands"]["predicate"]))
    assert any(
        expression.get("op") == "IS_NULL"
        and _is_row_ref(
            expression.get("operand"),
            "anchor_lifecycle",
            LIFECYCLE,
            "source_position",
        )
        for expression in key_expressions
    )
    for column in ("key_interval_start", "key_interval_end"):
        assert any(
            expression.get("op") == "IS_NOT_NULL"
            and _is_row_ref(
                expression.get("operand"),
                "anchor_lifecycle",
                LIFECYCLE,
                column,
            )
            for expression in key_expressions
        )
    assert any(
        expression.get("op") == "LT"
        and _is_row_ref(
            expression.get("left"),
            "anchor_lifecycle",
            LIFECYCLE,
            "key_interval_start",
        )
        and _is_row_ref(
            expression.get("right"),
            "anchor_lifecycle",
            LIFECYCLE,
            "key_interval_end",
        )
        for expression in key_expressions
    )
    for column in ("last_contiguous_position", "last_observation_digest"):
        checkpoint_comparisons = [
            expression
            for expression in key_expressions
            if expression.get("op") == "EQ"
            and (
                _is_row_ref(
                    expression.get("left"), "checkpoint", CHECKPOINT, column
                )
                or _is_row_ref(
                    expression.get("right"), "checkpoint", CHECKPOINT, column
                )
            )
        ]
        assert len(checkpoint_comparisons) == 1
        comparison = checkpoint_comparisons[0]
        assert _is_row_ref(
            comparison["left"], "checkpoint", CHECKPOINT, column
        )
        assert _is_row_ref(
            comparison["right"], "key_previous_anchor", ANCHOR, column
        )
    assert not any(
        expression.get("op") == "EQ"
        and {
            (
                expression.get("left", {}).get("symbol"),
                expression.get("left", {}).get("column"),
            ),
            (
                expression.get("right", {}).get("symbol"),
                expression.get("right", {}).get("column"),
            ),
        }
        == {
            ("anchor_lifecycle", "source_position"),
            ("checkpoint", "last_contiguous_position"),
        }
        for expression in key_expressions
    )


def _assert_rotation_parent_constraint(program: dict[str, Any]) -> None:
    lifecycle_insert = _node(program, ".lifecycle_insert")
    assert _binding_value(lifecycle_insert, "source_position") == {
        "op": "CONST",
        "type": "pg_catalog.bigint",
        "value": None,
    }
    prior = _binding_value(lifecycle_insert, "prior_lifecycle_digest")
    assert _is_row_ref(prior, "anchor", ANCHOR, "anchor_digest")
    interval_order = _node(program, ".interval_order")["operands"]["predicate"]
    assert interval_order["op"] == "GT"
    assert interval_order["left"]["field"] == "interval_end"
    assert interval_order["right"]["field"] == "interval_start"
    checkpoint_update = _node(program, ".checkpoint_update")
    updated_columns = {
        binding["column"]
        for binding in checkpoint_update["operands"]["set_bindings"]
    }
    assert "last_contiguous_position" not in updated_columns
    assert "last_observation_digest" not in updated_columns


def _assert_anchor_evidence(program: dict[str, Any]) -> None:
    required_nodes = {
        ".revision_nonzero",
        ".revision_current",
        ".common_state_exact",
        ".baseline_anchor_set",
        ".baseline_anchor_cardinality",
        ".baseline_anchor",
        ".lifecycle",
        ".checkpoint_lifecycle_timestamp",
        ".decision_lifecycle_shape",
        ".decision_previous_anchor",
        ".decision_audit",
        ".decision_matching_audit_set",
        ".decision_earlier_audit_set",
        ".decision_prior_audit_cardinality",
        ".decision_prior_audit",
        ".decision_later_audit_set",
        ".decision_latest_prior_audit",
        ".decision_baseline_audit",
        ".decision_prior_audit_route",
        ".decision_receipt_set",
        ".decision_receipt",
        ".anchor_primary_set",
        ".anchor_conflict_set",
        ".anchor_primary",
        ".rederive_receipt_digest",
        ".rederive_rebase_integrity",
        ".rederive_apply_integrity",
        ".key_audit_set",
        ".key_receipt_set",
        ".key_matching_audit_set",
        ".key_earlier_audit_set",
        ".key_prior_audit_cardinality",
        ".key_prior_audit",
        ".key_later_audit_set",
        ".key_latest_prior_audit",
        ".key_baseline_audit",
        ".key_prior_audit_route",
        ".anchor_key",
        ".key_previous_anchor",
        ".rederive_rotation_integrity",
        ".derive_anchor_digest",
        ".anchor_cardinality",
        ".stored_exact",
    }
    node_list = list(_nodes(program))
    node_ids = {node["node_id"] for node in node_list}
    for suffix in required_nodes:
        assert any(node_id.endswith(suffix) for node_id in node_ids)

    expected_cardinalities = {
        ".baseline_anchor_set": "COMPLETE_SET",
        ".baseline_anchor": "EXACTLY_ONE",
        ".lifecycle": "EXACTLY_ONE",
        ".decision_previous_anchor": "EXACTLY_ONE",
        ".decision_audit": "EXACTLY_ONE",
        ".decision_receipt_set": "COMPLETE_SET",
        ".decision_receipt": "EXACTLY_ONE",
        ".anchor_primary_set": "COMPLETE_SET",
        ".anchor_conflict_set": "COMPLETE_SET",
        ".anchor_primary": "EXACTLY_ONE",
        ".key_audit_set": "COMPLETE_SET",
        ".key_receipt_set": "COMPLETE_SET",
        ".anchor_key": "EXACTLY_ONE",
        ".key_previous_anchor": "EXACTLY_ONE",
    }
    for suffix, cardinality in expected_cardinalities.items():
        assert _node(program, suffix)["operands"]["cardinality"] == cardinality

    assert {
        "emr4_context_fabric.checkpoint_rebase_digest_v1",
        "emr4_context_fabric.classified_receipt_digest_v1",
        "emr4_context_fabric.checkpoint_apply_digest_v1",
        "emr4_context_fabric.key_rotation_digest_v1",
        ANCHOR_PROFILE,
    }.issubset(_digest_profiles(program))

    revision = json.dumps(_node(program, ".revision_nonzero"), sort_keys=True)
    assert '"op": "GT"' in revision and '"value": 0' in revision
    decision_condition = _node(program, ".lifecycle_is_decision")["operands"][
        "condition"
    ]
    key_condition = _node(program, ".lifecycle_is_key_rotation")["operands"][
        "condition"
    ]
    for condition, expected_kind in (
        (decision_condition, "DECISION"),
        (key_condition, "KEY_ROTATION"),
    ):
        assert condition["op"] == "EQ"
        assert _is_row_ref(
            condition["left"],
            "anchor_lifecycle",
            LIFECYCLE,
            "entry_kind",
        )
        assert _is_const(
            condition["right"],
            expected_kind,
            "emr4_context_fabric.lifecycle_entry_kind",
        )

    rebase_exact = json.dumps(
        _node(program, ".decision_rebase_exact"), sort_keys=True
    )
    receipt_exact = json.dumps(
        _node(program, ".decision_admission_exact"), sort_keys=True
    )
    key_exact = json.dumps(
        _node(program, ".key_zero_decision_evidence"), sort_keys=True
    )
    assert "decision_receipt_set" in rebase_exact and '"value": 0' in rebase_exact
    assert all(
        symbol in receipt_exact
        for symbol in (
            "decision_receipt_set",
            "anchor_primary_set",
            "anchor_conflict_set",
        )
    )
    assert all(
        symbol in key_exact for symbol in ("key_audit_set", "key_receipt_set")
    )

    baseline = _node(program, ".baseline_anchor")
    assert baseline["operands"]["relation"] == ANCHOR
    assert any(
        _is_const(expression, 0, "pg_catalog.bigint")
        for expression in _expressions(baseline["operands"]["predicate"])
    )
    baseline_cardinality = _node(program, ".baseline_anchor_cardinality")
    assert baseline_cardinality["operands"]["failure_id"] == "F_ANCHOR"
    _assert_count_comparison(
        baseline_cardinality, "EQ", "baseline_anchor_set", 1
    )
    _assert_audit_chain(program, "decision")
    _assert_audit_chain(program, "key")
    _assert_prior_anchor_is_immediate(program, ".decision_previous_anchor")
    _assert_prior_anchor_is_immediate(program, ".key_previous_anchor")
    _assert_lifecycle_shapes(program)

    stored_exact = _node(program, ".stored_exact")
    assert _row_columns(stored_exact, "stored_anchor") == set(ANCHOR_COLUMNS)
    top_level_ids = [node["node_id"] for node in program["ast"]["nodes"]]
    assert top_level_ids.index(
        next(node_id for node_id in top_level_ids if node_id.endswith(".derive_anchor_digest"))
    ) < top_level_ids.index(
        next(node_id for node_id in top_level_ids if node_id.endswith(".anchor_set"))
    )
    assert all(node["op"] not in {"UPDATE", "DELETE_SOURCE"} for node in node_list)


def test_anchor_has_complete_branch_specific_evidence_before_digest(
    contract: dict[str, Any],
) -> None:
    _assert_anchor_evidence(_program(contract, ANCHOR_BODY))
    _assert_rotation_parent_constraint(_program(contract, ROTATION_BODY))


@pytest.mark.parametrize(
    "missing_suffix",
    [
        ".lifecycle",
        ".decision_audit",
        ".decision_receipt",
        ".anchor_primary_set",
        ".anchor_conflict_set",
        ".anchor_key",
        ".decision_previous_anchor",
        ".key_previous_anchor",
        ".baseline_anchor",
        ".decision_prior_audit",
        ".key_prior_audit",
        ".decision_later_audit_set",
        ".key_later_audit_set",
    ],
)
def test_anchor_checker_rejects_omitted_branch_evidence(
    contract: dict[str, Any],
    missing_suffix: str,
) -> None:
    candidate = deepcopy(contract)
    program = _program(candidate, ANCHOR_BODY)
    assert _delete_node(program, missing_suffix)
    _reseal(candidate)
    with pytest.raises(AssertionError):
        _assert_anchor_evidence(program)


def test_rotation_producer_rejects_non_null_lifecycle_source_substitution(
    contract: dict[str, Any],
) -> None:
    candidate = deepcopy(contract)
    program = _program(candidate, ROTATION_BODY)
    lifecycle_insert = _node(program, ".lifecycle_insert")
    source_binding = next(
        binding
        for binding in lifecycle_insert["operands"]["bindings"]
        if binding["column"] == "source_position"
    )
    source_binding["value"] = {
        "op": "CONST",
        "type": "pg_catalog.bigint",
        "value": 0,
    }
    _reseal(candidate)

    with pytest.raises(AssertionError):
        _assert_rotation_parent_constraint(program)


@pytest.mark.parametrize(
    ("target_suffix", "mutation"),
    [
        (".decision_prior_audit_cardinality", "duplicate_match_allowed"),
        (".key_latest_prior_audit", "rollback_allowed"),
        (".baseline_anchor_cardinality", "missing_baseline_allowed"),
        (".checkpoint_lifecycle_timestamp", "timestamp_mismatch_allowed"),
        (".key_rotation_exact", "rotation_source_not_null"),
    ],
)
def test_anchor_checker_rejects_audit_chain_and_lifecycle_weakening(
    contract: dict[str, Any],
    target_suffix: str,
    mutation: str,
) -> None:
    candidate = deepcopy(contract)
    program = _program(candidate, ANCHOR_BODY)
    target = _node(program, target_suffix)
    predicate = target["operands"]["predicate"]
    if mutation == "duplicate_match_allowed":
        predicate["right"]["value"] = 2
    elif mutation == "rollback_allowed":
        predicate["right"]["value"] = 1
    elif mutation == "missing_baseline_allowed":
        predicate["right"]["value"] = 0
    elif mutation == "timestamp_mismatch_allowed":
        predicate["op"] = "NE"
    else:
        source_null = next(
            expression
            for expression in _expressions(predicate)
            if expression.get("op") == "IS_NULL"
            and _is_row_ref(
                expression.get("operand"),
                "anchor_lifecycle",
                LIFECYCLE,
                "source_position",
            )
        )
        source_null["op"] = "IS_NOT_NULL"
    _reseal(candidate)

    with pytest.raises(AssertionError):
        _assert_anchor_evidence(program)


@pytest.mark.parametrize(
    ("mutation", "target_suffix"),
    [
        ("revision_zero", ".revision_nonzero"),
        ("cardinality", ".lifecycle"),
        ("branch", ".lifecycle_is_key_rotation"),
        ("digest", ".rederive_rotation_integrity"),
        ("replay_field", ".stored_exact"),
    ],
)
def test_anchor_checker_rejects_substituted_revision_branch_digest_and_replay(
    contract: dict[str, Any],
    mutation: str,
    target_suffix: str,
) -> None:
    candidate = deepcopy(contract)
    program = _program(candidate, ANCHOR_BODY)
    target = _node(program, target_suffix)
    if mutation == "revision_zero":
        predicate = target["operands"]["predicate"]
        predicate["op"] = "GTE"
    elif mutation == "cardinality":
        target["operands"]["cardinality"] = "COMPLETE_SET"
    elif mutation == "branch":
        constant = next(
            expression
            for expression in _expressions(target["operands"]["condition"])
            if expression.get("op") == "CONST"
            and expression.get("value") == "KEY_ROTATION"
        )
        constant["value"] = "DECISION"
    elif mutation == "digest":
        digest = next(
            expression
            for expression in _expressions(target)
            if expression.get("op") == "CANONICAL_DIGEST"
        )
        digest["profile"] = ANCHOR_PROFILE
    else:
        stored_ref = next(
            expression
            for expression in _expressions(target)
            if expression.get("op") == "REF"
            and expression.get("kind") == "ROW_COLUMN"
            and expression.get("symbol") == "stored_anchor"
            and expression.get("column") == "created_at"
        )
        stored_ref["column"] = "anchor_digest"
        stored_ref["type"] = "emr4_context_fabric.digest_sha256"

    _reseal(candidate)
    with pytest.raises(AssertionError):
        _assert_anchor_evidence(program)
