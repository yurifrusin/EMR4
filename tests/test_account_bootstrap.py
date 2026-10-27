"""Authored synthetic acceptance scenarios; no results or runtime binding.

The future account_bootstrap_case fixture must inject independently reviewed
tenant and auth-only session factories into a local ASGI app against one fresh
disposable PostgreSQL database. No URL discovery, project conftest or live
provider is authorised by this file. `admin` is a separate controlled test-only
connection; production endpoints must never receive it. Fixture helpers expose
literal synthetic identity and DB mutation operations only.
"""
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError


def register(c, email="new@example.test"):
    response = c.client.post("/api/v1/auth/register", json={
        "email": email, "password": "Synthetic-Only-Passphrase-29",
    })
    assert response.status_code == 200
    return response.json()["access_token"]


def bearer(token):
    return {"Authorization": "Bearer " + token}


def test_practice_less_bootstrap_cannot_use_tenant_route(account_bootstrap_case):
    c = account_bootstrap_case
    bootstrap = register(c)
    claims = c.decode_for_test(bootstrap)
    assert claims["aud"] == "raisa-account-bootstrap"
    assert not ({"sub", "membership_id", "practice_id", "role", "authority_generation"} & claims.keys())
    assert c.client.get("/api/v1/auth/me", headers=bearer(bootstrap)).status_code == 401
    assert c.client.get("/api/v1/auth/memberships", headers=bearer(bootstrap)).json() == []


def test_atomic_first_owner_and_audit(account_bootstrap_case):
    c = account_bootstrap_case
    bootstrap = register(c)
    result = c.client.post("/api/v1/auth/practices", json={"name": "Synthetic Practice A"}, headers=bearer(bootstrap))
    assert result.status_code == 200
    selected = result.json()["access_token"]
    claims = c.decode_for_test(selected)
    assert claims["aud"] == "raisa-tenant"
    row = c.current_identity_for_test(claims["membership_id"])
    assert str(row.legacy_user_id) == claims["sub"]
    assert str(row.account_id) == claims["account_id"]
    assert row.user_role == row.membership_role == "PracticeOwner"
    assert row.user_generation == row.membership_generation == claims["authority_generation"]
    assert row.user_password_hash.startswith("!account-only:")
    assert c.client.get("/api/v1/auth/me", headers=bearer(selected)).status_code == 200
    assert c.committed_audit_codes_for_test(row.account_id).count("practice_created") == 1
    assert c.client.post("/api/v1/auth/practices", json={"name": "Second"}, headers=bearer(bootstrap)).status_code == 409


def test_first_owner_failure_leaves_no_orphan_or_success_audit(account_bootstrap_case):
    c = account_bootstrap_case
    bootstrap = register(c)
    before = c.owned_counts_for_test()
    # The fixture may inject a separately reviewed DB rejection after Practice
    # insert; the same function transaction must roll every insert back.
    with c.fail_membership_insert_for_test():
        response = c.client.post("/api/v1/auth/practices", json={"name": "Rejected"}, headers=bearer(bootstrap))
    assert response.status_code >= 400
    assert c.owned_counts_for_test() == before


def test_account_is_sole_login_verifier_and_database_normalization(account_bootstrap_case):
    c = account_bootstrap_case
    legacy = c.seed_and_backfill_legacy_for_test(
        email=" Owner@Example.test ", password="Account-Original-Passphrase-23",
    )
    c.replace_only_legacy_password_for_test(legacy.user_id, "Legacy-Only-Passphrase-44")
    for supplied in ("Owner@Example.test", "  owner@example.test  "):
        good = c.client.post("/api/v1/auth/login", data={
            "username": supplied, "password": "Account-Original-Passphrase-23",
        })
        assert good.status_code == 200
        assert c.client.get("/api/v1/auth/me", headers=bearer(good.json()["access_token"])).status_code == 200
    assert c.client.post("/api/v1/auth/login", data={
        "username": "owner@example.test", "password": "Legacy-Only-Passphrase-44",
    }).status_code == 401
    assert c.client.post("/api/v1/auth/register", json={
        "email": " OWNER@example.test ", "password": "Synthetic-Only-Passphrase-29",
    }).status_code == 409


@pytest.mark.parametrize("mutation", [
    "account_inactive", "membership_inactive", "user_inactive", "membership_missing",
    "role_missing", "role_disagrees", "membership_generation_changed",
    "user_generation_changed", "user_practice_mismatch", "practice_missing",
])
def test_current_state_change_denies_next_request(account_bootstrap_case, mutation):
    c = account_bootstrap_case
    token, identity = c.create_first_owner_for_test()
    assert c.client.get("/api/v1/auth/me", headers=bearer(token)).status_code == 200
    # FK-prohibited corruptions must instead be proved impossible; the helper
    # returns False only after asserting the real DB's targeted FK rejection.
    if not c.apply_current_state_mutation_for_test(identity, mutation):
        return
    assert c.client.get("/api/v1/auth/me", headers=bearer(token)).status_code == 401


def test_bootstrap_rechecks_account_and_selection_cannot_swap_tenant(account_bootstrap_case):
    c = account_bootstrap_case
    token_a, a = c.create_first_owner_for_test(email="a@example.test")
    token_b, b = c.create_first_owner_for_test(email="b@example.test")
    bootstrap_a = c.login_bootstrap_for_test("a@example.test")
    denied = c.client.post("/api/v1/auth/select-membership", json={
        "membership_id": str(b.membership_id),
    }, headers=bearer(bootstrap_a))
    assert denied.status_code == 401
    assert c.client.get("/api/v1/auth/memberships", headers=bearer(token_a)).status_code == 401
    tampered = c.resign_for_test(token_a, practice_id=str(b.practice_id))
    assert c.client.get("/api/v1/auth/me", headers=bearer(tampered)).status_code == 401
    c.deactivate_account_for_test(a.account_id)
    assert c.client.get("/api/v1/auth/memberships", headers=bearer(bootstrap_a)).status_code == 401


def test_restricted_auth_and_tenant_privileges(account_bootstrap_case):
    c = account_bootstrap_case
    _, identity = c.create_first_owner_for_test()
    for connection in (c.auth_caller_for_test(), c.tenant_caller_for_test(identity.practice_id)):
        with connection as conn:
            with pytest.raises(DBAPIError):
                with conn.begin_nested():
                    conn.execute(sa.text("SELECT password_hash FROM public.accounts"))
    with c.tenant_caller_for_test(identity.practice_id) as conn:
        with pytest.raises(DBAPIError):
            with conn.begin_nested():
                conn.execute(sa.text("SELECT * FROM account_api.credential_lookup(:email)"), {"email": "a@example.test"})
    assert c.assert_function_owner_no_login_no_bypass_and_no_membership_for_test()
    assert c.assert_force_rls_and_function_acl_for_test()


def test_token_confusion_and_missing_wiring_fail_closed(account_bootstrap_case):
    c = account_bootstrap_case
    token, _ = c.create_first_owner_for_test()
    for changes in (
        {"aud": "raisa-account-bootstrap"}, {"aud": ["raisa-tenant", "raisa-account-bootstrap"]},
        {"token_kind": "account_bootstrap"}, {"authority_generation": True},
        {"authority_generation": "1"}, {"membership_id": str(uuid.uuid4())},
    ):
        bad = c.resign_for_test(token, **changes)
        assert c.client.get("/api/v1/auth/me", headers=bearer(bad)).status_code == 401
    with c.without_auth_factory_for_test():
        assert c.client.post("/api/v1/auth/login", data={"username": "a@example.test", "password": "anything"}).status_code == 503


def test_registration_and_first_owner_concurrency(account_bootstrap_case):
    c = account_bootstrap_case
    # Future harness uses distinct real auth DB sessions and a bounded barrier;
    # sequential requests or mocked locking cannot satisfy this scenario.
    registrations = c.concurrent_requests_for_test([
        ("POST", "/api/v1/auth/register", {"email": email, "password": "Synthetic-Only-Passphrase-29"}, {})
        for email in ("Race@Example.test", " race@example.test ")
    ])
    assert sorted(response.status_code for response in registrations) == [200, 409]
    bootstrap = next(response.json()["access_token"] for response in registrations if response.status_code == 200)
    created = c.concurrent_requests_for_test([
        ("POST", "/api/v1/auth/practices", {"name": name}, bearer(bootstrap))
        for name in ("Race A", "Race B")
    ])
    assert sorted(response.status_code for response in created) == [200, 409]
    identity = c.identity_for_account_for_test(c.decode_for_test(bootstrap)["account_id"])
    assert c.committed_audit_codes_for_test(identity.account_id).count("registered") == 1
    assert c.committed_audit_codes_for_test(identity.account_id).count("practice_created") == 1


def test_success_audit_is_required_atomic_and_append_only(account_bootstrap_case):
    c = account_bootstrap_case
    bootstrap = register(c)
    before = c.owned_counts_for_test()
    with c.fail_audit_insert_for_test():
        response = c.client.post("/api/v1/auth/practices", json={"name": "Audit rejected"}, headers=bearer(bootstrap))
    assert response.status_code >= 400
    assert c.owned_counts_for_test() == before
    token, identity = c.create_first_owner_for_test(email="audit@example.test")
    assert c.client.get("/api/v1/auth/me", headers=bearer(token)).status_code == 200
    for statement in (
        "DELETE FROM public.account_bootstrap_audit",
        "UPDATE public.account_bootstrap_audit SET event_code = 'login_denied'",
        "TRUNCATE public.account_bootstrap_audit",
    ):
        with pytest.raises(DBAPIError):
            with c.admin.begin_nested():
                c.admin.execute(sa.text(statement))
    assert c.audit_has_only_fixed_codes_and_identifiers_for_test(identity.account_id)
