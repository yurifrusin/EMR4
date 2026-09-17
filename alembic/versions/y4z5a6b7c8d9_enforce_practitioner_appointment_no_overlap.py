"""Enforce practitioner appointment non-overlap across all locations.

Revision ID: y4z5a6b7c8d9
Revises: x3y4z5a6b7c8
Create Date: 2026-09-17

The invariant is tenant- and practitioner-scoped. Location is intentionally
absent. Blocking appointments use half-open actual-instant ranges, so an
appointment may start exactly when another ends.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "y4z5a6b7c8d9"
down_revision: Union[str, Sequence[str], None] = "x3y4z5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


EXCLUSION_NAME = "ex_appointments_practice_practitioner_no_overlap"
DURATION_CHECK_NAME = "ck_appointments_duration_minutes_1_480"
FINITE_START_CHECK_NAME = "ck_appointments_start_time_finite"
FINITE_END_CHECK_NAME = "ck_appointments_end_time_finite"
BLOCKING_STATUS_PREDICATE = (
    "status IN ('Booked', 'Confirmed', 'Arrived', 'InConsult', 'Completed')"
)
APPOINTMENT_RANGE_SQL = (
    "pg_catalog.tstzrange("
    "start_time, "
    "(((start_time AT TIME ZONE 'UTC') + "
    "duration_minutes * INTERVAL '1 minute') AT TIME ZONE 'UTC'), "
    "'[)')"
)


def upgrade() -> None:
    # Keep object and operator-class resolution deterministic. The explicit
    # UTC round trip converts to timestamp-without-time-zone before adding the
    # minute-only interval, avoiding session-TimeZone/DST calendar arithmetic.
    op.execute("SET LOCAL search_path TO pg_catalog, public")

    # Refuse malformed or conflicting existing data before adding any object.
    # PostgreSQL transactional DDL then leaves both data and schema unchanged.
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM public.appointments
                WHERE practice_id IS NULL
                   OR practitioner_id IS NULL
                   OR start_time IS NULL
                   OR NOT pg_catalog.isfinite(start_time)
                   OR duration_minutes IS NULL
                   OR duration_minutes NOT BETWEEN 1 AND 480
                   OR status IS NULL
            ) THEN
                RAISE EXCEPTION
                    'appointments contain null, infinite, or invalid scheduling values'
                    USING ERRCODE = '23514';
            END IF;

            BEGIN
                PERFORM {APPOINTMENT_RANGE_SQL}
                FROM public.appointments;
            EXCEPTION
                WHEN datetime_field_overflow THEN
                    RAISE EXCEPTION
                        'appointment duration produces an out-of-range end instant'
                        USING ERRCODE = '22008';
            END;

            IF EXISTS (
                SELECT 1
                FROM public.appointments AS earlier
                JOIN public.appointments AS later
                  ON earlier.id < later.id
                 AND earlier.practice_id = later.practice_id
                 AND earlier.practitioner_id = later.practitioner_id
                WHERE earlier.{BLOCKING_STATUS_PREDICATE}
                  AND later.{BLOCKING_STATUS_PREDICATE}
                  AND (
                      pg_catalog.tstzrange(
                          earlier.start_time,
                          (((earlier.start_time AT TIME ZONE 'UTC') +
                            earlier.duration_minutes * INTERVAL '1 minute')
                           AT TIME ZONE 'UTC'),
                          '[)'
                      )
                      &&
                      pg_catalog.tstzrange(
                          later.start_time,
                          (((later.start_time AT TIME ZONE 'UTC') +
                            later.duration_minutes * INTERVAL '1 minute')
                           AT TIME ZONE 'UTC'),
                          '[)'
                      )
                  )
            ) THEN
                RAISE EXCEPTION
                    'existing blocking appointments overlap for a practice and practitioner'
                    USING
                        ERRCODE = '23P01',
                        CONSTRAINT = '{EXCLUSION_NAME}';
            END IF;
        END;
        $$
        """
    )

    # btree_gist supplies GiST equality for UUID. A non-public installation is
    # refused rather than relying on ambient search_path or changing ownership.
    op.execute(
        """
        DO $$
        DECLARE
            extension_schema text;
        BEGIN
            SELECT namespace.nspname
              INTO extension_schema
              FROM pg_catalog.pg_extension AS extension
              JOIN pg_catalog.pg_namespace AS namespace
                ON namespace.oid = extension.extnamespace
             WHERE extension.extname = 'btree_gist';

            IF extension_schema IS NOT NULL
               AND extension_schema <> 'public' THEN
                RAISE EXCEPTION
                    'btree_gist must be installed in public; found in %',
                    extension_schema
                    USING ERRCODE = '55000';
            END IF;
        END;
        $$
        """
    )
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public")

    # NOT VALID plus explicit validation gives named rejection points for
    # legacy rows. Subsequent ALTER statements retain the table lock, and the
    # final exclusion build validates every row, including a writer that raced
    # the initial read-only preflight.
    op.execute(
        f"""
        ALTER TABLE public.appointments
        ADD CONSTRAINT {DURATION_CHECK_NAME}
        CHECK (duration_minutes BETWEEN 1 AND 480)
        NOT VALID
        """
    )
    op.execute(
        f"""
        ALTER TABLE public.appointments
        VALIDATE CONSTRAINT {DURATION_CHECK_NAME}
        """
    )
    op.execute(
        f"""
        ALTER TABLE public.appointments
        ADD CONSTRAINT {FINITE_START_CHECK_NAME}
        CHECK (pg_catalog.isfinite(start_time))
        NOT VALID
        """
    )
    op.execute(
        f"""
        ALTER TABLE public.appointments
        VALIDATE CONSTRAINT {FINITE_START_CHECK_NAME}
        """
    )
    # Apply endpoint validity to non-blocking rows too; the partial exclusion
    # alone would not evaluate their end instant after installation.
    op.execute(
        f"""
        ALTER TABLE public.appointments
        ADD CONSTRAINT {FINITE_END_CHECK_NAME}
        CHECK (pg_catalog.isfinite(
            (((start_time AT TIME ZONE 'UTC') +
              duration_minutes * INTERVAL '1 minute') AT TIME ZONE 'UTC')))
        NOT VALID
        """
    )
    op.execute(
        f"ALTER TABLE public.appointments VALIDATE CONSTRAINT {FINITE_END_CHECK_NAME}"
    )
    op.alter_column(
        "appointments",
        "duration_minutes",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column("appointments", "status", nullable=False)

    op.execute(
        f"""
        ALTER TABLE public.appointments
        ADD CONSTRAINT {EXCLUSION_NAME}
        EXCLUDE USING gist (
            practice_id WITH =,
            practitioner_id WITH =,
            ({APPOINTMENT_RANGE_SQL}) WITH &&
        )
        WHERE ({BLOCKING_STATUS_PREDICATE})
        NOT DEFERRABLE
        """
    )


def downgrade() -> None:
    op.execute(
        f"ALTER TABLE public.appointments DROP CONSTRAINT {FINITE_END_CHECK_NAME}"
    )
    # Remove only this revision's constraint/nullability changes. Existing
    # values remain untouched and btree_gist is retained as a shared extension.
    op.execute(
        f"""
        ALTER TABLE public.appointments
        DROP CONSTRAINT {EXCLUSION_NAME}
        """
    )
    op.execute(
        "ALTER TABLE public.appointments "
        "ALTER COLUMN status DROP NOT NULL"
    )
    op.execute(
        "ALTER TABLE public.appointments "
        "ALTER COLUMN duration_minutes DROP NOT NULL"
    )
    op.execute(
        f"""
        ALTER TABLE public.appointments
        DROP CONSTRAINT {FINITE_START_CHECK_NAME}
        """
    )
    op.execute(
        f"""
        ALTER TABLE public.appointments
        DROP CONSTRAINT {DURATION_CHECK_NAME}
        """
    )
