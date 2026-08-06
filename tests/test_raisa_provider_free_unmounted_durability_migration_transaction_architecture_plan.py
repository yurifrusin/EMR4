import ast
import copy
import hashlib
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
THREAT = (
    ROOT / "docs/security" / PLAN.name.replace("-plan.md", "-threat-model-delta.md")
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


def function_node(path: Path, name: str) -> ast.FunctionDef:
    module = ast.parse(text(path))
    return next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def canonical_contract_digest(contract: dict) -> str:
    payload = copy.deepcopy(contract)
    payload.pop("contract_sha256")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_machine_contract(contract: dict) -> None:
    schema = data(CONTRACT_SCHEMA)
    Draft202012Validator(schema).validate(contract)
    assert contract["contract_sha256"] == canonical_contract_digest(contract)


def relation_map(contract: dict) -> dict[str, dict]:
    return {
        relation["name"]: relation
        for relation in contract["relation_catalogue"]["relations"]
    }


def column_names(relation: dict) -> set[str]:
    return {column.split(":", 1)[0] for column in relation["columns"]}


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


def test_postgresql_16_provenance_and_temporal_obligation_are_exact() -> None:
    contract = data(CONTRACT)
    target = contract["postgresql_target"]
    expected_expression = (
        "((((pg_current_xact_id()::text)::bigint & 4294967295)::text)::xid)"
    )
    assert target == {
        "major": 16,
        "producer_isolation": "READ COMMITTED",
        "coordinator_isolation": "SERIALIZABLE",
        "retention_isolation": "SERIALIZABLE",
        "top_level_xid32_expression": expected_expression,
        "tuple_provenance_predicate": f"xmin = {expected_expression}",
        "savepoints_allowed": False,
        "subtransactions_allowed": False,
        "caller_supplied_xid": False,
        "stored_xid": False,
        "retained_xid": False,
        "xid_is_durability_position": False,
        "wrap_freeze_policy": (
            "active_top_level_only_zero_legacy_no_committed_in_progress"
        ),
    }
    model = contract["existing_model_contract"]
    assert model["temporal_transition_columns"] == [
        "start_time",
        "duration_minutes",
    ]
    assert model["temporal_obligation_sql"] == (
        "OLD.start_time IS DISTINCT FROM NEW.start_time OR "
        "OLD.duration_minutes IS DISTINCT FROM NEW.duration_minutes"
    )
    assert model["nested_transaction_calls_allowed"] is False

    joined = " ".join("\n".join((text(PLAN), text(DESIGN))).lower().split())
    for phrase in (
        "savepoints",
        "session.begin_nested()",
        "subtransaction",
        "text-to-`xid` cast",
        "old.start_time is distinct from new.start_time",
        "old.duration_minutes is distinct from new.duration_minutes",
        "non-temporal update-confirm",
        "insert-then-delete",
    ):
        assert phrase in joined


def test_relation_catalogue_has_exact_names_columns_keys_rls_and_retention() -> None:
    contract = data(CONTRACT)
    relations = contract["relation_catalogue"]["relations"]
    expected_names = [
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
    ]
    assert contract["relation_catalogue"]["count"] == 18
    assert [relation["name"] for relation in relations] == expected_names

    for relation in relations:
        columns = column_names(relation)
        assert "practice_id" in columns
        assert relation["primary_key"]
        assert set(relation["primary_key"]).issubset(columns)
        assert len(relation["columns"]) == len(columns)
        assert relation["rls"]
        assert relation["mutation"]
        assert relation["retention_family"] in {
            "source",
            "receipt_checkpoint",
            "audit",
            "none",
        }
        assert all("CASCADE" not in fk for fk in relation["foreign_keys"])

    expected_retention = {
        "diary_context_observation_outbox_v1": "source",
        "context_proofread_observation_admission": "receipt_checkpoint",
        "context_observer_generation": "receipt_checkpoint",
        "context_durability_checkpoint": "receipt_checkpoint",
        "context_recovery_anchor": "receipt_checkpoint",
        "context_classified_observation_receipt": "receipt_checkpoint",
        "context_frame_generation": "receipt_checkpoint",
        "context_invalidation_watermark": "receipt_checkpoint",
        "context_reassembly_obligation": "receipt_checkpoint",
        "context_durability_lifecycle": "receipt_checkpoint",
        "context_durability_audit": "audit",
        "context_observation_key_interval": "receipt_checkpoint",
    }
    mapped = relation_map(contract)
    assert {
        name: mapped[name]["retention_family"] for name in expected_retention
    } == expected_retention


def test_admission_alias_anchor_key_and_retention_contracts_are_structural() -> None:
    mapped = relation_map(data(CONTRACT))
    alias = mapped["diary_context_aggregate_aliases_v1"]
    assert alias["primary_key"] == [
        "practice_id",
        "source_contract_id",
        "product_appointment_uuid",
    ]
    assert alias["unique_keys"] == [
        [
            "practice_id",
            "source_contract_id",
            "opaque_aggregate_alias",
        ]
    ]
    assert alias["mutation"] == "insert_only_no_update_no_delete"
    assert alias["retention_family"] == "none"

    admission = mapped["context_proofread_observation_admission"]
    assert admission["primary_key"][-2:] == ["source_position", "entry_kind"]
    assert admission["mutation"] == "insert_only_max_one_primary_one_conflict"
    assert any("PRIMARY requires" in item for item in admission["checks"])
    assert any("CONFLICT requires" in item for item in admission["checks"])

    anchor = mapped["context_recovery_anchor"]
    assert anchor["mutation"] == "insert_only_no_update_no_delete"
    assert "checkpoint_integrity_digest" in column_names(anchor)
    assert "anchor_digest" in column_names(anchor)

    interval = mapped["context_observation_key_interval"]
    assert any("gap_free" in item for item in interval["checks"])
    assert any("future_fenced" in item for item in interval["checks"])
    assert interval["mutation"] == ("insert_only_future_interval_no_historical_edit")

    policy = mapped["context_retention_policy"]
    assert any(
        "retention_execution_enabled = false" in item for item in policy["checks"]
    )


def test_role_entry_point_and_rls_matrix_is_closed() -> None:
    contract = data(CONTRACT)
    roles = contract["role_matrix"]
    assert [row["role"] for row in roles] == [
        "context_schema_owner",
        "context_producer",
        "context_observer",
        "context_admission_receiver",
        "context_coordinator",
        "context_lifecycle",
        "context_retention",
        "context_application_read",
    ]
    assert roles[0]["login"] is False
    assert roles[0]["owns_objects"] is True
    for row in roles:
        assert row["noinherit"] is True
        assert row["nobypassrls"] is True
        assert row["direct_table_dml"] == []
        if row["role"] != "context_schema_owner":
            assert row["owns_objects"] is False

    entry_points = contract["entry_points"]
    assert [entry["name"] for entry in entry_points] == [
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
    for entry in entry_points:
        assert entry["security_definer"] is True
        assert entry["fixed_search_path"] is True
        assert entry["dynamic_sql"] is False
        assert entry["public_execute"] is False
        assert entry["authority_source"]

    producer = next(row for row in roles if row["role"] == "context_producer")
    assert producer["execute_entry_points"] == ["project_update_confirm_reschedule_v1"]
    assert producer["direct_table_select"] == []


def test_trigger_surface_closes_insert_update_delete_and_no_event_paths() -> None:
    trigger_surface = data(CONTRACT)["trigger_surface"]
    actual = [
        (
            trigger["table"],
            trigger["timing"],
            tuple(trigger["events"]),
            trigger["deferrable"],
            trigger.get("initially_deferred"),
        )
        for trigger in trigger_surface
    ]
    assert actual == [
        (
            "appointment_command_idempotency",
            "BEFORE",
            ("UPDATE", "DELETE"),
            False,
            None,
        ),
        (
            "appointment_command_idempotency",
            "AFTER",
            ("INSERT", "UPDATE", "DELETE"),
            True,
            True,
        ),
        (
            "appointments",
            "AFTER",
            ("UPDATE OF start_time,duration_minutes",),
            True,
            True,
        ),
        ("appointment_audit_log", "BEFORE", ("UPDATE", "DELETE"), False, None),
        ("appointment_audit_log", "AFTER", ("INSERT", "UPDATE", "DELETE"), True, True),
        ("diary_committed_events", "BEFORE", ("UPDATE", "DELETE"), False, None),
        ("diary_committed_events", "AFTER", ("INSERT", "UPDATE", "DELETE"), True, True),
        (
            "diary_context_aggregate_aliases_v1",
            "BEFORE",
            ("UPDATE", "DELETE"),
            False,
            None,
        ),
        (
            "diary_context_aggregate_aliases_v1",
            "AFTER",
            ("INSERT", "UPDATE", "DELETE"),
            True,
            True,
        ),
        (
            "context_observation_stream_head",
            "BEFORE",
            ("UPDATE", "DELETE"),
            False,
            None,
        ),
        (
            "context_observation_stream_head",
            "AFTER",
            ("INSERT", "UPDATE", "DELETE"),
            True,
            True,
        ),
        (
            "diary_context_observation_outbox_v1",
            "BEFORE",
            ("UPDATE", "DELETE"),
            False,
            None,
        ),
        (
            "diary_context_observation_outbox_v1",
            "AFTER",
            ("INSERT", "UPDATE", "DELETE"),
            True,
            True,
        ),
    ]
    assert any(
        trigger["table"] == "appointments"
        and "non-temporal projection absence" in trigger["purpose"]
        for trigger in trigger_surface
    )


def test_machine_contract_schema_and_canonical_digest_are_exact() -> None:
    contract = data(CONTRACT)
    schema = data(CONTRACT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    validate_machine_contract(contract)
    assert (
        schema["properties"]["contract_sha256"]["const"]
        == (contract["contract_sha256"])
    )

    boundary = contract["artifact_boundary"]
    for artifact in boundary["core_owned_artifacts"]:
        assert (ROOT / artifact).exists()
        assert not any(
            artifact.startswith(prefix) for prefix in boundary["forbidden_prefixes"]
        )
    assert boundary["executable_ddl"] is False
    assert boundary["database_contact"] is False
    assert boundary["provider_contact"] is False
    assert boundary["runtime_wiring"] is False
    assert boundary["product_data_processed"] is False


def test_existing_models_match_exact_foreign_keys_checks_and_defaults() -> None:
    contract = data(CONTRACT)["existing_model_contract"]
    appointment_model = ROOT / "app/models/appointments.py"
    event_model = ROOT / "app/models/diary_events.py"
    idem = class_node(appointment_model, "AppointmentCommandIdempotency")
    audit = class_node(appointment_model, "AppointmentAuditLog")
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
        nullable = next(
            keyword for keyword in call.keywords if keyword.arg == "nullable"
        )
        assert isinstance(nullable.value, ast.Constant)
        assert nullable.value.value is True

    created = idem_assignments[contract["claim_created_at_field"]]
    server_default = next(
        keyword for keyword in created.keywords if keyword.arg == "server_default"
    )
    assert isinstance(server_default.value, ast.Call)
    assert call_name(server_default.value) == "now"

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
    assert {("command_id",), ("audit_log_id",)}.issubset(unique_fields)

    foreign_keys = [
        call for call in event_calls if call_name(call) == "ForeignKeyConstraint"
    ]
    for key in (
        "event_command_foreign_key",
        "event_appointment_foreign_key",
        "event_audit_foreign_key",
    ):
        expected = contract[key]
        assert any(
            [item.value for item in call.args[0].elts] == expected["columns"]
            and [item.value for item in call.args[1].elts]
            == [
                f"{expected['references_table']}.{column}"
                for column in expected["references_columns"]
            ]
            for call in foreign_keys
            if isinstance(call.args[0], (ast.List, ast.Tuple))
            and isinstance(call.args[1], (ast.List, ast.Tuple))
        )

    check_text = " ".join(
        arg.value
        for call in event_calls
        if call_name(call) == "CheckConstraint"
        for arg in call.args
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
    )
    assert contract["event_type"] in check_text
    assert contract["event_schema_version"] in check_text

    audit_calls = [node for node in ast.walk(audit) if isinstance(node, ast.Call)]
    assert any(
        call_name(call) == "ForeignKeyConstraint"
        and [item.value for item in call.args[0].elts]
        == contract["audit_practice_command_key"]
        for call in audit_calls
        if len(call.args) >= 2 and isinstance(call.args[0], (ast.List, ast.Tuple))
    )


def test_update_confirm_source_flow_is_one_session_ordered_and_not_nested() -> None:
    contract = data(CONTRACT)["existing_model_contract"]
    router_path = ROOT / "app/routers/appointments.py"
    service_path = ROOT / "app/services/appointment_idempotency.py"
    route = function_node(router_path, "confirm_update_proposal_route")
    router_lines = text(router_path).splitlines()
    route_source = "\n".join(router_lines[route.lineno - 1 : route.end_lineno])
    positions = [
        route_source.index("claim_appointment_command("),
        route_source.index(".with_for_update()"),
        route_source.index("confirm_update_proposal("),
        route_source.index("AppointmentAuditLog.command_id"),
        route_source.index("complete_appointment_command("),
        route_source.index("db.commit()"),
    ]
    assert positions == sorted(positions)
    assert f'_UPDATE_CONFIRM_OPERATION_ID = "{contract["operation_id"]}"' in text(
        router_path
    )
    assert f'_UPDATE_CONFIRM_ROUTE_FAMILY = "{contract["route_family"]}"' in text(
        router_path
    )
    service_lines = text(service_path).splitlines()
    service_source = []
    for function_name in (
        "claim_appointment_command",
        "complete_appointment_command",
    ):
        function = function_node(service_path, function_name)
        service_source.append(
            "\n".join(service_lines[function.lineno - 1 : function.end_lineno])
        )
    combined = (route_source + "\n" + "\n".join(service_source)).lower()
    assert "begin_nested" not in combined
    assert "savepoint" not in combined
    assert "rollback to" not in combined
    assert "record.target_appointment_id = target_appointment_id" in combined
    assert "record.audit_log_id = audit_log_id" in combined


def test_machine_contract_rejects_adversarial_architecture_mutations() -> None:
    contract = data(CONTRACT)
    mutations: list[dict] = []

    def mutate(path: tuple[object, ...], value: object) -> None:
        candidate = copy.deepcopy(contract)
        target: object = candidate
        for part in path[:-1]:
            target = target[part]  # type: ignore[index]
        target[path[-1]] = value  # type: ignore[index]
        mutations.append(candidate)

    candidate = copy.deepcopy(contract)
    candidate["relation_catalogue"]["relations"].append(
        copy.deepcopy(candidate["relation_catalogue"]["relations"][-1])
    )
    mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["relation_catalogue"]["relations"].pop()
    mutations.append(candidate)
    mutate(("postgresql_target", "major"), 17)
    mutate(("postgresql_target", "top_level_xid32_expression"), "xmin")
    mutate(("postgresql_target", "savepoints_allowed"), True)
    mutate(("postgresql_target", "stored_xid"), True)
    mutate(
        ("existing_model_contract", "temporal_transition_columns"),
        ["start_time", "duration_minutes", "practitioner_id"],
    )
    mutate(
        ("existing_model_contract", "route_call_order"),
        list(reversed(contract["existing_model_contract"]["route_call_order"])),
    )
    mutate(
        ("relation_catalogue", "relations", 0, "columns", 0),
        "practice_id:text:not_null",
    )
    mutate(
        ("relation_catalogue", "relations", 1, "primary_key"),
        ["product_appointment_uuid"],
    )
    mutate(("relation_catalogue", "relations", 1, "unique_keys"), [])
    mutate(("relation_catalogue", "relations", 1, "mutation"), "delete_allowed")
    mutate(
        ("relation_catalogue", "relations", 2, "foreign_keys"),
        ["raw_event_uuid->diary_committed_events.id:CASCADE"],
    )
    mutate(("relation_catalogue", "relations", 3, "checks"), ["PRIMARY only"])
    mutate(("relation_catalogue", "relations", 7, "mutation"), "update_allowed")
    mutate(
        ("relation_catalogue", "relations", 14, "checks"),
        ["interval_end > interval_start"],
    )
    mutate(("relation_catalogue", "relations", 17, "checks"), ["all durations >= 0"])
    mutate(("role_matrix", 1, "direct_table_dml"), ["INSERT"])
    mutate(("role_matrix", 4, "nobypassrls"), False)
    mutate(("entry_points", 0, "public_execute"), True)
    mutate(("entry_points", 1, "dynamic_sql"), True)
    mutate(("entry_points", 2, "input"), ["decision_packet:jsonb"])
    mutate(("trigger_surface", 2, "events"), ["UPDATE"])
    mutate(("trigger_surface", 5, "events"), ["UPDATE"])
    mutate(("trigger_surface", 12, "deferrable"), False)
    candidate = copy.deepcopy(contract)
    candidate["cross_relation_invariants"].pop()
    mutations.append(candidate)
    mutate(("artifact_boundary", "forbidden_prefixes"), ["alembic/"])
    mutate(("artifact_boundary", "core_owned_artifacts", 0), "app/runtime.py")
    mutate(("artifact_boundary", "database_contact"), True)
    mutate(("artifact_boundary", "product_data_processed"), True)

    for candidate in mutations:
        with pytest.raises((ValidationError, AssertionError)):
            validate_machine_contract(candidate)


def test_cross_relation_invariants_and_claim_boundary_remain_fail_closed() -> None:
    contract = data(CONTRACT)
    joined = " ".join(contract["cross_relation_invariants"]).lower()
    for phrase in (
        "non-null practice_id",
        "never cascade",
        "one primary",
        "admission locator",
        "before optional source",
        "lifecycle-owned anchor",
        "gap-free",
        "generation-local",
        "retention families are independent",
        "complete non-consumed census",
        "false by default",
        "never grant fresh read or command authority",
    ):
        assert phrase in joined

    plan = " ".join(text(PLAN).lower().split())
    for phrase in (
        "disposable local database",
        "this architecture tranche itself performs none",
        "provider-free unmounted authored-synthetic migration/ddl rehearsal",
        "no applied migration",
        "no executable ddl",
    ):
        assert phrase in plan
