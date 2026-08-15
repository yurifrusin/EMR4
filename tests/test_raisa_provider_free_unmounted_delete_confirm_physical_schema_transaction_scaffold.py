import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
TENANCY_PATH = ROOT / "app/models/tenancy.py"
APPOINTMENTS_PATH = ROOT / "app/models/appointments.py"
SERVICE_PATH = ROOT / "app/services/appointment_delete_physical.py"
MIGRATION_PATH = (
    ROOT / "alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py"
)
VALIDATOR_PATH = (
    ROOT
    / "scripts/raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py"
)
OPENAPI_PATH = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"
CONTRACT_PATH = (
    ROOT / "orchestration/continuity/"
    "raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/"
    "scaffold-contract.json"
)
SCHEMA_PATH = CONTRACT_PATH.with_name("scaffold-contract.schema.json")
HOSTILE_MUTATION_TARGET = 90


def _load_service():
    spec = importlib.util.spec_from_file_location(
        "delete_physical_test_module", SERVICE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "delete_physical_validator_test_module", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_openapi_remains_frozen() -> None:
    assert hashlib.sha256(OPENAPI_PATH.read_bytes()).hexdigest() == (
        "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a"
    )


def test_tenancy_maps_authority_generation_and_grant_relation() -> None:
    source = TENANCY_PATH.read_text(encoding="utf-8")
    assert "authority_generation = Column(BigInteger, nullable=False" in source
    assert 'server_default="1", default=1' not in source
    assert "ck_users_authority_generation_positive" in source
    assert "uq_users_practice_id_id" in source
    assert "class UserCapabilityGrant(Base):" in source
    assert '__tablename__ = "user_capability_grants"' in source
    assert (
        "capability_code IN ('appointment.cancel.confirm', 'appointment.read')"
        in source
    )
    assert "pk_user_capability_grants" in source
    assert "fk_user_capability_grants_user" in source


def test_appointments_maps_receipt_and_audit_additive_fields() -> None:
    source = APPOINTMENTS_PATH.read_text(encoding="utf-8")
    for field in (
        "authority_generation = Column(BigInteger, nullable=True)",
        "audit_contract_version = Column(SmallInteger, nullable=True)",
        "pre_state_version = Column(BigInteger, nullable=True)",
        "post_state_version = Column(BigInteger, nullable=True)",
        "waiting_area_before_id = Column(UUID(as_uuid=True), nullable=True)",
        "waiting_area_after_id = Column(UUID(as_uuid=True), nullable=True)",
        "audit_evidence_codes = Column(JSONB, nullable=True)",
    ):
        assert field in source
    assert "ck_appt_cmd_idem_status_receipt_v1_complete" in source
    assert "ck_appt_audit_log_delete_v1_complete" in source
    assert "confirmAppointmentDeleteProposal" in source
    assert "route_family = 'delete-confirm'" in source
    assert "authority_generation IS NOT NULL AND authority_generation >= 1" in source


def test_migration_has_frozen_revision_and_ordered_cutover() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert 'revision: str = "x3y4z5a6b7c8"' in source
    assert 'down_revision: Union[str, Sequence[str], None] = "w2x3y4z5a6b7"' in source
    markers = (
        'sa.Column("authority_generation", sa.BigInteger(), nullable=True)',
        'server_default=sa.text("1")',
        "UPDATE public.users SET authority_generation = 1",
        "CHECK (authority_generation >= 1) NOT VALID",
        'op.alter_column("users", "authority_generation", nullable=False)',
        "ALTER TABLE public.users ADD CONSTRAINT uq_users_practice_id_id",
        "op.create_table(",
        "CREATE FUNCTION public.emr4_user_authority_generation_guard()",
        "CREATE TRIGGER trg_users_authority_generation_guard",
        "CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()",
        "CREATE TRIGGER trg_user_capability_grants_generation",
        "CREATE FUNCTION public.emr4_reject_user_capability_grant_update()",
        "CREATE TRIGGER trg_user_capability_grants_reject_update",
        "invalid authority_generation after cutover",
    )
    positions = [source.index(marker) for marker in markers]
    assert positions == sorted(positions)
    assert "BEFORE INSERT OR UPDATE ON public.users" in source
    assert "BEFORE INSERT OR DELETE ON public.user_capability_grants" in source
    assert "BEFORE UPDATE ON public.user_capability_grants" in source


def test_migration_triggers_and_guards() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    # Direct submitted generation is ignored.
    assert "v_submitted := NEW.authority_generation" in source
    assert "NEW.authority_generation := OLD.authority_generation" in source
    assert "NEW.authority_generation := 1" in source
    # The database-owned OLD + 1 transition is admitted only at the nested
    # trigger depth. A caller-settable custom GUC cannot spoof it.
    assert "pg_trigger_depth() = 2" in source
    assert "emr4.authority_advance_target" not in source
    assert "current_setting(" not in source
    assert "v_submitted = OLD.authority_generation + 1" in source
    assert "authority_generation overflow" in source
    assert "OLD.authority_generation + 1" in source
    # Capability insert/delete locks and advances the exact parent.
    assert "FOR UPDATE" in source
    assert "authority_generation = users.authority_generation + 1" in source
    assert "FROM public.user_capability_grants" in source
    assert (
        'f"""\n        CREATE FUNCTION public.emr4_user_capability_grant_generation_guard()'
        in source
    )
    insert_branch = source.split("ELSIF TG_OP = 'INSERT' THEN", maxsplit=1)[1]
    parent_lock = insert_branch.index("FOR UPDATE")
    duplicate_guard = insert_branch.index("SELECT 1 FROM public.user_capability_grants")
    generation_advance = insert_branch.index("UPDATE public.users")
    assert parent_lock < duplicate_guard < generation_advance
    assert "RETURN NEW;" in source
    assert "ON public.users" in source
    assert "UPDATE public.users" in source
    assert "user capability grant update is rejected" in source
    assert "user capability grant parent user missing" in source


def test_migration_downgrade_guards() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert "user capability grant exists; forward recovery required" in source
    assert "delete-confirm receipt v1 exists; forward recovery required" in source
    assert "delete audit v1 exists; forward recovery required" in source
    # The downgrade restores the unchanged status-only receipt constraint.
    downgrade = source.split("def downgrade()")[1]
    assert "confirmAppointmentStatusProposal" in downgrade
    assert "confirmAppointmentDeleteProposal" not in downgrade
    assert "route_family = 'status-confirm'" in downgrade


def test_migration_never_backfills_or_emits_events() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert "UPDATE appointment_command_idempotency" not in source
    assert "UPDATE appointment_audit_log" not in source
    assert "pg_notify" not in source.lower()
    assert "diary_committed" not in source.lower()


def test_canonical_response_is_exact_utf8_six_field_bytes() -> None:
    module = _load_service()
    payload = module.canonical_delete_confirm_response_bytes(
        appointment_id=UUID("11111111-1111-1111-1111-111111111111"),
        status_reason_code="PATIENT_CANCELLED",
        cancellation_reason=None,
        warning_codes=("requires_reason",),
    )
    assert payload == (
        b'{"appointment_id":"11111111-1111-1111-1111-111111111111",'
        b'"status":"Cancelled","status_reason_code":"PATIENT_CANCELLED",'
        b'"cancellation_reason":null,"waiting_area_id":null,'
        b'"warning_codes":["requires_reason"]}'
    )
    assert not payload.startswith(b"\xef\xbb\xbf")


def test_canonical_response_rejects_invalid_reason_or_overlength_text() -> None:
    module = _load_service()
    base = {
        "appointment_id": "11111111-1111-1111-1111-111111111111",
    }
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base,
            status_reason_code="LEGACY_UNCLASSIFIED",
            cancellation_reason=None,
            warning_codes=("requires_reason",),
        )
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base,
            status_reason_code=None,
            cancellation_reason=None,
            warning_codes=("requires_reason",),
        )
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base,
            status_reason_code="PATIENT_CANCELLED",
            cancellation_reason="x" * 501,
            warning_codes=("requires_reason",),
        )
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base,
            status_reason_code="PATIENT_CANCELLED",
            cancellation_reason=None,
            warning_codes=("requires_reason", "requires_reason"),
        )
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base,
            status_reason_code="PATIENT_CANCELLED",
            cancellation_reason=None,
            warning_codes=("requires_reason", 7),
        )


def test_session_binding_is_raw_deterministic_domain_separated_hmac() -> None:
    module = _load_service()
    digest = module.delete_confirm_session_binding_digest(
        secret=b"authored-synthetic-secret",
        practice_id="practice-1",
        actor_user_id="actor-1",
        authenticated_session_id="session-1",
    )
    assert isinstance(digest, bytes)
    assert len(digest) == 32
    assert digest.hex() == (
        "1fbc3fddcfff4519a79b5900acfcb73d6bbdd04b545cefc06666894fa6433400"
    )
    changed = module.delete_confirm_session_binding_digest(
        secret=b"authored-synthetic-secret",
        practice_id="practice-1",
        actor_user_id="actor-1",
        authenticated_session_id="session-2",
    )
    assert changed != digest


def test_session_binding_rejects_empty_inputs() -> None:
    module = _load_service()
    with pytest.raises(ValueError):
        module.delete_confirm_session_binding_digest(
            secret=b"",
            practice_id="practice-1",
            actor_user_id="actor-1",
            authenticated_session_id="session-1",
        )
    with pytest.raises(ValueError):
        module.delete_confirm_session_binding_digest(
            secret=b"secret",
            practice_id="practice-1",
            actor_user_id="actor-1",
            authenticated_session_id="",
        )
    with pytest.raises(ValueError):
        module.delete_confirm_session_binding_digest(
            secret=b"secret",
            practice_id="",
            actor_user_id="actor-1",
            authenticated_session_id="session-1",
        )


def test_response_integrity_is_lowercase_exact_and_fail_closed() -> None:
    module = _load_service()
    payload = b'{"appointment_id":"synthetic"}'
    digest = hashlib.sha256(payload).hexdigest()
    assert module.delete_confirm_response_integrity_valid(payload, digest)
    assert not module.delete_confirm_response_integrity_valid(payload + b" ", digest)
    assert not module.delete_confirm_response_integrity_valid(payload, digest.upper())
    assert not module.delete_confirm_response_integrity_valid(b"", digest)
    assert not module.delete_confirm_response_integrity_valid(payload, "nothex")


def _write_set_fixture(module):
    practice_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    target_id = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    actor_id = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
    command_id = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
    audit_id = UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
    session_digest = b"s" * 32
    request_hash = "1" * 64
    key_hash = "2" * 64
    warning_codes = ["REQUIRES_REASON"]
    response = module.canonical_delete_confirm_response_bytes(
        appointment_id=target_id,
        status_reason_code="PATIENT_CANCELLED",
        cancellation_reason="synthetic cancellation",
        warning_codes=warning_codes,
    )
    appointment = SimpleNamespace(
        practice_id=practice_id,
        id=target_id,
        appointment_state_version=8,
        status="Cancelled",
        waiting_area_id=None,
        status_reason_code="PATIENT_CANCELLED",
        cancellation_reason="synthetic cancellation",
    )
    audit = SimpleNamespace(
        id=audit_id,
        command_id=command_id,
        practice_id=practice_id,
        appointment_id=target_id,
        confirmed_by_user_id=actor_id,
        action="delete",
        audit_contract_version=1,
        authority_generation=4,
        pre_state_version=7,
        post_state_version=8,
        status_before="Booked",
        status_after="Cancelled",
        status_reason_code="PATIENT_CANCELLED",
        cancellation_reason="synthetic cancellation",
        waiting_area_before_id=UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"),
        waiting_area_after_id=None,
        confirmed_warnings=warning_codes,
        audit_evidence_codes=["AUTHORITY_CHECKED"],
    )
    record = SimpleNamespace(
        id=command_id,
        state="completed",
        completed_receipt_version=1,
        operation_id="confirmAppointmentDeleteProposal",
        route_family="delete-confirm",
        result_kind="confirmed_write",
        practice_id=practice_id,
        actor_user_id=str(actor_id),
        actor_role="Receptionist",
        target_appointment_id=target_id,
        authority_generation=4,
        request_body_hash=request_hash,
        idempotency_key_hash=key_hash,
        request_body_canonicalization_version=1,
        session_binding_digest=session_digest,
        pre_state_version=7,
        post_state_version=8,
        response_body_canonical_bytes=response,
        response_body_hash=hashlib.sha256(response).hexdigest(),
        response_body_json=json.loads(response),
        audit_log_id=audit_id,
        response_status_code=200,
    )
    arguments = {
        "record": record,
        "audit": audit,
        "appointment": appointment,
        "practice_id": practice_id,
        "target_appointment_id": target_id,
        "actor_user_id": actor_id,
        "actor_role": "Receptionist",
        "signed_authority_generation": 4,
        "request_body_hash": request_hash,
        "idempotency_key_hash": key_hash,
        "session_binding_digest": session_digest,
        "pre_state_version": 7,
        "pre_status": "Booked",
        "waiting_area_before_id": audit.waiting_area_before_id,
    }
    return arguments


def test_exact_three_artifact_write_set_is_complete() -> None:
    module = _load_service()
    assert module._delete_write_set_complete(**_write_set_fixture(module))


@pytest.mark.parametrize(
    ("owner", "field", "hostile"),
    (
        ("record", "state", "in_progress"),
        ("record", "authority_generation", 5),
        ("record", "idempotency_key_hash", "3" * 64),
        ("record", "response_body_canonical_bytes", b"{}"),
        ("record", "response_body_json", {}),
        ("audit", "command_id", UUID("00000000-0000-0000-0000-000000000001")),
        ("audit", "confirmed_by_user_id", UUID("00000000-0000-0000-0000-000000000002")),
        ("audit", "post_state_version", 9),
        ("audit", "status_after", "Booked"),
        (
            "audit",
            "waiting_area_after_id",
            UUID("00000000-0000-0000-0000-000000000003"),
        ),
        ("appointment", "appointment_state_version", 9),
        ("appointment", "status", "Booked"),
        (
            "appointment",
            "waiting_area_id",
            UUID("00000000-0000-0000-0000-000000000004"),
        ),
        ("appointment", "status_reason_code", "OTHER"),
    ),
)
def test_three_artifact_write_set_rejects_cross_artifact_corruption(
    owner, field, hostile
) -> None:
    module = _load_service()
    arguments = _write_set_fixture(module)
    setattr(arguments[owner], field, hostile)
    assert not module._delete_write_set_complete(**arguments)


def test_transaction_ast_has_one_boundary_and_exact_lock_authority_order() -> None:
    source = SERVICE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "delete_confirm_locked_transaction"
    )
    function_source = ast.get_source_segment(source, function)
    assert function_source is not None
    ordered = (
        "with db.begin():",
        "SET TRANSACTION ISOLATION LEVEL READ COMMITTED",
        'select(func.set_config("lock_timeout"',
        "db.query(User)",
        ".with_for_update(read=True)",
        "db.query(Appointment)",
        ".with_for_update()",
        "if not _authority_valid(",
        "db.query(AppointmentCommandIdempotency)",
        ".with_for_update()",
        "postgresql_insert(AppointmentCommandIdempotency)",
        "db.query(AppointmentCommandIdempotency)",
        ".with_for_update()",
        "if not _authority_valid(",
        "if inserted:",
    )
    cursor = -1
    for marker in ordered:
        cursor = function_source.index(marker, cursor + 1)
    assert function_source.count("if not _authority_valid(") == 2
    assert (
        function_source.count("\n        _apply_lock_budget()")
        + function_source.count("\n            _apply_lock_budget()")
    ) == 7
    assert "DELETE_CONFIRM_LOCK_WAIT_DEADLINE_MS = 2000" in source
    assert "time.monotonic()" in function_source
    assert "SET LOCAL lock_timeout = :timeout" not in function_source
    assert "authority_generation=signed_authority_generation" in function_source
    assert "actor_user_id=str(actor_uuid)" in function_source
    assert "nowait" not in function_source.lower()
    assert "skip_locked" not in function_source.lower()
    assert "advisory" not in function_source.lower()
    assert "current_authority" not in function_source
    assert "practice_is_active" not in function_source


def test_transaction_input_and_binding_guards_fail_closed() -> None:
    source = SERVICE_PATH.read_text(encoding="utf-8")
    assert 'practice_uuid = _as_uuid(practice_id, "practice_id")' in source
    assert (
        'target_uuid = _as_uuid(target_appointment_id, "target_appointment_id")'
        in source
    )
    assert 'actor_uuid = _as_uuid(actor_user_id, "actor_user_id")' in source
    assert "_lowercase_sha256(idempotency_key_hash" in source
    assert "_lowercase_sha256(request_body_hash" in source
    assert "not isinstance(session_binding_digest, bytes)" in source
    assert "isinstance(signed_authority_generation, bool)" in source
    assert "record.authority_generation == signed_authority_generation" in source
    assert "record.authority_generation is None" not in source


def test_service_is_unmounted_and_does_not_stage_product_write() -> None:
    service_source = SERVICE_PATH.read_text(encoding="utf-8")
    assert "appointment.status =" not in service_source
    assert "AppointmentAuditLog(" not in service_source
    assert 'record.state = "completed"' not in service_source
    assert "@router" not in service_source
    assert "FastAPI" not in service_source


def test_post_yield_guard_requires_exact_three_artifact_write_set() -> None:
    source = SERVICE_PATH.read_text(encoding="utf-8")
    assert 'record.state == "completed"' in source
    assert "db.query(AppointmentAuditLog)" in source
    assert "def _delete_write_set_complete(" in source
    for token in (
        "audit.command_id == record.id",
        "audit.practice_id == practice_id",
        "audit.appointment_id == target_appointment_id",
        "audit.confirmed_by_user_id == actor_user_id",
        'and _enum_value(audit.action) == "delete"',
        "audit.authority_generation == signed_authority_generation",
        "audit.pre_state_version == pre_state_version",
        "audit.post_state_version == post_state_version",
        "_enum_value(audit.status_before) == pre_status",
        "_enum_value(audit.status_after) == DELETE_CONFIRM_STATUS",
        "audit.status_reason_code == appointment.status_reason_code",
        "audit.cancellation_reason == appointment.cancellation_reason",
        "audit.waiting_area_before_id == waiting_area_before_id",
        "audit.waiting_area_after_id is None",
        "appointment.appointment_state_version == post_state_version",
        "_enum_value(appointment.status) == DELETE_CONFIRM_STATUS",
        "appointment.waiting_area_id is None",
        "record.response_body_canonical_bytes == expected_response",
        "record.response_body_json == expected_json",
        "record.idempotency_key_hash == idempotency_key_hash",
        "record.request_body_canonicalization_version == 1",
    ):
        assert token in source


def test_contract_is_schema_valid_and_bound_to_source_head() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = [
        error.message for error in Draft202012Validator(schema).iter_errors(contract)
    ]
    assert errors == []
    assert contract["source_head"] == "d500f1f86a83695cee0c2aac93aa2e2735e8f799"
    assert contract["result"].endswith("_pass")
    assert contract["migration"]["revision"] == "x3y4z5a6b7c8"
    assert contract["migration"]["down_revision"] == "w2x3y4z5a6b7"
    assert contract["transaction_seam"]["authority_check_count"] == 2
    assert contract["transaction_seam"]["cumulative_lock_wait_budget_ms"] == 2000
    assert contract["helpers"]["canonical_response"]["status_constant"] == "Cancelled"
    assert contract["authority_check"]["internal_only"] is True


def test_contract_bindings_match_frozen_source_hashes() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    checked = 0
    for group in ("input_bindings", "implementation_bindings"):
        for binding in contract[group]:
            path = ROOT / binding["path"]
            assert path.is_file(), f"missing:{binding['path']}"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == binding["sha256"], (
                f"hash_mismatch:{binding['path']}"
            )
            checked += 1
    assert checked >= 10


def test_hostile_mutations_rejected_at_least_ninety() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = _load_validator()
    attempted, rejected, admitted = validator.validate_hostile_mutations(
        contract, schema
    )
    assert attempted >= HOSTILE_MUTATION_TARGET
    assert rejected == attempted
    assert admitted == []


def test_closed_world_authority_writer_inventory_is_exact() -> None:
    validator = _load_validator()
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert validator._verify_closed_world_authority_writers(source) == []
