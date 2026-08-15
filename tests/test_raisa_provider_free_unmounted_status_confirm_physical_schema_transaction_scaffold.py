import ast
import hashlib
import importlib.util
import sys
from pathlib import Path
from uuid import UUID

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "app/models/appointments.py"
SERVICE_PATH = ROOT / "app/services/appointment_status_physical.py"
MIGRATION_PATH = (
    ROOT
    / "alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py"
)
OPENAPI_PATH = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"


def _load_service():
    spec = importlib.util.spec_from_file_location("status_physical_test_module", SERVICE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_public_openapi_remains_frozen() -> None:
    assert hashlib.sha256(OPENAPI_PATH.read_bytes()).hexdigest() == (
        "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a"
    )


def test_model_maps_exact_additive_fields_and_constraints() -> None:
    source = MODEL_PATH.read_text(encoding="utf-8")
    assert "appointment_state_version = Column(BigInteger, nullable=False" in source
    for field in (
        "completed_receipt_version = Column(SmallInteger, nullable=True)",
        "session_binding_digest = Column(LargeBinary, nullable=True)",
        "pre_state_version = Column(BigInteger, nullable=True)",
        "post_state_version = Column(BigInteger, nullable=True)",
        "response_body_canonical_bytes = Column(LargeBinary, nullable=True)",
    ):
        assert field in source
    assert "ck_appointments_state_version_positive" in source
    assert "ck_appt_cmd_idem_receipt_version" in source
    assert "ck_appt_cmd_idem_status_receipt_v1_complete" in source
    assert "post_state_version = pre_state_version + 1" in source
    assert "octet_length(session_binding_digest) = 32" in source


def test_migration_has_frozen_revision_and_ordered_seven_phase_cutover() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert 'revision: str = "w2x3y4z5a6b7"' in source
    assert 'down_revision: Union[str, Sequence[str], None] = "v1w2x3y4z5b6"' in source
    markers = (
        'sa.Column("appointment_state_version", sa.BigInteger(), nullable=True)',
        'server_default=sa.text("1")',
        "UPDATE appointments SET appointment_state_version = 1",
        "CHECK (appointment_state_version >= 1) NOT VALID",
        'op.alter_column("appointments", "appointment_state_version", nullable=False)',
        "CREATE FUNCTION emr4_advance_appointment_state_version()",
        "CREATE TRIGGER trg_appointments_advance_state_version",
        "invalid appointment_state_version after cutover",
    )
    positions = [source.index(marker) for marker in markers]
    assert positions == sorted(positions)
    assert "BEFORE UPDATE ON appointments" in source
    assert "NEW.appointment_state_version := OLD.appointment_state_version + 1" in source
    assert "appointment_state_version overflow" in source
    assert "status-confirm receipt v1 exists; forward recovery required" in source


def test_migration_never_backfills_legacy_receipts_or_emits_events() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert "UPDATE appointment_command_idempotency" not in source
    assert "pg_notify" not in source.lower()
    assert "diary_committed" not in source.lower()


def test_canonical_response_is_exact_utf8_five_field_bytes() -> None:
    module = _load_service()
    payload = module.canonical_status_confirm_response_bytes(
        appointment_id=UUID("11111111-1111-1111-1111-111111111111"),
        status="Arrived",
        status_reason_code=None,
        waiting_area_id=None,
        warning_codes=("requires_reason",),
    )
    assert payload == (
        b'{"appointment_id":"11111111-1111-1111-1111-111111111111",'
        b'"status":"Arrived","status_reason_code":null,"waiting_area_id":null,'
        b'"warning_codes":["requires_reason"]}'
    )
    assert not payload.startswith(b"\xef\xbb\xbf")


def test_canonical_response_rejects_duplicate_or_non_string_warning_codes() -> None:
    module = _load_service()
    kwargs = {
        "appointment_id": "11111111-1111-1111-1111-111111111111",
        "status": "Arrived",
        "status_reason_code": None,
        "waiting_area_id": None,
    }
    with pytest.raises(ValueError):
        module.canonical_status_confirm_response_bytes(
            **kwargs, warning_codes=("requires_reason", "requires_reason")
        )
    with pytest.raises(ValueError):
        module.canonical_status_confirm_response_bytes(
            **kwargs, warning_codes=("requires_reason", 7)
        )


def test_session_binding_is_raw_deterministic_domain_separated_hmac() -> None:
    module = _load_service()
    digest = module.status_confirm_session_binding_digest(
        secret=b"authored-synthetic-secret",
        practice_id="practice-1",
        actor_user_id="actor-1",
        authenticated_session_id="session-1",
    )
    assert isinstance(digest, bytes)
    assert len(digest) == 32
    assert digest.hex() == (
        "5adaf21c433cdab090ae6a4fe1482078b7bf9cf3fa74c8451e136fccf04f59d8"
    )
    changed = module.status_confirm_session_binding_digest(
        secret=b"authored-synthetic-secret",
        practice_id="practice-1",
        actor_user_id="actor-1",
        authenticated_session_id="session-2",
    )
    assert changed != digest


def test_session_binding_rejects_empty_inputs() -> None:
    module = _load_service()
    with pytest.raises(ValueError):
        module.status_confirm_session_binding_digest(
            secret=b"",
            practice_id="practice-1",
            actor_user_id="actor-1",
            authenticated_session_id="session-1",
        )
    with pytest.raises(ValueError):
        module.status_confirm_session_binding_digest(
            secret=b"secret",
            practice_id="practice-1",
            actor_user_id="actor-1",
            authenticated_session_id="",
        )


def test_response_integrity_is_lowercase_exact_and_fail_closed() -> None:
    module = _load_service()
    payload = b'{"appointment_id":"synthetic"}'
    digest = hashlib.sha256(payload).hexdigest()
    assert module.status_confirm_response_integrity_valid(payload, digest)
    assert not module.status_confirm_response_integrity_valid(payload + b" ", digest)
    assert not module.status_confirm_response_integrity_valid(payload, digest.upper())
    assert not module.status_confirm_response_integrity_valid(b"", digest)


def test_transaction_ast_has_one_boundary_and_exact_lock_authority_order() -> None:
    source = SERVICE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "status_confirm_locked_transaction"
    )
    function_source = ast.get_source_segment(source, function)
    assert function_source is not None
    ordered = (
        "with db.begin():",
        "SET TRANSACTION ISOLATION LEVEL READ COMMITTED",
        'func.set_config("lock_timeout"',
        "db.query(Practice)",
        ".with_for_update(read=True)",
        "db.query(Appointment)",
        ".with_for_update()",
        "if not current_authority(practice, appointment):",
        "postgresql_insert(AppointmentCommandIdempotency)",
        "db.query(AppointmentCommandIdempotency)",
        ".with_for_update()",
        "if not current_authority(practice, appointment):",
        "if inserted:",
    )
    cursor = -1
    for marker in ordered:
        cursor = function_source.index(marker, cursor + 1)
    assert function_source.count("current_authority(practice, appointment)") == 2
    assert "nowait" not in function_source.lower()
    assert "skip_locked" not in function_source.lower()


def test_service_is_unmounted_and_does_not_stage_product_write() -> None:
    service_source = SERVICE_PATH.read_text(encoding="utf-8")
    assert "appointment.status =" not in service_source
    assert "AppointmentAuditLog(" not in service_source
    assert "record.state = \"completed\"" not in service_source
    assert "@router" not in service_source
    assert "FastAPI" not in service_source
