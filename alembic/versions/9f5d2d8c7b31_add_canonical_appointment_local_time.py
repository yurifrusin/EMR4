"""add_canonical_appointment_local_time

Revision ID: 9f5d2d8c7b31
Revises: 6322b34e4de4
Create Date: 2026-06-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f5d2d8c7b31"
down_revision: Union[str, Sequence[str], None] = "6322b34e4de4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("appointments", sa.Column("appointment_date", sa.Date(), nullable=True))
    op.add_column("appointments", sa.Column("start_time_local", sa.Time(), nullable=True))

    # Legacy clients treated start_time as clinic wall-clock time even though the
    # column was timestamptz. Preserve that wall time in the canonical fields,
    # then rewrite start_time as the UTC instant derived from the practice zone.
    op.execute(
        """
        WITH canonical AS (
            SELECT
                a.id,
                (a.start_time AT TIME ZONE 'UTC') AS legacy_local_start,
                COALESCE(p.timezone, 'Australia/Sydney') AS practice_timezone
            FROM appointments AS a
            JOIN practices AS p ON p.id = a.practice_id
        )
        UPDATE appointments AS a
        SET
            appointment_date = canonical.legacy_local_start::date,
            start_time_local = canonical.legacy_local_start::time,
            start_time = canonical.legacy_local_start AT TIME ZONE canonical.practice_timezone
        FROM canonical
        WHERE a.id = canonical.id
          AND (a.appointment_date IS NULL OR a.start_time_local IS NULL)
        """
    )

    op.alter_column("appointments", "appointment_date", nullable=False)
    op.alter_column("appointments", "start_time_local", nullable=False)
    op.create_index(
        "ix_appointments_practice_date",
        "appointments",
        ["practice_id", "appointment_date"],
        unique=False,
    )
    op.create_index(
        "ix_appointments_practitioner_date_time",
        "appointments",
        ["practitioner_id", "appointment_date", "start_time_local"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_appointments_practitioner_date_time", table_name="appointments")
    op.drop_index("ix_appointments_practice_date", table_name="appointments")
    op.drop_column("appointments", "start_time_local")
    op.drop_column("appointments", "appointment_date")
