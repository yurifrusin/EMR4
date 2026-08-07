"""Focused R5A/R5B/R5C body-program assertions and hostile mutations."""

from __future__ import annotations

import copy
from collections.abc import Iterator
from typing import Any

import pytest

from scripts import raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs as entry


F = entry.F
PG = entry.PG


def walk_values(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


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


def program(body_name: str) -> dict[str, Any]:
    return {
        candidate["id"]: candidate for candidate in entry.build_entry_programs()
    }[F + body_name]


def all_nodes(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    return list(walk_nodes(candidate["ast"]["nodes"]))


def node(candidate: dict[str, Any], suffix: str) -> dict[str, Any]:
    return next(
        item for item in all_nodes(candidate) if item["node_id"].endswith(suffix)
    )


def remove_node(candidate: dict[str, Any], suffix: str) -> None:
    def remove(children: list[dict[str, Any]]) -> bool:
        for index, child in enumerate(children):
            if child.get("node_id", "").endswith(suffix):
                children.pop(index)
                return True
            operands = child.get("operands", {})
            for branch in ("then", "else", "default", "nodes"):
                nested = operands.get(branch)
                if isinstance(nested, list) and remove(nested):
                    return True
            for arm in operands.get("arms", []):
                if remove(arm.get("nodes", [])):
                    return True
        return False

    assert remove(candidate["ast"]["nodes"]), suffix


def row_columns(value: Any, symbol: str) -> set[str]:
    return {
        str(item["column"])
        for item in walk_values(value)
        if item.get("op") == "REF"
        and item.get("kind") == "ROW_COLUMN"
        and item.get("symbol") == symbol
    }


def source_columns(value: Any, relation: str) -> set[str]:
    return {
        str(item["column"])
        for item in walk_values(value)
        if item.get("op") == "REF"
        and item.get("kind") == "SOURCE_COLUMN"
        and item.get("relation") == relation
    }


def count_equalities(value: Any) -> set[tuple[str, int]]:
    results: set[tuple[str, int]] = set()
    for expression in walk_values(value):
        if expression.get("op") != "EQ":
            continue
        sides = (expression.get("left"), expression.get("right"))
        for count_side, constant_side in (sides, tuple(reversed(sides))):
            if not isinstance(count_side, dict) or not isinstance(constant_side, dict):
                continue
            if count_side.get("op") != "COUNT" or constant_side.get("op") != "CONST":
                continue
            operand = count_side.get("operand", {})
            if operand.get("kind") == "LOCAL" and isinstance(
                constant_side.get("value"), int
            ):
                results.add((str(operand["symbol"]), constant_side["value"]))
    return results


def count_symbols(value: Any) -> set[str]:
    return {
        str(expression.get("operand", {}).get("symbol"))
        for expression in walk_values(value)
        if expression.get("op") == "COUNT"
        and expression.get("operand", {}).get("kind") == "LOCAL"
    }


def assert_receipt_replay(candidate: dict[str, Any]) -> None:
    conflict_route = node(candidate, ".has_conflict_before_receipt")
    assert conflict_route["op"] == "IF"
    assert count_equalities(conflict_route["operands"]["condition"]) == {
        ("conflict_set", 1)
    }
    assert any(
        child["node_id"].endswith(".lock_conflict")
        for child in walk_nodes(conflict_route["operands"]["then"])
    )

    replay_route = node(candidate, ".has_receipt")
    assert count_equalities(replay_route["operands"]["condition"]) == {
        ("receipt_set", 1),
        ("primary_set", 1),
        ("conflict_set", 0),
    }

    derivation = node(candidate, ".rederive_receipt_digest")["operands"][
        "expression"
    ]
    assert derivation["op"] == "CANONICAL_DIGEST"
    assert derivation["profile"] == F + "classified_receipt_digest_v1"
    assert len(derivation["operands"]) == len(entry.COORDS) + 3
    assert [
        operand.get("field") for operand in derivation["operands"][: len(entry.COORDS)]
    ] == entry.COORDS
    assert [
        (
            operand.get("symbol"),
            operand.get("relation"),
            operand.get("column"),
        )
        for operand in derivation["operands"][-3:]
    ] == [
        ("stored_receipt", entry.RECEIPT, "source_position"),
        ("replay_primary", entry.ADMISSION, "admission_digest"),
        ("stored_receipt", entry.RECEIPT, "lifecycle_revision"),
    ]

    comparison = node(candidate, ".receipt_digest_matches")["operands"][
        "predicate"
    ]
    assert comparison["op"] == "EQ"
    assert {
        (
            value.get("kind"),
            value.get("symbol"),
            value.get("relation"),
            value.get("column"),
        )
        for value in walk_values(comparison)
        if value.get("op") == "REF"
    } == {
        ("LOCAL", "rederived_receipt_digest", None, None),
        ("ROW_COLUMN", "stored_receipt", entry.RECEIPT, "receipt_digest"),
    }


def test_receipt_replay_requires_conflict_free_primary_and_rederived_digest() -> None:
    assert_receipt_replay(program("apply_durability_transition_v1"))


@pytest.mark.parametrize(
    "mutation",
    ["conflict_blind", "digest_profile", "digest_operand", "digest_compare"],
)
def test_hostile_receipt_replay_mutation_is_structurally_visible(
    mutation: str,
) -> None:
    candidate = copy.deepcopy(program("apply_durability_transition_v1"))
    if mutation == "conflict_blind":
        conflict_guard = node(candidate, ".has_conflict_before_receipt")[
            "operands"
        ]["condition"]
        conflict_guard["right"]["value"] = 0
        route = node(candidate, ".has_receipt")["operands"]["condition"]
        route["operands"] = [
            operand
            for operand in route["operands"]
            if ("conflict_set", 0) not in count_equalities(operand)
        ]
    elif mutation == "digest_profile":
        node(candidate, ".rederive_receipt_digest")["operands"]["expression"][
            "profile"
        ] = F + "substituted_digest_v1"
    elif mutation == "digest_operand":
        derivation = node(candidate, ".rederive_receipt_digest")["operands"][
            "expression"
        ]
        derivation["operands"][-3]["column"] = "created_at"
    else:
        remove_node(candidate, ".receipt_digest_matches")

    with pytest.raises((AssertionError, StopIteration)):
        assert_receipt_replay(candidate)


CONTROLLING_DIGESTS = {
    "policy_digest",
    "principal_digest",
    "binding_digest",
    "source_digest",
    "registry_digest",
    "impact_digest",
    "key_schedule_digest",
}


def assert_registration_replay(candidate: dict[str, Any]) -> None:
    head_set = node(candidate, ".head_set")
    assert head_set["op"] == "SELECT_SET"
    assert head_set["operands"]["relation"] == entry.HEAD
    assert {
        "practice_id",
        "source_contract_id",
        "stream_id",
        "stream_epoch",
    } <= source_columns(head_set["operands"]["predicate"], entry.HEAD)
    head_ambiguity = node(candidate, ".head_unambiguous")["operands"][
        "predicate"
    ]
    assert head_ambiguity["op"] == "LTE"
    assert count_symbols(head_ambiguity) == {"head_set"}
    assert head_ambiguity["right"] == {
        "op": "CONST",
        "type": PG + "bigint",
        "value": 1,
    }

    head_branch = node(candidate, ".create_or_use_head")
    assert head_branch["op"] == "IF"
    assert head_branch["operands"]["convergence"] == "REJOIN"
    assert count_equalities(head_branch["operands"]["condition"]) == {
        ("head_set", 0)
    }
    head_insert = next(
        child
        for child in walk_nodes(head_branch["operands"]["then"])
        if child["node_id"].endswith(".create_or_reload_head")
    )
    assert head_insert["op"] == "INSERT_OR_RELOAD_COMPARE"
    assert head_insert["operands"]["relation"] == entry.HEAD
    assert head_insert["operands"]["output_symbol"] == "head"
    head_bindings = {
        binding["column"]: binding["value"]
        for binding in head_insert["operands"]["bindings"]
    }
    assert head_bindings["stream_epoch"]["field"] == "stream_epoch"
    assert head_bindings["last_position"] == {
        "op": "CONST",
        "type": PG + "bigint",
        "value": 0,
    }
    head_lock = next(
        child
        for child in walk_nodes(head_branch["operands"]["else"])
        if child["node_id"].endswith(".lock_existing_head")
    )
    assert head_lock["op"] == "LOCK_EXACT"
    assert head_lock["operands"]["relation"] == entry.HEAD
    assert head_lock["operands"]["output_symbol"] == "head"

    reads = {
        suffix: node(candidate, suffix)
        for suffix in (
            ".existing",
            ".replay_checkpoint",
            ".replay_frame_set",
            ".replay_diary_frame",
            ".replay_waiting_frame",
            ".replay_watermark_set",
            ".replay_diary_watermark",
            ".replay_waiting_watermark",
            ".replay_initial_key",
            ".replay_baseline_anchor",
        )
    }
    assert reads[".existing"]["operands"]["relation"] == entry.GENERATION
    assert reads[".replay_checkpoint"]["operands"]["relation"] == entry.CHECKPOINT
    assert reads[".replay_frame_set"]["operands"]["relation"] == entry.FRAME
    assert reads[".replay_watermark_set"]["operands"]["relation"] == entry.WATERMARK
    assert reads[".replay_initial_key"]["operands"]["relation"] == entry.KEY
    assert reads[".replay_baseline_anchor"]["operands"]["relation"] == entry.ANCHOR
    assert reads[".replay_frame_set"]["operands"]["cardinality"] == "COMPLETE_SET"
    assert reads[".replay_watermark_set"]["operands"]["cardinality"] == "COMPLETE_SET"
    replay_effects = {
        child["op"]
        for child in walk_nodes(node(candidate, ".registered")["operands"]["then"])
        if child["op"]
        in {"INSERT", "INSERT_OR_RELOAD_COMPARE", "UPDATE", "DELETE_SOURCE"}
    }
    assert replay_effects == set()

    proof = node(candidate, ".replay_exact")["operands"]["predicate"]
    assert CONTROLLING_DIGESTS <= row_columns(proof, "existing_generation")
    assert {
        "lifecycle_state",
        "consumed_at",
        "terminal_reason",
    } <= row_columns(proof, "existing_generation")
    assert {
        "checkpoint_state",
        "last_contiguous_position",
        "last_observation_digest",
        "lifecycle_revision",
        "audit_head_digest",
        "checkpoint_integrity_digest",
    } <= row_columns(proof, "replay_checkpoint")
    assert {
        "frame_generation_id",
        "frame_type",
        "assembled_through_position",
    } <= row_columns(proof, "replay_diary_frame")
    assert {
        "frame_generation_id",
        "frame_type",
        "assembled_through_position",
    } <= row_columns(proof, "replay_waiting_frame")
    assert {"frame_type", "watermark_position"} <= row_columns(
        proof, "replay_diary_watermark"
    )
    assert {"frame_type", "watermark_position"} <= row_columns(
        proof, "replay_waiting_watermark"
    )
    assert {
        "interval_start",
        "interval_end",
        "key_id",
        "availability_attestation_digest",
    } <= row_columns(proof, "replay_initial_key")
    assert {
        "lifecycle_revision",
        "checkpoint_state",
        "last_contiguous_position",
        "last_observation_digest",
        "checkpoint_integrity_digest",
        "anchor_digest",
        *CONTROLLING_DIGESTS,
    } <= row_columns(proof, "replay_baseline_anchor")
    assert {"stream_epoch", "last_position"} <= row_columns(proof, "head")
    assert {("replay_frame_set", 2), ("replay_watermark_set", 2)} <= (
        count_equalities(proof)
    )


def test_registration_creates_or_uses_head_and_proves_complete_replay() -> None:
    assert_registration_replay(program("register_observer_generation_v1"))


@pytest.mark.parametrize(
    "suffix",
    [
        ".create_or_reload_head",
        ".existing",
        ".replay_checkpoint",
        ".replay_frame_set",
        ".replay_diary_frame",
        ".replay_waiting_frame",
        ".replay_watermark_set",
        ".replay_diary_watermark",
        ".replay_waiting_watermark",
        ".replay_initial_key",
        ".replay_baseline_anchor",
        ".replay_exact",
    ],
)
def test_missing_registration_baseline_family_is_structurally_visible(
    suffix: str,
) -> None:
    candidate = copy.deepcopy(program("register_observer_generation_v1"))
    remove_node(candidate, suffix)
    with pytest.raises((AssertionError, StopIteration)):
        assert_registration_replay(candidate)


@pytest.mark.parametrize(
    ("symbol", "column", "substitute"),
    [
        ("existing_generation", "policy_digest", "principal_digest"),
        ("replay_checkpoint", "audit_head_digest", "checkpoint_state"),
        ("replay_diary_frame", "frame_type", "created_at"),
        ("replay_diary_watermark", "watermark_position", "updated_at"),
        ("replay_initial_key", "availability_attestation_digest", "key_id"),
        ("replay_baseline_anchor", "anchor_digest", "created_at"),
        ("head", "stream_epoch", "updated_at"),
    ],
)
def test_substituted_registration_baseline_proof_is_structurally_visible(
    symbol: str,
    column: str,
    substitute: str,
) -> None:
    candidate = copy.deepcopy(program("register_observer_generation_v1"))
    proof = node(candidate, ".replay_exact")["operands"]["predicate"]
    reference = next(
        value
        for value in walk_values(proof)
        if value.get("op") == "REF"
        and value.get("kind") == "ROW_COLUMN"
        and value.get("symbol") == symbol
        and value.get("column") == column
    )
    reference["column"] = substitute
    with pytest.raises(AssertionError):
        assert_registration_replay(candidate)


FULL_IDENTITY = [(column, column) for column in entry.COORDS]
PIN_IDENTITY = [
    (column, column)
    for column in entry.COORDS
    if column != "stream_epoch"
]


def set_contains_expression(read: dict[str, Any]) -> dict[str, Any]:
    expressions = [
        value
        for value in walk_values(read["operands"]["predicate"])
        if value.get("op") == "SET_CONTAINS_KEY"
    ]
    assert len(expressions) == 1
    return expressions[0]


def assert_set_contains(
    read: dict[str, Any],
    relation: str,
    key_pairs: list[tuple[str, str]],
) -> None:
    expression = set_contains_expression(read)
    assert expression == {
        "op": "SET_CONTAINS_KEY",
        "set": {
            "kind": "LOCAL",
            "symbol": "generation_set",
            "type": entry.GENERATION + "[]",
        },
        "source_relation": relation,
        "key_pairs": [
            {"source_column": source, "set_column": required}
            for source, required in key_pairs
        ],
        "type": PG + "boolean",
    }


def assert_retention_identity(candidate: dict[str, Any]) -> None:
    exact_reads = {
        ".checkpoints": (entry.CHECKPOINT, FULL_IDENTITY),
        ".anchors": (entry.ANCHOR, FULL_IDENTITY),
        ".pins": (entry.PIN, PIN_IDENTITY),
        ".keys": (entry.KEY, FULL_IDENTITY),
        ".receipts": (entry.RECEIPT, FULL_IDENTITY),
        ".audits": (entry.AUDIT, FULL_IDENTITY),
        ".mature_checkpoints": (entry.CHECKPOINT, FULL_IDENTITY),
        ".mature_receipts": (entry.RECEIPT, FULL_IDENTITY),
        ".mature_audits": (entry.AUDIT, FULL_IDENTITY),
        ".overlapping_keys": (entry.KEY, FULL_IDENTITY),
    }
    for suffix, (relation, keys) in exact_reads.items():
        assert_set_contains(node(candidate, suffix), relation, keys)

    coverage_node = node(candidate, ".key_overlap_coverage")
    coverage = coverage_node["operands"]["expression"]
    assert coverage == {
        "op": "SET_COVERS_KEYS",
        "required": {
            "kind": "LOCAL",
            "symbol": "generation_set",
            "type": entry.GENERATION + "[]",
        },
        "evidence": {
            "kind": "LOCAL",
            "symbol": "overlapping_key_set",
            "type": entry.KEY + "[]",
        },
        "key_pairs": [
            {"required_column": required, "evidence_column": evidence}
            for required, evidence in FULL_IDENTITY
        ],
        "type": PG + "boolean",
    }

    assert not any(
        expression.get("op") == "EQ"
        and count_symbols(expression)
        == {"generation_set", "overlapping_key_set"}
        for expression in walk_values(candidate["ast"])
    )
    coverage_consumers = [
        value
        for value in walk_values(candidate["ast"])
        if value.get("op") == "REF"
        and value.get("kind") == "LOCAL"
        and value.get("symbol") == "key_overlap_covered"
    ]
    expected_consumers = (
        2 if candidate["id"].endswith("evaluate_source_retention_v1") else 1
    )
    assert len(coverage_consumers) >= expected_consumers


@pytest.mark.parametrize(
    "body_name", ["evaluate_source_retention_v1", "purge_source_rows_v1"]
)
def test_retention_uses_identity_joined_sets_and_per_generation_key_coverage(
    body_name: str,
) -> None:
    assert_retention_identity(program(body_name))


@pytest.mark.parametrize(
    ("mutation", "suffix"),
    [
        ("contains_missing_coordinate", ".checkpoints"),
        ("contains_wrong_relation", ".pins"),
        ("coverage_missing_coordinate", ".key_overlap_coverage"),
        ("coverage_count_substitution", ".key_overlap_coverage"),
    ],
)
def test_hostile_retention_scope_or_coverage_mutation_is_structurally_visible(
    mutation: str,
    suffix: str,
) -> None:
    candidate = copy.deepcopy(program("evaluate_source_retention_v1"))
    target = node(candidate, suffix)
    if mutation == "contains_missing_coordinate":
        set_contains_expression(target)["key_pairs"].pop()
    elif mutation == "contains_wrong_relation":
        set_contains_expression(target)["source_relation"] = entry.KEY
    elif mutation == "coverage_missing_coordinate":
        target["operands"]["expression"]["key_pairs"].pop()
    else:
        target["operands"]["expression"] = entry.dsl.eq(
            entry._count("overlapping_key_set", entry.KEY),
            entry._count("generation_set", entry.GENERATION),
        )

    with pytest.raises((AssertionError, StopIteration)):
        assert_retention_identity(candidate)
