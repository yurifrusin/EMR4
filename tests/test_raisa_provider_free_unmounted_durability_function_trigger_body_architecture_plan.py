import json
from pathlib import Path


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
PARENT = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-migration-"
    "transaction-architecture/migration-transaction-architecture-contract.json"
)
PARENT_HASH = "sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8"


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
        "Construction cohorts",
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
