import json
from pathlib import Path
from typing import Any, Iterator

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder import (
    build_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "architecture-plan.md"
)
RECOVERY = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "architecture-recovery.md"
)
IMPLEMENTATION_RECOVERY = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "architecture-implementation-recovery.md"
)
TYPED_IR_RECOVERY = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "architecture-typed-ir-recovery.md"
)
REGISTRATION_RLS_REBIND = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "registration-rls-parent-rebind.md"
)
ALIAS_LOCK_POLICY_REBIND = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "alias-lock-policy-parent-rebind.md"
)
BINDING_RLS_REBIND = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "admission-receiver-binding-rls-parent-rebind.md"
)
GENERATION_LOCK_RLS_REBIND = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "generation-lock-rls-parent-rebind.md"
)
ADMISSION_LOCK_POLICY_REBIND = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "admission-lock-policy-parent-rebind.md"
)
PARENT = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-migration-"
    "transaction-architecture/migration-transaction-architecture-contract.json"
)
PLAN_PARENT_HASH = (
    "sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8"
)
CURRENT_PARENT_HASH = (
    "sha256:80d5b57eadef0e6ede54c48fc842fe5567723c0a9cdebe288efbf63048c4b3ac"
)


def _plan() -> str:
    return PLAN.read_text(encoding="utf-8")


def _parent() -> dict:
    return json.loads(PARENT.read_text(encoding="utf-8"))


def _recovery() -> str:
    return RECOVERY.read_text(encoding="utf-8")


def _implementation_recovery() -> str:
    return IMPLEMENTATION_RECOVERY.read_text(encoding="utf-8")


def _typed_ir_recovery() -> str:
    return TYPED_IR_RECOVERY.read_text(encoding="utf-8")


def _walk(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _node(contract: dict[str, Any], node_id: str) -> dict[str, Any]:
    matches = [node for node in _walk(contract) if node.get("node_id") == node_id]
    assert len(matches) == 1
    return matches[0]


def _bindings(node: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["column"]: row["value"] for row in node["operands"]["bindings"]}


def test_plan_binds_exact_parent_and_complete_body_population() -> None:
    plan = _plan()
    parent = _parent()

    assert PLAN_PARENT_HASH in plan
    assert "sha256:a79be259" in REGISTRATION_RLS_REBIND.read_text(encoding="utf-8")
    assert "sha256:00a4102f" in ALIAS_LOCK_POLICY_REBIND.read_text(encoding="utf-8")
    assert "sha256:ff64b568" in BINDING_RLS_REBIND.read_text(encoding="utf-8")
    assert "sha256:3ce317803d" in GENERATION_LOCK_RLS_REBIND.read_text(
        encoding="utf-8"
    )
    assert CURRENT_PARENT_HASH in ADMISSION_LOCK_POLICY_REBIND.read_text(
        encoding="utf-8"
    )
    assert parent["contract_sha256"] == CURRENT_PARENT_HASH
    for body in parent["entry_points"] + parent["trigger_function_catalogue"]:
        assert f"`{body['name']}`" in plan
    assert len(parent["entry_points"]) == 9
    assert len(parent["trigger_function_catalogue"]) == 13
    assert parent["function_body_boundary"]["entry_point_body_sql_present"] is False
    assert (
        parent["function_body_boundary"]["trigger_function_body_sql_present"] is False
    )


def test_plan_uses_closed_programs_and_exact_effect_rederivation() -> None:
    plan = "\n".join((_plan(), _recovery())).lower()
    for phrase in (
        "body_program_v1",
        "pl/pgsql prose",
        "finite allowlist",
        "no free-form statement field",
        "effect summary must be mechanically rederived",
        "call graph is acyclic",
        "no dynamic/generic execution path",
        "standard retryable postgresql sqlstates remain unaltered",
        "does not perform that lowering",
        "trigger context",
        "system `xmin`",
        "return_new`/`return_old`/`return_null",
        "unique insert followed by winner reload/compare",
    ):
        assert phrase in plan


def test_plan_preserves_api_spine_and_data_authority_boundaries() -> None:
    plan = " ".join(_plan().split())
    for phrase in (
        "GraphQL remains read-only and unchanged",
        "REST/OpenAPI remains the only command plane and gains no operation",
        "events and the future payload-free outbox remain observations",
        "No `app/**`, `alembic/**`, `docs/diary/**`, `docs/api-spine/**`",
        "Patient/product/protected/historical-PHI data: none",
        "Provider/model/external retrieval: none",
        "Database/source/network/browser contact: none",
        "docs/branding",
    ):
        assert phrase in plan


def test_recovery_closes_effective_parent_and_trigger_feasibility() -> None:
    recovery = " ".join(_recovery().split())
    for phrase in (
        "`structural_feasibility_recovery_v1`",
        "It does not rewrite the accepted parent artifact",
        "One stream per active service binding",
        "`public.appointment_command_idempotency`",
        "`context_admission_receiver` adds exact `SELECT`",
        "`durability_transition_result_v1`",
        "`initial_key_interval future_key_interval_v1`",
        "`terminal_reason generation_terminal_reason`",
        "`source_retention_reason`",
        "No locked product revision is invented",
        "a reused alias is an older immutable exact",
        "Exact trigger applicability and return matrix",
        "check-in remains outside",
        "Every deferred fence is read-only, lock-free, sibling-call-free",
        "second same-transaction appointment update",
    ):
        assert phrase in recovery


def test_implementation_recovery_requires_genuinely_lowerable_typed_bodies() -> None:
    recovery = " ".join(_implementation_recovery().split())
    for phrase in (
        "Rejected uncommitted candidate digest",
        "machine-lowerable bodies",
        "discriminated `instruction_node_v1` objects",
        "Expressions are discriminated nodes, never free strings",
        "full ordered signature objects",
        "`pg_catalog.trigger`",
        "column-minimal reads, locks and writes",
        "structured `{from,to}` objects",
        "ordered `prefixItems` or body-specific `const` definitions",
        "candidate-independent exact-head veto",
    ):
        assert phrase in recovery


def test_typed_ir_recovery_replaces_misbound_candidate_with_derived_semantics() -> None:
    recovery = " ".join(_typed_ir_recovery().split())
    for phrase in (
        "Rejected typed candidate content digest",
        "Predicates, derivation profiles, body programs, effects and call graph are rebuilt from zero",
        "one deterministic offline contract builder under `scripts/`",
        "no `PROFILE_EVAL`, `DERIVE_COLUMN_VALUE`, unproduced control fact",
        "No local effect field exists on an instruction node",
        "definite symbol assignment and use",
        "per-`TG_OP` legal `OLD`/`NEW` access",
        "Admission lock feasibility correction",
        "receives no `UPDATE` privilege",
        "Construction cohorts",
        "`COMPOSITE_CONSTRUCT` binds every field",
        "bounded affected-row count",
        "typed `MIN_FIELD`",
        "`SELECT_SET` assigns `<qualified-relation>[]`",
        "outbox insert retargeted to the alias relation",
        "creates no SQL, DDL, migration",
    ):
        assert phrase in recovery


def test_plan_keeps_ddl_and_database_execution_in_later_gates() -> None:
    plan = _plan()
    for phrase in (
        "emits no `CREATE`, `ALTER`,",
        "This tranche does not perform that lowering",
        "It will not create, render, parse through",
        "Only after independent acceptance may a separate provider-free unmounted inert",
        "Applied local migration",
        "database-backed execution",
        "operational credentials",
        "live source/product",
    ):
        assert phrase in plan


def test_admission_row_shapes_match_the_structural_check_constraint() -> None:
    contract = build_contract()
    prefix = "emr4_context_fabric.admit_proofread_observation_v1"
    outcome_fields = {
        "observation_digest",
        "decision",
        "reason_code",
        "affected_frame_mask",
        "checkpoint_disposition",
    }

    primary = _bindings(_node(contract, prefix + ".insert_primary"))
    assert primary["entry_kind"]["value"] == "PRIMARY"
    assert all(primary[field]["op"] == "FIELD" for field in outcome_fields)
    assert primary["attempted_admission_digest"] == {
        "op": "CONST",
        "type": "emr4_context_fabric.digest_sha256",
        "value": None,
    }
    assert primary["conflict_reason"]["value"] is None

    for suffix in ("insert_mismatch", "insert_reuse"):
        conflict = _bindings(_node(contract, prefix + "." + suffix))
        assert conflict["entry_kind"]["value"] == "CONFLICT"
        assert all(
            conflict[field]["op"] == "CONST" and conflict[field]["value"] is None
            for field in outcome_fields
        )
        assert conflict["attempted_admission_digest"]["op"] == "CANONICAL_DIGEST"
        assert conflict["conflict_reason"]["value"] is not None


def test_insert_reload_winner_predicates_use_is_null_for_typed_nulls() -> None:
    contract = build_contract()
    insert_nodes = [
        node for node in _walk(contract) if node.get("op") == "INSERT_OR_RELOAD_COMPARE"
    ]
    assert insert_nodes

    for insert in insert_nodes:
        null_binding_columns = {
            row["column"]
            for row in insert["operands"]["bindings"]
            if row["value"].get("op") == "CONST" and row["value"].get("value") is None
        }
        null_predicate_columns = {
            predicate["operand"]["column"]
            for predicate in _walk(insert["operands"]["winner_predicate"])
            if predicate.get("op") == "IS_NULL"
        }
        assert null_predicate_columns == null_binding_columns
        assert not any(
            predicate.get("op") == "EQ"
            and predicate.get("right", {}).get("op") == "CONST"
            and predicate.get("right", {}).get("value") is None
            for predicate in _walk(insert["operands"]["winner_predicate"])
        )
