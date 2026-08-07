from __future__ import annotations

from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema import (
    build_schema,
)
from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator import (
    ContractValidationError,
    EXACT_ENTRY_POINTS,
    EXACT_SUPPORT_FUNCTION,
    EXACT_TRIGGER_FUNCTIONS,
    EXPRESSION_OPCODES,
    INSTRUCTION_OPCODES,
    assert_contract_valid,
    derive_contract_semantics,
    validate_contract,
)


TEST_RELATION = "emr4_context_fabric.test_rows"
OTHER_RELATION = "emr4_context_fabric.other_rows"
TEST_COMPOSITE = "emr4_context_fabric.test_composite_v1"


def _const(type_name: str, value: object) -> dict[str, object]:
    return {"op": "CONST", "type": type_name, "value": value}


def _entry_signature(body_id: str) -> dict[str, object]:
    return {
        "id": body_id,
        "inputs": [],
        "output": {"type": TEST_RELATION, "cardinality": "EXACTLY_ONE"},
    }


def _trigger_signature(body_id: str) -> dict[str, object]:
    return {
        "id": body_id,
        "inputs": [],
        "output": {
            "type": "pg_catalog.trigger",
            "cardinality": "EXACTLY_ONE_OR_RAISE",
        },
    }


def _entry_program(body_id: str) -> dict[str, object]:
    return {
        "id": body_id,
        "kind": "ENTRY_POINT",
        "signature_id": body_id,
        "symbols": [{"id": "row", "type": TEST_RELATION, "source": {"kind": "LOCAL"}}],
        "ast": {
            "op": "SEQUENCE",
            "nodes": [
                {
                    "node_id": f"{body_id}.select",
                    "op": "SELECT_EXACT",
                    "operands": {
                        "relation": TEST_RELATION,
                        "columns": ["id", "value"],
                        "predicate": _const("pg_catalog.boolean", True),
                        "output_symbol": "row",
                        "cardinality": "EXACTLY_ONE",
                        "order_by": [{"column": "id", "direction": "ASC"}],
                    },
                },
                {
                    "node_id": f"{body_id}.return",
                    "op": "RETURN_ROW",
                    "operands": {
                        "source_symbol": "row",
                        "type": TEST_RELATION,
                        "cardinality": "EXACTLY_ONE",
                    },
                },
            ],
        },
    }


def _trigger_program(body_id: str) -> dict[str, object]:
    return {
        "id": body_id,
        "kind": "TRIGGER_FUNCTION",
        "signature_id": body_id,
        "symbols": [],
        "ast": {
            "op": "SEQUENCE",
            "nodes": [
                {
                    "node_id": f"{body_id}.switch",
                    "op": "SWITCH_TG_OP",
                    "operands": {
                        "arms": [
                            {
                                "tg_op": "UPDATE",
                                "nodes": [
                                    {
                                        "node_id": f"{body_id}.update.return",
                                        "op": "RETURN_NEW",
                                        "operands": {},
                                    }
                                ],
                            }
                        ],
                        "default": [
                            {
                                "node_id": f"{body_id}.default.raise",
                                "op": "RAISE",
                                "operands": {"failure_id": "F_TRIGGER_CONTEXT"},
                            }
                        ],
                        "convergence": "ALL_TERMINAL",
                    },
                }
            ],
        },
    }


def _unsealed_contract() -> dict[str, object]:
    entry_signatures = [_entry_signature(body_id) for body_id in EXACT_ENTRY_POINTS]
    trigger_signatures = [
        _trigger_signature(body_id) for body_id in EXACT_TRIGGER_FUNCTIONS
    ]
    declarations = [
        {
            "id": f"trg_{index:02d}",
            "function": body_id,
            "relation": TEST_RELATION,
            "timing": "BEFORE",
            "row_level": True,
            "events": ["UPDATE"],
            "deferrable": False,
            "initially_deferred": False,
        }
        for index, body_id in enumerate(EXACT_TRIGGER_FUNCTIONS, start=1)
    ]
    matrix = [
        {
            "function": body_id,
            "trigger": f"trg_{index:02d}",
            "relation": TEST_RELATION,
            "events": ["UPDATE"],
            "returns": {"UPDATE": "RETURN_NEW"},
            "read_only": True,
            "lock_free": True,
            "sibling_call_free": True,
        }
        for index, body_id in enumerate(EXACT_TRIGGER_FUNCTIONS, start=1)
    ]
    return {
        "qualified_identifier_catalogue": {
            "relations": {
                TEST_RELATION: ["id", "value"],
                OTHER_RELATION: ["id", "value"],
                "emr4_context_fabric.diary_context_observation_outbox_v1": [
                    "stream_id",
                    "transaction_position",
                ],
            },
            "column_types": {
                TEST_RELATION: {
                    "id": "pg_catalog.uuid",
                    "value": "pg_catalog.bigint",
                },
                OTHER_RELATION: {
                    "id": "pg_catalog.uuid",
                    "value": "pg_catalog.bigint",
                },
                "emr4_context_fabric.diary_context_observation_outbox_v1": {
                    "stream_id": "pg_catalog.uuid",
                    "transaction_position": "pg_catalog.bigint",
                },
            },
            "composite_fields": {
                TEST_COMPOSITE: {
                    "value": "pg_catalog.bigint",
                    "payload": "pg_catalog.jsonb",
                }
            },
            "types": [
                "pg_catalog.bigint",
                "pg_catalog.boolean",
                "pg_catalog.integer",
                "pg_catalog.jsonb",
                "pg_catalog.name",
                "pg_catalog.text",
                "pg_catalog.timestamptz",
                "pg_catalog.trigger",
                "pg_catalog.uuid",
                "pg_catalog.xid",
                "emr4_context_fabric.digest_sha256",
                TEST_COMPOSITE,
                f"{TEST_RELATION}[]",
                f"{OTHER_RELATION}[]",
            ],
        },
        "failure_registry": [
            {
                "id": "F_TRIGGER_CONTEXT",
                "sqlstate": "E0001",
                "reason_code": "UNEXPECTED_TRIGGER_CONTEXT",
            },
            {
                "id": "F_INVARIANT",
                "sqlstate": "E0002",
                "reason_code": "INVARIANT_FAILED",
            },
        ],
        "effective_parent_summary": {
            "effective_signatures": {
                "support": {
                    "id": EXACT_SUPPORT_FUNCTION,
                    "inputs": [],
                    "output": {
                        "type": "pg_catalog.boolean",
                        "cardinality": "EXACTLY_ONE",
                    },
                },
                "entry_points": entry_signatures,
                "trigger_functions": trigger_signatures,
            },
            "trigger_declarations": declarations,
        },
        "typed_ir_contract": {
            "instruction_opcodes": sorted(INSTRUCTION_OPCODES),
            "expression_opcodes": sorted(EXPRESSION_OPCODES),
        },
        "body_programs": [
            *[_entry_program(body_id) for body_id in EXACT_ENTRY_POINTS],
            *[_trigger_program(body_id) for body_id in EXACT_TRIGGER_FUNCTIONS],
        ],
        "trigger_applicability_return_matrix": matrix,
    }


def _valid_contract() -> dict[str, object]:
    contract = _unsealed_contract()
    derived = derive_contract_semantics(contract)
    summaries = derived["body_summaries"]
    for program in contract["body_programs"]:
        program["derived_effect_summary"] = summaries[program["id"]]
    contract["call_graph"] = derived["call_graph"]
    return contract


def _contract_with_field_and_json_keys() -> dict[str, object]:
    contract = _valid_contract()
    signature = contract["effective_parent_summary"]["effective_signatures"][
        "entry_points"
    ][0]
    signature["inputs"] = [{"name": "packet", "mode": "IN", "type": TEST_COMPOSITE}]
    first = contract["body_programs"][0]
    first["symbols"] = [
        {"id": "packet", "type": TEST_COMPOSITE, "source": {"kind": "INPUT"}},
        *first["symbols"],
        {
            "id": "packet_value",
            "type": "pg_catalog.bigint",
            "source": {"kind": "LOCAL"},
        },
        {
            "id": "payload_keys_valid",
            "type": "pg_catalog.boolean",
            "source": {"kind": "LOCAL"},
        },
    ]
    first["ast"]["nodes"].insert(
        1,
        {
            "node_id": f"{first['id']}.field",
            "op": "LET",
            "operands": {
                "output_symbol": "packet_value",
                "expression": {
                    "op": "FIELD",
                    "source": {
                        "op": "REF",
                        "kind": "INPUT",
                        "symbol": "packet",
                        "type": TEST_COMPOSITE,
                    },
                    "field": "value",
                    "type": "pg_catalog.bigint",
                },
            },
        },
    )
    first["ast"]["nodes"].insert(
        2,
        {
            "node_id": f"{first['id']}.json-keys",
            "op": "LET",
            "operands": {
                "output_symbol": "payload_keys_valid",
                "expression": {
                    "op": "JSON_KEYS_EXACT",
                    "source": {
                        "op": "FIELD",
                        "source": {
                            "op": "REF",
                            "kind": "INPUT",
                            "symbol": "packet",
                            "type": TEST_COMPOSITE,
                        },
                        "field": "payload",
                        "type": "pg_catalog.jsonb",
                    },
                    "keys": ["appointment_id", "start_time"],
                    "type": "pg_catalog.boolean",
                },
            },
        },
    )
    derived = derive_contract_semantics(contract)
    first["derived_effect_summary"] = derived["body_summaries"][first["id"]]
    contract["call_graph"] = derived["call_graph"]
    return contract


def _contract_with_composite_construct() -> dict[str, object]:
    contract = _contract_with_field_and_json_keys()
    first = contract["body_programs"][0]
    first["symbols"].append(
        {"id": "rebuilt", "type": TEST_COMPOSITE, "source": {"kind": "LOCAL"}}
    )
    first["ast"]["nodes"].insert(
        -1,
        {
            "node_id": f"{first['id']}.construct",
            "op": "LET",
            "operands": {
                "output_symbol": "rebuilt",
                "expression": {
                    "op": "COMPOSITE_CONSTRUCT",
                    "type": TEST_COMPOSITE,
                    "fields": [
                        {
                            "field": "value",
                            "value": {
                                "op": "FIELD",
                                "source": {
                                    "op": "REF",
                                    "kind": "INPUT",
                                    "symbol": "packet",
                                    "type": TEST_COMPOSITE,
                                },
                                "field": "value",
                                "type": "pg_catalog.bigint",
                            },
                        },
                        {
                            "field": "payload",
                            "value": {
                                "op": "FIELD",
                                "source": {
                                    "op": "REF",
                                    "kind": "INPUT",
                                    "symbol": "packet",
                                    "type": TEST_COMPOSITE,
                                },
                                "field": "payload",
                                "type": "pg_catalog.jsonb",
                            },
                        },
                    ],
                },
            },
        },
    )
    derived = derive_contract_semantics(contract)
    first["derived_effect_summary"] = derived["body_summaries"][first["id"]]
    contract["call_graph"] = derived["call_graph"]
    return contract


def _contract_with_delete_source() -> dict[str, object]:
    contract = _valid_contract()
    purge = contract["body_programs"][
        EXACT_ENTRY_POINTS.index("emr4_context_fabric.purge_source_rows_v1")
    ]
    purge["symbols"].append(
        {
            "id": "deleted_count",
            "type": "pg_catalog.bigint",
            "source": {"kind": "LOCAL"},
        }
    )
    purge["ast"]["nodes"].insert(
        1,
        {
            "node_id": f"{purge['id']}.delete",
            "op": "DELETE_SOURCE",
            "operands": {
                "relation": "emr4_context_fabric.diary_context_observation_outbox_v1",
                "key_columns": ["stream_id"],
                "predicate": _const("pg_catalog.boolean", True),
                "max_rows": 1,
                "cascade": False,
                "output_symbol": "deleted_count",
                "output_type": "pg_catalog.bigint",
            },
        },
    )
    derived = derive_contract_semantics(contract)
    purge["derived_effect_summary"] = derived["body_summaries"][purge["id"]]
    contract["call_graph"] = derived["call_graph"]
    return contract


def _codes(contract: dict[str, object]) -> set[str]:
    return {issue.code for issue in validate_contract(contract).issues}


def _schema_errors(
    contract: dict[str, object], schema: dict[str, object] | None = None
) -> list[object]:
    validator = Draft202012Validator(schema or build_schema(contract))
    return sorted(validator.iter_errors(contract), key=lambda error: list(error.path))


def test_valid_closed_contract_derives_deterministically() -> None:
    contract = _valid_contract()

    report = assert_contract_valid(contract)
    first = derive_contract_semantics(contract)
    second = derive_contract_semantics(deepcopy(contract))

    assert report.valid is True
    assert len(report.body_summaries) == 22
    assert first == second
    assert first["call_graph"] == contract["call_graph"]
    assert all(first["path_summaries"].values())


def test_terminal_assert_branch_is_carried_while_live_branch_continues() -> None:
    contract = _valid_contract()
    first = contract["body_programs"][0]
    first["ast"]["nodes"].insert(
        0,
        {
            "node_id": f"{first['id']}.assert",
            "op": "ASSERT",
            "operands": {
                "predicate": _const("pg_catalog.boolean", True),
                "failure_id": "F_INVARIANT",
            },
        },
    )

    derived = derive_contract_semantics(contract)

    assert "RAISE" in derived["body_summaries"][first["id"]]["terminals"]
    assert "RETURN_ROW" in derived["body_summaries"][first["id"]]["terminals"]


def test_select_set_assigns_relation_array_not_scalar_relation() -> None:
    contract = _valid_contract()
    first = contract["body_programs"][0]
    first["symbols"].append(
        {
            "id": "rows",
            "type": f"{TEST_RELATION}[]",
            "source": {"kind": "LOCAL"},
        }
    )
    first["ast"]["nodes"].insert(
        0,
        {
            "node_id": f"{first['id']}.select-set",
            "op": "SELECT_SET",
            "operands": {
                "relation": TEST_RELATION,
                "columns": ["id", "value"],
                "predicate": _const("pg_catalog.boolean", True),
                "output_symbol": "rows",
                "cardinality": "COMPLETE_SET",
                "order_by": [{"column": "id", "direction": "ASC"}],
            },
        },
    )

    assert derive_contract_semantics(contract)["body_summaries"][first["id"]]

    first["symbols"][-1]["type"] = TEST_RELATION
    assert "output_type" in _codes(contract)


def _contract_with_min_field() -> dict[str, object]:
    contract = _valid_contract()
    first = contract["body_programs"][0]
    first["symbols"].extend(
        [
            {
                "id": "rows",
                "type": f"{TEST_RELATION}[]",
                "source": {"kind": "LOCAL"},
            },
            {
                "id": "minimum_value",
                "type": "pg_catalog.bigint",
                "source": {"kind": "LOCAL"},
            },
        ]
    )
    first["ast"]["nodes"][0:0] = [
        {
            "node_id": f"{first['id']}.select-set",
            "op": "SELECT_SET",
            "operands": {
                "relation": TEST_RELATION,
                "columns": ["id", "value"],
                "predicate": _const("pg_catalog.boolean", True),
                "output_symbol": "rows",
                "cardinality": "COMPLETE_SET",
                "order_by": [{"column": "id", "direction": "ASC"}],
            },
        },
        {
            "node_id": f"{first['id']}.minimum",
            "op": "LET",
            "operands": {
                "output_symbol": "minimum_value",
                "expression": {
                    "op": "MIN_FIELD",
                    "source": {
                        "op": "REF",
                        "kind": "LOCAL",
                        "symbol": "rows",
                        "type": f"{TEST_RELATION}[]",
                    },
                    "field": "value",
                    "type": "pg_catalog.bigint",
                },
            },
        },
    ]
    return contract


def test_min_field_uses_only_assigned_selected_row_set_metadata() -> None:
    contract = _contract_with_min_field()

    derived = derive_contract_semantics(contract)
    summary = derived["body_summaries"][contract["body_programs"][0]["id"]]

    assert summary["reads"] == [
        {"relation": TEST_RELATION, "columns": ["id", "value"]}
    ]


def test_min_field_rejects_unselected_field_wrong_type_and_non_set_source() -> None:
    unselected = _contract_with_min_field()
    unselected_expression = unselected["body_programs"][0]["ast"]["nodes"][1][
        "operands"
    ]["expression"]
    unselected_expression["field"] = "missing"

    wrong_type = _contract_with_min_field()
    wrong_type_expression = wrong_type["body_programs"][0]["ast"]["nodes"][1][
        "operands"
    ]["expression"]
    wrong_type_expression["type"] = "pg_catalog.uuid"

    non_set = _contract_with_min_field()
    non_set_expression = non_set["body_programs"][0]["ast"]["nodes"][1]["operands"][
        "expression"
    ]
    non_set_expression["source"] = _const("pg_catalog.bigint", 1)

    assert "min_field_not_selected" in _codes(unselected)
    assert "min_field_result_type" in _codes(wrong_type)
    assert "min_field_source" in _codes(non_set)


def test_composite_field_and_exact_json_keys_are_typed_and_valid() -> None:
    contract = _contract_with_field_and_json_keys()

    report = assert_contract_valid(contract)

    assert report.valid is True


def test_composite_field_unknown_and_type_mismatch_reject() -> None:
    unknown = _contract_with_field_and_json_keys()
    unknown_expression = unknown["body_programs"][0]["ast"]["nodes"][1]["operands"][
        "expression"
    ]
    unknown_expression["field"] = "missing"

    mismatched = _contract_with_field_and_json_keys()
    mismatched_expression = mismatched["body_programs"][0]["ast"]["nodes"][1][
        "operands"
    ]["expression"]
    mismatched_expression["type"] = "pg_catalog.uuid"

    assert "composite_field_unknown" in _codes(unknown)
    assert "composite_field_type_mismatch" in _codes(mismatched)


def test_exact_json_keys_reject_wrong_source_duplicates_and_non_boolean_result() -> (
    None
):
    contract = _contract_with_field_and_json_keys()
    expression = contract["body_programs"][0]["ast"]["nodes"][2]["operands"][
        "expression"
    ]
    expression["source"]["field"] = "value"
    expression["source"]["type"] = "pg_catalog.bigint"
    expression["keys"] = ["appointment_id", "appointment_id"]
    expression["type"] = "pg_catalog.text"

    codes = _codes(contract)

    assert "json_keys_source_type" in codes
    assert "json_keys_duplicate" in codes
    assert "json_keys_result_type" in codes


def test_composite_construct_exact_population_and_types_are_valid() -> None:
    contract = _contract_with_composite_construct()

    assert assert_contract_valid(contract).valid is True


def test_composite_construct_rejects_missing_reordered_unknown_and_wrong_type() -> None:
    missing = _contract_with_composite_construct()
    missing_expression = missing["body_programs"][0]["ast"]["nodes"][-2]["operands"][
        "expression"
    ]
    missing_expression["fields"].pop()

    reordered = _contract_with_composite_construct()
    reordered_expression = reordered["body_programs"][0]["ast"]["nodes"][-2][
        "operands"
    ]["expression"]
    reordered_expression["fields"].reverse()

    wrong = _contract_with_composite_construct()
    wrong_expression = wrong["body_programs"][0]["ast"]["nodes"][-2]["operands"][
        "expression"
    ]
    wrong_expression["fields"][0]["field"] = "missing"
    wrong_expression["fields"][1]["value"] = _const("pg_catalog.bigint", 1)

    assert "composite_construct_population" in _codes(missing)
    assert "composite_construct_population" in _codes(reordered)
    wrong_codes = _codes(wrong)
    assert "composite_construct_field_unknown" in wrong_codes
    assert "composite_construct_field_type" in wrong_codes


def test_delete_source_assigns_exact_bigint_result_without_widening_delete_effect() -> (
    None
):
    contract = _contract_with_delete_source()

    report = assert_contract_valid(contract)
    summary = report.body_summaries["emr4_context_fabric.purge_source_rows_v1"]

    assert summary["deletes"] == [
        {
            "relation": "emr4_context_fabric.diary_context_observation_outbox_v1",
            "columns": ["stream_id"],
        }
    ]


def test_delete_source_requires_declared_bigint_output() -> None:
    contract = _contract_with_delete_source()
    purge = contract["body_programs"][
        EXACT_ENTRY_POINTS.index("emr4_context_fabric.purge_source_rows_v1")
    ]
    purge["ast"]["nodes"][1]["operands"]["output_type"] = "pg_catalog.uuid"

    assert "delete_output_type" in _codes(contract)


def test_builder_api_raises_with_sorted_deterministic_issues() -> None:
    contract = _valid_contract()
    contract["body_programs"][0]["ast"]["nodes"][0]["operands"]["columns"] = ["missing"]

    with pytest.raises(ContractValidationError) as error:
        derive_contract_semantics(contract)

    assert error.value.issues == tuple(sorted(set(error.value.issues)))
    assert "unknown_column" in {issue.code for issue in error.value.issues}


@pytest.mark.parametrize(
    "forbidden_op", ["PROFILE_EVAL", "DERIVE_COLUMN_VALUE", "RAW_SQL"]
)
def test_opaque_expression_and_raw_ops_are_unrepresentable(forbidden_op: str) -> None:
    contract = _valid_contract()
    select = contract["body_programs"][0]["ast"]["nodes"][0]
    select["operands"]["predicate"] = {"op": forbidden_op}

    assert "expression_opcode" in _codes(contract)


def test_authored_node_effect_and_authored_graph_fact_reject() -> None:
    contract = _valid_contract()
    contract["body_programs"][0]["ast"]["nodes"][0]["effect"] = {"reads": []}
    contract["call_graph"]["derived_facts"] = {"acyclic": True}

    codes = _codes(contract)

    assert "node_fields" in codes
    assert "authored_node_fact" in codes
    assert "call_graph_mismatch" in codes


def test_unassigned_symbol_and_unselected_source_column_reject() -> None:
    contract = _valid_contract()
    first = contract["body_programs"][0]
    first["symbols"].append(
        {"id": "ghost", "type": TEST_RELATION, "source": {"kind": "LOCAL"}}
    )
    first["ast"]["nodes"][0]["operands"]["predicate"] = {
        "op": "EQ",
        "left": {
            "op": "REF",
            "kind": "ROW_COLUMN",
            "symbol": "ghost",
            "relation": TEST_RELATION,
            "column": "value",
            "type": "pg_catalog.bigint",
        },
        "right": _const("pg_catalog.bigint", 1),
        "type": "pg_catalog.boolean",
    }

    codes = _codes(contract)

    assert "row_symbol_unassigned" in codes


def test_source_column_and_qualified_catalogue_are_enforced() -> None:
    contract = _valid_contract()
    first_select = contract["body_programs"][0]["ast"]["nodes"][0]
    first_select["operands"]["predicate"] = {
        "op": "EQ",
        "left": {
            "op": "REF",
            "kind": "SOURCE_COLUMN",
            "relation": "test_rows",
            "column": "id",
            "type": "pg_catalog.uuid",
        },
        "right": _const("pg_catalog.uuid", "00000000-0000-0000-0000-000000000000"),
        "type": "pg_catalog.boolean",
    }

    codes = _codes(contract)

    assert "unqualified_relation" in codes


def test_operand_retarget_derives_new_effect_and_stored_summary_rejects() -> None:
    contract = _valid_contract()
    first_select = contract["body_programs"][0]["ast"]["nodes"][0]
    first_select["operands"]["relation"] = OTHER_RELATION

    codes = _codes(contract)

    assert "output_type" in codes
    assert "summary_mismatch" in codes


def test_trigger_row_image_relation_and_return_matrix_are_derived() -> None:
    contract = _valid_contract()
    trigger = contract["body_programs"][len(EXACT_ENTRY_POINTS)]
    arm = trigger["ast"]["nodes"][0]["operands"]["arms"][0]["nodes"]
    arm.insert(
        0,
        {
            "node_id": f"{trigger['id']}.read-wrong-image",
            "op": "ASSERT",
            "operands": {
                "predicate": {
                    "op": "EQ",
                    "left": {
                        "op": "REF",
                        "kind": "TRIGGER_COLUMN",
                        "image": "NEW",
                        "relation": OTHER_RELATION,
                        "column": "value",
                        "type": "pg_catalog.bigint",
                    },
                    "right": _const("pg_catalog.bigint", 1),
                    "type": "pg_catalog.boolean",
                },
                "failure_id": "F_INVARIANT",
            },
        },
    )
    arm[-1]["op"] = "RETURN_OLD"

    codes = _codes(contract)

    assert "row_image_relation" in codes
    assert "trigger_terminal_matrix" in codes


def test_trigger_switch_must_be_total_and_default_raise() -> None:
    contract = _valid_contract()
    trigger = contract["body_programs"][len(EXACT_ENTRY_POINTS)]
    switch = trigger["ast"]["nodes"][0]
    switch["operands"]["arms"] = []
    switch["operands"]["default"][0]["op"] = "RETURN_NULL"
    switch["operands"]["default"][0]["operands"] = {}

    codes = _codes(contract)

    assert "switch_totality" in codes
    assert "switch_default" in codes
    assert "trigger_default_terminal" in codes


def test_cfg_unreachable_node_and_wrong_convergence_reject() -> None:
    contract = _valid_contract()
    first = contract["body_programs"][0]
    first["ast"]["nodes"].append(
        {
            "node_id": f"{first['id']}.unreachable",
            "op": "RAISE",
            "operands": {"failure_id": "F_INVARIANT"},
        }
    )
    trigger = contract["body_programs"][len(EXACT_ENTRY_POINTS)]
    trigger["ast"]["nodes"][0]["operands"]["convergence"] = "REJOIN"

    codes = _codes(contract)

    assert "unreachable_node" in codes
    assert "convergence" in codes


def test_lock_order_is_ast_derived_not_sorted_from_authored_summary() -> None:
    contract = _valid_contract()
    first = contract["body_programs"][0]
    locks = [
        {
            "node_id": f"{first['id']}.lock2",
            "op": "LOCK_EXACT",
            "operands": {
                "relation": TEST_RELATION,
                "key_columns": ["id"],
                "predicate": _const("pg_catalog.boolean", True),
                "mode": "FOR_UPDATE",
                "ordinal": 2,
            },
        },
        {
            "node_id": f"{first['id']}.lock1",
            "op": "LOCK_EXACT",
            "operands": {
                "relation": OTHER_RELATION,
                "key_columns": ["id"],
                "predicate": _const("pg_catalog.boolean", True),
                "mode": "FOR_UPDATE",
                "ordinal": 1,
            },
        },
    ]
    first["ast"]["nodes"] = [*locks, *first["ast"]["nodes"]]

    assert "lock_acquisition_order" in _codes(contract)


def test_sibling_call_and_derived_cycle_reject() -> None:
    contract = _valid_contract()
    first = contract["body_programs"][0]
    second = contract["body_programs"][1]
    first["ast"]["nodes"].insert(
        0,
        {
            "node_id": f"{first['id']}.bad-call",
            "op": "CALL_SUPPORT",
            "operands": {"function": second["id"], "arguments": []},
        },
    )
    second["ast"]["nodes"].insert(
        0,
        {
            "node_id": f"{second['id']}.bad-call",
            "op": "CALL_SUPPORT",
            "operands": {"function": first["id"], "arguments": []},
        },
    )

    codes = _codes(contract)

    assert "call_not_support" in codes
    assert "entry_sibling_call" in codes
    assert "call_cycle" in codes


def test_raw_ddl_text_internal_retry_and_non_source_delete_reject() -> None:
    contract = _valid_contract()
    first = contract["body_programs"][0]
    first["ast"]["nodes"][0]["operands"]["predicate"] = _const(
        "pg_catalog.text", "CREATE TABLE forbidden"
    )
    first["ast"]["nodes"].insert(
        1,
        {
            "node_id": f"{first['id']}.delete",
            "op": "DELETE_SOURCE",
            "operands": {
                "relation": TEST_RELATION,
                "key_columns": ["id"],
                "predicate": _const("pg_catalog.boolean", True),
                "max_rows": 1,
                "cascade": True,
            },
        },
    )
    first["ast"]["nodes"].insert(
        2,
        {
            "node_id": f"{first['id']}.retry",
            "op": "PROPAGATE_RETRYABLE",
            "operands": {"sqlstates": ["40001", "40P01"], "internal_retry": True},
        },
    )

    codes = _codes(contract)

    assert "raw_sql_text" in codes
    assert "internal_retry" in codes
    assert "delete_relation" in codes
    assert "delete_cascade" in codes


def test_unknown_vocabulary_and_population_swaps_reject() -> None:
    contract = _valid_contract()
    contract["typed_ir_contract"]["instruction_opcodes"].append("GENERIC_EXECUTE")
    first, second = contract["body_programs"][0:2]
    contract["body_programs"][0:2] = [second, first]

    codes = _codes(contract)

    assert "instruction_vocabulary" in codes
    assert "program_population_order" in codes


def test_structural_schema_is_valid_draft_2020_12_and_accepts_contract() -> None:
    contract = _contract_with_field_and_json_keys()
    schema = build_schema(contract)

    Draft202012Validator.check_schema(schema)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert "oneOf" in schema["$defs"]["instruction_node"]
    assert "oneOf" in schema["$defs"]["expression"]
    assert _schema_errors(contract, schema) == []


def test_structural_schema_position_closes_program_signatures_and_triggers() -> None:
    canonical = _valid_contract()
    schema = build_schema(canonical)

    program_swap = deepcopy(canonical)
    program_swap["body_programs"][0], program_swap["body_programs"][1] = (
        program_swap["body_programs"][1],
        program_swap["body_programs"][0],
    )
    signature_swap = deepcopy(canonical)
    signatures = signature_swap["effective_parent_summary"]["effective_signatures"]
    signatures["entry_points"][0]["id"] = EXACT_ENTRY_POINTS[1]
    trigger_swap = deepcopy(canonical)
    declarations = trigger_swap["effective_parent_summary"]["trigger_declarations"]
    declarations[0]["function"] = EXACT_TRIGGER_FUNCTIONS[1]

    assert _schema_errors(program_swap, schema)
    assert _schema_errors(signature_swap, schema)
    assert _schema_errors(trigger_swap, schema)


def test_structural_schema_position_closes_failure_ids_and_rejects_extra_fields() -> (
    None
):
    canonical = _valid_contract()
    schema = build_schema(canonical)
    wrong_failure = deepcopy(canonical)
    wrong_failure["failure_registry"][0]["id"] = "F_DIFFERENT"
    extra_node = deepcopy(canonical)
    extra_node["body_programs"][0]["ast"]["nodes"][0]["authored_effect"] = {}
    extra_expression = deepcopy(canonical)
    predicate = extra_expression["body_programs"][0]["ast"]["nodes"][0]["operands"][
        "predicate"
    ]
    predicate["opaque"] = "not admitted"

    assert _schema_errors(wrong_failure, schema)
    assert _schema_errors(extra_node, schema)
    assert _schema_errors(extra_expression, schema)


def test_structural_schema_rejects_unknown_node_and_expression_ops() -> None:
    canonical = _valid_contract()
    schema = build_schema(canonical)
    bad_node = deepcopy(canonical)
    bad_node["body_programs"][0]["ast"]["nodes"][0]["op"] = "GENERIC_EXECUTE"
    bad_expression = deepcopy(canonical)
    bad_expression["body_programs"][0]["ast"]["nodes"][0]["operands"]["predicate"][
        "op"
    ] = "PROFILE_EVAL"

    assert _schema_errors(bad_node, schema)
    assert _schema_errors(bad_expression, schema)


def test_structural_schema_does_not_const_freeze_program_bodies_or_effects() -> None:
    canonical = _valid_contract()
    schema = build_schema(canonical)
    structurally_equivalent = deepcopy(canonical)
    first = structurally_equivalent["body_programs"][0]
    first["ast"]["nodes"][0]["node_id"] = f"{first['id']}.renamed-select"
    first["ast"]["nodes"][0]["operands"]["predicate"]["value"] = False
    first["derived_effect_summary"]["terminals"].reverse()

    assert _schema_errors(structurally_equivalent, schema) == []
