from pathlib import Path

import pytest
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.models.bernie_sessions import BernieBookingSession, BernieSessionEventRow
from scripts.bernie_stage2_database_acceptance import run_acceptance


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "alembic" / "versions" / "m2n3o4p5q6r7_add_bernie_durable_authority.py"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"
GRAPHQL = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
IDEMPOTENCY_INDEX = ROOT / "docs" / "api-spine" / "idempotency-continuity-index.md"
AUDIT_INDEX = ROOT / "docs" / "api-spine" / "audit-correlation-continuity-index.md"


def _constraint_names(table, kind) -> set[str]:
    return {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, kind)
    }


def test_models_bind_every_stage2_correlation_to_the_same_practice() -> None:
    assert "uq_appointments_practice_id_id" in _constraint_names(
        Appointment.__table__, UniqueConstraint
    )
    assert "uq_appt_audit_log_practice_id_id" in _constraint_names(
        AppointmentAuditLog.__table__, UniqueConstraint
    )
    assert "uq_appt_cmd_idem_practice_id_id" in _constraint_names(
        AppointmentCommandIdempotency.__table__, UniqueConstraint
    )
    assert "uq_bernie_booking_sessions_practice_session" in _constraint_names(
        BernieBookingSession.__table__, UniqueConstraint
    )

    assert {
        "fk_appt_audit_log_practice_appointment",
        "fk_appt_audit_log_practice_command",
    } <= _constraint_names(AppointmentAuditLog.__table__, ForeignKeyConstraint)
    assert {
        "fk_appt_cmd_idem_practice_target",
        "fk_appt_cmd_idem_practice_audit",
    } <= _constraint_names(
        AppointmentCommandIdempotency.__table__, ForeignKeyConstraint
    )
    assert "fk_bernie_session_events_practice_session" in _constraint_names(
        BernieSessionEventRow.__table__, ForeignKeyConstraint
    )


def test_migration_contains_rls_immutability_retention_and_tenant_integrity_controls() -> None:
    source = MIGRATION.read_text(encoding="utf-8")

    assert 'revision: str = "m2n3o4p5q6r7"' in source
    assert 'down_revision: Union[str, Sequence[str], None] = "l1m2n3o4p5q6"' in source
    assert 'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY' in source
    assert '_enable_all_practice_policy("bernie_booking_sessions"' in source
    assert 'ALTER TABLE "bernie_session_events" FORCE ROW LEVEL SECURITY' in source
    assert '_enable_all_practice_policy("appointments"' in source
    assert '"appointment_command_idempotency_practice_all"' in source
    assert 'ALTER TABLE "appointment_audit_log" FORCE ROW LEVEL SECURITY' in source
    for constraint_name in (
        "fk_bernie_session_events_practice_session",
        "fk_appt_audit_log_practice_appointment",
        "fk_appt_audit_log_practice_command",
        "fk_appt_cmd_idem_practice_target",
        "fk_appt_cmd_idem_practice_audit",
    ):
        assert constraint_name in source
    assert "trg_appointment_audit_log_append_only" in source
    assert "appointment audit evidence is append-only" in source
    assert "completed create command does not have exactly one matching create audit" in source


def test_database_probe_is_pinned_to_the_disposable_database() -> None:
    with pytest.raises(ValueError, match="requires 'gp_pms_stage2_migration'"):
        run_acceptance(
            "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"
        )


def test_api_spine_records_bounded_runtime_checkpoint_without_graphql_mutation() -> None:
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed.")
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    receipt = spec["components"]["schemas"]["ConfirmationReceipt"]
    assert {
        "correlation_id",
        "audit_event_id",
        "session_id",
        "verification",
    } <= set(receipt["properties"])

    variants = {
        entry["current_backend_path"]: entry
        for entry in spec["x-emr4-current-backend-alignment"]["bernie_backend_variants"]
    }
    checkpoint = variants[
        "/appointments/proposals/create/confirm-bernie"
    ]["stage2_local_synthetic_checkpoint"]
    assert checkpoint["durable_session_state"] == "postgresql_transactional"
    assert checkpoint["production_runtime_role"] == "blocked_pending_fresh_decision"
    assert "type Mutation" not in GRAPHQL.read_text(encoding="utf-8")

    idempotency_text = IDEMPOTENCY_INDEX.read_text(encoding="utf-8")
    audit_text = AUDIT_INDEX.read_text(encoding="utf-8")
    assert "two independent same-key confirmation transactions" in idempotency_text
    assert "confirmation_receipt.correlation_id" in audit_text
    assert "local_synthetic_runtime_proven" in audit_text
