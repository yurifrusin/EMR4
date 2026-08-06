import ast
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-migration-transaction-"
    "architecture-plan.md"
)
DESIGN = PLAN.parent / PLAN.name.replace("-plan.md", "-design.md")
THREAT = ROOT / "docs/security" / PLAN.name.replace(
    "-plan.md", "-threat-model-delta.md"
)
CONTRACT_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "migration-transaction-architecture"
)
CONTRACT = CONTRACT_DIR / "migration-transaction-architecture-contract.json"
CONTRACT_SCHEMA = CONTRACT_DIR / (
    "migration-transaction-architecture-contract.schema.json"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def data(path: Path) -> dict:
    return json.loads(text(path))


def class_node(path: Path, name: str) -> ast.ClassDef:
    module = ast.parse(text(path))
    return next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == name
    )


def call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def test_architecture_plan_has_exact_api_and_non_authority_boundary() -> None:
    joined = "\n".join((text(PLAN), text(DESIGN), text(THREAT))).lower()
    for phrase in (
        "internal async durability architecture only",
        "graphql remains read-only and unchanged",
        "rest/openapi remains the only command plane and gains no operation",
        "existing staff committed-event get route",
        "no subscription",
        "event-triggered fresh read",
        "not executable ddl",
        "no `app/**`",
        "`alembic/**`",
        "database/source/network/provider contact",
        "creates no",
        "no protected evidence",
        "cryptographic authenticity",
    ):
        assert phrase in joined


def test_future_relation_catalogue_is_exact_and_closed() -> None:
    plan = text(PLAN)
    expected = (
        "context_observation_stream_head",
        "diary_context_aggregate_aliases_v1",
        "diary_context_observation_outbox_v1",
        "context_proofread_observation_admission",
        "context_generation_registry_barrier",
        "context_observer_generation",
        "context_durability_checkpoint",
        "context_recovery_anchor",
        "context_classified_observation_receipt",
        "context_frame_generation",
        "context_invalidation_watermark",
        "context_reassembly_obligation",
        "context_durability_lifecycle",
        "context_durability_audit",
        "context_observation_key_interval",
        "context_recovery_pin",
        "context_service_practice_binding",
        "context_retention_policy",
    )
    for relation in expected:
        assert f"`{relation}`" in plan
    for phrase in (
        "json/jsonb",
        "unbounded text",
        "arrays",
        "raw product uuid",
        "no generic work queue or event store",
        "source-row deletion never cascades",
    ):
        assert phrase in plan.lower()


def test_owner_private_alias_bridge_is_the_only_product_identifier_exception() -> None:
    joined = " ".join(
        "\n".join((text(PLAN), text(DESIGN), text(THREAT))).lower().split()
    )
    assert "sole product-identifier exception" in joined
    for phrase in (
        "(practice_id, source_contract_id, product_appointment_uuid)",
        "no runtime principal receives direct table dml",
        "receive neither `select` nor the product id",
        "never copied into the outbox",
        "not governed by the three durability retention families",
        "update and deletion are prohibited",
        "reverse uniqueness",
        "caller cannot supply the alias",
        "no separately executable alias helper",
        "exact `in_progress` update-confirm claim",
        "practice-scoped `(practice_id, command_id)` foreign key",
        "unique `command_id` constraint",
        "loads the sole event by command id",
        "one logical capability and one `session_user`",
        "cross-appointment collision",
        "delete/recreate",
        "new separately reviewed migration/contract descendant and source epoch",
        "never cascades",
        "only the opaque alias enters the outbox",
        "no actual product identifier is present or processed in this "
        "architecture-only tranche",
    ):
        assert phrase in joined


def test_authority_binding_and_transactions_are_fail_closed() -> None:
    joined = " ".join("\n".join((text(PLAN), text(DESIGN))).lower().split())
    for phrase in (
        "session_user",
        "exactly one active",
        "connection pool",
        "may not multiplex",
        "caller-set",
        "custom guc",
        "force rls",
        "noinherit",
        "nobypassrls",
        "fixed schema-qualified search path",
        "no dynamic sql",
        "public",
        "read committed",
        "serializable",
        "for update",
        "same transaction",
        "one logical capability and one `session_user`",
        "loads the sole event by command id",
        "on conflict do nothing",
        "at most three attempts",
        "new_generation_required",
        "rebase_required",
        "retention_execution_enabled: false",
        "producer neither holds the observer key",
        "only the complete stored admission set",
        "never accepts a caller-supplied decision packet",
        "source-membership digest",
        "at most one `primary` plus at most one `conflict`",
        "complete stored admission set",
        "any retained `conflict` sentinel",
        "later conflicting attempts cannot grow storage without bound",
        "concurrent first attempts race",
        "`on conflict do nothing` is not an outcome",
        "sufficient only for fail-closed rebase",
        "next lifecycle transition",
        "exact anchor",
        "receiver-owned immutable `primary` or `conflict` admission appends may continue",
        "coordinator cannot consume the next admission",
    ):
        assert phrase in joined


def test_continuity_and_retention_reject_unsafe_shortcuts() -> None:
    joined = "\n".join((text(PLAN), text(THREAT))).lower()
    for phrase in (
        "postgresql sequences/identities",
        "uuid/time ordering",
        "aggregate_revision",
        "wal lsn",
        "complete non-consumed generation census",
        "registration/rebaseline and purge",
        "three independent retention families",
        "caller cannot supply/filter the census",
        "one immutable total-order journal",
        "decision` and `key_rotation`",
        "bucket from canonical admitted audit history",
        "generation-local metadata",
        "changes no other generation",
    ):
        assert phrase in joined


def test_database_backed_acceptance_is_future_and_adversarial() -> None:
    plan = " ".join(text(PLAN).lower().split())
    for phrase in (
        "disposable local database",
        "authored synthetic opaque coordinates only",
        "rollback after every producer member",
        "concurrent same-stream producers",
        "concurrent coordinators",
        "after authorized source-row",
        "remains visible after source purge",
        "bounds the position to at most two admission rows",
        "without blocking bounded receiver-owned admission appends",
        "post-decision and post-rotation anchors",
        "lifecycle append",
        "cross-practice reads",
        "caller-set practice guc",
        "every non-producer principal and every durability output",
        "v1 bridge update/deletion is prohibited",
        "direct projection invocation",
        "one immutable alias",
        "incomplete/filtered census",
        "disabled mode performs zero connection",
        "this architecture tranche itself performs none",
        "authored-synthetic migration/ddl rehearsal",
    ):
        assert phrase in plan


def test_machine_contract_validates_and_has_exact_artifact_surface() -> None:
    contract = data(CONTRACT)
    schema = data(CONTRACT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)

    assert contract["relation_catalogue"]["count"] == 18
    assert len(contract["relation_catalogue"]["names"]) == 18
    assert len(set(contract["relation_catalogue"]["names"])) == 18

    boundary = contract["artifact_boundary"]
    for artifact in boundary["owned_artifacts"]:
        assert (ROOT / artifact).exists()
        assert not any(
            artifact.startswith(prefix) for prefix in boundary["forbidden_prefixes"]
        )
    assert boundary["executable_ddl"] is False
    assert boundary["database_contact"] is False
    assert boundary["provider_contact"] is False
    assert boundary["runtime_wiring"] is False


def test_existing_idempotency_and_event_constraints_match_machine_contract() -> None:
    contract = data(CONTRACT)["existing_model_contract"]
    appointment_model = ROOT / "app/models/appointments.py"
    event_model = ROOT / "app/models/diary_events.py"
    idem = class_node(appointment_model, "AppointmentCommandIdempotency")
    event = class_node(event_model, "DiaryCommittedEvent")

    idem_assignments = {
        target.id: node.value
        for node in idem.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance((target := node.targets[0]), ast.Name)
    }
    for field in (contract["target_binding_field"], contract["audit_binding_field"]):
        call = idem_assignments[field]
        assert isinstance(call, ast.Call)
        assert call_name(call) == "Column"
        nullable = next(keyword for keyword in call.keywords if keyword.arg == "nullable")
        assert isinstance(nullable.value, ast.Constant)
        assert nullable.value.value is True

    event_calls = [node for node in ast.walk(event) if isinstance(node, ast.Call)]
    unique_fields = {
        tuple(
            arg.value
            for arg in call.args
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
        )
        for call in event_calls
        if call_name(call) == "UniqueConstraint"
    }
    assert ("command_id",) in unique_fields
    assert ("audit_log_id",) in unique_fields

    foreign_keys = [
        call for call in event_calls if call_name(call) == "ForeignKeyConstraint"
    ]
    assert any(
        isinstance(call.args[0], (ast.List, ast.Tuple))
        and [item.value for item in call.args[0].elts]
        == contract["event_command_foreign_key"]
        for call in foreign_keys
    )

    router = text(ROOT / "app/routers/appointments.py")
    assert f'_UPDATE_CONFIRM_OPERATION_ID = "{contract["operation_id"]}"' in router
    assert f'_UPDATE_CONFIRM_ROUTE_FAMILY = "{contract["route_family"]}"' in router
    service = text(ROOT / "app/services/appointment_idempotency.py")
    assert "record.target_appointment_id = target_appointment_id" in service
    assert "record.audit_log_id = audit_log_id" in service


def test_transaction_provenance_and_commit_fence_are_machine_closed() -> None:
    producer = data(CONTRACT)["producer_transaction"]
    provenance = producer["transaction_provenance"]
    assert provenance == {
        "database_xid_function": "pg_current_xact_id()",
        "tuple_system_column": "xmin",
        "required_current_transaction_tuples": [
            "idempotency_claim",
            "appointment_current_tuple",
            "appointment_audit",
            "diary_committed_event",
        ],
        "claim_inserted_in_current_transaction": True,
        "immutable_claim_created_at_equals_transaction_timestamp": True,
        "caller_supplied": False,
        "stored_in_user_column": False,
        "retained_after_commit": False,
        "durability_position_authority": False,
    }
    fence = producer["deferred_commit_fence"]
    assert fence["constraint_mode"] == "DEFERRABLE INITIALLY DEFERRED"
    assert fence["bidirectional"] is True
    assert fence["runtime_execute"] is False
    assert fence["in_progress_event_commit_forbidden"] is True
    assert fence["in_progress_claim_commit_forbidden"] is True
    assert fence["prior_transaction_claim_adoption_forbidden"] is True
    assert fence["required_atomic_members"] == [
        "appointment_mutation",
        "appointment_audit",
        "diary_committed_event",
        "first_alias_if_needed",
        "stream_head_advance",
        "payload_free_outbox",
        "idempotency_completion",
    ]


def test_machine_contract_rejects_adversarial_architecture_mutations() -> None:
    contract = data(CONTRACT)
    validator = Draft202012Validator(data(CONTRACT_SCHEMA))
    mutations: list[dict] = []

    candidate = copy.deepcopy(contract)
    candidate["relation_catalogue"]["names"].append("generic_work_queue")
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["relation_catalogue"]["names"].pop()
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["existing_model_contract"]["operation_id"] = "genericUpdate"
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["producer_transaction"]["transaction_provenance"]["caller_supplied"] = True
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["producer_transaction"]["transaction_provenance"]["retained_after_commit"] = True
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["producer_transaction"]["transaction_provenance"]["required_current_transaction_tuples"].pop()
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["producer_transaction"]["deferred_commit_fence"]["bidirectional"] = False
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["producer_transaction"]["deferred_commit_fence"]["in_progress_claim_commit_forbidden"] = False
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["producer_transaction"]["deferred_commit_fence"]["required_atomic_members"].pop()
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["alias_bridge"]["reverse_unique_key"].pop()
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["alias_bridge"]["delete_allowed"] = True
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["artifact_boundary"]["owned_artifacts"][0] = "app/runtime.py"
    mutations.append(candidate)

    for candidate in mutations:
        with pytest.raises(ValidationError):
            validator.validate(candidate)
