"""Add WaitingArea model; link to rooms and appointments.

Named physical waiting areas give Bernie and the diary UI a practice-scoped
resource to assign patients to on arrival, separate from attendance status
and practitioner/room identity.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-06-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "waiting_areas",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "practice_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practices.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_index("ix_waiting_areas_practice_id", "waiting_areas", ["practice_id"])

    op.add_column(
        "rooms",
        sa.Column(
            "default_waiting_area_id",
            UUID(as_uuid=True),
            sa.ForeignKey("waiting_areas.id"),
            nullable=True,
        ),
    )

    op.add_column(
        "appointments",
        sa.Column(
            "waiting_area_id",
            UUID(as_uuid=True),
            sa.ForeignKey("waiting_areas.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_appointments_waiting_area_id", "appointments", ["waiting_area_id"])


def downgrade() -> None:
    op.drop_index("ix_appointments_waiting_area_id", table_name="appointments")
    op.drop_column("appointments", "waiting_area_id")
    op.drop_column("rooms", "default_waiting_area_id")
    op.drop_index("ix_waiting_areas_practice_id", table_name="waiting_areas")
    op.drop_table("waiting_areas")
