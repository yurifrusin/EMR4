"""Acceptance and adversarial tests for the closed durability body contract."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder import (
    PARENT_DIGEST,
    PARENT_PATH,
    build_contract,
)
from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema import (
    build_schema,
)
from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator import (
    EXACT_ENTRY_POINTS,
    EXACT_TRIGGER_FUNCTIONS,
    assert_contract_valid,
    derive_contract_semantics,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "function-trigger-body-architecture"
)
CONTRACT_PATH = CONTRACT_DIR / "function-trigger-body-architecture-contract.json"
SCHEMA_PATH = CONTRACT_DIR / "function-trigger-body-architecture-contract.schema.json"
PREFIX = "emr4_context_fabric."
OUTBOX = PREFIX + "diary_context_observation_outbox_v1"
ALIAS = PREFIX + "diary_context_aggregate_aliases_v1"
HEAD = PREFIX + "context_observation_stream_head"
ADMISSION = PREFIX + "context_proofread_observation_admission"
RECEIPT = PREFIX + "context_classified_observation_receipt"
EVENT = "public.diary_committed_events"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(contract: dict[str, Any]) -> str:
    payload = copy.deepcopy(contract)
    payload.pop("contract_sha256", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def programs(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {program["id"]: program for program in contract["body_programs"]}


def walk_nodes(nodes: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    for node in nodes:
        yield node
        operands = node["operands"]
        if node["op"] == "IF":
            yield from walk_nodes(operands["then"])
            yield from walk_nodes(operands["else"])
        elif node["op"] == "SWITCH_TG_OP":
            for arm in operands["arms"]:
                yield from walk_nodes(arm["nodes"])
            yield from walk_nodes(operands["default"])
        elif node["op"] == "FOR_EACH":
            yield from walk_nodes(operands["nodes"])


def nodes(program: dict[str, Any]) -> list[dict[str, Any]]:
    return list(walk_nodes(program["ast"]["nodes"]))


def expressions(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        if "op" in value and "node_id" not in value:
            yield value
        for child in value.values():
            yield from expressions(child)
    elif isinstance(value, list):
        for child in value:
            yield from expressions(child)


def refresh_evidence(candidate: dict[str, Any]) -> dict[str, Any]:
    for program in candidate["body_programs"]:
        program["derived_effect_summary"] = {}
    candidate["call_graph"] = {}
    derived = derive_contract_semantics(candidate)
    for program in candidate["body_programs"]:
        program["derived_effect_summary"] = derived["body_summaries"][program["id"]]
    candidate["call_graph"] = derived["call_graph"]
    candidate["contract_sha256"] = canonical_digest(candidate)
    return candidate


def frozen_policy(candidate: dict[str, Any], baseline: dict[str, Any]) -> None:
    """Independent exact-body envelope used by the hostile-mutation packet."""

    assert_contract_valid(candidate)
    assert candidate["structural_feasibility_recovery_v1"] == baseline[
        "structural_feasibility_recovery_v1"
    ]
    assert candidate["effective_parent_summary"] == baseline["effective_parent_summary"]
    assert candidate["qualified_identifier_catalogue"] == baseline[
        "qualified_identifier_catalogue"
    ]
    assert candidate["failure_registry"] == baseline["failure_registry"]
    assert candidate["trigger_applicability_return_matrix"] == baseline[
        "trigger_applicability_return_matrix"
    ]
    assert candidate["artifact_boundary"] == baseline["artifact_boundary"]
    assert candidate["renderer_order"] == baseline["renderer_order"]
    for actual, expected in zip(
        candidate["body_programs"], baseline["body_programs"], strict=True
    ):
        assert actual["id"] == expected["id"]
        assert actual["symbols"] == expected["symbols"]
        assert actual["ast"] == expected["ast"]
        assert actual["derived_effect_summary"] == expected["derived_effect_summary"]
    assert candidate["call_graph"] == baseline["call_graph"]


def rejected_after_refresh(
    baseline: dict[str, Any], mutate: Callable[[dict[str, Any]], None]
) -> None:
    candidate = copy.deepcopy(baseline)
    mutate(candidate)
    try:
        refresh_evidence(candidate)
    except Exception:  # a malformed typed program is an expected fail-closed result
        return
    try:
        schema = build_schema(candidate)
    except Exception:
        return
    if list(Draft202012Validator(schema).iter_errors(candidate)):
        return
    with pytest.raises((AssertionError, Exception)):
        frozen_policy(candidate, baseline)


@pytest.fixture(scope="module")
def contract() -> dict[str, Any]:
    return load(CONTRACT_PATH)


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    return load(SCHEMA_PATH)


def test_generated_artifacts_are_reproducible_and_digest_closed(
    contract: dict[str, Any], schema: dict[str, Any]
) -> None:
    rebuilt = build_contract()
    assert contract == rebuilt
    assert schema == build_schema(rebuilt)
    assert contract["contract_sha256"] == canonical_digest(contract)
    assert schema["properties"]["contract_sha256"] == {
        "const": contract["contract_sha256"]
    }


def test_parent_and_population_are_exact(contract: dict[str, Any]) -> None:
    parent = load(PARENT_PATH)
    assert parent["contract_sha256"] == PARENT_DIGEST
    assert contract["parent_binding"]["contract_sha256"] == PARENT_DIGEST
    expected = [*EXACT_ENTRY_POINTS, *EXACT_TRIGGER_FUNCTIONS]
    assert [program["id"] for program in contract["body_programs"]] == expected
    assert [program["kind"] for program in contract["body_programs"][:9]] == [
        "ENTRY_POINT"
    ] * 9
    assert [program["kind"] for program in contract["body_programs"][9:]] == [
        "TRIGGER_FUNCTION"
    ] * 13


def test_schema_and_semantic_validator_accept_exact_candidate(
    contract: dict[str, Any], schema: dict[str, Any]
) -> None:
    Draft202012Validator.check_schema(schema)
    assert list(Draft202012Validator(schema).iter_errors(contract)) == []
    report = assert_contract_valid(contract)
    assert report.valid
    assert report.issues == ()
    derived = derive_contract_semantics(contract)
    assert derived["call_graph"] == contract["call_graph"]
    assert derived["body_summaries"] == {
        program["id"]: program["derived_effect_summary"]
        for program in contract["body_programs"]
    }


def test_schema_is_structural_not_a_whole_program_or_effect_constant(
    schema: dict[str, Any]
) -> None:
    body_schema = schema["$defs"]["body_program"]
    encoded = json.dumps(body_schema, sort_keys=True)
    assert '"ast": {"const"' not in encoded
    assert '"derived_effect_summary": {"const"' not in encoded
    assert '"body_programs": {"const"' not in json.dumps(schema, sort_keys=True)
    assert body_schema["additionalProperties"] is False


def test_privilege_and_unmounted_boundaries_are_closed(contract: dict[str, Any]) -> None:
    roles = {
        role["role"]: role
        for role in contract["effective_parent_summary"]["effective_roles"]
    }
    receiver = roles[PREFIX + "context_admission_receiver"]
    assert receiver["direct_table_dml"] == [
        {"relation": ADMISSION, "privileges": ["INSERT"]}
    ]
    assert RECEIPT in receiver["direct_table_select"]
    assert all("UPDATE" not in grant["privileges"] for grant in receiver["direct_table_dml"])
    owner = roles[PREFIX + "context_schema_owner"]
    assert owner["direct_table_dml"] == []
    assert set(owner["direct_table_select"]) == {
        "public.appointment_command_idempotency",
        "public.appointments",
        "public.appointment_audit_log",
        EVENT,
    }
    assert contract["artifact_boundary"] == {
        "architecture_only": True,
        "unmounted": True,
        "executable_ddl": False,
        "database_contact": False,
        "provider_contact": False,
        "runtime_wiring": False,
        "product_or_patient_data": False,
        "migration_or_source_writes": False,
        "renderer_present": False,
    }


def test_producer_and_admission_freeze_the_required_concurrency_paths(
    contract: dict[str, Any]
) -> None:
    by_id = programs(contract)
    producer = nodes(by_id[PREFIX + "project_update_confirm_reschedule_v1"])
    producer_writes = [
        (node["op"], node["operands"].get("relation"))
        for node in producer
        if node["op"] in {"INSERT", "INSERT_OR_RELOAD_COMPARE", "UPDATE"}
    ]
    assert producer_writes == [
        ("INSERT_OR_RELOAD_COMPARE", ALIAS),
        ("INSERT", OUTBOX),
        ("UPDATE", HEAD),
    ]
    locks = [node["operands"] for node in producer if node["op"] == "LOCK_EXACT"]
    assert [(lock["relation"], lock["ordinal"]) for lock in locks] == [
        (ALIAS, 1),
        (HEAD, 2),
    ]

    admission = nodes(by_id[PREFIX + "admit_proofread_observation_v1"])
    retained_reads = [
        node for node in admission if node["op"] == "SELECT_SET"
    ]
    assert [node["operands"]["relation"] for node in retained_reads[:3]] == [
        ADMISSION,
        ADMISSION,
        RECEIPT,
    ]
    assert retained_reads[-1]["operands"]["relation"] == ADMISSION
    assert all(node["op"] != "LOCK_EXACT" for node in admission)
    admission_winners = [
        node for node in admission if node["op"] == "INSERT_OR_RELOAD_COMPARE"
    ]
    assert len(admission_winners) == 3
    assert all(node["operands"]["relation"] == ADMISSION for node in admission_winners)


def test_retention_uses_real_complete_set_minimum_and_bounded_delete(
    contract: dict[str, Any]
) -> None:
    by_id = programs(contract)
    evaluate = by_id[PREFIX + "evaluate_source_retention_v1"]
    purge = by_id[PREFIX + "purge_source_rows_v1"]
    for program in (evaluate, purge):
        mins = [expr for expr in expressions(program["ast"]) if expr.get("op") == "MIN_FIELD"]
        assert len(mins) == 1
        assert mins[0]["field"] == "last_contiguous_position"
        assert mins[0]["type"] == "pg_catalog.bigint"
    deletes = [node for node in nodes(purge) if node["op"] == "DELETE_SOURCE"]
    assert len(deletes) == 1
    delete = deletes[0]["operands"]
    assert delete["relation"] == OUTBOX
    assert delete["cascade"] is False
    assert delete["max_rows"] > 0
    assert delete["output_type"] == "pg_catalog.bigint"


def test_trigger_population_is_total_read_only_and_row_image_local(
    contract: dict[str, Any]
) -> None:
    declarations = {
        row["function"]: row
        for row in contract["effective_parent_summary"]["trigger_declarations"]
    }
    for program in contract["body_programs"][9:]:
        top = program["ast"]["nodes"]
        assert top[0]["op"] == "ASSERT"
        assert top[1]["op"] == "SWITCH_TG_OP"
        switch = top[1]["operands"]
        assert [arm["tg_op"] for arm in switch["arms"]] == declarations[program["id"]][
            "events"
        ]
        assert switch["default"][0]["op"] == "RAISE"
        summary = program["derived_effect_summary"]
        assert summary["locks"] == []
        assert summary["inserts"] == []
        assert summary["updates"] == []
        assert summary["deletes"] == []
        relation = declarations[program["id"]]["relation"]
        assert all(
            access["relation"] == relation
            for access in summary["row_image_access"]
        )


def _mutate_retarget_outbox(candidate: dict[str, Any]) -> None:
    program = candidate["body_programs"][0]
    target = next(
        node
        for node in nodes(program)
        if node["op"] == "INSERT" and node["operands"]["relation"] == OUTBOX
    )
    target["operands"]["relation"] = ALIAS


def _mutate_remove_head_update(candidate: dict[str, Any]) -> None:
    body_nodes = candidate["body_programs"][0]["ast"]["nodes"]
    body_nodes[:] = [
        node
        for node in body_nodes
        if not (node["op"] == "UPDATE" and node["operands"].get("relation") == HEAD)
    ]


def _mutate_unknown_derivation(candidate: dict[str, Any]) -> None:
    node = next(node for node in nodes(candidate["body_programs"][0]) if node["op"] == "LET")
    node["operands"]["expression"]["op"] = "DERIVE_COLUMN_VALUE"


def _mutate_illegal_trigger_image_relation(candidate: dict[str, Any]) -> None:
    appointment_fence = programs(candidate)[PREFIX + "cf_fence_appointment_update_v1"]
    ref = next(
        expr
        for expr in expressions(appointment_fence["ast"])
        if expr.get("kind") == "TRIGGER_COLUMN"
    )
    ref["relation"] = EVENT


def _mutate_update_returns_old(candidate: dict[str, Any]) -> None:
    guard = programs(candidate)[PREFIX + "cf_guard_claim_v1"]
    switch = guard["ast"]["nodes"][1]["operands"]
    update = next(arm for arm in switch["arms"] if arm["tg_op"] == "UPDATE")
    terminal = next(node for node in walk_nodes(update["nodes"]) if node["op"] == "RETURN_NEW")
    terminal["op"] = "RETURN_OLD"


def _mutate_incomplete_switch(candidate: dict[str, Any]) -> None:
    guard = programs(candidate)[PREFIX + "cf_guard_claim_v1"]
    guard["ast"]["nodes"][1]["operands"]["arms"].pop()


def _mutate_unassigned_result(candidate: dict[str, Any]) -> None:
    transition = programs(candidate)[PREFIX + "apply_durability_transition_v1"]
    terminal = next(node for node in nodes(transition) if node["op"] == "RETURN_COMPOSITE")
    terminal["operands"]["source_symbol"] = "unproduced_result"


def _mutate_admission_persistence_order(candidate: dict[str, Any]) -> None:
    admission = programs(candidate)[PREFIX + "admit_proofread_observation_v1"]
    branch = next(
        node for node in nodes(admission) if node["op"] == "INSERT_OR_RELOAD_COMPARE"
    )
    admission["ast"]["nodes"].insert(4, copy.deepcopy(branch))


def _mutate_remove_audit_old_new_lookup(candidate: dict[str, Any]) -> None:
    audit_fence = programs(candidate)[PREFIX + "cf_fence_audit_v1"]
    switch = audit_fence["ast"]["nodes"][1]["operands"]
    update = next(arm for arm in switch["arms"] if arm["tg_op"] == "UPDATE")
    first_select = next(
        index
        for index, node in enumerate(update["nodes"])
        if node["op"] == "SELECT_SET"
        and node["node_id"].endswith("old-command")
    )
    update["nodes"].pop(first_select)


def _mutate_authored_effect(candidate: dict[str, Any]) -> None:
    candidate["body_programs"][0]["ast"]["nodes"][0]["operands"]["effects"] = [
        "trusted"
    ]


def _mutate_swap_bodies(candidate: dict[str, Any]) -> None:
    candidate["body_programs"][0], candidate["body_programs"][1] = (
        candidate["body_programs"][1],
        candidate["body_programs"][0],
    )


def _mutate_lock_order(candidate: dict[str, Any]) -> None:
    producer_locks = [
        node for node in nodes(candidate["body_programs"][0]) if node["op"] == "LOCK_EXACT"
    ]
    producer_locks[1]["operands"]["ordinal"] = 1


def _mutate_widen_product_read(candidate: dict[str, Any]) -> None:
    producer = candidate["body_programs"][0]
    claim = next(
        node
        for node in nodes(producer)
        if node["op"] == "SELECT_EXACT"
        and node["operands"].get("relation") == "public.appointment_command_idempotency"
    )
    claim["operands"]["columns"].append("actor_user_id")


def _mutate_call_cycle(candidate: dict[str, Any]) -> None:
    call = next(node for node in nodes(candidate["body_programs"][0]) if node["op"] == "CALL_SUPPORT")
    call["operands"]["function"] = PREFIX + "apply_durability_transition_v1"


def _mutate_signature_swap(candidate: dict[str, Any]) -> None:
    entries = candidate["effective_parent_summary"]["effective_signatures"]["entry_points"]
    entries[0], entries[1] = entries[1], entries[0]


def _mutate_declaration_swap(candidate: dict[str, Any]) -> None:
    declarations = candidate["effective_parent_summary"]["trigger_declarations"]
    declarations[0]["events"], declarations[1]["events"] = (
        declarations[1]["events"],
        declarations[0]["events"],
    )


def _mutate_raw_sql(candidate: dict[str, Any]) -> None:
    candidate["body_programs"][0]["ast"]["nodes"][0]["operands"]["sql"] = "SELECT 1"


def _mutate_transaction_control(candidate: dict[str, Any]) -> None:
    candidate["body_programs"][0]["ast"]["nodes"][0]["op"] = "COMMIT"


def _mutate_runtime_authority(candidate: dict[str, Any]) -> None:
    candidate["artifact_boundary"]["runtime_wiring"] = True


@pytest.mark.parametrize(
    "mutate",
    [
        _mutate_retarget_outbox,
        _mutate_remove_head_update,
        _mutate_unknown_derivation,
        _mutate_illegal_trigger_image_relation,
        _mutate_update_returns_old,
        _mutate_incomplete_switch,
        _mutate_unassigned_result,
        _mutate_admission_persistence_order,
        _mutate_remove_audit_old_new_lookup,
        _mutate_authored_effect,
        _mutate_swap_bodies,
        _mutate_lock_order,
        _mutate_widen_product_read,
        _mutate_call_cycle,
        _mutate_signature_swap,
        _mutate_declaration_swap,
        _mutate_raw_sql,
        _mutate_transaction_control,
        _mutate_runtime_authority,
    ],
    ids=lambda function: function.__name__.removeprefix("_mutate_"),
)
def test_mandatory_hostile_mutations_fail_closed(
    contract: dict[str, Any], mutate: Callable[[dict[str, Any]], None]
) -> None:
    rejected_after_refresh(contract, mutate)


def test_stored_effect_or_graph_tampering_is_rejected(contract: dict[str, Any]) -> None:
    candidate = copy.deepcopy(contract)
    candidate["body_programs"][0]["derived_effect_summary"]["updates"] = []
    candidate["contract_sha256"] = canonical_digest(candidate)
    report = validate_contract(candidate)
    assert not report.valid
    assert "summary_mismatch" in {issue.code for issue in report.issues}

    candidate = copy.deepcopy(contract)
    candidate["call_graph"]["edges"] = []
    candidate["contract_sha256"] = canonical_digest(candidate)
    report = validate_contract(candidate)
    assert not report.valid
    assert "call_graph_mismatch" in {issue.code for issue in report.issues}


def test_local_system_xmin_requires_an_explicit_exact_read_projection(
    contract: dict[str, Any],
) -> None:
    candidate = copy.deepcopy(contract)
    fence = programs(candidate)[PREFIX + "cf_fence_stream_head_v1"]
    reload = next(
        node
        for node in nodes(fence)
        if node["node_id"]
        == PREFIX + "cf_fence_stream_head_v1.insert.reload"
    )
    reload["operands"]["columns"].remove("xmin")

    report = validate_contract(candidate)

    assert not report.valid
    assert "xmin_not_selected" in {issue.code for issue in report.issues}
