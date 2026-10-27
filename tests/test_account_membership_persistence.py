"""Proposed PostgreSQL scenarios, NOT executed acceptance evidence.

Required future isolated harness fixture `account_bridge_case` is intentionally
not supplied by this source batch. It must provide conn (migration-owner
connection), upgrade()/downgrade() bound to the exact revision, and seed_user()
that creates synthetic practices/users at b7c8d9e0f1a2. upgrade() must use the
current transaction; no fixture may discover a default URL or existing DB.
`as_tenant(practice_id)` must use a separate non-owner/non-BYPASSRLS role and
return a connection with SET LOCAL tenant context in its own transaction.
Admission must bind that fixture and classify its imports before collection.
"""
import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError


def scalar(case, sql, **params):
    return case.conn.execute(sa.text(sql), params).scalar_one()


def test_backfill_preserves_legacy_and_copies_exact_credentials(account_bridge_case):
    c = account_bridge_case
    one = c.seed_user(email="  Owner@Example.test  ", role="PracticeOwner", active=True, generation=7)
    two = c.seed_user(email="staff@example.test", role="Receptionist", active=False, generation=3)
    before = c.conn.execute(sa.text("SELECT row_to_json(u)::text FROM users u ORDER BY id")).scalars().all()
    c.upgrade()
    assert c.conn.execute(sa.text("SELECT row_to_json(u)::text FROM users u ORDER BY id")).scalars().all() == before
    for legacy in (one, two):
        row = c.conn.execute(sa.text("""
            SELECT a.normalized_email, a.password_hash = u.password_hash AS same_verifier,
                   a.is_active = u.is_active AS same_account_active,
                   m.is_active = u.is_active AS same_membership_active,
                   m.authority_generation = u.authority_generation AS same_generation,
                   m.practice_id = u.practice_id AS same_practice,
                   r.role = u.role::text AS same_role
            FROM users u JOIN practice_memberships m ON m.legacy_user_id = u.id
            JOIN accounts a ON a.id = m.account_id
            JOIN practice_membership_roles r ON r.membership_id = m.id
            WHERE u.id = :id
        """), {"id": legacy.user_id}).mappings().one()
        assert row["normalized_email"] == legacy.email.strip().lower()  # ASCII synthetic inputs only.
        assert all(row[key] for key in row if key != "normalized_email")


def test_collision_fails_before_any_schema_or_partial_backfill(account_bridge_case):
    c = account_bridge_case
    c.seed_user(email="Owner@Example.test")
    c.seed_user(email=" owner@example.test ")
    with c.conn.begin_nested():
        with pytest.raises(RuntimeError, match="normalized-email collision") as error:
            c.upgrade()
        assert "example.test" not in str(error.value)
        assert scalar(c, "SELECT to_regclass('public.accounts') IS NULL")
        assert scalar(c, "SELECT to_regclass('public.practice_memberships') IS NULL")
        assert scalar(c, "SELECT count(*) FROM users") == 2


def test_cross_practice_legacy_link_rejected_even_for_migration_owner(account_bridge_case):
    c = account_bridge_case
    one = c.seed_user(email="a@example.test")
    two = c.seed_user(email="b@example.test")
    assert one.practice_id != two.practice_id
    c.upgrade()
    with pytest.raises(IntegrityError):
        with c.conn.begin_nested():
            c.conn.execute(sa.text("""
                UPDATE practice_memberships SET practice_id = :other WHERE legacy_user_id = :user
            """), {"other": two.practice_id, "user": one.user_id})


def test_no_orphan_or_duplicate_membership_or_unbounded_role(account_bridge_case):
    c = account_bridge_case
    one = c.seed_user(email="a@example.test")
    two = c.seed_user(email="b@example.test")
    c.upgrade()
    invalid_statements = [
        ("DELETE FROM accounts WHERE id = :id", {"id": one.user_id}),
        ("DELETE FROM users WHERE id = :id", {"id": one.user_id}),
        ("UPDATE practice_memberships SET account_id = :a, practice_id = :p WHERE legacy_user_id = :u",
         {"a": one.user_id, "p": one.practice_id, "u": two.user_id}),
        ("UPDATE practice_membership_roles SET role = 'SuperUser' WHERE membership_id = :id", {"id": one.user_id}),
        ("UPDATE practice_memberships SET authority_generation = 0 WHERE legacy_user_id = :id", {"id": one.user_id}),
    ]
    for statement, params in invalid_statements:
        with pytest.raises(IntegrityError):
            with c.conn.begin_nested():
                c.conn.execute(sa.text(statement), params)


def test_global_user_email_constraint_remains(account_bridge_case):
    c = account_bridge_case
    c.seed_user(email="same@example.test")
    c.upgrade()
    with pytest.raises(IntegrityError):
        with c.conn.begin_nested():
            c.seed_user(email="same@example.test")


def test_migration_transaction_rollback_and_retained_data_downgrade(account_bridge_case):
    c = account_bridge_case
    c.seed_user(email="a@example.test")
    savepoint = c.conn.begin_nested()
    c.upgrade()
    assert scalar(c, "SELECT count(*) FROM accounts") == 1
    savepoint.rollback()
    assert scalar(c, "SELECT to_regclass('public.accounts') IS NULL")
    assert scalar(c, "SELECT count(*) FROM users") == 1
    c.upgrade()
    with pytest.raises(RuntimeError, match="non-destructive recovery"):
        c.downgrade()
    assert scalar(c, "SELECT count(*) FROM accounts") == 1
    assert scalar(c, "SELECT count(*) FROM practice_memberships") == 1


def test_tenant_role_sees_only_selected_memberships_and_roles(account_bridge_case):
    c = account_bridge_case
    one = c.seed_user(email="a@example.test")
    two = c.seed_user(email="b@example.test")
    c.upgrade()
    # Harness must expose the setup to the tenant role without relaxing FORCE
    # RLS; its transaction/commit strategy is part of the future launch review.
    with c.as_tenant(one.practice_id) as tenant:
        assert tenant.execute(sa.text("SELECT legacy_user_id FROM practice_memberships")).scalars().all() == [one.user_id]
        assert tenant.execute(sa.text("SELECT membership_id FROM practice_membership_roles")).scalars().all() == [one.user_id]
        assert tenant.execute(sa.text("SELECT count(*) FROM practice_memberships WHERE legacy_user_id = :id"), {"id": two.user_id}).scalar_one() == 0
