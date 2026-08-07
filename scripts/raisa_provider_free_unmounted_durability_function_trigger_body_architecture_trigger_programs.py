"""Typed trigger programs for the unmounted durability body architecture.

This module is an offline manifest component.  It builds typed dictionaries
only; it renders no SQL and performs no database, product, provider, or network
operation.
"""

from __future__ import annotations

from typing import Any

from scripts import (
    raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder
    as dsl,
)


PG = dsl.PG
FABRIC = dsl.FABRIC

CLAIM = "public.appointment_command_idempotency"
APPOINTMENT = "public.appointments"
AUDIT = "public.appointment_audit_log"
EVENT = "public.diary_committed_events"
BINDING = FABRIC + "context_service_practice_binding"
ALIAS = FABRIC + "diary_context_aggregate_aliases_v1"
HEAD = FABRIC + "context_observation_stream_head"
OUTBOX = FABRIC + "diary_context_observation_outbox_v1"
POLICY = FABRIC + "context_retention_policy"

SOURCE_CONTRACT = "diary.appointment_rescheduled.v1"
EVENT_TYPE = "diary.appointment_rescheduled"
EVENT_SCHEMA = "diary.appointment_rescheduled.v1"
EVENT_SOURCE = "emr4-diary"
OPERATION_ID = "confirmAppointmentUpdateProposal"
ROUTE_FAMILY = "update-confirm"


CLAIM_COLUMNS = [
    "id", "practice_id", "operation_id", "route_family", "request_body_hash",
    "state", "target_appointment_id", "audit_log_id", "created_at", "xmin",
]
APPOINTMENT_COLUMNS = [
    "id", "practice_id", "practitioner_id", "location_id", "start_time",
    "duration_minutes", "xmin",
]
AUDIT_COLUMNS = [
    "id", "practice_id", "appointment_id", "action", "command_id",
    "created_at", "xmin",
]
EVENT_COLUMNS = [
    "id", "practice_id", "event_type", "schema_version", "source_system",
    "appointment_id", "aggregate_revision", "occurred_at", "command_id",
    "audit_log_id", "payload", "created_at", "xmin",
]
ALIAS_COLUMNS = [
    "practice_id", "source_contract_id", "stream_id",
    "product_appointment_uuid", "opaque_aggregate_alias", "created_at",
]
HEAD_COLUMNS = [
    "practice_id", "source_contract_id", "stream_id", "stream_epoch",
    "last_position", "updated_at",
]
OUTBOX_COLUMNS = [
    "practice_id", "source_contract_id", "stream_id", "stream_epoch",
    "transaction_position", "predecessor_position", "raw_event_uuid",
    "opaque_aggregate_alias", "aggregate_revision", "source_contract_digest",
    "transaction_authored_at",
]


def _t(image: str, relation: str, column: str, type_name: str) -> dict[str, Any]:
    return dsl.trigger_column_ref(image, relation, column, type_name)


def _r(symbol: str, relation: str, column: str, type_name: str) -> dict[str, Any]:
    return dsl.column_ref(symbol, relation, column, type_name)


def _not(value: dict[str, Any]) -> dict[str, Any]:
    return dsl.unary("NOT", value)


def _same(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return _not(dsl.is_distinct(left, right))


def _count(symbol: str, relation: str) -> dict[str, Any]:
    return {
        "op": "COUNT",
        "operand": dsl.local_ref(symbol, relation + "[]"),
        "type": f"{PG}bigint",
    }


def _return(node_id: str, kind: str) -> dict[str, Any]:
    return dsl.node(node_id, kind)


def _raise(node_id: str, failure_id: str) -> dict[str, Any]:
    return dsl.node(node_id, "RAISE", failure_id=failure_id)


def _if(
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
        convergence="ALL_TERMINAL",
    )


def _switch(
    node_id: str,
    arms: list[tuple[str, list[dict[str, Any]]]],
) -> dict[str, Any]:
    return dsl.node(
        node_id,
        "SWITCH_TG_OP",
        arms=[{"tg_op": operation, "nodes": nodes} for operation, nodes in arms],
        default=[_raise(node_id + ".default.raise", "F_TRIGGER_CONTEXT")],
        convergence="ALL_TERMINAL",
    )


def _context(
    node_id: str,
    relation: str,
    timing: str,
) -> dict[str, Any]:
    schema, table = relation.split(".", 1)
    return dsl.assert_node(
        node_id,
        dsl.all_of(
            dsl.eq(
                dsl.system_ref("TG_TABLE_SCHEMA", f"{PG}name"),
                dsl.const(f"{PG}name", schema),
            ),
            dsl.eq(
                dsl.system_ref("TG_TABLE_NAME", f"{PG}name"),
                dsl.const(f"{PG}name", table),
            ),
            dsl.eq(
                dsl.system_ref("TG_WHEN", f"{PG}text"),
                dsl.const(f"{PG}text", timing),
            ),
            dsl.eq(
                dsl.system_ref("TG_LEVEL", f"{PG}text"),
                dsl.const(f"{PG}text", "ROW"),
            ),
        ),
        "F_TRIGGER_CONTEXT",
    )


def _claim_exact(image: str) -> dict[str, Any]:
    return dsl.all_of(
        dsl.eq(
            _t(image, CLAIM, "operation_id", f"{PG}text"),
            dsl.const(f"{PG}text", OPERATION_ID),
        ),
        dsl.eq(
            _t(image, CLAIM, "route_family", f"{PG}text"),
            dsl.const(f"{PG}text", ROUTE_FAMILY),
        ),
    )


def _event_exact(image: str) -> dict[str, Any]:
    return dsl.all_of(
        dsl.eq(
            _t(image, EVENT, "event_type", f"{PG}text"),
            dsl.const(f"{PG}text", EVENT_TYPE),
        ),
        dsl.eq(
            _t(image, EVENT, "schema_version", f"{PG}text"),
            dsl.const(f"{PG}text", EVENT_SCHEMA),
        ),
    )


def _audit_command_nodes(
    prefix: str, image: str, output_symbol: str
) -> list[dict[str, Any]]:
    """Read one image's command family through exactly four command columns."""
    predicate = dsl.all_of(
        dsl.eq(
            dsl.source_column(CLAIM, "practice_id", f"{PG}uuid"),
            _t(image, AUDIT, "practice_id", f"{PG}uuid"),
        ),
        dsl.eq(
            dsl.source_column(CLAIM, "id", f"{PG}uuid"),
            _t(image, AUDIT, "command_id", f"{PG}uuid"),
        ),
        dsl.eq(
            dsl.source_column(CLAIM, "operation_id", f"{PG}text"),
            dsl.const(f"{PG}text", OPERATION_ID),
        ),
        dsl.eq(
            dsl.source_column(CLAIM, "route_family", f"{PG}text"),
            dsl.const(f"{PG}text", ROUTE_FAMILY),
        ),
    )
    return [
        dsl.select_node(
            prefix,
            relation=CLAIM,
            columns=["practice_id", "id", "operation_id", "route_family"],
            predicate=predicate,
            cardinality="COMPLETE_SET",
            output_symbol=output_symbol,
            order_by=["practice_id", "id"],
            set_read=True,
        )
    ]


def _one(symbol: str, relation: str) -> dict[str, Any]:
    return dsl.eq(_count(symbol, relation), dsl.const(f"{PG}bigint", 1))


def _binding_predicate(
    capability: str,
    practice: dict[str, Any],
    stream: dict[str, Any] | None = None,
) -> dict[str, Any]:
    parts = [
        dsl.eq(
            dsl.source_column(BINDING, "database_login", f"{PG}name"),
            dsl.system_ref("SESSION_USER", f"{PG}name"),
        ),
        dsl.eq(
            dsl.source_column(
                BINDING, "logical_capability", f"{FABRIC}logical_capability"
            ),
            dsl.const(f"{FABRIC}logical_capability", capability),
        ),
        dsl.eq(
            dsl.source_column(BINDING, "practice_id", f"{PG}uuid"),
            practice,
        ),
        dsl.eq(
            dsl.source_column(
                BINDING, "source_contract_id", f"{FABRIC}source_contract_code"
            ),
            dsl.const(f"{FABRIC}source_contract_code", SOURCE_CONTRACT),
        ),
        dsl.binary(
            "LTE",
            dsl.source_column(BINDING, "active_from", f"{PG}timestamptz"),
            dsl.transaction_timestamp(),
        ),
        dsl.any_of(
            dsl.unary(
                "IS_NULL",
                dsl.source_column(BINDING, "active_until", f"{PG}timestamptz"),
            ),
            dsl.binary(
                "GT",
                dsl.source_column(BINDING, "active_until", f"{PG}timestamptz"),
                dsl.transaction_timestamp(),
            ),
        ),
    ]
    if stream is not None:
        parts.append(
            dsl.eq(
                dsl.source_column(BINDING, "stream_id", f"{PG}uuid"), stream
            )
        )
    return dsl.all_of(*parts)


def _binding_nodes(
    prefix: str,
    capability: str,
    practice: dict[str, Any],
    stream: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    predicate = _binding_predicate(capability, practice, stream)
    return [
        dsl.select_node(
            prefix + ".select",
            relation=BINDING,
            columns=dsl.BINDING_COLUMNS,
            predicate=predicate,
            cardinality="EXACTLY_ONE",
            output_symbol="binding",
            order_by=["database_login", "logical_capability", "practice_id"],
        ),
        dsl.node(
            prefix + ".support",
            "CALL_SUPPORT",
            function=FABRIC + "session_binding_allows_v1",
            arguments=[
                dsl.system_ref("SESSION_USER", f"{PG}name"),
                dsl.array_const(f"{FABRIC}logical_capability[]", [capability]),
                _r("binding", BINDING, "practice_id", f"{PG}uuid"),
                _r(
                    "binding", BINDING, "source_contract_id",
                    f"{FABRIC}source_contract_code",
                ),
                _r("binding", BINDING, "stream_id", f"{PG}uuid"),
                dsl.transaction_timestamp(),
            ],
            output_symbol="binding_allowed",
        ),
        dsl.assert_node(
            prefix + ".assert",
            dsl.local_ref("binding_allowed", f"{PG}boolean"),
            "F_BINDING_DENIED",
        ),
    ]


def _binding_symbols() -> list[dict[str, Any]]:
    return [
        dsl.node_symbol("binding", BINDING),
        dsl.node_symbol("binding_allowed", f"{PG}boolean"),
    ]


def _producer_membership_symbols() -> list[dict[str, Any]]:
    return [
        dsl.node_symbol("claim", CLAIM),
        dsl.node_symbol("appointment", APPOINTMENT),
        dsl.node_symbol("audit", AUDIT),
        dsl.node_symbol("audit_ids", AUDIT + "[]"),
        dsl.node_symbol("aggregate_revision", f"{PG}bigint"),
        dsl.node_symbol("event", EVENT),
        dsl.node_symbol("alias", ALIAS),
        dsl.node_symbol("head", HEAD),
        dsl.node_symbol("outbox", OUTBOX),
    ]


def _producer_membership_nodes(
    prefix: str,
    practice: dict[str, Any],
    *,
    command_id: dict[str, Any] | None = None,
    appointment_id: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Expand the exact C/A/U/E/L/H/O membership proof into typed nodes."""
    if (command_id is None) == (appointment_id is None):
        raise ValueError("exactly one producer membership anchor is required")
    binding_stream = _r("binding", BINDING, "stream_id", f"{PG}uuid")
    claim_predicates = [
        dsl.eq(dsl.source_column(CLAIM, "practice_id", f"{PG}uuid"), practice),
        dsl.eq(
            dsl.source_column(CLAIM, "operation_id", f"{PG}text"),
            dsl.const(f"{PG}text", OPERATION_ID),
        ),
        dsl.eq(
            dsl.source_column(CLAIM, "route_family", f"{PG}text"),
            dsl.const(f"{PG}text", ROUTE_FAMILY),
        ),
    ]
    if command_id is not None:
        claim_predicates.append(
            dsl.eq(dsl.source_column(CLAIM, "id", f"{PG}uuid"), command_id)
        )
    else:
        claim_predicates.append(
            dsl.eq(
                dsl.source_column(CLAIM, "target_appointment_id", f"{PG}uuid"),
                appointment_id,
            )
        )
    nodes: list[dict[str, Any]] = [
        dsl.select_node(
            prefix + ".claim",
            relation=CLAIM,
            columns=CLAIM_COLUMNS,
            predicate=dsl.all_of(*claim_predicates),
            cardinality="EXACTLY_ONE",
            output_symbol="claim",
            order_by=["practice_id", "id"],
        )
    ]
    claim = lambda column, type_name: _r("claim", CLAIM, column, type_name)
    nodes.append(
        dsl.select_node(
            prefix + ".appointment",
            relation=APPOINTMENT,
            columns=APPOINTMENT_COLUMNS,
            predicate=dsl.all_of(
                dsl.eq(
                    dsl.source_column(APPOINTMENT, "practice_id", f"{PG}uuid"),
                    practice,
                ),
                dsl.eq(
                    dsl.source_column(APPOINTMENT, "id", f"{PG}uuid"),
                    claim("target_appointment_id", f"{PG}uuid"),
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="appointment",
            order_by=["practice_id", "id"],
        )
    )
    appointment = lambda column, type_name: _r(
        "appointment", APPOINTMENT, column, type_name
    )
    nodes.append(
        dsl.select_node(
            prefix + ".audit",
            relation=AUDIT,
            columns=AUDIT_COLUMNS,
            predicate=dsl.all_of(
                dsl.eq(
                    dsl.source_column(AUDIT, "practice_id", f"{PG}uuid"),
                    practice,
                ),
                dsl.eq(
                    dsl.source_column(AUDIT, "id", f"{PG}uuid"),
                    claim("audit_log_id", f"{PG}uuid"),
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="audit",
            order_by=["practice_id", "id"],
        )
    )
    audit = lambda column, type_name: _r("audit", AUDIT, column, type_name)
    nodes.append(
        dsl.select_node(
            prefix + ".audit-set",
            relation=AUDIT,
            columns=["id"],
            predicate=dsl.all_of(
                dsl.eq(
                    dsl.source_column(AUDIT, "practice_id", f"{PG}uuid"), practice
                ),
                dsl.eq(
                    dsl.source_column(AUDIT, "appointment_id", f"{PG}uuid"),
                    appointment("id", f"{PG}uuid"),
                ),
            ),
            cardinality="COMPLETE_SET",
            output_symbol="audit_ids",
            order_by=["id"],
            set_read=True,
        )
    )
    nodes.append(
        dsl.let_node(
            prefix + ".audit-count",
            "aggregate_revision",
            f"{PG}bigint",
            {
                "op": "COUNT",
                "operand": dsl.local_ref("audit_ids", AUDIT + "[]"),
                "type": f"{PG}bigint",
            },
        )
    )
    nodes.append(
        dsl.select_node(
            prefix + ".event",
            relation=EVENT,
            columns=EVENT_COLUMNS,
            predicate=dsl.all_of(
                dsl.eq(
                    dsl.source_column(EVENT, "practice_id", f"{PG}uuid"), practice
                ),
                dsl.eq(
                    dsl.source_column(EVENT, "command_id", f"{PG}uuid"),
                    claim("id", f"{PG}uuid"),
                ),
                dsl.eq(
                    dsl.source_column(EVENT, "event_type", f"{PG}text"),
                    dsl.const(f"{PG}text", EVENT_TYPE),
                ),
                dsl.eq(
                    dsl.source_column(EVENT, "schema_version", f"{PG}text"),
                    dsl.const(f"{PG}text", EVENT_SCHEMA),
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="event",
            order_by=["practice_id", "id"],
        )
    )
    event = lambda column, type_name: _r("event", EVENT, column, type_name)
    nodes.append(
        dsl.select_node(
            prefix + ".alias",
            relation=ALIAS,
            columns=ALIAS_COLUMNS,
            predicate=dsl.all_of(
                dsl.eq(
                    dsl.source_column(ALIAS, "practice_id", f"{PG}uuid"), practice
                ),
                dsl.eq(
                    dsl.source_column(
                        ALIAS, "source_contract_id",
                        f"{FABRIC}source_contract_code",
                    ),
                    dsl.const(f"{FABRIC}source_contract_code", SOURCE_CONTRACT),
                ),
                dsl.eq(
                    dsl.source_column(ALIAS, "stream_id", f"{PG}uuid"),
                    binding_stream,
                ),
                dsl.eq(
                    dsl.source_column(
                        ALIAS, "product_appointment_uuid", f"{PG}uuid"
                    ),
                    appointment("id", f"{PG}uuid"),
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="alias",
            order_by=[
                "practice_id", "source_contract_id", "stream_id",
                "product_appointment_uuid",
            ],
        )
    )
    alias = lambda column, type_name: _r("alias", ALIAS, column, type_name)
    nodes.append(
        dsl.select_node(
            prefix + ".head",
            relation=HEAD,
            columns=HEAD_COLUMNS,
            predicate=dsl.all_of(
                dsl.eq(dsl.source_column(HEAD, "practice_id", f"{PG}uuid"), practice),
                dsl.eq(
                    dsl.source_column(
                        HEAD, "source_contract_id", f"{FABRIC}source_contract_code"
                    ),
                    dsl.const(f"{FABRIC}source_contract_code", SOURCE_CONTRACT),
                ),
                dsl.eq(
                    dsl.source_column(HEAD, "stream_id", f"{PG}uuid"),
                    binding_stream,
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="head",
            order_by=["practice_id", "source_contract_id", "stream_id"],
        )
    )
    nodes.append(
        dsl.select_node(
            prefix + ".outbox",
            relation=OUTBOX,
            columns=OUTBOX_COLUMNS,
            predicate=dsl.all_of(
                dsl.eq(
                    dsl.source_column(OUTBOX, "practice_id", f"{PG}uuid"), practice
                ),
                dsl.eq(
                    dsl.source_column(OUTBOX, "raw_event_uuid", f"{PG}uuid"),
                    event("id", f"{PG}uuid"),
                ),
                dsl.eq(
                    dsl.source_column(OUTBOX, "stream_id", f"{PG}uuid"),
                    binding_stream,
                ),
            ),
            cardinality="EXACTLY_ONE",
            output_symbol="outbox",
            order_by=[
                "practice_id", "source_contract_id", "stream_id",
                "stream_epoch", "transaction_position",
            ],
        )
    )
    head = lambda column, type_name: _r("head", HEAD, column, type_name)
    outbox = lambda column, type_name: _r("outbox", OUTBOX, column, type_name)
    payload = event("payload", f"{PG}jsonb")
    nodes.append(
        dsl.assert_node(
            prefix + ".assert",
            dsl.all_of(
                dsl.eq(claim("state", f"{PG}text"), dsl.const(f"{PG}text", "completed")),
                dsl.eq(claim("target_appointment_id", f"{PG}uuid"), appointment("id", f"{PG}uuid")),
                dsl.eq(claim("audit_log_id", f"{PG}uuid"), audit("id", f"{PG}uuid")),
                dsl.eq(audit("command_id", f"{PG}uuid"), claim("id", f"{PG}uuid")),
                dsl.eq(audit("appointment_id", f"{PG}uuid"), appointment("id", f"{PG}uuid")),
                dsl.eq(audit("action", f"{PG}text"), dsl.const(f"{PG}text", "update")),
                dsl.eq(event("source_system", f"{PG}text"), dsl.const(f"{PG}text", EVENT_SOURCE)),
                dsl.eq(event("appointment_id", f"{PG}uuid"), appointment("id", f"{PG}uuid")),
                dsl.eq(event("audit_log_id", f"{PG}uuid"), audit("id", f"{PG}uuid")),
                dsl.eq(event("aggregate_revision", f"{PG}bigint"), dsl.local_ref("aggregate_revision", f"{PG}bigint")),
                {"op": "JSON_KEYS_EXACT", "source": payload, "keys": ["appointment_id", "practitioner_id", "location_id", "start_time", "end_time", "reason_codes"], "type": f"{PG}boolean"},
                dsl.eq(dsl.json_value(payload, "appointment_id", f"{PG}uuid"), appointment("id", f"{PG}uuid")),
                dsl.eq(dsl.json_value(payload, "practitioner_id", f"{PG}uuid"), appointment("practitioner_id", f"{PG}uuid")),
                _same(dsl.json_value(payload, "location_id", f"{PG}uuid"), appointment("location_id", f"{PG}uuid")),
                dsl.eq(dsl.json_value(payload, "start_time", f"{PG}timestamptz"), appointment("start_time", f"{PG}timestamptz")),
                dsl.eq(
                    dsl.json_value(payload, "end_time", f"{PG}timestamptz"),
                    {"op": "TIMESTAMP_ADD_MINUTES", "left": appointment("start_time", f"{PG}timestamptz"), "right": appointment("duration_minutes", f"{PG}integer"), "type": f"{PG}timestamptz"},
                ),
                dsl.eq(dsl.json_value(payload, "reason_codes", f"{PG}text[]"), dsl.array_const(f"{PG}text[]", ["appointment_time_changed"])),
                dsl.eq(outbox("opaque_aggregate_alias", f"{PG}uuid"), alias("opaque_aggregate_alias", f"{PG}uuid")),
                dsl.eq(outbox("raw_event_uuid", f"{PG}uuid"), event("id", f"{PG}uuid")),
                dsl.eq(outbox("aggregate_revision", f"{PG}bigint"), event("aggregate_revision", f"{PG}bigint")),
                dsl.eq(outbox("stream_epoch", f"{PG}bigint"), head("stream_epoch", f"{PG}bigint")),
                dsl.eq(outbox("transaction_position", f"{PG}bigint"), head("last_position", f"{PG}bigint")),
                dsl.eq(outbox("predecessor_position", f"{PG}bigint"), dsl.add(outbox("transaction_position", f"{PG}bigint"), dsl.const(f"{PG}bigint", -1), f"{PG}bigint")),
                dsl.xmin_equals_current(dsl.local_ref("claim", CLAIM)),
                dsl.xmin_equals_current(dsl.local_ref("appointment", APPOINTMENT)),
                dsl.xmin_equals_current(dsl.local_ref("audit", AUDIT)),
                dsl.xmin_equals_current(dsl.local_ref("event", EVENT)),
                dsl.xmin_equals_current(dsl.local_ref("head", HEAD)),
                dsl.xmin_equals_current(dsl.local_ref("outbox", OUTBOX)),
            ),
            "F_TEMPORAL_BIJECTION",
        )
    )
    return nodes


def _base_symbols(*extra: dict[str, Any]) -> list[dict[str, Any]]:
    return [*extra]


def _build_guard_claim() -> dict[str, Any]:
    body_id = FABRIC + "cf_guard_claim_v1"
    update_exact = dsl.all_of(_claim_exact("OLD"), _claim_exact("NEW"))
    update_unrelated = dsl.all_of(_not(_claim_exact("OLD")), _not(_claim_exact("NEW")))
    immutable = dsl.all_of(
        *[
            _same(
                _t("OLD", CLAIM, column, type_name),
                _t("NEW", CLAIM, column, type_name),
            )
            for column, type_name in [
                ("id", f"{PG}uuid"), ("practice_id", f"{PG}uuid"),
                ("actor_user_id", f"{PG}uuid"), ("operation_id", f"{PG}text"),
                ("route_family", f"{PG}text"), ("request_body_hash", f"{PG}text"),
                ("created_at", f"{PG}timestamptz"),
            ]
        ]
    )
    monotonic = dsl.all_of(
        dsl.eq(_t("OLD", CLAIM, "state", f"{PG}text"), dsl.const(f"{PG}text", "in_progress")),
        dsl.any_of(
            dsl.eq(_t("NEW", CLAIM, "state", f"{PG}text"), dsl.const(f"{PG}text", "in_progress")),
            dsl.eq(_t("NEW", CLAIM, "state", f"{PG}text"), dsl.const(f"{PG}text", "completed")),
        ),
        dsl.any_of(
            _same(_t("OLD", CLAIM, "target_appointment_id", f"{PG}uuid"), _t("NEW", CLAIM, "target_appointment_id", f"{PG}uuid")),
            dsl.all_of(dsl.unary("IS_NULL", _t("OLD", CLAIM, "target_appointment_id", f"{PG}uuid")), dsl.unary("IS_NOT_NULL", _t("NEW", CLAIM, "target_appointment_id", f"{PG}uuid"))),
        ),
        dsl.any_of(
            _same(_t("OLD", CLAIM, "audit_log_id", f"{PG}uuid"), _t("NEW", CLAIM, "audit_log_id", f"{PG}uuid")),
            dsl.all_of(dsl.unary("IS_NULL", _t("OLD", CLAIM, "audit_log_id", f"{PG}uuid")), dsl.unary("IS_NOT_NULL", _t("NEW", CLAIM, "audit_log_id", f"{PG}uuid"))),
        ),
    )
    exact_update_nodes = [
        dsl.assert_node(body_id + ".update.provenance", dsl.xmin_equals_current(_t("OLD", CLAIM, "xmin", f"{PG}xid")), "F_PROVENANCE"),
        dsl.assert_node(body_id + ".update.immutable", immutable, "F_IMMUTABLE"),
        dsl.assert_node(body_id + ".update.monotonic", monotonic, "F_CLAIM_TRANSITION"),
        _return(body_id + ".update.return", "RETURN_NEW"),
    ]
    update = [_if(body_id + ".update.unrelated", update_unrelated, [_return(body_id + ".update.inert", "RETURN_NEW")], [_if(body_id + ".update.exact", update_exact, exact_update_nodes, [_raise(body_id + ".update.adoption", "F_CLAIM_TRANSITION")])])]
    delete = [_if(body_id + ".delete.exact", _claim_exact("OLD"), [_raise(body_id + ".delete.reject", "F_IMMUTABLE")], [_return(body_id + ".delete.inert", "RETURN_OLD")])]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, [], [_context(body_id + ".context", CLAIM, "BEFORE"), _switch(body_id + ".switch", [("UPDATE", update), ("DELETE", delete)])])


def _build_fence_claim() -> dict[str, Any]:
    body_id = FABRIC + "cf_fence_claim_v1"
    symbols = [*_binding_symbols(), *_producer_membership_symbols()]
    def proof(image: str, suffix: str) -> list[dict[str, Any]]:
        practice = _t(image, CLAIM, "practice_id", f"{PG}uuid")
        return [*_binding_nodes(body_id + f".{suffix}.binding", "PRODUCER", practice), *_producer_membership_nodes(body_id + f".{suffix}.proof", practice, command_id=_t(image, CLAIM, "id", f"{PG}uuid")), _return(body_id + f".{suffix}.return", "RETURN_NULL")]
    insert = [_if(body_id + ".insert.exact", _claim_exact("NEW"), proof("NEW", "insert"), [_return(body_id + ".insert.inert", "RETURN_NULL")])]
    both = dsl.all_of(_claim_exact("OLD"), _claim_exact("NEW"))
    neither = dsl.all_of(_not(_claim_exact("OLD")), _not(_claim_exact("NEW")))
    update = [_if(body_id + ".update.neither", neither, [_return(body_id + ".update.inert", "RETURN_NULL")], [_if(body_id + ".update.both", both, proof("NEW", "update"), [_raise(body_id + ".update.adoption", "F_CLAIM_TRANSITION")])])]
    delete = [_if(body_id + ".delete.exact", _claim_exact("OLD"), [_raise(body_id + ".delete.reject", "F_IMMUTABLE")], [_return(body_id + ".delete.inert", "RETURN_NULL")])]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", CLAIM, "AFTER"), _switch(body_id + ".switch", [("INSERT", insert), ("UPDATE", update), ("DELETE", delete)])])


def _build_fence_appointment() -> dict[str, Any]:
    body_id = FABRIC + "cf_fence_appointment_update_v1"
    symbols = [*_binding_symbols(), *_producer_membership_symbols(), dsl.node_symbol("binding_matches", BINDING + "[]"), dsl.node_symbol("final_appointment", APPOINTMENT), dsl.node_symbol("current_events", EVENT + "[]"), dsl.node_symbol("current_aliases", ALIAS + "[]"), dsl.node_symbol("current_outbox", OUTBOX + "[]")]
    practice = _t("NEW", APPOINTMENT, "practice_id", f"{PG}uuid")
    appointment_id = _t("NEW", APPOINTMENT, "id", f"{PG}uuid")
    temporal = dsl.any_of(dsl.is_distinct(_t("OLD", APPOINTMENT, "start_time", f"{PG}timestamptz"), _t("NEW", APPOINTMENT, "start_time", f"{PG}timestamptz")), dsl.is_distinct(_t("OLD", APPOINTMENT, "duration_minutes", f"{PG}integer"), _t("NEW", APPOINTMENT, "duration_minutes", f"{PG}integer")))
    prefix = body_id + ".update"
    common = [
        *_binding_nodes(prefix + ".binding", "PRODUCER", practice),
        dsl.assert_node(prefix + ".identity", dsl.all_of(_same(_t("OLD", APPOINTMENT, "practice_id", f"{PG}uuid"), practice), _same(_t("OLD", APPOINTMENT, "id", f"{PG}uuid"), appointment_id)), "F_IMMUTABLE"),
        dsl.assert_node(prefix + ".second", _not(dsl.xmin_equals_current(_t("OLD", APPOINTMENT, "xmin", f"{PG}xid"))), "F_SECOND_UPDATE"),
        dsl.select_node(prefix + ".final", relation=APPOINTMENT, columns=APPOINTMENT_COLUMNS, predicate=dsl.all_of(dsl.eq(dsl.source_column(APPOINTMENT, "practice_id", f"{PG}uuid"), practice), dsl.eq(dsl.source_column(APPOINTMENT, "id", f"{PG}uuid"), appointment_id)), cardinality="EXACTLY_ONE", output_symbol="final_appointment", order_by=["practice_id", "id"]),
        dsl.assert_node(prefix + ".final-equals", dsl.all_of(*[_same(_r("final_appointment", APPOINTMENT, column, type_name), _t("NEW", APPOINTMENT, column, type_name)) for column, type_name in [("practice_id", f"{PG}uuid"), ("id", f"{PG}uuid"), ("practitioner_id", f"{PG}uuid"), ("location_id", f"{PG}uuid"), ("start_time", f"{PG}timestamptz"), ("duration_minutes", f"{PG}integer")]], dsl.xmin_equals_current(dsl.local_ref("final_appointment", APPOINTMENT))), "F_TEMPORAL_BIJECTION"),
    ]
    positive = [*_producer_membership_nodes(prefix + ".positive", practice, appointment_id=appointment_id), _return(prefix + ".positive.return", "RETURN_NULL")]
    stream = _r("binding", BINDING, "stream_id", f"{PG}uuid")
    absence_reads = [
        dsl.select_node(prefix + ".absence.events", relation=EVENT, columns=["id"], predicate=dsl.all_of(dsl.eq(dsl.source_column(EVENT, "practice_id", f"{PG}uuid"), practice), dsl.eq(dsl.source_column(EVENT, "appointment_id", f"{PG}uuid"), appointment_id), dsl.eq(dsl.source_column(EVENT, "event_type", f"{PG}text"), dsl.const(f"{PG}text", EVENT_TYPE)), dsl.eq(dsl.source_column(EVENT, "schema_version", f"{PG}text"), dsl.const(f"{PG}text", EVENT_SCHEMA)), dsl.xmin_equals_current(dsl.source_column(EVENT, "xmin", f"{PG}xid"))), cardinality="COMPLETE_SET", output_symbol="current_events", order_by=["id"], set_read=True),
        dsl.select_node(prefix + ".absence.aliases", relation=ALIAS, columns=["opaque_aggregate_alias"], predicate=dsl.all_of(dsl.eq(dsl.source_column(ALIAS, "practice_id", f"{PG}uuid"), practice), dsl.eq(dsl.source_column(ALIAS, "stream_id", f"{PG}uuid"), stream), dsl.eq(dsl.source_column(ALIAS, "product_appointment_uuid", f"{PG}uuid"), appointment_id)), cardinality="COMPLETE_SET", output_symbol="current_aliases", order_by=["opaque_aggregate_alias"], set_read=True),
        dsl.select_node(prefix + ".absence.outbox", relation=OUTBOX, columns=["transaction_position"], predicate=dsl.all_of(dsl.eq(dsl.source_column(OUTBOX, "practice_id", f"{PG}uuid"), practice), dsl.eq(dsl.source_column(OUTBOX, "stream_id", f"{PG}uuid"), stream)), cardinality="COMPLETE_SET", output_symbol="current_outbox", order_by=["transaction_position"], set_read=True),
        dsl.assert_node(prefix + ".absence.assert", dsl.all_of(*[dsl.eq({"op": "COUNT", "operand": dsl.local_ref(symbol, relation + "[]"), "type": f"{PG}bigint"}, dsl.const(f"{PG}bigint", 0)) for symbol, relation in [("current_events", EVENT), ("current_aliases", ALIAS), ("current_outbox", OUTBOX)]]), "F_TEMPORAL_BIJECTION"),
        _return(prefix + ".absence.return", "RETURN_NULL"),
    ]
    common.append(_if(prefix + ".temporal", temporal, positive, absence_reads))
    update = [
        dsl.select_node(
            prefix + ".binding-census",
            relation=BINDING,
            columns=dsl.BINDING_COLUMNS,
            predicate=_binding_predicate("PRODUCER", practice),
            cardinality="COMPLETE_SET",
            output_symbol="binding_matches",
            order_by=["database_login", "logical_capability", "practice_id"],
            set_read=True,
        ),
        _if(
            prefix + ".credential",
            _one("binding_matches", BINDING),
            common,
            [_return(prefix + ".other-credential", "RETURN_NULL")],
        ),
    ]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", APPOINTMENT, "AFTER"), _switch(body_id + ".switch", [("UPDATE", update)])])


def _build_guard_audit() -> dict[str, Any]:
    body_id = FABRIC + "cf_guard_audit_v1"
    symbols = [
        dsl.node_symbol("old_command_matches", CLAIM + "[]"),
        dsl.node_symbol("new_command_matches", CLAIM + "[]"),
    ]
    update = [
        *_audit_command_nodes(
            body_id + ".update.old-command", "OLD", "old_command_matches"
        ),
        *_audit_command_nodes(
            body_id + ".update.new-command", "NEW", "new_command_matches"
        ),
        _if(
            body_id + ".update.any-exact",
            dsl.any_of(
                _one("old_command_matches", CLAIM),
                _one("new_command_matches", CLAIM),
            ),
            [_raise(body_id + ".update.reject", "F_IMMUTABLE")],
            [_return(body_id + ".update.inert", "RETURN_NEW")],
        ),
    ]
    delete = [
        *_audit_command_nodes(
            body_id + ".delete.old-command", "OLD", "old_command_matches"
        ),
        _if(
            body_id + ".delete.exact",
            _one("old_command_matches", CLAIM),
            [_raise(body_id + ".delete.reject", "F_IMMUTABLE")],
            [_return(body_id + ".delete.inert", "RETURN_OLD")],
        ),
    ]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", AUDIT, "BEFORE"), _switch(body_id + ".switch", [("UPDATE", update), ("DELETE", delete)])])


def _build_fence_audit() -> dict[str, Any]:
    body_id = FABRIC + "cf_fence_audit_v1"
    symbols = [
        *_binding_symbols(),
        *_producer_membership_symbols(),
        dsl.node_symbol("old_command_matches", CLAIM + "[]"),
        dsl.node_symbol("new_command_matches", CLAIM + "[]"),
    ]
    practice = _t("NEW", AUDIT, "practice_id", f"{PG}uuid")
    proof = [*_binding_nodes(body_id + ".insert.binding", "PRODUCER", practice), *_producer_membership_nodes(body_id + ".insert.proof", practice, command_id=_t("NEW", AUDIT, "command_id", f"{PG}uuid")), _return(body_id + ".insert.return", "RETURN_NULL")]
    insert = [
        *_audit_command_nodes(
            body_id + ".insert.new-command", "NEW", "new_command_matches"
        ),
        _if(body_id + ".insert.exact", _one("new_command_matches", CLAIM), proof, [_return(body_id + ".insert.inert", "RETURN_NULL")]),
    ]
    update = [
        *_audit_command_nodes(
            body_id + ".update.old-command", "OLD", "old_command_matches"
        ),
        *_audit_command_nodes(
            body_id + ".update.new-command", "NEW", "new_command_matches"
        ),
        _if(body_id + ".update.exact", dsl.any_of(_one("old_command_matches", CLAIM), _one("new_command_matches", CLAIM)), [_raise(body_id + ".update.reject", "F_IMMUTABLE")], [_return(body_id + ".update.inert", "RETURN_NULL")]),
    ]
    delete = [
        *_audit_command_nodes(
            body_id + ".delete.old-command", "OLD", "old_command_matches"
        ),
        _if(body_id + ".delete.exact", _one("old_command_matches", CLAIM), [_raise(body_id + ".delete.reject", "F_IMMUTABLE")], [_return(body_id + ".delete.inert", "RETURN_NULL")]),
    ]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", AUDIT, "AFTER"), _switch(body_id + ".switch", [("INSERT", insert), ("UPDATE", update), ("DELETE", delete)])])


def _build_guard_event() -> dict[str, Any]:
    body_id = FABRIC + "cf_guard_event_v1"
    update = [_if(body_id + ".update.exact", dsl.any_of(_event_exact("OLD"), _event_exact("NEW")), [_raise(body_id + ".update.reject", "F_IMMUTABLE")], [_return(body_id + ".update.inert", "RETURN_NEW")])]
    delete = [_if(body_id + ".delete.exact", _event_exact("OLD"), [_if(body_id + ".delete.current", dsl.xmin_equals_current(_t("OLD", EVENT, "xmin", f"{PG}xid")), [_raise(body_id + ".delete.reject-current", "F_IMMUTABLE")], [_return(body_id + ".delete.older", "RETURN_OLD")])], [_return(body_id + ".delete.inert", "RETURN_OLD")])]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, [], [_context(body_id + ".context", EVENT, "BEFORE"), _switch(body_id + ".switch", [("UPDATE", update), ("DELETE", delete)])])


def _build_fence_event() -> dict[str, Any]:
    body_id = FABRIC + "cf_fence_event_v1"
    symbols = [*_binding_symbols(), *_producer_membership_symbols()]
    practice = _t("NEW", EVENT, "practice_id", f"{PG}uuid")
    proof = [*_binding_nodes(body_id + ".insert.binding", "PRODUCER", practice), *_producer_membership_nodes(body_id + ".insert.proof", practice, command_id=_t("NEW", EVENT, "command_id", f"{PG}uuid")), _return(body_id + ".insert.return", "RETURN_NULL")]
    insert = [_if(body_id + ".insert.exact", _event_exact("NEW"), proof, [_return(body_id + ".insert.inert", "RETURN_NULL")])]
    update = [_if(body_id + ".update.exact", dsl.any_of(_event_exact("OLD"), _event_exact("NEW")), [_raise(body_id + ".update.reject", "F_IMMUTABLE")], [_return(body_id + ".update.inert", "RETURN_NULL")])]
    delete = [_if(body_id + ".delete.exact", _event_exact("OLD"), [_if(body_id + ".delete.current", dsl.xmin_equals_current(_t("OLD", EVENT, "xmin", f"{PG}xid")), [_raise(body_id + ".delete.reject-current", "F_IMMUTABLE")], [_return(body_id + ".delete.older", "RETURN_NULL")])], [_return(body_id + ".delete.inert", "RETURN_NULL")])]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", EVENT, "AFTER"), _switch(body_id + ".switch", [("INSERT", insert), ("UPDATE", update), ("DELETE", delete)])])


def _build_guard_alias() -> dict[str, Any]:
    body_id = FABRIC + "cf_guard_alias_v1"
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, [], [_context(body_id + ".context", ALIAS, "BEFORE"), _switch(body_id + ".switch", [("UPDATE", [_raise(body_id + ".update", "F_IMMUTABLE")]), ("DELETE", [_raise(body_id + ".delete", "F_IMMUTABLE")])])])


def _build_fence_alias() -> dict[str, Any]:
    body_id = FABRIC + "cf_fence_alias_v1"
    symbols = [*_binding_symbols(), dsl.node_symbol("final_alias", ALIAS), dsl.node_symbol("alias_outbox", OUTBOX)]
    practice = _t("NEW", ALIAS, "practice_id", f"{PG}uuid")
    stream = _t("NEW", ALIAS, "stream_id", f"{PG}uuid")
    insert = [
        dsl.assert_node(body_id + ".insert.source", dsl.eq(_t("NEW", ALIAS, "source_contract_id", f"{FABRIC}source_contract_code"), dsl.const(f"{FABRIC}source_contract_code", SOURCE_CONTRACT)), "F_MEMBERSHIP"),
        *_binding_nodes(body_id + ".insert.binding", "PRODUCER", practice, stream),
        dsl.select_node(body_id + ".insert.reload", relation=ALIAS, columns=ALIAS_COLUMNS, predicate=dsl.all_of(*[dsl.eq(dsl.source_column(ALIAS, column, type_name), _t("NEW", ALIAS, column, type_name)) for column, type_name in [("practice_id", f"{PG}uuid"), ("source_contract_id", f"{FABRIC}source_contract_code"), ("stream_id", f"{PG}uuid"), ("product_appointment_uuid", f"{PG}uuid")]]), cardinality="EXACTLY_ONE", output_symbol="final_alias", order_by=["practice_id", "source_contract_id", "stream_id", "product_appointment_uuid"]),
        dsl.select_node(body_id + ".insert.outbox", relation=OUTBOX, columns=OUTBOX_COLUMNS, predicate=dsl.all_of(dsl.eq(dsl.source_column(OUTBOX, "practice_id", f"{PG}uuid"), practice), dsl.eq(dsl.source_column(OUTBOX, "stream_id", f"{PG}uuid"), stream), dsl.eq(dsl.source_column(OUTBOX, "opaque_aggregate_alias", f"{PG}uuid"), _t("NEW", ALIAS, "opaque_aggregate_alias", f"{PG}uuid"))), cardinality="EXACTLY_ONE", output_symbol="alias_outbox", order_by=["practice_id", "source_contract_id", "stream_id", "stream_epoch", "transaction_position"]),
        dsl.assert_node(body_id + ".insert.proof", dsl.all_of(dsl.xmin_equals_current(dsl.local_ref("final_alias", ALIAS)), dsl.xmin_equals_current(dsl.local_ref("alias_outbox", OUTBOX))), "F_TEMPORAL_BIJECTION"),
        _return(body_id + ".insert.return", "RETURN_NULL"),
    ]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", ALIAS, "AFTER"), _switch(body_id + ".switch", [("INSERT", insert), ("UPDATE", [_raise(body_id + ".update", "F_IMMUTABLE")]), ("DELETE", [_raise(body_id + ".delete", "F_IMMUTABLE")])])])


def _build_guard_head() -> dict[str, Any]:
    body_id = FABRIC + "cf_guard_stream_head_v1"
    symbols = _binding_symbols()
    practice = _t("NEW", HEAD, "practice_id", f"{PG}uuid")
    stream = _t("NEW", HEAD, "stream_id", f"{PG}uuid")
    update = [
        *_binding_nodes(body_id + ".update.binding", "PRODUCER", practice, stream),
        dsl.assert_node(
            body_id + ".update.proof",
            dsl.all_of(
                *[
                    _same(
                        _t("OLD", HEAD, column, type_name),
                        _t("NEW", HEAD, column, type_name),
                    )
                    for column, type_name in [
                        ("practice_id", f"{PG}uuid"),
                        ("source_contract_id", f"{FABRIC}source_contract_code"),
                        ("stream_id", f"{PG}uuid"),
                        ("stream_epoch", f"{PG}bigint"),
                    ]
                ],
                dsl.eq(
                    _t("NEW", HEAD, "stream_epoch", f"{PG}bigint"),
                    dsl.const(f"{PG}bigint", 1),
                ),
                dsl.eq(
                    _t("NEW", HEAD, "last_position", f"{PG}bigint"),
                    dsl.add(
                        _t("OLD", HEAD, "last_position", f"{PG}bigint"),
                        dsl.const(f"{PG}bigint", 1),
                        f"{PG}bigint",
                    ),
                ),
                dsl.eq(
                    _t("NEW", HEAD, "updated_at", f"{PG}timestamptz"),
                    dsl.transaction_timestamp(),
                ),
            ),
            "F_STREAM",
        ),
        _return(body_id + ".update.return", "RETURN_NEW"),
    ]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", HEAD, "BEFORE"), _switch(body_id + ".switch", [("UPDATE", update), ("DELETE", [_raise(body_id + ".delete", "F_IMMUTABLE")])])])


def _build_fence_head() -> dict[str, Any]:
    body_id = FABRIC + "cf_fence_stream_head_v1"
    symbols = [*_binding_symbols(), dsl.node_symbol("final_head", HEAD), dsl.node_symbol("head_outbox", OUTBOX), dsl.node_symbol("head_event", EVENT)]
    def reload(image: str, suffix: str, capability: str) -> list[dict[str, Any]]:
        practice = _t(image, HEAD, "practice_id", f"{PG}uuid")
        stream = _t(image, HEAD, "stream_id", f"{PG}uuid")
        return [*_binding_nodes(body_id + f".{suffix}.binding", capability, practice, stream), dsl.select_node(body_id + f".{suffix}.reload", relation=HEAD, columns=HEAD_COLUMNS, predicate=dsl.all_of(dsl.eq(dsl.source_column(HEAD, "practice_id", f"{PG}uuid"), practice), dsl.eq(dsl.source_column(HEAD, "source_contract_id", f"{FABRIC}source_contract_code"), _t(image, HEAD, "source_contract_id", f"{FABRIC}source_contract_code")), dsl.eq(dsl.source_column(HEAD, "stream_id", f"{PG}uuid"), stream)), cardinality="EXACTLY_ONE", output_symbol="final_head", order_by=["practice_id", "source_contract_id", "stream_id"])]
    insert = [*reload("NEW", "insert", "LIFECYCLE"), dsl.assert_node(body_id + ".insert.baseline", dsl.all_of(dsl.eq(_r("final_head", HEAD, "last_position", f"{PG}bigint"), dsl.const(f"{PG}bigint", 0)), dsl.eq(_r("final_head", HEAD, "stream_epoch", f"{PG}bigint"), dsl.const(f"{PG}bigint", 1)), dsl.xmin_equals_current(dsl.local_ref("final_head", HEAD))), "F_STREAM"), _return(body_id + ".insert.return", "RETURN_NULL")]
    update = [*reload("NEW", "update", "PRODUCER"), dsl.select_node(body_id + ".update.outbox", relation=OUTBOX, columns=OUTBOX_COLUMNS, predicate=dsl.all_of(dsl.eq(dsl.source_column(OUTBOX, "practice_id", f"{PG}uuid"), _t("NEW", HEAD, "practice_id", f"{PG}uuid")), dsl.eq(dsl.source_column(OUTBOX, "stream_id", f"{PG}uuid"), _t("NEW", HEAD, "stream_id", f"{PG}uuid")), dsl.eq(dsl.source_column(OUTBOX, "predecessor_position", f"{PG}bigint"), _t("OLD", HEAD, "last_position", f"{PG}bigint")), dsl.eq(dsl.source_column(OUTBOX, "transaction_position", f"{PG}bigint"), _t("NEW", HEAD, "last_position", f"{PG}bigint"))), cardinality="EXACTLY_ONE", output_symbol="head_outbox", order_by=["practice_id", "source_contract_id", "stream_id", "stream_epoch", "transaction_position"]), dsl.select_node(body_id + ".update.event", relation=EVENT, columns=EVENT_COLUMNS, predicate=dsl.all_of(dsl.eq(dsl.source_column(EVENT, "practice_id", f"{PG}uuid"), _t("NEW", HEAD, "practice_id", f"{PG}uuid")), dsl.eq(dsl.source_column(EVENT, "id", f"{PG}uuid"), _r("head_outbox", OUTBOX, "raw_event_uuid", f"{PG}uuid"))), cardinality="EXACTLY_ONE", output_symbol="head_event", order_by=["practice_id", "id"]), dsl.assert_node(body_id + ".update.proof", dsl.all_of(dsl.xmin_equals_current(dsl.local_ref("final_head", HEAD)), dsl.xmin_equals_current(dsl.local_ref("head_outbox", OUTBOX)), dsl.xmin_equals_current(dsl.local_ref("head_event", EVENT)), dsl.eq(_r("head_event", EVENT, "event_type", f"{PG}text"), dsl.const(f"{PG}text", EVENT_TYPE)), dsl.eq(_r("head_event", EVENT, "schema_version", f"{PG}text"), dsl.const(f"{PG}text", EVENT_SCHEMA))), "F_TEMPORAL_BIJECTION"), _return(body_id + ".update.return", "RETURN_NULL")]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", HEAD, "AFTER"), _switch(body_id + ".switch", [("INSERT", insert), ("UPDATE", update), ("DELETE", [_raise(body_id + ".delete", "F_IMMUTABLE")])])])


def _retention_nodes(
    prefix: str, image: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    practice = _t(image, OUTBOX, "practice_id", f"{PG}uuid")
    stream = _t(image, OUTBOX, "stream_id", f"{PG}uuid")
    enabled_policy = dsl.all_of(
        dsl.eq(dsl.source_column(POLICY, "practice_id", f"{PG}uuid"), practice),
        dsl.eq(dsl.source_column(POLICY, "source_contract_id", f"{FABRIC}source_contract_code"), _t(image, OUTBOX, "source_contract_id", f"{FABRIC}source_contract_code")),
        dsl.eq(dsl.source_column(POLICY, "stream_id", f"{PG}uuid"), stream),
        dsl.eq(dsl.source_column(POLICY, "retention_execution_enabled", f"{PG}boolean"), dsl.const(f"{PG}boolean", True)),
        dsl.binary("LTE", dsl.source_column(POLICY, "effective_at", f"{PG}timestamptz"), dsl.transaction_timestamp()),
    )
    nodes = [
        dsl.select_node(
            prefix + ".bindings",
            relation=BINDING,
            columns=dsl.BINDING_COLUMNS,
            predicate=_binding_predicate("RETENTION", practice, stream),
            cardinality="COMPLETE_SET",
            output_symbol="retention_bindings",
            order_by=["database_login", "logical_capability", "practice_id"],
            set_read=True,
        ),
        dsl.select_node(
            prefix + ".policies",
            relation=POLICY,
            columns=[
                "practice_id",
                "source_contract_id",
                "stream_id",
                "policy_revision",
                "retention_execution_enabled",
                "effective_at",
            ],
            predicate=enabled_policy,
            cardinality="COMPLETE_SET",
            output_symbol="enabled_policies",
            order_by=[
                "practice_id",
                "source_contract_id",
                "stream_id",
                "policy_revision",
            ],
            set_read=True,
        ),
    ]
    authorized = dsl.all_of(
        _not(dsl.xmin_equals_current(_t(image, OUTBOX, "xmin", f"{PG}xid"))),
        _one("retention_bindings", BINDING),
        _one("enabled_policies", POLICY),
    )
    return nodes, authorized


def _build_guard_outbox() -> dict[str, Any]:
    body_id = FABRIC + "cf_guard_outbox_v1"
    retention_nodes, authorized = _retention_nodes(body_id + ".delete", "OLD")
    symbols = [
        dsl.node_symbol("retention_bindings", BINDING + "[]"),
        dsl.node_symbol("enabled_policies", POLICY + "[]"),
    ]
    delete = [
        *retention_nodes,
        _if(body_id + ".delete.authorized", authorized, [_return(body_id + ".delete.return", "RETURN_OLD")], [_raise(body_id + ".delete.reject", "F_RETENTION_DELETE")]),
    ]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", OUTBOX, "BEFORE"), _switch(body_id + ".switch", [("UPDATE", [_raise(body_id + ".update", "F_IMMUTABLE")]), ("DELETE", delete)])])


def _build_fence_outbox() -> dict[str, Any]:
    body_id = FABRIC + "cf_fence_outbox_v1"
    symbols = [
        *_binding_symbols(),
        *_producer_membership_symbols(),
        dsl.node_symbol("retention_bindings", BINDING + "[]"),
        dsl.node_symbol("enabled_policies", POLICY + "[]"),
    ]
    practice = _t("NEW", OUTBOX, "practice_id", f"{PG}uuid")
    # The command anchor is recovered through the exact event selected by raw_event_uuid.
    symbols.extend([dsl.node_symbol("seed_event", EVENT)])
    insert = [
        *_binding_nodes(body_id + ".insert.binding", "PRODUCER", practice, _t("NEW", OUTBOX, "stream_id", f"{PG}uuid")),
        dsl.select_node(body_id + ".insert.seed-event", relation=EVENT, columns=EVENT_COLUMNS, predicate=dsl.all_of(dsl.eq(dsl.source_column(EVENT, "practice_id", f"{PG}uuid"), practice), dsl.eq(dsl.source_column(EVENT, "id", f"{PG}uuid"), _t("NEW", OUTBOX, "raw_event_uuid", f"{PG}uuid"))), cardinality="EXACTLY_ONE", output_symbol="seed_event", order_by=["practice_id", "id"]),
        *_producer_membership_nodes(body_id + ".insert.proof", practice, command_id=_r("seed_event", EVENT, "command_id", f"{PG}uuid")),
        dsl.assert_node(body_id + ".insert.image", dsl.all_of(*[_same(_r("outbox", OUTBOX, column, type_name), _t("NEW", OUTBOX, column, type_name)) for column, type_name in [("practice_id", f"{PG}uuid"), ("source_contract_id", f"{FABRIC}source_contract_code"), ("stream_id", f"{PG}uuid"), ("stream_epoch", f"{PG}bigint"), ("transaction_position", f"{PG}bigint"), ("predecessor_position", f"{PG}bigint"), ("raw_event_uuid", f"{PG}uuid"), ("opaque_aggregate_alias", f"{PG}uuid"), ("aggregate_revision", f"{PG}bigint"), ("source_contract_digest", f"{FABRIC}digest_sha256"), ("transaction_authored_at", f"{PG}timestamptz")]]), "F_TEMPORAL_BIJECTION"),
        _return(body_id + ".insert.return", "RETURN_NULL"),
    ]
    retention_nodes, authorized = _retention_nodes(body_id + ".delete", "OLD")
    delete = [
        *retention_nodes,
        _if(body_id + ".delete.authorized", authorized, [_return(body_id + ".delete.return", "RETURN_NULL")], [_raise(body_id + ".delete.reject", "F_RETENTION_DELETE")]),
    ]
    return dsl.body(body_id, "TRIGGER_FUNCTION", body_id, symbols, [_context(body_id + ".context", OUTBOX, "AFTER"), _switch(body_id + ".switch", [("INSERT", insert), ("UPDATE", [_raise(body_id + ".update", "F_IMMUTABLE")]), ("DELETE", delete)])])


def build_trigger_programs() -> list[dict[str, Any]]:
    """Return all thirteen trigger programs in the frozen declaration order."""
    programs = [
        _build_guard_claim(),
        _build_fence_claim(),
        _build_fence_appointment(),
        _build_guard_audit(),
        _build_fence_audit(),
        _build_guard_event(),
        _build_fence_event(),
        _build_guard_alias(),
        _build_fence_alias(),
        _build_guard_head(),
        _build_fence_head(),
        _build_guard_outbox(),
        _build_fence_outbox(),
    ]
    expected = [FABRIC + name for name in dsl.TRIGGER_FUNCTION_NAMES]
    actual = [program["id"] for program in programs]
    if actual != expected:
        raise ValueError("trigger program order or population drift")
    return programs


__all__ = ["build_trigger_programs"]
