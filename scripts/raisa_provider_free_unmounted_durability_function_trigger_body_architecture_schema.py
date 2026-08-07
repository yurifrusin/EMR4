"""Build the structural JSON Schema for the durability typed body contract.

The schema is intentionally structural.  It position-closes frozen populations
and exposes reusable typed node/expression branches, but it does not turn body
programs, operands, effects, or derived summaries into whole-object constants.
Semantic equality remains the responsibility of the offline validator.
"""

from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator import (
    EXACT_ENTRY_POINTS,
    EXACT_ENUM_VALUES,
    EXACT_SUPPORT_FUNCTION,
    EXACT_TRIGGER_FUNCTIONS,
    assert_normative_envelope,
)


_QUALIFIED = r"^(?:pg_catalog|public|emr4_context_fabric)\.[a-z][a-z0-9_]*(?:\[\])?$"
_IDENTIFIER = r"^[A-Za-z_][A-Za-z0-9_.:-]*$"
_TG_OPS = ["INSERT", "UPDATE", "DELETE"]
_CARDINALITIES = ["EXACTLY_ONE", "ZERO_OR_ONE", "COMPLETE_SET"]
_LOCK_MODES = ["FOR_UPDATE", "FOR_NO_KEY_UPDATE", "FOR_SHARE", "FOR_KEY_SHARE"]


def _closed_object(
    properties: Mapping[str, Any],
    *,
    required: Sequence[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": dict(properties),
        "required": list(required if required is not None else properties),
        "additionalProperties": False,
    }


def _string(*, pattern: str | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "string", "minLength": 1}
    if pattern is not None:
        schema["pattern"] = pattern
    return schema


def _array(
    items: Mapping[str, Any],
    *,
    min_items: int = 0,
    unique: bool = False,
) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "array",
        "items": dict(items),
        "minItems": min_items,
    }
    if unique:
        schema["uniqueItems"] = True
    return schema


def _ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/$defs/{name}"}


def _position_array(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "array",
        "minItems": len(items),
        "maxItems": len(items),
        "items": False,
    }
    if items:
        schema["prefixItems"] = [dict(item) for item in items]
    return schema


def _overlay_id(base: Mapping[str, Any], **constants: str) -> dict[str, Any]:
    return {
        "allOf": [
            dict(base),
            {
                "type": "object",
                "properties": {
                    key: {"const": value} for key, value in constants.items()
                },
                "required": list(constants),
            },
        ]
    }


def _json_value_def() -> dict[str, Any]:
    return {
        "oneOf": [
            {"type": "null"},
            {"type": "boolean"},
            {"type": "integer"},
            {"type": "number", "not": {"type": "integer"}},
            {"type": "string"},
            _array(_ref("json_value")),
            {
                "type": "object",
                "additionalProperties": _ref("json_value"),
            },
        ]
    }


def _structural_shape(value: Any) -> dict[str, Any]:
    """Infer closed object shape without freezing scalar values."""

    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, Mapping):
        return _closed_object(
            {str(key): _structural_shape(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        if not value:
            return _array(_ref("json_value"))
        unique_shapes: dict[str, dict[str, Any]] = {}
        for item in value:
            shape = _structural_shape(item)
            unique_shapes.setdefault(
                json.dumps(shape, sort_keys=True, separators=(",", ":")), shape
            )
        schemas = list(unique_shapes.values())
        item_schema = schemas[0] if len(schemas) == 1 else {"oneOf": schemas}
        return _array(item_schema)
    raise TypeError(f"unsupported JSON value {type(value)!r}")


def _normative_shape(value: Any) -> dict[str, Any]:
    """Freeze scalar meaning and ordered populations without complex consts."""

    if isinstance(value, Mapping):
        return _closed_object(
            {str(key): _normative_shape(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return _position_array([_normative_shape(item) for item in value])
    return {"const": value}


def _expression_defs() -> dict[str, Any]:
    type_name = _string(pattern=_QUALIFIED)
    symbol = _string(pattern=_IDENTIFIER)
    relation = _string(pattern=_QUALIFIED)
    column = _string(pattern=r"^[a-z][a-z0-9_]*$")

    local_set_reference = _closed_object(
        {
            "kind": {"const": "LOCAL"},
            "symbol": symbol,
            "type": type_name,
        }
    )

    ref_branches = [
        _closed_object(
            {
                "op": {"const": "REF"},
                "kind": {"const": kind},
                "symbol": symbol,
                "type": type_name,
            }
        )
        for kind in ("INPUT", "LOCAL", "ITERATOR")
    ]
    ref_branches.extend(
        [
            _closed_object(
                {
                    "op": {"const": "REF"},
                    "kind": {"const": "ROW_COLUMN"},
                    "symbol": symbol,
                    "relation": relation,
                    "column": column,
                    "type": type_name,
                }
            ),
            _closed_object(
                {
                    "op": {"const": "REF"},
                    "kind": {"const": "SOURCE_COLUMN"},
                    "relation": relation,
                    "column": column,
                    "type": type_name,
                }
            ),
            _closed_object(
                {
                    "op": {"const": "REF"},
                    "kind": {"const": "TRIGGER_COLUMN"},
                    "image": {"enum": ["OLD", "NEW"]},
                    "relation": relation,
                    "column": column,
                    "type": type_name,
                }
            ),
            _closed_object(
                {
                    "op": {"const": "REF"},
                    "kind": {"const": "SYSTEM"},
                    "field": {
                        "enum": [
                            "TG_OP",
                            "TG_TABLE_SCHEMA",
                            "TG_TABLE_NAME",
                            "TG_WHEN",
                            "TG_LEVEL",
                            "SESSION_USER",
                        ]
                    },
                    "type": type_name,
                }
            ),
        ]
    )

    enum_types = sorted(EXACT_ENUM_VALUES)
    enum_array_types = [f"{enum_type}[]" for enum_type in enum_types]
    non_enum_type = {
        "allOf": [
            type_name,
            {"not": {"enum": [*enum_types, *enum_array_types]}},
        ]
    }
    const_branches = [
        _closed_object(
            {
                "op": {"const": "CONST"},
                "type": {"const": enum_type},
                "value": {
                    "anyOf": [
                        {"type": "null"},
                        {"enum": list(values)},
                    ]
                },
            }
        )
        for enum_type, values in sorted(EXACT_ENUM_VALUES.items())
    ]
    const_branches.append(
        _closed_object(
            {
                "op": {"const": "CONST"},
                "type": non_enum_type,
                "value": _ref("json_value"),
            }
        )
    )
    array_const_branches = [
        _closed_object(
            {
                "op": {"const": "ARRAY_CONST"},
                "type": {"const": f"{enum_type}[]"},
                "values": _array({"enum": list(values)}),
            }
        )
        for enum_type, values in sorted(EXACT_ENUM_VALUES.items())
    ]
    array_const_branches.append(
        _closed_object(
            {
                "op": {"const": "ARRAY_CONST"},
                "type": non_enum_type,
                "values": _array(_ref("json_value")),
            }
        )
    )

    expression_branches: list[dict[str, Any]] = [
        {"oneOf": ref_branches},
        {"oneOf": const_branches},
        {"oneOf": array_const_branches},
        _closed_object(
            {
                "op": {"const": "FIELD"},
                "source": _ref("expression"),
                "field": column,
                "type": type_name,
            }
        ),
        _closed_object(
            {
                "op": {"const": "MIN_FIELD"},
                "source": _ref("expression"),
                "field": column,
                "type": type_name,
            }
        ),
        _closed_object(
            {
                "op": {"const": "COMPOSITE_CONSTRUCT"},
                "type": type_name,
                "fields": _array(_ref("composite_field_binding"), min_items=1),
            }
        ),
    ]
    for op in (
        "SESSION_USER",
        "TRANSACTION_TIMESTAMP",
        "CURRENT_XID32",
        "GEN_RANDOM_UUID",
    ):
        expression_branches.append(
            _closed_object({"op": {"const": op}, "type": type_name})
        )
    expression_branches.append(
        _closed_object(
            {
                "op": {"const": "SYSTEM_XMIN"},
                "row": _ref("expression"),
                "type": type_name,
            }
        )
    )
    for op in ("NOT", "IS_NULL", "IS_NOT_NULL", "COUNT"):
        expression_branches.append(
            _closed_object(
                {
                    "op": {"const": op},
                    "operand": _ref("expression"),
                    "type": type_name,
                }
            )
        )
    for op in (
        "EQ",
        "NE",
        "LT",
        "LTE",
        "GT",
        "GTE",
        "IS_DISTINCT_FROM",
        "ADD",
        "SUBTRACT",
        "TIMESTAMP_ADD_MINUTES",
        "TIMESTAMP_ADD_SECONDS",
    ):
        expression_branches.append(
            _closed_object(
                {
                    "op": {"const": op},
                    "left": _ref("expression"),
                    "right": _ref("expression"),
                    "type": type_name,
                }
            )
        )
    for op in ("AND", "OR"):
        expression_branches.append(
            _closed_object(
                {
                    "op": {"const": op},
                    "operands": _array(_ref("expression"), min_items=2),
                    "type": type_name,
                }
            )
        )
    expression_branches.extend(
        [
            _closed_object(
                {
                    "op": {"const": "JSON_GET_CAST"},
                    "source": _ref("expression"),
                    "key": column,
                    "target_type": type_name,
                    "type": type_name,
                }
            ),
            _closed_object(
                {
                    "op": {"const": "JSON_KEYS_EXACT"},
                    "source": _ref("expression"),
                    "keys": _array(column, min_items=1, unique=True),
                    "type": {"const": "pg_catalog.boolean"},
                }
            ),
            _closed_object(
                {
                    "op": {"const": "SET_CONTAINS_KEY"},
                    "set": local_set_reference,
                    "source_relation": relation,
                    "key_pairs": _array(
                        _closed_object(
                            {
                                "source_column": column,
                                "set_column": column,
                            }
                        ),
                        min_items=1,
                    ),
                    "type": {"const": "pg_catalog.boolean"},
                }
            ),
            _closed_object(
                {
                    "op": {"const": "SET_COVERS_KEYS"},
                    "required": local_set_reference,
                    "evidence": local_set_reference,
                    "key_pairs": _array(
                        _closed_object(
                            {
                                "required_column": column,
                                "evidence_column": column,
                            }
                        ),
                        min_items=1,
                    ),
                    "type": {"const": "pg_catalog.boolean"},
                }
            ),
            _closed_object(
                {
                    "op": {"const": "CANONICAL_DIGEST"},
                    "profile": _string(pattern=_QUALIFIED),
                    "operands": _array(_ref("expression"), min_items=1),
                    "type": type_name,
                }
            ),
            _closed_object(
                {
                    "op": {"const": "CASE"},
                    "arms": _array(_ref("case_arm"), min_items=1),
                    "else": _ref("expression"),
                    "type": type_name,
                }
            ),
        ]
    )
    return {
        "expression": {"oneOf": expression_branches},
        "case_arm": _closed_object(
            {"when": _ref("expression"), "then": _ref("expression")}
        ),
        "composite_field_binding": _closed_object(
            {"field": column, "value": _ref("expression")}
        ),
    }


def _node_defs() -> dict[str, Any]:
    relation = _string(pattern=_QUALIFIED)
    identifier = _string(pattern=_IDENTIFIER)
    columns = _array(_string(pattern=r"^[a-z][a-z0-9_]*$"), min_items=1, unique=True)
    order_by = _array(_ref("order_item"), min_items=1)
    expression = _ref("expression")
    node_array = _array(_ref("instruction_node"))

    def node(op: str, operands: Mapping[str, Any]) -> dict[str, Any]:
        return _closed_object(
            {
                "node_id": identifier,
                "op": {"const": op},
                "operands": _closed_object(operands),
            }
        )

    branches: list[dict[str, Any]] = [
        node(
            "ASSERT_ISOLATION",
            {"required": {"enum": ["READ_COMMITTED", "SERIALIZABLE"]}},
        ),
        node(
            "DERIVE_BINDING",
            {
                "support_function": {"const": EXACT_SUPPORT_FUNCTION},
                "capability": _string(pattern=_QUALIFIED),
                "arguments": _array(expression),
                "relation": relation,
                "columns": columns,
                "predicate": expression,
                "output_symbol": identifier,
                "cardinality": {"const": "EXACTLY_ONE"},
            },
        ),
    ]
    for op, cardinality in (
        ("SELECT_EXACT", "EXACTLY_ONE"),
        ("SELECT_SET", "COMPLETE_SET"),
    ):
        branches.append(
            node(
                op,
                {
                    "relation": relation,
                    "columns": columns,
                    "predicate": expression,
                    "output_symbol": identifier,
                    "cardinality": {"const": cardinality},
                    "order_by": order_by,
                },
            )
        )
    branches.extend(
        [
            _closed_object(
                {
                    "node_id": identifier,
                    "op": {"const": "LOCK_EXACT"},
                    "operands": _closed_object(
                        {
                            "relation": relation,
                            "key_columns": columns,
                            "predicate": expression,
                            "mode": {"enum": _LOCK_MODES},
                            "ordinal": {"type": "integer", "minimum": 1},
                            "output_symbol": identifier,
                            "columns": columns,
                        },
                        required=[
                            "relation",
                            "key_columns",
                            "predicate",
                            "mode",
                            "ordinal",
                        ],
                    ),
                }
            ),
            node("LET", {"output_symbol": identifier, "expression": expression}),
            node("ASSERT", {"predicate": expression, "failure_id": identifier}),
            node(
                "IF",
                {
                    "condition": expression,
                    "then": node_array,
                    "else": node_array,
                    "convergence": {"enum": ["REJOIN", "ALL_TERMINAL"]},
                },
            ),
            node(
                "SWITCH_TG_OP",
                {
                    "arms": _array(_ref("trigger_arm"), min_items=1),
                    "default": node_array,
                    "convergence": {"enum": ["REJOIN", "ALL_TERMINAL"]},
                },
            ),
            node(
                "FOR_EACH",
                {
                    "set_symbol": identifier,
                    "row_symbol": identifier,
                    "nodes": node_array,
                    "complete_set": {"const": True},
                    "order_by": order_by,
                    "convergence": {"const": "REJOIN"},
                },
            ),
        ]
    )
    insert_required = {
        "relation": relation,
        "bindings": _array(_ref("binding"), min_items=1),
    }
    branches.append(
        _closed_object(
            {
                "node_id": identifier,
                "op": {"const": "INSERT"},
                "operands": _closed_object(
                    {
                        **insert_required,
                        "output_symbol": identifier,
                        "returning_columns": columns,
                    },
                    required=["relation", "bindings"],
                ),
            }
        )
    )
    branches.append(
        _closed_object(
            {
                "node_id": identifier,
                "op": {"const": "INSERT_OR_RELOAD_COMPARE"},
                "operands": _closed_object(
                    {
                        **insert_required,
                        "conflict_key_columns": columns,
                        "winner_columns": columns,
                        "winner_predicate": expression,
                        "cardinality": {"const": "EXACTLY_ONE"},
                        "output_symbol": identifier,
                        "returning_columns": columns,
                    },
                    required=[
                        "relation",
                        "bindings",
                        "conflict_key_columns",
                        "winner_columns",
                        "winner_predicate",
                        "cardinality",
                    ],
                ),
            }
        )
    )
    branches.append(
        _closed_object(
            {
                "node_id": identifier,
                "op": {"const": "UPDATE"},
                "operands": _closed_object(
                    {
                        "relation": relation,
                        "key_columns": columns,
                        "predicate": expression,
                        "set_bindings": _array(_ref("binding"), min_items=1),
                        "affected_cardinality": {"const": "EXACTLY_ONE"},
                        "output_symbol": identifier,
                        "returning_columns": columns,
                    },
                    required=[
                        "relation",
                        "key_columns",
                        "predicate",
                        "set_bindings",
                        "affected_cardinality",
                    ],
                ),
            }
        )
    )
    branches.extend(
        [
            node(
                "DELETE_SOURCE",
                {
                    "relation": relation,
                    "key_columns": columns,
                    "predicate": expression,
                    "max_rows": {"type": "integer", "minimum": 1},
                    "cascade": {"const": False},
                    "output_symbol": identifier,
                    "output_type": {"const": "pg_catalog.bigint"},
                },
            ),
            _closed_object(
                {
                    "node_id": identifier,
                    "op": {"const": "CALL_SUPPORT"},
                    "operands": _closed_object(
                        {
                            "function": {"const": EXACT_SUPPORT_FUNCTION},
                            "arguments": _array(expression),
                            "output_symbol": identifier,
                        },
                        required=["function", "arguments"],
                    ),
                }
            ),
        ]
    )
    for op in ("RETURN_ROW", "RETURN_COMPOSITE"):
        branches.append(
            node(
                op,
                {
                    "source_symbol": identifier,
                    "type": _string(pattern=_QUALIFIED),
                    "cardinality": {"enum": _CARDINALITIES},
                },
            )
        )
    for op in ("RETURN_NEW", "RETURN_OLD", "RETURN_NULL"):
        branches.append(node(op, {}))
    branches.extend(
        [
            node("RAISE", {"failure_id": identifier}),
            node(
                "PROPAGATE_RETRYABLE",
                {
                    "sqlstates": {
                        "type": "array",
                        "prefixItems": [{"const": "40001"}, {"const": "40P01"}],
                        "minItems": 2,
                        "maxItems": 2,
                        "items": False,
                    },
                    "internal_retry": {"const": False},
                },
            ),
        ]
    )
    return {
        "instruction_node": {"oneOf": branches},
        "order_item": _closed_object(
            {
                "column": _string(pattern=r"^[a-z][a-z0-9_]*$"),
                "direction": {"enum": ["ASC", "DESC"]},
            }
        ),
        "binding": _closed_object(
            {
                "column": _string(pattern=r"^[a-z][a-z0-9_]*$"),
                "value": expression,
            }
        ),
        "trigger_arm": _closed_object(
            {"tg_op": {"enum": _TG_OPS}, "nodes": node_array}
        ),
    }


def _effect_defs() -> dict[str, Any]:
    relation_columns = _closed_object(
        {
            "relation": _string(pattern=_QUALIFIED),
            "columns": _array(_string(pattern=r"^[a-z][a-z0-9_]*$"), unique=True),
        }
    )
    lock = _closed_object(
        {
            "relation": _string(pattern=_QUALIFIED),
            "columns": _array(
                _string(pattern=r"^[a-z][a-z0-9_]*$"), min_items=1, unique=True
            ),
            "mode": {"enum": _LOCK_MODES},
            "ordinal": {"type": "integer", "minimum": 1},
        }
    )
    row_image = _closed_object(
        {
            "image": {"enum": ["OLD", "NEW"]},
            "relation": _string(pattern=_QUALIFIED),
            "tg_op": _string(),
            "columns": _array(
                _string(pattern=r"^[a-z][a-z0-9_]*$"), min_items=1, unique=True
            ),
        }
    )
    output = _closed_object(
        {
            "type": _string(pattern=_QUALIFIED),
            "cardinality": _string(pattern=r"^[A-Z][A-Z0-9_]*$"),
        }
    )
    return {
        "relation_columns": relation_columns,
        "lock_effect": lock,
        "row_image_effect": row_image,
        "output": output,
        "derived_effect_summary": _closed_object(
            {
                "reads": _array(_ref("relation_columns")),
                "locks": _array(_ref("lock_effect")),
                "inserts": _array(_ref("relation_columns")),
                "updates": _array(_ref("relation_columns")),
                "deletes": _array(_ref("relation_columns")),
                "calls": _array(
                    _closed_object({"function": _string(pattern=_QUALIFIED)})
                ),
                "failures": _array(_string(pattern=_IDENTIFIER), unique=True),
                "terminals": _array(_string(pattern=r"^[A-Z][A-Z0-9_]*$"), unique=True),
                "row_image_access": _array(_ref("row_image_effect")),
                "output": {"oneOf": [_ref("output"), {"type": "null"}]},
            }
        ),
    }


def _program_def() -> dict[str, Any]:
    source = _closed_object(
        {
            "kind": {"enum": ["INPUT", "LOCAL", "SYSTEM"]},
            "relation": _string(pattern=_QUALIFIED),
            "columns": _array(
                _string(pattern=r"^[a-z][a-z0-9_]*$"), min_items=1, unique=True
            ),
        },
        required=["kind"],
    )
    symbol = _closed_object(
        {
            "id": _string(pattern=_IDENTIFIER),
            "type": _string(pattern=_QUALIFIED),
            "source": source,
        }
    )
    ast = _closed_object(
        {
            "op": {"const": "SEQUENCE"},
            "nodes": _array(_ref("instruction_node"), min_items=1),
        }
    )
    return _closed_object(
        {
            "id": _string(pattern=_QUALIFIED),
            "kind": {"enum": ["ENTRY_POINT", "TRIGGER_FUNCTION"]},
            "signature_id": _string(pattern=_QUALIFIED),
            "symbols": _array(symbol),
            "ast": ast,
            "derived_effect_summary": _ref("derived_effect_summary"),
        }
    )


def _extract_signature_groups(contract: Mapping[str, Any]) -> Mapping[str, Any]:
    parent = contract.get("effective_parent_summary")
    if not isinstance(parent, Mapping):
        raise ValueError("effective_parent_summary must be an object")
    signatures = parent.get("effective_signatures")
    if not isinstance(signatures, Mapping):
        raise ValueError("effective_signatures must be an object")
    return signatures


def _exact_ids(items: Any, *, field: str, label: str) -> list[str]:
    if not isinstance(items, list):
        raise ValueError(f"{label} must be an array")
    values: list[str] = []
    for item in items:
        if not isinstance(item, Mapping) or not isinstance(item.get(field), str):
            raise ValueError(f"{label} entries need string {field}")
        values.append(item[field])
    return values


def build_schema(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deterministic Draft 2020-12 structural schema.

    The supplied contract provides the exact positional envelopes.  Invalid or
    non-frozen populations are rejected before a schema is emitted.
    """

    if not isinstance(contract, Mapping):
        raise TypeError("contract must be an object")
    normative_envelope_present = (
        "parent_binding" in contract
        or "structural_feasibility_recovery_v1" in contract
    )
    if normative_envelope_present:
        assert_normative_envelope(contract)
    signatures = _extract_signature_groups(contract)
    entry_signatures = signatures.get("entry_points")
    trigger_signatures = signatures.get("trigger_functions")
    if _exact_ids(entry_signatures, field="id", label="entry signatures") != list(
        EXACT_ENTRY_POINTS
    ):
        raise ValueError("entry signature population/order is not frozen")
    if _exact_ids(trigger_signatures, field="id", label="trigger signatures") != list(
        EXACT_TRIGGER_FUNCTIONS
    ):
        raise ValueError("trigger signature population/order is not frozen")
    support = signatures.get("support")
    if not isinstance(support, Mapping) or support.get("id") != EXACT_SUPPORT_FUNCTION:
        raise ValueError("support signature is not frozen")

    programs = contract.get("body_programs")
    program_ids = _exact_ids(programs, field="id", label="body programs")
    exact_program_ids = [*EXACT_ENTRY_POINTS, *EXACT_TRIGGER_FUNCTIONS]
    if program_ids != exact_program_ids:
        raise ValueError("body program population/order is not frozen")

    parent = contract["effective_parent_summary"]
    declarations = parent.get("trigger_declarations")
    if _exact_ids(declarations, field="function", label="trigger declarations") != list(
        EXACT_TRIGGER_FUNCTIONS
    ):
        raise ValueError("trigger declaration population/order is not frozen")
    trigger_matrix = contract.get("trigger_applicability_return_matrix")
    if _exact_ids(trigger_matrix, field="function", label="trigger matrix") != list(
        EXACT_TRIGGER_FUNCTIONS
    ):
        raise ValueError("trigger matrix population/order is not frozen")
    failures = contract.get("failure_registry")
    failure_ids = _exact_ids(failures, field="id", label="failure registry")
    if len(failure_ids) != len(set(failure_ids)):
        raise ValueError("failure ids must be unique")

    defs: dict[str, Any] = {
        "json_value": _json_value_def(),
        **_expression_defs(),
        **_node_defs(),
        **_effect_defs(),
        "body_program": _program_def(),
    }

    top_properties = {
        str(key): _structural_shape(value) for key, value in contract.items()
    }
    top_properties["contract_sha256"] = {
        "const": str(contract.get("contract_sha256"))
    }
    top_properties["body_programs"] = _position_array(
        [
            _overlay_id(
                _ref("body_program"),
                id=body_id,
                signature_id=body_id,
                kind=(
                    "ENTRY_POINT"
                    if body_id in EXACT_ENTRY_POINTS
                    else "TRIGGER_FUNCTION"
                ),
            )
            for body_id in exact_program_ids
        ]
    )
    top_properties["failure_registry"] = _position_array(
        [
            _overlay_id(_structural_shape(failure), id=failure_id)
            for failure, failure_id in zip(failures, failure_ids, strict=True)
        ]
    )
    top_properties["trigger_applicability_return_matrix"] = _position_array(
        [
            _overlay_id(
                _structural_shape(row),
                function=body_id,
                trigger=str(row.get("trigger")),
            )
            for row, body_id in zip(
                trigger_matrix, EXACT_TRIGGER_FUNCTIONS, strict=True
            )
        ]
    )

    parent_schema = _structural_shape(parent)
    parent_properties = parent_schema["properties"]
    signature_schema = _structural_shape(signatures)
    signature_properties = signature_schema["properties"]
    signature_properties["support"] = _overlay_id(
        _structural_shape(support), id=EXACT_SUPPORT_FUNCTION
    )
    signature_properties["entry_points"] = _position_array(
        [
            _overlay_id(_structural_shape(item), id=body_id)
            for item, body_id in zip(entry_signatures, EXACT_ENTRY_POINTS, strict=True)
        ]
    )
    signature_properties["trigger_functions"] = _position_array(
        [
            _overlay_id(_structural_shape(item), id=body_id)
            for item, body_id in zip(
                trigger_signatures, EXACT_TRIGGER_FUNCTIONS, strict=True
            )
        ]
    )
    parent_properties["effective_signatures"] = signature_schema
    parent_properties["trigger_declarations"] = _position_array(
        [
            _overlay_id(
                _structural_shape(declaration),
                id=str(declaration.get("id")),
                function=body_id,
            )
            for declaration, body_id in zip(
                declarations, EXACT_TRIGGER_FUNCTIONS, strict=True
            )
        ]
    )
    effective_roles = parent.get("effective_roles")
    if effective_roles is not None and not isinstance(effective_roles, list):
        raise ValueError("effective roles must be an array")
    if isinstance(effective_roles, list):
        parent_properties["effective_roles"] = _position_array(
            [
                _overlay_id(
                    _structural_shape(role),
                    role=str(role.get("role")),
                )
                for role in effective_roles
            ]
        )
    top_properties["effective_parent_summary"] = parent_schema
    if normative_envelope_present:
        for normative_section in (
            "parent_binding",
            "structural_feasibility_recovery_v1",
            "effective_parent_summary",
            "typed_ir_contract",
            "trigger_applicability_return_matrix",
            "renderer_order",
            "artifact_boundary",
        ):
            top_properties[normative_section] = _normative_shape(
                contract[normative_section]
            )

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://emr4.local/schemas/raisa-provider-free-unmounted-durability-function-trigger-body-architecture.schema.json",
        "title": "EMR4 provider-free unmounted durability typed body architecture",
        "type": "object",
        "properties": top_properties,
        "required": list(contract),
        "additionalProperties": False,
        "$defs": defs,
    }


__all__ = ["build_schema"]
