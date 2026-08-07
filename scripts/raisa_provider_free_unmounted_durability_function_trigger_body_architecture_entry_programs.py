"""Typed-IR programs for the eight non-producer durability entry points.

The module is deliberately data-only: it composes the closed builder DSL and
does not render SQL, contact PostgreSQL, or inspect product/runtime state.
"""

from __future__ import annotations

from typing import Any

from scripts import raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder as dsl


F = dsl.FABRIC
PG = dsl.PG

GEN_LOC = F + "generation_locator_v1"
ADMISSION_LOC = F + "admission_locator_v1"
PACKET = F + "proofread_packet_v1"
REGISTRATION = F + "generation_registration_v1"
KEY_INPUT = F + "future_key_interval_v1"
SCOPE = F + "practice_source_stream_v1"

SOURCE = F + "diary_context_observation_outbox_v1"
ADMISSION = F + "context_proofread_observation_admission"
BARRIER = F + "context_generation_registry_barrier"
GENERATION = F + "context_observer_generation"
CHECKPOINT = F + "context_durability_checkpoint"
ANCHOR = F + "context_recovery_anchor"
RECEIPT = F + "context_classified_observation_receipt"
FRAME = F + "context_frame_generation"
WATERMARK = F + "context_invalidation_watermark"
OBLIGATION = F + "context_reassembly_obligation"
LIFECYCLE = F + "context_durability_lifecycle"
AUDIT = F + "context_durability_audit"
KEY = F + "context_observation_key_interval"
PIN = F + "context_recovery_pin"
POLICY = F + "context_retention_policy"
HEAD = F + "context_observation_stream_head"
BINDING = F + "context_service_practice_binding"

COORDS = [
    "practice_id",
    "source_contract_id",
    "stream_id",
    "stream_epoch",
    "observer_id",
    "observer_generation",
]

COLUMNS: dict[str, list[str]] = {
    BINDING: ["database_login", "logical_capability", "practice_id", "source_contract_id", "binding_revision", "credential_epoch", "active_from", "active_until", "stream_id"],
    SOURCE: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "transaction_position", "predecessor_position", "raw_event_uuid", "opaque_aggregate_alias", "aggregate_revision", "source_contract_digest", "transaction_authored_at"],
    ADMISSION: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "source_position", "entry_kind", "observer_binding_revision", "key_id", "source_membership_digest", "admission_digest", "observation_digest", "decision", "reason_code", "affected_frame_mask", "checkpoint_disposition", "attempted_admission_digest", "conflict_reason", "admitted_at"],
    BARRIER: ["practice_id", "source_contract_id", "stream_id", "barrier_revision", "updated_at"],
    GENERATION: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "lifecycle_state", "policy_digest", "principal_digest", "binding_digest", "source_digest", "registry_digest", "impact_digest", "key_schedule_digest", "created_at", "consumed_at", "terminal_reason"],
    CHECKPOINT: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "checkpoint_state", "last_contiguous_position", "last_observation_digest", "lifecycle_revision", "audit_head_digest", "checkpoint_integrity_digest", "updated_at"],
    ANCHOR: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "lifecycle_revision", "checkpoint_state", "last_contiguous_position", "last_observation_digest", "policy_digest", "principal_digest", "binding_digest", "source_digest", "registry_digest", "impact_digest", "key_schedule_digest", "checkpoint_integrity_digest", "anchor_digest", "created_at"],
    RECEIPT: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "source_position", "admission_entry_kind", "observation_digest", "decision", "reason_code", "affected_frame_mask", "checkpoint_disposition", "lifecycle_revision", "receipt_digest", "created_at"],
    FRAME: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "frame_generation_id", "frame_type", "assembled_through_position", "lifecycle_state", "created_at", "retired_at"],
    WATERMARK: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "frame_type", "watermark_position", "updated_at"],
    OBLIGATION: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "frame_generation_id", "earliest_position", "latest_position", "rolling_cause_digest", "count_bucket", "obligation_state", "created_at", "updated_at"],
    LIFECYCLE: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "lifecycle_revision", "entry_kind", "source_position", "key_interval_start", "key_interval_end", "prior_lifecycle_digest", "lifecycle_digest", "created_at"],
    AUDIT: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "lifecycle_revision", "decision", "reason_code", "affected_frame_mask", "prior_audit_digest", "audit_head_digest", "created_at"],
    KEY: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "observer_id", "observer_generation", "interval_start", "interval_end", "key_id", "availability_attestation_digest", "created_at"],
    PIN: ["practice_id", "source_contract_id", "pin_id", "retention_family", "stream_id", "observer_id", "observer_generation", "position_or_revision", "reason_code", "pin_state", "created_at", "released_at"],
    POLICY: ["practice_id", "source_contract_id", "policy_revision", "source_grace_seconds", "receipt_checkpoint_grace_seconds", "audit_grace_seconds", "key_overlap_seconds", "retention_execution_enabled", "effective_at", "stream_id"],
    HEAD: ["practice_id", "source_contract_id", "stream_id", "stream_epoch", "last_position", "updated_at"],
}

TYPES: dict[str, dict[str, str]] = {
    relation: {
        column: type_name
        for column, type_name in zip(columns, type_names, strict=True)
    }
    for relation, columns, type_names in [
        (BINDING, COLUMNS[BINDING], [PG+"name", F+"logical_capability", PG+"uuid", F+"source_contract_code", PG+"bigint", PG+"bigint", PG+"timestamptz", PG+"timestamptz", PG+"uuid"]),
        (SOURCE, COLUMNS[SOURCE], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"bigint", PG+"bigint", PG+"uuid", PG+"uuid", PG+"bigint", F+"digest_sha256", PG+"timestamptz"]),
        (ADMISSION, COLUMNS[ADMISSION], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"bigint", F+"admission_entry_kind", PG+"bigint", F+"key_id", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"observation_decision", F+"observation_reason", F+"frame_mask", F+"checkpoint_disposition", F+"digest_sha256", F+"admission_conflict_reason", PG+"timestamptz"]),
        (BARRIER, COLUMNS[BARRIER], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"timestamptz"]),
        (GENERATION, COLUMNS[GENERATION], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", F+"generation_state", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", PG+"timestamptz", PG+"timestamptz", F+"generation_terminal_reason"]),
        (CHECKPOINT, COLUMNS[CHECKPOINT], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", F+"checkpoint_state", PG+"bigint", F+"digest_sha256", PG+"bigint", F+"digest_sha256", F+"digest_sha256", PG+"timestamptz"]),
        (ANCHOR, COLUMNS[ANCHOR], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"bigint", F+"checkpoint_state", PG+"bigint", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", F+"digest_sha256", PG+"timestamptz"]),
        (RECEIPT, COLUMNS[RECEIPT], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"bigint", F+"admission_entry_kind", F+"digest_sha256", F+"observation_decision", F+"observation_reason", F+"frame_mask", F+"checkpoint_disposition", PG+"bigint", F+"digest_sha256", PG+"timestamptz"]),
        (FRAME, COLUMNS[FRAME], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"uuid", F+"frame_type", PG+"bigint", F+"frame_lifecycle", PG+"timestamptz", PG+"timestamptz"]),
        (WATERMARK, COLUMNS[WATERMARK], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", F+"frame_type", PG+"bigint", PG+"timestamptz"]),
        (OBLIGATION, COLUMNS[OBLIGATION], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"bigint", F+"digest_sha256", F+"obligation_count_bucket", F+"obligation_state", PG+"timestamptz", PG+"timestamptz"]),
        (LIFECYCLE, COLUMNS[LIFECYCLE], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"bigint", F+"lifecycle_entry_kind", PG+"bigint", PG+"bigint", PG+"bigint", F+"digest_sha256", F+"digest_sha256", PG+"timestamptz"]),
        (AUDIT, COLUMNS[AUDIT], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"bigint", F+"observation_decision", F+"observation_reason", F+"frame_mask", F+"digest_sha256", F+"digest_sha256", PG+"timestamptz"]),
        (KEY, COLUMNS[KEY], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"uuid", PG+"bigint", PG+"bigint", PG+"bigint", F+"key_id", F+"digest_sha256", PG+"timestamptz"]),
        (PIN, COLUMNS[PIN], [PG+"uuid", F+"source_contract_code", PG+"uuid", F+"retention_family", PG+"uuid", PG+"uuid", PG+"bigint", PG+"bigint", F+"recovery_pin_reason", F+"recovery_pin_state", PG+"timestamptz", PG+"timestamptz"]),
        (POLICY, COLUMNS[POLICY], [PG+"uuid", F+"source_contract_code", PG+"bigint", PG+"bigint", PG+"bigint", PG+"bigint", PG+"bigint", PG+"boolean", PG+"timestamptz", PG+"uuid"]),
        (HEAD, COLUMNS[HEAD], [PG+"uuid", F+"source_contract_code", PG+"uuid", PG+"bigint", PG+"bigint", PG+"timestamptz"]),
    ]
}


def _col(symbol: str, relation: str, column: str) -> dict[str, Any]:
    return dsl.column_ref(symbol, relation, column, TYPES[relation][column])


def _src(relation: str, column: str) -> dict[str, Any]:
    return dsl.source_column(relation, column, TYPES[relation][column])


def _field(value: dict[str, Any], name: str, type_name: str) -> dict[str, Any]:
    return dsl.field(value, name, type_name)


def _loc(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "practice_id": _field(value, "practice_id", PG + "uuid"),
        "source_contract_id": _field(value, "source_contract_id", F + "source_contract_code"),
        "stream_id": _field(value, "stream_id", PG + "uuid"),
        "stream_epoch": _field(value, "stream_epoch", PG + "bigint"),
        "observer_id": _field(value, "observer_id", PG + "uuid"),
        "observer_generation": _field(value, "observer_generation", PG + "bigint"),
    }


def _scope(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "practice_id": _field(value, "practice_id", PG + "uuid"),
        "source_contract_id": _field(value, "source_contract_id", F + "source_contract_code"),
        "stream_id": _field(value, "stream_id", PG + "uuid"),
    }


def _predicate(relation: str, values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return dsl.all_of(*(dsl.eq(_src(relation, key), value) for key, value in values.items()))


def _row_predicate(symbol: str, relation: str, values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return dsl.all_of(*(dsl.eq(_col(symbol, relation, key), value) for key, value in values.items()))


def _count(symbol: str, relation: str) -> dict[str, Any]:
    return dsl.unary("COUNT", dsl.local_ref(symbol, relation + "[]"), PG + "bigint")


def _if(node_id: str, condition: dict[str, Any], then: list[dict[str, Any]], otherwise: list[dict[str, Any]]) -> dict[str, Any]:
    return dsl.node(node_id, "IF", condition=condition, then=then, **{"else": otherwise}, convergence="ALL_TERMINAL")


def _if_rejoin(
    node_id: str,
    condition: dict[str, Any],
    then: list[dict[str, Any]],
    otherwise: list[dict[str, Any]],
) -> dict[str, Any]:
    return dsl.node(
        node_id,
        "IF",
        condition=condition,
        then=then,
        **{"else": otherwise},
        convergence="REJOIN",
    )


def _composite(type_name: str, fields: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    return {"op": "COMPOSITE_CONSTRUCT", "type": type_name, "fields": [{"field": name, "value": value} for name, value in fields]}


def _retry_or_return(body_id: str, suffix: str, source_symbol: str, type_name: str, *, composite: bool = False) -> dict[str, Any]:
    terminal = dsl.node(
        f"{body_id}.return.{suffix}",
        "RETURN_COMPOSITE" if composite else "RETURN_ROW",
        source_symbol=source_symbol,
        type=type_name,
        cardinality="EXACTLY_ONE",
    )
    return _if(
        f"{body_id}.retry_or_return.{suffix}",
        dsl.const(PG + "boolean", False),
        [dsl.propagate_retryable(f"{body_id}.retry.{suffix}")],
        [terminal],
    )


def _winner(relation: str, bindings: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    return dsl.all_of(*(dsl.eq(_src(relation, name), value) for name, value in bindings))


def _insert_reload(node_id: str, relation: str, bindings: list[tuple[str, dict[str, Any]]], output_symbol: str, key_columns: list[str]) -> dict[str, Any]:
    return dsl.insert_node(
        node_id,
        relation=relation,
        bindings=bindings,
        output_symbol=output_symbol,
        returning_columns=COLUMNS[relation],
        reload_key=key_columns,
        winner_predicate=_winner(relation, bindings),
    )


def _symbols(inputs: list[tuple[str, str]], locals_: list[tuple[str, str]]) -> list[dict[str, Any]]:
    return [
        *(dsl.symbol(name, type_name, "INPUT") for name, type_name in inputs),
        *(dsl.node_symbol(name, type_name) for name, type_name in locals_),
    ]


def _binding(body_id: str, capability: str, values: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return dsl.binding_fragment(
        body_id,
        capability,
        practice=values["practice_id"],
        stream=values["stream_id"],
    )


def _isolation(body_id: str, level: str) -> dict[str, Any]:
    return dsl.node(f"{body_id}.isolation", "ASSERT_ISOLATION", required=level)


def _admission_bindings(loc: dict[str, dict[str, Any]], position: dict[str, Any], packet: dict[str, Any], binding_revision: dict[str, Any], *, kind: str, attempted: dict[str, Any], conflict: str | None) -> list[tuple[str, dict[str, Any]]]:
    values: list[tuple[str, dict[str, Any]]] = [(name, loc[name]) for name in COORDS]
    values.extend(
        [
            ("source_position", position),
            ("entry_kind", dsl.const(F + "admission_entry_kind", kind)),
            ("observer_binding_revision", binding_revision),
            ("key_id", _field(packet, "key_id", F + "key_id")),
            ("source_membership_digest", _field(packet, "source_membership_digest", F + "digest_sha256")),
            ("admission_digest", attempted),
            ("observation_digest", _field(packet, "observation_digest", F + "digest_sha256")),
            ("decision", _field(packet, "decision", F + "observation_decision")),
            ("reason_code", _field(packet, "reason_code", F + "observation_reason")),
            ("affected_frame_mask", _field(packet, "affected_frame_mask", F + "frame_mask")),
            ("checkpoint_disposition", _field(packet, "checkpoint_disposition", F + "checkpoint_disposition")),
            ("attempted_admission_digest", attempted),
            ("conflict_reason", dsl.const(F + "admission_conflict_reason", conflict)),
            ("admitted_at", dsl.transaction_timestamp()),
        ]
    )
    return values


def build_admission_body() -> dict[str, Any]:
    body_id = F + "admit_proofread_observation_v1"
    locator = dsl.input_ref("generation_locator", GEN_LOC)
    packet = dsl.input_ref("proofread_packet", PACKET)
    position = dsl.input_ref("source_position", PG + "bigint")
    loc = _loc(locator)
    binding_nodes, binding_symbols = _binding(body_id, "OBSERVER", loc)
    coordinate = {**loc, "source_position": position}
    attempted = dsl.digest(
        F + "admission_digest_v1",
        [*loc.values(), position, *(_field(packet, name, type_name) for name, type_name in [
            ("observation_digest", F+"digest_sha256"), ("decision", F+"observation_decision"),
            ("reason_code", F+"observation_reason"), ("affected_frame_mask", F+"frame_mask"),
            ("checkpoint_disposition", F+"checkpoint_disposition"), ("key_id", F+"key_id"),
            ("source_membership_digest", F+"digest_sha256")])],
    )
    primary_pred = dsl.all_of(_predicate(ADMISSION, coordinate), dsl.eq(_src(ADMISSION, "entry_kind"), dsl.const(F+"admission_entry_kind", "PRIMARY")))
    conflict_pred = dsl.all_of(_predicate(ADMISSION, coordinate), dsl.eq(_src(ADMISSION, "entry_kind"), dsl.const(F+"admission_entry_kind", "CONFLICT")))
    binding_revision = _col("binding", BINDING, "binding_revision")
    primary_bindings = _admission_bindings(loc, position, packet, binding_revision, kind="PRIMARY", attempted=attempted, conflict=None)
    mismatch_bindings = _admission_bindings(loc, position, packet, binding_revision, kind="CONFLICT", attempted=attempted, conflict="POSITION_DIGEST_MISMATCH")
    reuse_bindings = _admission_bindings(loc, position, packet, binding_revision, kind="CONFLICT", attempted=attempted, conflict="OBSERVATION_DIGEST_REUSE")

    retained_primary = [
        dsl.select_node(f"{body_id}.retained_primary", relation=ADMISSION, columns=COLUMNS[ADMISSION], predicate=primary_pred, cardinality="EXACTLY_ONE", output_symbol="retained_primary", order_by=COORDS+["source_position", "entry_kind"]),
        _if(
            f"{body_id}.primary_matches",
            dsl.eq(_col("retained_primary", ADMISSION, "admission_digest"), attempted),
            [_retry_or_return(body_id, "primary_replay", "retained_primary", ADMISSION)],
            [_insert_reload(f"{body_id}.insert_mismatch", ADMISSION, mismatch_bindings, "mismatch_conflict", COORDS+["source_position", "entry_kind"]), _retry_or_return(body_id, "mismatch_conflict", "mismatch_conflict", ADMISSION)],
        ),
    ]
    retained_conflict = [
        dsl.select_node(f"{body_id}.retained_conflict", relation=ADMISSION, columns=COLUMNS[ADMISSION], predicate=conflict_pred, cardinality="EXACTLY_ONE", output_symbol="retained_conflict", order_by=COORDS+["source_position", "entry_kind"]),
        _retry_or_return(body_id, "conflict_replay", "retained_conflict", ADMISSION),
    ]
    source_pred = _predicate(SOURCE, {"practice_id": loc["practice_id"], "source_contract_id": loc["source_contract_id"], "stream_id": loc["stream_id"], "stream_epoch": loc["stream_epoch"], "transaction_position": position})
    key_pred = dsl.all_of(
        _predicate(KEY, loc),
        dsl.eq(_src(KEY, "key_id"), _field(packet, "key_id", F+"key_id")),
        dsl.binary("LTE", _src(KEY, "interval_start"), position),
        dsl.binary("GTE", _src(KEY, "interval_end"), position),
    )
    reuse_pred = dsl.all_of(
        _predicate(ADMISSION, loc),
        dsl.eq(_src(ADMISSION, "entry_kind"), dsl.const(F+"admission_entry_kind", "PRIMARY")),
        dsl.eq(_src(ADMISSION, "observation_digest"), _field(packet, "observation_digest", F+"digest_sha256")),
        dsl.binary("NE", _src(ADMISSION, "source_position"), position),
    )
    first_membership = [
        dsl.select_node(f"{body_id}.source", relation=SOURCE, columns=COLUMNS[SOURCE], predicate=source_pred, cardinality="EXACTLY_ONE", output_symbol="source", order_by=["practice_id", "source_contract_id", "stream_id", "stream_epoch", "transaction_position"]),
        dsl.assert_node(f"{body_id}.source_digest", dsl.eq(_field(packet, "source_membership_digest", F+"digest_sha256"), dsl.digest(F+"source_membership_digest_v1", [_col("source", SOURCE, name) for name in COLUMNS[SOURCE]])), "F_ADMISSION_SOURCE"),
        dsl.select_node(f"{body_id}.key", relation=KEY, columns=COLUMNS[KEY], predicate=key_pred, cardinality="EXACTLY_ONE", output_symbol="key", order_by=COORDS+["interval_start"]),
        dsl.assert_node(f"{body_id}.packet", dsl.all_of(
            dsl.eq(_col("key", KEY, "key_id"), _field(packet, "key_id", F+"key_id")),
            dsl.eq(_col("source", SOURCE, "transaction_position"), position),
            dsl.eq(_col("source", SOURCE, "stream_epoch"), loc["stream_epoch"]),
        ), "F_ADMISSION_PACKET"),
        dsl.select_node(f"{body_id}.reuse_set", relation=ADMISSION, columns=COLUMNS[ADMISSION], predicate=reuse_pred, cardinality="COMPLETE_SET", output_symbol="reuse_set", order_by=COORDS+["source_position", "entry_kind"], set_read=True),
        _if(
            f"{body_id}.digest_reused",
            dsl.binary("GT", _count("reuse_set", ADMISSION), dsl.const(PG+"bigint", 0)),
            [_insert_reload(f"{body_id}.insert_reuse", ADMISSION, reuse_bindings, "reuse_conflict", COORDS+["source_position", "entry_kind"]), _retry_or_return(body_id, "reuse_conflict", "reuse_conflict", ADMISSION)],
            [_insert_reload(f"{body_id}.insert_primary", ADMISSION, primary_bindings, "inserted_primary", COORDS+["source_position", "entry_kind"]), _retry_or_return(body_id, "primary_insert", "inserted_primary", ADMISSION)],
        ),
    ]
    nodes = [
        _isolation(body_id, "READ_COMMITTED"),
        *binding_nodes,
        dsl.let_node(f"{body_id}.attempted_digest", "attempted_digest", F+"digest_sha256", attempted),
        dsl.select_node(f"{body_id}.primary_set", relation=ADMISSION, columns=COLUMNS[ADMISSION], predicate=primary_pred, cardinality="COMPLETE_SET", output_symbol="primary_set", order_by=COORDS+["source_position", "entry_kind"], set_read=True),
        dsl.select_node(f"{body_id}.conflict_set", relation=ADMISSION, columns=COLUMNS[ADMISSION], predicate=conflict_pred, cardinality="COMPLETE_SET", output_symbol="conflict_set", order_by=COORDS+["source_position", "entry_kind"], set_read=True),
        dsl.select_node(f"{body_id}.receipt_set", relation=RECEIPT, columns=COLUMNS[RECEIPT], predicate=_predicate(RECEIPT, coordinate), cardinality="COMPLETE_SET", output_symbol="receipt_set", order_by=COORDS+["source_position"], set_read=True),
        dsl.assert_node(f"{body_id}.retained_cardinality", dsl.all_of(
            dsl.binary("LTE", _count("primary_set", ADMISSION), dsl.const(PG+"bigint", 1)),
            dsl.binary("LTE", _count("conflict_set", ADMISSION), dsl.const(PG+"bigint", 1)),
            dsl.binary("LTE", _count("receipt_set", RECEIPT), dsl.const(PG+"bigint", 1)),
        ), "F_STATE"),
        dsl.assert_node(f"{body_id}.receipt_has_primary", dsl.any_of(
            dsl.eq(_count("receipt_set", RECEIPT), dsl.const(PG+"bigint", 0)),
            dsl.eq(_count("primary_set", ADMISSION), dsl.const(PG+"bigint", 1)),
        ), "F_STATE"),
        _if(
            f"{body_id}.has_primary",
            dsl.eq(_count("primary_set", ADMISSION), dsl.const(PG+"bigint", 1)),
            retained_primary,
            [_if(f"{body_id}.has_conflict", dsl.eq(_count("conflict_set", ADMISSION), dsl.const(PG+"bigint", 1)), retained_conflict, first_membership)],
        ),
    ]
    locals_ = [(row["id"], row["type"]) for row in binding_symbols]
    locals_.extend([
        ("attempted_digest", F+"digest_sha256"), ("primary_set", ADMISSION+"[]"), ("conflict_set", ADMISSION+"[]"), ("receipt_set", RECEIPT+"[]"),
        ("retained_primary", ADMISSION), ("retained_conflict", ADMISSION), ("source", SOURCE), ("key", KEY),
        ("reuse_set", ADMISSION+"[]"), ("mismatch_conflict", ADMISSION), ("reuse_conflict", ADMISSION), ("inserted_primary", ADMISSION),
    ])
    return dsl.body(body_id, "ENTRY_POINT", body_id, _symbols([("generation_locator", GEN_LOC), ("source_position", PG+"bigint"), ("proofread_packet", PACKET)], locals_), nodes)


def _transition_result(
    *,
    kind: str,
    checkpoint_symbol: str,
    source_position: dict[str, Any],
    decision: dict[str, Any],
    reason: dict[str, Any],
    disposition: dict[str, Any],
    revision: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    result_type = F + "durability_transition_result_v1"
    return _composite(
        result_type,
        [
            ("result_kind", dsl.const(F+"durability_transition_result_kind", kind)),
            ("checkpoint_state", _col(checkpoint_symbol, CHECKPOINT, "checkpoint_state")),
            ("source_position", source_position),
            ("decision", decision),
            ("reason_code", reason),
            ("checkpoint_disposition", disposition),
            ("lifecycle_revision", revision),
            ("evidence_digest", evidence),
        ],
    )


def build_coordinator_body() -> dict[str, Any]:
    body_id = F + "apply_durability_transition_v1"
    result_type = F + "durability_transition_result_v1"
    admission_locator = dsl.input_ref("admission_locator", ADMISSION_LOC)
    locator = _field(admission_locator, "generation_locator", GEN_LOC)
    position = _field(admission_locator, "source_position", PG+"bigint")
    loc = _loc(locator)
    binding_nodes, binding_symbols = _binding(body_id, "COORDINATOR", loc)
    scope = {key: loc[key] for key in ("practice_id", "source_contract_id", "stream_id")}
    coordinate = {**loc, "source_position": position}
    primary_pred = dsl.all_of(
        _predicate(ADMISSION, coordinate),
        dsl.eq(
            _src(ADMISSION, "entry_kind"),
            dsl.const(F + "admission_entry_kind", "PRIMARY"),
        ),
    )
    conflict_pred = dsl.all_of(
        _predicate(ADMISSION, coordinate),
        dsl.eq(
            _src(ADMISSION, "entry_kind"),
            dsl.const(F + "admission_entry_kind", "CONFLICT"),
        ),
    )
    receipt_pred = _predicate(RECEIPT, coordinate)
    source_position_pred = _predicate(
        SOURCE,
        {
            **scope,
            "transaction_position": position,
        },
    )
    current_frame_pred = dsl.all_of(
        _predicate(FRAME, loc),
        dsl.eq(
            _src(FRAME, "lifecycle_state"),
            dsl.const(F + "frame_lifecycle", "CURRENT"),
        ),
    )
    watermark_pred = _predicate(WATERMARK, loc)
    pending_obligation_pred = dsl.all_of(
        _predicate(OBLIGATION, loc),
        dsl.eq(
            _src(OBLIGATION, "obligation_state"),
            dsl.const(F + "obligation_state", "PENDING"),
        ),
    )
    current_anchor_pred = _predicate(
        ANCHOR,
        {
            **loc,
            "lifecycle_revision": _col(
                "checkpoint", CHECKPOINT, "lifecycle_revision"
            ),
        },
    )
    next_revision = dsl.add(_col("checkpoint", CHECKPOINT, "lifecycle_revision"), dsl.const(PG+"bigint", 1), PG+"bigint")
    rebase_integrity = dsl.digest(F+"checkpoint_rebase_digest_v1", [*loc.values(), position, next_revision])
    applied_integrity = dsl.digest(F+"checkpoint_apply_digest_v1", [*loc.values(), position, _col("primary", ADMISSION, "admission_digest"), next_revision])

    terminal_disposition = dsl.case(
        F + "checkpoint_disposition",
        [
            {
                "when": dsl.eq(
                    _col("checkpoint", CHECKPOINT, "checkpoint_state"),
                    dsl.const(F + "checkpoint_state", "REBASE_REQUIRED"),
                ),
                "then": dsl.const(
                    F + "checkpoint_disposition", "HOLD_REBASE"
                ),
            }
        ],
        dsl.const(F + "checkpoint_disposition", "STOP_GENERATION"),
    )
    terminal_result = _transition_result(
        kind="TERMINAL_REPLAYED",
        checkpoint_symbol="checkpoint",
        source_position=_col("terminal_lifecycle", LIFECYCLE, "source_position"),
        decision=_col("terminal_audit", AUDIT, "decision"),
        reason=_col("terminal_audit", AUDIT, "reason_code"),
        disposition=terminal_disposition,
        revision=_col("checkpoint", CHECKPOINT, "lifecycle_revision"),
        evidence=_col("checkpoint", CHECKPOINT, "checkpoint_integrity_digest"),
    )
    terminal_branch = [
        dsl.lock_node(
            f"{body_id}.lock_terminal_lifecycle",
            relation=LIFECYCLE,
            predicate=_predicate(
                LIFECYCLE,
                {
                    **loc,
                    "lifecycle_revision": _col(
                        "checkpoint", CHECKPOINT, "lifecycle_revision"
                    ),
                },
            ),
            key_columns=COORDS + ["lifecycle_revision"],
            mode="FOR_SHARE",
            order=4,
            output_symbol="terminal_lifecycle",
            columns=COLUMNS[LIFECYCLE],
        ),
        dsl.lock_node(
            f"{body_id}.lock_terminal_audit",
            relation=AUDIT,
            predicate=_predicate(
                AUDIT,
                {
                    **loc,
                    "lifecycle_revision": _col(
                        "checkpoint", CHECKPOINT, "lifecycle_revision"
                    ),
                },
            ),
            key_columns=COORDS + ["lifecycle_revision"],
            mode="FOR_SHARE",
            order=5,
            output_symbol="terminal_audit",
            columns=COLUMNS[AUDIT],
        ),
        dsl.assert_node(
            f"{body_id}.terminal_integrity",
            dsl.all_of(
                dsl.binary(
                    "NE",
                    _col("generation", GENERATION, "lifecycle_state"),
                    dsl.const(F + "generation_state", "ACTIVE"),
                ),
                dsl.any_of(
                    dsl.all_of(
                        dsl.eq(
                            _col("checkpoint", CHECKPOINT, "checkpoint_state"),
                            dsl.const(
                                F + "checkpoint_state", "REBASE_REQUIRED"
                            ),
                        ),
                        dsl.eq(
                            _col("generation", GENERATION, "lifecycle_state"),
                            dsl.const(
                                F + "generation_state", "REBASE_REQUIRED"
                            ),
                        ),
                    ),
                    dsl.all_of(
                        dsl.eq(
                            _col("checkpoint", CHECKPOINT, "checkpoint_state"),
                            dsl.const(F + "checkpoint_state", "REVOKED"),
                        ),
                        dsl.eq(
                            _col("generation", GENERATION, "lifecycle_state"),
                            dsl.const(F + "generation_state", "REVOKED"),
                        ),
                    ),
                    dsl.all_of(
                        dsl.eq(
                            _col("checkpoint", CHECKPOINT, "checkpoint_state"),
                            dsl.const(F + "checkpoint_state", "CONSUMED"),
                        ),
                        dsl.eq(
                            _col("generation", GENERATION, "lifecycle_state"),
                            dsl.const(F + "generation_state", "CONSUMED"),
                        ),
                    ),
                ),
                dsl.eq(
                    _col("terminal_lifecycle", LIFECYCLE, "lifecycle_digest"),
                    _col(
                        "checkpoint", CHECKPOINT, "checkpoint_integrity_digest"
                    ),
                ),
                dsl.eq(
                    _col("terminal_audit", AUDIT, "audit_head_digest"),
                    _col("checkpoint", CHECKPOINT, "audit_head_digest"),
                ),
            ),
            "F_STATE",
        ),
        dsl.let_node(f"{body_id}.terminal_result", "terminal_result", result_type, terminal_result),
        _retry_or_return(body_id, "terminal", "terminal_result", result_type, composite=True),
    ]

    replay_result = _composite(result_type, [
        ("result_kind", dsl.const(F+"durability_transition_result_kind", "RECEIPT_REPLAYED")),
        ("checkpoint_state", _col("checkpoint", CHECKPOINT, "checkpoint_state")),
        ("source_position", _col("stored_receipt", RECEIPT, "source_position")),
        ("decision", _col("stored_receipt", RECEIPT, "decision")),
        ("reason_code", _col("stored_receipt", RECEIPT, "reason_code")),
        ("checkpoint_disposition", _col("stored_receipt", RECEIPT, "checkpoint_disposition")),
        ("lifecycle_revision", _col("stored_receipt", RECEIPT, "lifecycle_revision")),
        ("evidence_digest", _col("stored_receipt", RECEIPT, "receipt_digest")),
    ])
    replayed_receipt_digest = dsl.digest(
        F + "classified_receipt_digest_v1",
        [
            *loc.values(),
            _col("stored_receipt", RECEIPT, "source_position"),
            _col("replay_primary", ADMISSION, "admission_digest"),
            _col("stored_receipt", RECEIPT, "lifecycle_revision"),
        ],
    )
    receipt_replay = [
        dsl.lock_node(f"{body_id}.lock_receipt", relation=RECEIPT, predicate=receipt_pred, key_columns=COORDS+["source_position"], mode="FOR_UPDATE", order=4, output_symbol="stored_receipt", columns=COLUMNS[RECEIPT]),
        dsl.lock_node(f"{body_id}.lock_replay_primary", relation=ADMISSION, predicate=primary_pred, key_columns=COORDS+["source_position", "entry_kind"], mode="FOR_SHARE", order=5, output_symbol="replay_primary", columns=COLUMNS[ADMISSION]),
        dsl.let_node(
            f"{body_id}.rederive_receipt_digest",
            "rederived_receipt_digest",
            F + "digest_sha256",
            replayed_receipt_digest,
        ),
        dsl.assert_node(
            f"{body_id}.receipt_integrity",
            dsl.all_of(
                dsl.eq(
                    _col("stored_receipt", RECEIPT, "admission_entry_kind"),
                    dsl.const(F + "admission_entry_kind", "PRIMARY"),
                ),
                dsl.eq(
                    _col("stored_receipt", RECEIPT, "observation_digest"),
                    _col("replay_primary", ADMISSION, "observation_digest"),
                ),
                dsl.eq(
                    _col("stored_receipt", RECEIPT, "decision"),
                    _col("replay_primary", ADMISSION, "decision"),
                ),
                dsl.eq(
                    _col("stored_receipt", RECEIPT, "reason_code"),
                    _col("replay_primary", ADMISSION, "reason_code"),
                ),
                dsl.eq(
                    _col("stored_receipt", RECEIPT, "affected_frame_mask"),
                    _col("replay_primary", ADMISSION, "affected_frame_mask"),
                ),
                dsl.eq(
                    _col("stored_receipt", RECEIPT, "checkpoint_disposition"),
                    _col("replay_primary", ADMISSION, "checkpoint_disposition"),
                ),
                dsl.eq(
                    _col("stored_receipt", RECEIPT, "lifecycle_revision"),
                    _col("checkpoint", CHECKPOINT, "lifecycle_revision"),
                ),
            ),
            "F_STATE",
        ),
        dsl.assert_node(
            f"{body_id}.receipt_digest_matches",
            dsl.eq(
                dsl.local_ref("rederived_receipt_digest", F + "digest_sha256"),
                _col("stored_receipt", RECEIPT, "receipt_digest"),
            ),
            "F_STATE",
        ),
        dsl.let_node(f"{body_id}.replay_result", "replay_result", result_type, replay_result),
        _retry_or_return(body_id, "receipt_replay", "replay_result", result_type, composite=True),
    ]

    rebase_symbols: list[tuple[str, str]] = []

    def rebase_branch(tag: str, reason: dict[str, Any]) -> list[dict[str, Any]]:
        lifecycle_symbol = f"rebase_lifecycle_{tag}"
        audit_symbol = f"rebase_audit_{tag}"
        generation_symbol = f"rebased_generation_{tag}"
        checkpoint_symbol = f"rebased_checkpoint_{tag}"
        result_symbol = f"rebase_result_{tag}"
        rebase_symbols.extend(
            [
                (lifecycle_symbol, LIFECYCLE),
                (audit_symbol, AUDIT),
                (generation_symbol, GENERATION),
                (checkpoint_symbol, CHECKPOINT),
                (result_symbol, result_type),
            ]
        )
        lifecycle_bindings = [(name, loc[name]) for name in COORDS] + [
            ("lifecycle_revision", next_revision),
            ("entry_kind", dsl.const(F + "lifecycle_entry_kind", "DECISION")),
            ("source_position", position),
            ("key_interval_start", dsl.const(PG + "bigint", None)),
            ("key_interval_end", dsl.const(PG + "bigint", None)),
            (
                "prior_lifecycle_digest",
                _col("checkpoint", CHECKPOINT, "checkpoint_integrity_digest"),
            ),
            ("lifecycle_digest", rebase_integrity),
            ("created_at", dsl.transaction_timestamp()),
        ]
        audit_bindings = [(name, loc[name]) for name in COORDS] + [
            ("lifecycle_revision", next_revision),
            (
                "decision",
                dsl.const(F + "observation_decision", "REBASE_REQUIRED"),
            ),
            ("reason_code", reason),
            ("affected_frame_mask", dsl.const(F + "frame_mask", 0)),
            (
                "prior_audit_digest",
                _col("checkpoint", CHECKPOINT, "audit_head_digest"),
            ),
            ("audit_head_digest", rebase_integrity),
            ("created_at", dsl.transaction_timestamp()),
        ]
        return [
            dsl.insert_node(
                f"{body_id}.rebase_lifecycle.{tag}",
                relation=LIFECYCLE,
                bindings=lifecycle_bindings,
                output_symbol=lifecycle_symbol,
                returning_columns=COLUMNS[LIFECYCLE],
            ),
            dsl.insert_node(
                f"{body_id}.rebase_audit.{tag}",
                relation=AUDIT,
                bindings=audit_bindings,
                output_symbol=audit_symbol,
                returning_columns=COLUMNS[AUDIT],
            ),
            dsl.update_node(
                f"{body_id}.rebase_generation.{tag}",
                relation=GENERATION,
                predicate=_predicate(GENERATION, loc),
                key_columns=COORDS,
                bindings=[
                    (
                        "lifecycle_state",
                        dsl.const(F + "generation_state", "REBASE_REQUIRED"),
                    ),
                    (
                        "terminal_reason",
                        dsl.const(F + "generation_terminal_reason", None),
                    ),
                ],
                output_symbol=generation_symbol,
                returning_columns=COLUMNS[GENERATION],
            ),
            dsl.update_node(
                f"{body_id}.rebase_checkpoint.{tag}",
                relation=CHECKPOINT,
                predicate=_predicate(CHECKPOINT, loc),
                key_columns=COORDS,
                bindings=[
                    (
                        "checkpoint_state",
                        dsl.const(F + "checkpoint_state", "REBASE_REQUIRED"),
                    ),
                    ("lifecycle_revision", next_revision),
                    ("audit_head_digest", rebase_integrity),
                    ("checkpoint_integrity_digest", rebase_integrity),
                    ("updated_at", dsl.transaction_timestamp()),
                ],
                output_symbol=checkpoint_symbol,
                returning_columns=COLUMNS[CHECKPOINT],
            ),
            dsl.let_node(
                f"{body_id}.rebase_result.{tag}",
                result_symbol,
                result_type,
                _transition_result(
                    kind="REBASE_APPLIED",
                    checkpoint_symbol=checkpoint_symbol,
                    source_position=position,
                    decision=dsl.const(
                        F + "observation_decision", "REBASE_REQUIRED"
                    ),
                    reason=reason,
                    disposition=dsl.const(
                        F + "checkpoint_disposition", "HOLD_REBASE"
                    ),
                    revision=_col(
                        checkpoint_symbol, CHECKPOINT, "lifecycle_revision"
                    ),
                    evidence=_col(
                        checkpoint_symbol,
                        CHECKPOINT,
                        "checkpoint_integrity_digest",
                    ),
                ),
            ),
            _retry_or_return(
                body_id,
                f"rebase_{tag}",
                result_symbol,
                result_type,
                composite=True,
            ),
        ]

    receipt_digest = dsl.digest(F+"classified_receipt_digest_v1", [*loc.values(), position, _col("primary", ADMISSION, "admission_digest"), next_revision])
    receipt_bindings = [(name, loc[name]) for name in COORDS] + [
        ("source_position", position),
        ("admission_entry_kind", _col("primary", ADMISSION, "entry_kind")),
        ("observation_digest", _col("primary", ADMISSION, "observation_digest")),
        ("decision", _col("primary", ADMISSION, "decision")),
        ("reason_code", _col("primary", ADMISSION, "reason_code")),
        ("affected_frame_mask", _col("primary", ADMISSION, "affected_frame_mask")),
        ("checkpoint_disposition", _col("primary", ADMISSION, "checkpoint_disposition")),
        ("lifecycle_revision", next_revision),
        ("receipt_digest", receipt_digest),
        ("created_at", dsl.transaction_timestamp()),
    ]
    applied_lifecycle_bindings = [(name, loc[name]) for name in COORDS] + [
        ("lifecycle_revision", next_revision), ("entry_kind", dsl.const(F+"lifecycle_entry_kind", "DECISION")),
        ("source_position", position), ("key_interval_start", dsl.const(PG+"bigint", None)),
        ("key_interval_end", dsl.const(PG+"bigint", None)), ("prior_lifecycle_digest", _col("anchor", ANCHOR, "anchor_digest")),
        ("lifecycle_digest", applied_integrity), ("created_at", dsl.transaction_timestamp()),
    ]
    applied_audit_bindings = [(name, loc[name]) for name in COORDS] + [
        ("lifecycle_revision", next_revision), ("decision", _col("primary", ADMISSION, "decision")),
        ("reason_code", _col("primary", ADMISSION, "reason_code")), ("affected_frame_mask", _col("primary", ADMISSION, "affected_frame_mask")),
        ("prior_audit_digest", _col("checkpoint", CHECKPOINT, "audit_head_digest")), ("audit_head_digest", applied_integrity),
        ("created_at", dsl.transaction_timestamp()),
    ]
    dependent_symbols: list[tuple[str, str]] = []

    def dependent_effects(
        tag: str,
        frame_symbol: str,
        watermark_symbol: str,
        frame_type: str,
    ) -> list[dict[str, Any]]:
        obligation_set_symbol = f"{tag}_obligation_set"
        obligation_symbol = f"{tag}_obligation"
        coalesced_symbol = f"{tag}_coalesced_obligation"
        inserted_symbol = f"{tag}_inserted_obligation"
        retired_symbol = f"{tag}_retired_frame"
        advanced_symbol = f"{tag}_advanced_watermark"
        dependent_symbols.extend(
            [
                (obligation_set_symbol, OBLIGATION + "[]"),
                (obligation_symbol, OBLIGATION),
                (coalesced_symbol, OBLIGATION),
                (inserted_symbol, OBLIGATION),
                (retired_symbol, FRAME),
                (advanced_symbol, WATERMARK),
            ]
        )
        frame_id = _col(frame_symbol, FRAME, "frame_generation_id")
        obligation_coordinate = {**loc, "frame_generation_id": frame_id}
        obligation_predicate = dsl.all_of(
            _predicate(OBLIGATION, obligation_coordinate),
            dsl.eq(
                _src(OBLIGATION, "obligation_state"),
                dsl.const(F + "obligation_state", "PENDING"),
            ),
        )
        coalesced_digest = dsl.digest(
            F + "coalesced_reassembly_obligation_digest_v1",
            [
                _col(obligation_symbol, OBLIGATION, "rolling_cause_digest"),
                position,
                _col("primary", ADMISSION, "observation_digest"),
            ],
        )
        existing_branch = [
            dsl.select_node(
                f"{body_id}.reload_{tag}_obligation",
                relation=OBLIGATION,
                columns=COLUMNS[OBLIGATION],
                predicate=obligation_predicate,
                cardinality="EXACTLY_ONE",
                output_symbol=obligation_symbol,
                order_by=COORDS + ["frame_generation_id"],
            ),
            dsl.update_node(
                f"{body_id}.coalesce_{tag}_obligation",
                relation=OBLIGATION,
                predicate=obligation_predicate,
                key_columns=COORDS + ["frame_generation_id"],
                bindings=[
                    (
                        "earliest_position",
                        dsl.case(
                            PG + "bigint",
                            [
                                {
                                    "when": dsl.binary(
                                        "LTE",
                                        _col(
                                            obligation_symbol,
                                            OBLIGATION,
                                            "earliest_position",
                                        ),
                                        position,
                                    ),
                                    "then": _col(
                                        obligation_symbol,
                                        OBLIGATION,
                                        "earliest_position",
                                    ),
                                }
                            ],
                            position,
                        ),
                    ),
                    (
                        "latest_position",
                        dsl.case(
                            PG + "bigint",
                            [
                                {
                                    "when": dsl.binary(
                                        "GTE",
                                        _col(
                                            obligation_symbol,
                                            OBLIGATION,
                                            "latest_position",
                                        ),
                                        position,
                                    ),
                                    "then": _col(
                                        obligation_symbol,
                                        OBLIGATION,
                                        "latest_position",
                                    ),
                                }
                            ],
                            position,
                        ),
                    ),
                    ("rolling_cause_digest", coalesced_digest),
                    (
                        "count_bucket",
                        dsl.case(
                            F + "obligation_count_bucket",
                            [
                                {
                                    "when": dsl.eq(
                                        _col(
                                            obligation_symbol,
                                            OBLIGATION,
                                            "count_bucket",
                                        ),
                                        dsl.const(
                                            F + "obligation_count_bucket", "ONE"
                                        ),
                                    ),
                                    "then": dsl.const(
                                        F + "obligation_count_bucket",
                                        "TWO_TO_FOUR",
                                    ),
                                }
                            ],
                            dsl.const(
                                F + "obligation_count_bucket", "FIVE_PLUS"
                            ),
                        ),
                    ),
                    ("updated_at", dsl.transaction_timestamp()),
                ],
                output_symbol=coalesced_symbol,
                returning_columns=COLUMNS[OBLIGATION],
            ),
        ]
        initial_digest = dsl.digest(
            F + "reassembly_obligation_digest_v1",
            [frame_id, position, _col("primary", ADMISSION, "observation_digest")],
        )
        obligation_bindings = [(name, loc[name]) for name in COORDS] + [
            ("frame_generation_id", frame_id),
            ("earliest_position", position),
            ("latest_position", position),
            ("rolling_cause_digest", initial_digest),
            (
                "count_bucket",
                dsl.const(F + "obligation_count_bucket", "ONE"),
            ),
            ("obligation_state", dsl.const(F + "obligation_state", "PENDING")),
            ("created_at", dsl.transaction_timestamp()),
            ("updated_at", dsl.transaction_timestamp()),
        ]
        return [
            dsl.select_node(
                f"{body_id}.{tag}_obligation_set",
                relation=OBLIGATION,
                columns=COLUMNS[OBLIGATION],
                predicate=obligation_predicate,
                cardinality="COMPLETE_SET",
                output_symbol=obligation_set_symbol,
                order_by=COORDS + ["frame_generation_id"],
                set_read=True,
            ),
            dsl.assert_node(
                f"{body_id}.{tag}_obligation_cardinality",
                dsl.binary(
                    "LTE",
                    _count(obligation_set_symbol, OBLIGATION),
                    dsl.const(PG + "bigint", 1),
                ),
                "F_STATE",
            ),
            _if_rejoin(
                f"{body_id}.{tag}_obligation_exists",
                dsl.eq(
                    _count(obligation_set_symbol, OBLIGATION),
                    dsl.const(PG + "bigint", 1),
                ),
                existing_branch,
                [
                    _insert_reload(
                        f"{body_id}.insert_{tag}_obligation",
                        OBLIGATION,
                        obligation_bindings,
                        inserted_symbol,
                        COORDS + ["frame_generation_id"],
                    )
                ],
            ),
            dsl.update_node(
                f"{body_id}.retire_{tag}_frame",
                relation=FRAME,
                predicate=_predicate(
                    FRAME,
                    {
                        **loc,
                        "frame_generation_id": frame_id,
                        "frame_type": dsl.const(F + "frame_type", frame_type),
                        "lifecycle_state": dsl.const(
                            F + "frame_lifecycle", "CURRENT"
                        ),
                    },
                ),
                key_columns=COORDS + ["frame_generation_id"],
                bindings=[
                    (
                        "lifecycle_state",
                        dsl.const(F + "frame_lifecycle", "RETIRED"),
                    ),
                    ("retired_at", dsl.transaction_timestamp()),
                ],
                output_symbol=retired_symbol,
                returning_columns=COLUMNS[FRAME],
            ),
            dsl.update_node(
                f"{body_id}.advance_{tag}_watermark",
                relation=WATERMARK,
                predicate=_predicate(
                    WATERMARK,
                    {
                        **loc,
                        "frame_type": dsl.const(F + "frame_type", frame_type),
                    },
                ),
                key_columns=COORDS + ["frame_type"],
                bindings=[
                    ("watermark_position", position),
                    ("updated_at", dsl.transaction_timestamp()),
                ],
                output_symbol=advanced_symbol,
                returning_columns=COLUMNS[WATERMARK],
            ),
        ]

    diary_effects = dependent_effects(
        "diary_only",
        "diary_frame",
        "diary_watermark",
        "CURRENT_DIARY_PROJECTION",
    )
    waiting_effects = dependent_effects(
        "waiting_only",
        "waiting_frame",
        "waiting_watermark",
        "CURRENT_WAITING_ROOM_PROJECTION",
    )
    diary_both_effects = dependent_effects(
        "diary_both",
        "diary_frame",
        "diary_watermark",
        "CURRENT_DIARY_PROJECTION",
    )
    waiting_both_effects = dependent_effects(
        "waiting_both",
        "waiting_frame",
        "waiting_watermark",
        "CURRENT_WAITING_ROOM_PROJECTION",
    )
    mask = _col("primary", ADMISSION, "affected_frame_mask")
    dependent_branch = [
        _if_rejoin(
            f"{body_id}.mask_diary",
            dsl.eq(mask, dsl.const(F + "frame_mask", 1)),
            diary_effects,
            [
                _if_rejoin(
                    f"{body_id}.mask_waiting",
                    dsl.eq(mask, dsl.const(F + "frame_mask", 2)),
                    waiting_effects,
                    [
                        _if_rejoin(
                            f"{body_id}.mask_both",
                            dsl.eq(mask, dsl.const(F + "frame_mask", 3)),
                            [*diary_both_effects, *waiting_both_effects],
                            [
                                dsl.assert_node(
                                    f"{body_id}.mask_none",
                                    dsl.eq(
                                        mask, dsl.const(F + "frame_mask", 0)
                                    ),
                                    "F_STATE",
                                )
                            ],
                        )
                    ],
                )
            ],
        )
    ]

    apply_branch = [
        dsl.lock_node(f"{body_id}.lock_diary_frame", relation=FRAME, predicate=dsl.all_of(current_frame_pred, dsl.eq(_src(FRAME, "frame_type"), dsl.const(F+"frame_type", "CURRENT_DIARY_PROJECTION"))), key_columns=COORDS+["frame_generation_id"], mode="FOR_UPDATE", order=6, output_symbol="diary_frame", columns=COLUMNS[FRAME]),
        dsl.lock_node(f"{body_id}.lock_waiting_frame", relation=FRAME, predicate=dsl.all_of(current_frame_pred, dsl.eq(_src(FRAME, "frame_type"), dsl.const(F+"frame_type", "CURRENT_WAITING_ROOM_PROJECTION"))), key_columns=COORDS+["frame_generation_id"], mode="FOR_UPDATE", order=7, output_symbol="waiting_frame", columns=COLUMNS[FRAME]),
        dsl.lock_node(f"{body_id}.lock_diary_watermark", relation=WATERMARK, predicate=dsl.all_of(watermark_pred, dsl.eq(_src(WATERMARK, "frame_type"), dsl.const(F+"frame_type", "CURRENT_DIARY_PROJECTION"))), key_columns=COORDS+["frame_type"], mode="FOR_UPDATE", order=8, output_symbol="diary_watermark", columns=COLUMNS[WATERMARK]),
        dsl.lock_node(f"{body_id}.lock_waiting_watermark", relation=WATERMARK, predicate=dsl.all_of(watermark_pred, dsl.eq(_src(WATERMARK, "frame_type"), dsl.const(F+"frame_type", "CURRENT_WAITING_ROOM_PROJECTION"))), key_columns=COORDS+["frame_type"], mode="FOR_UPDATE", order=9, output_symbol="waiting_watermark", columns=COLUMNS[WATERMARK]),
        dsl.insert_node(f"{body_id}.lifecycle", relation=LIFECYCLE, bindings=applied_lifecycle_bindings, output_symbol="applied_lifecycle", returning_columns=COLUMNS[LIFECYCLE]),
        dsl.insert_node(f"{body_id}.audit", relation=AUDIT, bindings=applied_audit_bindings, output_symbol="applied_audit", returning_columns=COLUMNS[AUDIT]),
        _insert_reload(f"{body_id}.receipt_insert", RECEIPT, receipt_bindings, "inserted_receipt", COORDS+["source_position"]),
        *dependent_branch,
        dsl.update_node(f"{body_id}.checkpoint_update", relation=CHECKPOINT, predicate=_predicate(CHECKPOINT, loc), key_columns=COORDS, bindings=[
            ("checkpoint_state", dsl.const(F+"checkpoint_state", "ACTIVE")), ("last_contiguous_position", position),
            ("last_observation_digest", _col("primary", ADMISSION, "observation_digest")), ("lifecycle_revision", next_revision),
            ("audit_head_digest", applied_integrity), ("checkpoint_integrity_digest", applied_integrity), ("updated_at", dsl.transaction_timestamp()),
        ], output_symbol="applied_checkpoint", returning_columns=COLUMNS[CHECKPOINT]),
        dsl.let_node(f"{body_id}.applied_result", "applied_result", result_type, _transition_result(
            kind="RECEIPT_APPLIED", checkpoint_symbol="applied_checkpoint", source_position=position,
            decision=_col("inserted_receipt", RECEIPT, "decision"), reason=_col("inserted_receipt", RECEIPT, "reason_code"),
            disposition=_col("inserted_receipt", RECEIPT, "checkpoint_disposition"), revision=_col("inserted_receipt", RECEIPT, "lifecycle_revision"),
            evidence=_col("inserted_receipt", RECEIPT, "receipt_digest"),
        )),
        _retry_or_return(body_id, "applied", "applied_result", result_type, composite=True),
    ]

    key_membership_pred = dsl.all_of(
        _predicate(KEY, loc),
        dsl.eq(_src(KEY, "key_id"), _col("primary", ADMISSION, "key_id")),
        dsl.binary("LTE", _src(KEY, "interval_start"), position),
        dsl.binary("GTE", _src(KEY, "interval_end"), position),
    )
    expected_position = dsl.add(
        _col("checkpoint", CHECKPOINT, "last_contiguous_position"),
        dsl.const(PG + "bigint", 1),
        PG + "bigint",
    )
    anchor_integrity = dsl.all_of(
        dsl.eq(
            _col("anchor", ANCHOR, "checkpoint_state"),
            _col("checkpoint", CHECKPOINT, "checkpoint_state"),
        ),
        dsl.eq(
            _col("anchor", ANCHOR, "last_contiguous_position"),
            _col("checkpoint", CHECKPOINT, "last_contiguous_position"),
        ),
        dsl.eq(
            _col("anchor", ANCHOR, "checkpoint_integrity_digest"),
            _col("checkpoint", CHECKPOINT, "checkpoint_integrity_digest"),
        ),
    )
    dependent_state_exact = dsl.all_of(
        dsl.eq(_count("current_frame_set", FRAME), dsl.const(PG + "bigint", 2)),
        dsl.eq(
            _count("watermark_set", WATERMARK), dsl.const(PG + "bigint", 2)
        ),
        dsl.binary(
            "LTE",
            _count("pending_obligation_set", OBLIGATION),
            dsl.const(PG + "bigint", 2),
        ),
    )
    apply_state_branch = [
        dsl.select_node(
            f"{body_id}.key_membership_set",
            relation=KEY,
            columns=COLUMNS[KEY],
            predicate=key_membership_pred,
            cardinality="COMPLETE_SET",
            output_symbol="key_membership_set",
            order_by=COORDS + ["interval_start"],
            set_read=True,
        ),
        _if(
            f"{body_id}.epoch_matches",
            dsl.eq(
                _col("source_at_position", SOURCE, "stream_epoch"),
                loc["stream_epoch"],
            ),
            [
                _if(
                    f"{body_id}.gap",
                    dsl.binary("GT", position, expected_position),
                    rebase_branch(
                        "gap",
                        dsl.const(F + "observation_reason", "COVERAGE_GAP"),
                    ),
                    [
                        _if(
                            f"{body_id}.predecessor_matches",
                            dsl.all_of(
                                dsl.eq(position, expected_position),
                                dsl.eq(
                                    _col(
                                        "source_at_position",
                                        SOURCE,
                                        "predecessor_position",
                                    ),
                                    _col(
                                        "checkpoint",
                                        CHECKPOINT,
                                        "last_contiguous_position",
                                    ),
                                ),
                            ),
                            [
                                _if(
                                    f"{body_id}.key_membership_exact",
                                    dsl.eq(
                                        _count("key_membership_set", KEY),
                                        dsl.const(PG + "bigint", 1),
                                    ),
                                    [
                                        _if(
                                            f"{body_id}.anchor_present",
                                            dsl.eq(
                                                _count(
                                                    "current_anchor_set", ANCHOR
                                                ),
                                                dsl.const(PG + "bigint", 1),
                                            ),
                                            [
                                                dsl.lock_node(
                                                    f"{body_id}.lock_anchor_for_proof",
                                                    relation=ANCHOR,
                                                    predicate=current_anchor_pred,
                                                    key_columns=COORDS
                                                    + ["lifecycle_revision"],
                                                    mode="FOR_SHARE",
                                                    order=5,
                                                    output_symbol="anchor",
                                                    columns=COLUMNS[ANCHOR],
                                                ),
                                                _if(
                                                    f"{body_id}.anchor_fence_exact",
                                                    anchor_integrity,
                                                    [
                                                        _if(
                                                            f"{body_id}.dependent_state_exact",
                                                            dependent_state_exact,
                                                            apply_branch,
                                                            rebase_branch(
                                                                "dependent_state",
                                                                dsl.const(
                                                                    F
                                                                    + "observation_reason",
                                                                    "MALFORMED_OR_FOREIGN",
                                                                ),
                                                            ),
                                                        )
                                                    ],
                                                    rebase_branch(
                                                        "anchor_integrity",
                                                        dsl.const(
                                                            F
                                                            + "observation_reason",
                                                            "MALFORMED_OR_FOREIGN",
                                                        ),
                                                    ),
                                                ),
                                            ],
                                            rebase_branch(
                                                "anchor_missing",
                                                dsl.const(
                                                    F + "observation_reason",
                                                    "MALFORMED_OR_FOREIGN",
                                                ),
                                            ),
                                        )
                                    ],
                                    rebase_branch(
                                        "key",
                                        dsl.const(
                                            F + "observation_reason", "KEY_UNAVAILABLE"
                                        ),
                                    ),
                                )
                            ],
                            rebase_branch(
                                "predecessor",
                                dsl.const(
                                    F + "observation_reason", "WRONG_PREDECESSOR"
                                ),
                            ),
                        )
                    ],
                )
            ],
            rebase_branch(
                "epoch",
                dsl.const(F + "observation_reason", "WRONG_EPOCH"),
            ),
        ),
    ]
    primary_branch = [
        dsl.lock_node(f"{body_id}.lock_primary", relation=ADMISSION, predicate=primary_pred, key_columns=COORDS+["source_position", "entry_kind"], mode="FOR_UPDATE", order=4, output_symbol="primary", columns=COLUMNS[ADMISSION]),
        dsl.select_node(
            f"{body_id}.source_at_position",
            relation=SOURCE,
            columns=COLUMNS[SOURCE],
            predicate=source_position_pred,
            cardinality="EXACTLY_ONE",
            output_symbol="source_at_position",
            order_by=[
                "practice_id",
                "source_contract_id",
                "stream_id",
                "stream_epoch",
                "transaction_position",
            ],
        ),
        *apply_state_branch,
    ]
    conflict_reason = dsl.case(
        F + "observation_reason",
        [
            {
                "when": dsl.eq(
                    _col("conflict", ADMISSION, "conflict_reason"),
                    dsl.const(
                        F + "admission_conflict_reason",
                        "POSITION_DIGEST_MISMATCH",
                    ),
                ),
                "then": dsl.const(
                    F + "observation_reason", "SAME_POSITION_MISMATCH"
                ),
            }
        ],
        dsl.const(F + "observation_reason", "DIGEST_REUSE"),
    )
    conflict_branch = [
        dsl.lock_node(
            f"{body_id}.lock_conflict",
            relation=ADMISSION,
            predicate=conflict_pred,
            key_columns=COORDS + ["source_position", "entry_kind"],
            mode="FOR_UPDATE",
            order=4,
            output_symbol="conflict",
            columns=COLUMNS[ADMISSION],
        ),
        *rebase_branch("conflict", conflict_reason),
    ]
    admission_state = _if(
        f"{body_id}.admission_ambiguous",
        dsl.any_of(
            dsl.binary(
                "GT",
                _count("primary_set", ADMISSION),
                dsl.const(PG + "bigint", 1),
            ),
            dsl.binary(
                "GT",
                _count("conflict_set", ADMISSION),
                dsl.const(PG + "bigint", 1),
            ),
            dsl.all_of(
                dsl.eq(
                    _count("primary_set", ADMISSION), dsl.const(PG + "bigint", 1)
                ),
                dsl.eq(
                    _count("conflict_set", ADMISSION),
                    dsl.const(PG + "bigint", 1),
                ),
            ),
        ),
        rebase_branch(
            "ambiguous_admission",
            dsl.const(F + "observation_reason", "MALFORMED_OR_FOREIGN"),
        ),
        [
            _if(
                f"{body_id}.has_primary",
                dsl.eq(
                    _count("primary_set", ADMISSION),
                    dsl.const(PG + "bigint", 1),
                ),
                [
                    _if(
                        f"{body_id}.source_position_exact",
                        dsl.eq(
                            _count("source_position_set", SOURCE),
                            dsl.const(PG + "bigint", 1),
                        ),
                        primary_branch,
                        rebase_branch(
                            "source_ambiguous",
                            dsl.const(
                                F + "observation_reason",
                                "MALFORMED_OR_FOREIGN",
                            ),
                        ),
                    )
                ],
                [
                    *rebase_branch(
                        "missing_admission",
                        dsl.const(
                            F + "observation_reason", "MISSING_ADMISSION"
                        ),
                    )
                ],
            )
        ],
    )
    nodes = [
        _isolation(body_id, "SERIALIZABLE"), *binding_nodes,
        dsl.lock_node(f"{body_id}.lock_barrier", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], mode="FOR_UPDATE", order=1, output_symbol="barrier", columns=COLUMNS[BARRIER]),
        dsl.lock_node(f"{body_id}.lock_generation", relation=GENERATION, predicate=_predicate(GENERATION, loc), key_columns=COORDS, mode="FOR_UPDATE", order=2, output_symbol="generation", columns=COLUMNS[GENERATION]),
        dsl.lock_node(f"{body_id}.lock_checkpoint", relation=CHECKPOINT, predicate=_predicate(CHECKPOINT, loc), key_columns=COORDS, mode="FOR_UPDATE", order=3, output_symbol="checkpoint", columns=COLUMNS[CHECKPOINT]),
        dsl.select_node(f"{body_id}.receipt_set", relation=RECEIPT, columns=COLUMNS[RECEIPT], predicate=receipt_pred, cardinality="COMPLETE_SET", output_symbol="receipt_set", order_by=COORDS+["source_position"], set_read=True),
        dsl.select_node(f"{body_id}.primary_set", relation=ADMISSION, columns=COLUMNS[ADMISSION], predicate=primary_pred, cardinality="COMPLETE_SET", output_symbol="primary_set", order_by=COORDS+["source_position", "entry_kind"], set_read=True),
        dsl.select_node(f"{body_id}.conflict_set", relation=ADMISSION, columns=COLUMNS[ADMISSION], predicate=conflict_pred, cardinality="COMPLETE_SET", output_symbol="conflict_set", order_by=COORDS+["source_position", "entry_kind"], set_read=True),
        dsl.select_node(f"{body_id}.source_position_set", relation=SOURCE, columns=COLUMNS[SOURCE], predicate=source_position_pred, cardinality="COMPLETE_SET", output_symbol="source_position_set", order_by=["practice_id", "source_contract_id", "stream_id", "stream_epoch", "transaction_position"], set_read=True),
        dsl.select_node(f"{body_id}.current_anchor_set", relation=ANCHOR, columns=COLUMNS[ANCHOR], predicate=current_anchor_pred, cardinality="COMPLETE_SET", output_symbol="current_anchor_set", order_by=COORDS+["lifecycle_revision"], set_read=True),
        dsl.select_node(f"{body_id}.current_frame_set", relation=FRAME, columns=COLUMNS[FRAME], predicate=current_frame_pred, cardinality="COMPLETE_SET", output_symbol="current_frame_set", order_by=COORDS+["frame_type", "frame_generation_id"], set_read=True),
        dsl.select_node(f"{body_id}.watermark_set", relation=WATERMARK, columns=COLUMNS[WATERMARK], predicate=watermark_pred, cardinality="COMPLETE_SET", output_symbol="watermark_set", order_by=COORDS+["frame_type"], set_read=True),
        dsl.select_node(f"{body_id}.pending_obligation_set", relation=OBLIGATION, columns=COLUMNS[OBLIGATION], predicate=pending_obligation_pred, cardinality="COMPLETE_SET", output_symbol="pending_obligation_set", order_by=COORDS+["frame_generation_id"], set_read=True),
        _if(
            f"{body_id}.has_conflict_before_receipt",
            dsl.eq(
                _count("conflict_set", ADMISSION),
                dsl.const(PG + "bigint", 1),
            ),
            conflict_branch,
            [
                _if(
                    f"{body_id}.has_receipt",
                    dsl.all_of(
                        dsl.eq(
                            _count("receipt_set", RECEIPT),
                            dsl.const(PG + "bigint", 1),
                        ),
                        dsl.eq(
                            _count("primary_set", ADMISSION),
                            dsl.const(PG + "bigint", 1),
                        ),
                        dsl.eq(
                            _count("conflict_set", ADMISSION),
                            dsl.const(PG + "bigint", 0),
                        ),
                    ),
                    receipt_replay,
                    [
                        _if(
                            f"{body_id}.terminal",
                            dsl.binary("NE", _col("generation", GENERATION, "lifecycle_state"), dsl.const(F+"generation_state", "ACTIVE")),
                            terminal_branch,
                            [admission_state],
                        )
                    ],
                )
            ],
        ),
    ]
    locals_ = [(row["id"], row["type"]) for row in binding_symbols] + [
        ("barrier", BARRIER), ("generation", GENERATION), ("checkpoint", CHECKPOINT), ("anchor", ANCHOR),
        ("terminal_lifecycle", LIFECYCLE), ("terminal_audit", AUDIT), ("terminal_result", result_type),
        ("receipt_set", RECEIPT+"[]"), ("stored_receipt", RECEIPT), ("replay_primary", ADMISSION),
        ("rederived_receipt_digest", F+"digest_sha256"), ("replay_result", result_type),
        ("primary_set", ADMISSION+"[]"), ("conflict_set", ADMISSION+"[]"), ("conflict", ADMISSION),
        ("source_position_set", SOURCE+"[]"), ("source_at_position", SOURCE), ("key_membership_set", KEY+"[]"),
        ("current_anchor_set", ANCHOR+"[]"), ("current_frame_set", FRAME+"[]"), ("watermark_set", WATERMARK+"[]"),
        ("pending_obligation_set", OBLIGATION+"[]"), ("primary", ADMISSION),
        ("diary_frame", FRAME), ("waiting_frame", FRAME), ("diary_watermark", WATERMARK), ("waiting_watermark", WATERMARK),
        *rebase_symbols,
        *dependent_symbols,
        ("applied_lifecycle", LIFECYCLE), ("applied_audit", AUDIT),
        ("inserted_receipt", RECEIPT), ("applied_checkpoint", CHECKPOINT), ("applied_result", result_type),
    ]
    return dsl.body(body_id, "ENTRY_POINT", body_id, _symbols([("admission_locator", ADMISSION_LOC)], locals_), nodes)


def build_registration_body() -> dict[str, Any]:
    body_id = F + "register_observer_generation_v1"
    registration = dsl.input_ref("registration", REGISTRATION)
    locator = _field(registration, "generation_locator", GEN_LOC)
    interval = _field(registration, "initial_key_interval", KEY_INPUT)
    loc = _loc(locator)
    scope = {key: loc[key] for key in ("practice_id", "source_contract_id", "stream_id")}
    binding_nodes, binding_symbols = _binding(body_id, "LIFECYCLE", loc)
    controlling = {
        name: _field(registration, name, F+"digest_sha256")
        for name in ("policy_digest", "principal_digest", "binding_digest", "source_digest", "registry_digest", "impact_digest", "key_schedule_digest")
    }
    initial_start = _field(interval, "interval_start", PG+"bigint")
    initial_end = _field(interval, "interval_end", PG+"bigint")
    initial_key_id = _field(interval, "key_id", F+"key_id")
    initial_attestation = _field(interval, "availability_attestation_digest", F+"digest_sha256")
    head_coordinate = {**scope, "stream_epoch": loc["stream_epoch"]}
    head_bindings = [
        ("practice_id", scope["practice_id"]),
        ("source_contract_id", scope["source_contract_id"]),
        ("stream_id", scope["stream_id"]),
        ("stream_epoch", loc["stream_epoch"]),
        ("last_position", dsl.const(PG + "bigint", 0)),
        ("updated_at", dsl.transaction_timestamp()),
    ]
    create_head_branch = [
        dsl.insert_node(
            f"{body_id}.create_or_reload_head",
            relation=HEAD,
            bindings=head_bindings,
            output_symbol="head",
            returning_columns=COLUMNS[HEAD],
            reload_key=["practice_id", "source_contract_id", "stream_id"],
            winner_predicate=dsl.all_of(
                _predicate(HEAD, head_coordinate),
                dsl.eq(
                    _src(HEAD, "last_position"),
                    dsl.const(PG + "bigint", 0),
                ),
            ),
        )
    ]
    existing_head_branch = [
        dsl.lock_node(
            f"{body_id}.lock_existing_head",
            relation=HEAD,
            predicate=_predicate(HEAD, head_coordinate),
            key_columns=["practice_id", "source_contract_id", "stream_id"],
            mode="FOR_UPDATE",
            order=2,
            output_symbol="head",
            columns=COLUMNS[HEAD],
        )
    ]
    next_position = dsl.add(_col("head", HEAD, "last_position"), dsl.const(PG+"bigint", 1), PG+"bigint")
    baseline_digest = dsl.digest(F+"registration_baseline_digest_v1", [*loc.values(), *controlling.values(), _col("head", HEAD, "last_position"), initial_start, initial_end, initial_key_id, initial_attestation])
    existing_pred = _predicate(GENERATION, loc)
    replay_frame_pred = dsl.all_of(
        _predicate(FRAME, loc),
        dsl.eq(
            _src(FRAME, "lifecycle_state"),
            dsl.const(F + "frame_lifecycle", "CURRENT"),
        ),
    )
    replay_watermark_pred = _predicate(WATERMARK, loc)
    replay_key_pred = dsl.all_of(
        _predicate(KEY, loc),
        dsl.eq(_src(KEY, "interval_start"), initial_start),
    )
    replay_anchor_pred = _predicate(
        ANCHOR,
        {**loc, "lifecycle_revision": dsl.const(PG + "bigint", 0)},
    )
    expected_last_observation = dsl.case(
        F + "digest_sha256",
        [
            {
                "when": dsl.eq(
                    _col("head", HEAD, "last_position"),
                    dsl.const(PG + "bigint", 0),
                ),
                "then": dsl.const(F + "digest_sha256", None),
            }
        ],
        controlling["source_digest"],
    )
    replay_branch = [
        dsl.select_node(f"{body_id}.existing", relation=GENERATION, columns=COLUMNS[GENERATION], predicate=existing_pred, cardinality="EXACTLY_ONE", output_symbol="existing_generation", order_by=COORDS),
        dsl.select_node(f"{body_id}.replay_checkpoint", relation=CHECKPOINT, columns=COLUMNS[CHECKPOINT], predicate=_predicate(CHECKPOINT, loc), cardinality="EXACTLY_ONE", output_symbol="replay_checkpoint", order_by=COORDS),
        dsl.select_node(f"{body_id}.replay_frame_set", relation=FRAME, columns=COLUMNS[FRAME], predicate=replay_frame_pred, cardinality="COMPLETE_SET", output_symbol="replay_frame_set", order_by=COORDS+["frame_type", "frame_generation_id"], set_read=True),
        dsl.select_node(f"{body_id}.replay_diary_frame", relation=FRAME, columns=COLUMNS[FRAME], predicate=dsl.all_of(replay_frame_pred, dsl.eq(_src(FRAME, "frame_type"), dsl.const(F+"frame_type", "CURRENT_DIARY_PROJECTION"))), cardinality="EXACTLY_ONE", output_symbol="replay_diary_frame", order_by=COORDS+["frame_type", "frame_generation_id"]),
        dsl.select_node(f"{body_id}.replay_waiting_frame", relation=FRAME, columns=COLUMNS[FRAME], predicate=dsl.all_of(replay_frame_pred, dsl.eq(_src(FRAME, "frame_type"), dsl.const(F+"frame_type", "CURRENT_WAITING_ROOM_PROJECTION"))), cardinality="EXACTLY_ONE", output_symbol="replay_waiting_frame", order_by=COORDS+["frame_type", "frame_generation_id"]),
        dsl.select_node(f"{body_id}.replay_watermark_set", relation=WATERMARK, columns=COLUMNS[WATERMARK], predicate=replay_watermark_pred, cardinality="COMPLETE_SET", output_symbol="replay_watermark_set", order_by=COORDS+["frame_type"], set_read=True),
        dsl.select_node(f"{body_id}.replay_diary_watermark", relation=WATERMARK, columns=COLUMNS[WATERMARK], predicate=dsl.all_of(replay_watermark_pred, dsl.eq(_src(WATERMARK, "frame_type"), dsl.const(F+"frame_type", "CURRENT_DIARY_PROJECTION"))), cardinality="EXACTLY_ONE", output_symbol="replay_diary_watermark", order_by=COORDS+["frame_type"]),
        dsl.select_node(f"{body_id}.replay_waiting_watermark", relation=WATERMARK, columns=COLUMNS[WATERMARK], predicate=dsl.all_of(replay_watermark_pred, dsl.eq(_src(WATERMARK, "frame_type"), dsl.const(F+"frame_type", "CURRENT_WAITING_ROOM_PROJECTION"))), cardinality="EXACTLY_ONE", output_symbol="replay_waiting_watermark", order_by=COORDS+["frame_type"]),
        dsl.select_node(f"{body_id}.replay_initial_key", relation=KEY, columns=COLUMNS[KEY], predicate=replay_key_pred, cardinality="EXACTLY_ONE", output_symbol="replay_initial_key", order_by=COORDS+["interval_start"]),
        dsl.select_node(f"{body_id}.replay_baseline_anchor", relation=ANCHOR, columns=COLUMNS[ANCHOR], predicate=replay_anchor_pred, cardinality="EXACTLY_ONE", output_symbol="replay_baseline_anchor", order_by=COORDS+["lifecycle_revision"]),
        dsl.assert_node(
            f"{body_id}.replay_exact",
            dsl.all_of(
                dsl.eq(_col("existing_generation", GENERATION, "lifecycle_state"), dsl.const(F+"generation_state", "ACTIVE")),
                dsl.unary("IS_NULL", _col("existing_generation", GENERATION, "consumed_at")),
                dsl.unary("IS_NULL", _col("existing_generation", GENERATION, "terminal_reason")),
                *(dsl.eq(_col("existing_generation", GENERATION, name), value) for name, value in controlling.items()),
                dsl.eq(_col("replay_checkpoint", CHECKPOINT, "checkpoint_state"), dsl.const(F+"checkpoint_state", "ACTIVE")),
                dsl.eq(_col("replay_checkpoint", CHECKPOINT, "last_contiguous_position"), _col("head", HEAD, "last_position")),
                dsl.eq(_col("replay_checkpoint", CHECKPOINT, "last_observation_digest"), expected_last_observation),
                dsl.eq(_col("replay_checkpoint", CHECKPOINT, "lifecycle_revision"), dsl.const(PG+"bigint", 0)),
                dsl.eq(_col("replay_checkpoint", CHECKPOINT, "audit_head_digest"), baseline_digest),
                dsl.eq(_col("replay_checkpoint", CHECKPOINT, "checkpoint_integrity_digest"), baseline_digest),
                dsl.eq(_count("replay_frame_set", FRAME), dsl.const(PG+"bigint", 2)),
                dsl.binary("NE", _col("replay_diary_frame", FRAME, "frame_generation_id"), _col("replay_waiting_frame", FRAME, "frame_generation_id")),
                dsl.eq(_col("replay_diary_frame", FRAME, "frame_type"), dsl.const(F+"frame_type", "CURRENT_DIARY_PROJECTION")),
                dsl.eq(_col("replay_waiting_frame", FRAME, "frame_type"), dsl.const(F+"frame_type", "CURRENT_WAITING_ROOM_PROJECTION")),
                dsl.eq(_col("replay_diary_frame", FRAME, "assembled_through_position"), _col("head", HEAD, "last_position")),
                dsl.eq(_col("replay_waiting_frame", FRAME, "assembled_through_position"), _col("head", HEAD, "last_position")),
                dsl.eq(_count("replay_watermark_set", WATERMARK), dsl.const(PG+"bigint", 2)),
                dsl.eq(_col("replay_diary_watermark", WATERMARK, "frame_type"), dsl.const(F+"frame_type", "CURRENT_DIARY_PROJECTION")),
                dsl.eq(_col("replay_waiting_watermark", WATERMARK, "frame_type"), dsl.const(F+"frame_type", "CURRENT_WAITING_ROOM_PROJECTION")),
                dsl.eq(_col("replay_diary_watermark", WATERMARK, "watermark_position"), _col("head", HEAD, "last_position")),
                dsl.eq(_col("replay_waiting_watermark", WATERMARK, "watermark_position"), _col("head", HEAD, "last_position")),
                dsl.eq(_col("replay_initial_key", KEY, "interval_start"), initial_start),
                dsl.eq(_col("replay_initial_key", KEY, "interval_end"), initial_end),
                dsl.eq(_col("replay_initial_key", KEY, "key_id"), initial_key_id),
                dsl.eq(_col("replay_initial_key", KEY, "availability_attestation_digest"), initial_attestation),
                dsl.eq(_col("replay_baseline_anchor", ANCHOR, "lifecycle_revision"), dsl.const(PG+"bigint", 0)),
                dsl.eq(_col("replay_baseline_anchor", ANCHOR, "checkpoint_state"), dsl.const(F+"checkpoint_state", "ACTIVE")),
                dsl.eq(_col("replay_baseline_anchor", ANCHOR, "last_contiguous_position"), _col("head", HEAD, "last_position")),
                dsl.eq(_col("replay_baseline_anchor", ANCHOR, "last_observation_digest"), expected_last_observation),
                *(dsl.eq(_col("replay_baseline_anchor", ANCHOR, name), value) for name, value in controlling.items()),
                dsl.eq(_col("replay_baseline_anchor", ANCHOR, "checkpoint_integrity_digest"), baseline_digest),
                dsl.eq(_col("replay_baseline_anchor", ANCHOR, "anchor_digest"), baseline_digest),
                dsl.eq(_col("head", HEAD, "stream_epoch"), loc["stream_epoch"]),
                dsl.eq(_col("head", HEAD, "last_position"), _col("replay_checkpoint", CHECKPOINT, "last_contiguous_position")),
            ),
            "F_REGISTRATION",
        ),
        _retry_or_return(body_id, "registration_replay", "existing_generation", GENERATION),
    ]
    generation_bindings = [(name, loc[name]) for name in COORDS] + [
        ("lifecycle_state", dsl.const(F+"generation_state", "ACTIVE")),
        *controlling.items(),
        ("created_at", dsl.transaction_timestamp()),
        ("consumed_at", dsl.const(PG+"timestamptz", None)),
        ("terminal_reason", dsl.const(F+"generation_terminal_reason", None)),
    ]
    checkpoint_bindings = [(name, loc[name]) for name in COORDS] + [
        ("checkpoint_state", dsl.const(F+"checkpoint_state", "ACTIVE")),
        ("last_contiguous_position", _col("head", HEAD, "last_position")),
        ("last_observation_digest", dsl.case(F+"digest_sha256", [{"when": dsl.eq(_col("head", HEAD, "last_position"), dsl.const(PG+"bigint", 0)), "then": dsl.const(F+"digest_sha256", None)}], controlling["source_digest"])),
        ("lifecycle_revision", dsl.const(PG+"bigint", 0)),
        ("audit_head_digest", baseline_digest), ("checkpoint_integrity_digest", baseline_digest),
        ("updated_at", dsl.transaction_timestamp()),
    ]
    def frame_bindings(frame_type: str, frame_id: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
        return [(name, loc[name]) for name in COORDS] + [
            ("frame_generation_id", frame_id), ("frame_type", dsl.const(F+"frame_type", frame_type)),
            ("assembled_through_position", _col("head", HEAD, "last_position")), ("lifecycle_state", dsl.const(F+"frame_lifecycle", "CURRENT")),
            ("created_at", dsl.transaction_timestamp()), ("retired_at", dsl.const(PG+"timestamptz", None)),
        ]
    def watermark_bindings(frame_type: str) -> list[tuple[str, dict[str, Any]]]:
        return [(name, loc[name]) for name in COORDS] + [
            ("frame_type", dsl.const(F+"frame_type", frame_type)), ("watermark_position", _col("head", HEAD, "last_position")),
            ("updated_at", dsl.transaction_timestamp()),
        ]
    key_bindings = [(name, loc[name]) for name in COORDS] + [
        ("interval_start", initial_start), ("interval_end", initial_end), ("key_id", initial_key_id),
        ("availability_attestation_digest", initial_attestation), ("created_at", dsl.transaction_timestamp()),
    ]
    anchor_bindings = [(name, loc[name]) for name in COORDS] + [
        ("lifecycle_revision", dsl.const(PG+"bigint", 0)), ("checkpoint_state", dsl.const(F+"checkpoint_state", "ACTIVE")),
        ("last_contiguous_position", _col("head", HEAD, "last_position")),
        ("last_observation_digest", dsl.case(F+"digest_sha256", [{"when": dsl.eq(_col("head", HEAD, "last_position"), dsl.const(PG+"bigint", 0)), "then": dsl.const(F+"digest_sha256", None)}], controlling["source_digest"])),
        *controlling.items(), ("checkpoint_integrity_digest", baseline_digest), ("anchor_digest", baseline_digest), ("created_at", dsl.transaction_timestamp()),
    ]
    new_branch = [
        dsl.assert_node(f"{body_id}.initial_key_start", dsl.eq(initial_start, next_position), "F_KEY_PARTITION"),
        dsl.assert_node(f"{body_id}.initial_key_order", dsl.binary("GTE", initial_end, initial_start), "F_KEY_PARTITION"),
        _insert_reload(f"{body_id}.generation_insert", GENERATION, generation_bindings, "inserted_generation", COORDS),
        _insert_reload(f"{body_id}.checkpoint_insert", CHECKPOINT, checkpoint_bindings, "inserted_checkpoint", COORDS),
        dsl.let_node(f"{body_id}.diary_frame_id", "diary_frame_id", PG+"uuid", dsl.uuid_v4()),
        dsl.let_node(f"{body_id}.waiting_frame_id", "waiting_frame_id", PG+"uuid", dsl.uuid_v4()),
        _insert_reload(f"{body_id}.diary_frame", FRAME, frame_bindings("CURRENT_DIARY_PROJECTION", dsl.local_ref("diary_frame_id", PG+"uuid")), "diary_frame", COORDS+["frame_generation_id"]),
        _insert_reload(f"{body_id}.waiting_frame", FRAME, frame_bindings("CURRENT_WAITING_ROOM_PROJECTION", dsl.local_ref("waiting_frame_id", PG+"uuid")), "waiting_frame", COORDS+["frame_generation_id"]),
        _insert_reload(f"{body_id}.diary_watermark", WATERMARK, watermark_bindings("CURRENT_DIARY_PROJECTION"), "diary_watermark", COORDS+["frame_type"]),
        _insert_reload(f"{body_id}.waiting_watermark", WATERMARK, watermark_bindings("CURRENT_WAITING_ROOM_PROJECTION"), "waiting_watermark", COORDS+["frame_type"]),
        _insert_reload(f"{body_id}.initial_key", KEY, key_bindings, "initial_key", COORDS+["interval_start"]),
        _insert_reload(f"{body_id}.baseline_anchor", ANCHOR, anchor_bindings, "baseline_anchor", COORDS+["lifecycle_revision"]),
        dsl.update_node(f"{body_id}.barrier_update", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], bindings=[
            ("barrier_revision", dsl.add(_col("barrier", BARRIER, "barrier_revision"), dsl.const(PG+"bigint", 1), PG+"bigint")),
            ("updated_at", dsl.transaction_timestamp()),
        ], output_symbol="updated_barrier", returning_columns=COLUMNS[BARRIER]),
        _retry_or_return(body_id, "registration_insert", "inserted_generation", GENERATION),
    ]
    nodes = [
        _isolation(body_id, "SERIALIZABLE"), *binding_nodes,
        dsl.lock_node(f"{body_id}.lock_barrier", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], mode="FOR_UPDATE", order=1, output_symbol="barrier", columns=COLUMNS[BARRIER]),
        dsl.select_node(f"{body_id}.head_set", relation=HEAD, columns=COLUMNS[HEAD], predicate=_predicate(HEAD, head_coordinate), cardinality="COMPLETE_SET", output_symbol="head_set", order_by=["practice_id", "source_contract_id", "stream_id"], set_read=True),
        dsl.assert_node(f"{body_id}.head_unambiguous", dsl.binary("LTE", _count("head_set", HEAD), dsl.const(PG+"bigint", 1)), "F_REGISTRATION"),
        _if_rejoin(
            f"{body_id}.create_or_use_head",
            dsl.eq(_count("head_set", HEAD), dsl.const(PG+"bigint", 0)),
            create_head_branch,
            existing_head_branch,
        ),
        dsl.select_node(f"{body_id}.existing_set", relation=GENERATION, columns=COLUMNS[GENERATION], predicate=existing_pred, cardinality="COMPLETE_SET", output_symbol="existing_set", order_by=COORDS, set_read=True),
        dsl.assert_node(f"{body_id}.registration_unambiguous", dsl.binary("LTE", _count("existing_set", GENERATION), dsl.const(PG+"bigint", 1)), "F_REGISTRATION"),
        _if(f"{body_id}.registered", dsl.eq(_count("existing_set", GENERATION), dsl.const(PG+"bigint", 1)), replay_branch, new_branch),
    ]
    locals_ = [(row["id"], row["type"]) for row in binding_symbols] + [
        ("barrier", BARRIER), ("head_set", HEAD+"[]"), ("head", HEAD),
        ("existing_set", GENERATION+"[]"), ("existing_generation", GENERATION),
        ("replay_checkpoint", CHECKPOINT), ("replay_frame_set", FRAME+"[]"),
        ("replay_diary_frame", FRAME), ("replay_waiting_frame", FRAME),
        ("replay_watermark_set", WATERMARK+"[]"),
        ("replay_diary_watermark", WATERMARK), ("replay_waiting_watermark", WATERMARK),
        ("replay_initial_key", KEY), ("replay_baseline_anchor", ANCHOR),
        ("inserted_generation", GENERATION), ("inserted_checkpoint", CHECKPOINT), ("diary_frame_id", PG+"uuid"), ("waiting_frame_id", PG+"uuid"),
        ("diary_frame", FRAME), ("waiting_frame", FRAME), ("diary_watermark", WATERMARK), ("waiting_watermark", WATERMARK),
        ("initial_key", KEY), ("baseline_anchor", ANCHOR), ("updated_barrier", BARRIER),
    ]
    return dsl.body(body_id, "ENTRY_POINT", body_id, _symbols([("registration", REGISTRATION)], locals_), nodes)


def build_anchor_body() -> dict[str, Any]:
    body_id = F + "append_recovery_anchor_v1"
    locator = dsl.input_ref("generation_locator", GEN_LOC)
    requested_revision = dsl.input_ref("lifecycle_revision", PG+"bigint")
    loc = _loc(locator)
    scope = {key: loc[key] for key in ("practice_id", "source_contract_id", "stream_id")}
    binding_nodes, binding_symbols = _binding(body_id, "LIFECYCLE", loc)
    anchor_coord = {**loc, "lifecycle_revision": requested_revision}
    anchor_digest = dsl.digest(F+"recovery_anchor_digest_v1", [
        *loc.values(), requested_revision, _col("checkpoint", CHECKPOINT, "checkpoint_state"),
        _col("checkpoint", CHECKPOINT, "last_contiguous_position"), _col("checkpoint", CHECKPOINT, "last_observation_digest"),
        *(_col("generation", GENERATION, name) for name in ("policy_digest", "principal_digest", "binding_digest", "source_digest", "registry_digest", "impact_digest", "key_schedule_digest")),
        _col("checkpoint", CHECKPOINT, "checkpoint_integrity_digest"),
    ])
    anchor_bindings = [(name, loc[name]) for name in COORDS] + [
        ("lifecycle_revision", requested_revision),
        ("checkpoint_state", _col("checkpoint", CHECKPOINT, "checkpoint_state")),
        ("last_contiguous_position", _col("checkpoint", CHECKPOINT, "last_contiguous_position")),
        ("last_observation_digest", _col("checkpoint", CHECKPOINT, "last_observation_digest")),
        *[(name, _col("generation", GENERATION, name)) for name in ("policy_digest", "principal_digest", "binding_digest", "source_digest", "registry_digest", "impact_digest", "key_schedule_digest")],
        ("checkpoint_integrity_digest", _col("checkpoint", CHECKPOINT, "checkpoint_integrity_digest")),
        ("anchor_digest", anchor_digest), ("created_at", dsl.transaction_timestamp()),
    ]
    replay_branch = [
        dsl.select_node(f"{body_id}.stored", relation=ANCHOR, columns=COLUMNS[ANCHOR], predicate=_predicate(ANCHOR, anchor_coord), cardinality="EXACTLY_ONE", output_symbol="stored_anchor", order_by=COORDS+["lifecycle_revision"]),
        dsl.assert_node(f"{body_id}.stored_exact", dsl.eq(_col("stored_anchor", ANCHOR, "anchor_digest"), anchor_digest), "F_ANCHOR"),
        _retry_or_return(body_id, "anchor_replay", "stored_anchor", ANCHOR),
    ]
    insert_branch = [
        _insert_reload(f"{body_id}.insert", ANCHOR, anchor_bindings, "inserted_anchor", COORDS+["lifecycle_revision"]),
        _retry_or_return(body_id, "anchor_insert", "inserted_anchor", ANCHOR),
    ]
    nodes = [
        _isolation(body_id, "SERIALIZABLE"), *binding_nodes,
        dsl.lock_node(f"{body_id}.lock_barrier", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], mode="FOR_UPDATE", order=1, output_symbol="barrier", columns=COLUMNS[BARRIER]),
        dsl.lock_node(f"{body_id}.lock_generation", relation=GENERATION, predicate=_predicate(GENERATION, loc), key_columns=COORDS, mode="FOR_SHARE", order=2, output_symbol="generation", columns=COLUMNS[GENERATION]),
        dsl.lock_node(f"{body_id}.lock_checkpoint", relation=CHECKPOINT, predicate=_predicate(CHECKPOINT, loc), key_columns=COORDS, mode="FOR_SHARE", order=3, output_symbol="checkpoint", columns=COLUMNS[CHECKPOINT]),
        dsl.assert_node(f"{body_id}.revision", dsl.eq(requested_revision, _col("checkpoint", CHECKPOINT, "lifecycle_revision")), "F_ANCHOR"),
        dsl.select_node(f"{body_id}.anchor_set", relation=ANCHOR, columns=COLUMNS[ANCHOR], predicate=_predicate(ANCHOR, anchor_coord), cardinality="COMPLETE_SET", output_symbol="anchor_set", order_by=COORDS+["lifecycle_revision"], set_read=True),
        _if(f"{body_id}.exists", dsl.eq(_count("anchor_set", ANCHOR), dsl.const(PG+"bigint", 1)), replay_branch, insert_branch),
    ]
    locals_ = [(row["id"], row["type"]) for row in binding_symbols] + [
        ("barrier", BARRIER), ("generation", GENERATION), ("checkpoint", CHECKPOINT), ("anchor_set", ANCHOR+"[]"),
        ("stored_anchor", ANCHOR), ("inserted_anchor", ANCHOR),
    ]
    return dsl.body(body_id, "ENTRY_POINT", body_id, _symbols([("generation_locator", GEN_LOC), ("lifecycle_revision", PG+"bigint")], locals_), nodes)


def build_rotation_body() -> dict[str, Any]:
    body_id = F + "rotate_observation_key_v1"
    locator = dsl.input_ref("generation_locator", GEN_LOC)
    interval = dsl.input_ref("future_interval", KEY_INPUT)
    loc = _loc(locator)
    scope = {key: loc[key] for key in ("practice_id", "source_contract_id", "stream_id")}
    binding_nodes, binding_symbols = _binding(body_id, "LIFECYCLE", loc)
    start = _field(interval, "interval_start", PG+"bigint")
    end = _field(interval, "interval_end", PG+"bigint")
    key_id = _field(interval, "key_id", F+"key_id")
    attestation = _field(interval, "availability_attestation_digest", F+"digest_sha256")
    key_coord = {**loc, "interval_start": start}
    existing_pred = _predicate(KEY, key_coord)
    replay_branch = [
        dsl.select_node(f"{body_id}.stored_key", relation=KEY, columns=COLUMNS[KEY], predicate=existing_pred, cardinality="EXACTLY_ONE", output_symbol="stored_key", order_by=COORDS+["interval_start"]),
        dsl.assert_node(f"{body_id}.replay_exact", dsl.all_of(
            dsl.eq(_col("stored_key", KEY, "interval_end"), end), dsl.eq(_col("stored_key", KEY, "key_id"), key_id),
            dsl.eq(_col("stored_key", KEY, "availability_attestation_digest"), attestation),
        ), "F_KEY_PARTITION"),
        _retry_or_return(body_id, "rotation_replay", "stored_key", KEY),
    ]
    next_revision = dsl.add(_col("checkpoint", CHECKPOINT, "lifecycle_revision"), dsl.const(PG+"bigint", 1), PG+"bigint")
    rotation_digest = dsl.digest(F+"key_rotation_digest_v1", [*loc.values(), start, end, key_id, attestation, _col("anchor", ANCHOR, "anchor_digest"), next_revision])
    key_bindings = [(name, loc[name]) for name in COORDS] + [
        ("interval_start", start), ("interval_end", end), ("key_id", key_id),
        ("availability_attestation_digest", attestation), ("created_at", dsl.transaction_timestamp()),
    ]
    lifecycle_bindings = [(name, loc[name]) for name in COORDS] + [
        ("lifecycle_revision", next_revision), ("entry_kind", dsl.const(F+"lifecycle_entry_kind", "KEY_ROTATION")),
        ("source_position", _col("checkpoint", CHECKPOINT, "last_contiguous_position")), ("key_interval_start", start), ("key_interval_end", end),
        ("prior_lifecycle_digest", _col("anchor", ANCHOR, "anchor_digest")), ("lifecycle_digest", rotation_digest), ("created_at", dsl.transaction_timestamp()),
    ]
    new_branch = [
        dsl.lock_node(f"{body_id}.lock_anchor", relation=ANCHOR, predicate=_predicate(ANCHOR, {**loc, "lifecycle_revision": _col("checkpoint", CHECKPOINT, "lifecycle_revision")}), key_columns=COORDS+["lifecycle_revision"], mode="FOR_SHARE", order=4, output_symbol="anchor", columns=COLUMNS[ANCHOR]),
        dsl.lock_node(f"{body_id}.lock_prior_key", relation=KEY, predicate=dsl.all_of(_predicate(KEY, loc), dsl.eq(dsl.add(_src(KEY, "interval_end"), dsl.const(PG+"bigint", 1), PG+"bigint"), start)), key_columns=COORDS+["interval_start"], mode="FOR_UPDATE", order=5, output_symbol="prior_key", columns=COLUMNS[KEY]),
        dsl.assert_node(f"{body_id}.future_fence", dsl.binary("GT", start, _col("checkpoint", CHECKPOINT, "last_contiguous_position")), "F_KEY_PARTITION"),
        dsl.assert_node(f"{body_id}.interval_order", dsl.binary("GTE", end, start), "F_KEY_PARTITION"),
        _insert_reload(f"{body_id}.key_insert", KEY, key_bindings, "inserted_key", COORDS+["interval_start"]),
        _insert_reload(f"{body_id}.lifecycle_insert", LIFECYCLE, lifecycle_bindings, "rotation_lifecycle", COORDS+["lifecycle_revision"]),
        dsl.update_node(f"{body_id}.generation_update", relation=GENERATION, predicate=_predicate(GENERATION, loc), key_columns=COORDS, bindings=[("key_schedule_digest", rotation_digest)], output_symbol="rotated_generation", returning_columns=COLUMNS[GENERATION]),
        dsl.update_node(f"{body_id}.checkpoint_update", relation=CHECKPOINT, predicate=_predicate(CHECKPOINT, loc), key_columns=COORDS, bindings=[
            ("lifecycle_revision", next_revision), ("checkpoint_integrity_digest", rotation_digest), ("updated_at", dsl.transaction_timestamp()),
        ], output_symbol="rotated_checkpoint", returning_columns=COLUMNS[CHECKPOINT]),
        _retry_or_return(body_id, "rotation_insert", "inserted_key", KEY),
    ]
    nodes = [
        _isolation(body_id, "SERIALIZABLE"), *binding_nodes,
        dsl.lock_node(f"{body_id}.lock_barrier", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], mode="FOR_UPDATE", order=1, output_symbol="barrier", columns=COLUMNS[BARRIER]),
        dsl.lock_node(f"{body_id}.lock_generation", relation=GENERATION, predicate=_predicate(GENERATION, loc), key_columns=COORDS, mode="FOR_UPDATE", order=2, output_symbol="generation", columns=COLUMNS[GENERATION]),
        dsl.lock_node(f"{body_id}.lock_checkpoint", relation=CHECKPOINT, predicate=_predicate(CHECKPOINT, loc), key_columns=COORDS, mode="FOR_UPDATE", order=3, output_symbol="checkpoint", columns=COLUMNS[CHECKPOINT]),
        dsl.select_node(f"{body_id}.existing_set", relation=KEY, columns=COLUMNS[KEY], predicate=existing_pred, cardinality="COMPLETE_SET", output_symbol="existing_key_set", order_by=COORDS+["interval_start"], set_read=True),
        _if(f"{body_id}.replay", dsl.eq(_count("existing_key_set", KEY), dsl.const(PG+"bigint", 1)), replay_branch, new_branch),
    ]
    locals_ = [(row["id"], row["type"]) for row in binding_symbols] + [
        ("barrier", BARRIER), ("generation", GENERATION), ("checkpoint", CHECKPOINT), ("existing_key_set", KEY+"[]"),
        ("stored_key", KEY), ("anchor", ANCHOR), ("prior_key", KEY), ("inserted_key", KEY), ("rotation_lifecycle", LIFECYCLE),
        ("rotated_generation", GENERATION), ("rotated_checkpoint", CHECKPOINT),
    ]
    return dsl.body(body_id, "ENTRY_POINT", body_id, _symbols([("generation_locator", GEN_LOC), ("future_interval", KEY_INPUT)], locals_), nodes)


def build_consumption_body() -> dict[str, Any]:
    body_id = F + "consume_observer_generation_v1"
    locator = dsl.input_ref("generation_locator", GEN_LOC)
    closed_reason = dsl.input_ref("closed_reason", F+"generation_terminal_reason")
    loc = _loc(locator)
    scope = {key: loc[key] for key in ("practice_id", "source_contract_id", "stream_id")}
    binding_nodes, binding_symbols = _binding(body_id, "LIFECYCLE", loc)
    terminal = dsl.binary("NE", _col("generation", GENERATION, "lifecycle_state"), dsl.const(F+"generation_state", "ACTIVE"))
    replay_branch = [
        dsl.assert_node(f"{body_id}.reason_exact", dsl.eq(_col("generation", GENERATION, "terminal_reason"), closed_reason), "F_TERMINAL_REASON"),
        _retry_or_return(body_id, "terminal_replay", "generation", GENERATION),
    ]
    target_state = dsl.case(F+"generation_state", [{"when": dsl.eq(closed_reason, dsl.const(F+"generation_terminal_reason", "REVOKED")), "then": dsl.const(F+"generation_state", "REVOKED")}], dsl.const(F+"generation_state", "CONSUMED"))
    consumed_at = dsl.case(PG+"timestamptz", [{"when": dsl.eq(closed_reason, dsl.const(F+"generation_terminal_reason", "REVOKED")), "then": dsl.const(PG+"timestamptz", None)}], dsl.transaction_timestamp())
    consume_branch = [
        dsl.update_node(f"{body_id}.generation_update", relation=GENERATION, predicate=_predicate(GENERATION, loc), key_columns=COORDS, bindings=[
            ("lifecycle_state", target_state), ("terminal_reason", closed_reason), ("consumed_at", consumed_at),
        ], output_symbol="consumed_generation", returning_columns=COLUMNS[GENERATION]),
        dsl.update_node(f"{body_id}.barrier_update", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], bindings=[
            ("barrier_revision", dsl.add(_col("barrier", BARRIER, "barrier_revision"), dsl.const(PG+"bigint", 1), PG+"bigint")),
            ("updated_at", dsl.transaction_timestamp()),
        ], output_symbol="updated_barrier", returning_columns=COLUMNS[BARRIER]),
        _retry_or_return(body_id, "consumed", "consumed_generation", GENERATION),
    ]
    nodes = [
        _isolation(body_id, "SERIALIZABLE"), *binding_nodes,
        dsl.lock_node(f"{body_id}.lock_barrier", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], mode="FOR_UPDATE", order=1, output_symbol="barrier", columns=COLUMNS[BARRIER]),
        dsl.lock_node(f"{body_id}.lock_generation", relation=GENERATION, predicate=_predicate(GENERATION, loc), key_columns=COORDS, mode="FOR_UPDATE", order=2, output_symbol="generation", columns=COLUMNS[GENERATION]),
        _if(f"{body_id}.already_terminal", terminal, replay_branch, consume_branch),
    ]
    locals_ = [(row["id"], row["type"]) for row in binding_symbols] + [
        ("barrier", BARRIER), ("generation", GENERATION), ("consumed_generation", GENERATION), ("updated_barrier", BARRIER),
    ]
    return dsl.body(body_id, "ENTRY_POINT", body_id, _symbols([("generation_locator", GEN_LOC), ("closed_reason", F+"generation_terminal_reason")], locals_), nodes)


def _retention_census_nodes(body_id: str, scope: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    generation_pred = dsl.all_of(
        _predicate(GENERATION, scope),
        dsl.binary(
            "NE",
            _src(GENERATION, "lifecycle_state"),
            dsl.const(F + "generation_state", "CONSUMED"),
        ),
    )
    policy_pred = dsl.all_of(
        _predicate(POLICY, scope),
        dsl.binary("LTE", _src(POLICY, "effective_at"), dsl.transaction_timestamp()),
    )
    pin_pred = dsl.all_of(
        _predicate(PIN, scope),
        _generation_membership(PIN, include_epoch=False),
        dsl.eq(_src(PIN, "pin_state"), dsl.const(F+"recovery_pin_state", "ACTIVE")),
    )
    checkpoint_pred = dsl.all_of(
        _predicate(CHECKPOINT, scope),
        _generation_membership(CHECKPOINT),
    )
    anchor_pred = dsl.all_of(
        _predicate(ANCHOR, scope),
        _generation_membership(ANCHOR),
    )
    key_pred = dsl.all_of(
        _predicate(KEY, scope),
        _generation_membership(KEY),
    )
    receipt_pred = dsl.all_of(
        _predicate(RECEIPT, scope),
        _generation_membership(RECEIPT),
    )
    audit_pred = dsl.all_of(
        _predicate(AUDIT, scope),
        _generation_membership(AUDIT),
    )
    return [
        dsl.select_node(f"{body_id}.head", relation=HEAD, columns=COLUMNS[HEAD], predicate=_predicate(HEAD, scope), cardinality="EXACTLY_ONE", output_symbol="retention_head", order_by=["practice_id", "source_contract_id", "stream_id"]),
        dsl.select_node(f"{body_id}.policies", relation=POLICY, columns=COLUMNS[POLICY], predicate=policy_pred, cardinality="COMPLETE_SET", output_symbol="policy_set", order_by=["practice_id", "source_contract_id", "stream_id", "policy_revision"], set_read=True),
        dsl.select_node(f"{body_id}.generations", relation=GENERATION, columns=COLUMNS[GENERATION], predicate=generation_pred, cardinality="COMPLETE_SET", output_symbol="generation_set", order_by=COORDS, set_read=True),
        dsl.select_node(f"{body_id}.checkpoints", relation=CHECKPOINT, columns=COLUMNS[CHECKPOINT], predicate=checkpoint_pred, cardinality="COMPLETE_SET", output_symbol="checkpoint_set", order_by=COORDS+["last_contiguous_position"], set_read=True),
        dsl.select_node(f"{body_id}.anchors", relation=ANCHOR, columns=COLUMNS[ANCHOR], predicate=anchor_pred, cardinality="COMPLETE_SET", output_symbol="anchor_set", order_by=COORDS+["lifecycle_revision"], set_read=True),
        dsl.select_node(f"{body_id}.pins", relation=PIN, columns=COLUMNS[PIN], predicate=pin_pred, cardinality="COMPLETE_SET", output_symbol="pin_set", order_by=["practice_id", "source_contract_id", "stream_id", "pin_id"], set_read=True),
        dsl.select_node(f"{body_id}.keys", relation=KEY, columns=COLUMNS[KEY], predicate=key_pred, cardinality="COMPLETE_SET", output_symbol="key_set", order_by=COORDS+["interval_start"], set_read=True),
        dsl.select_node(f"{body_id}.source_rows", relation=SOURCE, columns=COLUMNS[SOURCE], predicate=_predicate(SOURCE, scope), cardinality="COMPLETE_SET", output_symbol="source_set", order_by=["practice_id", "source_contract_id", "stream_id", "stream_epoch", "transaction_position"], set_read=True),
        dsl.select_node(f"{body_id}.receipts", relation=RECEIPT, columns=COLUMNS[RECEIPT], predicate=receipt_pred, cardinality="COMPLETE_SET", output_symbol="retention_receipt_set", order_by=COORDS+["source_position"], set_read=True),
        dsl.select_node(f"{body_id}.audits", relation=AUDIT, columns=COLUMNS[AUDIT], predicate=audit_pred, cardinality="COMPLETE_SET", output_symbol="retention_audit_set", order_by=COORDS+["lifecycle_revision"], set_read=True),
    ]


def _generation_row_scope(
    *,
    include_epoch: bool = True,
) -> dict[str, dict[str, Any]]:
    names = ["practice_id", "source_contract_id", "stream_id"]
    if include_epoch:
        names.append("stream_epoch")
    names.extend(["observer_id", "observer_generation"])
    return {
        name: _col("census_generation", GENERATION, name)
        for name in names
    }


def _generation_membership(
    source_relation: str,
    *,
    include_epoch: bool = True,
) -> dict[str, Any]:
    columns = list(COORDS)
    if not include_epoch:
        columns.remove("stream_epoch")
    return dsl.set_contains_key(
        "generation_set",
        GENERATION,
        source_relation,
        [(column, column) for column in columns],
    )


def _key_overlap_coverage() -> dict[str, Any]:
    return dsl.set_covers_keys(
        "generation_set",
        GENERATION,
        "overlapping_key_set",
        KEY,
        [(column, column) for column in COORDS],
    )


def _retention_proof_nodes(
    body_id: str,
    scope: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    through = dsl.local_ref("slowest_checkpoint_position", PG + "bigint")
    now = dsl.transaction_timestamp()
    required_source_pred = dsl.all_of(
        _predicate(SOURCE, scope),
        dsl.binary("LTE", _src(SOURCE, "transaction_position"), through),
    )
    mature_source_pred = dsl.all_of(
        required_source_pred,
        dsl.binary(
            "LTE",
            dsl.binary(
                "TIMESTAMP_ADD_SECONDS",
                _src(SOURCE, "transaction_authored_at"),
                _col("retention_policy", POLICY, "source_grace_seconds"),
                PG + "timestamptz",
            ),
            now,
        ),
    )
    mature_checkpoint_pred = dsl.all_of(
        _predicate(CHECKPOINT, scope),
        _generation_membership(CHECKPOINT),
        dsl.binary(
            "LTE",
            dsl.binary(
                "TIMESTAMP_ADD_SECONDS",
                _src(CHECKPOINT, "updated_at"),
                _col(
                    "retention_policy",
                    POLICY,
                    "receipt_checkpoint_grace_seconds",
                ),
                PG + "timestamptz",
            ),
            now,
        ),
    )
    mature_receipt_pred = dsl.all_of(
        _predicate(RECEIPT, scope),
        _generation_membership(RECEIPT),
        dsl.binary(
            "LTE",
            dsl.binary(
                "TIMESTAMP_ADD_SECONDS",
                _src(RECEIPT, "created_at"),
                _col(
                    "retention_policy",
                    POLICY,
                    "receipt_checkpoint_grace_seconds",
                ),
                PG + "timestamptz",
            ),
            now,
        ),
    )
    mature_audit_pred = dsl.all_of(
        _predicate(AUDIT, scope),
        _generation_membership(AUDIT),
        dsl.binary(
            "LTE",
            dsl.binary(
                "TIMESTAMP_ADD_SECONDS",
                _src(AUDIT, "created_at"),
                _col("retention_policy", POLICY, "audit_grace_seconds"),
                PG + "timestamptz",
            ),
            now,
        ),
    )
    overlapping_key_pred = dsl.all_of(
        _predicate(KEY, scope),
        _generation_membership(KEY),
        dsl.binary("LTE", _src(KEY, "interval_start"), through),
        dsl.binary("GTE", _src(KEY, "interval_end"), through),
        dsl.binary(
            "LTE",
            dsl.binary(
                "TIMESTAMP_ADD_SECONDS",
                _src(KEY, "created_at"),
                _col("retention_policy", POLICY, "key_overlap_seconds"),
                PG + "timestamptz",
            ),
            now,
        ),
    )
    generation_checkpoint_pred = _predicate(CHECKPOINT, _generation_row_scope())
    generation_anchor_pred = _predicate(
        ANCHOR,
        {
            **_generation_row_scope(),
            "lifecycle_revision": _col(
                "census_checkpoint", CHECKPOINT, "lifecycle_revision"
            ),
        },
    )
    generation_key_pred = dsl.all_of(
        _predicate(KEY, _generation_row_scope()),
        dsl.binary("LTE", _src(KEY, "interval_start"), through),
        dsl.binary("GTE", _src(KEY, "interval_end"), through),
    )
    generation_pin_pred = dsl.all_of(
        _predicate(PIN, _generation_row_scope(include_epoch=False)),
        dsl.eq(
            _src(PIN, "pin_state"),
            dsl.const(F + "recovery_pin_state", "ACTIVE"),
        ),
    )
    generation_loop = dsl.node(
        f"{body_id}.generation_census_proof",
        "FOR_EACH",
        set_symbol="generation_set",
        row_symbol="census_generation",
        nodes=[
            dsl.select_node(
                f"{body_id}.generation_checkpoint",
                relation=CHECKPOINT,
                columns=COLUMNS[CHECKPOINT],
                predicate=generation_checkpoint_pred,
                cardinality="EXACTLY_ONE",
                output_symbol="census_checkpoint",
                order_by=COORDS,
            ),
            dsl.select_node(
                f"{body_id}.generation_anchor",
                relation=ANCHOR,
                columns=COLUMNS[ANCHOR],
                predicate=generation_anchor_pred,
                cardinality="EXACTLY_ONE",
                output_symbol="census_anchor",
                order_by=COORDS + ["lifecycle_revision"],
            ),
            dsl.select_node(
                f"{body_id}.generation_keys",
                relation=KEY,
                columns=COLUMNS[KEY],
                predicate=generation_key_pred,
                cardinality="COMPLETE_SET",
                output_symbol="census_generation_key_set",
                order_by=COORDS + ["interval_start"],
                set_read=True,
            ),
            dsl.select_node(
                f"{body_id}.generation_pins",
                relation=PIN,
                columns=COLUMNS[PIN],
                predicate=generation_pin_pred,
                cardinality="COMPLETE_SET",
                output_symbol="census_generation_pin_set",
                order_by=[
                    "practice_id",
                    "source_contract_id",
                    "stream_id",
                    "observer_id",
                    "observer_generation",
                    "pin_id",
                ],
                set_read=True,
            ),
        ],
        complete_set=True,
        order_by=[
            {"column": column, "direction": "ASC"} for column in COORDS
        ],
        convergence="REJOIN",
    )
    return [
        dsl.select_node(f"{body_id}.required_source_rows", relation=SOURCE, columns=COLUMNS[SOURCE], predicate=required_source_pred, cardinality="COMPLETE_SET", output_symbol="required_source_set", order_by=["practice_id", "source_contract_id", "stream_id", "stream_epoch", "transaction_position"], set_read=True),
        dsl.select_node(f"{body_id}.mature_source_rows", relation=SOURCE, columns=COLUMNS[SOURCE], predicate=mature_source_pred, cardinality="COMPLETE_SET", output_symbol="mature_source_set", order_by=["practice_id", "source_contract_id", "stream_id", "stream_epoch", "transaction_position"], set_read=True),
        dsl.select_node(f"{body_id}.mature_checkpoints", relation=CHECKPOINT, columns=COLUMNS[CHECKPOINT], predicate=mature_checkpoint_pred, cardinality="COMPLETE_SET", output_symbol="mature_checkpoint_set", order_by=COORDS, set_read=True),
        dsl.select_node(f"{body_id}.mature_receipts", relation=RECEIPT, columns=COLUMNS[RECEIPT], predicate=mature_receipt_pred, cardinality="COMPLETE_SET", output_symbol="mature_receipt_set", order_by=COORDS+["source_position"], set_read=True),
        dsl.select_node(f"{body_id}.mature_audits", relation=AUDIT, columns=COLUMNS[AUDIT], predicate=mature_audit_pred, cardinality="COMPLETE_SET", output_symbol="mature_audit_set", order_by=COORDS+["lifecycle_revision"], set_read=True),
        dsl.select_node(f"{body_id}.overlapping_keys", relation=KEY, columns=COLUMNS[KEY], predicate=overlapping_key_pred, cardinality="COMPLETE_SET", output_symbol="overlapping_key_set", order_by=COORDS+["interval_start"], set_read=True),
        generation_loop,
    ]


def _retention_census_digest() -> dict[str, Any]:
    return dsl.digest(F+"source_retention_census_digest_v1", [
        _count("policy_set", POLICY), _count("generation_set", GENERATION), _count("checkpoint_set", CHECKPOINT),
        _count("anchor_set", ANCHOR), _count("pin_set", PIN), _count("key_set", KEY), _count("source_set", SOURCE),
        _count("retention_receipt_set", RECEIPT), _count("retention_audit_set", AUDIT),
        _col("retention_head", HEAD, "stream_epoch"), _col("retention_head", HEAD, "last_position"),
    ])


def _slowest_checkpoint_position() -> dict[str, Any]:
    minimum = {
        "op": "MIN_FIELD",
        "source": dsl.local_ref("checkpoint_set", CHECKPOINT+"[]"),
        "field": "last_contiguous_position",
        "type": PG+"bigint",
    }
    return dsl.case(
        PG+"bigint",
        [{"when": dsl.eq(_count("checkpoint_set", CHECKPOINT), dsl.const(PG+"bigint", 0)), "then": dsl.const(PG+"bigint", 0)}],
        minimum,
    )


def _retention_reason() -> dict[str, Any]:
    census_complete = dsl.all_of(
        dsl.eq(_count("checkpoint_set", CHECKPOINT), _count("generation_set", GENERATION)),
        dsl.binary("GTE", _count("anchor_set", ANCHOR), _count("generation_set", GENERATION)),
    )
    checkpoint_current = dsl.eq(
        dsl.local_ref("slowest_checkpoint_position", PG + "bigint"),
        _col("retention_head", HEAD, "last_position"),
    )
    key_overlap = dsl.local_ref("key_overlap_covered", PG + "boolean")
    grace_elapsed = dsl.all_of(
        dsl.eq(_count("mature_source_set", SOURCE), _count("required_source_set", SOURCE)),
        dsl.eq(_count("mature_checkpoint_set", CHECKPOINT), _count("checkpoint_set", CHECKPOINT)),
        dsl.eq(_count("mature_receipt_set", RECEIPT), _count("retention_receipt_set", RECEIPT)),
        dsl.eq(_count("mature_audit_set", AUDIT), _count("retention_audit_set", AUDIT)),
    )
    return dsl.case(
        F+"source_retention_reason",
        [
            {"when": dsl.eq(_count("generation_set", GENERATION), dsl.const(PG+"bigint", 0)), "then": dsl.const(F+"source_retention_reason", "NO_NON_CONSUMED_GENERATION")},
            {"when": dsl.unary("NOT", census_complete), "then": dsl.const(F+"source_retention_reason", "AMBIGUOUS_CENSUS")},
            {"when": dsl.unary("NOT", checkpoint_current), "then": dsl.const(F+"source_retention_reason", "CHECKPOINT_LAG")},
            {"when": dsl.binary("GT", _count("pin_set", PIN), dsl.const(PG+"bigint", 0)), "then": dsl.const(F+"source_retention_reason", "ACTIVE_PIN")},
            {"when": dsl.unary("NOT", key_overlap), "then": dsl.const(F+"source_retention_reason", "KEY_OVERLAP")},
            {"when": dsl.unary("NOT", grace_elapsed), "then": dsl.const(F+"source_retention_reason", "GRACE_PENDING")},
            {"when": dsl.eq(_col("retention_policy", POLICY, "retention_execution_enabled"), dsl.const(PG+"boolean", False)), "then": dsl.const(F+"source_retention_reason", "EXECUTION_DISABLED")},
        ],
        dsl.const(F+"source_retention_reason", "ELIGIBLE"),
    )


def _retention_eligible() -> dict[str, Any]:
    return dsl.all_of(
        dsl.binary("GT", _count("generation_set", GENERATION), dsl.const(PG+"bigint", 0)),
        dsl.eq(_count("checkpoint_set", CHECKPOINT), _count("generation_set", GENERATION)),
        dsl.binary("GTE", _count("anchor_set", ANCHOR), _count("generation_set", GENERATION)),
        dsl.eq(dsl.local_ref("slowest_checkpoint_position", PG+"bigint"), _col("retention_head", HEAD, "last_position")),
        dsl.eq(_count("pin_set", PIN), dsl.const(PG+"bigint", 0)),
        dsl.local_ref("key_overlap_covered", PG+"boolean"),
        dsl.eq(_count("mature_source_set", SOURCE), _count("required_source_set", SOURCE)),
        dsl.eq(_count("mature_checkpoint_set", CHECKPOINT), _count("checkpoint_set", CHECKPOINT)),
        dsl.eq(_count("mature_receipt_set", RECEIPT), _count("retention_receipt_set", RECEIPT)),
        dsl.eq(_count("mature_audit_set", AUDIT), _count("retention_audit_set", AUDIT)),
        _col("retention_policy", POLICY, "retention_execution_enabled"),
    )


def _retention_locals() -> list[tuple[str, str]]:
    return [
        ("barrier", BARRIER), ("retention_head", HEAD), ("policy_set", POLICY+"[]"), ("generation_set", GENERATION+"[]"),
        ("checkpoint_set", CHECKPOINT+"[]"), ("anchor_set", ANCHOR+"[]"), ("pin_set", PIN+"[]"), ("key_set", KEY+"[]"),
        ("source_set", SOURCE+"[]"), ("retention_receipt_set", RECEIPT+"[]"), ("retention_audit_set", AUDIT+"[]"),
        ("retention_policy", POLICY), ("census_digest", F+"digest_sha256"),
        ("slowest_checkpoint_position", PG+"bigint"),
        ("required_source_set", SOURCE+"[]"), ("mature_source_set", SOURCE+"[]"),
        ("mature_checkpoint_set", CHECKPOINT+"[]"), ("mature_receipt_set", RECEIPT+"[]"),
        ("mature_audit_set", AUDIT+"[]"), ("overlapping_key_set", KEY+"[]"),
        ("key_overlap_covered", PG+"boolean"),
        ("census_generation", GENERATION), ("census_checkpoint", CHECKPOINT), ("census_anchor", ANCHOR),
        ("census_generation_key_set", KEY+"[]"), ("census_generation_pin_set", PIN+"[]"),
    ]


def build_retention_evaluation_body() -> dict[str, Any]:
    body_id = F + "evaluate_source_retention_v1"
    output_type = F + "context_source_retention_eligibility_v1"
    scope_input = dsl.input_ref("practice_source_stream", SCOPE)
    scope = _scope(scope_input)
    binding_nodes, binding_symbols = _binding(body_id, "RETENTION", scope)
    result = _composite(output_type, [
        ("eligible", _retention_eligible()), ("through_position", dsl.local_ref("slowest_checkpoint_position", PG+"bigint")),
        ("census_digest", dsl.local_ref("census_digest", F+"digest_sha256")), ("reason_code", _retention_reason()),
    ])
    ambiguous_result = _composite(output_type, [
        ("eligible", dsl.const(PG+"boolean", False)),
        ("through_position", dsl.const(PG+"bigint", 0)),
        ("census_digest", dsl.local_ref("census_digest", F+"digest_sha256")),
        ("reason_code", dsl.const(F+"source_retention_reason", "AMBIGUOUS_CENSUS")),
    ])
    exact_policy_branch = [
        dsl.select_node(f"{body_id}.policy", relation=POLICY, columns=COLUMNS[POLICY], predicate=dsl.all_of(_predicate(POLICY, scope), dsl.binary("LTE", _src(POLICY, "effective_at"), dsl.transaction_timestamp())), cardinality="EXACTLY_ONE", output_symbol="retention_policy", order_by=["practice_id", "source_contract_id", "stream_id", "policy_revision"]),
        dsl.let_node(f"{body_id}.slowest_checkpoint", "slowest_checkpoint_position", PG+"bigint", _slowest_checkpoint_position()),
        *_retention_proof_nodes(body_id, scope),
        dsl.let_node(f"{body_id}.key_overlap_coverage", "key_overlap_covered", PG+"boolean", _key_overlap_coverage()),
        dsl.let_node(f"{body_id}.result", "retention_result", output_type, result),
        _retry_or_return(body_id, "eligibility", "retention_result", output_type, composite=True),
    ]
    ambiguous_policy_branch = [
        dsl.let_node(f"{body_id}.ambiguous_result", "ambiguous_retention_result", output_type, ambiguous_result),
        _retry_or_return(body_id, "ambiguous_policy", "ambiguous_retention_result", output_type, composite=True),
    ]
    nodes = [
        _isolation(body_id, "SERIALIZABLE"), *binding_nodes,
        dsl.lock_node(f"{body_id}.lock_barrier", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], mode="FOR_SHARE", order=1, output_symbol="barrier", columns=COLUMNS[BARRIER]),
        *_retention_census_nodes(body_id, scope),
        dsl.let_node(f"{body_id}.census_digest", "census_digest", F+"digest_sha256", _retention_census_digest()),
        _if(
            f"{body_id}.policy_exact",
            dsl.eq(_count("policy_set", POLICY), dsl.const(PG+"bigint", 1)),
            exact_policy_branch,
            ambiguous_policy_branch,
        ),
    ]
    locals_ = [(row["id"], row["type"]) for row in binding_symbols] + _retention_locals() + [
        ("retention_result", output_type),
        ("ambiguous_retention_result", output_type),
    ]
    return dsl.body(body_id, "ENTRY_POINT", body_id, _symbols([("practice_source_stream", SCOPE)], locals_), nodes)


def build_purge_body() -> dict[str, Any]:
    body_id = F + "purge_source_rows_v1"
    output_type = F + "context_source_purge_result_v1"
    scope_input = dsl.input_ref("practice_source_stream", SCOPE)
    requested_through = dsl.input_ref("through_position", PG+"bigint")
    scope = _scope(scope_input)
    binding_nodes, binding_symbols = _binding(body_id, "RETENTION", scope)
    delete_predicate = dsl.all_of(
        _predicate(SOURCE, scope),
        dsl.binary("LTE", _src(SOURCE, "transaction_position"), requested_through),
    )
    delete_node = dsl.node(
        f"{body_id}.delete_source",
        "DELETE_SOURCE",
        relation=SOURCE,
        key_columns=["practice_id", "source_contract_id", "stream_id", "transaction_position"],
        predicate=delete_predicate,
        max_rows=1000,
        cascade=False,
        output_symbol="purged_row_count",
        output_type=PG+"bigint",
    )
    purge_result = _composite(output_type, [
        ("purged_row_count", dsl.local_ref("purged_row_count", PG+"bigint")),
        ("through_position", requested_through),
        ("census_digest", dsl.local_ref("census_digest", F+"digest_sha256")),
    ])
    nodes = [
        _isolation(body_id, "SERIALIZABLE"), *binding_nodes,
        dsl.lock_node(f"{body_id}.lock_barrier", relation=BARRIER, predicate=_predicate(BARRIER, scope), key_columns=["practice_id", "source_contract_id", "stream_id"], mode="FOR_UPDATE", order=1, output_symbol="barrier", columns=COLUMNS[BARRIER]),
        *_retention_census_nodes(body_id, scope),
        dsl.assert_node(f"{body_id}.one_policy", dsl.eq(_count("policy_set", POLICY), dsl.const(PG+"bigint", 1)), "F_RETENTION_CENSUS"),
        dsl.select_node(f"{body_id}.policy", relation=POLICY, columns=COLUMNS[POLICY], predicate=dsl.all_of(_predicate(POLICY, scope), dsl.binary("LTE", _src(POLICY, "effective_at"), dsl.transaction_timestamp())), cardinality="EXACTLY_ONE", output_symbol="retention_policy", order_by=["practice_id", "source_contract_id", "stream_id", "policy_revision"]),
        dsl.let_node(f"{body_id}.census_digest", "census_digest", F+"digest_sha256", _retention_census_digest()),
        dsl.let_node(f"{body_id}.slowest_checkpoint", "slowest_checkpoint_position", PG+"bigint", _slowest_checkpoint_position()),
        *_retention_proof_nodes(body_id, scope),
        dsl.let_node(f"{body_id}.key_overlap_coverage", "key_overlap_covered", PG+"boolean", _key_overlap_coverage()),
        dsl.let_node(
            f"{body_id}.retention_reason",
            "retention_reason",
            F+"source_retention_reason",
            _retention_reason(),
        ),
        dsl.assert_node(
            f"{body_id}.eligible",
            dsl.eq(
                dsl.local_ref("retention_reason", F+"source_retention_reason"),
                dsl.const(F+"source_retention_reason", "ELIGIBLE"),
            ),
            "F_RETENTION_DISABLED",
        ),
        dsl.assert_node(f"{body_id}.exact_through", dsl.eq(requested_through, dsl.local_ref("slowest_checkpoint_position", PG+"bigint")), "F_RETENTION_CENSUS"),
        delete_node,
        dsl.let_node(f"{body_id}.result", "purge_result", output_type, purge_result),
        _retry_or_return(body_id, "purge", "purge_result", output_type, composite=True),
    ]
    locals_ = [(row["id"], row["type"]) for row in binding_symbols] + _retention_locals() + [
        ("retention_reason", F+"source_retention_reason"),
        ("purged_row_count", PG+"bigint"),
        ("purge_result", output_type),
    ]
    return dsl.body(body_id, "ENTRY_POINT", body_id, _symbols([("practice_source_stream", SCOPE), ("through_position", PG+"bigint")], locals_), nodes)


def build_entry_programs() -> list[dict[str, Any]]:
    """Return the frozen non-producer entry population in parent order."""

    return [
        build_admission_body(),
        build_coordinator_body(),
        build_registration_body(),
        build_anchor_body(),
        build_rotation_body(),
        build_consumption_body(),
        build_retention_evaluation_body(),
        build_purge_body(),
    ]
