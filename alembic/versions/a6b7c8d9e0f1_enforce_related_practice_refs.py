"""Bind selected direct clinical and appointment references to their practice.

Revision ID: a6b7c8d9e0f1
Revises: z5a6b7c8d9e0

Only direct same-practice references are added. Existing single-column foreign
keys, nullability, RLS policies, and application writers are unchanged.
"""

from alembic import context, op
import sqlalchemy as sa


revision = "a6b7c8d9e0f1"
down_revision = "z5a6b7c8d9e0"
branch_labels = None
depends_on = None


# Acquire all referenced and referencing tables in one stable order before any
# history scan. SHARE ROW EXCLUSIVE excludes concurrent INSERT/UPDATE/DELETE.
LOCKED_TABLES = (
    "appointment_types",
    "appointments",
    "clinical_diagnoses",
    "encounters",
    "invoices",
    "mbs_claims",
    "patients",
    "practice_locations",
    "practitioners",
    "prescriptions",
    "waiting_areas",
)

# appointments(practice_id,id) was already created by m2n3o4p5q6r7.
NEW_UNIQUE_KEYS = (
    ("appointment_types", "uq_appointment_types_practice_id_id"),
    ("encounters", "uq_encounters_practice_id_id"),
    ("patients", "uq_patients_practice_id_id"),
    ("practice_locations", "uq_practice_locations_practice_id_id"),
    ("practitioners", "uq_practitioners_practice_id_id"),
    ("waiting_areas", "uq_waiting_areas_practice_id_id"),
)

# All identifiers are literal migration-owned identifiers, never input data.
# The source columns are (practice_id, target_id); target columns are
# (practice_id, id). MATCH SIMPLE leaves existing nullable targets optional.
NEW_FOREIGN_KEYS = (
    ("fk_appointments_practice_patient", "appointments", "patient_id", "patients"),
    ("fk_appointments_practice_practitioner", "appointments", "practitioner_id", "practitioners"),
    ("fk_appointments_practice_location", "appointments", "location_id", "practice_locations"),
    ("fk_appointments_practice_type", "appointments", "appointment_type_id", "appointment_types"),
    ("fk_appointments_practice_waiting_area", "appointments", "waiting_area_id", "waiting_areas"),
    ("fk_encounters_practice_patient", "encounters", "patient_id", "patients"),
    ("fk_encounters_practice_practitioner", "encounters", "practitioner_id", "practitioners"),
    ("fk_encounters_practice_appointment", "encounters", "appointment_id", "appointments"),
    ("fk_clinical_diagnoses_practice_patient", "clinical_diagnoses", "patient_id", "patients"),
    ("fk_clinical_diagnoses_practice_encounter", "clinical_diagnoses", "encounter_id", "encounters"),
    ("fk_prescriptions_practice_patient", "prescriptions", "patient_id", "patients"),
    ("fk_prescriptions_practice_encounter", "prescriptions", "encounter_id", "encounters"),
    ("fk_prescriptions_practice_prescriber", "prescriptions", "prescribed_by", "practitioners"),
    ("fk_mbs_claims_practice_patient", "mbs_claims", "patient_id", "patients"),
    ("fk_mbs_claims_practice_encounter", "mbs_claims", "encounter_id", "encounters"),
    ("fk_mbs_claims_practice_practitioner", "mbs_claims", "practitioner_id", "practitioners"),
    ("fk_invoices_practice_patient", "invoices", "patient_id", "patients"),
    ("fk_invoices_practice_encounter", "invoices", "encounter_id", "encounters"),
)


def _prepare_transaction() -> sa.engine.Connection:
    if context.is_offline_mode():
        raise RuntimeError("related-practice migration requires an online transaction")
    connection = op.get_bind()
    # Read-committed gives each post-lock preflight a fresh complete snapshot.
    isolation = connection.execute(sa.text("SELECT current_setting('transaction_isolation')")).scalar_one()
    if isolation != "read committed":
        raise RuntimeError("related-practice migration requires read committed isolation")
    op.execute("SET LOCAL search_path TO pg_catalog, public")
    # Cap rather than loosen a stricter timeout supplied by the reviewed outer
    # operation. pg_settings.setting uses milliseconds for these two settings.
    for setting, cap_ms in (("lock_timeout", 5_000), ("statement_timeout", 60_000)):
        current_ms = connection.execute(
            sa.text(
                "SELECT setting::bigint FROM pg_catalog.pg_settings "
                "WHERE name = :setting"
            ),
            {"setting": setting},
        ).scalar_one()
        if current_ms < 0:
            raise RuntimeError("invalid migration timeout setting")
        applied_ms = min(current_ms, cap_ms) if current_ms else cap_ms
        connection.execute(
            sa.text("SELECT pg_catalog.set_config(:setting, :value, true)"),
            {"setting": setting, "value": str(applied_ms)},
        ).scalar_one()
    # This setting errors instead of silently filtering a scan through FORCE
    # RLS when the migration role lacks a complete view of a source table.
    op.execute("SET LOCAL row_security TO off")
    return connection


def _lock_tables() -> None:
    for table in LOCKED_TABLES:
        op.execute(f'LOCK TABLE public."{table}" IN SHARE ROW EXCLUSIVE MODE')


def _preflight_all_references(connection: sa.engine.Connection) -> None:
    for name, child, column, parent in NEW_FOREIGN_KEYS:
        mismatch = connection.execute(
            sa.text(
                f'SELECT EXISTS (SELECT 1 FROM public."{child}" AS child '
                f'LEFT JOIN public."{parent}" AS parent '
                f'ON parent.id = child."{column}" '
                f'WHERE child."{column}" IS NOT NULL '
                'AND (parent.id IS NULL '
                'OR parent.practice_id IS DISTINCT FROM child.practice_id))'
            )
        ).scalar_one()
        if mismatch:
            # Do not put identifiers of patients or clinical records in logs.
            raise RuntimeError(f"existing related-practice mismatch: {name}")


def upgrade() -> None:
    connection = _prepare_transaction()
    _lock_tables()
    _preflight_all_references(connection)
    for table, name in NEW_UNIQUE_KEYS:
        op.execute(
            f'ALTER TABLE public."{table}" ADD CONSTRAINT "{name}" '
            'UNIQUE (practice_id, id)'
        )
    for name, child, column, parent in NEW_FOREIGN_KEYS:
        op.execute(
            f'ALTER TABLE public."{child}" ADD CONSTRAINT "{name}" '
            f'FOREIGN KEY (practice_id, "{column}") '
            f'REFERENCES public."{parent}" (practice_id, id) '
            'MATCH SIMPLE ON UPDATE NO ACTION ON DELETE NO ACTION NOT DEFERRABLE'
        )


def downgrade() -> None:
    _prepare_transaction()
    _lock_tables()
    for name, child, _, _ in reversed(NEW_FOREIGN_KEYS):
        # PostgreSQL's default RESTRICT refuses external dependents.
        op.execute(f'ALTER TABLE public."{child}" DROP CONSTRAINT "{name}" RESTRICT')
    for table, name in reversed(NEW_UNIQUE_KEYS):
        op.execute(f'ALTER TABLE public."{table}" DROP CONSTRAINT "{name}" RESTRICT')
