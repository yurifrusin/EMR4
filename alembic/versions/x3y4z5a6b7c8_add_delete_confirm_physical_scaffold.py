"""Add the unmounted delete-confirm physical scaffold.

Revision ID: x3y4z5a6b7c8
Revises: w2x3y4z5a6b7
Create Date: 2026-08-15

This migration is inert until separately admitted and executed. The user and
capability triggers are synchronous row invariants, not event watchers or cue
producers.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "x3y4z5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "w2x3y4z5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


GENERATION_MAX = 9223372036854775807


def upgrade() -> None:
    # --- Authority fence: users.authority_generation ---------------------
    # 1. Nullable, no default: avoid a table-rewriting semantic claim.
    op.add_column(
        "users",
        sa.Column("authority_generation", sa.BigInteger(), nullable=True),
    )
    # 2. New inserts begin at the cutover baseline one.
    op.alter_column(
        "users",
        "authority_generation",
        server_default=sa.text("1"),
    )
    # 3. Existing users receive a baseline, never fabricated chronology.
    op.execute(
        "UPDATE users SET authority_generation = 1 "
        "WHERE authority_generation IS NULL"
    )
    # 4. Validate the positive BIGINT domain before setting NOT NULL.
    op.execute(
        "ALTER TABLE users ADD CONSTRAINT "
        "ck_users_authority_generation_positive "
        "CHECK (authority_generation >= 1) NOT VALID"
    )
    op.execute(
        "ALTER TABLE users VALIDATE CONSTRAINT "
        "ck_users_authority_generation_positive"
    )
    op.alter_column("users", "authority_generation", nullable=False)
    # 5. Exact composite uniqueness required by the closed grant relation.
    op.execute(
        "ALTER TABLE users ADD CONSTRAINT uq_users_practice_id_id "
        "UNIQUE (practice_id, id)"
    )

    # --- Closed capability relation, empty at cutover --------------------
    op.create_table(
        "user_capability_grants",
        sa.Column("practice_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("capability_code", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint(
            "practice_id",
            "user_id",
            "capability_code",
            name="pk_user_capability_grants",
        ),
        sa.ForeignKeyConstraint(
            ["practice_id", "user_id"],
            ["users.practice_id", "users.id"],
            name="fk_user_capability_grants_user",
        ),
        sa.CheckConstraint(
            "capability_code IN "
            "('appointment.cancel.confirm', 'appointment.read')",
            name="ck_user_capability_grants_capability_code",
        ),
    )
    op.create_index(
        "ix_user_capability_grants_user",
        "user_capability_grants",
        ["practice_id", "user_id"],
    )

    # --- PostgreSQL-owned generation -------------------------------------
    op.execute(
        f"""
        CREATE FUNCTION emr4_user_authority_generation_guard()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_submitted bigint;
            v_advance_target text;
        BEGIN
            IF TG_OP = 'INSERT' THEN
                NEW.authority_generation := 1;
                RETURN NEW;
            END IF;

            v_submitted := NEW.authority_generation;
            NEW.authority_generation := OLD.authority_generation;

            v_advance_target := current_setting(
                'emr4.authority_advance_target', true);
            IF v_advance_target = OLD.practice_id::text || ':' || OLD.id::text
               AND v_submitted = OLD.authority_generation + 1 THEN
                IF OLD.authority_generation >= {GENERATION_MAX} THEN
                    RAISE EXCEPTION 'authority_generation overflow'
                        USING ERRCODE = '22003';
                END IF;
                NEW.authority_generation := OLD.authority_generation + 1;
            END IF;

            IF NEW.practice_id IS DISTINCT FROM OLD.practice_id
               OR NEW.role IS DISTINCT FROM OLD.role
               OR NEW.is_active IS DISTINCT FROM OLD.is_active THEN
                IF OLD.authority_generation >= {GENERATION_MAX} THEN
                    RAISE EXCEPTION 'authority_generation overflow'
                        USING ERRCODE = '22003';
                END IF;
                NEW.authority_generation := OLD.authority_generation + 1;
            END IF;

            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_users_authority_generation_guard
        BEFORE INSERT OR UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION emr4_user_authority_generation_guard()
        """
    )

    op.execute(
        """
        CREATE FUNCTION emr4_user_capability_grant_generation_guard()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_parent users%ROWTYPE;
        BEGIN
            IF TG_OP = 'DELETE' THEN
                SELECT * INTO v_parent FROM users
                WHERE practice_id = OLD.practice_id AND id = OLD.user_id
                FOR UPDATE;
                IF NOT FOUND THEN
                    RAISE EXCEPTION 'user capability grant parent user missing'
                        USING ERRCODE = '23503';
                END IF;
                PERFORM set_config(
                    'emr4.authority_advance_target',
                    OLD.practice_id::text || ':' || OLD.user_id::text,
                    true
                );
                UPDATE users
                SET authority_generation = users.authority_generation + 1
                WHERE practice_id = OLD.practice_id AND id = OLD.user_id;
                RETURN OLD;
            ELSIF TG_OP = 'INSERT' THEN
                SELECT * INTO v_parent FROM users
                WHERE practice_id = NEW.practice_id AND id = NEW.user_id
                FOR UPDATE;
                IF NOT FOUND THEN
                    RAISE EXCEPTION 'user capability grant parent user missing'
                        USING ERRCODE = '23503';
                END IF;
                PERFORM set_config(
                    'emr4.authority_advance_target',
                    NEW.practice_id::text || ':' || NEW.user_id::text,
                    true
                );
                UPDATE users
                SET authority_generation = users.authority_generation + 1
                WHERE practice_id = NEW.practice_id AND id = NEW.user_id;
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_user_capability_grants_generation
        BEFORE INSERT OR DELETE ON user_capability_grants
        FOR EACH ROW
        EXECUTE FUNCTION emr4_user_capability_grant_generation_guard()
        """
    )

    # Grant updates are rejected; reassignment is delete then insert.
    op.execute(
        """
        CREATE FUNCTION emr4_reject_user_capability_grant_update()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'user capability grant update is rejected'
                USING ERRCODE = '55000';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_user_capability_grants_reject_update
        BEFORE UPDATE ON user_capability_grants
        FOR EACH ROW
        EXECUTE FUNCTION emr4_reject_user_capability_grant_update()
        """
    )

    # --- Receipt and audit additive mapping ------------------------------
    op.add_column(
        "appointment_command_idempotency",
        sa.Column("authority_generation", sa.BigInteger(), nullable=True),
    )
    # Widen the named status-only v1 completeness constraint in place to the
    # exact two-family disjunction. The status branch is unchanged.
    op.drop_constraint(
        "ck_appt_cmd_idem_status_receipt_v1_complete",
        "appointment_command_idempotency",
        type_="check",
    )
    op.create_check_constraint(
        "ck_appt_cmd_idem_status_receipt_v1_complete",
        "appointment_command_idempotency",
        "completed_receipt_version IS NULL OR "
        "(state = 'completed' AND "
        "operation_id = 'confirmAppointmentStatusProposal' AND "
        "route_family = 'status-confirm' AND "
        "result_kind = 'confirmed_write' AND "
        "session_binding_digest IS NOT NULL AND "
        "octet_length(session_binding_digest) = 32 AND "
        "pre_state_version IS NOT NULL AND pre_state_version >= 1 AND "
        "post_state_version IS NOT NULL AND "
        "post_state_version = pre_state_version + 1 AND "
        "response_body_canonical_bytes IS NOT NULL AND "
        "octet_length(response_body_canonical_bytes) > 0 AND "
        "target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL AND "
        "response_status_code IS NOT NULL AND response_body_hash IS NOT NULL AND "
        "response_body_json IS NOT NULL) OR "
        "(state = 'completed' AND "
        "operation_id = 'confirmAppointmentDeleteProposal' AND "
        "route_family = 'delete-confirm' AND "
        "result_kind = 'confirmed_write' AND "
        "authority_generation IS NOT NULL AND authority_generation >= 1 AND "
        "session_binding_digest IS NOT NULL AND "
        "octet_length(session_binding_digest) = 32 AND "
        "pre_state_version IS NOT NULL AND pre_state_version >= 1 AND "
        "post_state_version IS NOT NULL AND "
        "post_state_version = pre_state_version + 1 AND "
        "response_body_canonical_bytes IS NOT NULL AND "
        "octet_length(response_body_canonical_bytes) > 0 AND "
        "target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL AND "
        "response_status_code IS NOT NULL AND response_body_hash IS NOT NULL AND "
        "response_body_json IS NOT NULL)",
    )

    for column in (
        sa.Column("audit_contract_version", sa.SmallInteger(), nullable=True),
        sa.Column("authority_generation", sa.BigInteger(), nullable=True),
        sa.Column("pre_state_version", sa.BigInteger(), nullable=True),
        sa.Column("post_state_version", sa.BigInteger(), nullable=True),
        sa.Column("waiting_area_before_id", UUID(as_uuid=True), nullable=True),
        sa.Column("waiting_area_after_id", UUID(as_uuid=True), nullable=True),
        sa.Column("audit_evidence_codes", JSONB(), nullable=True),
    ):
        op.add_column("appointment_audit_log", column)

    op.create_check_constraint(
        "ck_appt_audit_log_delete_v1_complete",
        "appointment_audit_log",
        "audit_contract_version IS NULL OR "
        "(audit_contract_version = 1 AND action = 'delete' AND "
        "command_id IS NOT NULL AND "
        "authority_generation IS NOT NULL AND authority_generation >= 1 AND "
        "pre_state_version IS NOT NULL AND pre_state_version >= 1 AND "
        "post_state_version IS NOT NULL AND post_state_version >= 1 AND "
        "post_state_version = pre_state_version + 1 AND "
        "status_after = 'Cancelled' AND status_reason_code IS NOT NULL AND "
        "waiting_area_after_id IS NULL AND "
        "confirmed_warnings IS NOT NULL AND "
        "jsonb_typeof(confirmed_warnings) = 'array' AND "
        "audit_evidence_codes IS NOT NULL AND "
        "jsonb_typeof(audit_evidence_codes) = 'array')",
    )

    # --- Cutover proof ---------------------------------------------------
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM users
                WHERE authority_generation IS NULL
                   OR authority_generation < 1
                   OR authority_generation > {GENERATION_MAX}
            ) THEN
                RAISE EXCEPTION 'invalid authority_generation after cutover';
            END IF;
            IF EXISTS (SELECT 1 FROM user_capability_grants) THEN
                RAISE EXCEPTION
                    'user_capability_grants must be empty after migration';
            END IF;
            IF EXISTS (
                SELECT 1 FROM user_capability_grants g
                LEFT JOIN users u
                    ON u.practice_id = g.practice_id AND u.id = g.user_id
                WHERE u.id IS NULL
            ) THEN
                RAISE EXCEPTION 'orphan user capability grant';
            END IF;
            IF EXISTS (
                SELECT 1 FROM user_capability_grants
                WHERE capability_code NOT IN
                    ('appointment.cancel.confirm', 'appointment.read')
            ) THEN
                RAISE EXCEPTION 'unknown capability code';
            END IF;
        END;
        $$
        """
    )
    # No capability row is granted and no consumer is mounted.


def downgrade() -> None:
    # Fail closed after any grant, delete-confirm receipt v1 or delete audit v1.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM user_capability_grants) THEN
                RAISE EXCEPTION
                    'user capability grant exists; forward recovery required';
            END IF;
            IF EXISTS (
                SELECT 1 FROM appointment_command_idempotency
                WHERE completed_receipt_version = 1
                  AND route_family = 'delete-confirm'
            ) THEN
                RAISE EXCEPTION
                    'delete-confirm receipt v1 exists; forward recovery required';
            END IF;
            IF EXISTS (
                SELECT 1 FROM appointment_audit_log
                WHERE audit_contract_version = 1
            ) THEN
                RAISE EXCEPTION
                    'delete audit v1 exists; forward recovery required';
            END IF;
        END;
        $$
        """
    )
    op.drop_constraint(
        "ck_appt_audit_log_delete_v1_complete",
        "appointment_audit_log",
        type_="check",
    )
    for column_name in (
        "audit_evidence_codes",
        "waiting_area_after_id",
        "waiting_area_before_id",
        "post_state_version",
        "pre_state_version",
        "authority_generation",
        "audit_contract_version",
    ):
        op.drop_column("appointment_audit_log", column_name)
    op.drop_constraint(
        "ck_appt_cmd_idem_status_receipt_v1_complete",
        "appointment_command_idempotency",
        type_="check",
    )
    op.create_check_constraint(
        "ck_appt_cmd_idem_status_receipt_v1_complete",
        "appointment_command_idempotency",
        "completed_receipt_version IS NULL OR "
        "(state = 'completed' AND "
        "operation_id = 'confirmAppointmentStatusProposal' AND "
        "route_family = 'status-confirm' AND "
        "result_kind = 'confirmed_write' AND "
        "session_binding_digest IS NOT NULL AND "
        "octet_length(session_binding_digest) = 32 AND "
        "pre_state_version IS NOT NULL AND pre_state_version >= 1 AND "
        "post_state_version IS NOT NULL AND "
        "post_state_version = pre_state_version + 1 AND "
        "response_body_canonical_bytes IS NOT NULL AND "
        "octet_length(response_body_canonical_bytes) > 0 AND "
        "target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL AND "
        "response_status_code IS NOT NULL AND response_body_hash IS NOT NULL AND "
        "response_body_json IS NOT NULL)",
    )
    op.drop_column("appointment_command_idempotency", "authority_generation")
    op.execute(
        "DROP TRIGGER trg_user_capability_grants_reject_update "
        "ON user_capability_grants"
    )
    op.execute("DROP FUNCTION emr4_reject_user_capability_grant_update()")
    op.execute(
        "DROP TRIGGER trg_user_capability_grants_generation "
        "ON user_capability_grants"
    )
    op.execute("DROP FUNCTION emr4_user_capability_grant_generation_guard()")
    op.execute(
        "DROP TRIGGER trg_users_authority_generation_guard ON users"
    )
    op.execute("DROP FUNCTION emr4_user_authority_generation_guard()")
    op.drop_index(
        "ix_user_capability_grants_user",
        table_name="user_capability_grants",
    )
    op.drop_table("user_capability_grants")
    op.execute("ALTER TABLE users DROP CONSTRAINT uq_users_practice_id_id")
    op.drop_constraint(
        "ck_users_authority_generation_positive",
        "users",
        type_="check",
    )
    op.drop_column("users", "authority_generation")
