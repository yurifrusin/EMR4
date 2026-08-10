"""Build the closed provider-free durability function/trigger body contract.

This is an offline architecture builder.  It emits typed metadata and a JSON
Schema only; it never renders SQL or contacts a database, product, or provider.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARENT_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "migration-transaction-architecture/migration-transaction-architecture-"
    "contract.json"
)
OUTPUT_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "function-trigger-body-architecture"
)
CONTRACT_PATH = OUTPUT_DIR / "function-trigger-body-architecture-contract.json"
SCHEMA_PATH = OUTPUT_DIR / "function-trigger-body-architecture-contract.schema.json"

PARENT_DIGEST = (
    "sha256:18fb00ff02820c31b4fcab4de096393cbea49e0a37ebb28d65c5eb2d6f154cfd"
)
FABRIC = "emr4_context_fabric."
PG = "pg_catalog."

ENTRY_POINT_NAMES = [
    "project_update_confirm_reschedule_v1",
    "admit_proofread_observation_v1",
    "apply_durability_transition_v1",
    "register_observer_generation_v1",
    "append_recovery_anchor_v1",
    "rotate_observation_key_v1",
    "consume_observer_generation_v1",
    "evaluate_source_retention_v1",
    "purge_source_rows_v1",
]
TRIGGER_FUNCTION_NAMES = [
    "cf_guard_claim_v1",
    "cf_fence_claim_v1",
    "cf_fence_appointment_update_v1",
    "cf_guard_audit_v1",
    "cf_fence_audit_v1",
    "cf_guard_event_v1",
    "cf_fence_event_v1",
    "cf_guard_alias_v1",
    "cf_fence_alias_v1",
    "cf_guard_stream_head_v1",
    "cf_fence_stream_head_v1",
    "cf_guard_outbox_v1",
    "cf_fence_outbox_v1",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_digest(value: dict[str, Any], field: str) -> str:
    payload = copy.deepcopy(value)
    payload.pop(field, None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _qualify_type(parent: dict[str, Any], type_name: str) -> str:
    array_suffix = "[]" if type_name.endswith("[]") else ""
    base = type_name.removesuffix("[]")
    pg_types = {
        *parent["type_catalogue"]["builtins"],
        "name",
        "trigger",
        "xid",
        "integer",
        "text",
        "jsonb",
    }
    prefix = PG if base in pg_types else FABRIC
    return f"{prefix}{base}{array_suffix}"


def input_ref(symbol: str, type_name: str) -> dict[str, Any]:
    return {"op": "REF", "kind": "INPUT", "symbol": symbol, "type": type_name}


def local_ref(symbol: str, type_name: str) -> dict[str, Any]:
    return {"op": "REF", "kind": "LOCAL", "symbol": symbol, "type": type_name}


def column_ref(
    symbol: str, relation: str, column: str, type_name: str
) -> dict[str, Any]:
    return {
        "op": "REF",
        "kind": "ROW_COLUMN",
        "symbol": symbol,
        "relation": relation,
        "column": column,
        "type": type_name,
    }


def source_column(relation: str, column: str, type_name: str) -> dict[str, Any]:
    return {
        "op": "REF",
        "kind": "SOURCE_COLUMN",
        "relation": relation,
        "column": column,
        "type": type_name,
    }


def trigger_column_ref(
    image: str,
    relation: str,
    column: str,
    type_name: str,
) -> dict[str, Any]:
    return {
        "op": "REF",
        "kind": "TRIGGER_COLUMN",
        "image": image,
        "relation": relation,
        "column": column,
        "type": type_name,
    }


def system_ref(field: str, type_name: str) -> dict[str, Any]:
    return {"op": "REF", "kind": "SYSTEM", "field": field, "type": type_name}


def const(type_name: str, value: Any) -> dict[str, Any]:
    return {"op": "CONST", "type": type_name, "value": value}


def unary(
    op: str, arg: dict[str, Any], result_type: str = f"{PG}boolean"
) -> dict[str, Any]:
    return {"op": op, "operand": arg, "type": result_type}


def binary(
    op: str,
    left: dict[str, Any],
    right: dict[str, Any],
    result_type: str = f"{PG}boolean",
) -> dict[str, Any]:
    return {"op": op, "left": left, "right": right, "type": result_type}


def nary(op: str, args: list[dict[str, Any]]) -> dict[str, Any]:
    return {"op": op, "operands": args, "type": f"{PG}boolean"}


def all_of(*args: dict[str, Any]) -> dict[str, Any]:
    return nary("AND", list(args))


def any_of(*args: dict[str, Any]) -> dict[str, Any]:
    return nary("OR", list(args))


def set_contains_key(
    set_symbol: str,
    set_relation: str,
    source_relation: str,
    key_pairs: list[tuple[str, str]],
) -> dict[str, Any]:
    return {
        "op": "SET_CONTAINS_KEY",
        "set": {
            "kind": "LOCAL",
            "symbol": set_symbol,
            "type": set_relation + "[]",
        },
        "source_relation": source_relation,
        "key_pairs": [
            {"source_column": source_column, "set_column": set_column}
            for source_column, set_column in key_pairs
        ],
        "type": f"{PG}boolean",
    }


def set_covers_keys(
    required_symbol: str,
    required_relation: str,
    evidence_symbol: str,
    evidence_relation: str,
    key_pairs: list[tuple[str, str]],
) -> dict[str, Any]:
    return {
        "op": "SET_COVERS_KEYS",
        "required": {
            "kind": "LOCAL",
            "symbol": required_symbol,
            "type": required_relation + "[]",
        },
        "evidence": {
            "kind": "LOCAL",
            "symbol": evidence_symbol,
            "type": evidence_relation + "[]",
        },
        "key_pairs": [
            {
                "required_column": required_column,
                "evidence_column": evidence_column,
            }
            for required_column, evidence_column in key_pairs
        ],
        "type": f"{PG}boolean",
    }


def eq(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return binary("EQ", left, right)


def is_distinct(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return binary("IS_DISTINCT_FROM", left, right)


def field(composite: dict[str, Any], name: str, type_name: str) -> dict[str, Any]:
    return {
        "op": "FIELD",
        "source": composite,
        "field": name,
        "type": type_name,
    }


def add(
    left: dict[str, Any], right: dict[str, Any], result_type: str
) -> dict[str, Any]:
    return {"op": "ADD", "left": left, "right": right, "type": result_type}


def digest(domain: str, values: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "op": "CANONICAL_DIGEST",
        "profile": domain,
        "operands": values,
        "type": f"{FABRIC}digest_sha256",
    }


def transaction_timestamp() -> dict[str, Any]:
    return {"op": "TRANSACTION_TIMESTAMP", "type": f"{PG}timestamptz"}


def current_xid32() -> dict[str, Any]:
    return {"op": "CURRENT_XID32", "type": f"{PG}xid"}


def xmin_equals_current(row_xmin: dict[str, Any]) -> dict[str, Any]:
    if row_xmin.get("type") == f"{PG}xid":
        return eq(row_xmin, current_xid32())
    return eq(
        {"op": "SYSTEM_XMIN", "row": row_xmin, "type": f"{PG}xid"},
        current_xid32(),
    )


def uuid_v4() -> dict[str, Any]:
    return {"op": "GEN_RANDOM_UUID", "type": f"{PG}uuid"}


def json_value(source: dict[str, Any], key: str, output_type: str) -> dict[str, Any]:
    return {
        "op": "JSON_GET_CAST",
        "source": source,
        "key": key,
        "target_type": output_type,
        "type": output_type,
    }


def array_const(type_name: str, values: list[Any]) -> dict[str, Any]:
    return {"op": "ARRAY_CONST", "type": type_name, "values": values}


def case(
    result_type: str,
    arms: list[dict[str, Any]],
    else_value: dict[str, Any],
) -> dict[str, Any]:
    return {"op": "CASE", "arms": arms, "else": else_value, "type": result_type}


def symbol(symbol_id: str, type_name: str, source_kind: str) -> dict[str, Any]:
    return {"id": symbol_id, "type": type_name, "source": {"kind": source_kind}}


def node_symbol(symbol_id: str, type_name: str) -> dict[str, Any]:
    return symbol(symbol_id, type_name, "LOCAL")


def node(node_id: str, op: str, **operands: Any) -> dict[str, Any]:
    return {"node_id": node_id, "op": op, "operands": operands}


def body(
    body_id: str,
    kind: str,
    signature_id: str,
    symbols: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": body_id,
        "kind": kind,
        "signature_id": signature_id,
        "symbols": symbols,
        "ast": {"op": "SEQUENCE", "nodes": nodes},
        "derived_effect_summary": {},
    }


def select_node(
    node_id: str,
    *,
    relation: str,
    columns: list[str],
    predicate: dict[str, Any],
    cardinality: str,
    output_symbol: str,
    order_by: list[str] | None = None,
    set_read: bool = False,
) -> dict[str, Any]:
    return node(
        node_id,
        "SELECT_SET" if set_read else "SELECT_EXACT",
        relation=relation,
        columns=columns,
        predicate=predicate,
        cardinality=cardinality,
        order_by=[{"column": column, "direction": "ASC"} for column in order_by or []],
        output_symbol=output_symbol,
    )


def lock_node(
    node_id: str,
    *,
    relation: str,
    predicate: dict[str, Any],
    key_columns: list[str],
    mode: str,
    order: int,
    output_symbol: str,
    columns: list[str],
) -> dict[str, Any]:
    return node(
        node_id,
        "LOCK_EXACT",
        relation=relation,
        predicate=predicate,
        key_columns=key_columns,
        mode=mode,
        ordinal=order,
        output_symbol=output_symbol,
        columns=columns,
    )


def assert_node(
    node_id: str, predicate: dict[str, Any], failure_id: str
) -> dict[str, Any]:
    return node(node_id, "ASSERT", predicate=predicate, failure_id=failure_id)


def let_node(
    node_id: str, output_symbol: str, output_type: str, expression: dict[str, Any]
) -> dict[str, Any]:
    if expression.get("type") != output_type:
        raise ValueError(f"LET {node_id} expression type does not match {output_type}")
    return node(
        node_id,
        "LET",
        output_symbol=output_symbol,
        expression=expression,
    )


def insert_node(
    node_id: str,
    *,
    relation: str,
    bindings: list[tuple[str, dict[str, Any]]],
    output_symbol: str,
    returning_columns: list[str],
    reload_key: list[str] | None = None,
    winner_predicate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    op = "INSERT_OR_RELOAD_COMPARE" if reload_key else "INSERT"
    result = node(
        node_id,
        op,
        relation=relation,
        bindings=[{"column": name, "value": value} for name, value in bindings],
        output_symbol=output_symbol,
        returning_columns=returning_columns,
    )
    if reload_key:
        result["operands"].update(
            {
                "conflict_key_columns": reload_key,
                "winner_columns": returning_columns,
                "winner_predicate": winner_predicate,
                "cardinality": "EXACTLY_ONE",
            }
        )
    return result


def update_node(
    node_id: str,
    *,
    relation: str,
    predicate: dict[str, Any],
    key_columns: list[str],
    bindings: list[tuple[str, dict[str, Any]]],
    output_symbol: str,
    returning_columns: list[str],
) -> dict[str, Any]:
    return node(
        node_id,
        "UPDATE",
        relation=relation,
        predicate=predicate,
        key_columns=key_columns,
        set_bindings=[{"column": name, "value": value} for name, value in bindings],
        affected_cardinality="EXACTLY_ONE",
        output_symbol=output_symbol,
        returning_columns=returning_columns,
    )


def return_row(node_id: str, source_symbol: str, output_type: str) -> dict[str, Any]:
    return node(
        node_id,
        "RETURN_ROW",
        source_symbol=source_symbol,
        type=output_type,
        cardinality="EXACTLY_ONE",
    )


def propagate_retryable(node_id: str) -> dict[str, Any]:
    return node(
        node_id,
        "PROPAGATE_RETRYABLE",
        sqlstates=["40001", "40P01"],
        internal_retry=False,
    )


RECOVERY_OPERATIONS: list[dict[str, Any]] = [
    {
        "id": "REC01",
        "kind": "ADD_COLUMN",
        "target": f"{FABRIC}context_service_practice_binding.stream_id",
        "type": f"{PG}uuid",
        "nullable": False,
    },
    {
        "id": "REC02",
        "kind": "ADD_COLUMN",
        "target": f"{FABRIC}diary_context_aggregate_aliases_v1.stream_id",
        "type": f"{PG}uuid",
        "nullable": False,
    },
    {
        "id": "REC03",
        "kind": "ADD_COLUMN",
        "target": f"{FABRIC}context_retention_policy.stream_id",
        "type": f"{PG}uuid",
        "nullable": False,
    },
    {
        "id": "REC04",
        "kind": "REWRITE_COORDINATES",
        "targets": [
            f"{FABRIC}diary_context_aggregate_aliases_v1",
            f"{FABRIC}context_retention_policy",
            f"{FABRIC}diary_context_observation_outbox_v1",
        ],
        "required_coordinate": "stream_id",
    },
    {
        "id": "REC05",
        "kind": "CHANGE_SUPPORT_SIGNATURE",
        "target": f"{FABRIC}session_binding_allows_v1",
        "append_input": {"name": "requested_stream_id", "type": f"{PG}uuid"},
        "predicate_addition": "BINDING_STREAM_EQUALS_REQUESTED_STREAM",
    },
    {
        "id": "REC06",
        "kind": "REWRITE_STREAM_RLS",
        "target_set": "ALL_STREAM_BEARING_EFFECTIVE_RELATIONS",
        "binding_input": "ROW_OR_LOCATOR_STREAM_ID",
    },
    {
        "id": "REC07",
        "kind": "ADD_OWNER_SELECT",
        "role": f"{FABRIC}context_schema_owner",
        "relations": [
            "public.appointment_command_idempotency",
            "public.appointments",
            "public.appointment_audit_log",
            "public.diary_committed_events",
        ],
        "dml": [],
    },
    {
        "id": "REC08",
        "kind": "ADD_RECEIVER_SELECT",
        "role": f"{FABRIC}context_admission_receiver",
        "relations": [f"{FABRIC}context_service_practice_binding"],
        "dml": [],
    },
    {
        "id": "REC09",
        "kind": "DECLARE_INSTALLATION_PRECONDITION",
        "privilege": "TRIGGER",
        "relations": [
            "public.appointment_command_idempotency",
            "public.appointments",
            "public.appointment_audit_log",
            "public.diary_committed_events",
        ],
        "runtime_grant": False,
    },
    {
        "id": "REC10",
        "kind": "ADD_ENUM",
        "target": f"{FABRIC}durability_transition_result_kind",
        "values": [
            "RECEIPT_APPLIED",
            "RECEIPT_REPLAYED",
            "REBASE_APPLIED",
            "TERMINAL_REPLAYED",
        ],
    },
    {
        "id": "REC11",
        "kind": "ADD_COMPOSITE",
        "target": f"{FABRIC}durability_transition_result_v1",
        "fields": [
            {
                "name": "result_kind",
                "type": f"{FABRIC}durability_transition_result_kind",
            },
            {"name": "checkpoint_state", "type": f"{FABRIC}checkpoint_state"},
            {"name": "source_position", "type": f"{PG}bigint"},
            {"name": "decision", "type": f"{FABRIC}observation_decision"},
            {"name": "reason_code", "type": f"{FABRIC}observation_reason"},
            {
                "name": "checkpoint_disposition",
                "type": f"{FABRIC}checkpoint_disposition",
            },
            {"name": "lifecycle_revision", "type": f"{PG}bigint"},
            {"name": "evidence_digest", "type": f"{FABRIC}digest_sha256"},
        ],
    },
    {
        "id": "REC12",
        "kind": "CHANGE_OUTPUT",
        "target": f"{FABRIC}apply_durability_transition_v1",
        "from": f"{FABRIC}context_classified_observation_receipt",
        "to": f"{FABRIC}durability_transition_result_v1",
    },
    {
        "id": "REC13",
        "kind": "APPEND_COMPOSITE_FIELD",
        "target": f"{FABRIC}generation_registration_v1",
        "field": {
            "name": "initial_key_interval",
            "type": f"{FABRIC}future_key_interval_v1",
        },
    },
    {
        "id": "REC14",
        "kind": "FREEZE_REGISTRATION_BASELINE",
        "effects": [
            "STREAM_HEAD_ZERO_OR_RELOAD",
            "GENERATION",
            "CHECKPOINT_AT_HEAD",
            "DIARY_FRAME_CURRENT",
            "WAITING_ROOM_FRAME_CURRENT",
            "TWO_WATERMARKS_AT_HEAD",
            "INITIAL_KEY_START_CHECKPOINT_PLUS_ONE",
            "BASELINE_ANCHOR",
        ],
    },
    {
        "id": "REC15",
        "kind": "ADD_COLUMN",
        "target": f"{FABRIC}context_observer_generation.terminal_reason",
        "type": f"{FABRIC}generation_terminal_reason",
        "nullable": True,
    },
    {
        "id": "REC16",
        "kind": "ADD_STATE_CHECK",
        "target": f"{FABRIC}context_observer_generation",
        "predicate": "TERMINAL_REASON_EXACTLY_IFF_REVOKED_OR_CONSUMED",
    },
    {
        "id": "REC17",
        "kind": "REMOVE_PIN_MUTATION_CLAIM",
        "target": "pin_one_way_release_v1",
        "entry_points": [],
        "pin_mutation_enabled": False,
    },
    {
        "id": "REC18",
        "kind": "FREEZE_ROTATION_REPLAY_ORDER",
        "order": [
            "EXACT_INTERVAL_REPLAY",
            "DIFFERING_INTERVAL_REJECT",
            "NEW_EFFECT_ANCHOR_FENCE",
        ],
    },
    {
        "id": "REC19",
        "kind": "ADD_ENUM",
        "target": f"{FABRIC}source_retention_reason",
        "values": [
            "ELIGIBLE",
            "EXECUTION_DISABLED",
            "CHECKPOINT_LAG",
            "ACTIVE_PIN",
            "KEY_OVERLAP",
            "GRACE_PENDING",
            "AMBIGUOUS_CENSUS",
            "NO_NON_CONSUMED_GENERATION",
        ],
    },
    {
        "id": "REC20",
        "kind": "CHANGE_COMPOSITE_FIELD_TYPE",
        "target": f"{FABRIC}context_source_retention_eligibility_v1.reason_code",
        "from": f"{FABRIC}observation_reason",
        "to": f"{FABRIC}source_retention_reason",
    },
    {
        "id": "REC21",
        "kind": "FREEZE_AGGREGATE_REVISION",
        "source": "COUNT_PUBLIC_APPOINTMENT_AUDIT_LOG_ID_BY_PRACTICE_AND_APPOINTMENT",
        "appointment_field": False,
    },
    {
        "id": "REC22",
        "kind": "FREEZE_ALIAS_PROVENANCE",
        "new_alias_requires_current_xid": True,
        "reused_alias_requires_current_xid": False,
        "reuse_coordinate": [
            "practice_id",
            "source_contract_id",
            "stream_id",
            "product_appointment_uuid",
        ],
    },
    {
        "id": "REC23",
        "kind": "FREEZE_TRIGGER_MATRIX",
        "matrix_id": "TRIGGER_APPLICABILITY_RETURN_MATRIX_V1",
    },
    {
        "id": "REC24",
        "kind": "FREEZE_SECOND_UPDATE_RULE",
        "target": "public.appointments",
        "predicate": "OLD_XMIN_IS_CURRENT_XID32",
        "outcome": "REJECT",
    },
    {
        "id": "REC25",
        "kind": "FREEZE_FENCE_PROPERTIES",
        "properties": [
            "READ_ONLY",
            "LOCK_FREE",
            "SIBLING_CALL_FREE",
            "ORDER_INDEPENDENT",
            "FINAL_TRANSACTION_STATE",
        ],
    },
    {
        "id": "REC26",
        "kind": "FREEZE_SHARED_TABLE_RULES",
        "rules": [
            "BOTH_IMAGES_CLASSIFY_ADOPTION_ESCAPE",
            "CHECK_IN_EXCLUDED",
            "OLDER_EVENT_RETENTION_ALLOWED",
            "OUTBOX_RETENTION_ONLY_VIA_PURGE",
            "LIFECYCLE_HEAD_BASELINE_ALLOWED",
        ],
    },
]


FAILURES = [
    ("F_BINDING_DENIED", "CF001", "binding_denied"),
    ("F_TRIGGER_CONTEXT", "CF002", "trigger_context_invalid"),
    ("F_LOCATOR", "CF003", "locator_malformed_or_foreign"),
    ("F_CARDINALITY", "CF004", "required_row_missing_or_ambiguous"),
    ("F_CLAIM", "CF101", "producer_claim_ineligible"),
    ("F_PROVENANCE", "CF102", "producer_provenance_mismatch"),
    ("F_MEMBERSHIP", "CF103", "producer_membership_mismatch"),
    ("F_ALIAS", "CF104", "alias_collision"),
    ("F_STREAM", "CF105", "stream_head_invalid_or_exhausted"),
    ("F_ADMISSION_SOURCE", "CF201", "admission_source_mismatch"),
    ("F_ADMISSION_KEY", "CF202", "admission_key_unavailable"),
    ("F_ADMISSION_PACKET", "CF203", "admission_packet_invalid"),
    ("F_ANCHOR", "CF301", "anchor_missing_or_mismatched"),
    ("F_TERMINAL", "CF302", "generation_terminal"),
    ("F_STATE", "CF303", "durability_state_ambiguous"),
    ("F_REGISTRATION", "CF401", "registration_conflict"),
    ("F_KEY_PARTITION", "CF402", "key_partition_invalid"),
    ("F_TERMINAL_REASON", "CF403", "terminal_reason_conflict"),
    ("F_RETENTION_CENSUS", "CF501", "retention_state_ambiguous"),
    ("F_RETENTION_DISABLED", "CF502", "retention_disabled_or_ineligible"),
    ("F_IMMUTABLE", "CF601", "immutable_member_mutation"),
    ("F_CLAIM_TRANSITION", "CF602", "claim_transition_invalid"),
    ("F_TEMPORAL_BIJECTION", "CF603", "temporal_bijection_invalid"),
    ("F_SECOND_UPDATE", "CF604", "second_appointment_update"),
    ("F_RETENTION_DELETE", "CF605", "retention_delete_invalid"),
]


def failure_registry() -> list[dict[str, Any]]:
    return [
        {
            "id": failure_id,
            "sqlstate": sqlstate,
            "reason_code": reason,
            "value_payload": "FORBIDDEN",
            "retryable": False,
        }
        for failure_id, sqlstate, reason in FAILURES
    ]


APPLICATION_COLUMNS: dict[str, dict[str, str]] = {
    "public.appointment_command_idempotency": {
        "id": f"{PG}uuid",
        "practice_id": f"{PG}uuid",
        "actor_user_id": f"{PG}uuid",
        "operation_id": f"{PG}text",
        "route_family": f"{PG}text",
        "request_body_hash": f"{PG}text",
        "state": f"{PG}text",
        "target_appointment_id": f"{PG}uuid",
        "audit_log_id": f"{PG}uuid",
        "created_at": f"{PG}timestamptz",
        "xmin": f"{PG}xid",
    },
    "public.appointments": {
        "id": f"{PG}uuid",
        "practice_id": f"{PG}uuid",
        "practitioner_id": f"{PG}uuid",
        "location_id": f"{PG}uuid",
        "start_time": f"{PG}timestamptz",
        "duration_minutes": f"{PG}integer",
        "xmin": f"{PG}xid",
    },
    "public.appointment_audit_log": {
        "id": f"{PG}uuid",
        "practice_id": f"{PG}uuid",
        "appointment_id": f"{PG}uuid",
        "action": f"{PG}text",
        "command_id": f"{PG}uuid",
        "created_at": f"{PG}timestamptz",
        "xmin": f"{PG}xid",
    },
    "public.diary_committed_events": {
        "id": f"{PG}uuid",
        "practice_id": f"{PG}uuid",
        "event_type": f"{PG}text",
        "schema_version": f"{PG}text",
        "source_system": f"{PG}text",
        "appointment_id": f"{PG}uuid",
        "aggregate_revision": f"{PG}bigint",
        "occurred_at": f"{PG}timestamptz",
        "command_id": f"{PG}uuid",
        "audit_log_id": f"{PG}uuid",
        "payload": f"{PG}jsonb",
        "created_at": f"{PG}timestamptz",
        "xmin": f"{PG}xid",
    },
}


def build_catalogue(parent: dict[str, Any]) -> dict[str, Any]:
    relations: dict[str, list[str]] = {}
    column_types: dict[str, dict[str, str]] = {}
    for relation in parent["relation_catalogue"]["relations"]:
        relation_id = FABRIC + relation["name"]
        columns = copy.deepcopy(relation["columns"])
        additions: list[tuple[str, str]] = []
        if relation["name"] in {
            "context_service_practice_binding",
            "diary_context_aggregate_aliases_v1",
            "context_retention_policy",
        }:
            additions.append(("stream_id", "uuid"))
        if relation["name"] == "context_observer_generation":
            additions.append(("terminal_reason", "generation_terminal_reason"))
        existing = {row["name"] for row in columns}
        if "xmin" not in existing:
            columns.append({"name": "xmin", "data_type": "xid"})
            existing.add("xmin")
        for name, type_name in additions:
            if name not in existing:
                columns.append({"name": name, "data_type": type_name})
        relations[relation_id] = [row["name"] for row in columns]
        column_types[relation_id] = {
            row["name"]: _qualify_type(parent, row["data_type"]) for row in columns
        }
    for relation_id, columns in APPLICATION_COLUMNS.items():
        relations[relation_id] = list(columns)
        column_types[relation_id] = dict(columns)

    types = {f"{PG}{name}" for name in parent["type_catalogue"]["builtins"]}
    types.update(
        {
            f"{PG}name",
            f"{PG}trigger",
            f"{PG}xid",
            f"{PG}integer",
            f"{PG}text",
            f"{PG}jsonb",
        }
    )
    types.update(
        f"{FABRIC}{row['name']}"
        for family in ("domains", "enums", "composites")
        for row in parent["type_catalogue"][family]
    )
    types.update(
        {
            f"{FABRIC}durability_transition_result_kind",
            f"{FABRIC}durability_transition_result_v1",
            f"{FABRIC}source_retention_reason",
        }
    )
    types.update(relations)
    composite_fields: dict[str, dict[str, str]] = {}
    for composite in parent["type_catalogue"]["composites"]:
        composite_id = FABRIC + composite["name"]
        fields = {
            item["name"]: _qualify_type(parent, item["data_type"])
            for item in composite["fields"]
        }
        if composite["name"] == "generation_registration_v1":
            fields["initial_key_interval"] = FABRIC + "future_key_interval_v1"
        if composite["name"] == "context_source_retention_eligibility_v1":
            fields["reason_code"] = FABRIC + "source_retention_reason"
        composite_fields[composite_id] = fields
    composite_fields[FABRIC + "durability_transition_result_v1"] = {
        row["name"]: row["type"] for row in RECOVERY_OPERATIONS[10]["fields"]
    }
    types.update(f"{type_name}[]" for type_name in list(types))
    return {
        "relations": relations,
        "types": sorted(types),
        "column_types": column_types,
        "composite_fields": composite_fields,
    }


def _signature_common(row: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    return {
        "language": row["language"],
        "owner": FABRIC + row["owner"],
        "strict": row.get("strict", False),
        "volatility": row["volatility"],
        "parallel_safety": row["parallel_safety"],
        "security_definer": row["security_definer"],
        "search_path": [part.strip() for part in row["search_path_sql"].split(",")],
        "public_execute": row["public_execute"],
        "invariant_ids": row.get("invariant_ids", []),
    }


def build_signatures(parent: dict[str, Any]) -> dict[str, Any]:
    support = parent["support_functions"][0]
    support_inputs = [
        {
            "name": row["name"],
            "mode": "IN",
            "type": _qualify_type(parent, row["data_type"]),
        }
        for row in support["inputs"]
    ]
    support_inputs.insert(
        -1, {"name": "requested_stream_id", "mode": "IN", "type": f"{PG}uuid"}
    )
    support_signature = {
        "id": FABRIC + support["name"],
        "inputs": support_inputs,
        "output": {
            "type": _qualify_type(parent, support["output"]["data_type"]),
            "cardinality": "EXACTLY_ONE",
        },
        "executor_roles": [FABRIC + role for role in support["execute_roles"]],
        **_signature_common(support, parent),
    }

    entries = []
    for row in parent["entry_points"]:
        output_type = _qualify_type(parent, row["output"]["data_type"])
        if row["name"] == "apply_durability_transition_v1":
            output_type = f"{FABRIC}durability_transition_result_v1"
        entries.append(
            {
                "id": FABRIC + row["name"],
                "inputs": [
                    {
                        "name": item["name"],
                        "mode": "IN",
                        "type": _qualify_type(parent, item["data_type"]),
                    }
                    for item in row["inputs"]
                ],
                "output": {
                    "type": output_type,
                    "cardinality": "EXACTLY_ONE",
                },
                "executor": FABRIC + row["executor_role"],
                "authority_source": row["authority_source"],
                **_signature_common(row, parent),
            }
        )

    triggers = []
    for row in parent["trigger_function_catalogue"]:
        triggers.append(
            {
                "id": FABRIC + row["name"],
                "inputs": [],
                "output": {
                    "type": f"{PG}trigger",
                    "cardinality": "EXACTLY_ONE_OR_RAISE",
                },
                "executor": "OWNER_INTERNAL",
                **_signature_common(row, parent),
            }
        )
    return {
        "support": support_signature,
        "entry_points": entries,
        "trigger_functions": triggers,
    }


def build_trigger_declarations(parent: dict[str, Any]) -> list[dict[str, Any]]:
    application_names = {item.removeprefix("public.") for item in APPLICATION_COLUMNS}
    declarations = []
    for row in parent["trigger_surface"]:
        prefix = "public." if row["table"] in application_names else FABRIC
        declarations.append(
            {
                "id": row["name"],
                "relation": prefix + row["table"],
                "timing": row["timing"],
                "row_level": row["row_level"],
                "events": row["events"],
                "deferrable": row["deferrable"],
                "initially_deferred": row["initially_deferred"],
                "function": FABRIC + row["function"],
                "invariant_ids": row["invariant_ids"],
            }
        )
    return declarations


def build_effective_roles(parent: dict[str, Any]) -> list[dict[str, Any]]:
    roles = copy.deepcopy(parent["role_matrix"])
    for role in roles:
        role["role"] = FABRIC + role["role"]
        role["owns_relations"] = [FABRIC + item for item in role["owns_relations"]]
        role["owns_functions"] = [FABRIC + item for item in role["owns_functions"]]
        role["execute_entry_points"] = [
            FABRIC + item for item in role["execute_entry_points"]
        ]
        role["direct_table_select"] = [
            item if item.startswith("public.") else FABRIC + item
            for item in role["direct_table_select"]
        ]
        for grant in role["direct_table_dml"]:
            grant["relation"] = FABRIC + grant["relation"]
    owner = next(row for row in roles if row["role"] == FABRIC + "context_schema_owner")
    owner["direct_table_select"] = list(APPLICATION_COLUMNS)
    receiver = next(
        row for row in roles if row["role"] == FABRIC + "context_admission_receiver"
    )
    receiver["direct_table_select"].append(FABRIC + "context_service_practice_binding")
    return roles


TRIGGER_TERMINALS: dict[str, dict[str, str]] = {
    "cf_guard_claim_v1": {
        "UPDATE": "RETURN_NEW_OR_RAISE",
        "DELETE": "RETURN_OLD_OR_RAISE",
    },
    "cf_fence_claim_v1": {
        "INSERT": "RETURN_NULL_OR_RAISE",
        "UPDATE": "RETURN_NULL_OR_RAISE",
        "DELETE": "RETURN_NULL_OR_RAISE",
    },
    "cf_fence_appointment_update_v1": {"UPDATE": "RETURN_NULL_OR_RAISE"},
    "cf_guard_audit_v1": {
        "UPDATE": "RETURN_NEW_OR_RAISE",
        "DELETE": "RETURN_OLD_OR_RAISE",
    },
    "cf_fence_audit_v1": {
        "INSERT": "RETURN_NULL_OR_RAISE",
        "UPDATE": "RETURN_NULL_OR_RAISE",
        "DELETE": "RETURN_NULL_OR_RAISE",
    },
    "cf_guard_event_v1": {
        "UPDATE": "RETURN_NEW_OR_RAISE",
        "DELETE": "RETURN_OLD_OR_RAISE",
    },
    "cf_fence_event_v1": {
        "INSERT": "RETURN_NULL_OR_RAISE",
        "UPDATE": "RETURN_NULL_OR_RAISE",
        "DELETE": "RETURN_NULL_OR_RAISE",
    },
    "cf_guard_alias_v1": {"UPDATE": "RAISE", "DELETE": "RAISE"},
    "cf_fence_alias_v1": {
        "INSERT": "RETURN_NULL_OR_RAISE",
        "UPDATE": "RAISE",
        "DELETE": "RAISE",
    },
    "cf_guard_stream_head_v1": {"UPDATE": "RETURN_NEW_OR_RAISE", "DELETE": "RAISE"},
    "cf_fence_stream_head_v1": {
        "INSERT": "RETURN_NULL_OR_RAISE",
        "UPDATE": "RETURN_NULL_OR_RAISE",
        "DELETE": "RAISE",
    },
    "cf_guard_outbox_v1": {"UPDATE": "RAISE", "DELETE": "RETURN_OLD_OR_RAISE"},
    "cf_fence_outbox_v1": {
        "INSERT": "RETURN_NULL_OR_RAISE",
        "UPDATE": "RAISE",
        "DELETE": "RETURN_NULL_OR_RAISE",
    },
}


def build_trigger_matrix(
    declarations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    by_function = {row["function"]: row for row in declarations}
    for name in TRIGGER_FUNCTION_NAMES:
        function = FABRIC + name
        declaration = by_function[function]
        events = declaration["events"]
        rows.append(
            {
                "function": function,
                "trigger": declaration["id"],
                "relation": declaration["relation"],
                "timing": declaration["timing"],
                "events": events,
                "old_on": [event for event in events if event in {"UPDATE", "DELETE"}],
                "new_on": [event for event in events if event in {"INSERT", "UPDATE"}],
                "returns": TRIGGER_TERMINALS[name],
                "read_only": True,
                "lock_free": True,
                "sibling_call_free": True,
            }
        )
    return rows


BINDING_COLUMNS = [
    "database_login",
    "logical_capability",
    "practice_id",
    "source_contract_id",
    "binding_revision",
    "credential_epoch",
    "active_from",
    "active_until",
    "stream_id",
]


def binding_fragment(
    prefix: str,
    capability: str,
    *,
    practice: dict[str, Any] | None = None,
    stream: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    relation = FABRIC + "context_service_practice_binding"
    binding_type = relation
    predicate_parts = [
        eq(
            source_column(relation, "database_login", f"{PG}name"),
            system_ref("SESSION_USER", f"{PG}name"),
        ),
        eq(
            source_column(
                relation, "logical_capability", f"{FABRIC}logical_capability"
            ),
            const(f"{FABRIC}logical_capability", capability),
        ),
        eq(
            source_column(
                relation, "source_contract_id", f"{FABRIC}source_contract_code"
            ),
            const(
                f"{FABRIC}source_contract_code",
                "diary.appointment_rescheduled.v1",
            ),
        ),
        binary(
            "LTE",
            source_column(relation, "active_from", f"{PG}timestamptz"),
            transaction_timestamp(),
        ),
        any_of(
            unary(
                "IS_NULL",
                source_column(relation, "active_until", f"{PG}timestamptz"),
            ),
            binary(
                "GT",
                source_column(relation, "active_until", f"{PG}timestamptz"),
                transaction_timestamp(),
            ),
        ),
    ]
    if practice is not None:
        predicate_parts.append(
            eq(
                source_column(relation, "practice_id", f"{PG}uuid"),
                practice,
            )
        )
    if stream is not None:
        predicate_parts.append(
            eq(
                source_column(relation, "stream_id", f"{PG}uuid"),
                stream,
            )
        )
    select_id = f"{prefix}.binding.select"
    call_id = f"{prefix}.binding.call"
    assert_id = f"{prefix}.binding.assert"
    nodes = [
        select_node(
            select_id,
            relation=relation,
            columns=BINDING_COLUMNS,
            predicate=all_of(*predicate_parts),
            cardinality="EXACTLY_ONE",
            output_symbol="binding",
            order_by=["database_login", "logical_capability", "practice_id"],
        ),
        node(
            call_id,
            "CALL_SUPPORT",
            function=FABRIC + "session_binding_allows_v1",
            arguments=[
                system_ref("SESSION_USER", f"{PG}name"),
                array_const(f"{FABRIC}logical_capability[]", [capability]),
                column_ref("binding", relation, "practice_id", f"{PG}uuid"),
                column_ref(
                    "binding",
                    relation,
                    "source_contract_id",
                    f"{FABRIC}source_contract_code",
                ),
                column_ref("binding", relation, "stream_id", f"{PG}uuid"),
                transaction_timestamp(),
            ],
            output_symbol="binding_allowed",
        ),
        assert_node(
            assert_id,
            local_ref("binding_allowed", f"{PG}boolean"),
            "F_BINDING_DENIED",
        ),
    ]
    symbols = [
        node_symbol("binding", binding_type),
        node_symbol("binding_allowed", f"{PG}boolean"),
    ]
    return nodes, symbols


def build_producer_body() -> dict[str, Any]:
    body_id = FABRIC + "project_update_confirm_reschedule_v1"
    nodes = [node(f"{body_id}.p01", "ASSERT_ISOLATION", required="READ_COMMITTED")]
    binding_nodes, binding_symbols = binding_fragment(f"{body_id}.p02", "PRODUCER")
    nodes.extend(binding_nodes)
    symbols = [symbol("command_id", f"{PG}uuid", "INPUT"), *binding_symbols]

    binding_relation = FABRIC + "context_service_practice_binding"
    claim_relation = "public.appointment_command_idempotency"
    appointment_relation = "public.appointments"
    audit_relation = "public.appointment_audit_log"
    event_relation = "public.diary_committed_events"
    alias_relation = FABRIC + "diary_context_aggregate_aliases_v1"
    head_relation = FABRIC + "context_observation_stream_head"
    outbox_relation = FABRIC + "diary_context_observation_outbox_v1"

    practice = column_ref("binding", binding_relation, "practice_id", f"{PG}uuid")
    source_contract = column_ref(
        "binding",
        binding_relation,
        "source_contract_id",
        f"{FABRIC}source_contract_code",
    )
    stream = column_ref("binding", binding_relation, "stream_id", f"{PG}uuid")
    tx = transaction_timestamp()

    claim_id = f"{body_id}.p03"
    claim_columns = [
        "id",
        "practice_id",
        "operation_id",
        "route_family",
        "request_body_hash",
        "state",
        "target_appointment_id",
        "audit_log_id",
        "created_at",
        "xmin",
    ]
    nodes.append(
        select_node(
            claim_id,
            relation=claim_relation,
            columns=claim_columns,
            predicate=all_of(
                eq(
                    source_column(claim_relation, "id", f"{PG}uuid"),
                    input_ref("command_id", f"{PG}uuid"),
                ),
                eq(source_column(claim_relation, "practice_id", f"{PG}uuid"), practice),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="claim",
            order_by=["practice_id", "id"],
        )
    )
    symbols.append(node_symbol("claim", claim_relation))
    claim = lambda column, type_name: column_ref(
        "claim", claim_relation, column, type_name
    )
    nodes.append(
        assert_node(
            f"{body_id}.p04",
            all_of(
                eq(
                    claim("operation_id", f"{PG}text"),
                    const(f"{PG}text", "confirmAppointmentUpdateProposal"),
                ),
                eq(
                    claim("route_family", f"{PG}text"),
                    const(f"{PG}text", "update-confirm"),
                ),
                eq(claim("state", f"{PG}text"), const(f"{PG}text", "in_progress")),
                unary("IS_NOT_NULL", claim("request_body_hash", f"{PG}text")),
                unary("IS_NOT_NULL", claim("target_appointment_id", f"{PG}uuid")),
                unary("IS_NOT_NULL", claim("audit_log_id", f"{PG}uuid")),
                eq(claim("created_at", f"{PG}timestamptz"), tx),
                xmin_equals_current(local_ref("claim", claim_relation)),
            ),
            "F_CLAIM",
        )
    )

    appointment_id = f"{body_id}.p05"
    appointment_columns = [
        "id",
        "practice_id",
        "practitioner_id",
        "location_id",
        "start_time",
        "duration_minutes",
        "xmin",
    ]
    nodes.append(
        select_node(
            appointment_id,
            relation=appointment_relation,
            columns=appointment_columns,
            predicate=all_of(
                eq(
                    source_column(appointment_relation, "practice_id", f"{PG}uuid"),
                    practice,
                ),
                eq(
                    source_column(appointment_relation, "id", f"{PG}uuid"),
                    claim("target_appointment_id", f"{PG}uuid"),
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="appointment",
            order_by=["practice_id", "id"],
        )
    )
    symbols.append(node_symbol("appointment", appointment_relation))
    appointment = lambda column, type_name: column_ref(
        "appointment", appointment_relation, column, type_name
    )
    nodes.append(
        assert_node(
            f"{body_id}.p06",
            all_of(
                xmin_equals_current(local_ref("appointment", appointment_relation)),
                binary(
                    "GT",
                    appointment("duration_minutes", f"{PG}integer"),
                    const(f"{PG}integer", 0),
                ),
            ),
            "F_PROVENANCE",
        )
    )

    audit_id = f"{body_id}.p07"
    audit_columns = [
        "id",
        "practice_id",
        "appointment_id",
        "action",
        "command_id",
        "created_at",
        "xmin",
    ]
    nodes.append(
        select_node(
            audit_id,
            relation=audit_relation,
            columns=audit_columns,
            predicate=all_of(
                eq(source_column(audit_relation, "practice_id", f"{PG}uuid"), practice),
                eq(
                    source_column(audit_relation, "id", f"{PG}uuid"),
                    claim("audit_log_id", f"{PG}uuid"),
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="audit",
            order_by=["practice_id", "id"],
        )
    )
    symbols.append(node_symbol("audit", audit_relation))
    audit = lambda column, type_name: column_ref(
        "audit", audit_relation, column, type_name
    )
    nodes.append(
        assert_node(
            f"{body_id}.p08",
            all_of(
                eq(
                    audit("appointment_id", f"{PG}uuid"), appointment("id", f"{PG}uuid")
                ),
                eq(audit("command_id", f"{PG}uuid"), claim("id", f"{PG}uuid")),
                eq(audit("action", f"{PG}text"), const(f"{PG}text", "update")),
                xmin_equals_current(local_ref("audit", audit_relation)),
            ),
            "F_MEMBERSHIP",
        )
    )

    audit_set_id = f"{body_id}.p09"
    nodes.append(
        select_node(
            audit_set_id,
            relation=audit_relation,
            columns=["id"],
            predicate=all_of(
                eq(source_column(audit_relation, "practice_id", f"{PG}uuid"), practice),
                eq(
                    source_column(audit_relation, "appointment_id", f"{PG}uuid"),
                    appointment("id", f"{PG}uuid"),
                ),
            ),
            cardinality="COMPLETE_SET",
            output_symbol="audit_ids",
            order_by=["id"],
            set_read=True,
        )
    )
    symbols.append(node_symbol("audit_ids", audit_relation + "[]"))
    nodes.append(
        let_node(
            f"{body_id}.p10",
            "aggregate_revision",
            f"{PG}bigint",
            {
                "op": "COUNT",
                "operand": local_ref("audit_ids", audit_relation + "[]"),
                "type": f"{PG}bigint",
            },
        )
    )
    symbols.append(node_symbol("aggregate_revision", f"{PG}bigint"))
    nodes.append(
        assert_node(
            f"{body_id}.p10a",
            binary(
                "GT",
                local_ref("aggregate_revision", f"{PG}bigint"),
                const(f"{PG}bigint", 0),
            ),
            "F_MEMBERSHIP",
        )
    )

    event_id = f"{body_id}.p11"
    event_columns = [
        "id",
        "practice_id",
        "event_type",
        "schema_version",
        "source_system",
        "appointment_id",
        "aggregate_revision",
        "occurred_at",
        "command_id",
        "audit_log_id",
        "payload",
        "created_at",
        "xmin",
    ]
    nodes.append(
        select_node(
            event_id,
            relation=event_relation,
            columns=event_columns,
            predicate=all_of(
                eq(source_column(event_relation, "practice_id", f"{PG}uuid"), practice),
                eq(
                    source_column(event_relation, "command_id", f"{PG}uuid"),
                    claim("id", f"{PG}uuid"),
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="event",
            order_by=["practice_id", "id"],
        )
    )
    symbols.append(node_symbol("event", event_relation))
    event = lambda column, type_name: column_ref(
        "event", event_relation, column, type_name
    )
    payload = event("payload", f"{PG}jsonb")
    end_time = {
        "op": "TIMESTAMP_ADD_MINUTES",
        "left": appointment("start_time", f"{PG}timestamptz"),
        "right": appointment("duration_minutes", f"{PG}integer"),
        "type": f"{PG}timestamptz",
    }
    nodes.append(
        assert_node(
            f"{body_id}.p12",
            all_of(
                eq(
                    event("event_type", f"{PG}text"),
                    const(f"{PG}text", "diary.appointment_rescheduled"),
                ),
                eq(
                    event("schema_version", f"{PG}text"),
                    const(f"{PG}text", "diary.appointment_rescheduled.v1"),
                ),
                eq(
                    event("source_system", f"{PG}text"),
                    const(f"{PG}text", "emr4-diary"),
                ),
                eq(
                    event("appointment_id", f"{PG}uuid"), appointment("id", f"{PG}uuid")
                ),
                eq(event("audit_log_id", f"{PG}uuid"), audit("id", f"{PG}uuid")),
                eq(
                    event("aggregate_revision", f"{PG}bigint"),
                    local_ref("aggregate_revision", f"{PG}bigint"),
                ),
                xmin_equals_current(local_ref("event", event_relation)),
                {
                    "op": "JSON_KEYS_EXACT",
                    "source": payload,
                    "keys": [
                        "appointment_id",
                        "practitioner_id",
                        "location_id",
                        "start_time",
                        "end_time",
                        "reason_codes",
                    ],
                    "type": f"{PG}boolean",
                },
                eq(
                    json_value(payload, "appointment_id", f"{PG}uuid"),
                    appointment("id", f"{PG}uuid"),
                ),
                eq(
                    json_value(payload, "practitioner_id", f"{PG}uuid"),
                    appointment("practitioner_id", f"{PG}uuid"),
                ),
                unary(
                    "NOT",
                    is_distinct(
                        json_value(payload, "location_id", f"{PG}uuid"),
                        appointment("location_id", f"{PG}uuid"),
                    ),
                ),
                eq(
                    json_value(payload, "start_time", f"{PG}timestamptz"),
                    appointment("start_time", f"{PG}timestamptz"),
                ),
                eq(json_value(payload, "end_time", f"{PG}timestamptz"), end_time),
                eq(
                    json_value(payload, "reason_codes", f"{PG}text[]"),
                    array_const(f"{PG}text[]", ["appointment_time_changed"]),
                ),
            ),
            "F_MEMBERSHIP",
        )
    )

    nodes.append(let_node(f"{body_id}.p13a", "candidate_alias", f"{PG}uuid", uuid_v4()))
    symbols.append(node_symbol("candidate_alias", f"{PG}uuid"))
    alias_columns = [
        "practice_id",
        "source_contract_id",
        "product_appointment_uuid",
        "opaque_aggregate_alias",
        "created_at",
        "stream_id",
    ]
    alias_bindings = [
        ("practice_id", practice),
        ("source_contract_id", source_contract),
        ("stream_id", stream),
        ("product_appointment_uuid", appointment("id", f"{PG}uuid")),
        ("opaque_aggregate_alias", local_ref("candidate_alias", f"{PG}uuid")),
        ("created_at", tx),
    ]
    alias_winner = all_of(
        eq(source_column(alias_relation, "practice_id", f"{PG}uuid"), practice),
        eq(
            source_column(
                alias_relation, "source_contract_id", f"{FABRIC}source_contract_code"
            ),
            source_contract,
        ),
        eq(source_column(alias_relation, "stream_id", f"{PG}uuid"), stream),
        eq(
            source_column(alias_relation, "product_appointment_uuid", f"{PG}uuid"),
            appointment("id", f"{PG}uuid"),
        ),
    )
    nodes.append(
        insert_node(
            f"{body_id}.p13",
            relation=alias_relation,
            bindings=alias_bindings,
            output_symbol="alias",
            returning_columns=alias_columns,
            reload_key=[
                "practice_id",
                "source_contract_id",
                "stream_id",
                "product_appointment_uuid",
            ],
            winner_predicate=alias_winner,
        )
    )
    symbols.append(node_symbol("alias", alias_relation))
    alias = lambda column, type_name: column_ref(
        "alias", alias_relation, column, type_name
    )
    alias_lock_id = f"{body_id}.p15"
    nodes.append(
        lock_node(
            alias_lock_id,
            relation=alias_relation,
            predicate=alias_winner,
            key_columns=[
                "practice_id",
                "source_contract_id",
                "stream_id",
                "product_appointment_uuid",
            ],
            mode="FOR_KEY_SHARE",
            order=1,
            output_symbol="locked_alias",
            columns=alias_columns,
        )
    )
    symbols.append(node_symbol("locked_alias", alias_relation))

    head_columns = [
        "practice_id",
        "source_contract_id",
        "stream_id",
        "stream_epoch",
        "last_position",
        "updated_at",
    ]
    head_predicate = all_of(
        eq(source_column(head_relation, "practice_id", f"{PG}uuid"), practice),
        eq(
            source_column(
                head_relation, "source_contract_id", f"{FABRIC}source_contract_code"
            ),
            source_contract,
        ),
        eq(source_column(head_relation, "stream_id", f"{PG}uuid"), stream),
    )
    nodes.append(
        lock_node(
            f"{body_id}.p16",
            relation=head_relation,
            predicate=head_predicate,
            key_columns=["practice_id", "source_contract_id", "stream_id"],
            mode="FOR_UPDATE",
            order=2,
            output_symbol="head",
            columns=head_columns,
        )
    )
    symbols.append(node_symbol("head", head_relation))
    head = lambda column, type_name: column_ref(
        "head", head_relation, column, type_name
    )
    nodes.append(
        assert_node(
            f"{body_id}.p16a",
            all_of(
                eq(head("stream_epoch", f"{PG}bigint"), const(f"{PG}bigint", 1)),
                binary(
                    "LT",
                    head("last_position", f"{PG}bigint"),
                    const(f"{PG}bigint", 9223372036854775807),
                ),
            ),
            "F_STREAM",
        )
    )
    nodes.append(
        let_node(
            f"{body_id}.p17",
            "next_position",
            f"{PG}bigint",
            add(
                head("last_position", f"{PG}bigint"),
                const(f"{PG}bigint", 1),
                f"{PG}bigint",
            ),
        )
    )
    symbols.append(node_symbol("next_position", f"{PG}bigint"))
    nodes.append(
        let_node(
            f"{body_id}.p18",
            "source_contract_digest",
            f"{FABRIC}digest_sha256",
            digest(
                f"{FABRIC}source_contract_digest_v1",
                [
                    source_contract,
                    event("event_type", f"{PG}text"),
                    event("schema_version", f"{PG}text"),
                ],
            ),
        )
    )
    symbols.append(node_symbol("source_contract_digest", f"{FABRIC}digest_sha256"))
    outbox_columns = [
        "practice_id",
        "source_contract_id",
        "stream_id",
        "stream_epoch",
        "transaction_position",
        "predecessor_position",
        "raw_event_uuid",
        "opaque_aggregate_alias",
        "aggregate_revision",
        "source_contract_digest",
        "transaction_authored_at",
    ]
    outbox_bindings = [
        ("practice_id", practice),
        ("source_contract_id", source_contract),
        ("stream_id", stream),
        ("stream_epoch", head("stream_epoch", f"{PG}bigint")),
        ("transaction_position", local_ref("next_position", f"{PG}bigint")),
        ("predecessor_position", head("last_position", f"{PG}bigint")),
        ("raw_event_uuid", event("id", f"{PG}uuid")),
        ("opaque_aggregate_alias", alias("opaque_aggregate_alias", f"{PG}uuid")),
        ("aggregate_revision", local_ref("aggregate_revision", f"{PG}bigint")),
        (
            "source_contract_digest",
            local_ref("source_contract_digest", f"{FABRIC}digest_sha256"),
        ),
        ("transaction_authored_at", tx),
    ]
    nodes.append(
        insert_node(
            f"{body_id}.p19",
            relation=outbox_relation,
            bindings=outbox_bindings,
            output_symbol="inserted_outbox",
            returning_columns=outbox_columns,
        )
    )
    symbols.append(node_symbol("inserted_outbox", outbox_relation))
    nodes.append(
        update_node(
            f"{body_id}.p20",
            relation=head_relation,
            predicate=head_predicate,
            key_columns=["practice_id", "source_contract_id", "stream_id"],
            bindings=[
                ("last_position", local_ref("next_position", f"{PG}bigint")),
                ("updated_at", tx),
            ],
            output_symbol="updated_head",
            returning_columns=head_columns,
        )
    )
    symbols.append(node_symbol("updated_head", head_relation))
    final_outbox_id = f"{body_id}.p21"
    nodes.append(
        select_node(
            final_outbox_id,
            relation=outbox_relation,
            columns=outbox_columns,
            predicate=all_of(
                eq(
                    source_column(outbox_relation, "practice_id", f"{PG}uuid"), practice
                ),
                eq(
                    source_column(
                        outbox_relation,
                        "source_contract_id",
                        f"{FABRIC}source_contract_code",
                    ),
                    source_contract,
                ),
                eq(source_column(outbox_relation, "stream_id", f"{PG}uuid"), stream),
                eq(
                    source_column(outbox_relation, "stream_epoch", f"{PG}bigint"),
                    head("stream_epoch", f"{PG}bigint"),
                ),
                eq(
                    source_column(
                        outbox_relation, "transaction_position", f"{PG}bigint"
                    ),
                    local_ref("next_position", f"{PG}bigint"),
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="outbox",
            order_by=[
                "practice_id",
                "source_contract_id",
                "stream_id",
                "stream_epoch",
                "transaction_position",
            ],
        )
    )
    symbols.append(node_symbol("outbox", outbox_relation))
    nodes.append(
        node(
            f"{body_id}.retry_or_return",
            "IF",
            condition=const(f"{PG}boolean", False),
            then=[propagate_retryable(f"{body_id}.retry")],
            convergence="ALL_TERMINAL",
            **{"else": [return_row(f"{body_id}.p22", "outbox", outbox_relation)]},
        )
    )
    return body(body_id, "ENTRY_POINT", body_id, symbols, nodes)


def build_contract() -> dict[str, Any]:
    """Build and semantically seal the complete unmounted contract."""

    from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs import (
        build_entry_programs,
    )
    from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs import (
        build_trigger_programs,
    )
    from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator import (
        EXPRESSION_OPCODES,
        INSTRUCTION_OPCODES,
        assert_contract_valid,
        derive_contract_semantics,
    )

    parent = _read_json(PARENT_PATH)
    if parent.get("contract_sha256") != PARENT_DIGEST:
        raise ValueError("parent contract digest field is not the frozen digest")
    if _canonical_digest(parent, "contract_sha256") != PARENT_DIGEST:
        raise ValueError("parent contract canonical content does not match its digest")

    signatures = build_signatures(parent)
    declarations = build_trigger_declarations(parent)
    programs = [
        build_producer_body(),
        *build_entry_programs(),
        *build_trigger_programs(),
    ]
    expected_ids = [
        *(FABRIC + name for name in ENTRY_POINT_NAMES),
        *(FABRIC + name for name in TRIGGER_FUNCTION_NAMES),
    ]
    if [program["id"] for program in programs] != expected_ids:
        raise ValueError("builder modules did not return the frozen body population")

    contract: dict[str, Any] = {
        "schema_version": "raisa.context_fabric.function_trigger_body_architecture.v3",
        "status": "architecture_only_unmounted_typed_ir",
        "contract_sha256": "sha256:pending",
        "parent_binding": {
            "path": str(PARENT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "contract_sha256": PARENT_DIGEST,
            "relation_signature_trigger_and_role_authority": "RETAINED_EXCEPT_EXPLICIT_RECOVERY_OPERATIONS",
        },
        "structural_feasibility_recovery_v1": {
            "status": "CLOSED_TYPED_RECOVERY",
            "operations": copy.deepcopy(RECOVERY_OPERATIONS),
            "receiver_admission_concurrency": "RETAINED_FIRST_SELECT_THEN_UNIQUE_INSERT_OR_RELOAD_COMPARE",
            "receiver_row_lock_privilege_required": False,
        },
        "effective_parent_summary": {
            "effective_signatures": signatures,
            "trigger_declarations": declarations,
            "effective_roles": build_effective_roles(parent),
        },
        "qualified_identifier_catalogue": build_catalogue(parent),
        "typed_ir_contract": {
            "version": "closed_typed_ir_v2",
            "execution": "UNMOUNTED_NO_RENDERER",
            "instruction_opcodes": sorted(INSTRUCTION_OPCODES),
            "expression_opcodes": sorted(EXPRESSION_OPCODES),
            "cardinalities": [
                "EXACTLY_ONE",
                "ZERO_OR_ONE",
                "COMPLETE_SET",
                "EXACTLY_ONE_OR_RAISE",
            ],
            "rules": {
                "raw_sql": False,
                "dynamic_execution": False,
                "transaction_control": False,
                "internal_retry": False,
                "recursion": False,
                "authored_effect_summaries": False,
                "unqualified_identifiers": False,
            },
        },
        "derivation_profile_catalogue": [],
        "predicate_catalogue": [],
        "failure_registry": failure_registry(),
        "body_programs": programs,
        "trigger_applicability_return_matrix": build_trigger_matrix(declarations),
        "call_graph": {},
        "effect_derivation": {
            "authority": "DETERMINISTIC_OPERAND_WALK",
            "validator": "scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py",
            "stored_summaries_are_recomputed": True,
        },
        "renderer_order": expected_ids,
        "artifact_boundary": {
            "architecture_only": True,
            "unmounted": True,
            "executable_ddl": False,
            "database_contact": False,
            "provider_contact": False,
            "runtime_wiring": False,
            "product_or_patient_data": False,
            "migration_or_source_writes": False,
            "renderer_present": False,
        },
    }

    derived = derive_contract_semantics(contract)
    for program in contract["body_programs"]:
        program["derived_effect_summary"] = derived["body_summaries"][program["id"]]
    contract["call_graph"] = derived["call_graph"]
    contract["contract_sha256"] = _canonical_digest(contract, "contract_sha256")
    assert_contract_valid(contract)
    return contract


def write_artifacts() -> tuple[Path, Path]:
    """Generate the contract and structural schema after deterministic validation."""

    from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema import (
        build_schema,
    )

    contract = build_contract()
    schema = build_schema(contract)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_PATH.write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    SCHEMA_PATH.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return CONTRACT_PATH, SCHEMA_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="build and validate in memory without writing artifacts",
    )
    args = parser.parse_args()
    if args.check:
        contract = build_contract()
        print(contract["contract_sha256"])
    else:
        contract_path, schema_path = write_artifacts()
        print(contract_path)
        print(schema_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
