"""Inert patient-six test SOURCE; writing/collecting it grants no execution.

Pure cases import only pure schemas at collection and the engine-free policy
helper locally. They do not prove SQL authority, RLS, atomicity or concurrency.
The SQL cases below NEVER build engines, discover a DSN, read environment/config
secrets, seed real data, run migrations, or use a repository conftest fixture.

A later, separately reviewed finite isolated-test mechanism may explicitly set
``pytest.Config._raisa_patient_registration_context_factory`` to a callable.
Absent that exact injected attribute the SQL cases skip. The callable accepts
``test_name=<node id>`` and returns a context manager for a RESET PER TEST,
exclusively owned disposable synthetic database, already migrated and populated
with two different practices and current Receptionist/PracticeOwner principals.
Its yielded object must supply:

* service: the actual enabled PatientRegistrationService (no fake/mocked adapter);
* tenant_engine: that service's actual raisa_local_tenant SQLAlchemy Engine;
* admin_engine: the bounded database-owner Engine for fault/authority injection
  and SET LOCAL ROLE raisa_local_patient_functions on the owned database;
* observer_engine: the bounded read/pg_stat_activity observer Engine, with
  visibility of the tenant connection's pg_blocking_pids, never a provider;
* actor_token, foreign_token: actual signed synthetic tenant tokens;
* actor: dict with UUID account_id, membership_id, user_id, practice_id,
  plus role and integer generation; foreign_practice_id: UUID;
* fresh_token(*, expires_in_seconds=None): existing synthetic token issuer,
  using current authority and no external identity service;
* mint_confirmation_evidence(payload, *, evidence_purpose): optional callback
  bound directly to the unchanged generic signer with the trusted synthetic
  signing secret; it does not reveal the secret or replace verification;
* expiry_wait_budget_seconds: optional finite separately admitted allowance.
  Only an allowance >=301 enables the original 300-second draft-expiry case.

The factory owns reset/cleanup even on a failed assertion, including the two
explicitly named audit-fault objects created by one case. It must enforce the
later admitted executable/import/DB/role/resource/cleanup boundaries; this source
does not supply those bindings or independently accept an implementation. Run
SQL cases serially on a schema. There is no environment or production fallback.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import time
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.schemas.patient_registration import (
    CANONICALIZATION_VERSION,
    CONFIRMATION_PURPOSE,
    ConfirmRegistration,
    PrepareRegistration,
    RegistrationBody,
    canonical_registration_body,
)


def _body(**changes):
    return RegistrationBody(first_name=changes.pop("first_name", "Synthetic"),
                            last_name=changes.pop("last_name", "PatientSix"),
                            date_of_birth=changes.pop("date_of_birth", "2000-02-29"),
                            **changes)


def _new(body=None, key=None):
    return PrepareRegistration(command_key=key or uuid4(), body=body or _body(),
                               new_registration=True)


def _correction(prepared, body=None, key=None, **changes):
    draft = prepared["draft"]
    values = dict(command_key=key or uuid4(), body=body or _body(first_name="Corrected"),
                  new_registration=False,
                  registration_intent_id=draft["registration_intent_id"],
                  supersedes_command_id=draft["command_id"],
                  supersedes_revision=draft["draft_revision"])
    values.update(changes)
    return PrepareRegistration(**values)


def confirm_request(prepared, **changes):
    """Use exactly the displayed draft and its supplied signed envelope."""
    draft = prepared["draft"]
    values = {key: draft[key] for key in (
        "command_key", "command_id", "registration_intent_id", "draft_revision", "body_digest")}
    values.update(confirmed=True,
                  signed_confirmation_evidence=prepared["confirmation_evidence"] or {})
    values.update(changes)
    return ConfirmRegistration(**values)


def test_canonical_body_trims_only_outer_spacing_and_preserves_spelling():
    body = _body(first_name=" \u2003SyntH\u00e9tic  Person\u2003 ", last_name="  O'Example-Six ")
    primitive, raw, digest = canonical_registration_body(body)
    assert primitive == {
        "canonicalization_version": "patient.registration.body.v1",
        "first_name": "SyntH\u00e9tic  Person", "last_name": "O'Example-Six",
        "date_of_birth": "2000-02-29", "distinct_person": False,
    }
    assert CANONICALIZATION_VERSION == primitive["canonicalization_version"]
    assert CONFIRMATION_PURPOSE == "patient_registration.confirm.v1"
    assert raw == json.dumps(primitive, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False)
    assert digest == hashlib.sha256(raw.encode("utf-8")).hexdigest()
    assert len(digest) == 64
    assert canonical_registration_body(_body(first_name=primitive["first_name"],
                                              last_name=primitive["last_name"])) == (primitive, raw, digest)


def test_distinct_person_decision_is_part_of_canonical_digest():
    assert canonical_registration_body(_body())[2] != canonical_registration_body(
        _body(distinct_person=True))[2]


def test_canonicalizer_does_not_accept_an_unvalidated_dictionary():
    with pytest.raises(ValueError):
        canonical_registration_body({"first_name": "Synthetic", "last_name": "PatientSix",
                                     "date_of_birth": "2000-02-29"})


@pytest.mark.parametrize("field", ["first_name", "last_name"])
@pytest.mark.parametrize("invalid", ["", "   ", "x" * 101, 7, None,
                                     "\nSynthetic", "Synthetic\t", "Syn\x00thetic", "Syn\x7fthetic"])
def test_name_bounds_types_and_controls_are_rejected(field, invalid):
    with pytest.raises(ValidationError):
        _body(**{field: invalid})


def test_name_length_boundary_and_exact_date_are_accepted():
    assert _body(first_name="x" * 100, last_name="y", date_of_birth=date(2000, 2, 29)).first_name == "x" * 100


@pytest.mark.parametrize("invalid", ["2001-02-29", "2000-2-29", "29/02/2000",
                                     "2000-02-29T00:00:00", " 2000-02-29", 0, True,
                                     datetime(2000, 2, 29, tzinfo=timezone.utc)])
def test_dob_is_a_real_exact_iso_date_not_a_datetime_or_coerced_number(invalid):
    with pytest.raises(ValidationError):
        _body(date_of_birth=invalid)


def test_future_dob_is_rejected():
    with pytest.raises(ValidationError):
        _body(date_of_birth=datetime.now(timezone.utc).date() + timedelta(days=1))


@pytest.mark.parametrize("extra", ["practice_id", "patient_id", "actor_user_id", "account_id",
                                  "ihi", "medicare", "document_url", "contact", "aggregate_version"])
def test_body_cannot_supply_identity_clinical_or_concurrency_fields(extra):
    with pytest.raises(ValidationError):
        _body(**{extra: "not-accepted"})


@pytest.mark.parametrize("invalid", [0, 1, "true", "false", None])
def test_distinct_person_is_a_strict_human_boolean(invalid):
    with pytest.raises(ValidationError):
        _body(distinct_person=invalid)


def test_new_intent_and_correction_contexts_are_explicit_and_closed():
    key, intent, predecessor = uuid4(), uuid4(), uuid4()
    assert _new(key=key).registration_intent_id is None
    correction = PrepareRegistration(command_key=key, body=_body(), new_registration=False,
                                     registration_intent_id=intent,
                                     supersedes_command_id=predecessor, supersedes_revision=1)
    assert correction.registration_intent_id == intent
    for name in ("registration_intent_id", "supersedes_command_id", "supersedes_revision"):
        values = correction.model_dump()
        values[name] = None
        with pytest.raises(ValidationError):
            PrepareRegistration(**values)
        values = _new().model_dump()
        values[name] = {"registration_intent_id": intent,
                        "supersedes_command_id": predecessor, "supersedes_revision": 1}[name]
        with pytest.raises(ValidationError):
            PrepareRegistration(**values)
    for invalid in (0, True, "1"):
        with pytest.raises(ValidationError):
            PrepareRegistration(**{**correction.model_dump(), "supersedes_revision": invalid})
    with pytest.raises(ValidationError):
        PrepareRegistration(**{**_new().model_dump(), "new_registration": "true"})
    with pytest.raises(ValidationError):
        PrepareRegistration(**{**_new().model_dump(), "practice_id": uuid4()})


def _valid_confirmation_fields():
    return dict(command_key=uuid4(), command_id=uuid4(), registration_intent_id=uuid4(),
                draft_revision=1, body_digest="a" * 64, confirmed=True,
                signed_confirmation_evidence={"payload": {}})


@pytest.mark.parametrize("field,invalid", [
    ("confirmed", False), ("confirmed", "true"), ("confirmed", 1),
    ("draft_revision", 0), ("draft_revision", True), ("draft_revision", "1"),
    ("body_digest", "A" * 64), ("body_digest", "a" * 63), ("body_digest", "g" * 64),
    ("body_digest", "a" * 64 + "\n"),
])
def test_confirmation_requires_explicit_true_revision_and_exact_digest(field, invalid):
    with pytest.raises(ValidationError):
        ConfirmRegistration(**{**_valid_confirmation_fields(), field: invalid})


def test_confirmation_cannot_replace_the_displayed_body_or_tenant():
    for field in ("body", "patient_id", "practice_id", "actor_membership_id"):
        with pytest.raises(ValidationError):
            ConfirmRegistration(**{**_valid_confirmation_fields(), field: {}})


@pytest.mark.parametrize("role", ["Receptionist", "PracticeOwner"])
@pytest.mark.parametrize("action", ["patient.read", "patient.create"])
def test_explicit_local_patient_policy_permits_only_the_two_selected_actions(role, action):
    from app.services.patient_registration import require_patient_policy
    assert require_patient_policy(role, action) is None


@pytest.mark.parametrize("role,action", [
    (role, action) for role in ("GP", "Nurse", "Admin", "receptionist", "", None, True)
    for action in ("patient.read", "patient.create")
] + [(role, action) for role in ("Receptionist", "PracticeOwner")
     for action in ("patient.update", "patient.merge", "appointment.read", None)])
def test_patient_policy_has_no_blanket_staff_or_unknown_action_fallback(role, action):
    from app.services.patient_registration import PatientRegistrationError, require_patient_policy
    with pytest.raises(PatientRegistrationError) as failure:
        require_patient_policy(role, action)
    assert failure.value.status_code == 403


# Everything below needs an explicitly injected future real PostgreSQL context.
# Collection itself does not import auth/config/signers or construct any Engine.
@pytest.fixture
def admitted_patient_db(request):
    factory = getattr(request.config, "_raisa_patient_registration_context_factory", None)
    if factory is None:
        pytest.skip("no explicitly injected admitted isolated patient SQL context")
    with factory(test_name=request.node.nodeid) as context:
        yield context


def _sql(engine, statement, parameters=None):
    from sqlalchemy import text
    with engine.begin() as connection:
        result = connection.execute(text(statement), parameters or {})
        return result.mappings().all() if result.returns_rows else []


def _counts(context):
    return dict(_sql(context.observer_engine, """
        SELECT (SELECT count(*) FROM public.patients WHERE practice_id=:practice) patients,
               (SELECT count(*) FROM public.patient_registration_commands
                 WHERE practice_id=:practice AND state='committed') receipts,
               (SELECT count(*) FROM public.patient_registration_audit
                 WHERE practice_id=:practice) audits
    """, {"practice": context.actor["practice_id"]})[0])


def _commands(context):
    return _sql(context.observer_engine, """SELECT id,command_key,registration_intent_id,
        draft_revision,state,body_digest,supersedes_command_id,patient_id,audit_event_id
        FROM public.patient_registration_commands
        WHERE practice_id=:practice AND actor_membership_id=:membership ORDER BY id""",
        {"practice": context.actor["practice_id"], "membership": context.actor["membership_id"]})


def _refused(call, *, statuses=(409,)):
    from app.services.patient_registration import PatientRegistrationError
    with pytest.raises(PatientRegistrationError) as failure:
        call()
    assert failure.value.status_code in statuses
    return failure.value


def _registered(context, body=None, token=None):
    token = token or context.actor_token
    request = _new(body)
    prepared = context.service.prepare(token, request)
    return request, prepared, context.service.confirm(token, confirm_request(prepared))


def _one_success(before, after):
    assert after == {key: value + 1 for key, value in before.items()}


def test_sql_prepare_is_not_creation_and_exact_replay_keeps_the_same_draft(admitted_patient_db):
    c = admitted_patient_db
    before = _counts(c)
    request = _new()
    first = c.service.prepare(c.actor_token, request)
    again = c.service.prepare(c.actor_token, request)
    assert first["state"] == again["state"] == "prepared"
    assert first["draft"] == again["draft"]
    assert first["confirmation_evidence"] == again["confirmation_evidence"]
    assert first["draft"]["draft_revision"] == 1
    assert _counts(c) == before
    commands = _commands(c)
    _refused(lambda: c.service.prepare(c.actor_token, _new(_body(first_name="Different"), request.command_key)))
    assert _counts(c) == before
    assert _commands(c) == commands


def test_sql_correction_keeps_intent_advances_revision_and_invalidates_old_evidence(admitted_patient_db):
    c = admitted_patient_db
    before = _counts(c)
    original = c.service.prepare(c.actor_token, _new())
    corrected_request = _correction(original)
    corrected = c.service.prepare(c.actor_token, corrected_request)
    assert corrected["draft"]["registration_intent_id"] == original["draft"]["registration_intent_id"]
    assert corrected["draft"]["draft_revision"] == original["draft"]["draft_revision"] + 1
    assert corrected["draft"]["command_id"] != original["draft"]["command_id"]
    assert corrected["draft"]["body_digest"] != original["draft"]["body_digest"]
    _refused(lambda: c.service.confirm(c.actor_token, confirm_request(original)))
    assert _sql(c.observer_engine, "SELECT state FROM public.patient_registration_commands WHERE id=:id",
                {"id": original["draft"]["command_id"]})[0]["state"] == "superseded"
    assert c.service.prepare(c.actor_token, corrected_request)["draft"] == corrected["draft"]
    commands = _commands(c)
    for changes in (dict(registration_intent_id=uuid4()), dict(supersedes_command_id=uuid4()),
                    dict(supersedes_revision=corrected_request.supersedes_revision + 1)):
        changed = corrected_request.model_copy(update=changes)
        _refused(lambda changed=changed: c.service.prepare(c.actor_token, changed))
    # A new key cannot bypass the now-stale predecessor/revision either.
    _refused(lambda: c.service.prepare(c.actor_token, _correction(original)))
    assert _counts(c) == before
    assert _commands(c) == commands
    receipt = c.service.confirm(c.actor_token, confirm_request(corrected))
    assert receipt["registration_intent_id"] == corrected["draft"]["registration_intent_id"]
    assert receipt["draft_revision"] == corrected["draft"]["draft_revision"]
    _one_success(before, _counts(c))


def test_sql_concurrent_corrections_have_one_live_successor(admitted_patient_db):
    c = admitted_patient_db
    original = c.service.prepare(c.actor_token, _new())
    requests = [_correction(original, _body(first_name=name)) for name in ("CorrectedOne", "CorrectedTwo")]
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(c.service.prepare, c.actor_token, request) for request in requests]
        results, failures = [], []
        for future in futures:
            try:
                results.append(future.result(timeout=10))
            except Exception as failure:
                failures.append(failure)
    from app.services.patient_registration import PatientRegistrationError
    assert len(results) == len(failures) == 1
    assert isinstance(failures[0], PatientRegistrationError) and failures[0].status_code == 409
    rows = _sql(c.observer_engine, """SELECT state,draft_revision FROM public.patient_registration_commands
        WHERE practice_id=:practice AND actor_membership_id=:membership AND registration_intent_id=:intent""",
        {"practice": c.actor["practice_id"], "membership": c.actor["membership_id"],
         "intent": original["draft"]["registration_intent_id"]})
    assert sorted((row["state"], row["draft_revision"]) for row in rows) == [("prepared", 2), ("superseded", 1)]
    _refused(lambda: c.service.confirm(c.actor_token, confirm_request(original)))


def test_sql_concurrent_confirms_create_one_patient_receipt_and_audit(admitted_patient_db):
    c = admitted_patient_db
    before = _counts(c)
    prepared = c.service.prepare(c.actor_token, _new())
    request = confirm_request(prepared)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(c.service.confirm, c.actor_token, request) for _ in range(2)]
        receipts = [future.result(timeout=10) for future in futures]
    assert receipts[0] == receipts[1]
    assert c.service.receipt(c.fresh_token(), request.command_key) == receipts[0]
    _one_success(before, _counts(c))
    rows = _sql(c.observer_engine, """SELECT c.patient_id,c.audit_event_id,a.id,a.patient_id audit_patient,
        a.command_id,a.body_digest,a.actor_account_id,a.actor_membership_id,a.actor_user_id
        FROM public.patient_registration_commands c JOIN public.patient_registration_audit a
          ON a.practice_id=c.practice_id AND a.command_id=c.id
        WHERE c.practice_id=:practice AND c.actor_membership_id=:membership AND c.command_key=:key""",
        {"practice": c.actor["practice_id"], "membership": c.actor["membership_id"], "key": request.command_key})
    assert len(rows) == 1
    row, receipt = rows[0], receipts[0]
    for field in ("patient_id", "audit_event_id", "command_id", "actor_account_id", "actor_membership_id", "actor_user_id"):
        assert str(row[field]) == str(receipt[field])
    assert row["id"] == row["audit_event_id"] and row["audit_patient"] == row["patient_id"]
    assert row["body_digest"] == receipt["body_digest"]


def test_sql_committed_intent_is_terminal_and_same_key_replay_is_immutable(admitted_patient_db):
    c = admitted_patient_db
    request, prepared, receipt = _registered(c)
    before = _counts(c)
    assert c.service.prepare(c.fresh_token(), request)["receipt"] == receipt
    assert c.service.confirm(c.fresh_token(), confirm_request(prepared)) == receipt
    assert c.service.receipt(c.fresh_token(), request.command_key) == receipt
    _refused(lambda: c.service.prepare(c.actor_token, _correction(prepared)))
    _refused(lambda: c.service.prepare(c.actor_token, _new(_body(first_name="Changed"), request.command_key)))
    assert _counts(c) == before


def test_sql_committed_replay_still_requires_current_membership(admitted_patient_db):
    c = admitted_patient_db
    request, prepared, _ = _registered(c)
    before = _counts(c)
    _sql(c.admin_engine, "UPDATE public.practice_memberships SET is_active=false WHERE id=:id",
         {"id": c.actor["membership_id"]})
    for call in (lambda: c.service.receipt(c.actor_token, request.command_key),
                 lambda: c.service.prepare(c.actor_token, request),
                 lambda: c.service.confirm(c.actor_token, confirm_request(prepared))):
        _refused(call, statuses=(401, 403))
    assert _counts(c) == before


def test_sql_receipt_recovery_after_original_server_draft_expiry_requires_fresh_auth(admitted_patient_db):
    c = admitted_patient_db
    if getattr(c, "expiry_wait_budget_seconds", 0) < 301:
        pytest.skip("original 300-second draft lifetime needs a separately admitted >=301-second allowance")
    request, prepared, receipt = _registered(c)
    before = _counts(c)
    expires_at = datetime.fromisoformat(prepared["draft"]["expires_at"].replace("Z", "+00:00"))
    remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()
    assert 0 < remaining <= c.expiry_wait_budget_seconds - 0.25
    time.sleep(remaining + 0.1)
    token = c.fresh_token()
    assert c.service.confirm(token, confirm_request(prepared)) == receipt
    assert c.service.prepare(token, request)["receipt"] == receipt
    assert c.service.receipt(token, request.command_key) == receipt
    assert _counts(c) == before


def test_sql_original_server_draft_expiry_refuses_first_creation(admitted_patient_db):
    c = admitted_patient_db
    if getattr(c, "expiry_wait_budget_seconds", 0) < 301:
        pytest.skip("uncommitted original draft expiry needs a separately admitted >=301-second allowance")
    prepared = c.service.prepare(c.actor_token, _new())
    before = _counts(c)
    expires_at = datetime.fromisoformat(prepared["draft"]["expires_at"].replace("Z", "+00:00"))
    remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()
    assert 0 < remaining <= c.expiry_wait_budget_seconds - 0.25
    time.sleep(remaining + 0.1)
    _refused(lambda: c.service.confirm(c.fresh_token(), confirm_request(prepared)))
    assert _counts(c) == before


def test_sql_search_read_and_receipt_are_tenant_bound_and_minimal(admitted_patient_db):
    c = admitted_patient_db
    request, prepared, receipt = _registered(c)
    _, _, foreign = _registered(c, _body(first_name="SyntheticForeign"), c.foreign_token)
    before = _counts(c)
    patient = c.service.read(c.actor_token, UUID(str(receipt["patient_id"])))
    assert set(patient) == {"id", "practice_id", "first_name", "last_name", "date_of_birth"}
    assert str(patient["id"]) == str(receipt["patient_id"])
    assert str(patient["practice_id"]) == str(c.actor["practice_id"])
    assert patient["first_name"] == prepared["draft"]["body"]["first_name"]
    assert patient["last_name"] == prepared["draft"]["body"]["last_name"]
    assert str(patient["date_of_birth"]) == "2000-02-29"
    assert str(patient["id"]) not in {str(c.actor[key]) for key in ("account_id", "membership_id", "user_id")}
    matches = c.service.search(c.actor_token, query="Synthetic", limit=1)
    assert matches == c.service.search(c.actor_token, query="Synthetic", limit=1)
    assert len(matches) == 1 and set(matches[0]) == set(patient)
    assert all(str(item["practice_id"]) == str(c.actor["practice_id"]) for item in matches)
    assert all(str(item["id"]) != str(foreign["patient_id"]) for item in matches)
    _refused(lambda: c.service.read(c.foreign_token, UUID(str(receipt["patient_id"]))), statuses=(403, 404))
    _refused(lambda: c.service.receipt(c.foreign_token, request.command_key), statuses=(403, 404))
    for args in ({}, {"query": " "}, {"query": "x"}, {"query": "Synthetic", "limit": 21},
                 {"query": "Synthetic", "limit": True}):
        _refused(lambda args=args: c.service.search(c.actor_token, **args), statuses=(400,))
    assert _counts(c) == before


def test_sql_duplicate_advice_requires_distinct_decision_and_never_merges(admitted_patient_db):
    c = admitted_patient_db
    _, _, existing = _registered(c)
    before = _counts(c)
    prepared = c.service.prepare(c.actor_token, _new())
    assert prepared["draft"]["requires_distinct_person_decision"] is True
    assert any(str(match["id"]) == str(existing["patient_id"]) for match in prepared["draft"]["advisory_matches"])
    assert prepared["confirmation_evidence"] is None
    _refused(lambda: c.service.confirm(c.actor_token, confirm_request(prepared)))
    assert _counts(c) == before
    acknowledged = c.service.prepare(c.actor_token, _correction(prepared, _body(distinct_person=True)))
    assert acknowledged["draft"]["requires_distinct_person_decision"] is False
    assert acknowledged["confirmation_evidence"] is not None
    receipt = c.service.confirm(c.actor_token, confirm_request(acknowledged))
    assert receipt["patient_id"] != existing["patient_id"]
    _one_success(before, _counts(c))
    # Equal demographics in an explicitly new, acknowledged intent are allowed;
    # no demographic unique key or automatic merge is being asserted.
    _, _, third = _registered(c, _body(distinct_person=True))
    assert len({str(existing["patient_id"]), str(receipt["patient_id"]), str(third["patient_id"])}) == 3


def test_sql_altered_confirmation_or_other_principal_never_creates(admitted_patient_db):
    c = admitted_patient_db
    prepared = c.service.prepare(c.actor_token, _new())
    before = _counts(c)
    for changes in (dict(body_digest="0" * 64), dict(command_id=uuid4()),
                    dict(registration_intent_id=uuid4()), dict(draft_revision=2)):
        _refused(lambda changes=changes: c.service.confirm(c.actor_token, confirm_request(prepared, **changes)))
    envelope = deepcopy(prepared["confirmation_evidence"])
    envelope["payload"]["body_digest"] = "0" * 64
    _refused(lambda: c.service.confirm(c.actor_token, confirm_request(prepared, signed_confirmation_evidence=envelope)))
    _refused(lambda: c.service.confirm(c.foreign_token, confirm_request(prepared)), statuses=(403, 409))
    assert _counts(c) == before


def test_sql_correctly_signed_appointment_purpose_cannot_confirm_patient(admitted_patient_db):
    c = admitted_patient_db
    mint = getattr(c, "mint_confirmation_evidence", None)
    if mint is None:
        pytest.skip("proof gap: no explicitly injected real signer callback for valid wrong-purpose evidence")
    prepared = c.service.prepare(c.actor_token, _new())
    before = _counts(c)
    payload = deepcopy(prepared["confirmation_evidence"]["payload"])
    envelope = mint(payload, evidence_purpose="bernie_confirm_create_proposal")
    _refused(lambda: c.service.confirm(c.actor_token,
        confirm_request(prepared, signed_confirmation_evidence=envelope)))
    assert _counts(c) == before


def test_sql_rls_roles_and_entry_privileges_have_no_direct_patient_write_escape(admitted_patient_db):
    c = admitted_patient_db
    roles = _sql(c.observer_engine, """SELECT rolname,rolcanlogin,rolsuper,rolbypassrls,rolinherit,
        rolcreaterole,rolcreatedb,rolreplication FROM pg_roles
        WHERE rolname IN ('raisa_local_tenant','raisa_local_patient_functions') ORDER BY rolname""")
    assert len(roles) == 2
    for role in roles:
        assert role["rolcanlogin"] is (role["rolname"] == "raisa_local_tenant")
        assert not any(role[key] for key in ("rolsuper", "rolbypassrls", "rolinherit", "rolcreaterole", "rolcreatedb", "rolreplication"))
    assert not _sql(c.observer_engine, """SELECT 1 FROM pg_auth_members m JOIN pg_roles r
        ON r.oid=m.member OR r.oid=m.roleid WHERE r.rolname IN
        ('raisa_local_tenant','raisa_local_patient_functions')""")
    rls = _sql(c.observer_engine, """SELECT relname,relrowsecurity,relforcerowsecurity
        FROM pg_class JOIN pg_namespace n ON n.oid=relnamespace WHERE n.nspname='public'
        AND relname IN ('patients','patient_registration_commands','patient_registration_audit')""")
    assert len(rls) == 3 and all(row["relrowsecurity"] and row["relforcerowsecurity"] for row in rls)
    assert _sql(c.observer_engine, """SELECT has_table_privilege('raisa_local_tenant',
        'public.patients','INSERT,UPDATE,DELETE,TRUNCATE,TRIGGER,REFERENCES') forbidden""")[0]["forbidden"] is False
    functions = _sql(c.observer_engine, """SELECT p.proname,
        pg_get_userbyid(p.proowner) owner,
        has_function_privilege('raisa_local_tenant',p.oid,'EXECUTE') tenant_execute,
        EXISTS(SELECT 1 FROM aclexplode(COALESCE(p.proacl,acldefault('f',p.proowner))) a
               WHERE a.grantee=0 AND a.privilege_type='EXECUTE') public_execute
        FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='patient_api'""")
    entries = {"patient_search", "patient_read", "registration_prepare", "registration_confirm", "registration_receipt"}
    assert {row["proname"] for row in functions if row["tenant_execute"]} == entries
    assert entries <= {row["proname"] for row in functions}
    assert all(not row["public_execute"] and row["owner"] == "raisa_local_patient_functions" for row in functions)
    paths = _sql(c.observer_engine, """SELECT p.proname,p.proconfig FROM pg_proc p
        JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='patient_api'""")
    assert all("search_path=pg_catalog" in (row["proconfig"] or []) for row in paths)
    assert not _sql(c.observer_engine, """SELECT n.nspname FROM pg_namespace n,
        LATERAL aclexplode(COALESCE(n.nspacl,acldefault('n',n.nspowner))) a
        WHERE n.nspname IN ('public','patient_api') AND a.grantee=0 AND a.privilege_type='CREATE'""")
    # Actual tenant SQL cannot INSERT even with its own tenant context set.
    from sqlalchemy import text
    from sqlalchemy.exc import DBAPIError
    with pytest.raises(DBAPIError) as failure:
        with c.tenant_engine.begin() as connection:
            connection.execute(text("SELECT set_config('app.current_practice_id',:practice,true)"),
                               {"practice": str(c.actor["practice_id"])})
            connection.execute(text("""INSERT INTO public.patients
                (id,practice_id,first_name,last_name,date_of_birth)
                VALUES (:id,:practice,'Synthetic','ForbiddenDirectWrite','2000-02-29')"""),
                {"id": uuid4(), "practice": c.actor["practice_id"]})
    assert (getattr(failure.value.orig, "sqlstate", None) or getattr(failure.value.orig, "pgcode", None)) == "42501"


def test_sql_function_owner_forced_rls_requires_selected_tenant_and_principal(admitted_patient_db):
    c = admitted_patient_db
    _, _, receipt = _registered(c)
    _, _, foreign_receipt = _registered(c, _body(first_name="SyntheticForeign"), c.foreign_token)
    from sqlalchemy import text
    selected_actor = str(c.actor["membership_id"])
    for practice, membership in (("", selected_actor), (str(c.foreign_practice_id), selected_actor),
                                 (str(c.actor["practice_id"]), ""),
                                 (str(c.actor["practice_id"]), selected_actor)):
        with c.admin_engine.begin() as connection:
            connection.execute(text("SET LOCAL ROLE raisa_local_patient_functions"))
            for guc, value in (("app.current_practice_id", practice),
                               ("patient.account_id", str(c.actor["account_id"])),
                               ("patient.membership_id", membership),
                               ("patient.user_id", str(c.actor["user_id"]))):
                connection.execute(text("SELECT set_config(:guc,:value,true)"), {"guc": guc, "value": value})
            patient_rows = connection.execute(text("SELECT id FROM public.patients WHERE id=:id"),
                                              {"id": receipt["patient_id"]}).all()
            command_rows = connection.execute(text("SELECT id FROM public.patient_registration_commands WHERE id=:id"),
                                              {"id": receipt["command_id"]}).all()
            expected = 1 if practice == str(c.actor["practice_id"]) else 0
            assert len(patient_rows) == expected
            assert len(command_rows) == (expected if membership == selected_actor else 0)
            foreign_rows = connection.execute(text("SELECT id FROM public.patients WHERE id=:id"),
                                               {"id": foreign_receipt["patient_id"]}).all()
            assert len(foreign_rows) == (1 if practice == str(c.foreign_practice_id) else 0)
    privileges = _sql(c.observer_engine, """SELECT
        has_table_privilege('raisa_local_patient_functions','public.patient_registration_audit','SELECT') can_select,
        has_table_privilege('raisa_local_patient_functions','public.patient_registration_audit','INSERT') can_insert""")[0]
    assert privileges == {"can_select": False, "can_insert": True}
    # Audit readback stays on the separately bound observer, not the function owner.
    assert len(_sql(c.observer_engine, "SELECT id FROM public.patient_registration_audit WHERE id=:id",
                    {"id": receipt["audit_event_id"]})) == 1


_AUTH_ROWS = (
    ("accounts", "id", "account_id"),
    ("practice_memberships", "id", "membership_id"),
    ("users", "id", "user_id"),
    ("practice_membership_roles", "membership_id", "membership_id"),
)


def _lock_authority(connection, actor, index, *, nowait=False):
    from sqlalchemy import text
    table, column, key = _AUTH_ROWS[index]
    # Table/column are source constants, never request/context-provided SQL.
    statement = f"SELECT {column} FROM public.{table} WHERE {column}=:id"
    parameters = {"id": actor[key]}
    if index == 3:
        statement += " AND role=:role"
        parameters["role"] = actor["role"]
    rows = connection.execute(text(statement + " FOR UPDATE" + (" NOWAIT" if nowait else "")), parameters).all()
    assert len(rows) == 1


def _await_confirm_wait(c, holder_pid, future):
    deadline = time.monotonic() + 1.5
    while time.monotonic() < deadline:
        waiting = _sql(c.observer_engine, """SELECT pid FROM pg_stat_activity
            WHERE datname=current_database() AND :holder=ANY(pg_blocking_pids(pid))
              AND query LIKE '%patient_api.registration_confirm(%'""", {"holder": holder_pid})
        if waiting:
            assert len(waiting) == 1
            return
        if future.done():
            future.result()  # Surface the actual unexpected service failure.
            pytest.fail("confirm completed while its required authority row was locked")
        time.sleep(0.01)
    pytest.fail("no observed confirm authority-lock wait within the bounded observation")


@pytest.mark.parametrize("blocked_index", range(4), ids=[row[0] for row in _AUTH_ROWS])
def test_sql_authority_locks_follow_account_membership_user_role_order(admitted_patient_db, blocked_index):
    c = admitted_patient_db
    prepared = c.service.prepare(c.actor_token, _new())
    from sqlalchemy import text
    from sqlalchemy.exc import DBAPIError
    with c.admin_engine.connect() as blocker, ThreadPoolExecutor(max_workers=1) as executor:
        transaction = blocker.begin()
        future = None
        try:
            holder_pid = blocker.execute(text("SELECT pg_backend_pid()")).scalar_one()
            _lock_authority(blocker, c.actor, blocked_index)
            future = executor.submit(c.service.confirm, c.actor_token, confirm_request(prepared))
            _await_confirm_wait(c, holder_pid, future)
            for index in range(4):
                if index == blocked_index:
                    continue
                with c.admin_engine.connect() as probe:
                    probe_transaction = probe.begin()
                    try:
                        if index < blocked_index:
                            with pytest.raises(DBAPIError) as failure:
                                _lock_authority(probe, c.actor, index, nowait=True)
                            code = getattr(failure.value.orig, "sqlstate", None) or getattr(failure.value.orig, "pgcode", None)
                            assert code == "55P03"
                        else:
                            _lock_authority(probe, c.actor, index, nowait=True)
                    finally:
                        probe_transaction.rollback()
        finally:
            transaction.rollback()
        assert future is not None and future.result(timeout=10)["patient_id"]


@pytest.mark.parametrize("mutation", [
    "UPDATE public.accounts SET is_active=false WHERE id=:account_id",
    "UPDATE public.practice_memberships SET is_active=false WHERE id=:membership_id",
    "UPDATE public.users SET is_active=false WHERE id=:user_id",
    "UPDATE public.practice_memberships SET authority_generation=authority_generation+1 WHERE id=:membership_id",
    "UPDATE public.users SET authority_generation=authority_generation+1 WHERE id=:user_id",
    "UPDATE public.users SET role='GP' WHERE id=:user_id",
    "DELETE FROM public.practice_membership_roles WHERE membership_id=:membership_id AND role=:role",
])
def test_sql_authority_is_rechecked_after_wait_before_any_write(admitted_patient_db, mutation):
    c = admitted_patient_db
    prepared = c.service.prepare(c.actor_token, _new())
    before = _counts(c)
    from sqlalchemy import text
    with c.admin_engine.connect() as blocker, ThreadPoolExecutor(max_workers=1) as executor:
        transaction = blocker.begin()
        try:
            _lock_authority(blocker, c.actor, 0)
            holder = blocker.execute(text("SELECT pg_backend_pid()")).scalar_one()
            future = executor.submit(c.service.confirm, c.actor_token, confirm_request(prepared))
            _await_confirm_wait(c, holder, future)
            blocker.execute(text(mutation), c.actor)
            transaction.commit()
            _refused(lambda: future.result(timeout=10), statuses=(401, 403))
        finally:
            if transaction.is_active:
                transaction.rollback()
    assert _counts(c) == before


def test_sql_token_expiry_is_rechecked_after_authority_lock_wait(admitted_patient_db):
    c = admitted_patient_db
    prepared = c.service.prepare(c.actor_token, _new())
    before = _counts(c)
    from sqlalchemy import text
    with c.admin_engine.connect() as blocker, ThreadPoolExecutor(max_workers=1) as executor:
        transaction = blocker.begin()
        try:
            _lock_authority(blocker, c.actor, 0)
            holder = blocker.execute(text("SELECT pg_backend_pid()")).scalar_one()
            token = c.fresh_token(expires_in_seconds=2)
            expiry_deadline = time.monotonic() + 2.1
            future = executor.submit(c.service.confirm, token, confirm_request(prepared))
            _await_confirm_wait(c, holder, future)
            time.sleep(max(0, expiry_deadline - time.monotonic()))
            transaction.commit()
            _refused(lambda: future.result(timeout=10), statuses=(401, 403))
        finally:
            if transaction.is_active:
                transaction.rollback()
    assert _counts(c) == before


def test_sql_audit_failure_rolls_back_patient_and_receipt_in_the_same_transaction(admitted_patient_db):
    c = admitted_patient_db
    prepared = c.service.prepare(c.actor_token, _new())
    before = _counts(c)
    assert not _sql(c.observer_engine, "SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='_patient6_test_reject_audit'")
    assert not _sql(c.observer_engine, "SELECT 1 FROM pg_trigger WHERE tgrelid='public.patient_registration_audit'::regclass AND tgname='patient6_test_reject_audit'")
    from sqlalchemy import text
    try:
        with c.admin_engine.begin() as connection:
            connection.execute(text("""CREATE FUNCTION public._patient6_test_reject_audit() RETURNS trigger
                LANGUAGE plpgsql SET search_path=pg_catalog AS $fault$
                BEGIN RAISE EXCEPTION 'synthetic patient-six audit failure' USING ERRCODE='XX000'; END;
                $fault$"""))
            connection.execute(text("REVOKE ALL ON FUNCTION public._patient6_test_reject_audit() FROM PUBLIC"))
            connection.execute(text("""CREATE TRIGGER patient6_test_reject_audit BEFORE INSERT
                ON public.patient_registration_audit FOR EACH ROW EXECUTE FUNCTION public._patient6_test_reject_audit()"""))
        failure = _refused(lambda: c.service.confirm(c.actor_token, confirm_request(prepared)), statuses=(503,))
        assert failure.code == "PATIENT_REGISTRATION_UNAVAILABLE"
        assert _counts(c) == before
        row = _sql(c.observer_engine, """SELECT state,patient_id,audit_event_id,committed_at
            FROM public.patient_registration_commands WHERE id=:id""", {"id": prepared["draft"]["command_id"]})[0]
        assert row == {"state": "prepared", "patient_id": None, "audit_event_id": None, "committed_at": None}
    finally:
        _sql(c.admin_engine, "DROP TRIGGER IF EXISTS patient6_test_reject_audit ON public.patient_registration_audit")
        _sql(c.admin_engine, "DROP FUNCTION IF EXISTS public._patient6_test_reject_audit()")
