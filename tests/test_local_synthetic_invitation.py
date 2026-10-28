"""Unexecuted isolated PostgreSQL scenarios, never project-conftest authority.

Required future reviewed fixture local_invitation_case supplies fresh migrated
PG, separate direct auth/tenant/migrator engines, same-practice synthetic owner
and practice-less recipient/other Account tokens, fixture_id, and literal IDs.
It independently provisions the fifth NOLOGIN role before this revision and
captures nine exact old d9 function definitions/ACLs before upgrading. It mounts
NO HTTP routes. Runtime credentials arrive through its reviewed private frame,
never environment/default URL discovery in this module.

The fixture must disable old auth writer EXECUTEs FOR THIS TEST CAPSULE AFTER
migration/catalogue-baseline capture: register_account, create_first_practice,
record_login, record_selection. No production grant mutation is proposed. Only
the three adapter commands and explicitly lock-ordered synthetic admin changes
are reachable during races. Its controlled audit-failure/lock-wait/hint-change
injections and private logging capture require separate source/admission review.
The separate local_invitation_catalogue_case supplies the same isolated database
BEFORE the test-only writer-EXECUTE restriction, solely for catalogue readback;
it exposes no commands, routes or races. This keeps the unchanged d9 baseline
claim distinct from the subsequent deliberate capsule-only writer restriction.
These unprovided hooks are prerequisites, not substituted executed evidence.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import uuid
import hashlib

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from app.services.local_synthetic_invitation import LocalSyntheticInvitationService, InvitationDenied


def service(c):
    return LocalSyntheticInvitationService(c.auth_engine)


def issue(c, key=None, role="Receptionist", ttl=600):
    return service(c).issue(c.owner_token, c.fixture_id, role, ttl, key or uuid.uuid4())


def population(c):
    with c.admin_engine.connect() as db:
        return tuple(db.execute(text("SELECT count(*) FROM public."+name)).scalar_one()
                     for name in ("accounts", "users", "practice_memberships", "practice_membership_roles",
                                  "local_invitation", "local_invitation_audit"))


def test_issue_typed_replay_does_not_replace_secret_or_absolute_expiry(local_invitation_case):
    c=local_invitation_case; key=uuid.uuid4(); before=population(c)
    receipt, secret=issue(c,key)
    assert receipt["created"] is True and secret is not None
    with c.admin_engine.connect() as db:
        original=db.execute(text("SELECT verifier_digest,expires_at,role,requested_ttl_seconds FROM public.local_invitation WHERE id=:i"),{"i":receipt["invitation_id"]}).one()
    replay, replacement=issue(c,key)
    assert replay==dict(receipt,created=False) and replacement is None
    with c.admin_engine.connect() as db:
        assert db.execute(text("SELECT verifier_digest,expires_at,role,requested_ttl_seconds FROM public.local_invitation WHERE id=:i"),{"i":receipt["invitation_id"]}).one()==original
    assert population(c)==before[:4]+(before[4]+1,before[5]+1)
    for role,ttl in (("GP",600),("Receptionist",601)):
        with pytest.raises(InvitationDenied,match="^invitation denied$"):
            issue(c,key,role,ttl)
    assert population(c)==before[:4]+(before[4]+1,before[5]+1)


def test_domain_separated_verifier_rejects_bare_digest_without_effects(local_invitation_case):
    c=local_invitation_case; receipt,secret=issue(c); invitation=receipt["invitation_id"]
    bare=hashlib.sha256(secret.encode("ascii")).digest()
    expected=hashlib.sha256(b"raisa.local-synthetic-invitation.v1\x00" + secret.encode("ascii")).digest()
    with c.admin_engine.begin() as db:
        db.execute(text("SELECT id FROM public.accounts WHERE id=:a FOR UPDATE"),{"a":c.recipient_account}).one()
        db.execute(text("SELECT id FROM public.local_invitation_fixture_binding WHERE id=:f FOR UPDATE"),{"f":c.fixture_id}).one()
        stored=db.execute(text("SELECT verifier_digest FROM public.local_invitation WHERE id=:i FOR UPDATE"),{"i":invitation}).scalar_one()
        assert bytes(stored)==expected and len(expected)==32 and expected!=bare
        db.execute(text("UPDATE public.local_invitation SET verifier_digest=:d WHERE id=:i"),{"d":bare,"i":invitation})
    with c.admin_engine.connect() as db:
        snapshot={name:db.execute(text("SELECT * FROM public."+name+" ORDER BY id")).all() for name in
                  ("users","practice_memberships","local_invitation","local_invitation_audit")}
        roles=db.execute(text("SELECT * FROM public.practice_membership_roles ORDER BY membership_id,role")).all()
    with pytest.raises(InvitationDenied,match="^invitation denied$"):
        service(c).accept(c.recipient_token,invitation,secret)
    with c.admin_engine.connect() as db:
        for name,rows in snapshot.items():
            assert db.execute(text("SELECT * FROM public."+name+" ORDER BY id")).all()==rows
        assert db.execute(text("SELECT * FROM public.practice_membership_roles ORDER BY membership_id,role")).all()==roles


def test_expired_pending_requires_explicit_revoke_then_distinct_key(local_invitation_case):
    c=local_invitation_case; first,secret=issue(c)
    # Controlled fixture changes use Account->fixture->invitation locks; no reset
    # or downgrade of generation/authority, no relation discovery while locked.
    with c.locked_invitation_expiry(first["invitation_id"],expired=True):
        with pytest.raises(InvitationDenied): issue(c)
        with pytest.raises(InvitationDenied): service(c).accept(c.recipient_token,first["invitation_id"],secret)
        assert service(c).revoke(c.owner_token,first["invitation_id"])["state"]=="revoked"
    second,other=issue(c)
    assert second["created"] is True and second["invitation_id"]!=first["invitation_id"] and other!=secret


@pytest.mark.parametrize("role",["GP","Receptionist"])
def test_accept_creates_one_membership_without_account_or_credential_change(local_invitation_case,role):
    c=local_invitation_case; first,secret=issue(c,role=role); before=population(c)
    with c.admin_engine.connect() as db:
        accounts=db.execute(text("SELECT id,normalized_email,password_hash,is_active FROM public.accounts ORDER BY id")).all()
    accepted=service(c).accept(c.recipient_token,first["invitation_id"],secret)
    assert accepted["practice_id"]==c.practice_id and accepted["role"]==role
    with c.admin_engine.connect() as db:
        assert db.execute(text("SELECT id,normalized_email,password_hash,is_active FROM public.accounts ORDER BY id")).all()==accounts
        row=db.execute(text("SELECT m.account_id,m.practice_id,m.is_active,m.authority_generation,u.is_active,u.authority_generation,u.role::text,r.role,u.practitioner_id,u.password_hash FROM public.practice_memberships m JOIN public.users u ON u.id=m.legacy_user_id JOIN public.practice_membership_roles r ON r.membership_id=m.id WHERE m.id=:i"),{"i":accepted["membership_id"]}).one()
        assert tuple(row[:9])==(c.recipient_account,c.practice_id,True,1,True,1,role,role,None)
        assert row[9].startswith("!account-only:")
    assert population(c)==(before[0],before[1]+1,before[2]+1,before[3]+1,before[4],before[5]+1)
    with pytest.raises(InvitationDenied): service(c).accept(c.recipient_token,first["invitation_id"],secret)


def test_wrong_secret_and_wrong_authenticated_account_leave_no_writes(local_invitation_case):
    c=local_invitation_case; receipt,secret=issue(c); before=population(c)
    wrong=("A" if secret[0]!="A" else "B")+secret[1:]
    for token,value in ((c.recipient_token,wrong),(c.other_account_token,secret)):
        with pytest.raises(InvitationDenied,match="^invitation denied$"):
            service(c).accept(token,receipt["invitation_id"],value)
        assert population(c)==before
    assert service(c).accept(c.recipient_token,receipt["invitation_id"],secret)["role"]=="Receptionist"


@pytest.mark.parametrize("boundary",["issue","accept","revoke"])
def test_audit_failure_rolls_back_entire_command(local_invitation_case,boundary):
    c=local_invitation_case
    receipt,secret=(None,None) if boundary=="issue" else issue(c)
    before=population(c)
    with c.reject_audit_insert(boundary):
        with pytest.raises(InvitationDenied):
            if boundary=="issue": issue(c)
            elif boundary=="accept": service(c).accept(c.recipient_token,receipt["invitation_id"],secret)
            else: service(c).revoke(c.owner_token,receipt["invitation_id"])
    assert population(c)==before
    if receipt:
        with c.admin_engine.connect() as db:
            assert db.execute(text("SELECT state FROM public.local_invitation WHERE id=:i"),{"i":receipt["invitation_id"]}).scalar_one()=="pending"


@pytest.mark.parametrize("case",["inactive_owner_account","inactive_owner_membership","inactive_owner_user",
    "wrong_practice","wrong_role","stale_member_generation","stale_user_generation","inactive_fixture"])
def test_current_owner_and_fixture_revalidation(local_invitation_case,case):
    c=local_invitation_case; before=population(c)
    with c.lock_ordered_denial_state(case):
        with pytest.raises(InvitationDenied): issue(c)
    assert population(c)==before


def test_token_expiring_during_account_lock_wait_is_denied(local_invitation_case):
    c=local_invitation_case; before=population(c)
    # Hook proves worker is waiting at Account FOR UPDATE, then releases only
    # after independently read DB clock >= trusted token expiry. No blind sleep.
    with c.account_lock_until_token_expiry() as token:
        with ThreadPoolExecutor(max_workers=1) as workers:
            job=workers.submit(service(c).issue,token,c.fixture_id,"Receptionist",600,uuid.uuid4())
            c.observe_wait_and_release_after_expiry(job)
            with pytest.raises(InvitationDenied): job.result(timeout=c.remaining_seconds())
    assert population(c)==before


def test_changed_hint_rejects_without_late_relock(local_invitation_case):
    c=local_invitation_case; before=population(c)
    with c.change_fixture_hint_before_ordered_lock():
        with pytest.raises(InvitationDenied): issue(c)
    assert population(c)==before
    assert c.observed_late_earlier_order_locks()==[]


def test_racing_replay_has_one_issue_and_one_released_secret(local_invitation_case):
    c=local_invitation_case; key=uuid.uuid4(); before=population(c)
    with ThreadPoolExecutor(max_workers=2) as workers:
        jobs=[workers.submit(issue,c,key) for _ in range(2)]
        results=[j.result(timeout=c.remaining_seconds()) for j in jobs]
    assert len({r[0]["invitation_id"] for r in results})==1
    assert sorted(r[0]["created"] for r in results)==[False,True]
    assert sum(r[1] is not None for r in results)==1
    assert population(c)==before[:4]+(before[4]+1,before[5]+1)


def test_accept_revoke_race_has_one_terminal_transition(local_invitation_case):
    c=local_invitation_case; receipt,secret=issue(c); before=population(c)
    def run(command):
        try: return command()
        except InvitationDenied: return None
    with ThreadPoolExecutor(max_workers=2) as workers:
        jobs=[workers.submit(run,lambda:service(c).accept(c.recipient_token,receipt["invitation_id"],secret)),
              workers.submit(run,lambda:service(c).revoke(c.owner_token,receipt["invitation_id"]))]
        results=[j.result(timeout=c.remaining_seconds()) for j in jobs]
    assert sum(r is not None for r in results)==1
    with c.admin_engine.connect() as db:
        row=db.execute(text("SELECT state,accepted_membership_id FROM public.local_invitation WHERE id=:i"),{"i":receipt["invitation_id"]}).one()
        codes=db.execute(text("SELECT event_code FROM public.local_invitation_audit WHERE invitation_id=:i ORDER BY event_code"),{"i":receipt["invitation_id"]}).scalars().all()
    assert row[0] in ("accepted","revoked")
    assert codes==(["accept","issue"] if row[0]=="accepted" else ["issue","revoke"])
    assert (row[1] is not None)==(row[0]=="accepted")
    after=population(c); delta=1 if row[0]=="accepted" else 0
    assert after==(before[0],before[1]+delta,before[2]+delta,before[3]+delta,before[4],before[5]+1)


def test_catalogue_exact_function_owner_acl_and_no_direct_caller_tables(local_invitation_catalogue_case):
    c=local_invitation_catalogue_case
    with c.admin_engine.connect() as db:
        roles=db.execute(text("SELECT rolname,rolcanlogin,rolsuper,rolbypassrls,rolinherit,rolcreaterole,rolcreatedb,rolreplication FROM pg_catalog.pg_roles WHERE rolname='raisa_local_invitation_functions'")).one()
        assert tuple(roles)==("raisa_local_invitation_functions",False,False,False,False,False,False,False)
        functions=db.execute(text("SELECT p.proname,pg_catalog.oidvectortypes(p.proargtypes),p.prosecdef,p.proconfig,pg_catalog.pg_get_userbyid(p.proowner),pg_catalog.pg_get_functiondef(p.oid) FROM pg_catalog.pg_proc p JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='account_api' AND p.proname LIKE 'local_invitation_%' ORDER BY p.proname")).all()
        assert [r[0] for r in functions]==["local_invitation_accept_finish","local_invitation_accept_lock","local_invitation_issue","local_invitation_revoke"]
        for row in functions:
            assert row[2] is True and row[3]==["search_path=pg_catalog"] and row[4]=="raisa_local_invitation_functions"
            signature="account_api."+row[0]+"("+row[1]+")"
            acl=db.execute(text("SELECT pg_catalog.pg_get_userbyid(a.grantee),a.privilege_type,a.is_grantable FROM pg_catalog.pg_proc p CROSS JOIN LATERAL pg_catalog.aclexplode(p.proacl) a WHERE p.oid=pg_catalog.to_regprocedure(:s)"),{"s":signature}).all()
            assert set(tuple(x) for x in acl)=={("raisa_local_invitation_functions","EXECUTE",False),("raisa_local_account_auth","EXECUTE",False)}
        for name in ("local_invitation","local_invitation_fixture_binding","local_invitation_audit"):
            assert tuple(db.execute(text("SELECT relrowsecurity,relforcerowsecurity FROM pg_catalog.pg_class WHERE oid=pg_catalog.to_regclass(:t)"),{"t":"public."+name}).one())==(True,True)
            for role in ("raisa_local_account_auth","raisa_local_tenant"):
                assert db.execute(text("SELECT pg_catalog.has_table_privilege(:r,:t,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') OR pg_catalog.has_any_column_privilege(:r,:t,'SELECT,INSERT,UPDATE,REFERENCES')"),{"r":role,"t":"public."+name}).scalar_one() is False
    assert c.exact_old_d9_function_definitions_and_acl()==c.old_d9_before


def test_exact_owner_column_union_and_policy_commands(local_invitation_catalogue_case):
    c=local_invitation_catalogue_case
    expected={
        "accounts":("id,is_active","","id"),
        "users":("id,practice_id,role,is_active,authority_generation","id,practice_id,email,password_hash,role,practitioner_id,is_active,authority_generation","id"),
        "practice_memberships":("id,account_id,practice_id,legacy_user_id,is_active,authority_generation","id,account_id,practice_id,legacy_user_id,is_active,authority_generation","id"),
        "practice_membership_roles":("membership_id,role","membership_id,role","membership_id"),
        "local_invitation_fixture_binding":("id,normalized_handle,account_id,practice_id,active","","id"),
        "local_invitation":("id,practice_id,issuer_membership_id,fixture_binding_id,intended_account_id,role,state,requested_ttl_seconds,expires_at,issue_key,verifier_digest,accepted_membership_id,created_at","id,practice_id,issuer_membership_id,fixture_binding_id,intended_account_id,role,state,requested_ttl_seconds,expires_at,issue_key,verifier_digest,accepted_membership_id,created_at","id,state,accepted_membership_id"),
        "local_invitation_audit":("","id,invitation_id,practice_id,actor_account_id,event_code,created_at","")}
    with c.admin_engine.connect() as db:
        assert db.execute(text("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_auth_members m JOIN pg_catalog.pg_roles r ON r.oid=m.member OR r.oid=m.roleid WHERE r.rolname='raisa_local_invitation_functions')")).scalar_one() is False
        assert db.execute(text("SELECT pg_catalog.has_schema_privilege('raisa_local_invitation_functions','public','CREATE')")).scalar_one() is False
        for table,columns in expected.items():
            params={"t":"public."+table,"r":"raisa_local_invitation_functions"}
            assert db.execute(text("SELECT pg_catalog.has_table_privilege(:r,:t,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')"),params).scalar_one() is False
            attrs=db.execute(text("SELECT attname FROM pg_catalog.pg_attribute WHERE attrelid=pg_catalog.to_regclass(:t) AND attnum>0 AND NOT attisdropped"),params).scalars().all()
            for privilege,allowed in zip(("SELECT","INSERT","UPDATE"),columns):
                for attr in attrs:
                    assert db.execute(text("SELECT pg_catalog.has_column_privilege(:r,:t,:a,:p)"),dict(params,a=attr,p=privilege)).scalar_one()==(attr in allowed.split(","))
            policies=db.execute(text("SELECT polcmd,polpermissive,pg_catalog.pg_get_expr(polqual,polrelid),pg_catalog.pg_get_expr(polwithcheck,polrelid) FROM pg_catalog.pg_policy WHERE polrelid=pg_catalog.to_regclass(:t) AND polroles=ARRAY[(SELECT oid FROM pg_catalog.pg_roles WHERE rolname=:r)]"),params).all()
            wanted=set()
            if table!="accounts":
                if columns[0]: wanted.add(("r",True,"true",None))
                if columns[1]: wanted.add(("a",True,None,"true"))
                if columns[2]: wanted.add(("w",True,"true","true"))
            assert set(tuple(row) for row in policies)==wanted


def test_tenant_cannot_call_private_invitation_function(local_invitation_case):
    c=local_invitation_case
    with pytest.raises(DBAPIError):
        with c.tenant_engine.begin() as db:
            db.execute(text("SELECT * FROM account_api.local_invitation_accept_lock(:a,:e,:i)"),
                       dict(a=c.recipient_account,e=datetime.now(timezone.utc)+timedelta(minutes=5),i=uuid.uuid4()))


def test_capsule_writer_closure_and_secret_redaction(local_invitation_case):
    c=local_invitation_case
    # This capsule constructs no HTTP application. Do not claim mounted-app
    # route inspection: verify the real installed exact-source/import/audit
    # guard before and after service commands. Its source rejects app.main and
    # app.routers entrypoints and socket.bind; database-only connect remains.
    # Outer native process/FD/network containment is separately bound/reviewed.
    def enforced_closure():
        observed=c.enforced_http_entrypoint_closure()
        assert observed["proof_kind"]=="SOURCE_BOUND_INSTALLED_GUARD_NOT_MOUNTED_APP_INSPECTION"
        assert observed["audit_hook_challenges_observed"]>0
        assert observed["exact_import_finder_installed"] is True
        assert observed["exact_path_loader_installed"] is True
        assert observed["verified_source_population"]==159
        assert observed["forbidden_case_entrypoints_loaded"]==[]
        assert observed["forbidden_entrypoint_attempts"]==0
        assert observed["listener_bind_attempts"]==0
        assert observed["guard_denials"]==[]
        assert observed["bound_database_endpoint"]==("127.0.0.1",55471)
        return observed
    before=enforced_closure()
    assert c.actual_disabled_auth_writers()=={
        "register_account(text,text)","create_first_practice(uuid,text)",
        "record_login(uuid,boolean)","record_selection(uuid,uuid)"}
    receipt,secret=issue(c)
    assert service(c).accept(c.recipient_token,receipt["invitation_id"],secret)["membership_id"]
    after=enforced_closure()
    assert after["audit_hook_challenges_observed"]==before["audit_hook_challenges_observed"]+1
    captured=c.captured_sanitized_logs()
    assert secret not in captured
    assert c.owner_token not in captured and c.recipient_token not in captured
    assert "verifier_digest" not in captured and "password_hash" not in captured