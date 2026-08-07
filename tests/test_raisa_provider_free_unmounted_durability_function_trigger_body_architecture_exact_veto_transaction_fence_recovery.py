"""Operand-level R3 tests for the current-transaction appointment fence."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from scripts import (
    raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs
    as triggers,
)


def _walk(value: Any) -> Iterator[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _program(name: str) -> dict[str, Any]:
    return next(
        program
        for program in triggers.build_trigger_programs()
        if program["id"] == triggers.FABRIC + name
    )


def _node(program: Mapping[str, Any], suffix: str) -> Mapping[str, Any]:
    return next(
        item
        for item in _walk(program["ast"])
        if item.get("node_id") == program["id"] + suffix
    )


def _ref(
    kind: str,
    relation: str,
    column: str,
    *,
    symbol: str | None = None,
) -> tuple[str, str, str, str | None]:
    return kind, relation, column, symbol


def _ref_value(value: Any) -> tuple[str, str, str, str | None] | None:
    if not isinstance(value, Mapping) or value.get("op") != "REF":
        return None
    kind = value.get("kind")
    relation = value.get("relation")
    column = value.get("column")
    if not all(isinstance(item, str) for item in (kind, relation, column)):
        return None
    symbol = value.get("symbol")
    return kind, relation, column, symbol if isinstance(symbol, str) else None


def _has_equality(
    expression: Mapping[str, Any],
    left: tuple[str, str, str, str | None],
    right: tuple[str, str, str, str | None],
) -> bool:
    for item in _walk(expression):
        if item.get("op") != "EQ":
            continue
        pair = (_ref_value(item.get("left")), _ref_value(item.get("right")))
        if pair in {(left, right), (right, left)}:
            return True
    return False


def _has_constant_equality(
    expression: Mapping[str, Any],
    ref: tuple[str, str, str, str | None],
    value: object,
) -> bool:
    for item in _walk(expression):
        if item.get("op") != "EQ":
            continue
        sides = ((item.get("left"), item.get("right")), (item.get("right"), item.get("left")))
        if any(
            _ref_value(reference) == ref
            and isinstance(constant, Mapping)
            and constant.get("op") == "CONST"
            and constant.get("value") == value
            for reference, constant in sides
        ):
            return True
    return False


def _has_current_xid(
    expression: Mapping[str, Any], relation: str
) -> bool:
    for item in _walk(expression):
        if item.get("op") != "EQ":
            continue
        sides = ((item.get("left"), item.get("right")), (item.get("right"), item.get("left")))
        if any(
            _ref_value(reference) == _ref("SOURCE_COLUMN", relation, "xmin")
            and isinstance(current, Mapping)
            and current.get("op") == "CURRENT_XID32"
            for reference, current in sides
        ):
            return True
    return False


def test_non_temporal_event_and_alias_sets_are_exact_current_xid_effects() -> None:
    program = _program("cf_fence_appointment_update_v1")
    event = _node(program, ".update.absence.events")["operands"]
    alias = _node(program, ".update.absence.aliases")["operands"]

    assert event["relation"] == triggers.EVENT
    assert event["cardinality"] == "COMPLETE_SET"
    assert _has_current_xid(event["predicate"], triggers.EVENT)
    assert _has_equality(
        event["predicate"],
        _ref("SOURCE_COLUMN", triggers.EVENT, "appointment_id"),
        _ref("TRIGGER_COLUMN", triggers.APPOINTMENT, "id"),
    )
    assert _has_constant_equality(
        event["predicate"],
        _ref("SOURCE_COLUMN", triggers.EVENT, "event_type"),
        triggers.EVENT_TYPE,
    )
    assert _has_constant_equality(
        event["predicate"],
        _ref("SOURCE_COLUMN", triggers.EVENT, "schema_version"),
        triggers.EVENT_SCHEMA,
    )

    assert alias["relation"] == triggers.ALIAS
    assert alias["cardinality"] == "COMPLETE_SET"
    assert _has_current_xid(alias["predicate"], triggers.ALIAS)
    assert _has_equality(
        alias["predicate"],
        _ref("SOURCE_COLUMN", triggers.ALIAS, "product_appointment_uuid"),
        _ref("TRIGGER_COLUMN", triggers.APPOINTMENT, "id"),
    )
    assert _has_equality(
        alias["predicate"],
        _ref("SOURCE_COLUMN", triggers.ALIAS, "stream_id"),
        _ref("ROW_COLUMN", triggers.BINDING, "stream_id", symbol="binding"),
    )
    assert _has_constant_equality(
        alias["predicate"],
        _ref("SOURCE_COLUMN", triggers.ALIAS, "source_contract_id"),
        triggers.SOURCE_CONTRACT,
    )


def test_current_outbox_is_joined_to_exact_event_alias_revision_and_transaction() -> None:
    program = _program("cf_fence_appointment_update_v1")
    exact_alias = _node(program, ".update.absence.exact-alias")["operands"]
    outbox = _node(program, ".update.absence.current-outbox")["operands"]

    assert not _has_current_xid(exact_alias["predicate"], triggers.ALIAS)
    assert _has_equality(
        exact_alias["predicate"],
        _ref("SOURCE_COLUMN", triggers.ALIAS, "product_appointment_uuid"),
        _ref("TRIGGER_COLUMN", triggers.APPOINTMENT, "id"),
    )
    assert _has_current_xid(outbox["predicate"], triggers.OUTBOX)
    for outbox_column, relation, column, symbol in (
        ("raw_event_uuid", triggers.EVENT, "id", "current_event"),
        (
            "opaque_aggregate_alias",
            triggers.ALIAS,
            "opaque_aggregate_alias",
            "appointment_alias",
        ),
        (
            "aggregate_revision",
            triggers.EVENT,
            "aggregate_revision",
            "current_event",
        ),
    ):
        assert _has_equality(
            outbox["predicate"],
            _ref("SOURCE_COLUMN", triggers.OUTBOX, outbox_column),
            _ref("ROW_COLUMN", relation, column, symbol=symbol),
        )
    assert _has_constant_equality(
        outbox["predicate"],
        _ref("SOURCE_COLUMN", triggers.OUTBOX, "source_contract_id"),
        triggers.SOURCE_CONTRACT,
    )
    predecessor = next(
        item
        for item in _walk(outbox["predicate"])
        if item.get("op") == "EQ"
        and _ref_value(item.get("left"))
        == _ref("SOURCE_COLUMN", triggers.OUTBOX, "predecessor_position")
    )
    assert predecessor["right"]["op"] == "ADD"
    assert _ref_value(predecessor["right"]["left"]) == _ref(
        "SOURCE_COLUMN", triggers.OUTBOX, "transaction_position"
    )
    assert predecessor["right"]["right"]["value"] == -1


def test_head_effect_is_current_xid_and_bound_to_the_exact_outbox_position() -> None:
    program = _program("cf_fence_appointment_update_v1")
    head = _node(program, ".update.absence.current-head")["operands"]

    assert _has_current_xid(head["predicate"], triggers.HEAD)
    assert _has_equality(
        head["predicate"],
        _ref("SOURCE_COLUMN", triggers.HEAD, "stream_epoch"),
        _ref(
            "ROW_COLUMN",
            triggers.OUTBOX,
            "stream_epoch",
            symbol="current_outbox",
        ),
    )
    assert _has_equality(
        head["predicate"],
        _ref("SOURCE_COLUMN", triggers.HEAD, "last_position"),
        _ref(
            "ROW_COLUMN",
            triggers.OUTBOX,
            "transaction_position",
            symbol="current_outbox",
        ),
    )
    assert any(
        item.get("op") == "TRANSACTION_TIMESTAMP"
        for item in _walk(head["predicate"])
    )


def test_non_temporal_branch_ignores_unrelated_rows_and_preserves_trigger_rules() -> None:
    program = _program("cf_fence_appointment_update_v1")
    event_count = _node(program, ".update.absence.event-count")
    no_event_ids = {
        item.get("node_id") for item in _walk(event_count["operands"]["then"])
    }
    current_effect_ids = {
        item.get("node_id") for item in _walk(event_count["operands"]["else"])
    }

    assert program["id"] + ".update.absence.aliases" in no_event_ids
    assert program["id"] + ".update.absence.return" in no_event_ids
    assert program["id"] + ".update.absence.current-outbox" not in no_event_ids
    assert program["id"] + ".update.absence.current-outbox" in current_effect_ids
    assert program["id"] + ".update.absence.current-head" in current_effect_ids
    assert program["id"] + ".update.absence.current-effect" in current_effect_ids
    assert _node(program, ".update.second")["op"] == "ASSERT"

    trigger_refs = [
        item
        for item in _walk(program["ast"])
        if item.get("kind") == "TRIGGER_COLUMN"
    ]
    assert trigger_refs
    assert {item["relation"] for item in trigger_refs} == {triggers.APPOINTMENT}
    terminals = {
        item.get("op")
        for item in _walk(program["ast"])
        if item.get("op") in {"RETURN_NEW", "RETURN_OLD", "RETURN_NULL", "RAISE"}
    }
    assert terminals == {"RETURN_NULL", "RAISE"}


def test_head_guard_keeps_legal_old_new_position_change_proof() -> None:
    program = _program("cf_guard_stream_head_v1")
    proof = _node(program, ".update.proof")["operands"]["predicate"]

    assert _has_equality(
        proof,
        _ref("TRIGGER_COLUMN", triggers.HEAD, "last_position"),
        _ref("TRIGGER_COLUMN", triggers.HEAD, "last_position"),
    ) is False
    position_eq = next(
        item
        for item in _walk(proof)
        if item.get("op") == "EQ"
        and _ref_value(item.get("left"))
        == ("TRIGGER_COLUMN", triggers.HEAD, "last_position", None)
        and isinstance(item.get("right"), Mapping)
        and item["right"].get("op") == "ADD"
    )
    assert position_eq["left"]["image"] == "NEW"
    assert position_eq["right"]["left"]["image"] == "OLD"
    assert position_eq["right"]["right"]["value"] == 1
