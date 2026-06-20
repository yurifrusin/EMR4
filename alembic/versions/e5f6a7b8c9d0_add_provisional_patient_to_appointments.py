"""Add provisional patient name to appointments; make patient_id nullable.

Supports provisional bookings (phone/walk-in) where only a free-text name
is known at booking time. patient_id is linked later when the record is found.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "appointments", "patient_id",
        existing_type=UUID(as_uuid=True),
        nullable=True,
        existing_nullable=False,
    )
    op.add_column(
        "appointments",
        sa.Column("patient_name_provisional", sa.String(200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("appointments", "patient_name_provisional")
    # NOTE: downgrade will fail if any appointment has patient_id IS NULL.
    op.alter_column(
        "appointments", "patient_id",
        existing_type=UUID(as_uuid=True),
        nullable=False,
        existing_nullable=True,
    )
