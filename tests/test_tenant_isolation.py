"""Source-only migrated tenant supplement; no runtime acceptance is asserted.

A reviewed isolated runner must provide tenant_runtime: four distinct PostgreSQL
engines and the exact fields of Runtime below. It owns fresh database creation,
real reviewed Alembic migrations, role/grants, verified import closure, admission,
finite whole-process budgets, selected nodes and disposal. Run without repository
conftest. Missing binding is an error. This module never creates tables or roles.
"""
from __future__ import annotations

from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
import json
import math
import re
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool


TABLES = (
    "patients", "encounters", "clinical_diagnoses",
    "prescriptions", "mbs_claims", "invoices",
)
SNAPSHOT_TABLES = (
    "practices", "users", "practitioners", *TABLES, "access_ai_audit_log",
)
PROTECTED_READS = (
    "users", "practitioners", *TABLES, "access_ai_audit_log",
)
TENANT_SETTING = "app.current_practice_id"
BASE_REVISION = "y4z5a6b7c8d9"
POLICY = "practice_id = NULLIF(current_setting('app.current_practice_id', true), '')::uuid"
FINALIZE_NOT_FOUND = {"_saved": False, "_save_error": "Patient not found."}


@dataclass(frozen=True)
class Runtime:
    engine: Engine
    command_engine: Engine
    observer_engine: Engine
    admin_engine: Engine
    database_name: str
    application_role: str
    expected_revision: str
    statement_timeout_ms: int
    lock_timeout_ms: int


def _normalize_policy(expression):
    return re.sub(r"\s|[()]", "", expression.lower().replace("::text", ""))


def _identity(connection):
    return connection.execute(text("""
        SELECT current_database() AS db, current_user AS role, session_user AS login,
               pg_backend_pid() AS pid, current_setting('row_security') AS rls,
               current_setting('app.current_practice_id', true) AS tenant
    """)).mappings().one()


def _assert_application_role(connection, runtime):
    identity = _identity(connection)
    assert identity["db"] == runtime.database_name
    assert identity["role"] == identity["login"] == runtime.application_role
    assert identity["rls"] == "on"
    role = connection.execute(text("""
        SELECT rolsuper, rolbypassrls, rolcreaterole, rolcreatedb, rolcanlogin
        FROM pg_roles WHERE rolname = current_user
    """)).mappings().one()
    assert not any(role[key] for key in
                   ("rolsuper", "rolbypassrls", "rolcreaterole", "rolcreatedb"))
    assert role["rolcanlogin"]
    # Direct grants suffice for this capsule. No inherited or SET ROLE path.
    assert connection.execute(text("""
        SELECT count(*) FROM pg_roles
        WHERE rolname <> current_user AND pg_has_role(current_user, oid, 'MEMBER')
    """)).scalar_one() == 0
    return identity


def _catalogue(connection):
    result = {}
    for table in TABLES:
        relation = connection.execute(text("""
            SELECT c.relrowsecurity, c.relforcerowsecurity,
                   pg_get_userbyid(c.relowner) AS owner,
                   has_table_privilege(current_user, c.oid, 'SELECT') AS can_select,
                   has_table_privilege(current_user, c.oid, 'INSERT') AS can_insert,
                   has_any_column_privilege(current_user, c.oid, 'UPDATE') AS can_lock,
                   has_table_privilege(current_user, c.oid, 'TRUNCATE') AS can_truncate
            FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND c.relname=:table AND c.relkind='r'
        """), {"table": table}).mappings().one()
        policies = connection.execute(text("""
            SELECT p.polname, p.polcmd, p.polpermissive,
                   p.polroles::text AS roles,
                   pg_get_expr(p.polqual,p.polrelid) AS using_expression,
                   pg_get_expr(p.polwithcheck,p.polrelid) AS check_expression
            FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='public' AND c.relname=:table ORDER BY p.polname
        """), {"table": table}).mappings().all()
        result[table] = {"relation": dict(relation),
                         "policies": [dict(p) for p in policies]}
    return result


def _assert_catalogue(connection, runtime):
    result = _catalogue(connection)
    for table, details in result.items():
        relation = details["relation"]
        assert relation["relrowsecurity"] and relation["relforcerowsecurity"], table
        assert relation["owner"] != runtime.application_role, table
        assert relation["can_select"] and relation["can_insert"], table
        assert not relation["can_truncate"], table
        if table in {"patients", "encounters"}:
            assert relation["can_lock"], table
        assert len(details["policies"]) == 1, table
        policy = details["policies"][0]
        assert (policy["polname"], policy["polcmd"], policy["polpermissive"],
                policy["roles"]) == ("tenant_isolation", "*", True, "{0}"), table
        for key in ("using_expression", "check_expression"):
            assert policy[key] is not None, (table, key)
            assert _normalize_policy(policy[key]) == _normalize_policy(POLICY), (table, key)
    return result


@pytest.fixture(scope="session")
def runtime_binding(tenant_runtime):
    if not isinstance(tenant_runtime, Mapping):
        raise RuntimeError("reviewed tenant_runtime mapping is required")
    if set(tenant_runtime) != set(Runtime.__dataclass_fields__):
        raise RuntimeError("tenant runtime fields differ from the frozen interface")
    runtime = Runtime(**dict(tenant_runtime))
    engines = (runtime.engine, runtime.command_engine,
               runtime.observer_engine, runtime.admin_engine)
    assert len({id(engine) for engine in engines}) == 4
    for engine in engines:
        assert isinstance(engine, Engine) and engine.dialect.name == "postgresql"
        assert engine.url.host in {"127.0.0.1", "::1"}
        assert engine.url.database == runtime.database_name
        assert not engine.echo and not engine.pool.echo
        assert (engine.url.host, engine.url.port, engine.url.database) == (
            runtime.engine.url.host, runtime.engine.url.port, runtime.database_name
        )
    assert isinstance(runtime.expected_revision, str)
    assert re.fullmatch(r"[A-Za-z0-9_]{1,64}", runtime.expected_revision)
    assert runtime.expected_revision != BASE_REVISION, "successor clinical RLS repair required"
    for value in (runtime.statement_timeout_ms, runtime.lock_timeout_ms):
        assert type(value) is int and 0 < value <= 30000
    for engine in (runtime.engine, runtime.command_engine):
        assert engine.url.username == runtime.application_role
        with engine.connect() as connection:
            identity = _assert_application_role(connection, runtime)
            assert identity["tenant"] in (None, "")
            for table in ("users", "practitioners", "access_ai_audit_log"):
                grants = connection.execute(text("""
                    SELECT has_table_privilege(current_user, :table, 'SELECT'),
                           has_any_column_privilege(current_user, :table, 'UPDATE')
                """), {"table": "public." + table}).one()
                assert tuple(grants) == (True, True), table
            assert connection.execute(text("""
                SELECT has_table_privilege(current_user,
                    'public.access_ai_audit_log', 'INSERT')
            """)).scalar_one() is True
            assert connection.execute(text("""
                SELECT has_table_privilege(current_user, 'public.practices', 'SELECT')
            """)).scalar_one() is True
    pool = runtime.command_engine.pool
    assert type(pool) is QueuePool and pool.size() == 1 and pool._max_overflow == 0
    assert math.isfinite(pool.timeout()) and 0 < pool.timeout() <= 30
    for engine in (runtime.observer_engine, runtime.admin_engine):
        with engine.connect() as connection:
            identity = _identity(connection)
            assert identity["db"] == runtime.database_name
            assert identity["role"] == identity["login"] == engine.url.username
            assert identity["role"] != runtime.application_role
    with runtime.observer_engine.connect() as connection:
        assert connection.execute(text(
            "SELECT version_num FROM public.alembic_version"
        )).scalars().all() == [runtime.expected_revision]
    return runtime


@contextmanager
def _transaction(runtime, tenant=None, *, engine=None):
    with (engine or runtime.engine).connect() as connection:
        with connection.begin():
            connection.execute(text(
                "SELECT set_config('statement_timeout', :v, true)"
            ), {"v": str(runtime.statement_timeout_ms)})
            connection.execute(text(
                "SELECT set_config('lock_timeout', :v, true)"
            ), {"v": str(runtime.lock_timeout_ms)})
            if tenant is not None:
                connection.execute(text(
                    "SELECT set_config('app.current_practice_id', :v, true)"
                ), {"v": str(tenant)})
            yield connection


def _insert(connection, table, values):
    assert table in SNAPSHOT_TABLES
    assert all(re.fullmatch(r"[a-z_]+", key) for key in values)
    columns = ", ".join(values)
    parameters = ", ".join(":" + key for key in values)
    connection.execute(text(
        f"INSERT INTO public.{table} ({columns}) VALUES ({parameters})"
    ), values)


def _row(table, tenant):
    values = {"id": uuid4(), "practice_id": tenant.practice_id}
    if table == "patients":
        values.update(first_name="Fictional", last_name="Supplement",
                      date_of_birth=date(1980, 1, 1),
                      document_url=tenant.document)
    else:
        values["patient_id"] = tenant.patient_id
    if table in {"clinical_diagnoses", "prescriptions", "mbs_claims", "invoices"}:
        values["encounter_id"] = tenant.encounter_id
    if table == "clinical_diagnoses":
        values["term"] = "Synthetic diagnosis"
    if table == "prescriptions":
        values["drug_name"] = "Synthetic medicine"
    if table == "mbs_claims":
        values["item_number"] = "00001"
    return values


def _snapshot(runtime, tenants):
    result = {}
    with runtime.observer_engine.connect() as connection:
        for table in SNAPSHOT_TABLES:
            key = "id" if table == "practices" else "practice_id"
            rows = connection.execute(text(
                f"SELECT to_jsonb(t) FROM public.{table} t "
                f"WHERE {key} IN (:p, :q) ORDER BY id"
            ), {"p": tenants[0].practice_id, "q": tenants[1].practice_id}).scalars().all()
            result[table] = rows
    return result


def _tenant_snapshot(snapshot, tenant):
    return {
        table: [row for row in rows if
                row["id" if table == "practices" else "practice_id"]
                == str(tenant.practice_id)]
        for table, rows in snapshot.items()
    }


@pytest.fixture
def world(runtime_binding):
    runtime = runtime_binding
    # Failure is deliberate on the old migration chain, never converted to skip.
    with runtime.engine.connect() as connection:
        _assert_catalogue(connection, runtime)
    from app.services.auth_service import hash_password
    tenants = []
    for label in ("P", "Q"):
        tenant = SimpleNamespace(
            practice_id=uuid4(), actor_id=uuid4(), practitioner_id=uuid4(),
            patient_id=uuid4(), encounter_id=uuid4(), rows={},
            password="Synthetic-Only-" + str(uuid4()),
        )
        tenant.email = f"supplement-{tenant.actor_id}@synthetic.invalid"
        tenant.document = f"https://synthetic.invalid/{tenant.patient_id}/document.docx"
        with _transaction(runtime, tenant.practice_id, engine=runtime.admin_engine) as connection:
            _insert(connection, "practices",
                    {"id": tenant.practice_id, "name": f"Synthetic {label}"})
            _insert(connection, "practitioners", {
                "id": tenant.practitioner_id, "practice_id": tenant.practice_id,
                "first_name": "Synthetic", "last_name": f"GP {label}", "is_active": True,
            })
            _insert(connection, "users", {
                "id": tenant.actor_id, "practice_id": tenant.practice_id,
                "email": tenant.email, "password_hash": hash_password(tenant.password),
                "role": "GP", "practitioner_id": tenant.practitioner_id, "is_active": True,
            })
            for table in TABLES:
                values = _row(table, tenant)
                if table == "patients":
                    values["id"] = tenant.patient_id
                elif table == "encounters":
                    values["id"] = tenant.encounter_id
                _insert(connection, table, values)
                tenant.rows[table] = values
        tenants.append(tenant)
    result = SimpleNamespace(runtime=runtime, p=tenants[0], q=tenants[1],
                             tenants=tuple(tenants))
    result.snapshot = lambda: _snapshot(runtime, result.tenants)
    seeded = result.snapshot()
    # Prove the observer sees both tenants, rather than comparing empty snapshots.
    for table in SNAPSHOT_TABLES:
        assert len(seeded[table]) == (0 if table == "access_ai_audit_log" else 2), table
    yield result
    # The runner disposes the whole uniquely owned database, including committed
    # clinical output. No destructive shared-database cleanup is performed here.


def test_tenant_01_migrated_catalogue_and_restricted_role(runtime_binding, record_property):
    runtime = runtime_binding
    with runtime.engine.connect() as connection:
        _assert_application_role(connection, runtime)
        catalogue = _assert_catalogue(connection, runtime)
    record_property("tenant_catalogue", json.dumps(catalogue, sort_keys=True))


@pytest.mark.parametrize("table", TABLES)
@pytest.mark.parametrize("context", ("foreign", "missing", "empty"))
def test_tenant_02_context_filters_and_rejects_otherwise_valid_insert(world, table, context):
    runtime = world.runtime
    before = world.snapshot()
    candidate = _row(table, world.p)
    # The exact candidate succeeds with the correct context, then is rolled back.
    with runtime.engine.connect() as connection:
        for tenant in world.tenants:
            transaction = connection.begin()
            try:
                connection.execute(text(
                    "SELECT set_config('app.current_practice_id', :p, true)"
                ), {"p": str(tenant.practice_id)})
                observed = connection.execute(text(
                    f"SELECT id FROM public.{table} WHERE id IN (:p, :q)"
                ), {"p": world.p.rows[table]["id"],
                    "q": world.q.rows[table]["id"]}).scalars().all()
                assert observed == [tenant.rows[table]["id"]]
                positive = candidate if tenant is world.p else _row(table, tenant)
                _insert(connection, table, positive)
                assert connection.execute(text(
                    f"SELECT id FROM public.{table} WHERE id=:id"
                ), {"id": positive["id"]}).scalar_one() == positive["id"]
            finally:
                transaction.rollback()
        if context == "missing":
            # A fresh physical connection distinguishes an unset GUC (NULL)
            # from the empty value left by SET LOCAL after transaction end.
            connection.invalidate()
        transaction = connection.begin()
        try:
            if context != "missing":
                connection.execute(text(
                    "SELECT set_config('app.current_practice_id', :p, true)"
                ), {"p": str(world.q.practice_id) if context == "foreign" else ""})
            identity = _assert_application_role(connection, runtime)
            expected_context = {"foreign": str(world.q.practice_id),
                                "empty": "", "missing": None}[context]
            assert identity["tenant"] == expected_context
            assert connection.execute(text(
                f"SELECT id FROM public.{table} WHERE id=:id"
            ), {"id": world.p.rows[table]["id"]}).scalars().all() == []
            if context != "foreign":
                assert connection.execute(text(
                    f"SELECT id FROM public.{table} WHERE id=:id"
                ), {"id": world.q.rows[table]["id"]}).scalars().all() == []
            with pytest.raises(DBAPIError) as raised:
                _insert(connection, table, candidate)
        finally:
            transaction.rollback()
        original = raised.value.orig
        assert (getattr(original, "sqlstate", None) or
                getattr(original, "pgcode", None)) == "42501"
        message = getattr(getattr(original, "diag", None), "message_primary", "") or ""
        assert "row-level security" in message.lower()
        assert table in message, "RLS denial must identify the intended table"
        assert not connection.in_transaction()
    assert world.snapshot() == before


@contextmanager
def _sql_trace(engine):
    """Observe real SQL without replacing statements, results or authority."""
    observations = []
    held_drivers = []
    def before(connection, cursor, statement, parameters, context, executemany):
        normalized = statement.lower().replace('"', "")
        tables = [table for table in PROTECTED_READS if re.search(
            rf"\b(?:from|join)\s+(?:public\.)?{table}\b", normalized
        )]
        if not tables:
            return
        driver = connection.connection.driver_connection
        held_drivers.append(driver)  # prevent object-id reuse from masking reconnect
        probe = driver.cursor()
        try:
            probe.execute(
                "SELECT pg_backend_pid(), current_user, session_user, "
                "current_setting('app.current_practice_id', true)"
            )
            pid, role, login, tenant = probe.fetchone()
        finally:
            probe.close()
        observations.append({
            "driver": driver, "pid": pid, "role": role, "login": login,
            "tenant": tenant, "tables": tables,
        })
    event.listen(engine, "before_cursor_execute", before)
    try:
        yield observations
    finally:
        event.remove(engine, "before_cursor_execute", before)


@pytest.fixture
def http(world):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.dependencies import get_db, get_command_session_factory
    from app.routers import auth, patients, consultation

    RequestSession = sessionmaker(bind=world.runtime.engine, expire_on_commit=False)
    CommandSession = sessionmaker(bind=world.runtime.command_engine, expire_on_commit=False)
    def request_db():
        with RequestSession() as session:
            yield session
    app = FastAPI()
    app.include_router(auth.router)
    app.include_router(patients.router)
    app.include_router(consultation.router)
    app.dependency_overrides[get_db] = request_db
    app.dependency_overrides[get_command_session_factory] = lambda: CommandSession
    assert set(app.dependency_overrides) == {get_db, get_command_session_factory}
    with TestClient(app) as client:
        yield SimpleNamespace(client=client, command_session=CommandSession,
                              consultation=consultation)


def _login(http, tenant):
    response = http.client.post("/api/v1/auth/login", data={
        "username": tenant.email, "password": tenant.password,
    })
    assert response.status_code == 200
    result = response.json()
    assert result["token_type"] == "bearer"
    assert isinstance(result["access_token"], str) and result["access_token"]
    return {"Authorization": "Bearer " + result["access_token"]}


def _assert_trace(trace, tenant, runtime, required):
    assert trace
    assert set(required) <= {table for row in trace for table in row["tables"]}
    for row in trace:
        assert row["tenant"] == str(tenant.practice_id)
        assert row["role"] == row["login"] == runtime.application_role


def test_tenant_04_login_bootstrap_and_patient_http_isolation(world, http):
    before = world.snapshot()
    for tenant, foreign in ((world.p, world.q), (world.q, world.p)):
        with _sql_trace(world.runtime.engine) as login_trace:
            headers = _login(http, tenant)
        assert login_trace and any("users" in row["tables"] for row in login_trace)
        assert all(row["tenant"] in (None, "") for row in login_trace)
        assert all(row["role"] == row["login"] == world.runtime.application_role
                   for row in login_trace)
        with _transaction(world.runtime) as connection:
            assert _identity(connection)["tenant"] in (None, "")
            assert connection.execute(text(
                "SELECT id FROM public.practices WHERE id=:p"
            ), {"p": tenant.practice_id}).scalar_one() == tenant.practice_id
        with _sql_trace(world.runtime.engine) as trace:
            own = http.client.get(f"/api/v1/patients/{tenant.patient_id}", headers=headers)
            denied = http.client.get(f"/api/v1/patients/{foreign.patient_id}", headers=headers)
            unknown = http.client.get(f"/api/v1/patients/{uuid4()}", headers=headers)
        assert own.status_code == 200
        assert own.json()["id"] == str(tenant.patient_id)
        assert own.json()["practice_id"] == str(tenant.practice_id)
        assert own.json()["document_url"] == tenant.document
        assert denied.status_code == unknown.status_code == 404
        assert denied.json() == unknown.json() == {"detail": "Patient not found"}
        _assert_trace(trace, tenant, world.runtime, {"users", "patients"})
    assert world.snapshot() == before


def _body(tenant):
    return {
        "document_id": str(uuid4()), "document_context": tenant.document,
        "text_delta": "Synthetic consultation text",
        "patient_id": str(tenant.patient_id), "clinician_attested": True,
        "clinician_overrides": {
            "consultation_type": "Synthetic tenant supplement",
            "mbs_items": [{"item_number": "00001", "description": "Synthetic item"}],
            "diagnoses": [{"term": "Synthetic diagnosis", "snomed_ct_au_code": "00001"}],
            "medications": [{"drug_name": "Synthetic medicine", "dosage_text": "Synthetic only"}],
        },
    }


def _driver_state(engine, runtime):
    assert engine.pool.checkedout() == 0
    with engine.connect() as connection:
        identity = _assert_application_role(connection, runtime)
        assert identity["tenant"] in (None, "")
        driver = connection.connection.driver_connection
        # Do not bind context in this observation transaction.
        connection.rollback()
    return driver, identity["pid"]


@contextmanager
def _command_boundaries(http):
    """Session events witness actual command completion, not endpoint return alone."""
    observations = []
    cls = http.command_session.class_
    def committed(session):
        observations.append("commit")
    def rolled_back(session):
        observations.append("rollback")
    event.listen(cls, "after_commit", committed)
    event.listen(cls, "after_rollback", rolled_back)
    try:
        yield observations
    finally:
        event.remove(cls, "after_commit", committed)
        event.remove(cls, "after_rollback", rolled_back)


@contextmanager
def _abort_after_flush(http, tenant):
    """Raise only after the real P receipt and complete clinical set have flushed."""
    from app.models.ai_audit import AccessAiAuditLog
    from app.models.billing import MbsClaim
    from app.models.clinical import Encounter, ClinicalDiagnosis, Prescription
    seen = set()
    reached = []
    cls = http.command_session.class_
    models = {AccessAiAuditLog, Encounter, ClinicalDiagnosis, Prescription, MbsClaim}
    def after_flush(session, flush_context):
        for row in session.new:
            if type(row) in models and row.practice_id == tenant.practice_id:
                seen.add(type(row))
        if models <= seen:
            reached.append(True)
            raise RuntimeError("synthetic tenant supplement precommit abort")
    event.listen(cls, "after_flush", after_flush)
    try:
        yield reached
    finally:
        event.remove(cls, "after_flush", after_flush)


def _assert_finalized_delta(before, after, tenant, body, response):
    assert response.status_code == 200 and response.json()["_saved"] is True
    encounter_id = response.json()["encounter_id"]
    expected = {"encounters", "clinical_diagnoses", "prescriptions",
                "mbs_claims", "access_ai_audit_log"}
    added = {}
    for table in SNAPSHOT_TABLES:
        old = {row["id"]: row for row in before[table]}
        new = {row["id"]: row for row in after[table]}
        assert old.keys() <= new.keys()
        assert all(new[key] == value for key, value in old.items()), table
        added[table] = [value for key, value in new.items() if key not in old]
        assert len(added[table]) == (1 if table in expected else 0), table
    encounter = added["encounters"][0]
    assert encounter["id"] == encounter_id
    assert encounter["practice_id"] == str(tenant.practice_id)
    assert encounter["patient_id"] == str(tenant.patient_id)
    assert encounter["practitioner_id"] == str(tenant.practitioner_id)
    assert encounter["google_doc_id"] == body["document_id"]
    assert encounter["raw_document_text"] == body["text_delta"]
    assert encounter["status"] == "Finalized" and encounter["is_finalized"] is True
    for table in ("clinical_diagnoses", "prescriptions", "mbs_claims"):
        child = added[table][0]
        assert child["practice_id"] == str(tenant.practice_id)
        assert child["patient_id"] == str(tenant.patient_id)
        assert child["encounter_id"] == encounter_id
    assert added["prescriptions"][0]["prescribed_by"] == str(tenant.practitioner_id)
    assert added["mbs_claims"][0]["practitioner_id"] == str(tenant.practitioner_id)
    receipt = added["access_ai_audit_log"][0]
    assert receipt["practice_id"] == str(tenant.practice_id)
    assert receipt["actor_user_id"] == str(tenant.actor_id)
    assert receipt["target_resource_type"] == "encounter"
    assert receipt["target_resource_id"] == encounter_id
    assert receipt["metadata"]["patient_id"] == str(tenant.patient_id)
    assert receipt["metadata"]["practitioner_id"] == str(tenant.practitioner_id)
    assert receipt["metadata"]["attested"] is True
    assert receipt["event_type"] == "clinical.consultation.attested"
    assert receipt["decision"] == "recorded" and receipt["source_surface"] == "api"
    assert receipt["actor_roles"] == ["GP"]


@pytest.mark.parametrize("completion", ("commit", "rollback"))
def test_tenant_05_clinical_context_rebinds_same_physical_connection(world, http, completion):
    runtime = world.runtime
    p_headers, q_headers = _login(http, world.p), _login(http, world.q)
    before = world.snapshot()
    driver, pid = _driver_state(runtime.command_engine, runtime)
    p_body = _body(world.p)
    with _sql_trace(runtime.command_engine) as p_trace:
        with _command_boundaries(http) as p_boundaries:
            if completion == "rollback":
                with _abort_after_flush(http, world.p) as reached:
                    p_response = http.client.post("/api/v1/finalize", json=p_body, headers=p_headers)
                assert reached == [True], "real receipt and all clinical children must flush"
                assert p_response.status_code == 200
                assert p_response.json() == {
                    "_saved": False,
                    "_save_error": "Encounter save failed. Please contact support.",
                }
                assert p_boundaries == ["rollback"]
            else:
                p_response = http.client.post("/api/v1/finalize", json=p_body, headers=p_headers)
                assert p_boundaries == ["commit"]
    # The pinned route SELECTs the receipt for idempotency before any INSERT.
    _assert_trace(p_trace, world.p, runtime, {"users", "practitioners", "patients",
                                            "access_ai_audit_log"})
    after_p = world.snapshot()
    if completion == "commit":
        _assert_finalized_delta(before, after_p, world.p, p_body, p_response)
    else:
        assert after_p == before
    next_driver, next_pid = _driver_state(runtime.command_engine, runtime)
    assert next_driver is driver and next_pid == pid
    # Failed cross-tenant lookup and unknown ID are indistinguishable.
    for patient_id in (world.p.patient_id, uuid4()):
        rejected_body = _body(world.q)
        rejected_body["patient_id"] = str(patient_id)
        with _sql_trace(runtime.command_engine) as rejected_trace:
            response = http.client.post("/api/v1/finalize", json=rejected_body, headers=q_headers)
        assert response.status_code == 404 and response.json() == FINALIZE_NOT_FOUND
        _assert_trace(rejected_trace, world.q, runtime, {"users", "practitioners", "patients"})
        assert world.snapshot() == after_p
        assert all(row["driver"] is driver and row["pid"] == pid for row in rejected_trace)
        check_driver, check_pid = _driver_state(runtime.command_engine, runtime)
        assert check_driver is driver and check_pid == pid
    q_body = _body(world.q)
    with _sql_trace(runtime.command_engine) as q_trace:
        with _command_boundaries(http) as q_boundaries:
            q_response = http.client.post("/api/v1/finalize", json=q_body, headers=q_headers)
    assert q_boundaries == ["commit"]
    _assert_trace(q_trace, world.q, runtime, {"users", "practitioners", "patients",
                                            "access_ai_audit_log"})
    assert all(row["driver"] is driver and row["pid"] == pid for row in p_trace + q_trace)
    after_q = world.snapshot()
    _assert_finalized_delta(after_p, after_q, world.q, q_body, q_response)
    assert _tenant_snapshot(after_q, world.p) == _tenant_snapshot(after_p, world.p)
    final_driver, final_pid = _driver_state(runtime.command_engine, runtime)
    assert final_driver is driver and final_pid == pid
