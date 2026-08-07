import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "architecture-plan.md"
)
PARENT = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-migration-"
    "transaction-architecture/migration-transaction-architecture-contract.json"
)
PARENT_HASH = "sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8"


def _plan() -> str:
    return PLAN.read_text(encoding="utf-8")


def _parent() -> dict:
    return json.loads(PARENT.read_text(encoding="utf-8"))


def test_plan_binds_exact_parent_and_complete_body_population() -> None:
    plan = _plan()
    parent = _parent()

    assert PARENT_HASH in plan
    assert parent["contract_sha256"] == PARENT_HASH
    for body in parent["entry_points"] + parent["trigger_function_catalogue"]:
        assert f"`{body['name']}`" in plan
    assert len(parent["entry_points"]) == 9
    assert len(parent["trigger_function_catalogue"]) == 13
    assert parent["function_body_boundary"]["entry_point_body_sql_present"] is False
    assert (
        parent["function_body_boundary"]["trigger_function_body_sql_present"] is False
    )


def test_plan_uses_closed_programs_and_exact_effect_rederivation() -> None:
    plan = _plan().lower()
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
    ):
        assert phrase in plan


def test_plan_preserves_api_spine_and_data_authority_boundaries() -> None:
    plan = _plan()
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
