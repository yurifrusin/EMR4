"""Add location_id FK to rooms, waiting_areas, and diary_templates for multi-location support.

Removes the single-template-per-practice constraint (diary_templates.practice_id UNIQUE)
and replaces it with two partial unique indexes so each location can have its own
template while still supporting a single practice-wide fallback (location_id IS NULL).

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-06-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from alembic import op

revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # rooms: nullable location_id FK
    op.add_column("rooms", sa.Column(
        "location_id", UUID(as_uuid=True),
        sa.ForeignKey("practice_locations.id"), nullable=True,
    ))
    op.create_index("ix_rooms_location_id", "rooms", ["location_id"])

    # waiting_areas: nullable location_id FK
    op.add_column("waiting_areas", sa.Column(
        "location_id", UUID(as_uuid=True),
        sa.ForeignKey("practice_locations.id"), nullable=True,
    ))
    op.create_index("ix_waiting_areas_location_id", "waiting_areas", ["location_id"])

    # diary_templates: nullable location_id FK + replace the column-level unique
    op.add_column("diary_templates", sa.Column(
        "location_id", UUID(as_uuid=True),
        sa.ForeignKey("practice_locations.id"), nullable=True,
    ))
    # Drop the UNIQUE constraint created by unique=True in the original create_table
    op.drop_constraint("diary_templates_practice_id_key", "diary_templates", type_="unique")
    # One practice-wide template per practice (location_id NULL)
    op.execute(
        "CREATE UNIQUE INDEX uq_diary_templates_practice_no_loc "
        "ON diary_templates (practice_id) WHERE location_id IS NULL"
    )
    # One template per (practice, location) when location is set
    op.execute(
        "CREATE UNIQUE INDEX uq_diary_templates_practice_loc "
        "ON diary_templates (practice_id, location_id) WHERE location_id IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_diary_templates_practice_loc")
    op.execute("DROP INDEX IF EXISTS uq_diary_templates_practice_no_loc")
    op.create_unique_constraint(
        "diary_templates_practice_id_key", "diary_templates", ["practice_id"]
    )
    op.drop_column("diary_templates", "location_id")

    op.drop_index("ix_waiting_areas_location_id", table_name="waiting_areas")
    op.drop_column("waiting_areas", "location_id")

    op.drop_index("ix_rooms_location_id", table_name="rooms")
    op.drop_column("rooms", "location_id")
