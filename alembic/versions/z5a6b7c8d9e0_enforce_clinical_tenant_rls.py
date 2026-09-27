"""Enforce practice isolation for six clinical tables.

Revision ID: z5a6b7c8d9e0
Revises: y4z5a6b7c8d9
Create Date: 2026-09-27

Application connections must use the separately provisioned restricted role.
Login/bootstrap tables and mixed-purpose audit records retain their contracts.
"""

from alembic import op


revision = "z5a6b7c8d9e0"
down_revision = "y4z5a6b7c8d9"
branch_labels = None
depends_on = None

TABLES = (
    "patients",
    "encounters",
    "clinical_diagnoses",
    "prescriptions",
    "mbs_claims",
    "invoices",
)
TENANT_PREDICATE = (
    "practice_id = "
    "NULLIF(pg_catalog.current_setting('app.current_practice_id', true), '')::uuid"
)


def upgrade() -> None:
    op.execute("SET LOCAL search_path TO pg_catalog, public")
    for table in TABLES:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation ON public.{table} "
            f"FOR ALL TO PUBLIC USING ({TENANT_PREDICATE}) "
            f"WITH CHECK ({TENANT_PREDICATE})"
        )


def downgrade() -> None:
    op.execute("SET LOCAL search_path TO pg_catalog, public")
    for table in reversed(TABLES):
        op.execute(f"DROP POLICY tenant_isolation ON public.{table}")
        op.execute(f"ALTER TABLE public.{table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY")
