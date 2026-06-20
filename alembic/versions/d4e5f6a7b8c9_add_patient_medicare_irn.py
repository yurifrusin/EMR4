"""Add Medicare IRN to patients.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("medicare_irn", sa.String(length=2), nullable=True))
    op.create_index("ix_patients_ihi_number", "patients", ["ihi_number"])


def downgrade() -> None:
    op.drop_index("ix_patients_ihi_number", table_name="patients")
    op.drop_column("patients", "medicare_irn")
