"""Add and backfill Account and a single-role Membership bridge.

Revision ID: c8d9e0f1a2b3
Revises: b7c8d9e0f1a2

Inert candidate until independently reviewed and admitted with login cutover.
No User column, credential, identity, role, generation or constraint is changed.
"""
from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c8d9e0f1a2b3"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None


def _prepare_transaction():
    if context.is_offline_mode():
        raise RuntimeError("account backfill requires an online transaction")
    connection = op.get_bind()
    if not connection.in_transaction():
        raise RuntimeError("account backfill requires one transaction")
    isolation = connection.execute(sa.text(
        "SELECT current_setting('transaction_isolation')"
    )).scalar_one()
    if isolation != "read committed":
        raise RuntimeError("account backfill requires read committed isolation")
    op.execute("SET LOCAL search_path TO pg_catalog, public")
    for setting, cap in (("lock_timeout", 5000), ("statement_timeout", 60000)):
        current = connection.execute(sa.text(
            "SELECT setting::bigint FROM pg_catalog.pg_settings WHERE name = :name"
        ), {"name": setting}).scalar_one()
        if current < 0:
            raise RuntimeError("invalid migration timeout setting")
        connection.execute(sa.text(
            "SELECT pg_catalog.set_config(:name, :value, true)"
        ), {"name": setting, "value": str(min(current, cap) if current else cap)})
    # A role unable to see every source row must fail, never silently backfill
    # a filtered tenant subset. Do not use a product application connection.
    op.execute("SET LOCAL row_security TO off")
    op.execute("LOCK TABLE public.practices IN SHARE ROW EXCLUSIVE MODE")
    op.execute("LOCK TABLE public.users IN SHARE ROW EXCLUSIVE MODE")
    return connection


def upgrade():
    connection = _prepare_transaction()
    # Complete checks precede all DDL and inserts; messages contain no emails,
    # hashes, user IDs or counts. Normalization is PostgreSQL lower(btrim()).
    invalid = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM public.users
            WHERE btrim(email) = '' OR is_active IS NULL
               OR authority_generation IS NULL OR authority_generation < 1
        )
    """)).scalar_one()
    if invalid:
        raise RuntimeError("account backfill requires valid explicit legacy state")
    collision = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM public.users GROUP BY lower(btrim(email))
            HAVING count(*) > 1
        )
    """)).scalar_one()
    if collision:
        raise RuntimeError("account backfill normalized-email collision")

    uid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "accounts",
        sa.Column("id", uid, primary_key=True),
        sa.Column("normalized_email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "normalized_email <> '' AND normalized_email = lower(btrim(normalized_email))",
            name="ck_accounts_normalized_email",
        ), schema="public",
    )
    op.create_table(
        "practice_memberships",
        sa.Column("id", uid, primary_key=True),
        sa.Column("account_id", uid, sa.ForeignKey("public.accounts.id"), nullable=False),
        sa.Column("practice_id", uid, sa.ForeignKey("public.practices.id"), nullable=False),
        sa.Column("legacy_user_id", uid, nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("authority_generation", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("account_id", "practice_id", name="uq_membership_account_practice"),
        sa.ForeignKeyConstraint(
            ["practice_id", "legacy_user_id"], ["public.users.practice_id", "public.users.id"],
            name="fk_membership_practice_user",
        ),
        sa.CheckConstraint("authority_generation >= 1", name="ck_membership_generation_positive"),
        schema="public",
    )
    op.create_index("ix_memberships_practice_id", "practice_memberships", ["practice_id"], schema="public")
    op.create_table(
        "practice_membership_roles",
        sa.Column("membership_id", uid, sa.ForeignKey("public.practice_memberships.id"), primary_key=True),
        sa.Column("role", sa.String(32), nullable=False),
        sa.CheckConstraint(
            "role IN ('GP', 'Receptionist', 'Nurse', 'Admin', 'PracticeOwner')",
            name="ck_membership_role_existing_user_role",
        ), schema="public",
    )
    # Reuse each legacy UUID as the new tables' initial key only to avoid any
    # extension dependency. These remain distinct typed identities; callers
    # must join explicit columns, never infer identity equality for new rows.
    op.execute("""
        INSERT INTO public.accounts (id, normalized_email, password_hash, is_active, created_at)
        SELECT id, lower(btrim(email)), password_hash, is_active, created_at FROM public.users
    """)
    op.execute("""
        INSERT INTO public.practice_memberships
            (id, account_id, practice_id, legacy_user_id, is_active, authority_generation, created_at)
        SELECT id, id, practice_id, id, is_active, authority_generation, created_at FROM public.users
    """)
    op.execute("""
        INSERT INTO public.practice_membership_roles (membership_id, role)
        SELECT id, role::text FROM public.users
    """)
    for table in ("practice_memberships", "practice_membership_roles"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY")
    predicate = (
        "practice_id = NULLIF(pg_catalog.current_setting('app.current_practice_id', true), '')::uuid"
    )
    op.execute(
        "CREATE POLICY tenant_isolation ON public.practice_memberships FOR ALL TO PUBLIC "
        f"USING ({predicate}) WITH CHECK ({predicate})"
    )
    role_predicate = (
        "EXISTS (SELECT 1 FROM public.practice_memberships AS membership "
        "WHERE membership.id = membership_id AND " + predicate + ")"
    )
    op.execute(
        "CREATE POLICY tenant_isolation ON public.practice_membership_roles FOR ALL TO PUBLIC "
        f"USING ({role_predicate}) WITH CHECK ({role_predicate})"
    )


def downgrade():
    # Account/bootstrap may have introduced records with no legacy equivalent.
    # Never DROP or reverse-copy credentials. Even an apparently empty database
    # needs a separately reviewed rollback plan rather than a destructive path.
    raise RuntimeError("account bridge retained; downgrade requires reviewed non-destructive recovery")
