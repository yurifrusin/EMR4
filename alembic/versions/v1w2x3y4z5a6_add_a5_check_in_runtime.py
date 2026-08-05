"""Add the A5.1 Rayleen check-in command runtime.

Revision ID: v1w2x3y4z5a6
Revises: u0v1w2x3y4z5
Create Date: 2026-08-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "v1w2x3y4z5a6"
down_revision: Union[str, Sequence[str], None] = "u0v1w2x3y4z5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TABLE = "appointment_command_idempotency"
_EVENTS_TABLE = "diary_committed_events"

# Prior idempotency correlation constraint admitted only the create operation.
_PRIOR_CORRELATION = (
    "NOT (state = 'completed' AND "
    "operation_id = 'confirmAppointmentCreateProposal' AND "
    "result_kind = 'confirmed_write') OR "
    "(target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL)"
)
_CURRENT_CORRELATION = (
    "NOT (state = 'completed' AND "
    "operation_id IN ('confirmAppointmentCreateProposal', "
    "'confirmAppointmentCheckInProposal') AND "
    "result_kind = 'confirmed_write') OR "
    "(target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL)"
)

# Completed A5 check-in command rows must carry the consumed signed-evidence hash.
_CHECK_IN_EVIDENCE = (
    "NOT (state = 'completed' AND "
    "operation_id = 'confirmAppointmentCheckInProposal' AND "
    "result_kind = 'confirmed_write') OR "
    "(confirmation_evidence_hash IS NOT NULL AND "
    "confirmation_evidence_consumed_at IS NOT NULL)"
)

# Prior committed-event constraints admitted only reschedule rows.
_PRIOR_TYPE = "event_type = 'diary.appointment_rescheduled'"
_PRIOR_SCHEMA = "schema_version = 'diary.appointment_rescheduled.v1'"
_PRIOR_PAYLOAD = (
    "jsonb_typeof(payload) = 'object' AND "
    "payload ?& ARRAY['appointment_id', 'practitioner_id', 'location_id', "
    "'start_time', 'end_time', 'reason_codes'] AND "
    "payload - ARRAY['appointment_id', 'practitioner_id', 'location_id', "
    "'start_time', 'end_time', 'reason_codes'] = '{}'::jsonb AND "
    "payload->'reason_codes' = '[\"appointment_time_changed\"]'::jsonb"
)
_CURRENT_TYPE = (
    "event_type IN ('diary.appointment_rescheduled', "
    "'diary.appointment_checked_in')"
)
_CURRENT_SCHEMA = (
    "(event_type = 'diary.appointment_rescheduled' AND "
    "schema_version = 'diary.appointment_rescheduled.v1') OR "
    "(event_type = 'diary.appointment_checked_in' AND "
    "schema_version = 'diary.appointment_checked_in.v1')"
)
_CURRENT_PAYLOAD = (
    "(event_type = 'diary.appointment_rescheduled' AND "
    "jsonb_typeof(payload) = 'object' AND "
    "payload ?& ARRAY['appointment_id', 'practitioner_id', 'location_id', "
    "'start_time', 'end_time', 'reason_codes'] AND "
    "payload - ARRAY['appointment_id', 'practitioner_id', 'location_id', "
    "'start_time', 'end_time', 'reason_codes'] = '{}'::jsonb AND "
    "payload->'reason_codes' = '[\"appointment_time_changed\"]'::jsonb) "
    "OR "
    "(event_type = 'diary.appointment_checked_in' AND "
    "jsonb_typeof(payload) = 'object' AND "
    "payload ?& ARRAY['appointment_id', 'practitioner_id', 'location_id', "
    "'status_before', 'status_after', 'waiting_area_id_before', "
    "'waiting_area_id_after', 'reason_codes'] AND "
    "payload - ARRAY['appointment_id', 'practitioner_id', 'location_id', "
    "'status_before', 'status_after', 'waiting_area_id_before', "
    "'waiting_area_id_after', 'reason_codes'] = '{}'::jsonb AND "
    "payload->'reason_codes' = '[\"appointment_checked_in\"]'::jsonb AND "
    "payload->>'status_before' IN ('Booked', 'Confirmed') AND "
    "payload->>'status_after' = 'Arrived')"
)


def _replace_diary_constraint(name: str, expression: str) -> None:
    op.drop_constraint(name, _EVENTS_TABLE, type_="check")
    op.create_check_constraint(name, _EVENTS_TABLE, expression)


def upgrade() -> None:
    op.add_column(
        _TABLE,
        sa.Column("confirmation_evidence_hash", sa.String(length=128), nullable=True),
    )
    op.add_column(
        _TABLE,
        sa.Column(
            "confirmation_evidence_consumed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.create_index(
        "uq_appt_cmd_idem_evidence_hash",
        _TABLE,
        ["practice_id", "operation_id", "confirmation_evidence_hash"],
        unique=True,
        postgresql_where=sa.text("confirmation_evidence_hash IS NOT NULL"),
    )
    op.drop_constraint(
        "ck_appt_cmd_idem_completed_create_correlation",
        _TABLE,
        type_="check",
    )
    op.create_check_constraint(
        "ck_appt_cmd_idem_completed_create_correlation",
        _TABLE,
        _CURRENT_CORRELATION,
    )
    op.create_check_constraint(
        "ck_appt_cmd_idem_completed_check_in_evidence",
        _TABLE,
        _CHECK_IN_EVIDENCE,
    )

    _replace_diary_constraint("ck_diary_committed_events_type", _CURRENT_TYPE)
    _replace_diary_constraint("ck_diary_committed_events_schema", _CURRENT_SCHEMA)
    _replace_diary_constraint(
        "ck_diary_committed_events_payload_allowlist", _CURRENT_PAYLOAD
    )


def downgrade() -> None:
    _replace_diary_constraint(
        "ck_diary_committed_events_payload_allowlist", _PRIOR_PAYLOAD
    )
    _replace_diary_constraint("ck_diary_committed_events_schema", _PRIOR_SCHEMA)
    _replace_diary_constraint("ck_diary_committed_events_type", _PRIOR_TYPE)

    op.drop_constraint(
        "ck_appt_cmd_idem_completed_check_in_evidence",
        _TABLE,
        type_="check",
    )
    op.drop_constraint(
        "ck_appt_cmd_idem_completed_create_correlation",
        _TABLE,
        type_="check",
    )
    op.create_check_constraint(
        "ck_appt_cmd_idem_completed_create_correlation",
        _TABLE,
        _PRIOR_CORRELATION,
    )
    op.drop_index("uq_appt_cmd_idem_evidence_hash", table_name=_TABLE)
    op.drop_column(_TABLE, "confirmation_evidence_consumed_at")
    op.drop_column(_TABLE, "confirmation_evidence_hash")
