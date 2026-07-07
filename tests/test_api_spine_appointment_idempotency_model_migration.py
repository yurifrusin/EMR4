from pathlib import Path

from sqlalchemy import CheckConstraint, UniqueConstraint

from app.models.appointments import AppointmentCommandIdempotency


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "alembic"
    / "versions"
    / "l1m2n3o4p5q6_add_appointment_command_idempotency.py"
)
PREFLIGHT_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_model_migration_preflight.md"
)
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"

TABLE_NAME = "appointment_command_idempotency"
REQUIRED_COLUMNS = (
    "id",
    "practice_id",
    "actor_user_id",
    "actor_role",
    "operation_id",
    "route_family",
    "idempotency_key_hash",
    "request_body_hash",
    "request_body_canonicalization_version",
    "state",
    "response_status_code",
    "response_body_hash",
    "response_body_json",
    "result_kind",
    "target_appointment_id",
    "audit_log_id",
    "created_at",
    "updated_at",
    "expires_at",
)
FORBIDDEN_FIELDS = (
    "raw_idempotency_key",
    "idempotency_key_raw",
    "raw_request_body",
    "request_body_json",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_model_declares_appointment_command_idempotency_table_contract():
    table = AppointmentCommandIdempotency.__table__

    assert table.name == TABLE_NAME
    assert tuple(table.columns.keys()) == REQUIRED_COLUMNS
    for column in (
        "practice_id",
        "actor_user_id",
        "actor_role",
        "operation_id",
        "route_family",
        "idempotency_key_hash",
        "request_body_hash",
        "request_body_canonicalization_version",
        "state",
        "created_at",
        "updated_at",
    ):
        assert table.c[column].nullable is False
    for column in (
        "response_status_code",
        "response_body_hash",
        "response_body_json",
        "result_kind",
        "target_appointment_id",
        "audit_log_id",
        "expires_at",
    ):
        assert table.c[column].nullable is True
    assert str(table.c.actor_user_id.type) == "VARCHAR(64)"


def test_preflight_doc_records_storage_only_scope_and_next_slice():
    text = _read(PREFLIGHT_DOC)

    assert "# API Spine Appointment Idempotency Model/Migration Preflight" in text
    assert "| Sprint | 128 |" in text
    assert "Model and migration preflight only; no appointment route enforcement" in text
    assert "AppointmentCommandIdempotency" in text
    assert "appointment_command_idempotency" in text
    assert "does not:" in text
    assert "bind or require HTTP `Idempotency-Key`" in text
    assert "Recommended Sprint 129" in text
    assert "storage helper tests" in text


def test_model_declares_uniqueness_indexes_and_state_checks():
    table = AppointmentCommandIdempotency.__table__

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    assert any(
        constraint.name == "uq_appt_cmd_idem_practice_actor_operation_key"
        and [column.name for column in constraint.columns]
        == ["practice_id", "actor_user_id", "operation_id", "idempotency_key_hash"]
        for constraint in unique_constraints
    )

    indexes = {index.name: [column.name for column in index.columns] for index in table.indexes}
    assert indexes["ix_appt_cmd_idem_practice_target"] == [
        "practice_id",
        "target_appointment_id",
    ]
    assert indexes["ix_appt_cmd_idem_practice_created"] == [
        "practice_id",
        "created_at",
    ]

    checks = {
        constraint.name: str(constraint.sqltext)
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert checks["ck_appt_cmd_idem_state"] == (
        "state in ('in_progress', 'completed', 'failed_transient')"
    )
    assert "response_status_code IS NOT NULL" in checks[
        "ck_appt_cmd_idem_completed_response"
    ]
    assert "response_body_hash IS NOT NULL" in checks[
        "ck_appt_cmd_idem_completed_response"
    ]
    assert "response_body_json IS NOT NULL" in checks[
        "ck_appt_cmd_idem_completed_response"
    ]


def test_model_does_not_store_raw_keys_or_raw_request_bodies():
    model_source = _read(ROOT / "app" / "models" / "appointments.py")

    for forbidden in FORBIDDEN_FIELDS:
        assert forbidden not in AppointmentCommandIdempotency.__table__.columns
        assert forbidden not in model_source


def test_migration_matches_model_contract_and_previous_revision():
    text = _read(MIGRATION)

    assert 'revision: str = "l1m2n3o4p5q6"' in text
    assert 'down_revision: Union[str, Sequence[str], None] = "k0l1m2n3o4p5"' in text
    assert f'op.create_table(\n        "{TABLE_NAME}"' in text
    for column in REQUIRED_COLUMNS:
        assert f'"{column}"' in text
    assert "uq_appt_cmd_idem_practice_actor_operation_key" in text
    assert "ix_appt_cmd_idem_practice_target" in text
    assert "ix_appt_cmd_idem_practice_created" in text
    assert "ck_appt_cmd_idem_state" in text
    assert "ck_appt_cmd_idem_completed_response" in text
    assert "in_progress" in text
    assert "completed" in text
    assert "failed_transient" in text
    for forbidden in FORBIDDEN_FIELDS:
        assert forbidden not in text


def test_appointment_routes_do_not_import_storage_model_directly():
    route_text = _read(APPOINTMENTS_ROUTER)

    assert TABLE_NAME not in route_text
    assert "AppointmentCommandIdempotency" not in route_text
    assert "confirmAppointmentCreateProposal" in route_text
    assert "Idempotency-Key" in route_text
