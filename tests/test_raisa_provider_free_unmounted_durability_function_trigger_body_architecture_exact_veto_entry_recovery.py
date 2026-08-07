"""Focused R1/R2 assertions independent of generated-contract equality."""

from __future__ import annotations

import copy
from collections.abc import Iterator
from typing import Any

import pytest

from scripts import raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs as entry


F = entry.F
PG = entry.PG

REC19 = {
    "ELIGIBLE",
    "EXECUTION_DISABLED",
    "CHECKPOINT_LAG",
    "ACTIVE_PIN",
    "KEY_OVERLAP",
    "GRACE_PENDING",
    "AMBIGUOUS_CENSUS",
    "NO_NON_CONSUMED_GENERATION",
}


def walk_nodes(nodes: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    for node in nodes:
        yield node
        operands = node.get("operands", {})
        for branch in ("then", "else", "default", "nodes"):
            children = operands.get(branch)
            if isinstance(children, list):
                yield from walk_nodes(children)
        for arm in operands.get("arms", []):
            yield from walk_nodes(arm.get("nodes", []))


def nodes(program: dict[str, Any]) -> list[dict[str, Any]]:
    return list(walk_nodes(program["ast"]["nodes"]))


def walk_values(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def expressions(program: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        value
        for value in walk_values(program["ast"])
        if isinstance(value.get("op"), str)
    ]


def program_by_id(body_id: str) -> dict[str, Any]:
    return {program["id"]: program for program in entry.build_entry_programs()}[
        F + body_id
    ]


def remove_node(program: dict[str, Any], fragment: str) -> None:
    def remove(children: list[dict[str, Any]]) -> bool:
        for index, node in enumerate(children):
            if fragment in node.get("node_id", ""):
                children.pop(index)
                return True
            operands = node.get("operands", {})
            for branch in ("then", "else", "default", "nodes"):
                nested = operands.get(branch)
                if isinstance(nested, list) and remove(nested):
                    return True
            for arm in operands.get("arms", []):
                if remove(arm.get("nodes", [])):
                    return True
        return False

    assert remove(program["ast"]["nodes"]), fragment


def predicate_refs(node: dict[str, Any]) -> set[tuple[str, str, str]]:
    return {
        (str(value.get("kind")), str(value.get("relation")), str(value.get("column")))
        for value in walk_values(node.get("operands", {}).get("predicate"))
        if value.get("op") == "REF" and value.get("kind") in {"SOURCE_COLUMN", "ROW_COLUMN"}
    }


def assert_coordinator_recovery(program: dict[str, Any]) -> None:
    all_nodes = nodes(program)
    ids = {node["node_id"] for node in all_nodes}
    for fragment in {
        ".has_receipt",
        ".receipt_integrity",
        ".terminal_integrity",
        ".admission_ambiguous",
        ".has_conflict",
        ".missing_admission",
        ".gap",
        ".predecessor_matches",
        ".epoch_matches",
        ".key_membership_exact",
        ".anchor_fence_exact",
        ".dependent_state_exact",
        ".advance_diary_only_watermark",
    }:
        assert any(fragment in node_id for node_id in ids), fragment

    lock_pairs = {
        (node["operands"]["relation"], node["operands"]["ordinal"])
        for node in all_nodes
        if node["op"] == "LOCK_EXACT"
    }
    assert (entry.BARRIER, 1) in lock_pairs
    assert (entry.GENERATION, 2) in lock_pairs
    assert (entry.CHECKPOINT, 3) in lock_pairs
    assert {ordinal for _relation, ordinal in lock_pairs} == set(range(1, 10))
    assert (entry.RECEIPT, 4) in lock_pairs
    assert (entry.ADMISSION, 5) in lock_pairs
    assert (entry.LIFECYCLE, 4) in lock_pairs
    assert (entry.AUDIT, 5) in lock_pairs
    assert (entry.ANCHOR, 4) in lock_pairs
    assert (entry.FRAME, 6) in lock_pairs
    assert (entry.FRAME, 7) in lock_pairs
    assert (entry.WATERMARK, 8) in lock_pairs
    assert (entry.WATERMARK, 9) in lock_pairs

    effects = {
        (node["op"], node["operands"].get("relation"))
        for node in all_nodes
        if node["op"]
        in {"INSERT", "INSERT_OR_RELOAD_COMPARE", "UPDATE", "DELETE_SOURCE"}
    }
    for effect in {
        ("INSERT_OR_RELOAD_COMPARE", entry.RECEIPT),
        ("INSERT", entry.LIFECYCLE),
        ("INSERT", entry.AUDIT),
        ("UPDATE", entry.GENERATION),
        ("UPDATE", entry.CHECKPOINT),
        ("UPDATE", entry.FRAME),
        ("UPDATE", entry.WATERMARK),
        ("UPDATE", entry.OBLIGATION),
        ("INSERT_OR_RELOAD_COMPARE", entry.OBLIGATION),
    }:
        assert effect in effects

    kinds = {
        expression["value"]
        for expression in expressions(program)
        if expression.get("op") == "CONST"
        and expression.get("type") == F + "durability_transition_result_kind"
    }
    assert kinds == {
        "RECEIPT_APPLIED",
        "RECEIPT_REPLAYED",
        "REBASE_APPLIED",
        "TERMINAL_REPLAYED",
    }
    for expression in expressions(program):
        if expression.get("op") != "COMPOSITE_CONSTRUCT":
            continue
        if expression.get("type") != F + "durability_transition_result_v1":
            continue
        assert [field["field"] for field in expression["fields"]] == [
            "result_kind",
            "checkpoint_state",
            "source_position",
            "decision",
            "reason_code",
            "checkpoint_disposition",
            "lifecycle_revision",
            "evidence_digest",
        ]


def assert_retention_recovery(program: dict[str, Any]) -> None:
    all_nodes = nodes(program)
    generation_read = next(
        node
        for node in all_nodes
        if node["node_id"].endswith(".generations")
    )
    generation_predicates = list(
        walk_values(generation_read["operands"]["predicate"])
    )
    assert any(
        value.get("op") == "NE"
        and any(
            child.get("op") == "CONST"
            and child.get("type") == F + "generation_state"
            and child.get("value") == "CONSUMED"
            for child in walk_values(value)
        )
        for value in generation_predicates
    )

    base_reads = {
        entry.CHECKPOINT,
        entry.ANCHOR,
        entry.PIN,
        entry.KEY,
        entry.SOURCE,
        entry.RECEIPT,
        entry.AUDIT,
    }
    for node in all_nodes:
        if node["op"] != "SELECT_SET" or node["operands"]["relation"] not in base_reads:
            continue
        if ".mature_" in node["node_id"] or ".required_" in node["node_id"]:
            continue
        refs = predicate_refs(node)
        for column in ("practice_id", "source_contract_id", "stream_id"):
            assert any(
                kind == "SOURCE_COLUMN" and ref_column == column
                for kind, _relation, ref_column in refs
            ), node["node_id"]

    generation_loop = next(
        node for node in all_nodes if node["node_id"].endswith(".generation_census_proof")
    )
    assert generation_loop["op"] == "FOR_EACH"
    assert generation_loop["operands"]["set_symbol"] == "generation_set"
    assert generation_loop["operands"]["complete_set"] is True
    loop_relations = {
        node["operands"]["relation"]
        for node in walk_nodes(generation_loop["operands"]["nodes"])
        if node["op"] in {"SELECT_EXACT", "SELECT_SET"}
    }
    assert loop_relations == {entry.CHECKPOINT, entry.ANCHOR, entry.KEY, entry.PIN}
    for node in walk_nodes(generation_loop["operands"]["nodes"]):
        if node["op"] not in {"SELECT_EXACT", "SELECT_SET"}:
            continue
        refs = predicate_refs(node)
        for column in ("practice_id", "source_contract_id", "stream_id"):
            assert (
                "ROW_COLUMN",
                entry.GENERATION,
                column,
            ) in refs, node["node_id"]

    mins = [value for value in expressions(program) if value.get("op") == "MIN_FIELD"]
    assert len(mins) == 1
    assert mins[0]["source"]["symbol"] == "checkpoint_set"
    assert mins[0]["field"] == "last_contiguous_position"

    grace_columns = {
        child.get("column")
        for value in expressions(program)
        if value.get("op") == "TIMESTAMP_ADD_SECONDS"
        for child in walk_values(value.get("right"))
        if child.get("kind") == "ROW_COLUMN"
        and child.get("relation") == entry.POLICY
    }
    assert grace_columns == {
        "source_grace_seconds",
        "receipt_checkpoint_grace_seconds",
        "audit_grace_seconds",
        "key_overlap_seconds",
    }

    key_proof = next(
        node for node in all_nodes if node["node_id"].endswith(".overlapping_keys")
    )
    key_refs = predicate_refs(key_proof)
    assert ("SOURCE_COLUMN", entry.KEY, "interval_start") in key_refs
    assert ("SOURCE_COLUMN", entry.KEY, "interval_end") in key_refs
    assert any(
        value.get("kind") == "LOCAL"
        and value.get("symbol") == "slowest_checkpoint_position"
        for value in walk_values(key_proof["operands"]["predicate"])
    )

    reasons = {
        value.get("value")
        for value in expressions(program)
        if value.get("op") == "CONST"
        and value.get("type") == F + "source_retention_reason"
    }
    assert reasons == REC19


def test_coordinator_represents_every_state_and_required_effect() -> None:
    assert_coordinator_recovery(program_by_id("apply_durability_transition_v1"))


@pytest.mark.parametrize(
    "fragment",
    [
        ".epoch_matches",
        ".predecessor_matches",
        ".key_membership_exact",
        ".dependent_state_exact",
        ".advance_diary_only_watermark",
    ],
)
def test_coordinator_omitted_state_or_effect_fails_focused_assertions(
    fragment: str,
) -> None:
    program = copy.deepcopy(program_by_id("apply_durability_transition_v1"))
    remove_node(program, fragment)
    with pytest.raises(AssertionError):
        assert_coordinator_recovery(program)


@pytest.mark.parametrize(
    "body_id",
    ["evaluate_source_retention_v1", "purge_source_rows_v1"],
)
def test_retention_uses_complete_generation_census_grace_and_key_overlap(
    body_id: str,
) -> None:
    assert_retention_recovery(program_by_id(body_id))


def test_active_only_census_fails_focused_assertions() -> None:
    program = copy.deepcopy(program_by_id("evaluate_source_retention_v1"))
    generation_read = next(
        node for node in nodes(program) if node["node_id"].endswith(".generations")
    )
    generation_read["operands"]["predicate"] = entry.dsl.eq(
        entry._src(entry.GENERATION, "lifecycle_state"),
        entry.dsl.const(F + "generation_state", "ACTIVE"),
    )
    with pytest.raises(AssertionError):
        assert_retention_recovery(program)


def test_out_of_enum_retention_reason_fails_focused_assertions() -> None:
    program = copy.deepcopy(program_by_id("evaluate_source_retention_v1"))
    reason = next(
        value
        for value in expressions(program)
        if value.get("op") == "CONST"
        and value.get("type") == F + "source_retention_reason"
    )
    reason["value"] = "NOT_REC19"
    with pytest.raises(AssertionError):
        assert_retention_recovery(program)


def test_unscoped_related_census_set_fails_focused_assertions() -> None:
    program = copy.deepcopy(program_by_id("evaluate_source_retention_v1"))
    checkpoint_read = next(
        node for node in nodes(program) if node["node_id"].endswith(".checkpoints")
    )
    predicate = checkpoint_read["operands"]["predicate"]
    predicate["operands"] = [
        operand
        for operand in predicate["operands"]
        if not any(
            value.get("kind") == "SOURCE_COLUMN"
            and value.get("column") == "stream_id"
            for value in walk_values(operand)
        )
    ]
    with pytest.raises(AssertionError):
        assert_retention_recovery(program)


@pytest.mark.parametrize("fragment", [".mature_source_rows", ".overlapping_keys"])
def test_omitted_grace_or_key_proof_fails_focused_assertions(fragment: str) -> None:
    program = copy.deepcopy(program_by_id("evaluate_source_retention_v1"))
    remove_node(program, fragment)
    with pytest.raises((AssertionError, StopIteration)):
        assert_retention_recovery(program)
