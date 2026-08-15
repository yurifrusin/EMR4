import ast
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from uuid import UUID

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
TENANCY_PATH = ROOT / "app/models/tenancy.py"
APPOINTMENTS_PATH = ROOT / "app/models/appointments.py"
SERVICE_PATH = ROOT / "app/services/appointment_delete_physical.py"
MIGRATION_PATH = (
    ROOT
    / "alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py"
)
OPENAPI_PATH = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"
CONTRACT_PATH = (
    ROOT
    / "orchestration/continuity/"
    "raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/"
    "scaffold-contract.json"
)
SCHEMA_PATH = CONTRACT_PATH.with_name("scaffold-contract.schema.json")
HOSTILE_MUTATION_TARGET = 90


def _load_service():
    spec = importlib.util.spec_from_file_location("delete_physical_test_module", SERVICE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _canonical_digest(value) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _leaf_paths(value, prefix=()):
    if isinstance(value, dict):
        paths = []
        for key, child in value.items():
            paths.extend(_leaf_paths(child, (*prefix, key)))
        return paths
    if isinstance(value, list):
        paths = []
        for index, child in enumerate(value):
            paths.extend(_leaf_paths(child, (*prefix, index)))
        return paths
    return [prefix]


def _mutated_leaf(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return f"{value}-hostile"
    if value is None:
        return "hostile-non-null"
    raise TypeError(f"unsupported contract leaf: {type(value).__name__}")


def _mutate_at(candidate, path):
    parent = candidate
    for component in path[:-1]:
        parent = parent[component]
    final = path[-1]
    parent[final] = _mutated_leaf(parent[final])


def test_public_openapi_remains_frozen() -> None:
    assert hashlib.sha256(OPENAPI_PATH.read_bytes()).hexdigest() == (
        "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a"
    )


def test_tenancy_maps_authority_generation_and_grant_relation() -> None:
    source = TENANCY_PATH.read_text(encoding="utf-8")
    assert "authority_generation = Column(BigInteger, nullable=False" in source
    assert "ck_users_authority_generation_positive" in source
    assert "uq_users_practice_id_id" in source
    assert "class UserCapabilityGrant(Base):" in source
    assert "__tablename__ = \"user_capability_grants\"" in source
    assert "capability_code IN ('appointment.cancel.confirm', 'appointment.read')" in source
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
        "UPDATE users SET authority_generation = 1",
        "CHECK (authority_generation >= 1) NOT VALID",
        'op.alter_column("users", "authority_generation", nullable=False)',
        "ALTER TABLE users ADD CONSTRAINT uq_users_practice_id_id",
        "op.create_table(",
        "CREATE FUNCTION emr4_user_authority_generation_guard()",
        "CREATE TRIGGER trg_users_authority_generation_guard",
        "CREATE FUNCTION emr4_user_capability_grant_generation_guard()",
        "CREATE TRIGGER trg_user_capability_grants_generation",
        "CREATE FUNCTION emr4_reject_user_capability_grant_update()",
        "CREATE TRIGGER trg_user_capability_grants_reject_update",
        "invalid authority_generation after cutover",
    )
    positions = [source.index(marker) for marker in markers]
    assert positions == sorted(positions)
    assert "BEFORE INSERT OR UPDATE ON users" in source
    assert "BEFORE INSERT OR DELETE ON user_capability_grants" in source
    assert "BEFORE UPDATE ON user_capability_grants" in source


def test_migration_triggers_and_guards() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    # Direct submitted generation is ignored.
    assert "v_submitted := NEW.authority_generation" in source
    assert "NEW.authority_generation := OLD.authority_generation" in source
    assert "NEW.authority_generation := 1" in source
    # The nested database-owned OLD + 1 transition is admitted only via the
    # transaction-local marker naming the exact parent user.
    assert "current_setting(" in source
    assert "emr4.authority_advance_target" in source
    assert "v_submitted = OLD.authority_generation + 1" in source
    assert "authority_generation overflow" in source
    assert "OLD.authority_generation + 1" in source
    # Capability insert/delete locks and advances the exact parent.
    assert "FOR UPDATE" in source
    assert "authority_generation = users.authority_generation + 1" in source
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
            **base, status_reason_code="LEGACY_UNCLASSIFIED",
            cancellation_reason=None, warning_codes=("requires_reason",),
        )
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base, status_reason_code=None, cancellation_reason=None,
            warning_codes=("requires_reason",),
        )
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base, status_reason_code="PATIENT_CANCELLED",
            cancellation_reason="x" * 501, warning_codes=("requires_reason",),
        )
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base, status_reason_code="PATIENT_CANCELLED",
            cancellation_reason=None, warning_codes=("requires_reason", "requires_reason"),
        )
    with pytest.raises(ValueError):
        module.canonical_delete_confirm_response_bytes(
            **base, status_reason_code="PATIENT_CANCELLED",
            cancellation_reason=None, warning_codes=("requires_reason", 7),
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
        "SET LOCAL lock_timeout",
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
    assert "nowait" not in function_source.lower()
    assert "skip_locked" not in function_source.lower()
    assert "advisory" not in function_source.lower()
    assert "current_authority" not in function_source
    assert "practice_is_active" not in function_source


def test_service_is_unmounted_and_does_not_stage_product_write() -> None:
    service_source = SERVICE_PATH.read_text(encoding="utf-8")
    assert "appointment.status =" not in service_source
    assert "AppointmentAuditLog(" not in service_source
    assert "record.state = \"completed\"" not in service_source
    assert "@router" not in service_source
    assert "FastAPI" not in service_source


def test_contract_is_schema_valid_and_bound_to_source_head() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = [
        error.message
        for error in Draft202012Validator(schema).iter_errors(contract)
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
    original_digest = _canonical_digest(contract)
    leaf_paths = _leaf_paths(contract)
    assert len(leaf_paths) >= HOSTILE_MUTATION_TARGET
    rejected = 0
    for path in leaf_paths[:HOSTILE_MUTATION_TARGET]:
        mutated = copy.deepcopy(contract)
        _mutate_at(mutated, path)
        schema_errors = [
            error.message
            for error in Draft202012Validator(schema).iter_errors(mutated)
        ]
        digest_changed = _canonical_digest(mutated) != original_digest
        assert schema_errors or digest_changed, f"hostile_mutation_admitted:{path}"
        rejected += 1
    assert rejected >= HOSTILE_MUTATION_TARGET
