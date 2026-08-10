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

EXPECTED_RELATIONS = [
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
EXPECTED_ENUMS = {
    "admission_entry_kind": ["PRIMARY", "CONFLICT"],
    "observation_decision": [
        "ADMIT_SELECTIVE",
        "ADMIT_NO_INTERSECTION",
        "ADMIT_FULL_INVALIDATION",
        "REBASE_REQUIRED",
    ],
    "observation_reason": [
        "RELEVANT_INTERSECTION",
        "NO_INTERSECTION",
        "FULL_SCOPE",
        "COVERAGE_GAP",
        "SAME_POSITION_MISMATCH",
        "DIGEST_REUSE",
        "WRONG_PREDECESSOR",
        "WRONG_EPOCH",
        "MISSING_ADMISSION",
        "KEY_UNAVAILABLE",
        "MALFORMED_OR_FOREIGN",
    ],
    "checkpoint_disposition": ["ADVANCE", "HOLD_REBASE", "STOP_GENERATION"],
    "admission_conflict_reason": [
        "POSITION_DIGEST_MISMATCH",
        "OBSERVATION_DIGEST_REUSE",
    ],
    "generation_state": ["ACTIVE", "REBASE_REQUIRED", "REVOKED", "CONSUMED"],
    "checkpoint_state": ["ACTIVE", "REBASE_REQUIRED", "REVOKED", "CONSUMED"],
    "frame_type": [
        "CURRENT_DIARY_PROJECTION",
        "CURRENT_WAITING_ROOM_PROJECTION",
    ],
    "frame_lifecycle": ["CURRENT", "RETIRED"],
    "obligation_count_bucket": ["ONE", "TWO_TO_FOUR", "FIVE_PLUS"],
    "obligation_state": ["PENDING", "COMPLETED"],
    "lifecycle_entry_kind": ["DECISION", "KEY_ROTATION"],
    "retention_family": ["SOURCE", "RECEIPT_CHECKPOINT", "AUDIT"],
    "recovery_pin_reason": [
        "RECOVERY",
        "AUDIT_REVIEW",
        "KEY_OVERLAP",
        "LEGAL_HOLD",
    ],
    "recovery_pin_state": ["ACTIVE", "RELEASED"],
    "logical_capability": [
        "PRODUCER",
        "OBSERVER",
        "COORDINATOR",
        "LIFECYCLE",
        "RETENTION",
        "APPLICATION_READ",
    ],
    "generation_terminal_reason": [
        "REVOKED",
        "CONTINUITY_LOSS",
        "KEY_LOSS",
        "DISABLED",
    ],
}
EXPECTED_BINDING_SELECT_POLICY = (
    "(current_user = 'context_schema_owner'::name OR "
    "current_user = 'context_admission_receiver'::name) AND "
    "database_login = session_user AND "
    "active_from <= transaction_timestamp() AND "
    "(active_until IS NULL OR active_until > transaction_timestamp())"
)
EXPECTED_ANCHOR_LOCK_POLICY = (
    "emr4_context_fabric.session_binding_allows_v1(session_user, "
    "ARRAY['COORDINATOR'::emr4_context_fabric.logical_capability, "
    "'LIFECYCLE'::emr4_context_fabric.logical_capability], "
    "practice_id, source_contract_id, transaction_timestamp())"
)
EXPECTED_ADMISSION_LOCK_POLICY = (
    "emr4_context_fabric.session_binding_allows_v1(session_user, "
    "ARRAY['COORDINATOR'::emr4_context_fabric.logical_capability], "
    "practice_id, source_contract_id, transaction_timestamp())"
)
EXPECTED_OUTBOX_SELECT_POLICY = (
    "emr4_context_fabric.session_binding_allows_v1(session_user, "
    "ARRAY['PRODUCER'::emr4_context_fabric.logical_capability, "
    "'OBSERVER'::emr4_context_fabric.logical_capability, "
    "'COORDINATOR'::emr4_context_fabric.logical_capability, "
    "'RETENTION'::emr4_context_fabric.logical_capability], "
    "practice_id, source_contract_id, transaction_timestamp())"
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


def reseal_contract(contract: dict) -> dict:
    contract["contract_sha256"] = canonical_contract_digest(contract)
    return contract


def relation_map(contract: dict) -> dict[str, dict]:
    return {
        relation["name"]: relation
        for relation in contract["relation_catalogue"]["relations"]
    }


def column_names(relation: dict) -> set[str]:
    return {column["name"] for column in relation["columns"]}


def declared_type_names(contract: dict) -> set[str]:
    catalogue = contract["type_catalogue"]
    return {
        *catalogue["builtins"],
        *(item["name"] for item in catalogue["domains"]),
        *(item["name"] for item in catalogue["enums"]),
        *(item["name"] for item in catalogue["composites"]),
    }


def base_type(type_name: str) -> str:
    return type_name.removesuffix("[]")


def validate_renderer_semantics(contract: dict) -> None:
    assert contract["schema_version"].endswith(".v3")
    target = contract["postgresql_target"]
    assert target["major"] == 16
    assert target["savepoint_application_contract"] == "FORBIDDEN"
    assert target["savepoint_without_relevant_tuple_database_detectable"] is False
    assert target["subtransaction_authored_relevant_tuple_database_detectable"] is True
    assert target["subtransactions_allowed"] is False
    assert target["stored_xid"] is False
    assert target["xid_is_durability_position"] is False

    catalogue = contract["type_catalogue"]
    assert catalogue["schema_name"] == "emr4_context_fabric"
    assert {item["name"]: item["values"] for item in catalogue["enums"]} == (
        EXPECTED_ENUMS
    )
    assert all(item["check_sql"] for item in catalogue["domains"])
    known_types = declared_type_names(contract)

    relations = contract["relation_catalogue"]["relations"]
    assert contract["relation_catalogue"]["count"] == 18
    assert contract["relation_catalogue"]["all_unlisted_column_defaults"] == (
        "NO DEFAULT"
    )
    assert [relation["name"] for relation in relations] == EXPECTED_RELATIONS
    mapped = relation_map(contract)
    relation_names = set(mapped)

    constraint_names: set[str] = set()
    for relation in relations:
        columns = relation["columns"]
        assert columns
        assert all(
            set(column) == {"name", "data_type", "nullable", "default_sql"}
            for column in columns
        )
        assert len({column["name"] for column in columns}) == len(columns)
        assert all(column["default_sql"] is None for column in columns)
        assert all(base_type(column["data_type"]) in known_types for column in columns)
        names = column_names(relation)
        assert "practice_id" in names

        primary = relation["primary_key"]
        assert primary["name"] not in constraint_names
        constraint_names.add(primary["name"])
        assert primary["columns"]
        assert set(primary["columns"]).issubset(names)
        assert "practice_id" in primary["columns"] or relation["name"] == (
            "context_service_practice_binding"
        )

        for unique in relation["unique_constraints"]:
            assert unique["name"] not in constraint_names
            constraint_names.add(unique["name"])
            assert unique["kind"] in {"UNIQUE_CONSTRAINT", "UNIQUE_INDEX"}
            assert unique["columns"]
            assert set(unique["columns"]).issubset(names)
            if unique["kind"] == "UNIQUE_INDEX":
                assert unique["predicate_sql"]
            else:
                assert unique["predicate_sql"] is None

        for foreign_key in relation["foreign_keys"]:
            assert foreign_key["name"] not in constraint_names
            constraint_names.add(foreign_key["name"])
            assert set(foreign_key["columns"]).issubset(names)
            assert foreign_key["on_delete"] in {"RESTRICT", "NO ACTION"}
            assert foreign_key["on_delete"] != "CASCADE"
            target_relation = foreign_key["references_relation"]
            assert target_relation in relation_names or target_relation in {
                "appointments",
                "appointment_command_idempotency",
                "appointment_audit_log",
            }
            if target_relation in relation_names:
                assert set(foreign_key["references_columns"]).issubset(
                    column_names(mapped[target_relation])
                )

        for check in relation["check_constraints"]:
            assert check["name"] not in constraint_names
            constraint_names.add(check["name"])
            sql = check["expression_sql"]
            assert sql
            assert not any(
                phrase in sql.lower()
                for phrase in (
                    " requires ",
                    " iff ",
                    " derived ",
                    "gap_free",
                    "linked lifecycle",
                )
            )

        assert relation["rls_enabled"] is True
        assert relation["rls_forced"] is True
        assert relation["rls_policy_ids"]
        assert relation["invariant_enforcement_ids"]
        assert relation["retention_family"] in {
            "source",
            "receipt_checkpoint",
            "audit",
            "none",
        }

    outbox = mapped["diary_context_observation_outbox_v1"]
    assert all(
        foreign_key["references_relation"] != "diary_committed_events"
        for foreign_key in outbox["foreign_keys"]
    )
    assert (
        contract["existing_model_contract"]["event_row_persistent_dependency_allowed"]
        is False
    )
    assert (
        contract["existing_model_contract"][
            "event_physical_retention_owned_by_this_contract"
        ]
        is False
    )
    assert (
        contract["existing_model_contract"][
            "outbox_survives_event_expiry_or_later_authorized_deletion"
        ]
        is True
    )

    policies = {
        policy["id"]: policy for policy in contract["rls_policy_catalogue"]["policies"]
    }
    assert len(policies) == len(contract["rls_policy_catalogue"]["policies"])
    for relation in relations:
        assert set(relation["rls_policy_ids"]).issubset(policies)
        for policy_id in relation["rls_policy_ids"]:
            policy = policies[policy_id]
            assert policy["relation"] == relation["name"]
            assert policy["command"] in {"SELECT", "INSERT", "UPDATE", "DELETE"}
            assert policy["roles"] == ["PUBLIC"]
            assert policy["permissive"] is True
            predicates = [
                item
                for item in (policy["using_sql"], policy["with_check_sql"])
                if item is not None
            ]
            assert predicates
            if relation["name"] == "context_service_practice_binding":
                assert "database_login = session_user" in predicates[0]
            else:
                assert all(
                    "session_binding_allows_v1(session_user" in item
                    and "practice_id" in item
                    and "source_contract_id" in item
                    for item in predicates
                )
    assert contract["rls_policy_catalogue"]["deny_when_no_applicable_policy"] is True
    assert contract["rls_policy_catalogue"]["public_privileges_revoked"] is True
    assert policies["pol_cf_17_select"] == {
        "id": "pol_cf_17_select",
        "relation": "context_service_practice_binding",
        "command": "SELECT",
        "roles": ["PUBLIC"],
        "permissive": True,
        "using_sql": EXPECTED_BINDING_SELECT_POLICY,
        "with_check_sql": None,
    }
    lifecycle = "'LIFECYCLE'::emr4_context_fabric.logical_capability"
    assert lifecycle in policies["pol_cf_01_select"]["using_sql"]
    assert lifecycle in policies["pol_cf_01_insert"]["with_check_sql"]
    assert lifecycle in policies["pol_cf_01_update"]["using_sql"]
    assert lifecycle not in policies["pol_cf_01_update"]["with_check_sql"]
    producer = (
        "emr4_context_fabric.session_binding_allows_v1(session_user, "
        "ARRAY['PRODUCER'::emr4_context_fabric.logical_capability], "
        "practice_id, source_contract_id, transaction_timestamp())"
    )
    assert "pol_cf_02_update_lock" in policies
    alias_lock = policies["pol_cf_02_update_lock"]
    assert alias_lock["command"] == "UPDATE"
    assert alias_lock["using_sql"] == producer
    assert alias_lock["with_check_sql"] == producer + " AND FALSE"
    outbox_select = policies["pol_cf_03_select"]
    assert outbox_select == {
        "id": "pol_cf_03_select",
        "relation": "diary_context_observation_outbox_v1",
        "command": "SELECT",
        "roles": ["PUBLIC"],
        "permissive": True,
        "using_sql": EXPECTED_OUTBOX_SELECT_POLICY,
        "with_check_sql": None,
    }
    admission = mapped["context_proofread_observation_admission"]
    assert admission["rls_policy_ids"] == [
        "pol_cf_04_select",
        "pol_cf_04_insert",
        "pol_cf_04_update_lock",
    ]
    admission_lock = policies["pol_cf_04_update_lock"]
    assert admission_lock == {
        "id": "pol_cf_04_update_lock",
        "relation": "context_proofread_observation_admission",
        "command": "UPDATE",
        "roles": ["PUBLIC"],
        "permissive": True,
        "using_sql": EXPECTED_ADMISSION_LOCK_POLICY,
        "with_check_sql": EXPECTED_ADMISSION_LOCK_POLICY + " AND FALSE",
    }
    anchor = mapped["context_recovery_anchor"]
    assert anchor["rls_policy_ids"] == [
        "pol_cf_08_select",
        "pol_cf_08_insert",
        "pol_cf_08_update_lock",
    ]
    anchor_lock = policies["pol_cf_08_update_lock"]
    assert anchor_lock == {
        "id": "pol_cf_08_update_lock",
        "relation": "context_recovery_anchor",
        "command": "UPDATE",
        "roles": ["PUBLIC"],
        "permissive": True,
        "using_sql": EXPECTED_ANCHOR_LOCK_POLICY,
        "with_check_sql": EXPECTED_ANCHOR_LOCK_POLICY + " AND FALSE",
    }
    coordinator = "'COORDINATOR'::emr4_context_fabric.logical_capability"
    generation_update = policies["pol_cf_06_update"]
    assert coordinator in generation_update["using_sql"]
    assert coordinator in generation_update["with_check_sql"]
    assert lifecycle in generation_update["using_sql"]
    assert lifecycle in generation_update["with_check_sql"]
    for policy_id in ("pol_cf_10_update", "pol_cf_11_update"):
        assert lifecycle not in policies[policy_id]["using_sql"]
        assert lifecycle not in policies[policy_id]["with_check_sql"]

    roles = {role["role"]: role for role in contract["role_matrix"]}
    assert set(roles) == {
        "context_schema_owner",
        "context_producer",
        "context_observer",
        "context_admission_receiver",
        "context_coordinator",
        "context_lifecycle",
        "context_retention",
        "context_application_read",
    }
    for role in roles.values():
        assert role["noinherit"] is True
        assert role["nobypassrls"] is True
        assert role["createrole"] is False
        assert role["createdb"] is False
        assert role["replication"] is False
        if role["runtime_role"]:
            assert role["direct_table_dml"] == []
    assert roles["context_coordinator"]["direct_table_select"] == []
    admission_owner = roles["context_admission_receiver"]
    assert admission_owner["login"] is False
    assert admission_owner["runtime_role"] is False
    assert admission_owner["owns_relations"] == []
    assert admission_owner["owns_functions"] == ["admit_proofread_observation_v1"]
    assert admission_owner["owner_inherent_relation_privileges"] is False
    assert admission_owner["direct_table_select"] == [
        "diary_context_observation_outbox_v1",
        "context_proofread_observation_admission",
        "context_observer_generation",
        "context_durability_checkpoint",
        "context_classified_observation_receipt",
        "context_observation_key_interval",
    ]
    assert admission_owner["direct_table_dml"] == [
        {
            "relation": "context_proofread_observation_admission",
            "privileges": ["INSERT"],
        }
    ]
    assert admission_owner["execute_entry_points"] == []

    body_boundary = contract["function_body_boundary"]
    assert body_boundary == {
        "catalogue_mode": "SIGNATURE_AND_INVARIANT_BINDING_ONLY",
        "entry_point_body_sql_present": False,
        "trigger_function_body_sql_present": False,
        "structural_renderer_must_omit_entry_points": True,
        "structural_renderer_must_omit_trigger_functions": True,
        "structural_renderer_must_omit_trigger_declarations": True,
        "structural_renderer_must_omit_execute_grants": True,
        "execute_grants_effective_before_body_gate": False,
        "support_function_exception": "session_binding_allows_v1",
        "support_function_may_render_only_with_no_runtime_bindings": True,
        "next_required_gate": (
            "provider_free_unmounted_function_and_trigger_body_architecture"
        ),
        "ddl_rehearsal_blocked_until_next_gate_passes": True,
        "renderer_invention_forbidden": True,
    }

    entry_points = {entry["name"]: entry for entry in contract["entry_points"]}
    support = {function["name"]: function for function in contract["support_functions"]}
    trigger_functions = {
        function["name"]: function
        for function in contract["trigger_function_catalogue"]
    }
    function_names = {*entry_points, *support, *trigger_functions}
    for entry in entry_points.values():
        owner = roles[entry["owner"]]
        assert entry["name"] in owner["owns_functions"]
        assert entry["security_definer"] is True
        assert entry["search_path_sql"] == "pg_catalog, emr4_context_fabric"
        assert entry["dynamic_sql"] is False
        assert entry["public_execute"] is False
        assert entry["language"] == "plpgsql"
        assert entry["output"]["cardinality"] == "ONE"
        assert base_type(entry["output"]["data_type"]) in (known_types | relation_names)
        for argument in entry["inputs"]:
            assert argument["mode"] == "IN"
            assert base_type(argument["data_type"]) in known_types
        assert entry["invariant_ids"]
        assert "body_sql" not in entry

    helper = support["session_binding_allows_v1"]
    assert helper["output"] == {"data_type": "boolean", "cardinality": "ONE"}
    assert "count(*) = 1" in helper["body_sql"]
    assert "binding.database_login = session_user" in helper["body_sql"]
    assert set(support) == {body_boundary["support_function_exception"]}

    triggers = contract["trigger_surface"]
    appointment_trigger = next(
        trigger for trigger in triggers if trigger["table"] == "appointments"
    )
    assert appointment_trigger["events"] == ["UPDATE"]
    assert appointment_trigger["deferrable"] is True
    assert appointment_trigger["initially_deferred"] is True
    assert appointment_trigger["function"] == "cf_fence_appointment_update_v1"
    for trigger in triggers:
        assert trigger["row_level"] is True
        assert trigger["function"] in trigger_functions
        assert trigger_functions[trigger["function"]]["returns"] == "trigger"
        assert trigger["invariant_ids"]
        assert "body_sql" not in trigger_functions[trigger["function"]]

    invariants = {
        item["id"]: item for item in contract["invariant_enforcement_catalogue"]
    }
    assert len(invariants) == len(contract["invariant_enforcement_catalogue"])
    assert contract["cross_relation_invariants"] == list(invariants)
    valid_enforcers = function_names | constraint_names | set(invariants)
    for relation in relations:
        assert set(relation["invariant_enforcement_ids"]).issubset(invariants)
    for item in invariants.values():
        assert item["predicate"]
        assert item["enforced_by"]
        assert set(item["enforced_by"]).issubset(valid_enforcers)
    assert "event_retention_independence_v1" in invariants
    assert "producer_temporal_bijection_v1" in invariants
    assert "savepoint with no relevant tuple is not observable" in (
        invariants["current_xid_provenance_v1"]["predicate"].lower()
    )


def validate_machine_contract(contract: dict) -> None:
    schema = data(CONTRACT_SCHEMA)
    Draft202012Validator(schema).validate(contract)
    validate_renderer_semantics(contract)
    assert contract["contract_sha256"] == canonical_contract_digest(contract)


def semantic_schema_without_digest_const() -> dict:
    schema = copy.deepcopy(data(CONTRACT_SCHEMA))
    schema["properties"]["contract_sha256"] = {
        "type": "string",
        "pattern": "^sha256:[0-9a-f]{64}$",
    }
    return schema


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


def test_postgresql_16_provenance_savepoint_claim_and_temporal_rule_are_exact() -> None:
    contract = data(CONTRACT)
    target = contract["postgresql_target"]
    expected_expression = (
        "((((pg_current_xact_id()::text)::bigint & 4294967295)::text)::xid)"
    )
    assert target["top_level_xid32_expression"] == expected_expression
    assert target["tuple_provenance_predicate"] == f"xmin = {expected_expression}"
    assert target["savepoint_application_contract"] == "FORBIDDEN"
    assert target["savepoint_without_relevant_tuple_database_detectable"] is False
    assert target["subtransaction_authored_relevant_tuple_database_detectable"] is True
    model = contract["existing_model_contract"]
    assert model["temporal_transition_columns"] == [
        "start_time",
        "duration_minutes",
    ]
    assert model["appointment_trigger_event"] == "UPDATE"
    assert model["temporal_obligation_sql"] == (
        "OLD.start_time IS DISTINCT FROM NEW.start_time OR "
        "OLD.duration_minutes IS DISTINCT FROM NEW.duration_minutes"
    )
    assert model["nested_transaction_calls_allowed"] is False

    joined = " ".join("\n".join((text(PLAN), text(DESIGN))).lower().split())
    for phrase in (
        "session.begin_nested()",
        "subtransaction-authored",
        "no-write savepoint",
        "not database-observable",
        "text-to-`xid` cast",
        "old.start_time is distinct from new.start_time",
        "old.duration_minutes is distinct from new.duration_minutes",
        "all-`update`",
        "non-temporal update-confirm",
        "insert-then-delete",
    ):
        assert phrase in joined


def test_structural_catalogue_is_closed_and_function_body_rendering_is_denied() -> None:
    validate_renderer_semantics(data(CONTRACT))


def test_admission_owner_has_exact_internal_privileges() -> None:
    contract = data(CONTRACT)
    roles = {row["role"]: row for row in contract["role_matrix"]}
    owner = roles["context_admission_receiver"]
    assert owner["login"] is False
    assert owner["runtime_role"] is False
    assert owner["owns_relations"] == []
    assert owner["owns_functions"] == ["admit_proofread_observation_v1"]
    assert owner["owner_inherent_relation_privileges"] is False
    assert owner["direct_table_select"] == [
        "diary_context_observation_outbox_v1",
        "context_proofread_observation_admission",
        "context_observer_generation",
        "context_durability_checkpoint",
        "context_classified_observation_receipt",
        "context_observation_key_interval",
    ]
    assert owner["direct_table_dml"] == [
        {
            "relation": "context_proofread_observation_admission",
            "privileges": ["INSERT"],
        }
    ]
    assert owner["execute_entry_points"] == []
    entry = next(
        item
        for item in contract["entry_points"]
        if item["name"] == "admit_proofread_observation_v1"
    )
    assert entry["owner"] == "context_admission_receiver"
    assert entry["output"]["data_type"] == ("context_proofread_observation_admission")
    assert [item["data_type"] for item in entry["inputs"]] == [
        "generation_locator_v1",
        "bigint",
        "proofread_packet_v1",
    ]


def test_binding_select_rls_retains_exact_owner_pair_and_session_time_fences() -> None:
    contract = data(CONTRACT)
    policies = {
        policy["id"]: policy for policy in contract["rls_policy_catalogue"]["policies"]
    }
    assert policies["pol_cf_17_select"]["using_sql"] == (EXPECTED_BINDING_SELECT_POLICY)

    roles = {role["role"]: role for role in contract["role_matrix"]}
    for owner in ("context_schema_owner", "context_admission_receiver"):
        assert roles[owner]["login"] is False
        assert roles[owner]["noinherit"] is True
        assert roles[owner]["nobypassrls"] is True
    assert roles["context_admission_receiver"]["owns_functions"] == [
        "admit_proofread_observation_v1"
    ]
    assert (
        "context_service_practice_binding"
        not in roles["context_observer"]["direct_table_select"]
    )

    unsafe_predicates = (
        EXPECTED_BINDING_SELECT_POLICY.replace(
            " OR current_user = 'context_admission_receiver'::name", ""
        ),
        EXPECTED_BINDING_SELECT_POLICY.replace(
            "current_user = 'context_admission_receiver'::name",
            "(current_user = 'context_admission_receiver'::name OR "
            "current_user = 'context_observer'::name)",
        ),
        EXPECTED_BINDING_SELECT_POLICY.replace(
            "database_login = session_user AND ", ""
        ),
        EXPECTED_BINDING_SELECT_POLICY.replace(
            "active_from <= transaction_timestamp() AND ", ""
        ),
        EXPECTED_BINDING_SELECT_POLICY.replace(
            " AND (active_until IS NULL OR active_until > transaction_timestamp())",
            "",
        ),
    )
    for predicate in unsafe_predicates:
        candidate = copy.deepcopy(contract)
        policy = next(
            item
            for item in candidate["rls_policy_catalogue"]["policies"]
            if item["id"] == "pol_cf_17_select"
        )
        policy["using_sql"] = predicate
        with pytest.raises(AssertionError):
            validate_renderer_semantics(reseal_contract(candidate))


def test_all_update_trigger_enforces_positive_and_negative_temporal_obligation() -> (
    None
):
    contract = data(CONTRACT)
    trigger = next(
        item
        for item in contract["trigger_surface"]
        if item["name"] == "trg_cf_appointment_fence"
    )
    assert trigger["events"] == ["UPDATE"]
    assert trigger["function"] == "cf_fence_appointment_update_v1"
    invariant = next(
        item
        for item in contract["invariant_enforcement_catalogue"]
        if item["id"] == "producer_temporal_bijection_v1"
    )
    assert "OLD.start_time IS DISTINCT FROM NEW.start_time" in invariant["predicate"]
    assert "false requires their absence" in invariant["predicate"]
    assert trigger["function"] in invariant["enforced_by"]


def test_outbox_is_transaction_bound_but_physically_event_independent() -> None:
    contract = data(CONTRACT)
    outbox = relation_map(contract)["diary_context_observation_outbox_v1"]
    assert "raw_event_uuid" in column_names(outbox)
    assert all(
        key["references_relation"] != "diary_committed_events"
        for key in outbox["foreign_keys"]
    )
    invariant = next(
        item
        for item in contract["invariant_enforcement_catalogue"]
        if item["id"] == "event_retention_independence_v1"
    )
    assert "no persistent foreign key" in invariant["predicate"]
    assert "later product-event expiry" in invariant["predicate"]


def test_exact_schema_and_canonical_digest_pass() -> None:
    contract = data(CONTRACT)
    schema = data(CONTRACT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    validate_machine_contract(contract)
    assert (
        schema["properties"]["contract_sha256"]["const"]
        == (contract["contract_sha256"])
    )
    assert (
        schema["properties"]["relation_catalogue"]["const"]
        == (contract["relation_catalogue"])
    )
    assert (
        schema["properties"]["type_catalogue"]["const"] == (contract["type_catalogue"])
    )
    assert (
        schema["properties"]["rls_policy_catalogue"]["const"]
        == (contract["rls_policy_catalogue"])
    )
    assert (
        schema["properties"]["function_body_boundary"]["const"]
        == contract["function_body_boundary"]
    )


def test_generation_registration_rls_covers_only_its_initial_projection_effects() -> (
    None
):
    contract = data(CONTRACT)
    policies = {
        policy["id"]: policy for policy in contract["rls_policy_catalogue"]["policies"]
    }
    lifecycle = "'LIFECYCLE'::emr4_context_fabric.logical_capability"

    expected_lifecycle_predicates = {
        "pol_cf_01_select": "using_sql",
        "pol_cf_01_insert": "with_check_sql",
        "pol_cf_01_update": "using_sql",
        "pol_cf_10_select": "using_sql",
        "pol_cf_10_insert": "with_check_sql",
        "pol_cf_11_select": "using_sql",
        "pol_cf_11_insert": "with_check_sql",
    }
    for policy_id, predicate_field in expected_lifecycle_predicates.items():
        assert lifecycle in policies[policy_id][predicate_field]

    # PostgreSQL applies UPDATE USING policy visibility to SELECT FOR UPDATE.
    # Lifecycle may therefore lock an existing stream head during registration,
    # while producer-only WITH CHECK and zero direct DML keep mutation closed.
    assert lifecycle not in policies["pol_cf_01_update"]["with_check_sql"]
    for policy_id in ("pol_cf_10_update", "pol_cf_11_update"):
        assert lifecycle not in policies[policy_id]["using_sql"]
        assert lifecycle not in policies[policy_id]["with_check_sql"]

    roles = {role["role"]: role for role in contract["role_matrix"]}
    lifecycle_role = roles["context_lifecycle"]
    assert lifecycle_role["direct_table_dml"] == []
    assert lifecycle_role["direct_table_select"] == []
    assert "register_observer_generation_v1" in lifecycle_role["execute_entry_points"]


def test_stream_head_lock_visibility_cannot_be_removed_or_widened_to_mutation() -> None:
    contract = data(CONTRACT)
    lifecycle = ", 'LIFECYCLE'::emr4_context_fabric.logical_capability"

    missing_lock_visibility = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in missing_lock_visibility["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_01_update"]["using_sql"] = policies["pol_cf_01_update"][
        "using_sql"
    ].replace(lifecycle, "")
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(missing_lock_visibility))

    widened_write_check = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in widened_write_check["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_01_update"]["with_check_sql"] = policies["pol_cf_01_update"][
        "with_check_sql"
    ].replace(
        "'PRODUCER'::emr4_context_fabric.logical_capability",
        "'PRODUCER'::emr4_context_fabric.logical_capability" + lifecycle,
    )
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(widened_write_check))


def test_coordinator_generation_lock_and_transition_visibility_cannot_be_removed() -> (
    None
):
    contract = data(CONTRACT)
    coordinator = "'COORDINATOR'::emr4_context_fabric.logical_capability, "

    for predicate_field in ("using_sql", "with_check_sql"):
        candidate = copy.deepcopy(contract)
        policies = {
            policy["id"]: policy
            for policy in candidate["rls_policy_catalogue"]["policies"]
        }
        policies["pol_cf_06_update"][predicate_field] = policies["pol_cf_06_update"][
            predicate_field
        ].replace(coordinator, "")
        with pytest.raises(AssertionError):
            validate_renderer_semantics(reseal_contract(candidate))

    roles = {role["role"]: role for role in contract["role_matrix"]}
    assert roles["context_coordinator"]["direct_table_dml"] == []
    assert roles["context_coordinator"]["direct_table_select"] == []
    assert roles["context_coordinator"]["execute_entry_points"] == [
        "apply_durability_transition_v1"
    ]


def test_alias_lock_visibility_cannot_be_removed_or_widened_to_mutation() -> None:
    contract = data(CONTRACT)
    policies = {
        policy["id"]: policy for policy in contract["rls_policy_catalogue"]["policies"]
    }
    alias = relation_map(contract)["diary_context_aggregate_aliases_v1"]
    assert alias["rls_policy_ids"] == [
        "pol_cf_02_select",
        "pol_cf_02_insert",
        "pol_cf_02_update_lock",
    ]
    assert policies["pol_cf_02_update_lock"]["with_check_sql"].endswith(" AND FALSE")
    roles = {role["role"]: role for role in contract["role_matrix"]}
    assert roles["context_producer"]["direct_table_dml"] == []

    missing_lock_visibility = copy.deepcopy(contract)
    missing_lock_visibility["rls_policy_catalogue"]["policies"] = [
        policy
        for policy in missing_lock_visibility["rls_policy_catalogue"]["policies"]
        if policy["id"] != "pol_cf_02_update_lock"
    ]
    relation_map(missing_lock_visibility)["diary_context_aggregate_aliases_v1"][
        "rls_policy_ids"
    ].remove("pol_cf_02_update_lock")
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(missing_lock_visibility))

    widened_write_check = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in widened_write_check["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_02_update_lock"]["with_check_sql"] = policies[
        "pol_cf_02_update_lock"
    ]["using_sql"]
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(widened_write_check))

    foreign_lock_visibility = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in foreign_lock_visibility["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_02_update_lock"]["using_sql"] = policies["pol_cf_02_update_lock"][
        "using_sql"
    ].replace("'PRODUCER'", "'OBSERVER'")
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(foreign_lock_visibility))


def test_anchor_lock_visibility_cannot_be_removed_widened_or_reassigned() -> None:
    contract = data(CONTRACT)
    policies = {
        policy["id"]: policy for policy in contract["rls_policy_catalogue"]["policies"]
    }
    anchor = relation_map(contract)["context_recovery_anchor"]
    assert anchor["rls_policy_ids"] == [
        "pol_cf_08_select",
        "pol_cf_08_insert",
        "pol_cf_08_update_lock",
    ]
    assert policies["pol_cf_08_update_lock"]["using_sql"] == (
        EXPECTED_ANCHOR_LOCK_POLICY
    )
    assert policies["pol_cf_08_update_lock"]["with_check_sql"] == (
        EXPECTED_ANCHOR_LOCK_POLICY + " AND FALSE"
    )

    missing_lock_visibility = copy.deepcopy(contract)
    missing_lock_visibility["rls_policy_catalogue"]["policies"] = [
        policy
        for policy in missing_lock_visibility["rls_policy_catalogue"]["policies"]
        if policy["id"] != "pol_cf_08_update_lock"
    ]
    relation_map(missing_lock_visibility)["context_recovery_anchor"][
        "rls_policy_ids"
    ].remove("pol_cf_08_update_lock")
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(missing_lock_visibility))

    widened_write_check = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in widened_write_check["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_08_update_lock"]["with_check_sql"] = policies[
        "pol_cf_08_update_lock"
    ]["using_sql"]
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(widened_write_check))

    foreign_capability = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in foreign_capability["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_08_update_lock"]["using_sql"] = policies[
        "pol_cf_08_update_lock"
    ]["using_sql"].replace("'LIFECYCLE'", "'RETENTION'")
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(foreign_capability))

    non_public = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in non_public["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_08_update_lock"]["roles"] = ["context_coordinator"]
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(non_public))


def test_admission_lock_visibility_cannot_be_removed_widened_or_reassigned() -> None:
    contract = data(CONTRACT)
    policies = {
        policy["id"]: policy for policy in contract["rls_policy_catalogue"]["policies"]
    }
    admission = relation_map(contract)["context_proofread_observation_admission"]
    assert admission["rls_policy_ids"] == [
        "pol_cf_04_select",
        "pol_cf_04_insert",
        "pol_cf_04_update_lock",
    ]
    assert policies["pol_cf_04_update_lock"]["using_sql"] == (
        EXPECTED_ADMISSION_LOCK_POLICY
    )
    assert policies["pol_cf_04_update_lock"]["with_check_sql"] == (
        EXPECTED_ADMISSION_LOCK_POLICY + " AND FALSE"
    )

    missing_lock_visibility = copy.deepcopy(contract)
    missing_lock_visibility["rls_policy_catalogue"]["policies"] = [
        policy
        for policy in missing_lock_visibility["rls_policy_catalogue"]["policies"]
        if policy["id"] != "pol_cf_04_update_lock"
    ]
    relation_map(missing_lock_visibility)["context_proofread_observation_admission"][
        "rls_policy_ids"
    ].remove("pol_cf_04_update_lock")
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(missing_lock_visibility))

    widened_write_check = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in widened_write_check["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_04_update_lock"]["with_check_sql"] = policies[
        "pol_cf_04_update_lock"
    ]["using_sql"]
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(widened_write_check))

    foreign_capability = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in foreign_capability["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_04_update_lock"]["using_sql"] = policies[
        "pol_cf_04_update_lock"
    ]["using_sql"].replace("'COORDINATOR'", "'OBSERVER'")
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(foreign_capability))

    non_public = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in non_public["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_04_update_lock"]["roles"] = ["context_coordinator"]
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(non_public))


def test_outbox_coordinator_select_visibility_cannot_be_removed_or_widened() -> None:
    contract = data(CONTRACT)
    policies = {
        policy["id"]: policy for policy in contract["rls_policy_catalogue"]["policies"]
    }
    assert policies["pol_cf_03_select"]["using_sql"] == EXPECTED_OUTBOX_SELECT_POLICY

    missing_coordinator = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in missing_coordinator["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_03_select"]["using_sql"] = policies["pol_cf_03_select"][
        "using_sql"
    ].replace(
        ", 'COORDINATOR'::emr4_context_fabric.logical_capability",
        "",
    )
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(missing_coordinator))

    widened_application = copy.deepcopy(contract)
    policies = {
        policy["id"]: policy
        for policy in widened_application["rls_policy_catalogue"]["policies"]
    }
    policies["pol_cf_03_select"]["using_sql"] = policies["pol_cf_03_select"][
        "using_sql"
    ].replace(
        "'RETENTION'::emr4_context_fabric.logical_capability]",
        "'RETENTION'::emr4_context_fabric.logical_capability, "
        "'APPLICATION_READ'::emr4_context_fabric.logical_capability]",
    )
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(widened_application))

    direct_grant = copy.deepcopy(contract)
    roles = {row["role"]: row for row in direct_grant["role_matrix"]}
    roles["context_coordinator"]["direct_table_select"] = [
        "diary_context_observation_outbox_v1"
    ]
    with pytest.raises(AssertionError):
        validate_renderer_semantics(reseal_contract(direct_grant))


def test_exact_schema_rejects_resealed_non_hash_mutation() -> None:
    contract = data(CONTRACT)
    candidate = copy.deepcopy(contract)
    candidate["invariant_enforcement_catalogue"][0]["predicate"] += " unsafe"
    reseal_contract(candidate)
    with pytest.raises(ValidationError):
        Draft202012Validator(semantic_schema_without_digest_const()).validate(candidate)


def test_semantic_validator_rejects_resealed_unsafe_variants() -> None:
    contract = data(CONTRACT)
    candidates: list[dict] = []

    def mutated(path: tuple[object, ...], value: object) -> None:
        candidate = copy.deepcopy(contract)
        target: object = candidate
        for part in path[:-1]:
            target = target[part]  # type: ignore[index]
        target[path[-1]] = value  # type: ignore[index]
        candidates.append(reseal_contract(candidate))

    mutated(
        ("postgresql_target", "savepoint_without_relevant_tuple_database_detectable"),
        True,
    )
    mutated(
        ("type_catalogue", "enums", 0, "values"),
        ["PRIMARY", "CONFLICT", "UNBOUNDED"],
    )
    mutated(
        ("relation_catalogue", "relations", 0, "columns", 0, "default_sql"),
        "now()",
    )
    mutated(
        ("relation_catalogue", "relations", 1, "primary_key", "columns"),
        ["product_appointment_uuid"],
    )
    event_fk = {
        "name": "fk_unsafe_event",
        "columns": ["practice_id", "raw_event_uuid"],
        "references_relation": "diary_committed_events",
        "references_columns": ["practice_id", "id"],
        "on_delete": "RESTRICT",
        "deferrable": False,
    }
    candidate = copy.deepcopy(contract)
    candidate["relation_catalogue"]["relations"][2]["foreign_keys"].append(event_fk)
    candidates.append(reseal_contract(candidate))
    mutated(
        ("rls_policy_catalogue", "policies", 0, "using_sql"),
        "TRUE",
    )
    mutated(
        ("entry_points", 1, "output", "data_type"),
        "jsonb",
    )
    mutated(
        ("role_matrix", 3, "direct_table_dml"),
        [],
    )
    candidate = copy.deepcopy(contract)
    candidate["role_matrix"][3]["direct_table_select"].append("appointments")
    candidates.append(reseal_contract(candidate))
    candidate = copy.deepcopy(contract)
    candidate["role_matrix"][3]["direct_table_dml"].append(
        {"relation": "appointments", "privileges": ["UPDATE"]}
    )
    candidates.append(reseal_contract(candidate))
    mutated(
        ("function_body_boundary", "structural_renderer_must_omit_entry_points"),
        False,
    )
    mutated(
        (
            "function_body_boundary",
            "structural_renderer_must_omit_trigger_declarations",
        ),
        False,
    )
    mutated(
        ("function_body_boundary", "structural_renderer_must_omit_execute_grants"),
        False,
    )
    mutated(
        ("trigger_surface", 2, "events"),
        ["UPDATE OF start_time,duration_minutes"],
    )
    mutated(
        ("trigger_function_catalogue", 2, "returns"),
        "text",
    )
    candidate = copy.deepcopy(contract)
    candidate["invariant_enforcement_catalogue"].pop()
    candidates.append(reseal_contract(candidate))
    candidate = copy.deepcopy(contract)
    candidate["cross_relation_invariants"][0] = "nonexistent_invariant"
    candidates.append(reseal_contract(candidate))

    assert len(candidates) == 17
    for candidate in candidates:
        with pytest.raises(AssertionError):
            validate_renderer_semantics(candidate)


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


def test_artifact_boundary_remains_static_and_unmounted() -> None:
    contract = data(CONTRACT)
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

    plan = " ".join(text(PLAN).lower().split())
    for phrase in (
        "disposable local database",
        "this architecture tranche itself performs none",
        "provider-free unmounted function-and-trigger-body architecture",
        "authored-synthetic migration/ddl rehearsal",
        "no applied migration",
        "no executable ddl",
    ):
        assert phrase in plan
