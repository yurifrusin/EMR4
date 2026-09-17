"""Isolated appointment collision tests; authored source, not runtime evidence.

The reviewed external runner owns creation, real Alembic migration, import/input
verification, exact node selection, whole-process limits and database disposal.
It supplies the explicit ``appointment_runtime`` pytest fixture. This module
never discovers a database, imports conftest, creates ORM tables or starts an app.
Missing runtime inputs are errors, not skips. Database variants exercise real SQL
as the application role; they do not establish HTTP/confirmation authority.
"""

from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import math
import threading
import time
from types import MappingProxyType
from uuid import UUID, uuid5
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError


COLLISION_CONSTRAINT = "ex_appointments_practice_practitioner_no_overlap"
BLOCKING_STATUSES = ("Booked", "Confirmed", "Arrived", "InConsult", "Completed")
NONBLOCKING_STATUSES = ("Cancelled", "NoShow", "DNA")
TENANT_SETTING = "app.current_practice_id"
SNAPSHOT_TABLES = ("appointments", "appointment_audit_log", "appointment_command_idempotency")
INSERT_COLUMNS = (
    "id", "practice_id", "location_id", "patient_name_provisional",
    "practitioner_id", "start_time", "appointment_date", "start_time_local",
    "duration_minutes", "status", "booked_via", "appointment_state_version",
)
UPDATE_COLUMNS = frozenset(INSERT_COLUMNS) - {"id", "practice_id"}
CASE_NAMESPACE = UUID("b855a5b4-fccd-4c1a-8d0f-88992b43b702")


def _finite_positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(f"runtime field {name} must be numeric")
    if not math.isfinite(value) or value <= 0:
        raise RuntimeError(f"runtime field {name} must be finite and positive")
    return value


def _collision(error):
    original = error.orig if isinstance(error, DBAPIError) else error
    return (
        getattr(original, "sqlstate", None) or getattr(original, "pgcode", None),
        getattr(getattr(original, "diag", None), "constraint_name", None),
    ) == ("23P01", COLLISION_CONSTRAINT)


def _assert_db_collision(writer, action):
    """Observe direct database failure only; public mapping is a separate test."""
    with pytest.raises(DBAPIError) as raised:
        action()
    writer.rollback()
    assert not writer.connection.in_transaction(), "rollback must complete before classification"
    assert _collision(raised.value), "write failed for a cause other than the overlap constraint"
    return raised.value


@dataclass(frozen=True)
class Runtime:
    engine: Engine
    observer_engine: Engine
    admin_engine: Engine
    database_name: str
    application_role: str
    expected_revision: str
    wait_timeout_seconds: float
    test_deadline_seconds: float

    @property
    def application_engine(self):
        return self.engine

    @property
    def run_id(self):
        return uuid5(CASE_NAMESPACE, self.database_name)

    @property
    def start(self):
        return datetime(2040, 1, 9, 10, tzinfo=timezone.utc)

    timezone_name = "UTC"

    @property
    def statement_timeout_ms(self):
        return math.ceil(self.wait_timeout_seconds * 2000)

    @property
    def lock_timeout_ms(self):
        return math.ceil(self.wait_timeout_seconds * 1500)

    @property
    def schedule_timeout_seconds(self):
        return self.wait_timeout_seconds

    @property
    def thread_join_seconds(self):
        return self.test_deadline_seconds

    @property
    def poll_interval_seconds(self):
        return min(0.02, self.wait_timeout_seconds / 100)


@pytest.fixture(scope="session")
def runtime_binding(appointment_runtime):
    supplied = appointment_runtime
    if not isinstance(supplied, Mapping):
        raise RuntimeError("the reviewed isolated runner must supply appointment runtime inputs")
    required = set(Runtime.__dataclass_fields__)
    if set(supplied) != required:
        raise RuntimeError("appointment runtime fields differ from the reviewed fixture interface")
    values = dict(supplied)
    for name in ("engine", "observer_engine", "admin_engine"):
        engine = values[name]
        if not isinstance(engine, Engine) or engine.dialect.name != "postgresql":
            raise RuntimeError(f"{name} must be the bound PostgreSQL engine")
        if engine.url.host not in {"127.0.0.1", "::1"}:
            raise RuntimeError("test database must use an explicit loopback address")
        if engine.url.database != values["database_name"] or engine.echo:
            raise RuntimeError("database identity or SQL logging differs from the binding")
    if len({id(values[name]) for name in ("engine", "observer_engine", "admin_engine")}) != 3:
        raise RuntimeError("application, observer and administrative engines must be distinct")
    app_url = values["engine"].url
    for name in ("observer_engine", "admin_engine"):
        other_url = values[name].url
        if (app_url.host, app_url.port, app_url.database) != (other_url.host, other_url.port, other_url.database):
            raise RuntimeError("all engines must address the same bound disposable database")
    for name in ("wait_timeout_seconds", "test_deadline_seconds"):
        _finite_positive(values[name], name)
    if values["test_deadline_seconds"] <= 3 * values["wait_timeout_seconds"]:
        raise RuntimeError("test deadline must allow observation, database timeout and bounded cleanup")
    if values["expected_revision"] != "y4z5a6b7c8d9":
        raise RuntimeError("unexpected appointment migration revision")
    runtime = Runtime(**values)
    _verify_runtime_database(runtime)
    return runtime


def _verify_runtime_database(runtime):
    with runtime.application_engine.connect() as connection:
        identity = connection.execute(text("""
            SELECT current_database() AS db, current_user AS role, session_user AS login,
                   current_setting('server_version_num')::integer AS version,
                   current_setting('row_security') AS row_security,
                   current_setting('app.current_practice_id', true) AS tenant
        """)).mappings().one()
        assert identity["db"] == runtime.database_name
        assert identity["role"] == identity["login"] == runtime.application_role
        assert identity["row_security"] == "on"
        assert identity["tenant"] in (None, "")
        elevated = connection.execute(text("""
            SELECT rolname FROM pg_roles
            WHERE (rolsuper OR rolbypassrls)
              AND (rolname = current_user OR pg_has_role(current_user, oid, 'MEMBER'))
        """)).scalars().all()
        assert not elevated, "application role has elevated membership"
        policies = connection.execute(text("""
            SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity,
                   pg_get_userbyid(c.relowner) AS owner
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relname IN
              ('appointments','appointment_audit_log','appointment_command_idempotency')
            ORDER BY c.relname
        """)).mappings().all()
        assert {row["relname"] for row in policies} == set(SNAPSHOT_TABLES)
        assert all(row["relrowsecurity"] and row["relforcerowsecurity"] for row in policies)
        assert all(row["owner"] != runtime.application_role for row in policies)
        constraint = connection.execute(text("""
            SELECT c.contype, c.condeferrable, c.condeferred, c.convalidated,
                   pg_get_constraintdef(c.oid) AS definition
            FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE n.nspname = 'public' AND t.relname = 'appointments' AND c.conname = :name
        """), {"name": COLLISION_CONSTRAINT}).mappings().one()
        assert constraint["contype"] == "x" and constraint["convalidated"]
        assert not constraint["condeferrable"] and not constraint["condeferred"]
    for engine in (runtime.observer_engine, runtime.admin_engine):
        with engine.connect() as connection:
            identity = connection.execute(text("SELECT current_database(), current_user, session_user")).one()
            assert tuple(identity) == (runtime.database_name, engine.url.username, engine.url.username)
            if engine is runtime.observer_engine:
                assert connection.execute(text("SELECT version_num FROM public.alembic_version")).scalars().all() == [runtime.expected_revision]


def _begin(connection, runtime, practice_id=None):
    transaction = connection.begin()
    connection.execute(text("SELECT set_config('statement_timeout', :value, true)"), {"value": str(runtime.statement_timeout_ms)})
    connection.execute(text("SELECT set_config('lock_timeout', :value, true)"), {"value": str(runtime.lock_timeout_ms)})
    connection.execute(text("SELECT set_config('row_security', 'on', true)"))
    if practice_id is not None:
        connection.execute(text("SELECT set_config('app.current_practice_id', :practice, true)"), {"practice": str(practice_id)})
    return transaction


class Writer:
    def __init__(self, world, practice_id):
        self.world = world
        self.practice_id = practice_id
        self.connection = None
        self.transaction = None
        self.pid = None

    def __enter__(self):
        with self.world.writer_lock:
            assert len(self.world.active_writers) < 2, "only two test writers are permitted"
            self.world.active_writers.add(self)
        try:
            self.connection = self.world.runtime.application_engine.connect()
            self.transaction = _begin(self.connection, self.world.runtime, self.practice_id)
            self.pid = self.connection.execute(text("SELECT pg_backend_pid()")).scalar_one()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_):
        try:
            if self.connection is not None:
                try:
                    self.connection.rollback()
                finally:
                    self.connection.close()
        finally:
            if self.connection is None or self.connection.closed:
                with self.world.writer_lock:
                    self.world.active_writers.discard(self)

    def insert(self, row):
        assert set(row) == set(INSERT_COLUMNS), "direct insert shape differs from the test fixture"
        columns = ", ".join(INSERT_COLUMNS)
        parameters = ", ".join(":" + name for name in INSERT_COLUMNS)
        self.connection.execute(text(f"INSERT INTO public.appointments ({columns}) VALUES ({parameters})"), dict(row))

    def update(self, row_id, **changes):
        assert changes and set(changes) <= UPDATE_COLUMNS
        assignments = ", ".join(f"{column} = :{column}" for column in changes)
        result = self.connection.execute(text(f"UPDATE public.appointments SET {assignments} WHERE id = :row_id AND practice_id = :bound_practice"), {**changes, "row_id": row_id, "bound_practice": self.practice_id})
        assert result.rowcount == 1, "update did not reach exactly the intended tenant row"

    def get(self, row_id):
        result = self.connection.execute(text("SELECT * FROM public.appointments WHERE id = :id"), {"id": row_id}).mappings().one_or_none()
        return None if result is None else dict(result)

    def all_rows(self):
        return [dict(row) for row in self.connection.execute(text("SELECT * FROM public.appointments ORDER BY id")).mappings()]

    def commit(self):
        self.transaction.commit()

    def rollback(self):
        if self.transaction.is_active:
            self.transaction.rollback()


class CaseWorld:
    def __init__(self, runtime, node_id):
        self.runtime = runtime
        self.namespace = uuid5(CASE_NAMESPACE, str(runtime.run_id) + "/" + node_id)
        for name in ("p", "q", "r", "r2", "rq", "l1", "l2", "lq", "actor", "actor_q"):
            setattr(self, name, uuid5(self.namespace, name))
        self.start = runtime.start
        self.timezone_name = runtime.timezone_name
        self.writer_lock = threading.Lock()
        self.active_writers = set()

    def row(self, label, *, practice_id=None, practitioner_id=None, location_id=None, start=None, minutes=30, status="Booked"):
        practice_id = self.p if practice_id is None else practice_id
        practitioner_id = (self.rq if practice_id == self.q else self.r) if practitioner_id is None else practitioner_id
        start = self.start if start is None else start
        assert start.utcoffset() is not None
        local = start.astimezone(ZoneInfo(self.timezone_name))
        return {
            "id": uuid5(self.namespace, "appointment/" + label),
            "practice_id": practice_id, "location_id": location_id,
            "patient_name_provisional": "Synthetic appointment test",
            "practitioner_id": practitioner_id, "start_time": start,
            "appointment_date": local.date(), "start_time_local": local.time().replace(tzinfo=None),
            "duration_minutes": minutes, "status": status,
            "booked_via": "Receptionist", "appointment_state_version": 1,
        }

    def writer(self, practice_id=None):
        return Writer(self, self.p if practice_id is None else practice_id)

    def snapshot(self, practice_id=None):
        practice_id = self.p if practice_id is None else practice_id
        with self.writer(practice_id) as writer:
            result = {}
            for table in SNAPSHOT_TABLES:
                rows = writer.connection.execute(text(f"SELECT to_jsonb(t) FROM public.{table} t WHERE practice_id = :practice ORDER BY id"), {"practice": practice_id}).scalars().all()
                result[table] = json.dumps(rows, sort_keys=True, separators=(",", ":"))
        return MappingProxyType(result)

    assert_collision = staticmethod(_assert_db_collision)

    def set_timezone(self, name):
        ZoneInfo(name)
        assert not self.active_writers
        with self.runtime.admin_engine.begin() as connection:
            changed = connection.execute(text("UPDATE public.practices SET timezone = :zone WHERE id = :practice"), {"zone": name, "practice": self.p})
            assert changed.rowcount == 1
        self.timezone_name = name

    def set_actor_active(self, active):
        assert type(active) is bool
        assert not self.active_writers
        with self.runtime.admin_engine.begin() as connection:
            changed = connection.execute(text("UPDATE public.users SET is_active = :active WHERE id = :actor AND practice_id = :practice"), {"active": active, "actor": self.actor, "practice": self.p})
            assert changed.rowcount == 1

    def seed(self):
        with self.runtime.admin_engine.begin() as connection:
            existing = connection.execute(text("SELECT count(*) FROM public.practices WHERE id IN (:p, :q)"), {"p": self.p, "q": self.q}).scalar_one()
            assert existing == 0, "case namespace already exists; do not reuse or clean it silently"
            for practice in (self.p, self.q):
                connection.execute(text("INSERT INTO public.practices (id,name,timezone) VALUES (:id,'Synthetic collision test',:zone)"), {"id": practice, "zone": self.runtime.timezone_name})
            for location, practice in ((self.l1, self.p), (self.l2, self.p), (self.lq, self.q)):
                connection.execute(text("INSERT INTO public.practice_locations (id,practice_id,name,is_active) VALUES (:id,:practice,'Synthetic test site',true)"), {"id": location, "practice": practice})
            for practitioner, practice in ((self.r, self.p), (self.r2, self.p), (self.rq, self.q)):
                connection.execute(text("INSERT INTO public.practitioners (id,practice_id,first_name,last_name,is_active) VALUES (:id,:practice,'Synthetic','Practitioner',true)"), {"id": practitioner, "practice": practice})
            for actor, practice in ((self.actor, self.p), (self.actor_q, self.q)):
                connection.execute(text("INSERT INTO public.users (id,practice_id,email,password_hash,role,is_active) VALUES (:id,:practice,:email,'invalid-synthetic-no-login','Receptionist',true)"), {"id": actor, "practice": practice, "email": str(actor) + '@example.invalid'})

    def cleanup(self):
        with self.writer_lock:
            assert not self.active_writers, "writer remains open; outer runner must reconcile before disposal"
        with self.runtime.observer_engine.connect() as observer:
            with observer.begin():
                observer.execute(text("SET TRANSACTION READ ONLY"))
                remaining = observer.execute(text("SELECT count(*) FROM pg_stat_activity WHERE datname = :database AND usename = :role AND xact_start IS NOT NULL"), {"database": self.runtime.database_name, "role": self.runtime.application_role}).scalar_one()
                assert remaining == 0, "application transaction remains open; preserve case for outer reconciliation"
        with self.runtime.admin_engine.begin() as connection:
            parameters = {"p": self.p, "q": self.q}
            retained_counts = {}
            for table in ("appointment_audit_log", "appointment_command_idempotency"):
                count = connection.execute(text(f"SELECT count(*) FROM public.{table} WHERE practice_id IN (:p,:q)"), parameters).scalar_one()
                retained_counts[table] = count
            if any(retained_counts.values()):
                # Real HTTP commands create immutable audit evidence. Preserve
                # that case's unique synthetic tenant for the reviewed outer DB
                # drop; do not disable RLS/triggers or misreport row deletion.
                return {"disposition": "retained_for_outer_database_drop", "practices": [str(self.p), str(self.q)], "evidence_rows": retained_counts}
            for table in ("appointments", "users", "practitioners", "practice_locations", "practices"):
                column = "id" if table == "practices" else "practice_id"
                connection.execute(text(f"DELETE FROM public.{table} WHERE {column} IN (:p,:q)"), parameters)
            for table in ("appointments", "users", "practitioners", "practice_locations", "practices"):
                column = "id" if table == "practices" else "practice_id"
                assert connection.execute(text(f"SELECT count(*) FROM public.{table} WHERE {column} IN (:p,:q)"), parameters).scalar_one() == 0
        return {"disposition": "case_rows_deleted", "practices": [str(self.p), str(self.q)]}


@pytest.fixture
def case_world(runtime_binding, request):
    world = CaseWorld(runtime_binding, request.node.nodeid)
    world.seed()
    try:
        yield world
    finally:
        outcome = world.cleanup()
        request.node.user_properties.append(("synthetic_case_cleanup", json.dumps(outcome, sort_keys=True)))


def _remaining(deadline):
    return max(0.0, deadline - time.monotonic())


def _observe_database_wait(world, waiting_pid, blocking_pid, finished, deadline):
    """A real PostgreSQL dependency is the oracle; polling delay is not proof."""
    with world.runtime.observer_engine.connect() as observer:
        with observer.begin():
            observer.execute(text("SET TRANSACTION READ ONLY"))
            observer.execute(text("SELECT set_config('statement_timeout', :value, true)"), {"value": str(max(1, math.ceil(_remaining(deadline) * 1000)))})
            while _remaining(deadline) > 0:
                observer.execute(text("SELECT pg_stat_clear_snapshot()"))
                row = observer.execute(text("""
                    SELECT pid, wait_event_type, wait_event, state,
                           pg_blocking_pids(pid) AS blockers
                    FROM pg_stat_activity
                    WHERE datname = :database AND pid = :waiting
                """), {"database": world.runtime.database_name, "waiting": waiting_pid}).mappings().one_or_none()
                if row is not None and blocking_pid in row["blockers"]:
                    assert row["wait_event_type"] == "Lock"
                    assert row["state"] == "active"
                    return dict(row)
                if finished.is_set():
                    pytest.fail("contender completed before the required PostgreSQL wait was observed")
                finished.wait(min(world.runtime.poll_interval_seconds, _remaining(deadline)))
    pytest.fail("database wait was not observed within the reviewed schedule budget")


def _controlled_wait(world, first_action, second_action, *, release, second_outcome):
    deadline = time.monotonic() + world.runtime.test_deadline_seconds
    ready = threading.Event()
    finished = threading.Event()
    result = {}

    def contender():
        try:
            with world.writer() as writer:
                result["pid"] = writer.pid
                ready.set()
                try:
                    second_action(writer)
                    writer.commit()
                    result["outcome"] = "committed"
                except DBAPIError as error:
                    writer.rollback()
                    assert not writer.connection.in_transaction()
                    if not _collision(error):
                        raise
                    result["outcome"] = "collision"
        except BaseException as error:
            result["error"] = error
        finally:
            ready.set()
            finished.set()

    thread = threading.Thread(target=contender, name="appointment-contender", daemon=False)
    started = False
    observation = None
    with world.writer() as first:
        try:
            first_action(first)
            thread.start()
            started = True
            assert ready.wait(min(world.runtime.wait_timeout_seconds, _remaining(deadline))), "contender did not open its bounded writer"
            if "error" in result:
                raise result["error"]
            assert result["pid"] != first.pid
            observation = _observe_database_wait(
                world, result["pid"], first.pid, finished,
                min(deadline, time.monotonic() + world.runtime.wait_timeout_seconds),
            )
            if release == "commit":
                first.commit()
            elif release == "rollback":
                first.rollback()
            else:
                raise AssertionError("unknown staged-writer release")
        finally:
            # Release our own lock even if the observation or an assertion fails.
            # Database timeouts and the outer process supervisor bound the child;
            # a live thread is never hidden by daemonization or an automatic retry.
            if first.connection.in_transaction():
                first.connection.rollback()
            if started:
                thread.join(_remaining(deadline))
                assert not thread.is_alive(), "contender exit is unconfirmed; outer runner must reconcile"
    if "error" in result:
        raise result["error"]
    assert result["outcome"] == second_outcome
    return observation


@pytest.mark.parametrize(
    "first_site,second_site,reverse",
    [pytest.param("l1", "l2", False, id="APT-R1-db-sites-forward"),
     pytest.param("l1", "l2", True, id="APT-R1-db-sites-reverse"),
     pytest.param("none", "l1", False, id="APT-R1-db-null-forward"),
     pytest.param("none", "l1", True, id="APT-R1-db-null-reverse")],
)
def test_apt_r1_concurrent_creates_have_one_occupant(case_world, first_site, second_site, reverse):
    rows = [case_world.row("r1-left", location_id=_site(case_world, first_site)),
            case_world.row("r1-right", location_id=_site(case_world, second_site))]
    if reverse:
        rows.reverse()
    _controlled_wait(case_world, lambda w: w.insert(rows[0]), lambda w: w.insert(rows[1]), release="commit", second_outcome="collision")
    assert _read(case_world, case_world.p, rows[0]["id"])["start_time"] == rows[0]["start_time"]
    assert _read(case_world, case_world.p, rows[1]["id"]) is None
    with case_world.writer() as reader:
        assert len(reader.all_rows()) == 1


@pytest.mark.parametrize("operation", [
    pytest.param("move", id="APT-R2-db-move"),
    pytest.param("resize", id="APT-R2-db-resize"),
    pytest.param("reactivate", id="APT-R2-db-reactivate"),
    pytest.param("both-reactivate", id="APT-R2-db-both-reactivate"),
])
def test_apt_r2_concurrent_occupancy_changes_are_serializable(case_world, operation):
    winner = case_world.row("r2-winner", location_id=case_world.l1)
    target = case_world.row("r2-target", location_id=None, start=case_world.start + timedelta(minutes=60))
    if operation == "move":
        change = _time_changes(case_world.start)
    elif operation == "resize":
        target = case_world.row("r2-target", location_id=None, start=case_world.start - timedelta(minutes=30), minutes=30)
        change = {"duration_minutes": 60}
    else:
        target = case_world.row("r2-target", location_id=None, status="Cancelled")
        change = {"status": "Booked"}
    _insert_and_commit(case_world, target)
    before_target = _read(case_world, case_world.p, target["id"])
    before = case_world.snapshot()
    if operation == "both-reactivate":
        winner["status"] = "NoShow"
        _insert_and_commit(case_world, winner)
        first_action = lambda w: w.update(winner["id"], status="Booked")
    else:
        first_action = lambda w: w.insert(winner)
    _controlled_wait(case_world, first_action, lambda w: w.update(target["id"], **change), release="commit", second_outcome="collision")
    assert _read(case_world, case_world.p, target["id"]) == before_target
    assert _read(case_world, case_world.p, winner["id"])["status"] == "Booked"
    after = case_world.snapshot()
    assert after["appointment_audit_log"] == before["appointment_audit_log"]
    assert after["appointment_command_idempotency"] == before["appointment_command_idempotency"]


@pytest.mark.parametrize("sites", [pytest.param(("l1", "l2"), id="APT-R3-db-sites"), pytest.param(("none", "l1"), id="APT-R3-db-null")])
def test_apt_r3_rollback_releases_pending_conflict(case_world, sites):
    first = case_world.row("r3-first", location_id=_site(case_world, sites[0]))
    second = case_world.row("r3-second", location_id=_site(case_world, sites[1]))
    _controlled_wait(case_world, lambda w: w.insert(first), lambda w: w.insert(second), release="rollback", second_outcome="committed")
    assert _read(case_world, case_world.p, first["id"]) is None
    assert _read(case_world, case_world.p, second["id"])["start_time"] == second["start_time"]
    with case_world.writer() as reader:
        assert len(reader.all_rows()) == 1


@pytest.mark.parametrize("release", [pytest.param("commit", id="APT-R4-db-cancel-commit"), pytest.param("rollback", id="APT-R4-db-cancel-rollback")])
def test_apt_r4_cancellation_and_create_follow_a_serial_order(case_world, release):
    first = case_world.row("r4-incumbent", location_id=case_world.l1)
    second = case_world.row("r4-contender", location_id=None)
    _insert_and_commit(case_world, first)
    before = case_world.snapshot()
    _controlled_wait(case_world, lambda w: w.update(first["id"], status="Cancelled"), lambda w: w.insert(second), release=release, second_outcome="committed" if release == "commit" else "collision")
    if release == "commit":
        assert _read(case_world, case_world.p, first["id"])["status"] == "Cancelled"
        assert _read(case_world, case_world.p, second["id"])["status"] == "Booked"
    else:
        assert case_world.snapshot() == before


@pytest.mark.parametrize("kind", [pytest.param("adjacent", id="APT-R5-db-adjacent"), pytest.param("different-practitioner", id="APT-R5-db-different-practitioner")])
def test_apt_r5_nonconflicting_concurrent_writes_both_commit(case_world, kind):
    first = case_world.row("r5-first", location_id=case_world.l1)
    second = case_world.row("r5-second", location_id=None, start=case_world.start + timedelta(minutes=30)) if kind == "adjacent" else case_world.row("r5-second", practitioner_id=case_world.r2, location_id=None)
    deadline = time.monotonic() + case_world.runtime.test_deadline_seconds
    before_flush = threading.Barrier(3)
    after_flush = threading.Barrier(3)
    release_commit = threading.Event()
    cancel = threading.Event()
    results = [{}, {}]

    def work(index, row):
        try:
            with case_world.writer() as writer:
                results[index]["pid"] = writer.pid
                before_flush.wait(_remaining(deadline))
                writer.insert(row)
                results[index]["flushed"] = True
                after_flush.wait(_remaining(deadline))
                assert release_commit.wait(_remaining(deadline)), "commit release timed out"
                if cancel.is_set():
                    return
                writer.commit()
                results[index]["committed"] = True
        except BaseException as error:
            results[index]["error"] = error
            before_flush.abort()
            after_flush.abort()

    threads = [threading.Thread(target=work, args=(index, row), name=f"appointment-writer-{index}", daemon=False) for index, row in enumerate((first, second))]
    started = []
    schedule_complete = False
    try:
        for thread in threads:
            thread.start()
            started.append(thread)
        before_flush.wait(_remaining(deadline))
        after_flush.wait(_remaining(deadline))
        assert all(result.get("flushed") and not result.get("committed") for result in results)
        assert results[0]["pid"] != results[1]["pid"]
        schedule_complete = True
        release_commit.set()
    finally:
        if not schedule_complete:
            cancel.set()
            before_flush.abort()
            after_flush.abort()
        release_commit.set()
        for thread in started:
            thread.join(_remaining(deadline))
        assert not any(thread.is_alive() for thread in started), "writer exit is unconfirmed; outer runner must reconcile"
    for result in results:
        if "error" in result:
            raise result["error"]
        assert result.get("committed") is True
    assert _read(case_world, case_world.p, first["id"])["start_time"] == first["start_time"]
    assert _read(case_world, case_world.p, second["id"])["start_time"] == second["start_time"]


# Sequential direct-database scenarios authored by the bounded Sol/High worker.
def _site(case_world, name):
    if name == "none":
        return None
    return getattr(case_world, name)


def _insert_and_commit(case_world, row):
    with case_world.writer(row["practice_id"]) as writer:
        writer.insert(row)
        writer.commit()


def _read(case_world, practice_id, row_id):
    with case_world.writer(practice_id) as reader:
        return reader.get(row_id)


def _time_changes(instant):
    return {
        "start_time": instant,
        "appointment_date": instant.date(),
        "start_time_local": instant.timetz().replace(tzinfo=None),
    }


SITE_ORDER_CASES = [
    pytest.param("none", "none", False, id="APT-S1-db-null-null-forward"),
    pytest.param("none", "none", True, id="APT-S1-db-null-null-reverse"),
    pytest.param("none", "l1", False, id="APT-S1-db-null-l1-forward"),
    pytest.param("none", "l1", True, id="APT-S1-db-null-l1-reverse"),
    pytest.param("none", "l2", False, id="APT-S1-db-null-l2-forward"),
    pytest.param("none", "l2", True, id="APT-S1-db-null-l2-reverse"),
    pytest.param("l1", "l1", False, id="APT-S1-db-l1-l1-forward"),
    pytest.param("l1", "l1", True, id="APT-S1-db-l1-l1-reverse"),
    pytest.param("l1", "l2", False, id="APT-S1-db-l1-l2-forward"),
    pytest.param("l1", "l2", True, id="APT-S1-db-l1-l2-reverse"),
    pytest.param("l2", "l2", False, id="APT-S1-db-l2-l2-forward"),
    pytest.param("l2", "l2", True, id="APT-S1-db-l2-l2-reverse"),
]


@pytest.mark.parametrize("site_a,site_b,reverse", SITE_ORDER_CASES)
def test_apt_s1_create_overlap_is_location_and_order_independent(
    case_world, site_a, site_b, reverse
):
    first_site, second_site = (_site(case_world, site_a), _site(case_world, site_b))

    incumbent = case_world.row(
        "s1-incumbent",
        location_id=first_site,
        start=case_world.start,
        minutes=60,
    )
    contender = case_world.row(
        "s1-contender",
        location_id=second_site,
        start=case_world.start + timedelta(minutes=15),
        minutes=30,
    )

    if reverse:
        incumbent, contender = contender, incumbent

    _insert_and_commit(case_world, incumbent)
    assert _read(case_world, case_world.p, incumbent["id"])["id"] == incumbent["id"]
    before = case_world.snapshot()

    with case_world.writer() as writer:
        case_world.assert_collision(writer, lambda: writer.insert(contender))
        writer.rollback()

    assert case_world.snapshot() == before
    assert _read(case_world, case_world.p, contender["id"]) is None


OVERLAP_SHAPE_CASES = [
    pytest.param(0, 60, 0, 60, id="APT-S2-db-equal"),
    pytest.param(0, 90, 15, 30, id="APT-S2-db-first-contains-second"),
    pytest.param(15, 30, 0, 90, id="APT-S2-db-second-contains-first"),
    pytest.param(0, 60, -15, 30, id="APT-S2-db-left-partial"),
    pytest.param(0, 60, 45, 30, id="APT-S2-db-right-partial"),
]


@pytest.mark.parametrize(
    "first_offset,first_minutes,second_offset,second_minutes", OVERLAP_SHAPE_CASES
)
def test_apt_s2_overlap_shape_and_containment_are_symmetric(
    case_world, first_offset, first_minutes, second_offset, second_minutes
):
    incumbent = case_world.row(
        "s2-incumbent",
        location_id=case_world.l1,
        start=case_world.start + timedelta(minutes=first_offset),
        minutes=first_minutes,
    )
    contender = case_world.row(
        "s2-contender",
        location_id=None,
        start=case_world.start + timedelta(minutes=second_offset),
        minutes=second_minutes,
    )

    _insert_and_commit(case_world, incumbent)
    assert _read(case_world, case_world.p, incumbent["id"])["id"] == incumbent["id"]
    before = case_world.snapshot()

    with case_world.writer() as writer:
        case_world.assert_collision(writer, lambda: writer.insert(contender))
        writer.rollback()

    assert case_world.snapshot() == before


BOUNDARY_CASES = [
    pytest.param("ordinary", 0, 30, 30, 30, id="APT-S3-db-right-adjacent"),
    pytest.param("ordinary", 0, 30, -30, 30, id="APT-S3-db-left-adjacent"),
    pytest.param("ordinary", 0, 30, 45, 30, id="APT-S3-db-positive-gap"),
    pytest.param("cross-midnight", 0, 30, 30, 30, id="APT-S3-db-cross-midnight-adjacent"),
]


@pytest.mark.parametrize(
    "clock_case,first_offset,first_minutes,second_offset,second_minutes",
    BOUNDARY_CASES,
)
def test_apt_s3_half_open_boundaries_allow_adjacency(
    case_world,
    clock_case,
    first_offset,
    first_minutes,
    second_offset,
    second_minutes,
):
    base = case_world.start
    if clock_case == "cross-midnight":
        base = base.replace(hour=23, minute=45, second=0, microsecond=0)

    first_start = base + timedelta(minutes=first_offset)
    second_start = base + timedelta(minutes=second_offset)
    first = case_world.row(
        "s3-first",
        location_id=None,
        start=first_start,
        minutes=first_minutes,
    )
    second = case_world.row(
        "s3-second",
        location_id=case_world.l2,
        start=second_start,
        minutes=second_minutes,
    )

    _insert_and_commit(case_world, first)
    _insert_and_commit(case_world, second)

    first_read = _read(case_world, case_world.p, first["id"])
    second_read = _read(case_world, case_world.p, second["id"])
    assert first_read["start_time"] == first_start
    assert second_read["start_time"] == second_start
    assert first_read["duration_minutes"] == first_minutes
    assert second_read["duration_minutes"] == second_minutes


KEY_CASES = [
    pytest.param("same-tenant", id="APT-S4-db-same-tenant-different-practitioner"),
    pytest.param("different-tenant", id="APT-S4-db-different-tenant-different-practitioner"),
]


@pytest.mark.parametrize("key_case", KEY_CASES)
def test_apt_s4_practitioner_and_tenant_keys_do_not_overblock(case_world, key_case):
    first = case_world.row(
        "s4-first",
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
        minutes=60,
    )
    if key_case == "same-tenant":
        second = case_world.row(
            "s4-second",
            practice_id=case_world.p,
            practitioner_id=case_world.r2,
            location_id=None,
            start=case_world.start,
            minutes=60,
        )
    else:
        second = case_world.row(
            "s4-second",
            practice_id=case_world.q,
            practitioner_id=case_world.rq,
            location_id=case_world.lq,
            start=case_world.start,
            minutes=60,
        )

    _insert_and_commit(case_world, first)
    _insert_and_commit(case_world, second)

    assert _read(case_world, case_world.p, first["id"])["id"] == first["id"]
    assert _read(case_world, second["practice_id"], second["id"])["id"] == second["id"]


STATUS_CASES = [
    pytest.param("Booked", "incumbent", True, id="APT-S5-db-booked-incumbent"),
    pytest.param("Booked", "contender", True, id="APT-S5-db-booked-contender"),
    pytest.param("Confirmed", "incumbent", True, id="APT-S5-db-confirmed-incumbent"),
    pytest.param("Confirmed", "contender", True, id="APT-S5-db-confirmed-contender"),
    pytest.param("Arrived", "incumbent", True, id="APT-S5-db-arrived-incumbent"),
    pytest.param("Arrived", "contender", True, id="APT-S5-db-arrived-contender"),
    pytest.param("InConsult", "incumbent", True, id="APT-S5-db-inconsult-incumbent"),
    pytest.param("InConsult", "contender", True, id="APT-S5-db-inconsult-contender"),
    pytest.param("Completed", "incumbent", True, id="APT-S5-db-completed-incumbent"),
    pytest.param("Completed", "contender", True, id="APT-S5-db-completed-contender"),
    pytest.param("Cancelled", "incumbent", False, id="APT-S5-db-cancelled-incumbent"),
    pytest.param("Cancelled", "contender", False, id="APT-S5-db-cancelled-contender"),
    pytest.param("NoShow", "incumbent", False, id="APT-S5-db-noshow-incumbent"),
    pytest.param("NoShow", "contender", False, id="APT-S5-db-noshow-contender"),
    pytest.param("DNA", "incumbent", False, id="APT-S5-db-dna-incumbent"),
    pytest.param("DNA", "contender", False, id="APT-S5-db-dna-contender"),
]


@pytest.mark.parametrize("status,status_role,blocks", STATUS_CASES)
def test_apt_s5_blocking_status_predicate_is_exact(
    case_world, status, status_role, blocks
):
    incumbent_status = status if status_role == "incumbent" else "Booked"
    contender_status = status if status_role == "contender" else "Booked"
    incumbent = case_world.row(
        "s5-incumbent",
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
        status=incumbent_status,
    )
    contender = case_world.row(
        "s5-contender",
        location_id=None,
        start=case_world.start,
        minutes=30,
        status=contender_status,
    )

    _insert_and_commit(case_world, incumbent)
    assert _read(case_world, case_world.p, incumbent["id"])["status"] == incumbent_status
    before = case_world.snapshot()

    if blocks:
        with case_world.writer() as writer:
            case_world.assert_collision(writer, lambda: writer.insert(contender))
            writer.rollback()
        assert case_world.snapshot() == before
        assert _read(case_world, case_world.p, contender["id"]) is None
    else:
        _insert_and_commit(case_world, contender)
        assert case_world.snapshot() != before
        assert _read(case_world, case_world.p, contender["id"])["status"] == contender_status


ATOMIC_UPDATE_CASES = [
    pytest.param("move", id="APT-S6-db-conflicting-move-null-to-l2"),
    pytest.param("practitioner", id="APT-S6-db-conflicting-practitioner-change"),
    pytest.param("duration", id="APT-S6-db-conflicting-duration-extension"),
]


@pytest.mark.parametrize("update_case", ATOMIC_UPDATE_CASES)
def test_apt_s6_update_to_conflicting_final_row_is_atomic(case_world, update_case):
    if update_case == "move":
        incumbent = case_world.row(
            "s6-incumbent",
            location_id=case_world.l1,
            start=case_world.start,
            minutes=30,
        )
        target = case_world.row(
            "s6-target",
            location_id=None,
            start=case_world.start + timedelta(minutes=60),
            minutes=30,
        )
        changes = {
            **_time_changes(case_world.start + timedelta(minutes=15)),
            "location_id": case_world.l2,
        }
    elif update_case == "practitioner":
        incumbent = case_world.row(
            "s6-incumbent",
            practitioner_id=case_world.r,
            location_id=None,
            start=case_world.start,
            minutes=30,
        )
        target = case_world.row(
            "s6-target",
            practitioner_id=case_world.r2,
            location_id=case_world.l2,
            start=case_world.start,
            minutes=30,
        )
        changes = {"practitioner_id": case_world.r}
    else:
        incumbent = case_world.row(
            "s6-incumbent",
            location_id=None,
            start=case_world.start + timedelta(minutes=60),
            minutes=30,
        )
        target = case_world.row(
            "s6-target",
            location_id=case_world.l2,
            start=case_world.start,
            minutes=30,
        )
        changes = {"duration_minutes": 75}

    _insert_and_commit(case_world, incumbent)
    _insert_and_commit(case_world, target)
    assert _read(case_world, case_world.p, target["id"])["id"] == target["id"]
    before = case_world.snapshot()

    with case_world.writer() as writer:
        case_world.assert_collision(writer, lambda: writer.update(target["id"], **changes))
        writer.rollback()

    assert case_world.snapshot() == before


SELF_UPDATE_CASES = [
    pytest.param("shrink", id="APT-S7-db-self-shrink"),
    pytest.param("move", id="APT-S7-db-self-free-move"),
    pytest.param("unchanged", id="APT-S7-db-self-unchanged-interval-identity"),
]


@pytest.mark.parametrize("update_case", SELF_UPDATE_CASES)
def test_apt_s7_nonconflicting_update_excludes_self(case_world, update_case):
    blocker = case_world.row(
        "s7-blocker",
        location_id=None,
        start=case_world.start,
        minutes=30,
    )
    target = case_world.row(
        "s7-target",
        location_id=case_world.l1,
        start=case_world.start + timedelta(minutes=60),
        minutes=30,
    )
    _insert_and_commit(case_world, blocker)
    _insert_and_commit(case_world, target)

    blocker_before = _read(case_world, case_world.p, blocker["id"])
    target_before = _read(case_world, case_world.p, target["id"])
    snapshot_before = case_world.snapshot()

    if update_case == "shrink":
        changes = {"duration_minutes": 15}
    elif update_case == "move":
        changes = _time_changes(case_world.start + timedelta(minutes=120))
    else:
        changes = {
            **_time_changes(target_before["start_time"]),
            "practitioner_id": target_before["practitioner_id"],
            "location_id": target_before["location_id"],
            "duration_minutes": target_before["duration_minutes"],
            "status": target_before["status"],
        }

    with case_world.writer() as writer:
        writer.update(target["id"], **changes)
        writer.commit()

    blocker_after = _read(case_world, case_world.p, blocker["id"])
    target_after = _read(case_world, case_world.p, target["id"])
    assert blocker_after == blocker_before
    for field, expected in changes.items():
        assert target_after[field] == expected
    expected_version = target_before["appointment_state_version"] + 1
    assert target_after["appointment_state_version"] == expected_version
    assert target_after == {
        **target_before,
        **changes,
        "appointment_state_version": expected_version,
    }
    snapshot_after = case_world.snapshot()
    for table in SNAPSHOT_TABLES:
        if table != "appointments":
            assert snapshot_after[table] == snapshot_before[table]
    before_rows = _snapshot_rows(snapshot_before, "appointments")
    after_rows = _snapshot_rows(snapshot_after, "appointments")
    assert [row for row in after_rows if row["id"] != str(target["id"])] == [
        row for row in before_rows if row["id"] != str(target["id"])
    ]
    if update_case == "unchanged":
        expected_snapshot = dict(snapshot_before)
        for row in before_rows:
            if row["id"] == str(target["id"]):
                row["appointment_state_version"] = expected_version
        expected_snapshot["appointments"] = json.dumps(
            before_rows, sort_keys=True, separators=(",", ":")
        )
        assert snapshot_after == expected_snapshot


REACTIVATION_CASES = [
    pytest.param("Cancelled", id="APT-S8-db-cancelled-reactivation"),
    pytest.param("NoShow", id="APT-S8-db-noshow-reactivation"),
    pytest.param("DNA", id="APT-S8-db-dna-reactivation"),
]


@pytest.mark.parametrize("inactive_status", REACTIVATION_CASES)
def test_apt_s8_reactivation_rechecks_occupancy(case_world, inactive_status):
    incumbent = case_world.row(
        "s8-incumbent",
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
    )
    conflicting_inactive = case_world.row(
        "s8-conflicting-inactive",
        location_id=None,
        start=case_world.start,
        minutes=30,
        status=inactive_status,
    )
    _insert_and_commit(case_world, incumbent)
    _insert_and_commit(case_world, conflicting_inactive)
    assert _read(case_world, case_world.p, conflicting_inactive["id"])["status"] == inactive_status
    before = case_world.snapshot()

    with case_world.writer() as writer:
        case_world.assert_collision(
            writer, lambda: writer.update(conflicting_inactive["id"], status="Booked")
        )
        writer.rollback()

    assert case_world.snapshot() == before
    assert _read(case_world, case_world.p, conflicting_inactive["id"])["status"] == inactive_status

    free_inactive = case_world.row(
        "s8-free-inactive",
        location_id=case_world.l2,
        start=case_world.start + timedelta(minutes=60),
        minutes=30,
        status=inactive_status,
    )
    _insert_and_commit(case_world, free_inactive)
    with case_world.writer() as writer:
        writer.update(free_inactive["id"], status="Booked")
        writer.commit()
    assert _read(case_world, case_world.p, free_inactive["id"])["status"] == "Booked"


SLOT_RELEASE_CASES = [
    pytest.param("cancel", "l1", "none", id="APT-S9-db-cancel-releases-to-null-site"),
    pytest.param("cancel", "none", "l2", id="APT-S9-db-cancel-null-releases-to-l2"),
    pytest.param("site-edit", "l1", "l2", id="APT-S9-db-site-edit-l1-to-l2-still-blocks"),
    pytest.param("site-edit", "l1", "none", id="APT-S9-db-site-edit-l1-to-null-still-blocks"),
    pytest.param("site-edit", "none", "l1", id="APT-S9-db-site-edit-null-to-l1-still-blocks"),
]


@pytest.mark.parametrize("scenario,initial_site,new_site", SLOT_RELEASE_CASES)
def test_apt_s9_cancellation_releases_slot_without_location_exemption(
    case_world, scenario, initial_site, new_site
):
    incumbent = case_world.row(
        "s9-incumbent",
        location_id=_site(case_world, initial_site),
        start=case_world.start,
        minutes=30,
    )
    _insert_and_commit(case_world, incumbent)
    assert _read(case_world, case_world.p, incumbent["id"])["status"] == "Booked"

    if scenario == "cancel":
        with case_world.writer() as writer:
            writer.update(incumbent["id"], status="Cancelled")
            writer.commit()
        assert _read(case_world, case_world.p, incumbent["id"])["status"] == "Cancelled"

        replacement = case_world.row(
            "s9-replacement",
            location_id=_site(case_world, new_site),
            start=case_world.start,
            minutes=30,
        )
        _insert_and_commit(case_world, replacement)
        assert _read(case_world, case_world.p, replacement["id"])["status"] == "Booked"
        return

    with case_world.writer() as writer:
        writer.update(incumbent["id"], location_id=_site(case_world, new_site))
        writer.commit()
    assert _read(case_world, case_world.p, incumbent["id"])["location_id"] == _site(
        case_world, new_site
    )
    before = case_world.snapshot()

    contender = case_world.row(
        "s9-contender",
        location_id=_site(case_world, initial_site),
        start=case_world.start,
        minutes=30,
    )
    with case_world.writer() as writer:
        case_world.assert_collision(writer, lambda: writer.insert(contender))
        writer.rollback()

    assert case_world.snapshot() == before
    assert _read(case_world, case_world.p, contender["id"]) is None


# Tenant, input and real-router cases; no runtime execution has occurred.
def _bind_practice(connection, practice_id):
    connection.execute(text("SELECT set_config('app.current_practice_id', :practice, true)"), {"practice": str(practice_id)})


@pytest.mark.parametrize("completion", [pytest.param("commit", id="APT-T1-db-pooled-after-commit"), pytest.param("rollback", id="APT-T1-db-pooled-after-rollback")])
def test_apt_t1_transaction_local_context_is_absent_on_same_pooled_backend(case_world, completion):
    p_row = case_world.row("t1-p", location_id=case_world.l1)
    q_row = case_world.row("t1-q", practice_id=case_world.q, practitioner_id=case_world.rq, location_id=case_world.lq)
    _insert_and_commit(case_world, p_row)
    _insert_and_commit(case_world, q_row)
    engine = case_world.runtime.engine
    # This test owns the bound test engine. Start a fresh idle pool so the next
    # checkout can prove reuse of the exact backend, not merely a fresh login.
    assert not case_world.active_writers
    assert callable(getattr(engine.pool, "checkedout", None)), "reviewed pool must expose checked-out count"
    assert engine.pool.checkedout() == 0
    engine.dispose()
    with engine.connect() as connection:
        transaction = _begin(connection, case_world.runtime, case_world.p)
        previous_pid = connection.execute(text("SELECT pg_backend_pid()")).scalar_one()
        assert connection.execute(text("SELECT id FROM public.appointments WHERE id = :id"), {"id": p_row["id"]}).scalar_one() == p_row["id"]
        if completion == "commit":
            transaction.commit()
        else:
            transaction.rollback()
    with engine.connect() as connection:
        with _begin(connection, case_world.runtime):
            assert connection.execute(text("SELECT pg_backend_pid()")).scalar_one() == previous_pid, "pool schedule did not reuse the same backend"
            assert connection.execute(text("SELECT current_setting('app.current_practice_id', true)")).scalar_one() in (None, "")
            assert connection.execute(text("SELECT id FROM public.appointments WHERE id IN (:p,:q)"), {"p": p_row["id"], "q": q_row["id"]}).all() == []
            _bind_practice(connection, case_world.q)
            assert connection.execute(text("SELECT id FROM public.appointments WHERE id = :id"), {"id": p_row["id"]}).all() == []
            assert connection.execute(text("SELECT id FROM public.appointments WHERE id = :id"), {"id": q_row["id"]}).scalar_one() == q_row["id"]


@pytest.mark.parametrize("context", [pytest.param("missing", id="APT-T3-db-missing-context-write"), pytest.param("wrong", id="APT-T3-db-wrong-context-write")])
def test_apt_t3_database_rejects_missing_or_wrong_tenant_write(case_world, context):
    baseline = case_world.row("t3-baseline", location_id=case_world.l1)
    _insert_and_commit(case_world, baseline)
    assert _read(case_world, case_world.p, baseline["id"])["id"] == baseline["id"]
    before_p, before_q = case_world.snapshot(), case_world.snapshot(case_world.q)
    with case_world.writer(case_world.q) as writer:
        if context == "missing":
            writer.connection.execute(text("SELECT set_config('app.current_practice_id', '', true)"))
        assert writer.get(baseline["id"]) is None
        invalid = case_world.row("t3-unbound-write", practitioner_id=case_world.r2)
        with pytest.raises(DBAPIError) as raised:
            writer.insert(invalid)
        assert (getattr(raised.value.orig, "sqlstate", None) or getattr(raised.value.orig, "pgcode", None)) == "42501"
        writer.rollback()
    assert case_world.snapshot() == before_p
    assert case_world.snapshot(case_world.q) == before_q


def _direct_receipt(connection, world, practice, label, target_id, audit_id=None):
    receipt_id = uuid5(world.namespace, "receipt/" + label)
    connection.execute(text("""
        INSERT INTO public.appointment_command_idempotency
          (id,practice_id,actor_user_id,actor_role,operation_id,route_family,
           idempotency_key_hash,request_body_hash,request_body_canonicalization_version,
           state,target_appointment_id,audit_log_id)
        VALUES (:id,:practice,:actor,'Receptionist','synthetic-link-check','synthetic',
                :key_hash,:body_hash,1,'in_progress',:target,:audit)
    """), {"id": receipt_id, "practice": practice, "actor": str(world.actor if practice == world.p else world.actor_q), "key_hash": str(receipt_id), "body_hash": str(receipt_id), "target": target_id, "audit": audit_id})
    return receipt_id


def _direct_audit(connection, world, practice, label, target_id, command_id=None):
    audit_id = uuid5(world.namespace, "audit/" + label)
    connection.execute(text("""
        INSERT INTO public.appointment_audit_log
          (id,practice_id,appointment_id,confirmed_by_user_id,action,status_after,command_id)
        VALUES (:id,:practice,:target,:actor,'create','Booked',:command)
    """), {"id": audit_id, "practice": practice, "target": target_id, "actor": world.actor if practice == world.p else world.actor_q, "command": command_id})
    return audit_id


@pytest.mark.parametrize("link,constraint", [
    pytest.param("audit-target", "fk_appt_audit_log_practice_appointment", id="APT-T3-db-audit-target-composite"),
    pytest.param("receipt-target", "fk_appt_cmd_idem_practice_target", id="APT-T3-db-receipt-target-composite"),
    pytest.param("audit-command", "fk_appt_audit_log_practice_command", id="APT-T3-db-audit-command-composite"),
    pytest.param("receipt-audit", "fk_appt_cmd_idem_practice_audit", id="APT-T3-db-receipt-audit-composite"),
])
def test_apt_t3_composite_evidence_links_preserve_tenant_binding(case_world, link, constraint):
    p_row = case_world.row("t3-links-p")
    q_row = case_world.row("t3-links-q", practice_id=case_world.q, practitioner_id=case_world.rq)
    _insert_and_commit(case_world, p_row)
    _insert_and_commit(case_world, q_row)
    before_p, before_q = case_world.snapshot(), case_world.snapshot(case_world.q)
    # Every FK-negative has a positive same-tenant control, rolled back so no
    # immutable audit evidence needs deletion. These are DB-link tests only.
    with case_world.writer() as writer:
        command = _direct_receipt(writer.connection, case_world, case_world.p, "positive-command", p_row["id"])
        audit = _direct_audit(writer.connection, case_world, case_world.p, "positive-audit", p_row["id"], command)
        _direct_receipt(writer.connection, case_world, case_world.p, "positive-receipt", p_row["id"], audit)
        writer.rollback()
    assert case_world.snapshot() == before_p
    with case_world.writer() as writer:
        foreign_reference = None
        if link in ("audit-command", "receipt-audit"):
            _bind_practice(writer.connection, case_world.q)
            if link == "audit-command":
                foreign_reference = _direct_receipt(writer.connection, case_world, case_world.q, "q-command", q_row["id"])
            else:
                foreign_reference = _direct_audit(writer.connection, case_world, case_world.q, "q-audit", q_row["id"])
            _bind_practice(writer.connection, case_world.p)
        with pytest.raises(DBAPIError) as raised:
            if link == "audit-target":
                _direct_audit(writer.connection, case_world, case_world.p, "wrong-target", q_row["id"])
            elif link == "receipt-target":
                _direct_receipt(writer.connection, case_world, case_world.p, "wrong-target", q_row["id"])
            elif link == "audit-command":
                _direct_audit(writer.connection, case_world, case_world.p, "wrong-command", p_row["id"], foreign_reference)
            else:
                _direct_receipt(writer.connection, case_world, case_world.p, "wrong-audit", p_row["id"], foreign_reference)
        original = raised.value.orig
        assert (getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)) == "23503"
        assert original.diag.constraint_name == constraint
        writer.rollback()
    assert case_world.snapshot() == before_p
    assert case_world.snapshot(case_world.q) == before_q


@pytest.mark.parametrize("offset_hours", [pytest.param(10, id="APT-INPUT-INSTANT-db-equivalent-plus10"), pytest.param(-5, id="APT-INPUT-INSTANT-db-equivalent-minus5")])
def test_apt_input_instant_database_compares_instants_not_wall_clock(case_world, offset_hours):
    first = case_world.row("instant-first", location_id=case_world.l1)
    other_encoding = case_world.start.astimezone(timezone(timedelta(hours=offset_hours)))
    second = case_world.row("instant-second", location_id=None, start=other_encoding)
    _insert_and_commit(case_world, first)
    before = case_world.snapshot()
    with case_world.writer() as writer:
        case_world.assert_collision(writer, lambda: writer.insert(second))
        writer.rollback()
    assert case_world.snapshot() == before


@pytest.mark.parametrize("field,value,sqlstate,diagnostic", [
    pytest.param("duration_minutes", 0, "23514", "ck_appointments_duration_minutes_1_480", id="APT-INPUT-OVERFLOW-db-zero"),
    pytest.param("duration_minutes", 481, "23514", "ck_appointments_duration_minutes_1_480", id="APT-INPUT-OVERFLOW-db-481"),
    pytest.param("duration_minutes", None, "23502", "duration_minutes", id="APT-INPUT-NULL-db-duration"),
    pytest.param("status", None, "23502", "status", id="APT-INPUT-NULL-db-status"),
    pytest.param("start_time", "infinity", "23514", {"ck_appointments_start_time_finite", "ck_appointments_end_time_finite"}, id="APT-INPUT-OVERFLOW-db-positive-infinity"),
    pytest.param("start_time", "-infinity", "23514", {"ck_appointments_start_time_finite", "ck_appointments_end_time_finite"}, id="APT-INPUT-OVERFLOW-db-negative-infinity"),
])
def test_apt_input_database_interval_guards_have_targeted_rejections(case_world, field, value, sqlstate, diagnostic):
    baseline = case_world.row("input-baseline")
    _insert_and_commit(case_world, baseline)
    assert _read(case_world, case_world.p, baseline["id"])["id"] == baseline["id"]
    before = case_world.snapshot()
    invalid = case_world.row("input-invalid", practitioner_id=case_world.r2)
    invalid[field] = value
    with case_world.writer() as writer:
        with pytest.raises(DBAPIError) as raised:
            writer.insert(invalid)
        writer.rollback()
        assert not writer.connection.in_transaction()
        original = raised.value.orig
        assert (getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)) == sqlstate
        name = original.diag.column_name if sqlstate == "23502" else original.diag.constraint_name
        expected = diagnostic if isinstance(diagnostic, set) else {diagnostic}
        assert name in expected
    assert case_world.snapshot() == before


import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_db
from app.models.tenancy import UserRole
from app.routers.appointments import router as appointment_router
from app.schemas.appointments import AppointmentCreate, AppointmentUpdate
from app.services.auth_service import create_access_token


EXPECTED_APPOINTMENT_RUNTIME_KEYS = frozenset(
    {
        "engine",
        "observer_engine",
        "admin_engine",
        "database_name",
        "application_role",
        "expected_revision",
        "wait_timeout_seconds",
        "test_deadline_seconds",
    }
)

SCHEMA_PRACTITIONER_ID = uuid.UUID("d06c07ae-2f1e-5d32-92e8-3efb38c6cc10")
SCHEMA_START = datetime(2027, 2, 3, 9, 15, tzinfo=timezone.utc)


def _local_time(instant):
    return instant.timetz().replace(tzinfo=None)


def _parse_api_datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _utc(instant):
    return instant.astimezone(timezone.utc)


def _create_schema_payload(**changes):
    payload = {
        "patient_name_provisional": "Synthetic Input Patient",
        "practitioner_id": SCHEMA_PRACTITIONER_ID,
        "start_time": SCHEMA_START,
        "duration_minutes": 30,
    }
    payload.update(changes)
    return payload


@pytest.fixture
def appointment_http_client(appointment_runtime, case_world, monkeypatch):
    """Real ASGI/router/auth path with only database dependencies substituted."""
    assert frozenset(appointment_runtime) == EXPECTED_APPOINTMENT_RUNTIME_KEYS
    assert appointment_runtime["expected_revision"] == "y4z5a6b7c8d9"
    assert appointment_runtime["database_name"]
    assert appointment_runtime["application_role"]
    assert appointment_runtime["wait_timeout_seconds"] > 0
    assert appointment_runtime["test_deadline_seconds"] > 0

    request_sessions = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=True,
        bind=appointment_runtime["engine"],
    )

    def bound_get_db():
        db = request_sessions()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(appointment_router)
    app.dependency_overrides[get_db] = bound_get_db
    assert frozenset(app.dependency_overrides) == frozenset(
        {get_db}
    )

    # Password login alone is outside this isolated surface.  The token is
    # nevertheless minted and verified by the real auth service, and the real
    # get_current_user/require_role dependencies must find the active seeded
    # Receptionist row before either route can execute.
    token = create_access_token(
        {
            "sub": str(case_world.actor),
            "practice_id": str(case_world.p),
            "role": UserRole.Receptionist.value,
        }
    )
    headers = {"Authorization": f"Bearer {token}"}

    try:
        with monkeypatch.context() as clinic_clock:
            # Fix only clinic calendar time; token/signature clocks stay real.
            clinic_clock.setattr(appointment_routes, "_clinic_local_now",
                lambda practice_tz: datetime(2027, 1, 1, 12, tzinfo=timezone.utc).astimezone(practice_tz))
            with TestClient(app, raise_server_exceptions=True) as client:
                yield client, headers
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "_apt_input_case",
    [pytest.param(None, id="APT-INPUT-LOCAL-schema-complete-pair")],
)
def test_apt_input_local_schema_accepts_complete_local_pair(
    _apt_input_case,
):
    local = AppointmentCreate.model_validate(
        {
            "patient_name_provisional": "Synthetic Local Patient",
            "practitioner_id": SCHEMA_PRACTITIONER_ID,
            "appointment_date": SCHEMA_START.date().isoformat(),
            "start_time_local": _local_time(SCHEMA_START).isoformat(),
            "duration_minutes": 30,
        }
    )

    assert local.start_time is None
    assert local.appointment_date == SCHEMA_START.date()
    assert local.start_time_local == _local_time(SCHEMA_START)
    assert {"appointment_date", "start_time_local"} <= local.model_fields_set


INSTANT_SCHEMA_CASES = [
    pytest.param(
        "equivalent-offset",
        id="APT-INPUT-INSTANT-schema-equivalent-offset",
    ),
    pytest.param(
        "sydney-second-fold-explicit-offset",
        id="APT-INPUT-INSTANT-schema-second-fold-explicit-offset",
    ),
]


@pytest.mark.parametrize("instant_case", INSTANT_SCHEMA_CASES)
def test_apt_input_instant_schema_preserves_explicit_absolute_instant(
    instant_case,
):
    if instant_case == "equivalent-offset":
        expected = SCHEMA_START
        encoded = expected.astimezone(timezone(timedelta(hours=9, minutes=30))).isoformat()
    else:
        # This explicit +10:00 instant is the second 02:30 occurrence in
        # Australia/Sydney on 2027-04-04.  No local-time ambiguity inference is
        # requested from the schema; the offset makes the instant unambiguous.
        encoded = "2027-04-04T02:30:00+10:00"
        expected = datetime.fromisoformat(encoded)

    direct = AppointmentCreate.model_validate(
        {
            "patient_name_provisional": "Synthetic Instant Patient",
            "practitioner_id": SCHEMA_PRACTITIONER_ID,
            "start_time": encoded,
            "duration_minutes": 30,
        }
    )

    assert direct.start_time is not None
    assert _utc(direct.start_time) == _utc(expected)
    assert direct.appointment_date is None
    assert direct.start_time_local is None


EXPLICIT_NULL_UPDATE_CASES = [
    pytest.param("practitioner_id", id="APT-INPUT-NULL-schema-update-practitioner"),
    pytest.param("start_time", id="APT-INPUT-NULL-schema-update-start-time"),
    pytest.param("appointment_date", id="APT-INPUT-NULL-schema-update-date"),
    pytest.param("start_time_local", id="APT-INPUT-NULL-schema-update-local-time"),
    pytest.param("duration_minutes", id="APT-INPUT-NULL-schema-update-duration"),
]


@pytest.mark.parametrize("field", EXPLICIT_NULL_UPDATE_CASES)
def test_apt_input_null_schema_rejects_explicit_null_for_required_update_fields(field):
    with pytest.raises(ValidationError):
        AppointmentUpdate.model_validate({field: None})


OVERFLOW_SCHEMA_CASES = [
    pytest.param("create", 0, id="APT-INPUT-OVERFLOW-schema-create-zero"),
    pytest.param("create", 481, id="APT-INPUT-OVERFLOW-schema-create-481"),
    pytest.param("update", 0, id="APT-INPUT-OVERFLOW-schema-update-zero"),
    pytest.param("update", 481, id="APT-INPUT-OVERFLOW-schema-update-481"),
]


@pytest.mark.parametrize("schema_case,duration", OVERFLOW_SCHEMA_CASES)
def test_apt_input_overflow_schema_rejects_out_of_range_duration(
    schema_case, duration
):
    payload = {"duration_minutes": duration}
    model = AppointmentUpdate
    if schema_case == "create":
        payload = _create_schema_payload(duration_minutes=duration)
        model = AppointmentCreate

    with pytest.raises(ValidationError):
        model.model_validate(payload)


@pytest.mark.parametrize(
    "_apt_input_case",
    [pytest.param(None, id="APT-INPUT-OMITTED-schema-update-preserves-absence")],
)
def test_apt_input_omitted_schema_keeps_temporal_fields_unset(_apt_input_case):
    update = AppointmentUpdate.model_validate({"reason": "Synthetic reason-only edit"})

    assert update.model_dump(exclude_unset=True) == {
        "reason": "Synthetic reason-only edit"
    }
    assert not {
        "practitioner_id",
        "start_time",
        "appointment_date",
        "start_time_local",
        "duration_minutes",
    } & update.model_fields_set


@pytest.mark.parametrize(
    "_apt_input_case",
    [pytest.param(None, id="APT-INPUT-LOCATION-CLEAR-schema-explicit-null")],
)
def test_apt_input_location_clear_schema_preserves_explicit_null(
    _apt_input_case,
):
    update = AppointmentUpdate.model_validate({"location_id": None})

    assert "location_id" in update.model_fields_set
    assert update.model_dump(exclude_unset=True) == {"location_id": None}


HTTP_CREATE_INSTANT_CASES = [
    pytest.param(
        "case-world-equivalent-offset",
        id="APT-INPUT-INSTANT-http-raw-create-equivalent-offset",
    ),
    pytest.param(
        "sydney-second-fold-explicit-offset",
        id="APT-INPUT-INSTANT-http-raw-create-second-fold-explicit-offset",
    ),
]


@pytest.mark.parametrize("instant_case", HTTP_CREATE_INSTANT_CASES)
def test_apt_input_instant_http_raw_create_preserves_stored_absolute_instant(
    appointment_http_client, case_world, instant_case
):
    client, headers = appointment_http_client
    if instant_case == "case-world-equivalent-offset":
        expected = case_world.start
        encoded = expected.astimezone(timezone(timedelta(hours=9, minutes=30))).isoformat()
    else:
        case_world.set_timezone("Australia/Sydney")
        encoded = "2027-04-04T02:30:00+10:00"
        expected = datetime.fromisoformat(encoded)
        assert expected.astimezone(ZoneInfo("Australia/Sydney")).fold == 1

    response = client.post(
        "/api/v1/appointments",
        headers=headers,
        json={
            "patient_name_provisional": "Synthetic HTTP Create Patient",
            "practitioner_id": str(case_world.r),
            "location_id": str(case_world.l1),
            "start_time": encoded,
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["practitioner_id"] == str(case_world.r)
    assert body["location_id"] == str(case_world.l1)
    assert body["duration_minutes"] == 30
    assert _utc(_parse_api_datetime(body["start_time"])) == _utc(expected)

    with case_world.writer() as reader:
        stored = reader.get(uuid.UUID(body["id"]))
    assert stored is not None
    assert _utc(stored["start_time"]) == _utc(expected)


@pytest.mark.parametrize(
    "_apt_input_case",
    [pytest.param(None, id="APT-INPUT-OMITTED-http-raw-update-preserves-instant")],
)
def test_apt_input_omitted_http_reason_and_duration_updates_preserve_instant(
    appointment_http_client, case_world, _apt_input_case
):
    client, headers = appointment_http_client
    case_world.set_timezone("Australia/Sydney")
    encoded = "2027-04-04T02:30:00+10:00"
    expected = datetime.fromisoformat(encoded)
    created = client.post(
        "/api/v1/appointments",
        headers=headers,
        json={
            "patient_name_provisional": "Synthetic HTTP Update Patient",
            "practitioner_id": str(case_world.r),
            "location_id": str(case_world.l1),
            "start_time": encoded,
            "duration_minutes": 30,
        },
    )
    assert created.status_code == 201
    appointment_id = created.json()["id"]

    reason_only = client.put(
        f"/api/v1/appointments/{appointment_id}",
        headers=headers,
        json={"reason": "Synthetic reason-only edit"},
    )
    assert reason_only.status_code == 200
    assert reason_only.json()["reason"] == "Synthetic reason-only edit"
    assert _utc(_parse_api_datetime(reason_only.json()["start_time"])) == _utc(expected)

    duration_only = client.put(
        f"/api/v1/appointments/{appointment_id}",
        headers=headers,
        json={"duration_minutes": 45},
    )
    assert duration_only.status_code == 200
    assert duration_only.json()["duration_minutes"] == 45
    assert _utc(_parse_api_datetime(duration_only.json()["start_time"])) == _utc(expected)

    with case_world.writer() as reader:
        stored = reader.get(uuid.UUID(appointment_id))
    assert stored is not None
    assert stored["duration_minutes"] == 45
    assert _utc(stored["start_time"]) == _utc(expected)


@pytest.mark.parametrize("active", [pytest.param(False, id="APT-S9-db-unused-site-inactive"), pytest.param(True, id="APT-S9-db-unused-site-active")])
def test_apt_s9_unused_site_count_does_not_change_collision(case_world, active):
    incumbent = case_world.row("site-count-incumbent", location_id=None)
    _insert_and_commit(case_world, incumbent)
    # Change only this case's fixture site. Appointments still use the actual
    # application-role writer and the already installed database constraint.
    with case_world.runtime.admin_engine.begin() as connection:
        changed = connection.execute(text("UPDATE public.practice_locations SET is_active = :active WHERE id = :site AND practice_id = :practice"), {"active": active, "site": case_world.l2, "practice": case_world.p})
        assert changed.rowcount == 1
    before = case_world.snapshot()
    contender = case_world.row("site-count-contender", location_id=case_world.l1)
    with case_world.writer() as writer:
        case_world.assert_collision(writer, lambda: writer.insert(contender))
    assert case_world.snapshot() == before


@pytest.mark.parametrize("_case", [pytest.param(None, id="APT-INPUT-INSTANT-db-distinct-fold-instants")])
def test_apt_input_database_distinguishes_equal_local_clock_at_distinct_instants(case_world, _case):
    case_world.set_timezone("Australia/Sydney")
    zone = ZoneInfo("Australia/Sydney")
    first_start = datetime.fromisoformat("2027-04-04T02:15:00+11:00")
    second_start = datetime.fromisoformat("2027-04-04T02:15:00+10:00")
    assert first_start.astimezone(zone).fold == 0
    assert second_start.astimezone(zone).fold == 1
    first = case_world.row("fold-first", location_id=None, start=first_start, minutes=30)
    second = case_world.row("fold-second", location_id=case_world.l1, start=second_start, minutes=30)
    assert first["appointment_date"] == second["appointment_date"]
    assert first["start_time_local"] == second["start_time_local"]
    assert first_start.astimezone(timezone.utc) + timedelta(minutes=30) < second_start.astimezone(timezone.utc)
    _insert_and_commit(case_world, first)
    _insert_and_commit(case_world, second)
    assert _read(case_world, case_world.p, first["id"])["start_time"] == first_start
    assert _read(case_world, case_world.p, second["id"])["start_time"] == second_start


# Create-family confirmation and real-auth negative cases.
from copy import deepcopy
from datetime import datetime, timezone
import uuid

import pytest


CREATE_PROPOSAL_ENDPOINT = "/api/v1/appointments/proposals/create"
CREATE_CONFIRM_ENDPOINT = "/api/v1/appointments/proposals/create/confirm"
RAW_CREATE_ENDPOINT = "/api/v1/appointments"

STAFF_CREATE_AUDIT_EVIDENCE = [
    "staff_confirm_create_proposal",
    "source_create_proposal",
    "staff_signed_confirmation_evidence_verified",
]


def _confirmation_key_headers(headers, key):
    return {**headers, "Idempotency-Key": key}


def _confirmation_datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _confirmation_utc(value):
    return value.astimezone(timezone.utc)


def _staff_create_proposal(
    client,
    headers,
    case_world,
    *,
    start,
    location_id,
    proposal_key,
    patient_label,
    minutes=30,
):
    encoded_start = start if isinstance(start, str) else start.isoformat()
    response = client.post(
        CREATE_PROPOSAL_ENDPOINT,
        headers=_confirmation_key_headers(headers, proposal_key),
        json={
            "patient_name_provisional": patient_label,
            "practitioner_id": str(case_world.r),
            "location_id": None if location_id is None else str(location_id),
            "start_time": encoded_start,
            "duration_minutes": minutes,
        },
    )

    assert response.status_code == 200
    proposal = response.json()
    assert proposal["intent"] == "create_appointment"
    assert proposal["safe"] is True
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "proposal"
    assert proposal["blocks"] == []
    assert proposal["conflict"] is None
    assert proposal["patient_identity"] == "provisional"
    assert proposal["confirm_endpoint"] == CREATE_CONFIRM_ENDPOINT
    assert proposal["create_proposal_freshness_id"]
    assert proposal["signed_confirmation_evidence_required"] is True
    assert proposal["signed_confirmation_evidence"]
    assert proposal["signed_confirmation_evidence"]["purpose"] == (
        "staff_confirm_create_proposal"
    )

    confirm_payload = proposal["confirm_payload"]
    assert confirm_payload is not None
    assert confirm_payload["confirmed"] is False
    assert confirm_payload["create_proposal"]["intent"] == "create_appointment"
    assert confirm_payload["create_proposal"]["command"] == proposal["command"]
    assert confirm_payload["create_proposal_freshness_id"] == (
        proposal["create_proposal_freshness_id"]
    )
    assert confirm_payload["signed_confirmation_evidence"] == (
        proposal["signed_confirmation_evidence"]
    )
    assert confirm_payload["signed_confirmation_evidence_required"] is True
    return proposal, deepcopy(confirm_payload)


def _confirm_create(client, headers, endpoint, key, body):
    return client.post(
        endpoint,
        headers=_confirmation_key_headers(headers, key),
        json=body,
    )


def _assert_blocked_create_confirmation(body):
    assert body["intent"] == "confirm_create_appointment"
    assert body["safe"] is False
    assert body["requires_confirmation"] is True
    assert body["autonomy_tier"] == "blocked"
    assert body["summary"] == "Cannot confirm create proposal. See blocked issues."
    assert body["appointment"] is None
    assert body["confirmation_receipt"] is None
    assert all(block["severity"] == "blocked" for block in body["blocks"])


def _assert_confirmed_create_confirmation(body, expected_start):
    assert body["intent"] == "confirm_create_appointment"
    assert body["safe"] is True
    assert body["requires_confirmation"] is False
    assert body["autonomy_tier"] == "confirmed_write"
    assert body["summary"] == "Confirmed create proposal and created one appointment."
    assert body["blocks"] == []
    assert body["audit_evidence"] == STAFF_CREATE_AUDIT_EVIDENCE

    appointment = body["appointment"]
    receipt = body["confirmation_receipt"]
    assert appointment is not None
    assert receipt is not None
    assert _confirmation_utc(_confirmation_datetime(appointment["start_time"])) == (
        _confirmation_utc(expected_start)
    )
    assert receipt["schema_version"] == "appointment.confirmation_receipt.v1"
    assert receipt["outcome"] == "appointment_created"
    assert receipt["appointment_id"] == appointment["id"]
    assert receipt["appointment_date"] == appointment["appointment_date"]
    assert receipt["start_time_local"] == appointment["start_time_local"]
    assert receipt["duration_minutes"] == appointment["duration_minutes"]
    assert receipt["status"] == "Booked"
    assert receipt["confirmed_by_role"] == "Receptionist"
    assert receipt["correlation_id"]
    assert receipt["audit_event_id"]
    assert receipt["session_id"] is None
    assert receipt["verification"] == {
        "actor_authenticated": True,
        "practice_scope_verified": True,
        "proposal_revalidated": True,
        "conflict_check_passed": True,
        "idempotency_verified": True,
        "audit_recorded": True,
        "signed_evidence_verified": True,
        "visual_diary_check_required": False,
    }


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-S10-http-create-stale-proposal-conflict")],
)
def test_apt_s10_confirmation_revalidates_after_competing_booking(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    before_proposal = case_world.snapshot()
    proposal, confirmation = _staff_create_proposal(
        client,
        headers,
        case_world,
        start=case_world.start,
        location_id=case_world.l1,
        proposal_key="apt-s10-proposal",
        patient_label="Synthetic S10 Proposed Patient",
    )
    assert case_world.snapshot() == before_proposal

    winner = client.post(
        RAW_CREATE_ENDPOINT,
        headers=headers,
        json={
            "patient_name_provisional": "Synthetic S10 Winning Patient",
            "practitioner_id": str(case_world.r),
            "location_id": str(case_world.l2),
            "start_time": case_world.start.isoformat(),
            "duration_minutes": 30,
        },
    )
    assert winner.status_code == 201
    winner_id = winner.json()["id"]
    after_winner = case_world.snapshot()

    confirmation["confirmed"] = True
    rejected = _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        "apt-s10-confirm",
        confirmation,
    )
    assert rejected.status_code == 200
    blocked = rejected.json()
    _assert_blocked_create_confirmation(blocked)
    assert [item["code"] for item in blocked["blocks"]] == [
        "appointment_conflict", "create_proposal_revalidation_blocked",
    ]
    assert {
        "code": "appointment_conflict",
        "severity": "blocked",
        "message": "This appointment overlaps an existing booking.",
    } in blocked["blocks"]
    assert blocked["audit_evidence"] == STAFF_CREATE_AUDIT_EVIDENCE

    # The blocked confirmation rolls back its provisional idempotency claim.
    # The committed raw winner and its audit remain the only new effects.
    assert case_world.snapshot() == after_winner
    with case_world.writer() as reader:
        assert reader.get(uuid.UUID(winner_id)) is not None


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-R6-http-create-confirm-replay-and-key-conflict")],
)
def test_apt_r6_confirm_create_replay_is_one_logical_effect(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    case_world.set_timezone("Australia/Sydney")
    second_fold = datetime.fromisoformat("2027-04-04T02:30:00+10:00")
    assert second_fold.astimezone(ZoneInfo("Australia/Sydney")).fold == 1
    before_proposal = case_world.snapshot()
    proposal, confirmation = _staff_create_proposal(
        client,
        headers,
        case_world,
        start=second_fold,
        location_id=case_world.l1,
        proposal_key="apt-r6-proposal",
        patient_label="Synthetic R6 Replay Patient",
    )
    assert case_world.snapshot() == before_proposal

    confirmation["confirmed"] = True
    confirmation_key = "apt-r6-confirm"
    first = _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        confirmation_key,
        confirmation,
    )
    assert first.status_code == 200
    first_body = first.json()
    _assert_confirmed_create_confirmation(first_body, second_fold)
    first_snapshot = case_world.snapshot()
    appointments = json.loads(first_snapshot["appointments"])
    audits = json.loads(first_snapshot["appointment_audit_log"])
    receipts = json.loads(first_snapshot["appointment_command_idempotency"])
    assert len(appointments) == len(audits) == len(receipts) == 1
    assert audits[0]["appointment_id"] == appointments[0]["id"]
    assert audits[0]["command_id"] == receipts[0]["id"]
    assert receipts[0]["audit_log_id"] == audits[0]["id"]
    assert receipts[0]["state"] == "completed"
    assert receipts[0]["result_kind"] == "confirmed_write"

    replay = _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        confirmation_key,
        confirmation,
    )
    assert replay.status_code == 200
    assert replay.json() == first_body
    assert case_world.snapshot() == first_snapshot

    changed_confirmation = deepcopy(confirmation)
    changed_confirmation["confirmed_warnings"] = [
        *changed_confirmation["confirmed_warnings"],
        "synthetic_changed_body",
    ]
    changed = _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        confirmation_key,
        changed_confirmation,
    )
    assert changed.status_code == 409
    assert changed.json() == {
        "detail": {
            "code": "idempotency_key_conflict",
            "message": (
                "Idempotency-Key was already used with a different "
                "confirmation payload."
            ),
        }
    }
    assert case_world.snapshot() == first_snapshot

    appointment_id = first_body["appointment"]["id"]
    with case_world.writer() as reader:
        stored = reader.get(uuid.UUID(appointment_id))
        matching_rows = [
            row for row in reader.all_rows() if str(row["id"]) == appointment_id
        ]
    assert stored is not None
    assert len(matching_rows) == 1
    assert _confirmation_utc(stored["start_time"]) == _confirmation_utc(second_fold)


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-T4-http-create-revoked-active-user")],
)
def test_apt_t4_create_confirmation_rechecks_active_actor(
    appointment_http_client, appointment_runtime, case_world, _appointment_case
):
    client, headers = appointment_http_client
    before_proposal = case_world.snapshot()
    proposal, confirmation = _staff_create_proposal(
        client,
        headers,
        case_world,
        start=case_world.start,
        location_id=None,
        proposal_key="apt-t4-revoked-proposal",
        patient_label="Synthetic T4 Revoked Actor Patient",
    )
    assert case_world.snapshot() == before_proposal

    # Administrative fixture control changes only the synthetic actor's source
    # state.  The confirmation still has to fail through the real application
    # role, signed token, get_current_user lookup, and require_role dependency.
    case_world.set_actor_active(False)

    confirmation["confirmed"] = True
    denied = _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        "apt-t4-revoked-confirm",
        confirmation,
    )
    assert denied.status_code == 401
    assert denied.json() == {"detail": "User not found or inactive"}
    assert case_world.snapshot() == before_proposal


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-T4-http-create-explicit-confirmation-and-valid-control")],
)
def test_apt_t4_create_confirmation_requires_explicit_true_then_valid_path_succeeds(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    before_proposal = case_world.snapshot()
    proposal, confirmation = _staff_create_proposal(
        client,
        headers,
        case_world,
        start=case_world.start,
        location_id=case_world.l2,
        proposal_key="apt-t4-explicit-proposal",
        patient_label="Synthetic T4 Explicit Confirmation Patient",
    )
    assert case_world.snapshot() == before_proposal

    # The actual proposal endpoint deliberately returns confirmed=false.
    confirmation_key = "apt-t4-explicit-confirm"
    blocked_response = _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        confirmation_key,
        confirmation,
    )
    assert blocked_response.status_code == 200
    blocked = blocked_response.json()
    _assert_blocked_create_confirmation(blocked)
    assert blocked["blocks"] == [
        {
            "code": "explicit_confirmation_required",
            "severity": "blocked",
            "message": "confirmed=true is required before creating an appointment.",
        }
    ]
    assert blocked["audit_evidence"] == STAFF_CREATE_AUDIT_EVIDENCE
    assert case_world.snapshot() == before_proposal

    # Blocked responses are not completed receipts: the claim was rolled back,
    # so the same key can authorize this changed, now-explicit confirmation.
    confirmation["confirmed"] = True
    succeeded = _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        confirmation_key,
        confirmation,
    )
    assert succeeded.status_code == 200
    _assert_confirmed_create_confirmation(succeeded.json(), case_world.start)
    assert case_world.snapshot() != before_proposal


RAW_APPOINTMENTS_ENDPOINT = "/api/v1/appointments"
RAW_CONFLICT_CODE = "appointment_conflict"
RAW_CONFLICT_MESSAGE = "Appointment conflicts with an existing booking"
RAW_CONFLICT_REQUIRED_FIELDS = {"code", "message"}
RAW_CONFLICT_WINNER_FIELDS = {
    "conflicting_appointment_id",
    "conflicting_start_time",
    "conflicting_end_time",
}


def _raw_site(case_world, name):
    if name == "none":
        return None
    return getattr(case_world, name)


def _raw_parse_datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _raw_utc(value):
    return value.astimezone(timezone.utc)


def _raw_create_success(
    client,
    headers,
    case_world,
    *,
    patient_label,
    start,
    minutes,
    location_id,
    practitioner_id=None,
):
    practitioner_id = practitioner_id or case_world.r
    response = client.post(
        RAW_APPOINTMENTS_ENDPOINT,
        headers=headers,
        json={
            "patient_name_provisional": patient_label,
            "practitioner_id": str(practitioner_id),
            "location_id": None if location_id is None else str(location_id),
            "start_time": start.isoformat(),
            "duration_minutes": minutes,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["practitioner_id"] == str(practitioner_id)
    assert body["location_id"] == (
        None if location_id is None else str(location_id)
    )
    assert body["duration_minutes"] == minutes
    assert body["status"] == "Booked"
    assert _raw_utc(_raw_parse_datetime(body["start_time"])) == _raw_utc(start)
    with case_world.writer() as reader:
        stored = reader.get(uuid.UUID(body["id"]))
    assert stored is not None
    assert _raw_utc(stored["start_time"]) == _raw_utc(start)
    return body


def _assert_raw_collision(response, winner):
    assert response.status_code == 409
    payload = response.json()
    assert set(payload) == {"detail"}
    detail = payload["detail"]
    assert detail["code"] == RAW_CONFLICT_CODE
    assert detail["message"] == RAW_CONFLICT_MESSAGE
    assert RAW_CONFLICT_REQUIRED_FIELDS <= set(detail)
    assert set(detail) <= RAW_CONFLICT_REQUIRED_FIELDS | RAW_CONFLICT_WINNER_FIELDS

    winner_fields = set(detail) & RAW_CONFLICT_WINNER_FIELDS
    assert not winner_fields or winner_fields == RAW_CONFLICT_WINNER_FIELDS
    if winner_fields:
        winner_start = _raw_parse_datetime(winner["start_time"])
        winner_end = winner_start + timedelta(minutes=winner["duration_minutes"])
        assert detail["conflicting_appointment_id"] == winner["id"]
        assert _raw_utc(_raw_parse_datetime(detail["conflicting_start_time"])) == (
            _raw_utc(winner_start)
        )
        assert _raw_utc(_raw_parse_datetime(detail["conflicting_end_time"])) == (
            _raw_utc(winner_end)
        )

    rendered = response.text.lower()
    for forbidden in (
        "23p01",
        "ex_appointments_practice_practitioner_no_overlap",
        "sqlstate",
        "integrityerror",
        "postgresql",
    ):
        assert forbidden not in rendered


RAW_CREATE_SITE_CASES = [
    pytest.param("l1", "none", id="APT-S1-http-raw-create-l1-v-null"),
    pytest.param("none", "l2", id="APT-S1-http-raw-create-null-v-l2"),
]


@pytest.mark.parametrize("winner_site,loser_site", RAW_CREATE_SITE_CASES)
def test_raw_create_collision_is_409_and_atomic_across_locations(
    appointment_http_client, case_world, winner_site, loser_site
):
    client, headers = appointment_http_client
    winner = _raw_create_success(
        client,
        headers,
        case_world,
        patient_label="Synthetic Raw Create Winner",
        start=case_world.start,
        minutes=30,
        location_id=_raw_site(case_world, winner_site),
    )
    after_winner = case_world.snapshot()

    loser = client.post(
        RAW_APPOINTMENTS_ENDPOINT,
        headers=headers,
        json={
            "patient_name_provisional": "Synthetic Raw Create Loser",
            "practitioner_id": str(case_world.r),
            "location_id": (
                None
                if _raw_site(case_world, loser_site) is None
                else str(_raw_site(case_world, loser_site))
            ),
            "start_time": (case_world.start + timedelta(minutes=15)).isoformat(),
            "duration_minutes": 30,
        },
    )

    _assert_raw_collision(loser, winner)
    assert case_world.snapshot() == after_winner


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-S6-http-raw-update-conflict")],
)
def test_raw_update_collision_is_409_and_preserves_target(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    winner = _raw_create_success(
        client,
        headers,
        case_world,
        patient_label="Synthetic Raw Update Winner",
        start=case_world.start,
        minutes=30,
        location_id=case_world.l1,
    )
    target = _raw_create_success(
        client,
        headers,
        case_world,
        patient_label="Synthetic Raw Update Target",
        start=case_world.start + timedelta(minutes=60),
        minutes=30,
        location_id=case_world.l2,
    )

    valid_update = client.put(
        f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}",
        headers=headers,
        json={"reason": "Synthetic valid raw update control"},
    )
    assert valid_update.status_code == 200
    assert valid_update.json()["reason"] == "Synthetic valid raw update control"
    with case_world.writer() as reader:
        target_before = reader.get(uuid.UUID(target["id"]))
    assert target_before is not None
    after_valid_update = case_world.snapshot()

    rejected = client.put(
        f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}",
        headers=headers,
        json={
            "start_time": (case_world.start + timedelta(minutes=15)).isoformat(),
            "location_id": None,
        },
    )

    _assert_raw_collision(rejected, winner)
    assert case_world.snapshot() == after_valid_update
    with case_world.writer() as reader:
        target_after = reader.get(uuid.UUID(target["id"]))
    assert target_after == target_before


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-S8-http-raw-status-reactivation-conflict")],
)
def test_raw_status_reactivation_collision_is_409_and_atomic(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    winner = _raw_create_success(
        client,
        headers,
        case_world,
        patient_label="Synthetic Raw Status Winner",
        start=case_world.start,
        minutes=30,
        location_id=case_world.l1,
    )
    target = case_world.row(
        "raw-status-reactivation-target",
        location_id=None,
        start=case_world.start,
        minutes=30,
        status="Cancelled",
    )
    with case_world.writer() as writer:
        writer.insert(target)
        writer.commit()

    valid_status = client.patch(
        f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}/status",
        headers=headers,
        json={"status": "NoShow"},
    )
    assert valid_status.status_code == 200
    assert valid_status.json()["status"] == "NoShow"
    with case_world.writer() as reader:
        target_before = reader.get(target["id"])
    assert target_before is not None
    assert target_before["status"] == "NoShow"
    after_valid_status = case_world.snapshot()

    rejected = client.patch(
        f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}/status",
        headers=headers,
        json={"status": "Booked"},
    )

    _assert_raw_collision(rejected, winner)
    assert case_world.snapshot() == after_valid_status
    with case_world.writer() as reader:
        target_after = reader.get(target["id"])
    assert target_after == target_before


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-T3-http-cross-tenant-related-location")],
)
def test_raw_create_rejects_cross_tenant_location_without_detail_leak(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    own_location_booking = _raw_create_success(
        client,
        headers,
        case_world,
        patient_label="Synthetic Own Location Control",
        start=case_world.start,
        minutes=30,
        location_id=case_world.l1,
    )
    assert own_location_booking["location_id"] == str(case_world.l1)
    p_after_control = case_world.snapshot(case_world.p)
    q_before_rejection = case_world.snapshot(case_world.q)

    rejected = client.post(
        RAW_APPOINTMENTS_ENDPOINT,
        headers=headers,
        json={
            "patient_name_provisional": "Synthetic Cross-Tenant Location Rejection",
            "practitioner_id": str(case_world.r),
            "location_id": str(case_world.lq),
            "start_time": (case_world.start + timedelta(minutes=60)).isoformat(),
            "duration_minutes": 30,
        },
    )

    assert rejected.status_code == 404
    assert rejected.json() == {"detail": "Practice location not found"}
    rendered = rejected.text
    assert str(case_world.q) not in rendered
    assert str(case_world.lq) not in rendered
    assert str(case_world.rq) not in rendered
    assert str(case_world.actor_q) not in rendered
    assert case_world.snapshot(case_world.p) == p_after_control
    assert case_world.snapshot(case_world.q) == q_before_rejection


from sqlalchemy import event
import re


class TenantSqlTrace:
    """Observe actual engine work without issuing SQL or changing authority.

    Only table names and context-match booleans are retained. Bind values, JWTs,
    SQL parameters and full statements never enter the observation record.
    """

    def __init__(self, engine, practice_id):
        self.engine = engine
        self.practice_id = str(practice_id)
        self.transactions = []
        self._live = {}
        self._lock = threading.Lock()
        self._listeners = (
            ("begin", self._begin),
            ("commit", self._commit),
            ("rollback", self._rollback),
            ("before_cursor_execute", self._before_sql),
            ("after_cursor_execute", self._after_sql),
        )

    def _begin(self, connection):
        with self._lock:
            record = {"bound": False, "events": [("begin",)], "tables": []}
            self.transactions.append(record)
            self._live[id(connection)] = record

    def _end(self, connection, kind):
        with self._lock:
            record = self._live.pop(id(connection), None)
            if record is not None:
                record["events"].append((kind,))

    def _commit(self, connection):
        self._end(connection, "commit")

    def _rollback(self, connection):
        self._end(connection, "rollback")

    def _before_sql(self, connection, cursor, statement, parameters, context, executemany):
        normalized = re.sub(r"\s+", " ", statement.lower().replace('"', '')).strip()
        tables = re.findall(r"\b(?:from|join|update|into)\s+(?:public\.)?([a-z_][a-z_0-9]*)", normalized)
        # Capture every relation-shaped reference in the generated route SQL,
        # including joined patient/location/Diary relations and authority grants.
        # This is scoped to the inspected SQLAlchemy route statements, not a
        # general-purpose SQL parser. No hand-maintained table allowlist hides
        # a newly reached relation.
        observed = tables
        if observed:
            with self._lock:
                record = self._live.get(id(connection))
                if record is None:
                    raise AssertionError("observed application SQL without an engine begin event")
                for table in observed:
                    record["tables"].append((table, record["bound"]))
                    record["events"].append(("table", table, record["bound"]))

    def _after_sql(self, connection, cursor, statement, parameters, context, executemany):
        normalized = re.sub(r"\s+", " ", statement.lower()).strip()
        matched = None
        if normalized.startswith("set local app.current_practice_id = "):
            matched = normalized.rstrip(";") == f"set local app.current_practice_id = '{self.practice_id}'"
        elif normalized.startswith("select set_config("):
            # SQLAlchemy's compiled parameter objects are inspected only to
            # compare the tenant; no value is copied into retained records.
            groups = getattr(context, "compiled_parameters", ())
            is_tenant_setting = "'app.current_practice_id'" in normalized or any(
                isinstance(group, Mapping) and "app.current_practice_id" in group.values() for group in groups
            )
            if is_tenant_setting:
                matched = bool(groups) and all(
                    isinstance(group, Mapping)
                    and any(str(value) == self.practice_id for value in group.values())
                    and (bool(re.search(r",\s*true\s*\)", normalized)) or any(value is True for value in group.values()))
                    for group in groups
                )
        if matched is not None:
            with self._lock:
                record = self._live[id(connection)]
                record["bound"] = matched
                record["events"].append(("bind", matched))

    def __enter__(self):
        for name, listener in self._listeners:
            event.listen(self.engine, name, listener)
        return self

    def __exit__(self, exc_type, exc, traceback):
        for name, listener in reversed(self._listeners):
            event.remove(self.engine, name, listener)

    def assert_bound_reads(self):
        assert self.transactions, "no real SQL transaction was observed"
        observed = [item for record in self.transactions for item in record["tables"]]
        assert observed, "no application table SQL was observed"
        assert all(bound for _, bound in observed), "application table access preceded the required tenant bind"
        assert not self._live, "a traced request or command transaction remains open"

    def assert_first_table(self, table):
        self.assert_bound_reads()
        matches = [record for record in self.transactions if record["tables"] and record["tables"][0][0] == table]
        assert matches, f"no distinct transaction started with the expected {table} read"
        return matches


def _tenant_sql_trace(engine, practice_id):
    return TenantSqlTrace(engine, practice_id)


@pytest.mark.parametrize("operation", [
    pytest.param("create", id="APT-T2-http-raw-create-rebind"),
    pytest.param("update", id="APT-T2-http-raw-update-rebind"),
    pytest.param("status", id="APT-T2-http-raw-status-rebind"),
])
def test_apt_t2_raw_response_reload_rebinds_after_commit(appointment_http_client, case_world, operation):
    client, headers = appointment_http_client
    target = None
    if operation != "create":
        target = _raw_create_success(client, headers, case_world,
            patient_label="Synthetic Tenant Trace Target", start=case_world.start,
            minutes=30, location_id=case_world.l1)
    q_before = case_world.snapshot(case_world.q)
    with _tenant_sql_trace(case_world.runtime.engine, case_world.p) as trace:
        if operation == "create":
            response = client.post(RAW_APPOINTMENTS_ENDPOINT, headers=headers, json={
                "patient_name_provisional": "Synthetic Tenant Trace Create",
                "practitioner_id": str(case_world.r), "location_id": str(case_world.l1),
                "start_time": case_world.start.isoformat(), "duration_minutes": 30,
            })
        elif operation == "update":
            response = client.put(f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}", headers=headers,
                json={"reason": "Synthetic Tenant Trace Update"})
        else:
            response = client.patch(f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}/status", headers=headers,
                json={"status": "Confirmed"})
    assert response.status_code == (201 if operation == "create" else 200)
    trace.assert_bound_reads()
    assert trace.transactions[0]["tables"][0] == ("users", True)
    commits = [index for index, record in enumerate(trace.transactions) if ("commit",) in record["events"]]
    assert len(commits) == 1
    reloads = trace.transactions[commits[0] + 1:]
    assert reloads and any(("appointments", True) in record["tables"] for record in reloads)
    assert all(("bind", True) in record["events"] for record in reloads if record["tables"])
    body = response.json()
    with case_world.writer() as reader:
        stored = reader.get(UUID(body["id"]))
    assert stored is not None
    assert str(stored["practice_id"]) == str(case_world.p)
    assert case_world.snapshot(case_world.q) == q_before


CREATE_TIME_ROUNDTRIPS = [
    pytest.param({"appointment_date": "2027-10-03", "start_time_local": "02:30:00"},
        "2027-10-02T16:30:00+00:00", "2027-10-03", "03:30:00", id="APT-INPUT-LOCAL-http-gap-roundtrip"),
    pytest.param({"start_time": "2027-10-03T02:30:00"},
        "2027-10-02T16:30:00+00:00", "2027-10-03", "03:30:00", id="APT-INPUT-INSTANT-http-naive-gap-roundtrip"),
    pytest.param({"start_time": "2027-04-04T02:30:00+11:00"},
        "2027-04-03T15:30:00+00:00", "2027-04-04", "02:30:00", id="APT-INPUT-INSTANT-http-first-fold-roundtrip"),
    pytest.param({"start_time": "2027-04-04T02:30:00+10:00"},
        "2027-04-03T16:30:00+00:00", "2027-04-04", "02:30:00", id="APT-INPUT-INSTANT-http-second-fold-roundtrip"),
]


@pytest.mark.parametrize("time_fields,expected_utc,expected_date,expected_local", CREATE_TIME_ROUNDTRIPS)
def test_apt_input_create_proposal_json_roundtrip_has_consistent_coordinates(
    appointment_http_client, case_world, time_fields, expected_utc, expected_date, expected_local,
):
    client, headers = appointment_http_client
    case_world.set_timezone("Australia/Sydney")
    expected = datetime.fromisoformat(expected_utc)
    projected = expected.astimezone(ZoneInfo("Australia/Sydney"))
    assert projected.date().isoformat() == expected_date
    assert projected.time().replace(tzinfo=None).isoformat() == expected_local
    before = case_world.snapshot()
    proposal_response = client.post(CREATE_PROPOSAL_ENDPOINT,
        headers=_confirmation_key_headers(headers, "temporal-roundtrip-propose"), json={
            "patient_name_provisional": "Synthetic Temporal Roundtrip",
            "practitioner_id": str(case_world.r), "location_id": str(case_world.l1),
            "duration_minutes": 30, **time_fields,
        })
    assert proposal_response.status_code == 200
    proposal = proposal_response.json()
    assert proposal["safe"] is True and proposal["blocks"] == []
    assert proposal["requires_confirmation"] is True
    assert proposal["signed_confirmation_evidence_required"] is True
    assert proposal["signed_confirmation_evidence"]
    assert proposal["confirm_endpoint"] == CREATE_CONFIRM_ENDPOINT
    command = proposal["command"]
    assert _utc(_parse_api_datetime(command["start_time"])) == expected
    assert command["appointment_date"] == expected_date
    assert command["start_time_local"] == expected_local
    confirmation = deepcopy(proposal["confirm_payload"])
    assert confirmation["create_proposal"]["command"] == command
    assert confirmation["signed_confirmation_evidence"] == proposal["signed_confirmation_evidence"]
    assert case_world.snapshot() == before
    confirmation["confirmed"] = True
    confirmed = _confirm_create(client, headers, proposal["confirm_endpoint"], "temporal-roundtrip-confirm", confirmation)
    assert confirmed.status_code == 200
    body = confirmed.json()
    _assert_confirmed_create_confirmation(body, expected)
    assert body["appointment"]["appointment_date"] == expected_date
    assert body["appointment"]["start_time_local"] == expected_local
    with case_world.writer() as reader:
        stored = reader.get(UUID(body["appointment"]["id"]))
    assert _utc(stored["start_time"]) == expected
    assert stored["appointment_date"].isoformat() == expected_date
    assert stored["start_time_local"].isoformat() == expected_local
    assert stored["duration_minutes"] == 30
    after = case_world.snapshot()

    # A complete explicit local pair that contradicts the instant must be
    # rejected before writing; existing-time canonicalization is not license
    # to silently replace caller-supplied conflicting coordinates.
    invalid = client.post(RAW_CREATE_ENDPOINT, headers=headers, json={
        "patient_name_provisional": "Synthetic Temporal Inconsistent Input",
        "practitioner_id": str(case_world.r2), "location_id": str(case_world.l2),
        "start_time": expected_utc, "appointment_date": expected_date,
        "start_time_local": "06:00:00", "duration_minutes": 30,
    })
    assert invalid.status_code == 422
    assert invalid.json() == {"detail": "Local appointment coordinates disagree with start_time"}
    assert case_world.snapshot() == after


from app.routers import appointments as appointment_routes


@pytest.mark.parametrize("operation", [
    pytest.param("raw-create", id="APT-INPUT-INSTANT-http-same-day-fold-raw-create"),
    pytest.param("confirmed-create", id="APT-INPUT-INSTANT-http-same-day-fold-confirm-create"),
    pytest.param("raw-update", id="APT-INPUT-INSTANT-http-same-day-fold-duration-update"),
    pytest.param("update-proposal", id="APT-INPUT-INSTANT-http-same-day-fold-update-proposal"),
])
def test_apt_input_same_day_fold_uses_actual_time_and_retains_past_date_policy(
    appointment_http_client, case_world, monkeypatch, operation,
):
    client, headers = appointment_http_client
    case_world.set_timezone("Australia/Sydney")
    zone = ZoneInfo("Australia/Sydney")
    fixed_now = datetime.fromisoformat("2027-04-04T02:45:00+11:00").astimezone(zone)
    future = datetime.fromisoformat("2027-04-04T02:15:00+10:00").astimezone(zone)
    assert fixed_now.fold == 0 and future.fold == 1
    assert future.date() == fixed_now.date()
    assert future.time().replace(tzinfo=None) < fixed_now.time().replace(tzinfo=None)
    assert _utc(future) > _utc(fixed_now)
    target = None
    if operation in {"raw-update", "update-proposal"}:
        target = case_world.row("same-day-fold-update", start=future, minutes=30, location_id=case_world.l1)
        _insert_and_commit(case_world, target)
    initial = case_world.snapshot()
    past = "2027-04-03T20:00:00+11:00"
    # A-approved seam: only the clinic clock is controlled. The actual guard,
    # schema, authentication, proposal signatures, SQL and serializers run.
    with monkeypatch.context() as clock_patch:
        clock_patch.setattr(appointment_routes, "_clinic_local_now", lambda practice_tz: fixed_now.astimezone(practice_tz))
        if operation == "raw-create":
            created = _raw_create_success(client, headers, case_world,
                patient_label="Synthetic Same-day Fold", start=future, minutes=15, location_id=case_world.l1)
            assert _utc(_parse_api_datetime(created["start_time"])) == _utc(future)
        elif operation == "confirmed-create":
            proposal, confirmation = _staff_create_proposal(client, headers, case_world,
                start=future, location_id=case_world.l1, proposal_key="same-day-fold-propose",
                patient_label="Synthetic Same-day Fold Confirmation", minutes=15)
            assert case_world.snapshot() == initial
            confirmation["confirmed"] = True
            response = _confirm_create(client, headers, proposal["confirm_endpoint"], "same-day-fold-confirm", confirmation)
            assert response.status_code == 200
            _assert_confirmed_create_confirmation(response.json(), future)
        elif operation == "raw-update":
            response = client.put(f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}", headers=headers,
                json={"duration_minutes": 15})
            assert response.status_code == 200
            assert _utc(_parse_api_datetime(response.json()["start_time"])) == _utc(future)
            assert response.json()["duration_minutes"] == 15
            with case_world.writer() as reader:
                stored = reader.get(target["id"])
            assert _utc(stored["start_time"]) == _utc(future) and stored["duration_minutes"] == 15
        else:
            response = client.post(f"{RAW_APPOINTMENTS_ENDPOINT}/proposals/update/{target['id']}",
                headers=_confirmation_key_headers(headers, "same-day-fold-update-propose"), json={"duration_minutes": 15})
            assert response.status_code == 200
            body = response.json()
            assert body["safe"] is True and body["blocks"] == []
            assert _utc(_parse_api_datetime(body["command"]["start_time"])) == _utc(future)
            assert body["command"]["duration_minutes"] == 15
            assert case_world.snapshot() == initial
        after_positive = case_world.snapshot()

        if operation in {"raw-create", "confirmed-create"}:
            endpoint = RAW_CREATE_ENDPOINT if operation == "raw-create" else CREATE_PROPOSAL_ENDPOINT
            rejected = client.post(endpoint,
                headers=_confirmation_key_headers(headers, "past-calendar-propose"), json={
                    "patient_name_provisional": "Synthetic Preserved Past Date Policy",
                    "practitioner_id": str(case_world.r2), "location_id": str(case_world.l2),
                    "start_time": past, "duration_minutes": 15,
                })
        elif operation == "raw-update":
            rejected = client.put(f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}", headers=headers,
                json={"start_time": past})
        else:
            rejected = client.post(f"{RAW_APPOINTMENTS_ENDPOINT}/proposals/update/{target['id']}",
                headers=_confirmation_key_headers(headers, "past-calendar-update-propose"), json={"start_time": past})
        if operation in {"raw-create", "raw-update"}:
            assert rejected.status_code == 422
            assert rejected.json() == {"detail": {"code": "appointment_in_past", "message": "Appointment date is in the past."}}
        else:
            assert rejected.status_code == 200
            assert rejected.json()["safe"] is False
            assert {"code": "appointment_in_past", "severity": "blocked", "message": "Appointment date is in the past."} in rejected.json()["blocks"]
        assert case_world.snapshot() == after_positive


from copy import deepcopy

from sqlalchemy import event
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.routers import appointments as appointment_routes
from app.services.appointment_idempotency import hash_idempotency_key
from app.services.appointment_status_physical import StatusConfirmPhysicalError


UPDATE_PROPOSAL_ENDPOINT = "/api/v1/appointments/proposals/update"
UPDATE_CONFIRM_ENDPOINT = "/api/v1/appointments/proposals/update/confirm"
STATUS_PROPOSAL_ENDPOINT = "/api/v1/appointments/proposals/status"
STATUS_CONFIRM_ENDPOINT = "/api/v1/appointments/proposals/status/confirm"
STATUS_CONFIRM_OPERATION = "confirmAppointmentStatusProposal"
PHYSICAL_STATUS_LOCK_TIMEOUT_MS = 1000

UPDATE_CONFIRM_AUDIT_EVIDENCE = [
    "bernie_confirm_update_proposal",
    "source_update_proposal",
    "source_tool_intent_proposal",
    "bernie_signed_confirmation_evidence_verified",
]
STATUS_CONFIRM_AUDIT_EVIDENCE = [
    "status_product_adapter_v1",
    "status_signed_confirmation_evidence_verified",
    "status_current_authority_rechecked",
]


def _snapshot_rows(snapshot, table):
    rows = json.loads(snapshot[table])
    assert isinstance(rows, list)
    return rows


def _snapshot_row(snapshot, table, row_id):
    matches = [row for row in _snapshot_rows(snapshot, table) if row["id"] == str(row_id)]
    assert len(matches) == 1
    return matches[0]


def _assert_confirmation_graph(
    snapshot,
    *,
    target_id,
    operation_id,
    action,
    expected_pre_version,
    status_before=None,
    status_after=None,
    private_status_receipt=False,
):
    target = _snapshot_row(snapshot, "appointments", target_id)
    audits = _snapshot_rows(snapshot, "appointment_audit_log")
    receipts = _snapshot_rows(snapshot, "appointment_command_idempotency")
    assert len(audits) == len(receipts) == 1
    audit = audits[0]
    receipt = receipts[0]
    assert audit["appointment_id"] == str(target_id)
    assert audit["action"] == action
    assert audit["command_id"] == receipt["id"]
    assert receipt["operation_id"] == operation_id
    assert receipt["state"] == "completed"
    assert receipt["result_kind"] == "confirmed_write"
    assert receipt["target_appointment_id"] == str(target_id)
    assert receipt["audit_log_id"] == audit["id"]
    assert target["appointment_state_version"] == expected_pre_version + 1
    if status_before is not None:
        assert audit["status_before"] == status_before
    if status_after is not None:
        assert audit["status_after"] == status_after
        assert target["status"] == status_after
    if private_status_receipt:
        assert receipt["completed_receipt_version"] == 1
        assert receipt["pre_state_version"] == expected_pre_version
        assert receipt["post_state_version"] == expected_pre_version + 1
        assert receipt["response_body_canonical_bytes"]
    return target, audit, receipt


def _actual_update_confirmation(client, headers, target_id, changes, *, proposal_key):
    response = client.post(
        f"{UPDATE_PROPOSAL_ENDPOINT}/{target_id}",
        headers=_confirmation_key_headers(headers, proposal_key),
        json=changes,
    )
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["intent"] == "update_appointment"
    assert proposal["safe"] is True
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "proposal"
    assert proposal["blocks"] == []
    assert proposal["confirm_endpoint"] == UPDATE_CONFIRM_ENDPOINT
    assert proposal["update_proposal_freshness_id"]
    assert proposal["signed_confirmation_evidence_required"] is True
    assert proposal["signed_confirmation_evidence"]

    confirmation = deepcopy(proposal["confirm_payload"])
    assert confirmation["confirmed"] is False
    assert confirmation["update_proposal"]["command"] == proposal["command"]
    assert confirmation["update_proposal_freshness_id"] == (
        proposal["update_proposal_freshness_id"]
    )
    assert confirmation["signed_confirmation_evidence"] == (
        proposal["signed_confirmation_evidence"]
    )
    assert confirmation["signed_confirmation_evidence_required"] is True
    confirmation["confirmed"] = True
    return proposal, confirmation


def _actual_status_confirmation(client, headers, target_id, changes, *, proposal_key):
    response = client.post(
        f"{STATUS_PROPOSAL_ENDPOINT}/{target_id}",
        headers=_confirmation_key_headers(headers, proposal_key),
        json=changes,
    )
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["intent"] == "update_appointment_status"
    assert proposal["safe"] is True
    assert proposal["requires_confirmation"] is True
    assert proposal["blocks"] == []
    assert proposal["confirm_endpoint"] == STATUS_CONFIRM_ENDPOINT
    assert proposal["status_proposal_freshness_id"]
    assert proposal["status_proposal_version_binding"]
    assert proposal["signed_confirmation_evidence_required"] is True
    assert proposal["signed_confirmation_evidence"]

    confirmation = deepcopy(proposal["confirm_payload"])
    assert confirmation["confirmed"] is False
    assert confirmation["status_proposal"]["command"] == proposal["command"]
    assert confirmation["status_proposal_freshness_id"] == (
        proposal["status_proposal_freshness_id"]
    )
    assert confirmation["status_proposal_version_binding"] == (
        proposal["status_proposal_version_binding"]
    )
    assert confirmation["signed_confirmation_evidence"] == (
        proposal["signed_confirmation_evidence"]
    )
    assert confirmation["signed_confirmation_evidence_required"] is True
    confirmation["confirmed"] = True
    return proposal, confirmation


def _confirm_update(client, headers, key, confirmation):
    return client.post(
        UPDATE_CONFIRM_ENDPOINT,
        headers=_confirmation_key_headers(headers, key),
        json=confirmation,
    )


def _confirm_status(client, headers, key, confirmation):
    return client.post(
        STATUS_CONFIRM_ENDPOINT,
        headers=_confirmation_key_headers(headers, key),
        json=confirmation,
    )


def _assert_confirmed_update(body):
    assert body["intent"] == "confirm_update_appointment"
    assert body["safe"] is True
    assert body["requires_confirmation"] is False
    assert body["autonomy_tier"] == "confirmed_write"
    assert body["summary"] == (
        "Confirmed supervised Bernie update proposal and updated one appointment."
    )
    assert body["blocks"] == []
    assert body["audit_evidence"] == UPDATE_CONFIRM_AUDIT_EVIDENCE
    assert body["appointment"] is not None


def _assert_confirmed_status(body):
    assert body["intent"] == "confirm_status_appointment"
    assert body["safe"] is True
    assert body["requires_confirmation"] is False
    assert body["autonomy_tier"] == "confirmed_write"
    assert body["summary"] == "Confirmed status proposal and updated one appointment."
    assert body["blocks"] == []
    assert body["audit_evidence"] == STATUS_CONFIRM_AUDIT_EVIDENCE
    assert body["appointment"] is not None


def _assert_blocked_confirmation(body, intent):
    assert body["intent"] == intent
    assert body["safe"] is False
    assert body["requires_confirmation"] is True
    assert body["autonomy_tier"] == "blocked"
    assert body["appointment"] is None
    assert body["blocks"]
    assert all(item["severity"] == "blocked" for item in body["blocks"])


def _start_http(call, world):
    deadline = time.monotonic() + world.runtime.test_deadline_seconds
    result = {}
    finished = threading.Event()

    def run():
        try:
            result["response"] = call()
        except BaseException as exc:
            result["error"] = exc
        finally:
            finished.set()

    thread = threading.Thread(target=run, name="appointment-http-writer")
    thread.start()
    return result, finished, thread, deadline


def _observe_application_wait_for_blocker(world, blocker_pid, finished, *, deadline):
    observed = []
    while time.monotonic() < deadline:
        with world.runtime.observer_engine.connect() as observer:
            rows = observer.execute(
                text("""
                    SELECT pid, pg_blocking_pids(pid) AS blockers
                    FROM pg_stat_activity
                    WHERE datname = :database
                      AND usename = :role
                      AND pid <> :blocker
                      AND :blocker = ANY(pg_blocking_pids(pid))
                    ORDER BY pid
                """),
                {
                    "database": world.runtime.database_name,
                    "role": world.runtime.application_role,
                    "blocker": blocker_pid,
                },
            ).mappings().all()
        if rows:
            assert len(rows) == 1, "one HTTP command session must own the observed wait"
            assert rows[0]["blockers"] == [blocker_pid]
            observed.append(rows[0]["pid"])
            return observed[0]
        if finished.is_set():
            raise AssertionError("HTTP command finished before a real database wait was observed")
        finished.wait(min(world.runtime.poll_interval_seconds, _remaining(deadline)))
    raise AssertionError("expected pg_blocking_pids dependency was not observed")


def _join_http(result, finished, thread, deadline):
    # One deadline includes observation, database wait and this final closure
    # attempt. Never reset a budget or assert before attempting the join.
    thread.join(timeout=_remaining(deadline))
    assert not thread.is_alive(), "HTTP writer remains alive; outer runner must reconcile before database disposal"
    assert finished.is_set(), "HTTP writer ended without a completion observation"
    return result


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-UPDATE-http-legacy-local-coordinates-recanonicalized")],
)
def test_confirmed_reason_only_update_recanonicalizes_legacy_coordinates(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    case_world.set_timezone("Australia/Sydney")
    target = case_world.row(
        "update-legacy-coordinates",
        location_id=case_world.l1,
        start=case_world.start + timedelta(minutes=90),
    )
    actual_instant = target["start_time"]
    target["appointment_date"] = target["appointment_date"] + timedelta(days=3)
    target["start_time_local"] = target["start_time_local"].replace(hour=5, minute=17)
    _insert_and_commit(case_world, target)
    before = case_world.snapshot()

    proposal, confirmation = _actual_update_confirmation(
        client,
        headers,
        target["id"],
        {"reason": "Synthetic reason-only canonicalization"},
        proposal_key="apt-update-legacy-proposal",
    )
    assert case_world.snapshot() == before
    canonical = actual_instant.astimezone(ZoneInfo("Australia/Sydney"))
    assert _confirmation_utc(_confirmation_datetime(proposal["command"]["start_time"])) == (
        _confirmation_utc(actual_instant)
    )
    assert proposal["command"]["appointment_date"] == canonical.date().isoformat()
    assert proposal["command"]["start_time_local"] == (
        canonical.time().replace(tzinfo=None).isoformat()
    )

    response = _confirm_update(
        client, headers, "apt-update-legacy-confirm", confirmation
    )
    assert response.status_code == 200
    body = response.json()
    _assert_confirmed_update(body)
    assert _confirmation_utc(_confirmation_datetime(body["appointment"]["start_time"])) == (
        _confirmation_utc(actual_instant)
    )
    assert body["appointment"]["appointment_date"] == canonical.date().isoformat()
    assert body["appointment"]["start_time_local"] == (
        canonical.time().replace(tzinfo=None).isoformat()
    )
    assert body["appointment"]["reason"] == "Synthetic reason-only canonicalization"

    after = case_world.snapshot()
    stored, _, _ = _assert_confirmation_graph(
        after,
        target_id=target["id"],
        operation_id="confirmAppointmentUpdateProposal",
        action="update",
        expected_pre_version=1,
    )
    assert _confirmation_utc(_confirmation_datetime(stored["start_time"])) == (
        _confirmation_utc(actual_instant)
    )
    assert stored["appointment_date"] == canonical.date().isoformat()
    assert stored["start_time_local"] == canonical.time().replace(tzinfo=None).isoformat()


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-UPDATE-http-explicit-second-fold-move")],
)
def test_confirmed_update_preserves_explicit_second_fold_instant(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    case_world.set_timezone("Australia/Sydney")
    target = case_world.row(
        "update-second-fold-target",
        location_id=case_world.l2,
        start=case_world.start,
    )
    _insert_and_commit(case_world, target)
    second_fold = datetime.fromisoformat("2040-04-01T02:30:00+10:00")
    localized = second_fold.astimezone(ZoneInfo("Australia/Sydney"))
    assert localized.fold == 1
    before = case_world.snapshot()

    proposal, confirmation = _actual_update_confirmation(
        client,
        headers,
        target["id"],
        {"start_time": second_fold.isoformat()},
        proposal_key="apt-update-second-fold-proposal",
    )
    assert case_world.snapshot() == before
    assert _confirmation_utc(_confirmation_datetime(proposal["command"]["start_time"])) == (
        _confirmation_utc(second_fold)
    )
    assert proposal["command"]["appointment_date"] == "2040-04-01"
    assert proposal["command"]["start_time_local"] == "02:30:00"

    response = _confirm_update(
        client, headers, "apt-update-second-fold-confirm", confirmation
    )
    assert response.status_code == 200
    body = response.json()
    _assert_confirmed_update(body)
    assert _confirmation_utc(_confirmation_datetime(body["appointment"]["start_time"])) == (
        _confirmation_utc(second_fold)
    )
    assert body["appointment"]["appointment_date"] == "2040-04-01"
    assert body["appointment"]["start_time_local"] == "02:30:00"
    after = case_world.snapshot()
    stored, _, _ = _assert_confirmation_graph(
        after,
        target_id=target["id"],
        operation_id="confirmAppointmentUpdateProposal",
        action="update",
        expected_pre_version=1,
    )
    assert _confirmation_utc(_confirmation_datetime(stored["start_time"])) == (
        _confirmation_utc(second_fold)
    )


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-STATUS-http-confirmed-write-and-tenant-first-read")],
)
def test_confirmed_status_uses_actual_proposal_and_atomic_receipt(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    target = case_world.row("status-success", location_id=case_world.l1)
    _insert_and_commit(case_world, target)
    before = case_world.snapshot()
    proposal, confirmation = _actual_status_confirmation(
        client,
        headers,
        target["id"],
        {"status": "Confirmed"},
        proposal_key="apt-status-success-proposal",
    )
    assert case_world.snapshot() == before
    assert proposal["command"]["status"] == "Confirmed"

    with _tenant_sql_trace(case_world.runtime.engine, case_world.p) as trace:
        response = _confirm_status(
            client, headers, "apt-status-success-confirm", confirmation
        )
    assert response.status_code == 200
    body = response.json()
    _assert_confirmed_status(body)
    assert body["appointment"]["status"] == "Confirmed"
    trace.assert_bound_reads()
    assert trace.transactions[0]["tables"][0] == ("users", True)
    trace.assert_first_table("practices")

    _assert_confirmation_graph(
        case_world.snapshot(),
        target_id=target["id"],
        operation_id=STATUS_CONFIRM_OPERATION,
        action="status_change",
        expected_pre_version=1,
        status_before="Booked",
        status_after="Confirmed",
        private_status_receipt=True,
    )


@pytest.mark.parametrize(
    "_case",
    [pytest.param(None, id="APT-R2-http-update-confirm-observed-wait-conflict")],
)
def test_confirmations_rollback_after_real_database_wait_and_collision(
    appointment_http_client, case_world, _case,
):
    # The signed terminal-status path is deferred before physical execution;
    # its separate policy test preserves that boundary. This is a real update.
    client, headers = appointment_http_client
    target = case_world.row(
        "held-update-target", location_id=case_world.l1,
        start=case_world.start + timedelta(minutes=60),
    )
    _insert_and_commit(case_world, target)
    _, confirmation = _actual_update_confirmation(
        client, headers, target["id"], {"start_time": case_world.start.isoformat()},
        proposal_key="apt-held-update-proposal",
    )
    call = lambda: _confirm_update(client, headers, "apt-held-update-confirm", confirmation)
    before = case_world.snapshot()
    target_before = _snapshot_row(before, "appointments", target["id"])
    winner = case_world.row("held-update-winner", location_id=case_world.l2,
                            start=case_world.start)
    with case_world.writer() as blocker:
        blocker.insert(winner)
        result, finished, thread, deadline = _start_http(call, case_world)
        try:
            observation_deadline = deadline - case_world.runtime.wait_timeout_seconds
            waiting_pid = _observe_application_wait_for_blocker(
                case_world, blocker.pid, finished, deadline=observation_deadline,
            )
            assert waiting_pid != blocker.pid
            blocker.commit()
        finally:
            blocker.rollback()
            _join_http(result, finished, thread, deadline)
    assert "error" not in result
    response = result["response"]
    assert response.status_code == 200
    body = response.json()
    _assert_blocked_confirmation(body, "confirm_update_appointment")
    assert body["blocks"][0]["code"] == "appointment_conflict"
    assert {
        "code": "appointment_conflict", "severity": "blocked",
        "message": "This appointment overlaps an existing booking.",
    } in body["blocks"]
    after = case_world.snapshot()
    assert _snapshot_row(after, "appointments", target["id"]) == target_before
    assert _snapshot_row(after, "appointments", winner["id"])["status"] == "Booked"
    assert after["appointment_audit_log"] == before["appointment_audit_log"]
    assert after["appointment_command_idempotency"] == before["appointment_command_idempotency"]


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-R7-http-status-physical-lock-timeout-not-conflict")],
)
def test_status_physical_lock_timeout_is_not_appointment_conflict_or_retried(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    target = case_world.row("status-lock-timeout", location_id=case_world.l1)
    _insert_and_commit(case_world, target)
    _, confirmation = _actual_status_confirmation(
        client,
        headers,
        target["id"],
        {"status": "Confirmed"},
        proposal_key="apt-status-lock-timeout-proposal",
    )
    before = case_world.snapshot()
    physical_errors = []

    def capture_physical_error(context):
        original = context.original_exception
        physical_errors.append(
            (
                getattr(original, "sqlstate", None) or getattr(original, "pgcode", None),
                getattr(getattr(original, "diag", None), "constraint_name", None),
            )
        )

    event.listen(case_world.runtime.engine, "handle_error", capture_physical_error)
    try:
        with case_world.writer() as blocker:
            blocker.connection.execute(
                text("""
                    SELECT id FROM public.appointments
                    WHERE practice_id = :practice AND id = :target
                    FOR UPDATE
                """),
                {"practice": case_world.p, "target": target["id"]},
            ).one()
            result, finished, thread, deadline = _start_http(
                lambda: _confirm_status(
                    client,
                    headers,
                    "apt-status-lock-timeout-confirm",
                    confirmation,
                ),
                case_world,
            )
            try:
                observation_deadline = deadline - case_world.runtime.wait_timeout_seconds
                _observe_application_wait_for_blocker(
                    case_world,
                    blocker.pid,
                    finished,
                    deadline=observation_deadline,
                )
                assert finished.wait(
                    _remaining(deadline - case_world.runtime.wait_timeout_seconds)
                ), "physical status lock timeout did not terminate the command"
            finally:
                blocker.rollback()
                _join_http(result, finished, thread, deadline)
    finally:
        event.remove(case_world.runtime.engine, "handle_error", capture_physical_error)

    assert "response" not in result
    error = result.get("error")
    assert isinstance(error, DBAPIError)
    original = error.orig
    assert (getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)) == (
        "55P03"
    )
    assert not _collision(error)
    assert physical_errors == [("55P03", None)], "the command must not automatically retry"
    assert case_world.snapshot() == before

    legitimate = _confirm_status(client, headers, "apt-status-after-timeout-confirm", confirmation)
    assert legitimate.status_code == 200
    _assert_confirmed_status(legitimate.json())
    _assert_confirmation_graph(
        case_world.snapshot(), target_id=target["id"],
        operation_id=STATUS_CONFIRM_OPERATION, action="status_change",
        expected_pre_version=1, status_before="Booked", status_after="Confirmed",
        private_status_receipt=True,
    )


@pytest.mark.parametrize(
    "_appointment_case",
    [pytest.param(None, id="APT-R7-http-status-before-commit-atomic-abort")],
)
def test_status_before_commit_fault_rolls_back_complete_staged_write_set(
    appointment_http_client, case_world, _appointment_case
):
    client, headers = appointment_http_client
    target = case_world.row("status-before-commit-abort", location_id=case_world.l1)
    _insert_and_commit(case_world, target)
    _, confirmation = _actual_status_confirmation(
        client,
        headers,
        target["id"],
        {"status": "Confirmed"},
        proposal_key="apt-status-abort-proposal",
    )
    before = case_world.snapshot()
    fault_key = "apt-status-abort-confirm"
    expected_key_hash = hash_idempotency_key(
        fault_key,
        appointment_routes._status_confirm_domain_secret("idempotency"),
    )
    boundary = {}
    hook_reached = threading.Event()
    rollback_observed = threading.Event()

    def fail_exact_command_before_commit(session):
        if session.get_bind() is not case_world.runtime.engine:
            return
        candidate = session.execute(
            text("""
                SELECT id FROM public.appointment_command_idempotency
                WHERE practice_id = :practice
                  AND operation_id = :operation
                  AND idempotency_key_hash = :key_hash
            """),
            {
                "practice": case_world.p,
                "operation": STATUS_CONFIRM_OPERATION,
                "key_hash": expected_key_hash,
            },
        ).scalar_one_or_none()
        if candidate is None:
            return

        # SQLAlchemy 2.0.50 session.py SHA
        # b12db5f1bc4056e8be239a9557b0124c136a8addd139a3a3efce1668c032fbd3 dispatches
        # before_commit before _prepare_impl's automatic flush loop.  This is
        # therefore an explicit real flush of the final staged write set.
        session.flush()
        receipt = session.execute(
            text("""
                SELECT to_jsonb(t) FROM public.appointment_command_idempotency t
                WHERE id = :id AND practice_id = :practice
            """),
            {"id": candidate, "practice": case_world.p},
        ).scalar_one()
        staged_target = session.execute(
            text("""
                SELECT to_jsonb(t) FROM public.appointments t
                WHERE id = :id AND practice_id = :practice
            """),
            {"id": target["id"], "practice": case_world.p},
        ).scalar_one()
        staged_audit = session.execute(
            text("""
                SELECT to_jsonb(t) FROM public.appointment_audit_log t
                WHERE id = :id AND practice_id = :practice
            """),
            {"id": receipt["audit_log_id"], "practice": case_world.p},
        ).scalar_one()

        assert receipt["operation_id"] == STATUS_CONFIRM_OPERATION
        assert receipt["idempotency_key_hash"] == expected_key_hash
        assert receipt["state"] == "completed"
        assert receipt["result_kind"] == "confirmed_write"
        assert receipt["target_appointment_id"] == str(target["id"])
        assert receipt["completed_receipt_version"] == 1
        assert receipt["pre_state_version"] == 1
        assert receipt["post_state_version"] == 2
        assert receipt["audit_log_id"] == staged_audit["id"]
        assert staged_target["status"] == "Confirmed"
        assert staged_target["appointment_state_version"] == 2
        assert staged_audit["appointment_id"] == str(target["id"])
        assert staged_audit["command_id"] == receipt["id"]
        assert staged_audit["action"] == "status_change"
        assert staged_audit["status_before"] == "Booked"
        assert staged_audit["status_after"] == "Confirmed"
        boundary["session"] = session
        boundary["snapshot"] = MappingProxyType(
            {
                "appointments": json.dumps(
                    [staged_target], sort_keys=True, separators=(",", ":")
                ),
                "appointment_audit_log": json.dumps(
                    [staged_audit], sort_keys=True, separators=(",", ":")
                ),
                "appointment_command_idempotency": json.dumps(
                    [receipt], sort_keys=True, separators=(",", ":")
                ),
            }
        )
        hook_reached.set()
        raise StatusConfirmPhysicalError("authored synthetic pre-commit abort")

    def observe_real_rollback(session):
        if session is boundary.get("session"):
            rollback_observed.set()

    event.listen(Session, "before_commit", fail_exact_command_before_commit)
    event.listen(Session, "after_rollback", observe_real_rollback)
    try:
        response = _confirm_status(client, headers, fault_key, confirmation)
    finally:
        event.remove(Session, "after_rollback", observe_real_rollback)
        event.remove(Session, "before_commit", fail_exact_command_before_commit)

    assert hook_reached.is_set(), "the exact command never reached before_commit"
    assert rollback_observed.is_set(), "db.begin() exit did not issue a real DBAPI rollback"
    staged = boundary["snapshot"]
    assert tuple(staged) == SNAPSHOT_TABLES
    assert all(isinstance(staged[table], str) for table in SNAPSHOT_TABLES)
    assert all(_snapshot_rows(staged, table) for table in SNAPSHOT_TABLES)
    assert all(staged[table] != before[table] for table in SNAPSHOT_TABLES)
    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "status_confirm_transaction_unavailable",
            "message": "The status confirmation did not commit.",
        }
    }
    assert case_world.snapshot() == before

    # The fault was removed and the first transaction left no claim.  The same
    # server-minted evidence remains current; a fresh key must commit once.
    legitimate = _confirm_status(
        client,
        headers,
        "apt-status-after-abort-confirm",
        confirmation,
    )
    assert legitimate.status_code == 200
    legitimate_body = legitimate.json()
    _assert_confirmed_status(legitimate_body)
    assert legitimate_body["appointment"]["status"] == "Confirmed"
    _assert_confirmation_graph(
        case_world.snapshot(),
        target_id=target["id"],
        operation_id=STATUS_CONFIRM_OPERATION,
        action="status_change",
        expected_pre_version=1,
        status_before="Booked",
        status_after="Confirmed",
        private_status_receipt=True,
    )


@pytest.mark.parametrize("_case", [pytest.param(None, id="APT-T2-http-delete-first-user-read-bound")])
def test_apt_t2_delete_confirmation_binds_before_first_command_user_read(
    appointment_http_client, case_world, _case,
):
    client, headers = appointment_http_client
    target = case_world.row("delete-tenant-trace", location_id=case_world.l1)
    _insert_and_commit(case_world, target)
    before = case_world.snapshot()
    q_before = case_world.snapshot(case_world.q)
    grant_parameters = {"practice": case_world.p, "actor": case_world.actor}
    with case_world.runtime.admin_engine.begin() as setup:
        setup.execute(text("""
            INSERT INTO public.user_capability_grants (practice_id,user_id,capability_code)
            VALUES (:practice,:actor,'appointment.cancel.confirm')
        """), grant_parameters)
    try:
        # The real grant trigger advances authority generation before the
        # actual authenticated proposal signs its current state.
        proposed = client.post(f"{RAW_APPOINTMENTS_ENDPOINT}/proposals/delete/{target['id']}",
            headers=_confirmation_key_headers(headers, "delete-trace-proposal"),
            json={"cancellation_reason": "Synthetic tenant trace cancellation", "status_reason_code": "PATIENT_CANCELLED"})
        assert proposed.status_code == 200
        proposal = proposed.json()
        assert proposal["safe"] is True and proposal["blocks"] == []
        assert proposal["confirm_endpoint"] == "/api/v1/appointments/proposals/delete/confirm"
        assert proposal["delete_proposal_version_binding"]
        assert proposal["signed_confirmation_evidence"]
        confirmation = deepcopy(proposal["confirm_payload"])
        assert confirmation["confirmed"] is False
        confirmation["confirmed"] = True
        assert case_world.snapshot() == before
        with _tenant_sql_trace(case_world.runtime.engine, case_world.p) as trace:
            response = client.post(proposal["confirm_endpoint"],
                headers=_confirmation_key_headers(headers, "delete-trace-confirm"), json=confirmation)
        assert response.status_code == 200
        body = response.json()
        assert body["schema_version"] == "raisa.delete_confirm_public_envelope.v1"
        assert body["intent"] == "confirm_delete_appointment"
        assert body["safe"] is True and body["requires_confirmation"] is False
        assert body["autonomy_tier"] == "confirmed_write" and body["blocks"] == []
        assert body["receipt"]["appointment_id"] == str(target["id"])
        assert body["receipt"]["status"] == "Cancelled"
        assert body["receipt"]["status_reason_code"] == "PATIENT_CANCELLED"
        trace.assert_bound_reads()
        first_user_transactions = trace.assert_first_table("users")
        assert len(first_user_transactions) >= 2, "request authentication cannot stand in for fresh command context"
        command_transactions = [record for record in first_user_transactions
            if ("user_capability_grants", True) in record["tables"]]
        assert len(command_transactions) == 1
        assert ("commit",) in command_transactions[0]["events"]
        after = case_world.snapshot()
        appointments = json.loads(after["appointments"])
        audits = json.loads(after["appointment_audit_log"])
        receipts = json.loads(after["appointment_command_idempotency"])
        assert len(appointments) == len(audits) == len(receipts) == 1
        assert appointments[0]["id"] == str(target["id"])
        assert appointments[0]["status"] == "Cancelled"
        assert appointments[0]["appointment_state_version"] == 2
        assert audits[0]["action"] == "delete"
        assert audits[0]["appointment_id"] == str(target["id"])
        assert receipts[0]["operation_id"] == "confirmAppointmentDeleteProposal"
        assert receipts[0]["state"] == "completed"
        assert audits[0]["command_id"] == receipts[0]["id"]
        assert receipts[0]["audit_log_id"] == audits[0]["id"]
        assert case_world.snapshot(case_world.q) == q_before
    finally:
        # Remove only the synthetic grant, using its real trigger. Audit rows
        # remain append-only and are retained for the outer database drop.
        with case_world.runtime.admin_engine.begin() as cleanup:
            cleanup.execute(text("""
                DELETE FROM public.user_capability_grants
                WHERE practice_id=:practice AND user_id=:actor
                  AND capability_code='appointment.cancel.confirm'
            """), grant_parameters)


@pytest.mark.parametrize("status", [
    pytest.param("Cancelled", id="APT-INPUT-OVERFLOW-db-end-Cancelled"),
    pytest.param("NoShow", id="APT-INPUT-OVERFLOW-db-end-NoShow"),
    pytest.param("DNA", id="APT-INPUT-OVERFLOW-db-end-DNA"),
])
def test_apt_input_nonblocking_rows_still_reject_end_overflow(case_world, status):
    row = case_world.row("finite-end-positive", status=status, minutes=1)
    # SQL text/JSON observations avoid the Python datetime year limit. The
    # positive start is finite in PostgreSQL and a one-minute end is valid.
    row["start_time"] = "294276-12-31 23:50:00+00"
    _insert_and_commit(case_world, row)
    before = case_world.snapshot()
    stored = json.loads(before["appointments"])
    assert len(stored) == 1 and stored[0]["duration_minutes"] == 1
    assert stored[0]["status"] == status
    with case_world.writer() as writer:
        with pytest.raises(DBAPIError) as raised:
            writer.update(row["id"], duration_minutes=30)
        writer.rollback()
        assert not writer.connection.in_transaction()
        original = raised.value.orig
        assert (getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)) == "22008"
        assert not _collision(raised.value)
    assert case_world.snapshot() == before


from collections.abc import Mapping
from datetime import date, datetime, time as datetime_time, timedelta, timezone
from ipaddress import ip_address
import math
import re
from uuid import NAMESPACE_URL, uuid5

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine


PREDECESSOR = "x3y4z5a6b7c8"
CANDIDATE = "y4z5a6b7c8d9"

EXCLUSION = "ex_appointments_practice_practitioner_no_overlap"
DURATION_CHECK = "ck_appointments_duration_minutes_1_480"
FINITE_START_CHECK = "ck_appointments_start_time_finite"
FINITE_END_CHECK = "ck_appointments_end_time_finite"
OWNED_CONSTRAINTS = {
    EXCLUSION,
    DURATION_CHECK,
    FINITE_START_CHECK,
    FINITE_END_CHECK,
}

RUNTIME_KEYS = {
    "admin_engine",
    "observer_engine",
    "database_name",
    "predecessor_revision",
    "candidate_revision",
    "migrate",
    "test_deadline_seconds",
}
RESULT_KEYS = {"exit_code", "timed_out", "stdout", "stderr"}


def _require(condition, message):
    """Fail without rendering engine URLs, credentials, or connection values."""
    if not condition:
        raise AssertionError(message)


def _is_loopback(host):
    if not isinstance(host, str) or not host:
        return False
    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False


def _validated_engine_endpoint(engine, expected_database, label):
    _require(isinstance(engine, Engine), f"{label} must be a SQLAlchemy Engine")
    _require(engine.dialect.name == "postgresql", f"{label} must use PostgreSQL")
    _require(not engine.echo, f"{label} SQL logging must be disabled")

    url = engine.url
    _require(_is_loopback(url.host), f"{label} URL must use a loopback host")
    _require(isinstance(url.username, str) and url.username, f"{label} URL needs a user")
    _require(url.database == expected_database, f"{label} URL database mismatch")
    url_port = url.port if url.port is not None else 5432
    _require(type(url_port) is int and url_port > 0, f"{label} URL port is invalid")

    with engine.connect() as connection:
        actual = connection.execute(
            text(
                """
                SELECT pg_catalog.current_database(),
                       CURRENT_USER,
                       SESSION_USER,
                       pg_catalog.host(pg_catalog.inet_server_addr()),
                       pg_catalog.inet_server_port()
                """
            )
        ).one()

    _require(actual[0] == expected_database, f"{label} connected database mismatch")
    _require(actual[1] == url.username, f"{label} current_user mismatch")
    _require(actual[2] == url.username, f"{label} session_user mismatch")
    _require(_is_loopback(actual[3]), f"{label} server address is not loopback")
    _require(actual[4] == url_port, f"{label} connected port mismatch")
    return ("loopback", url_port, expected_database, actual[3])


def _runtime(raw):
    _require(isinstance(raw, Mapping), "migration runtime must be a mapping")
    _require(set(raw) == RUNTIME_KEYS, "migration runtime keys mismatch")
    _require(raw["predecessor_revision"] == PREDECESSOR, "predecessor mismatch")
    _require(raw["candidate_revision"] == CANDIDATE, "candidate mismatch")
    _require(
        isinstance(raw["database_name"], str) and raw["database_name"],
        "database_name must be a non-empty string",
    )
    _require(callable(raw["migrate"]), "migrate must be callable")
    deadline = raw["test_deadline_seconds"]
    _require(
        isinstance(deadline, (int, float))
        and not isinstance(deadline, bool)
        and math.isfinite(deadline)
        and deadline > 0,
        "test_deadline_seconds must be finite and positive",
    )

    admin_engine = raw["admin_engine"]
    observer_engine = raw["observer_engine"]
    _require(admin_engine is not observer_engine, "admin and observer engines must differ")
    admin_endpoint = _validated_engine_endpoint(
        admin_engine,
        raw["database_name"],
        "admin_engine",
    )
    observer_endpoint = _validated_engine_endpoint(
        observer_engine,
        raw["database_name"],
        "observer_engine",
    )
    _require(
        admin_engine.url.username != observer_engine.url.username,
        "admin and observer database users must differ",
    )
    _require(
        admin_endpoint[:3] == observer_endpoint[:3],
        "admin and observer engines must target the same loopback host, port, and database",
    )
    _require(
        admin_endpoint[3] == observer_endpoint[3],
        "admin and observer engines must reach the same server address",
    )
    return raw


def _assert_result_shape(result):
    assert isinstance(result, dict)
    assert set(result) == RESULT_KEYS
    assert type(result["exit_code"]) is int
    assert type(result["timed_out"]) is bool
    assert isinstance(result["stdout"], str)
    assert isinstance(result["stderr"], str)


def _assert_migration_succeeded(result):
    _assert_result_shape(result)
    assert result["timed_out"] is False
    assert result["exit_code"] == 0, result["stdout"] + "\n" + result["stderr"]


def _assert_migration_refused(result, expected_reason):
    _assert_result_shape(result)
    assert result["timed_out"] is False
    assert result["exit_code"] != 0
    diagnostic = (result["stdout"] + "\n" + result["stderr"]).lower()
    assert expected_reason.lower() in diagnostic


def _revision(observer_engine):
    with observer_engine.connect() as connection:
        rows = connection.execute(
            text("SELECT version_num FROM public.alembic_version")
        ).scalars().all()
    assert len(rows) == 1
    return rows[0]


def _catalogue(observer_engine):
    """Return immutable, ordered table and database catalogue observations."""
    with observer_engine.connect() as connection:
        columns = tuple(
            tuple(row)
            for row in connection.execute(
                text(
                    """
                    SELECT attribute.attnum,
                           attribute.attname,
                           pg_catalog.format_type(
                               attribute.atttypid,
                               attribute.atttypmod
                           ) AS formatted_type,
                           attribute.attnotnull,
                           pg_catalog.pg_get_expr(
                               default_value.adbin,
                               default_value.adrelid
                           ) AS default_expression
                    FROM pg_catalog.pg_attribute AS attribute
                    LEFT JOIN pg_catalog.pg_attrdef AS default_value
                      ON default_value.adrelid = attribute.attrelid
                     AND default_value.adnum = attribute.attnum
                    WHERE attribute.attrelid = 'public.appointments'::regclass
                      AND attribute.attnum > 0
                      AND NOT attribute.attisdropped
                    ORDER BY attribute.attnum
                    """
                )
            )
        )
        constraints = tuple(
            tuple(row)
            for row in connection.execute(
                text(
                    """
                    SELECT constraint_row.conname,
                           constraint_row.contype,
                           constraint_row.convalidated,
                           constraint_row.condeferrable,
                           constraint_row.condeferred,
                           pg_catalog.pg_get_constraintdef(
                               constraint_row.oid,
                               true
                           ) AS definition
                    FROM pg_catalog.pg_constraint AS constraint_row
                    WHERE constraint_row.conrelid =
                          'public.appointments'::regclass
                    ORDER BY constraint_row.conname
                    """
                )
            )
        )
        indexes = tuple(
            tuple(row)
            for row in connection.execute(
                text(
                    """
                    SELECT index_row.indexrelid::regclass::text AS index_name,
                           index_row.indisunique,
                           index_row.indisprimary,
                           index_row.indisexclusion,
                           index_row.indimmediate,
                           index_row.indisvalid,
                           index_row.indisready,
                           access_method.amname,
                           pg_catalog.pg_get_indexdef(
                               index_row.indexrelid
                           ) AS definition
                    FROM pg_catalog.pg_index AS index_row
                    JOIN pg_catalog.pg_class AS index_class
                      ON index_class.oid = index_row.indexrelid
                    JOIN pg_catalog.pg_am AS access_method
                      ON access_method.oid = index_class.relam
                    WHERE index_row.indrelid = 'public.appointments'::regclass
                    ORDER BY index_name
                    """
                )
            )
        )
        exclusion_semantics = tuple(
            tuple(row)
            for row in connection.execute(
                text(
                    """
                    SELECT constraint_row.conname,
                           access_method.amname,
                           constraint_row.contype,
                           constraint_row.convalidated,
                           constraint_row.condeferrable,
                           constraint_row.condeferred,
                           index_row.indisexclusion,
                           index_row.indimmediate,
                           index_row.indisvalid,
                           index_row.indisready,
                           pg_catalog.pg_get_expr(
                               index_row.indpred,
                               index_row.indrelid,
                               true
                           ) AS predicate,
                           pg_catalog.pg_get_expr(
                               index_row.indexprs,
                               index_row.indrelid,
                               true
                           ) AS expressions,
                           (
                               SELECT pg_catalog.string_agg(
                                   operator_row.oprname,
                                   ',' ORDER BY operator_ref.ordinality
                               )
                               FROM pg_catalog.unnest(
                                   constraint_row.conexclop
                               ) WITH ORDINALITY
                                   AS operator_ref(operator_oid, ordinality)
                               JOIN pg_catalog.pg_operator AS operator_row
                                 ON operator_row.oid = operator_ref.operator_oid
                           ) AS operators
                    FROM pg_catalog.pg_constraint AS constraint_row
                    JOIN pg_catalog.pg_index AS index_row
                      ON index_row.indexrelid = constraint_row.conindid
                    JOIN pg_catalog.pg_class AS index_class
                      ON index_class.oid = index_row.indexrelid
                    JOIN pg_catalog.pg_am AS access_method
                      ON access_method.oid = index_class.relam
                    WHERE constraint_row.conrelid =
                          'public.appointments'::regclass
                      AND constraint_row.conname = :owned_exclusion
                    """
                ),
                {"owned_exclusion": EXCLUSION},
            )
        )
        extensions = tuple(
            tuple(row)
            for row in connection.execute(
                text(
                    """
                    SELECT extension.extname,
                           namespace.nspname,
                           extension.extversion
                    FROM pg_catalog.pg_extension AS extension
                    JOIN pg_catalog.pg_namespace AS namespace
                      ON namespace.oid = extension.extnamespace
                    ORDER BY extension.extname
                    """
                )
            )
        )
    return {
        "columns": columns,
        "constraints": constraints,
        "indexes": indexes,
        "exclusion_semantics": exclusion_semantics,
        "extensions": extensions,
    }


def _appointment_rows(observer_engine):
    """Observe every column without driver conversion of extreme timestamps."""
    with observer_engine.connect() as connection:
        return tuple(
            row[0]
            for row in connection.execute(
                text(
                    """
                    SELECT pg_catalog.to_jsonb(appointment_row)::text
                    FROM public.appointments AS appointment_row
                    ORDER BY appointment_row.id
                    """
                )
            )
        )


def _id(label):
    return uuid5(NAMESPACE_URL, "emr4-appointment-migration/" + label)


def _seed_populated_predecessor(admin_engine, legacy_defect=None):
    ids = {
        "p": _id("practice-p"),
        "q": _id("practice-q"),
        "l1": _id("location-p-1"),
        "l2": _id("location-p-2"),
        "lq": _id("location-q"),
        "r": _id("practitioner-p-r"),
        "r2": _id("practitioner-p-r2"),
        "rq": _id("practitioner-q-rq"),
        "a": _id("appointment-a"),
        "b": _id("appointment-b"),
        "c": _id("appointment-c"),
        "d": _id("appointment-d"),
        "e": _id("appointment-e"),
        "f": _id("appointment-f"),
    }
    start = datetime(2027, 4, 5, 0, 0, tzinfo=timezone.utc)

    with admin_engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO public.practices (id, name, timezone)
                VALUES (:p, 'Migration Practice P', 'Australia/Sydney'),
                       (:q, 'Migration Practice Q', 'Australia/Sydney')
                """
            ),
            ids,
        )
        connection.execute(
            text(
                """
                INSERT INTO public.practice_locations (id, practice_id, name)
                VALUES (:l1, :p, 'P One'),
                       (:l2, :p, 'P Two'),
                       (:lq, :q, 'Q One')
                """
            ),
            ids,
        )
        connection.execute(
            text(
                """
                INSERT INTO public.practitioners
                    (id, practice_id, first_name, last_name)
                VALUES (:r, :p, 'Primary', 'Practitioner'),
                       (:r2, :p, 'Second', 'Practitioner'),
                       (:rq, :q, 'Other Tenant', 'Practitioner')
                """
            ),
            ids,
        )

        rows = [
            {
                "id": ids["a"],
                "practice_id": ids["p"],
                "location_id": ids["l1"],
                "practitioner_id": ids["r"],
                "start_time": start,
                "appointment_date": date(2027, 4, 5),
                "start_time_local": datetime_time(10, 0),
                "duration_minutes": 30,
                "status": "Booked",
                "reason": "first blocking row",
            },
            {
                "id": ids["b"],
                "practice_id": ids["p"],
                "location_id": None,
                "practitioner_id": ids["r"],
                "start_time": start + timedelta(minutes=30),
                "appointment_date": date(2027, 4, 5),
                "start_time_local": datetime_time(10, 30),
                "duration_minutes": 30,
                "status": "Confirmed",
                "reason": "half-open adjacent row",
            },
            {
                "id": ids["c"],
                "practice_id": ids["p"],
                "location_id": ids["l2"],
                "practitioner_id": ids["r2"],
                "start_time": start + timedelta(minutes=10),
                "appointment_date": date(2027, 4, 5),
                "start_time_local": datetime_time(10, 10),
                "duration_minutes": 30,
                "status": "Arrived",
                "reason": "different practitioner row",
            },
            {
                "id": ids["d"],
                "practice_id": ids["q"],
                "location_id": ids["lq"],
                "practitioner_id": ids["rq"],
                "start_time": start,
                "appointment_date": date(2027, 4, 5),
                "start_time_local": datetime_time(10, 0),
                "duration_minutes": 30,
                "status": "Completed",
                "reason": "different tenant row",
            },
            {
                "id": ids["e"],
                "practice_id": ids["p"],
                "location_id": ids["l2"],
                "practitioner_id": ids["r"],
                "start_time": start + timedelta(minutes=10),
                "appointment_date": date(2027, 4, 5),
                "start_time_local": datetime_time(10, 10),
                "duration_minutes": 20,
                "status": "Cancelled",
                "reason": "overlapping nonblocking row",
            },
            {
                "id": ids["f"],
                "practice_id": ids["p"],
                "location_id": None,
                "practitioner_id": ids["r"],
                # Replaced below with an ordinary SQL literal because Python's
                # datetime cannot represent PostgreSQL's upper year 294276.
                "start_time": start + timedelta(days=1),
                "appointment_date": date(2027, 4, 6),
                "start_time_local": datetime_time(10, 0),
                "duration_minutes": 1,
                "status": "Cancelled",
                "reason": "finite upper-boundary nonblocking row",
            },
        ]
        connection.execute(
            text(
                """
                INSERT INTO public.appointments
                    (id, practice_id, location_id, practitioner_id,
                     start_time, appointment_date, start_time_local,
                     duration_minutes, status, reason)
                VALUES
                    (:id, :practice_id, :location_id, :practitioner_id,
                     :start_time, :appointment_date, :start_time_local,
                     :duration_minutes, :status, :reason)
                """
            ),
            rows,
        )
        # This finite start plus one minute has a finite end and is a positive
        # control for the all-status endpoint validation in the migration.
        connection.execute(
            text(
                """
                UPDATE public.appointments
                   SET start_time = CAST(
                           '294276-12-31 23:50:00+00'
                           AS timestamptz
                       ),
                       duration_minutes = 1,
                       status = 'Cancelled'
                 WHERE id = :id
                """
            ),
            {"id": ids["f"]},
        )

        if legacy_defect == "overlap":
            connection.execute(
                text(
                    """
                    UPDATE public.appointments
                       SET start_time = :start_time,
                           start_time_local = :start_time_local
                     WHERE id = :id
                    """
                ),
                {
                    "start_time": start + timedelta(minutes=15),
                    "start_time_local": datetime_time(10, 15),
                    "id": ids["b"],
                },
            )
        elif legacy_defect == "duration-null":
            connection.execute(
                text(
                    "UPDATE public.appointments "
                    "SET duration_minutes = NULL WHERE id = :id"
                ),
                {"id": ids["e"]},
            )
        elif legacy_defect == "duration-zero":
            connection.execute(
                text(
                    "UPDATE public.appointments "
                    "SET duration_minutes = 0 WHERE id = :id"
                ),
                {"id": ids["e"]},
            )
        elif legacy_defect == "duration-oversize":
            connection.execute(
                text(
                    "UPDATE public.appointments "
                    "SET duration_minutes = 481 WHERE id = :id"
                ),
                {"id": ids["e"]},
            )
        elif legacy_defect == "status-null":
            connection.execute(
                text(
                    "UPDATE public.appointments SET status = NULL WHERE id = :id"
                ),
                {"id": ids["e"]},
            )
        elif legacy_defect == "start-infinity":
            connection.execute(
                text(
                    "UPDATE public.appointments "
                    "SET start_time = CAST('infinity' AS timestamptz) "
                    "WHERE id = :id"
                ),
                {"id": ids["e"]},
            )
        elif legacy_defect == "nonblocking-end-overflow":
            connection.execute(
                text(
                    """
                    UPDATE public.appointments
                       SET duration_minutes = 30
                     WHERE id = :id
                    """
                ),
                {"id": ids["f"]},
            )
        else:
            assert legacy_defect is None

    return ids


def _constraint_map(catalogue):
    return {row[0]: row for row in catalogue["constraints"]}


def _column_map(catalogue):
    return {row[1]: row for row in catalogue["columns"]}


def _unqualified_identifier(identifier):
    return identifier.rsplit(".", 1)[-1].strip('"')


def _index_map(catalogue):
    return {
        _unqualified_identifier(row[0]): row
        for row in catalogue["indexes"]
    }


def _assert_utc_minute_end_expression(definition):
    normalized = " ".join(definition.lower().split())
    assert "start_time" in normalized
    assert "duration_minutes" in normalized
    assert len(re.findall(r"\bat\s+time\s+zone\b", normalized)) == 2
    assert len(re.findall(r"'utc'(?:\s*::\s*text)?", normalized)) == 2
    interval_literals = {
        literal.lower()
        for literal in re.findall(
            r"'([^']+)'\s*::\s*interval",
            normalized,
        )
    }
    assert interval_literals & {"00:01:00", "00:01", "1 min", "1 minute"}


def _assert_candidate_catalogue(catalogue):
    constraints = _constraint_map(catalogue)
    assert OWNED_CONSTRAINTS <= constraints.keys()

    duration = constraints[DURATION_CHECK]
    assert duration[1] == "c"
    assert duration[2] is True
    assert duration[3] is False
    assert duration[4] is False
    assert "duration_minutes >= 1" in duration[5]
    assert "duration_minutes <= 480" in duration[5]

    finite_start = constraints[FINITE_START_CHECK]
    assert finite_start[1] == "c"
    assert finite_start[2] is True
    assert finite_start[3] is False
    assert finite_start[4] is False
    assert "isfinite(start_time)" in finite_start[5]

    finite_end = constraints[FINITE_END_CHECK]
    assert finite_end[1] == "c"
    assert finite_end[2] is True
    assert finite_end[3] is False
    assert finite_end[4] is False
    assert "isfinite" in finite_end[5]
    assert "status" not in finite_end[5].lower()
    _assert_utc_minute_end_expression(finite_end[5])

    exclusion = constraints[EXCLUSION]
    assert exclusion[1] == "x"
    assert exclusion[2] is True
    assert exclusion[3] is False
    assert exclusion[4] is False
    exclusion_definition = " ".join(exclusion[5].lower().split())
    assert "exclude using gist" in exclusion_definition
    assert "practice_id with =" in exclusion_definition
    assert "practitioner_id with =" in exclusion_definition
    assert "tstzrange" in exclusion_definition
    assert "with &&" in exclusion_definition
    assert "'[)'" in exclusion_definition
    blocking_statuses = {
        "booked",
        "confirmed",
        "arrived",
        "inconsult",
        "completed",
    }
    for blocking_status in blocking_statuses:
        assert blocking_status in exclusion_definition
    for nonblocking_status in {"cancelled", "noshow", "dna"}:
        assert nonblocking_status not in exclusion_definition
    for forbidden_coordinate in {
        "location_id",
        "appointment_date",
        "start_time_local",
    }:
        assert forbidden_coordinate not in exclusion_definition

    indexes = _index_map(catalogue)
    assert EXCLUSION in indexes
    owned_index = indexes[EXCLUSION]
    assert owned_index[1] is False  # indisunique
    assert owned_index[2] is False  # indisprimary
    assert owned_index[3] is True   # indisexclusion
    assert owned_index[4] is True   # indimmediate
    assert owned_index[5] is True   # indisvalid
    assert owned_index[6] is True   # indisready
    assert owned_index[7] == "gist"

    assert len(catalogue["exclusion_semantics"]) == 1
    semantic = catalogue["exclusion_semantics"][0]
    assert semantic[0] == EXCLUSION
    assert semantic[1] == "gist"
    assert semantic[2] == "x"
    assert semantic[3] is True      # convalidated
    assert semantic[4] is False     # condeferrable
    assert semantic[5] is False     # condeferred
    assert semantic[6] is True      # indisexclusion
    assert semantic[7] is True      # indimmediate
    assert semantic[8] is True      # indisvalid
    assert semantic[9] is True      # indisready
    assert semantic[12] == "=,=,&&"

    predicate = " ".join(semantic[10].split())
    expressions = " ".join(semantic[11].split())
    predicate_statuses = {
        literal.lower()
        for literal in re.findall(r"'([^']+)'", predicate)
    }
    assert predicate_statuses == blocking_statuses

    expressions_lower = expressions.lower()
    assert "tstzrange" in expressions_lower
    assert re.search(r"tstzrange\s*\(\s*start_time\s*,", expressions_lower)
    assert "'[)'" in expressions_lower
    _assert_utc_minute_end_expression(expressions_lower)

    complete_owned_definition = " ".join(
        (exclusion_definition, predicate.lower(), expressions_lower)
    )
    for forbidden_coordinate in {
        "location_id",
        "appointment_date",
        "start_time_local",
    }:
        assert forbidden_coordinate not in complete_owned_definition
    for nonblocking_status in {"cancelled", "noshow", "dna"}:
        assert nonblocking_status not in predicate.lower()

    columns = _column_map(catalogue)
    assert columns["duration_minutes"][3] is True
    assert columns["status"][3] is True
    assert any(
        name == "btree_gist" and schema == "public"
        for name, schema, _version in catalogue["extensions"]
    )


@pytest.mark.parametrize(
    "_apt_mig_case",
    [pytest.param(None, id="APT-MIG-upgrade-populated")],
)
def test_apt_migration_populated_upgrade_installs_exact_protections_and_keeps_rows(
    appointment_migration_runtime,
    _apt_mig_case,
):
    runtime = _runtime(appointment_migration_runtime)
    assert _revision(runtime["observer_engine"]) == PREDECESSOR
    _seed_populated_predecessor(runtime["admin_engine"])

    before_rows = _appointment_rows(runtime["observer_engine"])
    before_catalogue = _catalogue(runtime["observer_engine"])
    assert len(before_rows) == 6
    assert OWNED_CONSTRAINTS.isdisjoint(_constraint_map(before_catalogue))

    result = runtime["migrate"]("upgrade", CANDIDATE)
    _assert_migration_succeeded(result)

    assert _revision(runtime["observer_engine"]) == CANDIDATE
    assert _appointment_rows(runtime["observer_engine"]) == before_rows
    _assert_candidate_catalogue(_catalogue(runtime["observer_engine"]))


@pytest.mark.parametrize(
    ("legacy_defect", "expected_reason"),
    [
        (
            "overlap",
            "existing blocking appointments overlap for a practice and practitioner",
        ),
        (
            "duration-null",
            "appointments contain null, infinite, or invalid scheduling values",
        ),
        (
            "duration-zero",
            "appointments contain null, infinite, or invalid scheduling values",
        ),
        (
            "duration-oversize",
            "appointments contain null, infinite, or invalid scheduling values",
        ),
        (
            "status-null",
            "appointments contain null, infinite, or invalid scheduling values",
        ),
        (
            "start-infinity",
            "appointments contain null, infinite, or invalid scheduling values",
        ),
        (
            "nonblocking-end-overflow",
            "appointment duration produces an out-of-range end instant",
        ),
    ],
    ids=[
        "APT-MIG-refuse-overlap",
        "APT-MIG-refuse-null-duration",
        "APT-MIG-refuse-zero-duration",
        "APT-MIG-refuse-oversize-duration",
        "APT-MIG-refuse-null-status",
        "APT-MIG-refuse-infinite-start",
        "APT-MIG-refuse-nonblocking-end-overflow",
    ],
)
def test_apt_migration_refuses_populated_invalid_predecessor_atomically(
    appointment_migration_runtime,
    legacy_defect,
    expected_reason,
):
    runtime = _runtime(appointment_migration_runtime)
    assert _revision(runtime["observer_engine"]) == PREDECESSOR
    _seed_populated_predecessor(runtime["admin_engine"], legacy_defect)

    before_rows = _appointment_rows(runtime["observer_engine"])
    before_catalogue = _catalogue(runtime["observer_engine"])
    assert len(before_rows) == 6

    # Exactly one migration attempt: failure is observed, never retried.
    result = runtime["migrate"]("upgrade", CANDIDATE)
    _assert_migration_refused(result, expected_reason)

    assert _revision(runtime["observer_engine"]) == PREDECESSOR
    assert _appointment_rows(runtime["observer_engine"]) == before_rows
    assert _catalogue(runtime["observer_engine"]) == before_catalogue


@pytest.mark.parametrize(
    "_apt_mig_case",
    [pytest.param(None, id="APT-MIG-down-up-preserves")],
)
def test_apt_migration_down_then_up_removes_only_owned_protections_and_keeps_rows(
    appointment_migration_runtime,
    _apt_mig_case,
):
    runtime = _runtime(appointment_migration_runtime)
    assert _revision(runtime["observer_engine"]) == PREDECESSOR
    _seed_populated_predecessor(runtime["admin_engine"])

    predecessor_rows = _appointment_rows(runtime["observer_engine"])
    predecessor_catalogue = _catalogue(runtime["observer_engine"])
    assert len(predecessor_rows) == 6

    first_upgrade = runtime["migrate"]("upgrade", CANDIDATE)
    _assert_migration_succeeded(first_upgrade)
    assert _revision(runtime["observer_engine"]) == CANDIDATE
    first_candidate_rows = _appointment_rows(runtime["observer_engine"])
    first_candidate_catalogue = _catalogue(runtime["observer_engine"])
    assert first_candidate_rows == predecessor_rows
    _assert_candidate_catalogue(first_candidate_catalogue)

    downgrade = runtime["migrate"]("downgrade", PREDECESSOR)
    _assert_migration_succeeded(downgrade)
    assert _revision(runtime["observer_engine"]) == PREDECESSOR
    assert _appointment_rows(runtime["observer_engine"]) == predecessor_rows

    downgraded_catalogue = _catalogue(runtime["observer_engine"])
    assert downgraded_catalogue["columns"] == predecessor_catalogue["columns"]
    assert downgraded_catalogue["constraints"] == predecessor_catalogue["constraints"]
    assert downgraded_catalogue["indexes"] == predecessor_catalogue["indexes"]
    assert OWNED_CONSTRAINTS.isdisjoint(_constraint_map(downgraded_catalogue))
    assert any(
        name == "btree_gist" and schema == "public"
        for name, schema, _version in downgraded_catalogue["extensions"]
    )
    predecessor_extensions = {
        row[0]: row for row in predecessor_catalogue["extensions"]
    }
    downgraded_extensions = {
        row[0]: row for row in downgraded_catalogue["extensions"]
    }
    assert {
        name: downgraded_extensions.get(name)
        for name in predecessor_extensions
    } == predecessor_extensions
    assert downgraded_extensions.keys() - predecessor_extensions.keys() <= {
        "btree_gist"
    }

    second_upgrade = runtime["migrate"]("upgrade", CANDIDATE)
    _assert_migration_succeeded(second_upgrade)
    assert _revision(runtime["observer_engine"]) == CANDIDATE
    assert _appointment_rows(runtime["observer_engine"]) == predecessor_rows
    second_candidate_catalogue = _catalogue(runtime["observer_engine"])
    _assert_candidate_catalogue(second_candidate_catalogue)
    assert second_candidate_catalogue == first_candidate_catalogue


@pytest.mark.parametrize("_case", [pytest.param(None, id="APT-MIG-head-catalogue")])
def test_apt_migration_actual_application_database_has_candidate_catalogue(runtime_binding, _case):
    _assert_candidate_catalogue(_catalogue(runtime_binding.observer_engine))


from app.models.appointments import Appointment as AppointmentModel


DST_ELAPSED_INTERVALS = [
    pytest.param("2027-10-03T01:45:00+10:00", "2027-10-02T16:15:00+00:00",
        "2027-10-03T03:15:00+11:00", id="spring-forward"),
    pytest.param("2027-04-04T02:45:00+11:00", "2027-04-03T16:15:00+00:00",
        "2027-04-04T02:15:00+10:00", id="fall-back"),
]


@pytest.mark.parametrize("encoded_start,encoded_end,local_end", DST_ELAPSED_INTERVALS)
def test_apt_elapsed_focused_model_endpoint_crosses_offset_transition(
    encoded_start, encoded_end, local_end,
):
    """Focused ORM property proof; no persistence or HTTP claim for this case."""
    zone = ZoneInfo("Australia/Sydney")
    start = datetime.fromisoformat(encoded_start).astimezone(zone)
    expected_end = datetime.fromisoformat(encoded_end)
    assert isinstance(start.tzinfo, ZoneInfo), "fixed-offset inputs would hide model wall-time arithmetic"
    assert expected_end == _utc(start) + timedelta(minutes=30)
    appointment = AppointmentModel(start_time=start, duration_minutes=30)
    actual_end = appointment.end_time
    assert _utc(actual_end) == expected_end
    assert actual_end.astimezone(zone).isoformat() == local_end
    assert actual_end.utcoffset() != start.utcoffset()


@pytest.mark.parametrize("encoded_start,encoded_end,local_end", DST_ELAPSED_INTERVALS)
@pytest.mark.parametrize("family", [
    pytest.param("raw", id="raw"), pytest.param("confirmed", id="confirmed"),
])
def test_apt_elapsed_actual_http_endpoint_crosses_offset_transition(
    appointment_http_client, case_world, family, encoded_start, encoded_end, local_end,
):
    client, headers = appointment_http_client
    case_world.set_timezone("Australia/Sydney")
    start = datetime.fromisoformat(encoded_start).astimezone(ZoneInfo("Australia/Sydney"))
    expected_end = datetime.fromisoformat(encoded_end)
    assert expected_end == _utc(start) + timedelta(minutes=30)
    if family == "raw":
        appointment = _raw_create_success(client, headers, case_world,
            patient_label="Synthetic Elapsed DST Raw", start=start, minutes=30,
            location_id=case_world.l1)
    else:
        before = case_world.snapshot()
        proposal, confirmation = _staff_create_proposal(client, headers, case_world,
            start=start, location_id=case_world.l1, proposal_key="dst-endpoint-proposal",
            patient_label="Synthetic Elapsed DST Confirm", minutes=30)
        assert case_world.snapshot() == before
        confirmation["confirmed"] = True
        confirmed = _confirm_create(client, headers, proposal["confirm_endpoint"],
            "dst-endpoint-confirm", confirmation)
        assert confirmed.status_code == 200
        _assert_confirmed_create_confirmation(confirmed.json(), start)
        appointment = confirmed.json()["appointment"]
    assert _utc(_parse_api_datetime(appointment["start_time"])) == _utc(start)
    actual_end = _parse_api_datetime(appointment["end_time"])
    assert _utc(actual_end) == expected_end
    assert actual_end.astimezone(ZoneInfo("Australia/Sydney")).isoformat() == local_end
    with case_world.writer() as reader:
        stored = reader.get(UUID(appointment["id"]))
    assert _utc(stored["start_time"]) + timedelta(minutes=stored["duration_minutes"]) == expected_end


def _elapsed_create_body(world, practitioner):
    return {
        "patient_name_provisional": "Synthetic Elapsed Window",
        "practitioner_id": str(practitioner), "location_id": str(world.l1),
        "start_time": world.start.isoformat(), "duration_minutes": 15,
    }


def _elapsed_safe_proposal(client, headers, endpoint, payload, key):
    response = client.post(endpoint, headers=_confirmation_key_headers(headers, key), json=payload)
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["safe"] is True and proposal["blocks"] == []
    assert proposal["requires_confirmation"] is True
    assert proposal["signed_confirmation_evidence_required"] is True
    assert proposal["signed_confirmation_evidence"]
    confirmation = deepcopy(proposal["confirm_payload"])
    assert confirmation["confirmed"] is False
    confirmation["confirmed"] = True
    return proposal, confirmation


@pytest.mark.parametrize("family", [
    pytest.param("raw-create", id="raw-create"),
    pytest.param("create-proposal", id="create-proposal"),
    pytest.param("create-confirm", id="create-confirm"),
    pytest.param("raw-update", id="raw-update"),
    pytest.param("update-proposal", id="update-proposal"),
    pytest.param("update-confirm", id="update-confirm"),
])
@pytest.mark.parametrize("past_end_seconds", [
    pytest.param(0, id="end-equals-now"), pytest.param(1, id="end-before-now"),
])
def test_apt_elapsed_same_day_window_rejects_at_and_after_end(
    appointment_http_client, case_world, monkeypatch, family, past_end_seconds,
):
    client, headers = appointment_http_client
    expected_end = _utc(case_world.start) + timedelta(minutes=15)
    before_end = expected_end - timedelta(seconds=1)
    after_end = expected_end + timedelta(seconds=past_end_seconds)
    assert before_end.date() == after_end.date() == case_world.start.date()
    target = None
    secondary = None
    if "update" in family:
        target = case_world.row("elapsed-update-control", start=case_world.start, minutes=30, location_id=case_world.l1)
        _insert_and_commit(case_world, target)
        if family == "update-confirm":
            secondary = case_world.row("elapsed-update-pending", practitioner_id=case_world.r2,
                start=case_world.start, minutes=30, location_id=case_world.l2)
            _insert_and_commit(case_world, secondary)
    with monkeypatch.context() as clinic_clock:
        clinic_clock.setattr(appointment_routes, "_clinic_local_now", lambda zone: before_end.astimezone(zone))
        if family == "raw-create":
            valid = client.post(RAW_CREATE_ENDPOINT, headers=headers, json=_elapsed_create_body(case_world, case_world.r))
            assert valid.status_code == 201
            assert _utc(_parse_api_datetime(valid.json()["end_time"])) == expected_end
        elif family == "create-proposal":
            _elapsed_safe_proposal(client, headers, CREATE_PROPOSAL_ENDPOINT,
                _elapsed_create_body(case_world, case_world.r), "elapsed-create-proposal-control")
        elif family == "create-confirm":
            proposal, confirmation = _elapsed_safe_proposal(client, headers, CREATE_PROPOSAL_ENDPOINT,
                _elapsed_create_body(case_world, case_world.r), "elapsed-create-control-proposal")
            valid = _confirm_create(client, headers, proposal["confirm_endpoint"], "elapsed-create-control-confirm", confirmation)
            assert valid.status_code == 200
            _assert_confirmed_create_confirmation(valid.json(), case_world.start)
            pending_proposal, pending_confirmation = _elapsed_safe_proposal(client, headers, CREATE_PROPOSAL_ENDPOINT,
                _elapsed_create_body(case_world, case_world.r2), "elapsed-create-pending-proposal")
        elif family == "raw-update":
            valid = client.put(f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}", headers=headers, json={"duration_minutes": 15})
            assert valid.status_code == 200
            assert valid.json()["duration_minutes"] == 15
            assert _utc(_parse_api_datetime(valid.json()["end_time"])) == expected_end
        elif family == "update-proposal":
            _elapsed_safe_proposal(client, headers, f"{UPDATE_PROPOSAL_ENDPOINT}/{target['id']}",
                {"duration_minutes": 15}, "elapsed-update-proposal-control")
        else:
            proposal, confirmation = _elapsed_safe_proposal(client, headers, f"{UPDATE_PROPOSAL_ENDPOINT}/{target['id']}",
                {"duration_minutes": 15}, "elapsed-update-control-proposal")
            valid = _confirm_update(client, headers, "elapsed-update-control-confirm", confirmation)
            assert valid.status_code == 200
            _assert_confirmed_update(valid.json())
            pending_proposal, pending_confirmation = _elapsed_safe_proposal(client, headers,
                f"{UPDATE_PROPOSAL_ENDPOINT}/{secondary['id']}", {"duration_minutes": 15}, "elapsed-update-pending-proposal")
        before_rejection = case_world.snapshot()
        clinic_clock.setattr(appointment_routes, "_clinic_local_now", lambda zone: after_end.astimezone(zone))
        if family == "raw-create":
            rejected = client.post(RAW_CREATE_ENDPOINT, headers=headers, json=_elapsed_create_body(case_world, case_world.r2))
        elif family == "create-proposal":
            rejected = client.post(CREATE_PROPOSAL_ENDPOINT,
                headers=_confirmation_key_headers(headers, "elapsed-create-proposal-reject"), json=_elapsed_create_body(case_world, case_world.r))
        elif family == "create-confirm":
            rejected = _confirm_create(client, headers, pending_proposal["confirm_endpoint"], "elapsed-create-pending-confirm", pending_confirmation)
        elif family == "raw-update":
            rejected = client.put(f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}", headers=headers, json={"duration_minutes": 15})
        elif family == "update-proposal":
            rejected = client.post(f"{UPDATE_PROPOSAL_ENDPOINT}/{target['id']}",
                headers=_confirmation_key_headers(headers, "elapsed-update-proposal-reject"), json={"duration_minutes": 15})
        else:
            rejected = _confirm_update(client, headers, "elapsed-update-pending-confirm", pending_confirmation)
        if family.startswith("raw-"):
            assert rejected.status_code == 422
            assert rejected.json() == {"detail": {"code": "same_day_window_elapsed", "message": "Same-day appointment window has already elapsed."}}
        else:
            assert rejected.status_code == 200
            body = rejected.json()
            assert body["safe"] is False and body["requires_confirmation"] is True
            assert body["autonomy_tier"] == "blocked"
            if family.endswith("confirm"):
                assert body["appointment"] is None
                expected_wrapper = "create_proposal_revalidation_blocked" if family == "create-confirm" else "update_proposal_revalidation_blocked"
                assert [item["code"] for item in body["blocks"]] == [expected_wrapper, "same_day_window_elapsed"]
            else:
                assert body["blocks"][0]["code"] == "same_day_window_elapsed"
        assert case_world.snapshot() == before_rejection


# Late actual public transactions: independently authored fragment d045de17.
LATE_COLLISION_FAMILIES = ("raw-create", "confirmed-create", "raw-update")


@contextmanager
def _observe_late_collision_transaction(engine):
    """Bind one physical engine error to the exact ORM Session that received it."""
    state = {
        "lock": threading.Lock(),
        "bindings": [],
        "collision_sessions": [],
        "unmapped_diagnostics": 0,
        "diagnostics": [],
        "physical_rollbacks": 0,
        "soft_rollback_parents": [],
        "events": [],
    }

    def after_begin(session, transaction, connection):
        if session.get_bind() is not engine:
            return
        with state["lock"]:
            state["bindings"].append((connection, session))

    def handle_error(context):
        original = context.original_exception
        diagnostic = (
            getattr(original, "sqlstate", None)
            or getattr(original, "pgcode", None),
            getattr(getattr(original, "diag", None), "constraint_name", None),
        )
        with state["lock"]:
            collision_session = None
            for connection, session in reversed(state["bindings"]):
                if connection is context.connection:
                    collision_session = session
                    break
            if collision_session is None:
                state["unmapped_diagnostics"] += 1
            state["collision_sessions"].append(collision_session)
            # Retain only bounded typed diagnostics.  Do not retain SQL,
            # parameters, DBAPI messages, JWTs or connection metadata.
            state["diagnostics"].append(diagnostic)
            state["events"].append(("handle_error", diagnostic))

    def after_rollback(session):
        with state["lock"]:
            if any(session is candidate for candidate in state["collision_sessions"]):
                state["physical_rollbacks"] += 1
                state["events"].append(("after_rollback",))

    def after_soft_rollback(session, previous_transaction):
        with state["lock"]:
            if any(session is candidate for candidate in state["collision_sessions"]):
                has_parent = previous_transaction.parent is not None
                state["soft_rollback_parents"].append(has_parent)
                state["events"].append(("after_soft_rollback", has_parent))

    listeners = (
        (Session, "after_begin", after_begin),
        (engine, "handle_error", handle_error),
        (Session, "after_rollback", after_rollback),
        (Session, "after_soft_rollback", after_soft_rollback),
    )
    for target, name, listener in listeners:
        event.listen(target, name, listener)
    try:
        yield state
    finally:
        for target, name, listener in reversed(listeners):
            event.remove(target, name, listener)
        with state["lock"]:
            state["bindings"].clear()
            state["collision_sessions"].clear()


def _late_collision_request(client, headers, case_world, family):
    assert family in LATE_COLLISION_FAMILIES
    loser_start = case_world.start + timedelta(minutes=15)
    target = None

    if family == "raw-create":
        payload = {
            "patient_name_provisional": "Synthetic Late Raw Create Loser",
            "practitioner_id": str(case_world.r),
            "location_id": str(case_world.l1),
            "start_time": loser_start.isoformat(),
            "duration_minutes": 30,
        }

        def call():
            return client.post(RAW_APPOINTMENTS_ENDPOINT, headers=headers, json=payload)

    elif family == "confirmed-create":
        before_proposal = case_world.snapshot()
        proposal, confirmation = _staff_create_proposal(
            client,
            headers,
            case_world,
            start=loser_start,
            location_id=case_world.l1,
            proposal_key="apt-late-confirmed-create-proposal",
            patient_label="Synthetic Late Confirmed Create Loser",
        )
        assert case_world.snapshot() == before_proposal
        confirmation["confirmed"] = True

        def call():
            return _confirm_create(
                client,
                headers,
                proposal["confirm_endpoint"],
                "apt-late-confirmed-create-confirm",
                confirmation,
            )

    else:
        target = case_world.row(
            "late-raw-update-target",
            location_id=case_world.l2,
            start=case_world.start + timedelta(minutes=60),
        )
        assert target["appointment_state_version"] == 1
        _insert_and_commit(case_world, target)
        payload = {
            "start_time": loser_start.isoformat(),
            "location_id": None,
            "reason": "Synthetic late raw update",
        }

        def call():
            return client.put(
                f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}",
                headers=headers,
                json=payload,
            )

    return call, loser_start, target


def _mark_late_collision_response(call, transaction_state):
    response = call()
    with transaction_state["lock"]:
        transaction_state["events"].append(("response", response.status_code))
    return response


def _assert_late_collision_transaction_observation(
    transaction_state,
    *,
    family,
    winner_outcome,
    response_status,
):
    with transaction_state["lock"]:
        diagnostics = tuple(transaction_state["diagnostics"])
        unmapped = transaction_state["unmapped_diagnostics"]
        physical_rollbacks = transaction_state["physical_rollbacks"]
        soft_parents = tuple(transaction_state["soft_rollback_parents"])
        events = tuple(transaction_state["events"])

    if winner_outcome == "rollback":
        assert diagnostics == (), "a rolled-back winner must not create a hidden retry"
        assert unmapped == 0
        assert physical_rollbacks == 0
        assert soft_parents == ()
        assert events == (("response", response_status),)
        return

    diagnostic = ("23P01", COLLISION_CONSTRAINT)
    assert diagnostics == (diagnostic,), "the product must attempt the losing write once"
    assert unmapped == 0, "the physical collision was not bound to its exact Session"
    assert physical_rollbacks == 1, "the collision Session did not issue one DBAPI rollback"
    # SQLAlchemy 2.0.50 rolls back the failed flush subtransaction first.  The
    # create/update helper then explicitly rolls back the inactive root. Raw
    # create returns through its router; confirmed create's outer catch calls
    # rollback again after the root has closed, which emits no extra soft event.
    assert soft_parents == (True, False)
    expected_events = (
        ("handle_error", diagnostic),
        ("after_rollback",),
        ("after_soft_rollback", True),
        ("after_soft_rollback", False),
        ("response", response_status),
    )
    assert events == expected_events
    if family == "confirmed-create":
        assert response_status == 200
    else:
        assert response_status == 409


def _assert_late_collision_winner_only(case_world, before, after, winner, target):
    appointments = _snapshot_rows(after, "appointments")
    appointment_ids = {row["id"] for row in appointments}
    expected_ids = {str(winner["id"])}
    if target is not None:
        expected_ids.add(str(target["id"]))
        original_target = _snapshot_row(before, "appointments", target["id"])
        assert original_target["appointment_state_version"] == 1
        assert _snapshot_row(after, "appointments", target["id"]) == original_target
    assert appointment_ids == expected_ids
    stored_winner = _snapshot_row(after, "appointments", winner["id"])
    assert stored_winner["status"] == "Booked"
    assert stored_winner["appointment_state_version"] == 1
    assert after["appointment_audit_log"] == before["appointment_audit_log"]
    assert after["appointment_command_idempotency"] == before[
        "appointment_command_idempotency"
    ]


def _assert_late_collision_success_graph(
    case_world,
    family,
    response,
    loser_start,
    target,
    winner,
):
    after = case_world.snapshot()
    appointments = _snapshot_rows(after, "appointments")
    audits = _snapshot_rows(after, "appointment_audit_log")
    receipts = _snapshot_rows(after, "appointment_command_idempotency")
    assert str(winner["id"]) not in {row["id"] for row in appointments}

    body = response.json()
    if family == "raw-create":
        assert response.status_code == 201
        assert body["status"] == "Booked"
        assert body["practitioner_id"] == str(case_world.r)
        assert body["location_id"] == str(case_world.l1)
        assert _raw_utc(_raw_parse_datetime(body["start_time"])) == _raw_utc(loser_start)
        assert len(appointments) == len(audits) == 1
        assert receipts == []
        assert appointments[0]["id"] == body["id"]
        assert appointments[0]["appointment_state_version"] == 1
        assert appointments[0]["practitioner_id"] == str(case_world.r)
        assert appointments[0]["location_id"] == str(case_world.l1)
        assert _raw_utc(_raw_parse_datetime(appointments[0]["start_time"])) == _raw_utc(loser_start)
        assert audits[0]["appointment_id"] == body["id"]
        assert audits[0]["action"] == "create"
        assert audits[0]["command_id"] is None
        return

    if family == "confirmed-create":
        assert response.status_code == 200
        _assert_confirmed_create_confirmation(body, loser_start)
        assert len(appointments) == len(audits) == len(receipts) == 1
        appointment = appointments[0]
        audit = audits[0]
        receipt = receipts[0]
        assert appointment["id"] == body["appointment"]["id"]
        assert appointment["appointment_state_version"] == 1
        assert appointment["practitioner_id"] == str(case_world.r)
        assert appointment["location_id"] == str(case_world.l1)
        assert _raw_utc(_raw_parse_datetime(appointment["start_time"])) == _raw_utc(loser_start)
        assert audit["action"] == "create"
        assert audit["appointment_id"] == appointment["id"]
        assert audit["command_id"] == receipt["id"]
        assert receipt["operation_id"] == "confirmAppointmentCreateProposal"
        assert receipt["state"] == "completed"
        assert receipt["result_kind"] == "confirmed_write"
        assert receipt["target_appointment_id"] == appointment["id"]
        assert receipt["audit_log_id"] == audit["id"]
        public_receipt = body["confirmation_receipt"]
        assert public_receipt["appointment_id"] == appointment["id"]
        assert public_receipt["correlation_id"] == receipt["id"]
        assert public_receipt["audit_event_id"] == audit["id"]
        return

    assert family == "raw-update"
    assert response.status_code == 200
    assert target is not None
    assert body["id"] == str(target["id"])
    assert body["reason"] == "Synthetic late raw update"
    assert body["location_id"] is None
    assert _raw_utc(_raw_parse_datetime(body["start_time"])) == _raw_utc(loser_start)
    assert len(appointments) == len(audits) == 1
    assert receipts == []
    assert appointments[0]["id"] == str(target["id"])
    assert appointments[0]["location_id"] is None
    assert appointments[0]["reason"] == "Synthetic late raw update"
    assert appointments[0]["practitioner_id"] == str(case_world.r)
    assert _raw_utc(_raw_parse_datetime(appointments[0]["start_time"])) == _raw_utc(loser_start)
    assert appointments[0]["appointment_state_version"] == (
        target["appointment_state_version"] + 1
    )
    assert audits[0]["appointment_id"] == str(target["id"])
    assert audits[0]["action"] == "update"
    assert audits[0]["command_id"] is None


@pytest.mark.parametrize(
    "family,winner_outcome",
    [
        pytest.param("raw-create", "commit", id="APT-LATE-http-raw-create-winner-commit"),
        pytest.param("raw-create", "rollback", id="APT-LATE-http-raw-create-winner-rollback"),
        pytest.param(
            "confirmed-create",
            "commit",
            id="APT-LATE-http-confirmed-create-winner-commit",
        ),
        pytest.param(
            "confirmed-create",
            "rollback",
            id="APT-LATE-http-confirmed-create-winner-rollback",
        ),
        pytest.param("raw-update", "commit", id="APT-LATE-http-raw-update-winner-commit"),
        pytest.param(
            "raw-update",
            "rollback",
            id="APT-LATE-http-raw-update-winner-rollback",
        ),
    ],
)
def test_late_http_collision_reaches_real_exclusion_transaction(
    appointment_http_client,
    case_world,
    family,
    winner_outcome,
):
    client, headers = appointment_http_client
    call, loser_start, target = _late_collision_request(
        client, headers, case_world, family
    )
    before = case_world.snapshot()
    winner = case_world.row(
        "late-uncommitted-winner",
        location_id=case_world.l2,
        start=case_world.start,
    )
    assert winner["appointment_state_version"] == 1

    with _observe_late_collision_transaction(
        case_world.runtime.engine
    ) as transaction_state:
        with case_world.writer() as blocker:
            blocker.insert(winner)
            result, finished, thread, deadline = _start_http(
                lambda: _mark_late_collision_response(call, transaction_state),
                case_world,
            )
            try:
                assert thread.daemon is False
                observation_deadline = deadline - case_world.runtime.wait_timeout_seconds
                waiting_pid = _observe_application_wait_for_blocker(
                    case_world,
                    blocker.pid,
                    finished,
                    deadline=observation_deadline,
                )
                assert waiting_pid != blocker.pid
                assert not finished.is_set(), (
                    "the losing request must remain pending on the observed database blocker"
                )
                if winner_outcome == "commit":
                    blocker.commit()
                else:
                    blocker.rollback()
            finally:
                # Release the real lock even when observation or outcome checks
                # fail, then spend only the original request deadline on closure.
                blocker.rollback()
                _join_http(result, finished, thread, deadline)

    assert "error" not in result
    response = result["response"]
    _assert_late_collision_transaction_observation(
        transaction_state,
        family=family,
        winner_outcome=winner_outcome,
        response_status=response.status_code,
    )

    if winner_outcome == "commit":
        after = case_world.snapshot()
        if family == "confirmed-create":
            assert response.status_code == 200
            body = response.json()
            _assert_blocked_create_confirmation(body)
            conflict = {
                "code": "appointment_conflict",
                "severity": "blocked",
                "message": "This appointment overlaps an existing booking.",
            }
            assert body["blocks"][0] == conflict
            assert body["blocks"] == [conflict]
            assert body["audit_evidence"] == STAFF_CREATE_AUDIT_EVIDENCE
        else:
            rendered_winner = {
                "id": str(winner["id"]),
                "start_time": winner["start_time"].isoformat(),
                "duration_minutes": winner["duration_minutes"],
            }
            _assert_raw_collision(response, rendered_winner)
            assert response.json() == {
                "detail": {
                    "code": RAW_CONFLICT_CODE,
                    "message": RAW_CONFLICT_MESSAGE,
                }
            }
        _assert_late_collision_winner_only(
            case_world, before, after, winner, target
        )
        return

    _assert_late_collision_success_graph(
        case_world,
        family,
        response,
        loser_start,
        target,
        winner,
    )


# Unrelated integrity mapping: independently reviewed fragment 735fe2b1.
from types import SimpleNamespace

import pytest
from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointments import Appointment


REAL_UNRELATED_SQLSTATE = "23514"
REAL_UNRELATED_CONSTRAINT = "ck_appointments_duration_minutes_1_480"
SYNTHETIC_WRONG_EXCLUSION = "ex_synthetic_unrelated_resource_no_overlap"


def _integrity_pair(error):
    """Read public DBAPI diagnostics without using the product classifier."""
    assert isinstance(error, IntegrityError)
    original = error.orig
    return (
        getattr(original, "sqlstate", None)
        or getattr(original, "pgcode", None),
        getattr(getattr(original, "diag", None), "constraint_name", None),
    )


def _marked_pending_create(
    session,
    case_world,
    *,
    patient_label,
    expected_start,
    expected_practitioner,
    expected_location,
):
    """Return only the exact create targeted by this case's event seam."""
    if session.get_bind() is not case_world.runtime.engine:
        return None
    candidates = [
        candidate
        for candidate in session.new
        if isinstance(candidate, Appointment)
        and candidate.practice_id == case_world.p
        and candidate.patient_name_provisional == patient_label
    ]
    if not candidates:
        return None
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.practitioner_id == expected_practitioner
    assert candidate.location_id == expected_location
    assert candidate.duration_minutes == 30
    assert _raw_utc(candidate.start_time) == _raw_utc(expected_start)
    return candidate


def _raw_create_request(
    client,
    headers,
    case_world,
    *,
    patient_label,
    start,
    practitioner_id,
    location_id,
):
    return client.post(
        RAW_APPOINTMENTS_ENDPOINT,
        headers=headers,
        json={
            "patient_name_provisional": patient_label,
            "practitioner_id": str(practitioner_id),
            "location_id": None if location_id is None else str(location_id),
            "start_time": start.isoformat(),
            "duration_minutes": 30,
        },
    )


@pytest.mark.parametrize(
    "_case",
    [pytest.param(None, id="APT-ERRORMAP-real-23514-duration-check")],
)
def test_public_create_does_not_relabel_real_unrelated_check_as_overlap(
    appointment_http_client,
    case_world,
    _case,
):
    client, headers = appointment_http_client
    control_start = case_world.start + timedelta(minutes=120)
    _raw_create_success(
        client,
        headers,
        case_world,
        patient_label="Synthetic unrelated-integrity positive control",
        start=control_start,
        minutes=30,
        location_id=case_world.l1,
        practitioner_id=case_world.r2,
    )
    before = case_world.snapshot()

    patient_label = "Synthetic real 23514 mapping negative"
    attempted_start = case_world.start + timedelta(minutes=180)
    boundary = {"before_flush_calls": 0, "rollback_calls": 0}
    physical_pairs = []
    soft_rollback_nested = []

    def force_real_duration_check(session, flush_context, instances):
        candidate = _marked_pending_create(
            session,
            case_world,
            patient_label=patient_label,
            expected_start=attempted_start,
            expected_practitioner=case_world.r2,
            expected_location=case_world.l2,
        )
        if candidate is None:
            return
        assert boundary["before_flush_calls"] == 0
        boundary["before_flush_calls"] += 1
        boundary["session"] = session
        # Input validation has already accepted 30.  Mutate only this marked
        # pending object so the installed PostgreSQL check is the real oracle.
        candidate.duration_minutes = 0

    def observe_physical_error(context):
        original = context.original_exception
        physical_pairs.append(
            (
                getattr(original, "sqlstate", None)
                or getattr(original, "pgcode", None),
                getattr(
                    getattr(original, "diag", None),
                    "constraint_name",
                    None,
                ),
            )
        )

    def observe_rollback(session):
        if session is boundary.get("session"):
            boundary["rollback_calls"] += 1

    def observe_soft_rollback(session, previous_transaction):
        if session is boundary.get("session"):
            # Failed flush rolls back its child; the router must then close
            # the root explicitly. Session.close() alone emits neither event.
            soft_rollback_nested.append(previous_transaction.parent is not None)

    event.listen(Session, "before_flush", force_real_duration_check)
    event.listen(Session, "after_rollback", observe_rollback)
    event.listen(Session, "after_soft_rollback", observe_soft_rollback)
    event.listen(case_world.runtime.engine, "handle_error", observe_physical_error)
    try:
        with pytest.raises(IntegrityError) as raised:
            _raw_create_request(
                client,
                headers,
                case_world,
                patient_label=patient_label,
                start=attempted_start,
                practitioner_id=case_world.r2,
                location_id=case_world.l2,
            )
    finally:
        event.remove(case_world.runtime.engine, "handle_error", observe_physical_error)
        event.remove(Session, "after_soft_rollback", observe_soft_rollback)
        event.remove(Session, "after_rollback", observe_rollback)
        event.remove(Session, "before_flush", force_real_duration_check)

    assert boundary["before_flush_calls"] == 1
    assert boundary["rollback_calls"] == 1
    assert soft_rollback_nested == [True, False]
    assert physical_pairs == [
        (REAL_UNRELATED_SQLSTATE, REAL_UNRELATED_CONSTRAINT)
    ]
    assert _integrity_pair(raised.value) == (
        REAL_UNRELATED_SQLSTATE,
        REAL_UNRELATED_CONSTRAINT,
    )
    # A broad IntegrityError classifier would have returned a business 409 and
    # failed the pytest.raises boundary above.  The fresh read proves rollback.
    assert case_world.snapshot() == before


class _SyntheticIntegrityOriginal(Exception):
    """Typed diagnostic double for unavailable SQLSTATE/constraint pairs."""

    def __init__(self, sqlstate, constraint_name):
        super().__init__("authored non-PostgreSQL integrity diagnostic")
        self.sqlstate = sqlstate
        self.pgcode = sqlstate
        self.diag = SimpleNamespace(constraint_name=constraint_name)


@pytest.mark.parametrize(
    ("diagnostic_sqlstate", "diagnostic_constraint"),
    [
        pytest.param(
            "23514",
            COLLISION_CONSTRAINT,
            id="APT-ERRORMAP-synthetic-23514-exact-overlap-name",
        ),
        pytest.param(
            "23P01",
            SYNTHETIC_WRONG_EXCLUSION,
            id="APT-ERRORMAP-synthetic-23p01-wrong-constraint",
        ),
    ],
)
def test_public_create_requires_both_overlap_diagnostic_components(
    appointment_http_client,
    case_world,
    diagnostic_sqlstate,
    diagnostic_constraint,
):
    """Synthetic AND-pair proof after a real INSERT; not PG enforcement proof."""
    client, headers = appointment_http_client
    control_start = case_world.start + timedelta(minutes=240)
    _raw_create_success(
        client,
        headers,
        case_world,
        patient_label="Synthetic wrong-constraint positive control",
        start=control_start,
        minutes=30,
        location_id=None,
        practitioner_id=case_world.r2,
    )
    before = case_world.snapshot()

    patient_label = (
        "Synthetic diagnostic pair negative "
        + diagnostic_sqlstate
        + " "
        + diagnostic_constraint
    )
    attempted_start = case_world.start + timedelta(minutes=300)
    boundary = {
        "before_flush_calls": 0,
        "after_flush_postexec_calls": 0,
        "rollback_calls": 0,
    }
    physical_pairs = []
    soft_rollback_nested = []
    synthetic_original = _SyntheticIntegrityOriginal(
        diagnostic_sqlstate,
        diagnostic_constraint,
    )

    def identify_exact_create(session, flush_context, instances):
        candidate = _marked_pending_create(
            session,
            case_world,
            patient_label=patient_label,
            expected_start=attempted_start,
            expected_practitioner=case_world.r2,
            expected_location=case_world.l2,
        )
        if candidate is None:
            return
        assert boundary["before_flush_calls"] == 0
        boundary["before_flush_calls"] += 1
        boundary["session"] = session
        boundary["candidate"] = candidate

    def inject_wrong_constraint_after_real_flush(session, flush_context):
        if session is not boundary.get("session"):
            return
        assert boundary["after_flush_postexec_calls"] == 0
        boundary["after_flush_postexec_calls"] += 1
        candidate = boundary["candidate"]
        assert candidate.id is not None
        staged = session.connection().execute(
            text(
                """
                SELECT pg_catalog.to_jsonb(appointment_row)
                FROM public.appointments AS appointment_row
                WHERE appointment_row.id = :appointment
                  AND appointment_row.practice_id = :practice
                """
            ),
            {"appointment": candidate.id, "practice": case_world.p},
        ).scalar_one()
        assert staged["id"] == str(candidate.id)
        assert staged["practice_id"] == str(case_world.p)
        assert staged["patient_name_provisional"] == patient_label
        assert staged["duration_minutes"] == 30
        boundary["staged_row"] = staged
        raise IntegrityError(
            "authored synthetic appointment INSERT boundary",
            {},
            synthetic_original,
        )

    def observe_physical_error(context):
        original = context.original_exception
        physical_pairs.append(
            (
                getattr(original, "sqlstate", None)
                or getattr(original, "pgcode", None),
                getattr(
                    getattr(original, "diag", None),
                    "constraint_name",
                    None,
                ),
            )
        )

    def observe_rollback(session):
        if session is boundary.get("session"):
            boundary["rollback_calls"] += 1

    def observe_soft_rollback(session, previous_transaction):
        if session is boundary.get("session"):
            # Failed flush rolls back its child; the router must then close
            # the root explicitly. Session.close() alone emits neither event.
            soft_rollback_nested.append(previous_transaction.parent is not None)

    event.listen(Session, "before_flush", identify_exact_create)
    event.listen(Session, "after_flush_postexec", inject_wrong_constraint_after_real_flush)
    event.listen(Session, "after_rollback", observe_rollback)
    event.listen(Session, "after_soft_rollback", observe_soft_rollback)
    event.listen(case_world.runtime.engine, "handle_error", observe_physical_error)
    try:
        with pytest.raises(IntegrityError) as raised:
            _raw_create_request(
                client,
                headers,
                case_world,
                patient_label=patient_label,
                start=attempted_start,
                practitioner_id=case_world.r2,
                location_id=case_world.l2,
            )
    finally:
        event.remove(case_world.runtime.engine, "handle_error", observe_physical_error)
        event.remove(Session, "after_soft_rollback", observe_soft_rollback)
        event.remove(Session, "after_rollback", observe_rollback)
        event.remove(
            Session,
            "after_flush_postexec",
            inject_wrong_constraint_after_real_flush,
        )
        event.remove(Session, "before_flush", identify_exact_create)

    assert boundary["before_flush_calls"] == 1
    assert boundary["after_flush_postexec_calls"] == 1
    assert boundary["rollback_calls"] == 1
    assert soft_rollback_nested == [True, False]
    assert boundary["staged_row"]
    assert physical_pairs == [], "synthetic diagnostic must not claim DB enforcement"
    assert raised.value.orig is synthetic_original
    assert _integrity_pair(raised.value) == (
        diagnostic_sqlstate,
        diagnostic_constraint,
    )
    # A classifier that weakens either member of the required logical AND would
    # have returned a business 409 in one parameter and failed pytest.raises.
    assert case_world.snapshot() == before


# Sequential command coverage: independently reviewed e0c152de.
SEQ_CREATE_OPERATION = "confirmAppointmentCreateProposal"
SEQ_UPDATE_OPERATION = "confirmAppointmentUpdateProposal"


def _seq_site(world, name):
    return None if name == "none" else getattr(world, name)


def _seq_headers(world, *, practice_id, actor_id):
    token = create_access_token(
        {
            "sub": str(actor_id),
            "practice_id": str(practice_id),
            "role": UserRole.Receptionist.value,
        }
    )
    return {"Authorization": f"Bearer {token}"}


def _seq_rows(snapshot, table):
    rows = json.loads(snapshot[table])
    assert isinstance(rows, list)
    return {row["id"]: row for row in rows}


def _seq_added_row(before, after, table):
    before_rows = _seq_rows(before, table)
    after_rows = _seq_rows(after, table)
    added = set(after_rows) - set(before_rows)
    assert len(added) == 1
    assert set(after_rows) == set(before_rows) | added
    assert all(after_rows[row_id] == row for row_id, row in before_rows.items())
    return after_rows[added.pop()]


def _seq_assert_command_links(
    before,
    after,
    *,
    appointment_id,
    operation_id,
    action,
):
    audit = _seq_added_row(before, after, "appointment_audit_log")
    receipt = _seq_added_row(before, after, "appointment_command_idempotency")
    assert audit["appointment_id"] == str(appointment_id)
    assert audit["action"] == action
    assert audit["command_id"] == receipt["id"]
    assert receipt["operation_id"] == operation_id
    assert receipt["state"] == "completed"
    assert receipt["result_kind"] == "confirmed_write"
    assert receipt["target_appointment_id"] == str(appointment_id)
    assert receipt["audit_log_id"] == audit["id"]
    assert receipt["response_status_code"] == 200
    assert receipt["practice_id"] == audit["practice_id"]
    if operation_id in (SEQ_CREATE_OPERATION, SEQ_UPDATE_OPERATION):
        # Generic create/update receipts do not claim the private status contract.
        assert receipt["completed_receipt_version"] is None
        assert receipt["pre_state_version"] is None
        assert receipt["post_state_version"] is None
    return audit, receipt


def _seq_create_success(
    client,
    headers,
    world,
    *,
    practice_id,
    practitioner_id,
    location_id,
    start,
    minutes,
    label,
):
    before = world.snapshot(practice_id)
    proposal_response = client.post(
        CREATE_PROPOSAL_ENDPOINT,
        headers=_confirmation_key_headers(headers, f"{label}-proposal"),
        json={
            "patient_name_provisional": f"Synthetic {label}",
            "practitioner_id": str(practitioner_id),
            "location_id": None if location_id is None else str(location_id),
            "start_time": start.isoformat(),
            "duration_minutes": minutes,
        },
    )
    assert proposal_response.status_code == 200
    proposal = proposal_response.json()
    assert proposal["intent"] == "create_appointment"
    assert proposal["safe"] is True
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "proposal"
    assert proposal["blocks"] == []
    assert proposal["conflict"] is None
    assert proposal["confirm_endpoint"] == CREATE_CONFIRM_ENDPOINT
    assert proposal["create_proposal_freshness_id"]
    assert proposal["signed_confirmation_evidence_required"] is True
    assert proposal["signed_confirmation_evidence"]
    assert world.snapshot(practice_id) == before

    confirmation = deepcopy(proposal["confirm_payload"])
    assert confirmation["confirmed"] is False
    assert confirmation["create_proposal"]["command"] == proposal["command"]
    assert confirmation["signed_confirmation_evidence"] == proposal[
        "signed_confirmation_evidence"
    ]
    confirmation["confirmed"] = True
    response = _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        f"{label}-confirm",
        confirmation,
    )
    assert response.status_code == 200
    body = response.json()
    _assert_confirmed_create_confirmation(body, start)
    appointment = body["appointment"]
    assert appointment["practitioner_id"] == str(practitioner_id)
    assert appointment["location_id"] == (
        None if location_id is None else str(location_id)
    )
    assert appointment["duration_minutes"] == minutes
    assert appointment["status"] == "Booked"

    after = world.snapshot(practice_id)
    created = _seq_added_row(before, after, "appointments")
    assert created["id"] == appointment["id"]
    assert created["practice_id"] == str(practice_id)
    assert created["practitioner_id"] == str(practitioner_id)
    assert created["location_id"] == (
        None if location_id is None else str(location_id)
    )
    assert created["duration_minutes"] == minutes
    assert created["status"] == "Booked"
    assert created["appointment_state_version"] == 1
    assert _confirmation_utc(_confirmation_datetime(created["start_time"])) == _confirmation_utc(start)
    audit, receipt = _seq_assert_command_links(
        before,
        after,
        appointment_id=appointment["id"],
        operation_id=SEQ_CREATE_OPERATION,
        action="create",
    )
    assert body["confirmation_receipt"]["correlation_id"] == receipt["id"]
    assert body["confirmation_receipt"]["audit_event_id"] == audit["id"]
    assert receipt["response_body_json"] == body
    return appointment


def _seq_blocked_create_proposal(
    client,
    headers,
    world,
    *,
    practice_id,
    practitioner_id,
    location_id,
    start,
    minutes,
    label,
):
    before = world.snapshot(practice_id)
    response = client.post(
        CREATE_PROPOSAL_ENDPOINT,
        headers=_confirmation_key_headers(headers, f"{label}-proposal"),
        json={
            "patient_name_provisional": f"Synthetic {label}",
            "practitioner_id": str(practitioner_id),
            "location_id": None if location_id is None else str(location_id),
            "start_time": start.isoformat(),
            "duration_minutes": minutes,
        },
    )
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["intent"] == "create_appointment"
    assert proposal["safe"] is False
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "blocked"
    assert proposal["blocks"] == [
        {
            "code": "appointment_conflict",
            "severity": "blocked",
            "message": "This appointment overlaps an existing booking.",
        }
    ]
    assert proposal["conflict"] is not None
    # The public contract does not mint authority for an already blocked
    # proposal.  The prior successful command is the signed write control.
    assert not proposal.get("confirm_payload")
    assert not proposal.get("signed_confirmation_evidence")
    assert world.snapshot(practice_id) == before
    return proposal


def _seq_status_success(
    client,
    headers,
    world,
    *,
    practice_id,
    appointment_id,
    status,
    label,
):
    before = world.snapshot(practice_id)
    before_target = _seq_rows(before, "appointments")[str(appointment_id)]
    proposal, confirmation = _actual_status_confirmation(
        client,
        headers,
        appointment_id,
        {"status": status},
        proposal_key=f"{label}-proposal",
    )
    assert proposal["command"]["status"] == status
    assert world.snapshot(practice_id) == before
    response = _confirm_status(client, headers, f"{label}-confirm", confirmation)
    assert response.status_code == 200
    body = response.json()
    _assert_confirmed_status(body)
    assert body["appointment"]["status"] == status

    after = world.snapshot(practice_id)
    before_rows = _seq_rows(before, "appointments")
    after_rows = _seq_rows(after, "appointments")
    assert set(after_rows) == set(before_rows)
    assert {
        key: value for key, value in after_rows.items() if key != str(appointment_id)
    } == {
        key: value for key, value in before_rows.items() if key != str(appointment_id)
    }
    target = after_rows[str(appointment_id)]
    assert target["status"] == status
    assert target["appointment_state_version"] == (
        before_target["appointment_state_version"] + 1
    )
    audit, receipt = _seq_assert_command_links(
        before,
        after,
        appointment_id=appointment_id,
        operation_id=STATUS_CONFIRM_OPERATION,
        action="status_change",
    )
    assert audit["status_before"] == before_target["status"]
    assert audit["status_after"] == status
    assert receipt["pre_state_version"] == before_target["appointment_state_version"]
    assert receipt["post_state_version"] == target["appointment_state_version"]
    return target


def _seq_update_success(
    client,
    headers,
    world,
    *,
    practice_id,
    appointment_id,
    changes,
    expected,
    label,
):
    before = world.snapshot(practice_id)
    before_target = _seq_rows(before, "appointments")[str(appointment_id)]
    _, confirmation = _actual_update_confirmation(
        client,
        headers,
        appointment_id,
        changes,
        proposal_key=f"{label}-proposal",
    )
    assert world.snapshot(practice_id) == before
    response = _confirm_update(client, headers, f"{label}-confirm", confirmation)
    assert response.status_code == 200
    body = response.json()
    _assert_confirmed_update(body)

    after = world.snapshot(practice_id)
    before_rows = _seq_rows(before, "appointments")
    after_rows = _seq_rows(after, "appointments")
    assert set(after_rows) == set(before_rows)
    assert {
        key: value for key, value in after_rows.items() if key != str(appointment_id)
    } == {
        key: value for key, value in before_rows.items() if key != str(appointment_id)
    }
    target = after_rows[str(appointment_id)]
    for field, value in before_target.items():
        if field not in set(expected) | {"appointment_state_version"}:
            assert target[field] == value, f"unrequested appointment field changed: {field}"
    for field, value in expected.items():
        assert target[field] == (str(value) if isinstance(value, uuid.UUID) else value)
        assert body["appointment"][field] == (
            str(value) if isinstance(value, uuid.UUID) else value
        )
    assert target["appointment_state_version"] == (
        before_target["appointment_state_version"] + 1
    )
    _, receipt = _seq_assert_command_links(
        before,
        after,
        appointment_id=appointment_id,
        operation_id=SEQ_UPDATE_OPERATION,
        action="update",
    )
    assert receipt["response_body_json"] == body
    return target


def _seq_blocked_update_proposal(
    client,
    headers,
    world,
    *,
    practice_id,
    appointment_id,
    changes,
    label,
):
    before = world.snapshot(practice_id)
    response = client.post(
        f"{UPDATE_PROPOSAL_ENDPOINT}/{appointment_id}",
        headers=_confirmation_key_headers(headers, f"{label}-proposal"),
        json=changes,
    )
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["intent"] == "update_appointment"
    assert proposal["safe"] is False
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "blocked"
    assert proposal["blocks"] == [
        {
            "code": "appointment_conflict",
            "severity": "blocked",
            "message": "The proposed time overlaps an existing booking.",
        }
    ]
    assert proposal["conflict"] is not None
    assert not proposal.get("confirm_payload")
    assert not proposal.get("signed_confirmation_evidence")
    assert world.snapshot(practice_id) == before
    return proposal


S1_COMMAND_SITE_ORDER_CASES = [
    pytest.param("l1", "l1", False, id="APT-S1-http-signed-create-l1-l1-forward"),
    pytest.param("l1", "l1", True, id="APT-S1-http-signed-create-l1-l1-reverse"),
    pytest.param("l1", "l2", False, id="APT-S1-http-signed-create-l1-l2-forward"),
    pytest.param("l1", "l2", True, id="APT-S1-http-signed-create-l1-l2-reverse"),
    pytest.param("l1", "none", False, id="APT-S1-http-signed-create-l1-null-forward"),
    pytest.param("l1", "none", True, id="APT-S1-http-signed-create-l1-null-reverse"),
    pytest.param("l2", "l2", False, id="APT-S1-http-signed-create-l2-l2-forward"),
    pytest.param("l2", "l2", True, id="APT-S1-http-signed-create-l2-l2-reverse"),
    pytest.param("l2", "none", False, id="APT-S1-http-signed-create-l2-null-forward"),
    pytest.param("l2", "none", True, id="APT-S1-http-signed-create-l2-null-reverse"),
    pytest.param("none", "none", False, id="APT-S1-http-signed-create-null-null-forward"),
    pytest.param("none", "none", True, id="APT-S1-http-signed-create-null-null-reverse"),
]


@pytest.mark.parametrize("site_a,site_b,reverse", S1_COMMAND_SITE_ORDER_CASES)
def test_apt_s1_signed_create_is_location_and_order_independent(
    appointment_http_client, case_world, site_a, site_b, reverse
):
    client, headers = appointment_http_client
    bookings = [
        {
            "site": _seq_site(case_world, site_a),
            "start": case_world.start,
            "label": "apt-s1-a",
        },
        {
            "site": _seq_site(case_world, site_b),
            "start": case_world.start + timedelta(minutes=15),
            "label": "apt-s1-b",
        },
    ]
    if reverse:
        bookings.reverse()
    winner, loser = bookings
    _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=winner["site"],
        start=winner["start"],
        minutes=30,
        label=winner["label"],
    )
    after_winner = case_world.snapshot()
    _seq_blocked_create_proposal(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=loser["site"],
        start=loser["start"],
        minutes=30,
        label=loser["label"],
    )
    assert case_world.snapshot() == after_winner
    assert len(_seq_rows(after_winner, "appointments")) == 1


S2_COMMAND_SHAPES = [
    pytest.param(0, 60, 0, 60, id="APT-S2-http-signed-create-equal"),
    pytest.param(0, 90, 15, 30, id="APT-S2-http-signed-create-first-contains-second"),
    pytest.param(15, 30, 0, 90, id="APT-S2-http-signed-create-second-contains-first"),
    pytest.param(0, 60, -15, 30, id="APT-S2-http-signed-create-left-partial"),
    pytest.param(0, 60, 45, 30, id="APT-S2-http-signed-create-right-partial"),
]


@pytest.mark.parametrize(
    "first_offset,first_minutes,second_offset,second_minutes", S2_COMMAND_SHAPES
)
def test_apt_s2_signed_create_rejects_every_overlap_shape(
    appointment_http_client,
    case_world,
    first_offset,
    first_minutes,
    second_offset,
    second_minutes,
):
    client, headers = appointment_http_client
    _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start + timedelta(minutes=first_offset),
        minutes=first_minutes,
        label="apt-s2-winner",
    )
    after_winner = case_world.snapshot()
    _seq_blocked_create_proposal(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l2,
        start=case_world.start + timedelta(minutes=second_offset),
        minutes=second_minutes,
        label="apt-s2-loser",
    )
    assert case_world.snapshot() == after_winner


S3_COMMAND_BOUNDARIES = [
    pytest.param(30, id="APT-S3-http-signed-create-right-adjacent"),
    pytest.param(-30, id="APT-S3-http-signed-create-left-adjacent"),
    pytest.param(45, id="APT-S3-http-signed-create-positive-gap"),
]


@pytest.mark.parametrize("second_offset", S3_COMMAND_BOUNDARIES)
def test_apt_s3_signed_create_allows_adjacency_and_gap(
    appointment_http_client, case_world, second_offset
):
    client, headers = appointment_http_client
    _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
        label="apt-s3-first",
    )
    _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l2,
        start=case_world.start + timedelta(minutes=second_offset),
        minutes=30,
        label="apt-s3-second",
    )
    assert len(_seq_rows(case_world.snapshot(), "appointments")) == 2


S4_COMMAND_KEYS = [
    pytest.param("practitioner", id="APT-S4-http-signed-create-different-practitioner"),
    pytest.param("practice", id="APT-S4-http-signed-create-different-practice"),
]


@pytest.mark.parametrize("key_case", S4_COMMAND_KEYS)
def test_apt_s4_signed_create_does_not_overblock_other_keys(
    appointment_http_client, case_world, key_case
):
    client, p_headers = appointment_http_client
    _seq_create_success(
        client,
        p_headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
        label="apt-s4-primary",
    )
    if key_case == "practitioner":
        _seq_create_success(
            client,
            p_headers,
            case_world,
            practice_id=case_world.p,
            practitioner_id=case_world.r2,
            location_id=case_world.l2,
            start=case_world.start,
            minutes=30,
            label="apt-s4-other-practitioner",
        )
        assert len(_seq_rows(case_world.snapshot(), "appointments")) == 2
        return

    p_after = case_world.snapshot(case_world.p)
    q_headers = _seq_headers(
        case_world, practice_id=case_world.q, actor_id=case_world.actor_q
    )
    _seq_create_success(
        client,
        q_headers,
        case_world,
        practice_id=case_world.q,
        practitioner_id=case_world.rq,
        location_id=case_world.lq,
        start=case_world.start,
        minutes=30,
        label="apt-s4-other-practice",
    )
    assert case_world.snapshot(case_world.p) == p_after
    assert len(_seq_rows(case_world.snapshot(case_world.q), "appointments")) == 1


S5_COMMAND_STATUSES = [
    pytest.param("Booked", True, id="APT-S5-http-status-booked-blocks"),
    pytest.param("Confirmed", True, id="APT-S5-http-status-confirmed-blocks"),
    pytest.param("Arrived", True, id="APT-S5-http-status-arrived-blocks"),
    pytest.param("InConsult", True, id="APT-S5-http-status-inconsult-blocks"),
    pytest.param("Completed", True, id="APT-S5-http-status-completed-blocks"),
    pytest.param("Cancelled", False, id="APT-S5-http-status-cancelled-releases"),
    pytest.param("NoShow", False, id="APT-S5-http-status-noshow-releases"),
    pytest.param("DNA", False, id="APT-S5-http-status-dna-releases"),
]


@pytest.mark.parametrize("status_name,blocks", S5_COMMAND_STATUSES)
def test_apt_s5_authorised_status_disposition_controls_occupancy(
    appointment_http_client, case_world, status_name, blocks
):
    client, headers = appointment_http_client
    incumbent = _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
        label="apt-s5-incumbent",
    )
    if status_name != "Booked":
        _seq_status_success(
            client,
            headers,
            case_world,
            practice_id=case_world.p,
            appointment_id=incumbent["id"],
            status=status_name,
            label="apt-s5-status",
        )

    if blocks:
        after_status = case_world.snapshot()
        _seq_blocked_create_proposal(
            client,
            headers,
            case_world,
            practice_id=case_world.p,
            practitioner_id=case_world.r,
            location_id=case_world.l2,
            start=case_world.start + timedelta(minutes=15),
            minutes=30,
            label="apt-s5-contender",
        )
        assert case_world.snapshot() == after_status
    else:
        _seq_create_success(
            client,
            headers,
            case_world,
            practice_id=case_world.p,
            practitioner_id=case_world.r,
            location_id=case_world.l2,
            start=case_world.start + timedelta(minutes=15),
            minutes=30,
            label="apt-s5-contender",
        )
        assert len(_seq_rows(case_world.snapshot(), "appointments")) == 2


S6_COMMAND_UPDATES = [
    pytest.param("practitioner", id="APT-S6-http-update-practitioner-conflict"),
    pytest.param("extension", id="APT-S6-http-update-extension-conflict"),
]


@pytest.mark.parametrize("update_case", S6_COMMAND_UPDATES)
def test_apt_s6_update_proposal_rejects_conflicting_final_row(
    appointment_http_client, case_world, update_case
):
    client, headers = appointment_http_client
    if update_case == "practitioner":
        incumbent_start = case_world.start
        target_start = case_world.start
        target_practitioner = case_world.r2
        changes = {"practitioner_id": str(case_world.r)}
    else:
        incumbent_start = case_world.start
        target_start = case_world.start - timedelta(minutes=30)
        target_practitioner = case_world.r
        changes = {"duration_minutes": 45}

    _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=incumbent_start,
        minutes=30,
        label="apt-s6-incumbent",
    )
    target = _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=target_practitioner,
        location_id=None,
        start=target_start,
        minutes=30,
        label="apt-s6-target",
    )
    before = case_world.snapshot()
    target_before = _seq_rows(before, "appointments")[target["id"]]
    _seq_blocked_update_proposal(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        appointment_id=target["id"],
        changes=changes,
        label="apt-s6-conflict",
    )
    after = case_world.snapshot()
    assert after == before
    assert _seq_rows(after, "appointments")[target["id"]] == target_before


@pytest.mark.parametrize(
    "_case",
    [pytest.param(None, id="APT-S7-http-update-self-shrink")],
)
def test_apt_s7_confirmed_shrink_excludes_the_target_itself(
    appointment_http_client, case_world, _case
):
    client, headers = appointment_http_client
    target = _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
        label="apt-s7-target",
    )
    _seq_update_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        appointment_id=target["id"],
        changes={"duration_minutes": 15},
        expected={"duration_minutes": 15},
        label="apt-s7-shrink",
    )


S8_COMMAND_REACTIVATIONS = [
    pytest.param(True, id="APT-S8-http-status-dna-conflict"),
    pytest.param(False, id="APT-S8-http-status-dna-free"),
]


@pytest.mark.parametrize("conflicting", S8_COMMAND_REACTIVATIONS)
def test_apt_s8_dna_reactivation_rechecks_current_occupancy(
    appointment_http_client, case_world, conflicting
):
    client, headers = appointment_http_client
    target_start = case_world.start
    target = _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=None,
        start=target_start,
        minutes=30,
        label="apt-s8-target",
    )
    _seq_status_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        appointment_id=target["id"],
        status="DNA",
        label="apt-s8-inactivate",
    )
    incumbent = None
    if conflicting:
        incumbent = _seq_create_success(
            client,
            headers,
            case_world,
            practice_id=case_world.p,
            practitioner_id=case_world.r,
            location_id=case_world.l1,
            start=target_start,
            minutes=30,
            label="apt-s8-incumbent",
        )

    before = case_world.snapshot()
    target_before = _seq_rows(before, "appointments")[target["id"]]
    prior_public_response = client.get(
        f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}", headers=headers,
    )
    assert prior_public_response.status_code == 200
    prior_public = prior_public_response.json()
    assert prior_public["status"] == "DNA"
    # Terminal reactivation is deliberately deferred by the signed adapter.
    # The existing authorized raw status command supplies this C-layer control.
    response = client.patch(
        f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}/status",
        headers=headers,
        json={"status": "Booked"},
    )
    if conflicting:
        assert incumbent is not None
        _assert_raw_collision(response, incumbent)
        assert case_world.snapshot() == before
    else:
        assert response.status_code == 200
        assert response.json() == {**prior_public, "status": "Booked"}
        after = case_world.snapshot()
        after_target = _seq_rows(after, "appointments")[target["id"]]
        assert after_target["status"] == "Booked"
        assert after_target["appointment_state_version"] == target_before["appointment_state_version"] + 1
        for field, value in target_before.items():
            if field not in {"status", "appointment_state_version"}:
                assert after_target[field] == value
        for field, value in response.json().items():
            if field in after_target:
                if field in {"start_time", "created_at"}:
                    assert _confirmation_utc(_confirmation_datetime(value)) == _confirmation_utc(_confirmation_datetime(after_target[field]))
                else:
                    assert value == after_target[field]
        assert _confirmation_utc(_confirmation_datetime(response.json()["end_time"])) == _confirmation_utc(_confirmation_datetime(after_target["start_time"])) + timedelta(minutes=after_target["duration_minutes"])
        before_rows, after_rows = _seq_rows(before, "appointments"), _seq_rows(after, "appointments")
        assert set(after_rows) == set(before_rows)
        assert all(after_rows[row_id] == row for row_id, row in before_rows.items() if row_id != target["id"])
        audit = _seq_added_row(before, after, "appointment_audit_log")
        assert audit["appointment_id"] == target["id"]
        assert audit["action"] == "status_change"
        assert audit["status_before"] == "DNA" and audit["status_after"] == "Booked"
        assert audit["command_id"] is None
        assert after["appointment_command_idempotency"] == before["appointment_command_idempotency"]


@pytest.mark.parametrize(
    "_case",
    [pytest.param(None, id="APT-S9-http-cancel-then-signed-create")],
)
def test_apt_s9_confirmed_cancellation_releases_the_slot(
    appointment_http_client, case_world, _case
):
    client, headers = appointment_http_client
    incumbent = _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
        label="apt-s9-cancel-target",
    )
    _seq_status_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        appointment_id=incumbent["id"],
        status="Cancelled",
        label="apt-s9-cancel",
    )
    _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=None,
        start=case_world.start,
        minutes=30,
        label="apt-s9-replacement",
    )
    rows = _seq_rows(case_world.snapshot(), "appointments")
    assert rows[incumbent["id"]]["status"] == "Cancelled"
    assert len(rows) == 2


@pytest.mark.parametrize(
    "_case",
    [pytest.param(None, id="APT-S9-http-site-only-confirmed-update")],
)
def test_apt_s9_site_only_confirmed_update_remains_valid(
    appointment_http_client, case_world, _case
):
    client, headers = appointment_http_client
    target = _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
        label="apt-s9-site-target",
    )
    before_target = _seq_rows(case_world.snapshot(), "appointments")[target["id"]]
    updated = _seq_update_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        appointment_id=target["id"],
        changes={"location_id": str(case_world.l2)},
        expected={"location_id": case_world.l2},
        label="apt-s9-site-update",
    )
    for field in (
        "practice_id",
        "practitioner_id",
        "start_time",
        "appointment_date",
        "start_time_local",
        "duration_minutes",
        "status",
    ):
        assert updated[field] == before_target[field]


S9_COMMAND_SITE_COUNTS = [
    pytest.param(False, id="APT-S9-http-unused-site-two-to-one"),
    pytest.param(True, id="APT-S9-http-unused-site-one-to-two"),
]


@pytest.mark.parametrize("reactivate_unused_site", S9_COMMAND_SITE_COUNTS)
def test_apt_s9_unused_site_count_does_not_change_command_collision(
    appointment_http_client, case_world, reactivate_unused_site
):
    client, headers = appointment_http_client
    _seq_create_success(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
        minutes=30,
        label="apt-s9-site-count-incumbent",
    )

    with case_world.runtime.admin_engine.begin() as connection:
        disabled = connection.execute(
            text(
                "UPDATE public.practice_locations SET is_active=false "
                "WHERE id=:site AND practice_id=:practice"
            ),
            {"site": case_world.l2, "practice": case_world.p},
        )
        assert disabled.rowcount == 1
        active_count = connection.execute(
            text(
                "SELECT count(*) FROM public.practice_locations "
                "WHERE practice_id=:practice AND is_active"
            ),
            {"practice": case_world.p},
        ).scalar_one()
        assert active_count == 1
        if reactivate_unused_site:
            enabled = connection.execute(
                text(
                    "UPDATE public.practice_locations SET is_active=true "
                    "WHERE id=:site AND practice_id=:practice"
                ),
                {"site": case_world.l2, "practice": case_world.p},
            )
            assert enabled.rowcount == 1
            active_count = connection.execute(
                text(
                    "SELECT count(*) FROM public.practice_locations "
                    "WHERE practice_id=:practice AND is_active"
                ),
                {"practice": case_world.p},
            ).scalar_one()
            assert active_count == 2

    after_toggle = case_world.snapshot()
    _seq_blocked_create_proposal(
        client,
        headers,
        case_world,
        practice_id=case_world.p,
        practitioner_id=case_world.r,
        location_id=None,
        start=case_world.start + timedelta(minutes=15),
        minutes=30,
        label="apt-s9-site-count-contender",
    )
    assert case_world.snapshot() == after_toggle


@pytest.mark.parametrize("_case", [
    pytest.param(None, id="APT-S7-http-signed-update-same-values-and-replay"),
])
def test_apt_s7_same_value_confirmation_preserves_row_version_and_audits_once(
    appointment_http_client, case_world, _case,
):
    """No row UPDATE means no trigger increment; command audit is still real."""
    client, headers = appointment_http_client
    target = _seq_create_success(client, headers, case_world,
        practice_id=case_world.p, practitioner_id=case_world.r,
        location_id=case_world.l1, start=case_world.start, minutes=30,
        label="apt-s7-noop-target")
    before = case_world.snapshot()
    before_target = _seq_rows(before, "appointments")[target["id"]]
    _, confirmation = _actual_update_confirmation(client, headers, target["id"], {
        "start_time": case_world.start.isoformat(),
        "duration_minutes": 30,
        "practitioner_id": str(case_world.r),
        "location_id": str(case_world.l1),
    }, proposal_key="apt-s7-noop-proposal")
    assert case_world.snapshot() == before
    observed = {"appointment_updates": 0, "commits": 0}

    def observe_statement(connection, cursor, statement, parameters, context, executemany):
        # Retain only a statement-shape count, never SQL/bind values or tokens.
        normalized = re.sub(r"\s+", " ", statement.lower().replace('"', '')).strip()
        if re.match(r"^update\s+(?:public\.)?appointments\s+set\b", normalized):
            observed["appointment_updates"] += 1

    def observe_commit(connection):
        observed["commits"] += 1

    engine = case_world.runtime.engine
    event.listen(engine, "before_cursor_execute", observe_statement)
    event.listen(engine, "commit", observe_commit)
    try:
        response = _confirm_update(client, headers, "apt-s7-noop-confirm", confirmation)
    finally:
        event.remove(engine, "commit", observe_commit)
        event.remove(engine, "before_cursor_execute", observe_statement)

    assert observed == {"appointment_updates": 0, "commits": 1}
    assert response.status_code == 200
    body = response.json()
    _assert_confirmed_update(body)
    after = case_world.snapshot()
    assert after["appointments"] == before["appointments"]
    stored = _seq_rows(after, "appointments")[target["id"]]
    assert stored == before_target
    assert stored["appointment_state_version"] == 1
    for field in ("id", "practitioner_id", "location_id", "duration_minutes", "status"):
        assert body["appointment"][field] == stored[field]
    assert _confirmation_utc(_confirmation_datetime(body["appointment"]["start_time"])) == (
        _confirmation_utc(_confirmation_datetime(stored["start_time"]))
    )
    audit, receipt = _seq_assert_command_links(before, after,
        appointment_id=target["id"], operation_id=SEQ_UPDATE_OPERATION, action="update")
    assert audit["status_before"] == "Booked"
    assert receipt["response_body_json"] == body
    assert receipt["pre_state_version"] is None and receipt["post_state_version"] is None

    replay = _confirm_update(client, headers, "apt-s7-noop-confirm", confirmation)
    assert replay.status_code == response.status_code
    assert replay.json() == body
    assert case_world.snapshot() == after


# Tenant and identity controls: independently reviewed 358e9fb8.
def _tenant_headers(case_world, *, practice_id, actor_id):
    token = create_access_token({
        "sub": str(actor_id),
        "practice_id": str(practice_id),
        "role": UserRole.Receptionist.value,
    })
    return {"Authorization": f"Bearer {token}"}


def _tenant_create_body(*, practitioner_id, location_id, start, minutes=30):
    return {
        "patient_name_provisional": "Synthetic tenant command control",
        "practitioner_id": str(practitioner_id),
        "location_id": None if location_id is None else str(location_id),
        "start_time": start.isoformat(),
        "duration_minutes": minutes,
    }


def _tenant_raw_create(client, headers, case_world, *, practice_id,
                       practitioner_id, location_id, start, minutes=30):
    before = case_world.snapshot(practice_id)
    response = client.post(RAW_APPOINTMENTS_ENDPOINT, headers=headers, json=
        _tenant_create_body(practitioner_id=practitioner_id,
                            location_id=location_id, start=start, minutes=minutes))
    assert response.status_code == 201
    body = response.json()
    assert body["practitioner_id"] == str(practitioner_id)
    assert body["location_id"] == (None if location_id is None else str(location_id))
    assert _raw_utc(_raw_parse_datetime(body["start_time"])) == _raw_utc(start)
    assert body["duration_minutes"] == minutes and body["status"] == "Booked"
    after = case_world.snapshot(practice_id)
    stored = _snapshot_row(after, "appointments", body["id"])
    assert stored["practice_id"] == str(practice_id)
    assert stored["practitioner_id"] == str(practitioner_id)
    assert stored["location_id"] == body["location_id"]
    assert _raw_utc(_raw_parse_datetime(stored["start_time"])) == _raw_utc(start)
    assert stored["duration_minutes"] == minutes
    assert stored["appointment_state_version"] == 1
    audits = [row for row in _snapshot_rows(after, "appointment_audit_log")
              if row["appointment_id"] == body["id"]]
    assert len(audits) == 1 and audits[0]["action"] == "create"
    assert audits[0]["practice_id"] == str(practice_id)
    assert audits[0]["command_id"] is None
    assert _snapshot_rows(after, "appointment_command_idempotency") == []
    for table, added_id in (("appointments", body["id"]),
                            ("appointment_audit_log", audits[0]["id"])):
        old_rows = {row["id"]: row for row in _snapshot_rows(before, table)}
        new_rows = {row["id"]: row for row in _snapshot_rows(after, table)}
        assert set(new_rows) == set(old_rows) | {added_id}
        assert all(new_rows[row_id] == row for row_id, row in old_rows.items())
    assert after["appointment_command_idempotency"] == before["appointment_command_idempotency"]
    return body


@pytest.mark.parametrize("_case", [
    pytest.param(None, id="APT-T3-command-complete-own-occupancy-unrelated-tenant"),
])
def test_command_tenant_occupancy_includes_own_sites_and_excludes_other_practice(
    appointment_http_client, case_world, _case,
):
    client, headers = appointment_http_client
    q_headers = _tenant_headers(case_world, practice_id=case_world.q,
                                actor_id=case_world.actor_q)
    other = _tenant_raw_create(client, q_headers, case_world,
        practice_id=case_world.q, practitioner_id=case_world.rq,
        location_id=case_world.lq, start=case_world.start, minutes=90)
    q_before = case_world.snapshot(case_world.q)
    first = _tenant_raw_create(client, headers, case_world,
        practice_id=case_world.p, practitioner_id=case_world.r,
        location_id=case_world.l1, start=case_world.start)
    second = _tenant_raw_create(client, headers, case_world,
        practice_id=case_world.p, practitioner_id=case_world.r,
        location_id=None, start=case_world.start + timedelta(minutes=60))
    p_before = case_world.snapshot(case_world.p)

    # Both own occupants must participate despite different/unspecified sites.
    for winner, offset, probe_site in (
        (first, 15, case_world.l2), (second, 75, case_world.l1),
    ):
        with _tenant_sql_trace(case_world.runtime.engine, case_world.p) as trace:
            rejected = client.post(RAW_APPOINTMENTS_ENDPOINT, headers=headers,
                json=_tenant_create_body(practitioner_id=case_world.r,
                    location_id=probe_site,
                    start=case_world.start + timedelta(minutes=offset)))
        trace.assert_bound_reads()
        _assert_raw_collision(rejected, winner)
        assert other["id"] not in rejected.text
        assert str(case_world.q) not in rejected.text
        assert str(case_world.rq) not in rejected.text
        assert case_world.snapshot(case_world.p) == p_before
        assert case_world.snapshot(case_world.q) == q_before

    # Q occupies this entire gap; its booking must not create a false conflict.
    gap = _tenant_raw_create(client, headers, case_world,
        practice_id=case_world.p, practitioner_id=case_world.r,
        location_id=case_world.l2, start=case_world.start + timedelta(minutes=30))
    p_after = case_world.snapshot(case_world.p)
    assert {row["id"] for row in _snapshot_rows(p_after, "appointments")} == {
        first["id"], second["id"], gap["id"],
    }
    assert len(_snapshot_rows(p_after, "appointment_audit_log")) == 3
    assert case_world.snapshot(case_world.q) == q_before


@pytest.mark.parametrize("operation", [
    pytest.param("read", id="APT-T3-command-other-tenant-target-read"),
    pytest.param("update", id="APT-T3-command-other-tenant-target-update"),
    pytest.param("status", id="APT-T3-command-other-tenant-target-status"),
])
def test_command_cannot_address_other_practice_appointment(
    appointment_http_client, case_world, operation,
):
    client, headers = appointment_http_client
    q_headers = _tenant_headers(case_world, practice_id=case_world.q,
                                actor_id=case_world.actor_q)
    target = _tenant_raw_create(client, q_headers, case_world,
        practice_id=case_world.q, practitioner_id=case_world.rq,
        location_id=case_world.lq, start=case_world.start)
    path = f"{RAW_APPOINTMENTS_ENDPOINT}/{target['id']}"
    # Q's real identity can read its legitimate target through the same router.
    control = client.get(path, headers=q_headers)
    assert control.status_code == 200 and control.json()["id"] == target["id"]
    p_before, q_before = case_world.snapshot(), case_world.snapshot(case_world.q)
    with _tenant_sql_trace(case_world.runtime.engine, case_world.p) as trace:
        if operation == "read":
            rejected = client.get(path, headers=headers)
        elif operation == "update":
            rejected = client.put(path, headers=headers,
                                  json={"reason": "Synthetic forbidden cross-tenant edit"})
        else:
            rejected = client.patch(path + "/status", headers=headers,
                                    json={"status": "Confirmed"})
    trace.assert_bound_reads()
    assert rejected.status_code == 404
    assert rejected.json() == {"detail": "Appointment not found"}
    assert target["id"] not in rejected.text and str(case_world.q) not in rejected.text
    assert case_world.snapshot() == p_before
    assert case_world.snapshot(case_world.q) == q_before


@pytest.mark.parametrize("_case", [
    pytest.param(None, id="APT-T3-command-other-tenant-practitioner"),
])
def test_command_cannot_bind_other_practice_practitioner(
    appointment_http_client, case_world, _case,
):
    client, headers = appointment_http_client
    _tenant_raw_create(client, headers, case_world,
        practice_id=case_world.p, practitioner_id=case_world.r,
        location_id=case_world.l1, start=case_world.start)
    before_p, before_q = case_world.snapshot(), case_world.snapshot(case_world.q)
    with _tenant_sql_trace(case_world.runtime.engine, case_world.p) as trace:
        rejected = client.post(RAW_APPOINTMENTS_ENDPOINT, headers=headers,
            json=_tenant_create_body(practitioner_id=case_world.rq,
                location_id=case_world.l1,
                start=case_world.start + timedelta(minutes=60)))
    trace.assert_bound_reads()
    assert rejected.status_code == 404
    assert rejected.json() == {"detail": "Practitioner not found"}
    assert str(case_world.rq) not in rejected.text
    assert case_world.snapshot() == before_p
    assert case_world.snapshot(case_world.q) == before_q


@pytest.mark.parametrize("identity_case", [
    pytest.param("missing-practice", id="APT-T1-auth-missing-practice-claim"),
    pytest.param("wrong-practice", id="APT-T1-auth-subject-practice-mismatch"),
])
def test_command_authentication_rejects_missing_or_mismatched_practice(
    appointment_http_client, case_world, identity_case,
):
    """Identity controls only; fresh SQL-context controls are separate tests."""
    client, headers = appointment_http_client
    _tenant_raw_create(client, headers, case_world,
        practice_id=case_world.p, practitioner_id=case_world.r,
        location_id=case_world.l1, start=case_world.start)
    before_p, before_q = case_world.snapshot(), case_world.snapshot(case_world.q)
    claims = {"sub": str(case_world.actor), "role": UserRole.Receptionist.value}
    if identity_case == "wrong-practice":
        claims["practice_id"] = str(case_world.q)
    # The service really signs and verifies this token; no authentication
    # dependency is replaced, and token/signature clocks remain unchanged.
    invalid_token = create_access_token(claims)
    rejected = client.post(RAW_APPOINTMENTS_ENDPOINT,
        headers={"Authorization": f"Bearer {invalid_token}"},
        json=_tenant_create_body(practitioner_id=case_world.r,
            location_id=case_world.l1, start=case_world.start + timedelta(minutes=60)))
    assert rejected.status_code == 401
    if identity_case == "missing-practice":
        assert rejected.json() == {"detail": "Could not validate credentials"}
        assert rejected.headers["www-authenticate"] == "Bearer"
    else:
        # The actual dependency has two rejection branches: an unavailable
        # user or its explicit practice-mismatch check. Neither may authorise P.
        assert rejected.json()["detail"] in {
            "User not found or inactive",
            "Token practice does not match the current user practice",
        }
    assert str(case_world.p) not in rejected.text
    assert str(case_world.q) not in rejected.text
    assert str(case_world.actor) not in rejected.text
    assert case_world.snapshot() == before_p
    assert case_world.snapshot(case_world.q) == before_q

    q_headers = _tenant_headers(case_world, practice_id=case_world.q,
                                actor_id=case_world.actor_q)
    own_q = _tenant_raw_create(client, q_headers, case_world,
        practice_id=case_world.q, practitioner_id=case_world.rq,
        location_id=case_world.lq, start=case_world.start)
    assert own_q["practitioner_id"] == str(case_world.rq)
    assert case_world.snapshot() == before_p


# Preserve the signed terminal-status policy: reviewed 7f2da2ce.
@pytest.mark.parametrize("_case", [
    pytest.param(None, id="APT-POLICY-http-signed-terminal-reactivation-deferred"),
])
def test_signed_terminal_reactivation_is_deferred_without_command_effects(
    appointment_http_client, case_world, _case,
):
    """Preserve the signed adapter's policy; raw reactivation is tested separately."""
    client, headers = appointment_http_client
    target = case_world.row("signed-terminal-policy-target", location_id=case_world.l1,
                            status="Cancelled")
    _insert_and_commit(case_world, target)
    before = case_world.snapshot()
    _, confirmation = _actual_status_confirmation(client, headers, target["id"],
        {"status": "Booked"}, proposal_key="apt-signed-terminal-policy-proposal")
    assert case_world.snapshot() == before
    response = _confirm_status(client, headers, "apt-signed-terminal-policy-confirm", confirmation)
    assert response.status_code == 200
    body = response.json()
    _assert_blocked_confirmation(body, "confirm_status_appointment")
    assert body["blocks"] == [{
        "code": "transition_policy_deferred",
        "severity": "blocked",
        "message": "The status confirmation did not pass current checks.",
    }]
    assert case_world.snapshot() == before


# C T1 status/delete command-context tests. This fragment is appended to the
# pinned appointment concurrency test by Host A; it is authored source only.

from app.services.appointment_delete_physical import DeleteConfirmPhysicalError


_CONTEXT_STATUS_OPERATION = "confirmAppointmentStatusProposal"
_CONTEXT_DELETE_OPERATION = "confirmAppointmentDeleteProposal"


def _context_headers(case_world, *, practice_id, actor_id):
    token = create_access_token(
        {
            "sub": str(actor_id),
            "practice_id": str(practice_id),
            "role": UserRole.Receptionist.value,
        }
    )
    return {"Authorization": f"Bearer {token}"}


def _context_assert_idle_pool(case_world):
    engine = case_world.runtime.engine
    pool = engine.pool
    assert not case_world.active_writers
    assert callable(getattr(pool, "checkedout", None))
    assert pool.checkedout() == 0
    return engine


def _context_assert_reviewed_pool(engine):
    pool = engine.pool
    queue = getattr(pool, "_pool", None)
    max_overflow = getattr(pool, "_max_overflow", None)
    assert type(pool).__name__ == "QueuePool"
    assert getattr(queue, "use_lifo", None) is True
    assert type(max_overflow) is int and max_overflow >= 0
    assert pool.size() + max_overflow >= 2
    assert getattr(pool, "_recycle", None) == -1
    assert pool.checkedout() == 0
    return pool


@contextmanager
def _context_delete_grants(case_world, identities):
    rows = [
        {"practice": practice_id, "actor": actor_id}
        for practice_id, actor_id in identities
    ]
    if not rows:
        yield
        return
    with case_world.runtime.admin_engine.begin() as setup:
        for row in rows:
            setup.execute(
                text(
                    """
                    INSERT INTO public.user_capability_grants
                        (practice_id, user_id, capability_code)
                    VALUES (:practice, :actor, 'appointment.cancel.confirm')
                    """
                ),
                row,
            )
    try:
        yield
    finally:
        with case_world.runtime.admin_engine.begin() as cleanup:
            for row in rows:
                cleanup.execute(
                    text(
                        """
                        DELETE FROM public.user_capability_grants
                        WHERE practice_id = :practice
                          AND user_id = :actor
                          AND capability_code = 'appointment.cancel.confirm'
                        """
                    ),
                    row,
                )


@contextmanager
def _context_family_authority(case_world, family, identities):
    if family == "delete":
        with _context_delete_grants(case_world, identities):
            yield
        return
    assert family == "status"
    yield


def _context_prepare_confirmation(
    client,
    headers,
    case_world,
    *,
    family,
    target_id,
    key_prefix,
):
    if family == "status":
        return _actual_status_confirmation(
            client,
            headers,
            target_id,
            {"status": "Confirmed"},
            proposal_key=f"{key_prefix}-proposal",
        )
    assert family == "delete"
    response = client.post(
        f"{RAW_APPOINTMENTS_ENDPOINT}/proposals/delete/{target_id}",
        headers=_confirmation_key_headers(headers, f"{key_prefix}-proposal"),
        json={
            "cancellation_reason": "Synthetic context isolation cancellation",
            "status_reason_code": "PATIENT_CANCELLED",
        },
    )
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["safe"] is True
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "proposal"
    assert proposal["blocks"] == []
    assert proposal["confirm_endpoint"] == (
        "/api/v1/appointments/proposals/delete/confirm"
    )
    assert proposal["delete_proposal_freshness_id"]
    assert proposal["delete_proposal_version_binding"]
    assert proposal["signed_confirmation_evidence_required"] is True
    assert proposal["signed_confirmation_evidence"]
    confirmation = deepcopy(proposal["confirm_payload"])
    assert confirmation["confirmed"] is False
    assert confirmation["delete_proposal"]["command"] == proposal["command"]
    assert confirmation["delete_proposal_freshness_id"] == (
        proposal["delete_proposal_freshness_id"]
    )
    assert confirmation["delete_proposal_version_binding"] == (
        proposal["delete_proposal_version_binding"]
    )
    assert confirmation["signed_confirmation_evidence"] == (
        proposal["signed_confirmation_evidence"]
    )
    confirmation["confirmed"] = True
    return proposal, confirmation


def _context_confirm(
    client,
    headers,
    *,
    family,
    proposal,
    confirmation,
    key_prefix,
):
    if family == "status":
        return _confirm_status(
            client,
            headers,
            f"{key_prefix}-confirm",
            confirmation,
        )
    assert family == "delete"
    return client.post(
        proposal["confirm_endpoint"],
        headers=_confirmation_key_headers(headers, f"{key_prefix}-confirm"),
        json=confirmation,
    )


def _context_assert_success_response(family, response, target_id):
    assert response.status_code == 200
    body = response.json()
    if family == "status":
        _assert_confirmed_status(body)
        assert body["appointment"]["id"] == str(target_id)
        assert body["appointment"]["status"] == "Confirmed"
        operation = _CONTEXT_STATUS_OPERATION
        action = "status_change"
        status_after = "Confirmed"
    else:
        assert family == "delete"
        assert body["schema_version"] == "raisa.delete_confirm_public_envelope.v1"
        assert body["intent"] == "confirm_delete_appointment"
        assert body["safe"] is True
        assert body["requires_confirmation"] is False
        assert body["autonomy_tier"] == "confirmed_write"
        assert body["blocks"] == []
        assert body["receipt"]["appointment_id"] == str(target_id)
        assert body["receipt"]["status"] == "Cancelled"
        assert body["receipt"]["status_reason_code"] == "PATIENT_CANCELLED"
        operation = _CONTEXT_DELETE_OPERATION
        action = "delete"
        status_after = "Cancelled"
    return operation, action, status_after


def _context_assert_success(
    case_world,
    family,
    response,
    target_id,
    *,
    practice_id,
):
    operation, action, status_after = _context_assert_success_response(
        family,
        response,
        target_id,
    )
    _assert_confirmation_graph(
        case_world.snapshot(practice_id),
        target_id=target_id,
        operation_id=operation,
        action=action,
        expected_pre_version=1,
        status_before="Booked",
        status_after=status_after,
        private_status_receipt=True,
    )


def _context_new_event_sequence():
    return {
        "events": [],
        "connection_objects": [],
        "session_objects": [],
    }


def _context_object_token(sequence, namespace, value):
    objects = sequence[f"{namespace}_objects"]
    for existing, token in objects:
        if existing is value:
            return token
    token = f"{namespace}-{len(objects) + 1}"
    objects.append((value, token))
    return token


def _context_record_event(
    sequence,
    kind,
    *,
    connection=None,
    session=None,
):
    connection_token = (
        _context_object_token(sequence, "connection", connection)
        if connection is not None
        else None
    )
    session_token = (
        _context_object_token(sequence, "session", session)
        if session is not None
        else None
    )
    sequence["events"].append((kind, connection_token, session_token))
    return len(sequence["events"]) - 1


def _context_event_index(
    observation,
    kind,
    *,
    connection=None,
    session=None,
):
    sequence = observation["sequence"]
    connection_token = (
        _context_object_token(sequence, "connection", connection)
        if connection is not None
        else None
    )
    session_token = (
        _context_object_token(sequence, "session", session)
        if session is not None
        else None
    )
    matches = [
        index
        for index in range(
            observation["sequence_start"],
            observation["sequence_stop"],
        )
        if sequence["events"][index][0] == kind
        and (
            connection is None
            or sequence["events"][index][1] == connection_token
        )
        and (session is None or sequence["events"][index][2] == session_token)
    ]
    assert len(matches) == 1
    return matches[0]


def _context_assert_no_event(observation, kind):
    sequence = observation["sequence"]
    assert not any(
        sequence["events"][index][0] == kind
        for index in range(
            observation["sequence_start"],
            observation["sequence_stop"],
        )
    )


@contextmanager
def _context_command_connection_probe(engine, sequence):
    pool = _context_assert_reviewed_pool(engine)
    assert tuple(sequence) == (
        "events",
        "connection_objects",
        "session_objects",
    )
    state = {
        "sequence": sequence,
        "sequence_start": len(sequence["events"]),
        "connects": [],
        "checkouts": [],
        "checkins": [],
        "invalidations": [],
        "command_begins": [],
        "command_ends": [],
        "command_commits": [],
        "command_rollbacks": [],
        "command_soft_rollbacks": [],
    }

    def connected(dbapi_connection, connection_record):
        state["connects"].append(dbapi_connection)
        _context_record_event(
            sequence,
            "connect",
            connection=dbapi_connection,
        )

    def checked_out(dbapi_connection, connection_record, connection_proxy):
        state["checkouts"].append(dbapi_connection)
        _context_record_event(
            sequence,
            "checkout",
            connection=dbapi_connection,
        )

    def checked_in(dbapi_connection, connection_record):
        state["checkins"].append(dbapi_connection)
        _context_record_event(
            sequence,
            "checkin",
            connection=dbapi_connection,
        )

    def invalidated(dbapi_connection, connection_record, exception):
        state["invalidations"].append(("invalidate", dbapi_connection))
        _context_record_event(
            sequence,
            "invalidate",
            connection=dbapi_connection,
        )

    def soft_invalidated(dbapi_connection, connection_record, exception):
        state["invalidations"].append(("soft_invalidate", dbapi_connection))
        _context_record_event(
            sequence,
            "soft_invalidate",
            connection=dbapi_connection,
        )

    def is_command_session(session):
        return (
            session.get_bind() is engine
            and session.expire_on_commit is False
        )

    def command_began(session, transaction, connection):
        if not is_command_session(session):
            return
        if getattr(transaction, "parent", None) is not None:
            return
        fairy = connection.connection
        dbapi_connection = getattr(fairy, "dbapi_connection", None)
        assert dbapi_connection is not None
        state["command_begins"].append((session, dbapi_connection))
        _context_record_event(
            sequence,
            "begin",
            connection=dbapi_connection,
            session=session,
        )

    def command_committed(session):
        if not is_command_session(session):
            return
        state["command_commits"].append(session)
        _context_record_event(sequence, "commit", session=session)

    def command_rolled_back(session):
        if not is_command_session(session):
            return
        state["command_rollbacks"].append(session)
        _context_record_event(sequence, "rollback", session=session)

    def command_ended(session, transaction):
        if not is_command_session(session):
            return
        if getattr(transaction, "parent", None) is None:
            state["command_ends"].append(session)
            _context_record_event(sequence, "end", session=session)

    def command_soft_rolled_back(session, previous_transaction):
        if not is_command_session(session):
            return
        if getattr(previous_transaction, "parent", None) is None:
            state["command_soft_rollbacks"].append(session)
            _context_record_event(sequence, "soft_rollback", session=session)

    listeners = (
        (pool, "connect", connected),
        (pool, "checkout", checked_out),
        (pool, "checkin", checked_in),
        (pool, "invalidate", invalidated),
        (pool, "soft_invalidate", soft_invalidated),
        (Session, "after_begin", command_began),
        (Session, "after_commit", command_committed),
        (Session, "after_rollback", command_rolled_back),
        (Session, "after_transaction_end", command_ended),
        (Session, "after_soft_rollback", command_soft_rolled_back),
    )
    for target, name, listener in listeners:
        event.listen(target, name, listener)
    try:
        yield state
    finally:
        for target, name, listener in reversed(listeners):
            event.remove(target, name, listener)
        state["sequence_stop"] = len(sequence["events"])


def _context_assert_command_closed(engine, observation, completion):
    assert completion in {"commit", "rollback"}
    assert len(observation["command_begins"]) == 1
    session, dbapi_connection = observation["command_begins"][0]
    assert observation["command_ends"] == [session]
    assert not session.in_transaction()
    assert sum(item is dbapi_connection for item in observation["checkouts"]) == 1
    assert sum(item is dbapi_connection for item in observation["checkins"]) == 1
    assert observation["invalidations"] == []
    _context_assert_no_event(observation, "invalidate")
    _context_assert_no_event(observation, "soft_invalidate")
    assert engine.pool.checkedout() == 0

    checkout_index = _context_event_index(
        observation,
        "checkout",
        connection=dbapi_connection,
    )
    begin_index = _context_event_index(
        observation,
        "begin",
        connection=dbapi_connection,
        session=session,
    )
    checkin_index = _context_event_index(
        observation,
        "checkin",
        connection=dbapi_connection,
    )
    end_index = _context_event_index(
        observation,
        "end",
        session=session,
    )
    if any(item is dbapi_connection for item in observation["connects"]):
        connect_index = _context_event_index(
            observation,
            "connect",
            connection=dbapi_connection,
        )
        assert connect_index < checkout_index

    # Pinned SQLAlchemy 2.0.50 session.py SHA-256
    # b12db5f1bc4056e8be239a9557b0124c136a8addd139a3a3efce1668c032fbd3
    # dispatches after_commit/after_rollback before close(), closes the
    # connection at lines 1422-1423, dispatches after_transaction_end at
    # line 1436, then dispatches after_soft_rollback at line 1399.
    if completion == "commit":
        assert observation["command_commits"] == [session]
        assert observation["command_rollbacks"] == []
        assert observation["command_soft_rollbacks"] == []
        commit_index = _context_event_index(
            observation,
            "commit",
            session=session,
        )
        assert (
            checkout_index
            < begin_index
            < commit_index
            < checkin_index
            < end_index
        )
    else:
        assert observation["command_commits"] == []
        assert observation["command_rollbacks"] == [session]
        assert observation["command_soft_rollbacks"] == [session]
        rollback_index = _context_event_index(
            observation,
            "rollback",
            session=session,
        )
        soft_rollback_index = _context_event_index(
            observation,
            "soft_rollback",
            session=session,
        )
        assert (
            checkout_index
            < begin_index
            < rollback_index
            < checkin_index
            < end_index
            < soft_rollback_index
        )
    return dbapi_connection


def _context_assert_reuse_handoff(
    p_observation,
    q_observation,
    p_connection,
    q_connection,
):
    assert p_observation["sequence"] is q_observation["sequence"]
    assert p_observation["sequence_stop"] == q_observation["sequence_start"]
    assert q_connection is p_connection
    q_session, observed_q_connection = q_observation["command_begins"][0]
    assert observed_q_connection is q_connection
    p_checkin_index = _context_event_index(
        p_observation,
        "checkin",
        connection=p_connection,
    )
    q_checkout_index = _context_event_index(
        q_observation,
        "checkout",
        connection=q_connection,
    )
    q_begin_index = _context_event_index(
        q_observation,
        "begin",
        connection=q_connection,
        session=q_session,
    )
    assert p_checkin_index < q_checkout_index < q_begin_index


def _context_assert_bound_command(trace, family):
    trace.assert_bound_reads()
    if family == "status":
        command_transactions = trace.assert_first_table("practices")
        assert len(command_transactions) == 1
        assert ("appointments", True) in command_transactions[0]["tables"]
        assert ("appointment_command_idempotency", True) in (
            command_transactions[0]["tables"]
        )
    else:
        assert family == "delete"
        first_user_transactions = trace.assert_first_table("users")
        command_transactions = [
            record
            for record in first_user_transactions
            if ("user_capability_grants", True) in record["tables"]
        ]
        assert len(command_transactions) == 1
        assert ("appointments", True) in command_transactions[0]["tables"]
        assert ("appointment_command_idempotency", True) in (
            command_transactions[0]["tables"]
        )


def _context_fault_details(family, key_prefix):
    key = f"{key_prefix}-confirm"
    if family == "status":
        return (
            _CONTEXT_STATUS_OPERATION,
            hash_idempotency_key(
                key,
                appointment_routes._status_confirm_domain_secret("idempotency"),
            ),
            StatusConfirmPhysicalError,
            "Confirmed",
            "status_change",
        )
    assert family == "delete"
    return (
        _CONTEXT_DELETE_OPERATION,
        hash_idempotency_key(
            key,
            appointment_routes._delete_confirm_domain_secret("idempotency"),
        ),
        DeleteConfirmPhysicalError,
        "Cancelled",
        "delete",
    )


@contextmanager
def _context_precommit_abort(case_world, *, family, target_id, key_prefix):
    operation, key_hash, error_type, status_after, action = _context_fault_details(
        family, key_prefix
    )
    boundary = {
        "hook_reached": threading.Event(),
        "rollback_observed": threading.Event(),
    }

    def fail_after_complete_flush(session):
        if session.get_bind() is not case_world.runtime.engine:
            return
        if session.expire_on_commit is not False:
            return
        session.flush()
        receipt = session.execute(
            text(
                """
                SELECT to_jsonb(t)
                FROM public.appointment_command_idempotency t
                WHERE t.practice_id = :practice
                  AND t.operation_id = :operation
                  AND t.idempotency_key_hash = :key_hash
                """
            ),
            {
                "practice": case_world.p,
                "operation": operation,
                "key_hash": key_hash,
            },
        ).scalar_one_or_none()
        if receipt is None:
            return
        target = session.execute(
            text(
                """
                SELECT to_jsonb(t) FROM public.appointments t
                WHERE t.practice_id = :practice AND t.id = :target
                """
            ),
            {"practice": case_world.p, "target": target_id},
        ).scalar_one()
        audit = session.execute(
            text(
                """
                SELECT to_jsonb(t) FROM public.appointment_audit_log t
                WHERE t.practice_id = :practice AND t.id = :audit
                """
            ),
            {"practice": case_world.p, "audit": receipt["audit_log_id"]},
        ).scalar_one()
        assert receipt["state"] == "completed"
        assert receipt["result_kind"] == "confirmed_write"
        assert receipt["operation_id"] == operation
        assert receipt["idempotency_key_hash"] == key_hash
        assert receipt["target_appointment_id"] == str(target_id)
        assert receipt["completed_receipt_version"] == 1
        assert receipt["pre_state_version"] == 1
        assert receipt["post_state_version"] == 2
        assert receipt["response_body_canonical_bytes"]
        assert receipt["audit_log_id"] == audit["id"]
        assert target["status"] == status_after
        assert target["appointment_state_version"] == 2
        assert audit["appointment_id"] == str(target_id)
        assert audit["command_id"] == receipt["id"]
        assert audit["action"] == action
        assert audit["status_before"] == "Booked"
        assert audit["status_after"] == status_after
        if family == "delete":
            assert receipt["authority_generation"] >= 1
            assert audit["audit_contract_version"] == 1
            assert audit["authority_generation"] == receipt["authority_generation"]
        boundary["session"] = session
        boundary["staged"] = MappingProxyType(
            {
                "appointments": json.dumps(
                    [target], sort_keys=True, separators=(",", ":")
                ),
                "appointment_audit_log": json.dumps(
                    [audit], sort_keys=True, separators=(",", ":")
                ),
                "appointment_command_idempotency": json.dumps(
                    [receipt], sort_keys=True, separators=(",", ":")
                ),
            }
        )
        boundary["hook_reached"].set()
        raise error_type("authored synthetic pre-commit context rollback")

    def observe_rollback(session):
        if session is boundary.get("session"):
            boundary["rollback_observed"].set()

    event.listen(Session, "before_commit", fail_after_complete_flush)
    event.listen(Session, "after_rollback", observe_rollback)
    try:
        yield boundary
    finally:
        event.remove(Session, "after_rollback", observe_rollback)
        event.remove(Session, "before_commit", fail_after_complete_flush)


def _context_assert_aborted(boundary, before, response, family):
    assert boundary["hook_reached"].is_set()
    assert boundary["rollback_observed"].is_set()
    staged = boundary["staged"]
    assert tuple(staged) == SNAPSHOT_TABLES
    assert all(_snapshot_rows(staged, table) for table in SNAPSHOT_TABLES)
    assert all(staged[table] != before[table] for table in SNAPSHOT_TABLES)
    if family == "status":
        expected = {
            "detail": {
                "code": "status_confirm_transaction_unavailable",
                "message": "The status confirmation did not commit.",
            }
        }
    else:
        expected = {
            "detail": {
                "code": "delete_confirm_transaction_unavailable",
                "message": "The delete confirmation did not commit.",
            }
        }
    assert response.status_code == 503
    assert response.json() == expected


def _context_cross_tenant_proposal(client, q_headers, *, family, target_id, key_prefix):
    if family == "status":
        response = client.post(
            f"{STATUS_PROPOSAL_ENDPOINT}/{target_id}",
            headers=_confirmation_key_headers(q_headers, f"{key_prefix}-cross"),
            json={"status": "Arrived"},
        )
    else:
        assert family == "delete"
        response = client.post(
            f"{RAW_APPOINTMENTS_ENDPOINT}/proposals/delete/{target_id}",
            headers=_confirmation_key_headers(q_headers, f"{key_prefix}-cross"),
            json={
                "cancellation_reason": "Synthetic inaccessible tenant target",
                "status_reason_code": "PATIENT_CANCELLED",
            },
        )
    assert response.status_code == 404
    assert response.json() == {"detail": "Appointment not found"}
    assert str(target_id) not in response.text
    return response


_CONTEXT_FRESH_CASES = [
    pytest.param("status", id="APT-T1-http-status-fresh-command-context"),
    pytest.param("delete", id="APT-T1-http-delete-fresh-command-context"),
]


@pytest.mark.parametrize("family", _CONTEXT_FRESH_CASES)
def test_context_fresh_status_and_delete_commands_bind_before_protected_reads(
    appointment_http_client,
    case_world,
    family,
):
    client, p_headers = appointment_http_client
    target = case_world.row(
        f"context-fresh-{family}",
        location_id=case_world.l1,
    )
    _insert_and_commit(case_world, target)
    authority = [(case_world.p, case_world.actor)]
    with _context_family_authority(case_world, family, authority):
        before = case_world.snapshot()
        proposal, confirmation = _context_prepare_confirmation(
            client,
            p_headers,
            case_world,
            family=family,
            target_id=target["id"],
            key_prefix=f"context-fresh-{family}",
        )
        assert case_world.snapshot() == before
        engine = _context_assert_idle_pool(case_world)
        engine.dispose()
        _context_assert_reviewed_pool(engine)
        sequence = _context_new_event_sequence()
        with _tenant_sql_trace(engine, case_world.p) as trace:
            with _context_command_connection_probe(
                engine,
                sequence,
            ) as observation:
                response = _context_confirm(
                    client,
                    p_headers,
                    family=family,
                    proposal=proposal,
                    confirmation=confirmation,
                    key_prefix=f"context-fresh-{family}",
                )
        _context_assert_bound_command(trace, family)
        command_connection = _context_assert_command_closed(
            engine,
            observation,
            "commit",
        )
        assert any(item is command_connection for item in observation["connects"])
        _context_event_index(
            observation,
            "connect",
            connection=command_connection,
        )
        _context_assert_success(
            case_world,
            family,
            response,
            target["id"],
            practice_id=case_world.p,
        )


_CONTEXT_REUSE_CASES = [
    pytest.param(
        "status",
        "commit",
        id="APT-T1-http-status-pooled-q-after-p-commit",
    ),
    pytest.param(
        "status",
        "rollback",
        id="APT-T1-http-status-pooled-q-after-p-rollback",
    ),
    pytest.param(
        "delete",
        "commit",
        id="APT-T1-http-delete-pooled-q-after-p-commit",
    ),
    pytest.param(
        "delete",
        "rollback",
        id="APT-T1-http-delete-pooled-q-after-p-rollback",
    ),
]


@pytest.mark.parametrize("family,completion", _CONTEXT_REUSE_CASES)
def test_context_q_command_rebinds_reused_p_physical_connection(
    appointment_http_client,
    case_world,
    family,
    completion,
):
    client, p_headers = appointment_http_client
    q_headers = _context_headers(
        case_world,
        practice_id=case_world.q,
        actor_id=case_world.actor_q,
    )
    p_target = case_world.row(
        f"context-p-{family}-{completion}",
        location_id=case_world.l1,
    )
    q_target = case_world.row(
        f"context-q-{family}-{completion}",
        practice_id=case_world.q,
        practitioner_id=case_world.rq,
        location_id=case_world.lq,
    )
    _insert_and_commit(case_world, p_target)
    _insert_and_commit(case_world, q_target)
    authority = [
        (case_world.p, case_world.actor),
        (case_world.q, case_world.actor_q),
    ]
    with _context_family_authority(case_world, family, authority):
        p_proposal, p_confirmation = _context_prepare_confirmation(
            client,
            p_headers,
            case_world,
            family=family,
            target_id=p_target["id"],
            key_prefix=f"context-p-{family}-{completion}",
        )
        q_proposal, q_confirmation = _context_prepare_confirmation(
            client,
            q_headers,
            case_world,
            family=family,
            target_id=q_target["id"],
            key_prefix=f"context-q-{family}-{completion}",
        )
        p_before = case_world.snapshot(case_world.p)
        engine = _context_assert_idle_pool(case_world)
        engine.dispose()
        _context_assert_reviewed_pool(engine)
        sequence = _context_new_event_sequence()

        with _tenant_sql_trace(engine, case_world.p) as p_trace:
            with _context_command_connection_probe(
                engine,
                sequence,
            ) as p_observation:
                if completion == "commit":
                    p_response = _context_confirm(
                        client,
                        p_headers,
                        family=family,
                        proposal=p_proposal,
                        confirmation=p_confirmation,
                        key_prefix=f"context-p-{family}-{completion}",
                    )
                    p_boundary = None
                else:
                    with _context_precommit_abort(
                        case_world,
                        family=family,
                        target_id=p_target["id"],
                        key_prefix=f"context-p-{family}-{completion}",
                    ) as p_boundary:
                        p_response = _context_confirm(
                            client,
                            p_headers,
                            family=family,
                            proposal=p_proposal,
                            confirmation=p_confirmation,
                            key_prefix=f"context-p-{family}-{completion}",
                        )
        _context_assert_bound_command(p_trace, family)
        p_command_connection = _context_assert_command_closed(
            engine,
            p_observation,
            completion,
        )
        assert any(item is p_command_connection for item in p_observation["connects"])
        _context_event_index(
            p_observation,
            "connect",
            connection=p_command_connection,
        )
        if completion == "commit":
            _context_assert_success_response(
                family,
                p_response,
                p_target["id"],
            )
        else:
            _context_assert_aborted(p_boundary, p_before, p_response, family)
        assert engine.pool.checkedout() == 0

        with _tenant_sql_trace(engine, case_world.q) as q_trace:
            with _context_command_connection_probe(
                engine,
                sequence,
            ) as q_observation:
                q_response = _context_confirm(
                    client,
                    q_headers,
                    family=family,
                    proposal=q_proposal,
                    confirmation=q_confirmation,
                    key_prefix=f"context-q-{family}-{completion}",
                )
        _context_assert_bound_command(q_trace, family)
        q_command_connection = _context_assert_command_closed(
            engine,
            q_observation,
            "commit",
        )
        _context_assert_reuse_handoff(
            p_observation,
            q_observation,
            p_command_connection,
            q_command_connection,
        )
        assert q_observation["connects"] == []
        _context_assert_success_response(family, q_response, q_target["id"])

        if completion == "commit":
            _context_assert_success(
                case_world,
                family,
                p_response,
                p_target["id"],
                practice_id=case_world.p,
            )
        else:
            assert case_world.snapshot(case_world.p) == p_before
        _context_assert_success(
            case_world,
            family,
            q_response,
            q_target["id"],
            practice_id=case_world.q,
        )
        p_before_cross = case_world.snapshot(case_world.p)
        q_before_cross = case_world.snapshot(case_world.q)
        with _tenant_sql_trace(engine, case_world.q) as cross_trace:
            _context_cross_tenant_proposal(
                client,
                q_headers,
                family=family,
                target_id=p_target["id"],
                key_prefix=f"context-q-{family}-{completion}",
            )
        cross_trace.assert_bound_reads()
        assert case_world.snapshot(case_world.p) == p_before_cross
        assert case_world.snapshot(case_world.q) == q_before_cross
        assert _snapshot_row(
            p_before_cross, "appointments", p_target["id"]
        )["practice_id"] == str(case_world.p)
        assert _snapshot_row(
            q_before_cross, "appointments", q_target["id"]
        )["practice_id"] == str(case_world.q)
        assert engine.pool.checkedout() == 0


RACE_CREATE_OPERATION = "confirmAppointmentCreateProposal"
RACE_UPDATE_OPERATION = "confirmAppointmentUpdateProposal"
RACE_STATUS_OPERATION = STATUS_CONFIRM_OPERATION
RACE_RAW_STATUS_FAMILY = "raw-status-patch"


class CommandRaceCommitAbort(RuntimeError):
    """Authored test fault propagated by routes without a commit mapper."""


def _race_key_hash(operation, key):
    if operation == RACE_STATUS_OPERATION:
        secret = appointment_routes._status_confirm_domain_secret("idempotency")
    else:
        assert operation in {RACE_CREATE_OPERATION, RACE_UPDATE_OPERATION}
        secret = appointment_routes._staff_create_confirm_idempotency_secret()
    return hash_idempotency_key(key, secret)


def _race_command_spec(case_world, label, operation, key, *, abort=False):
    return MappingProxyType(
        {
            "kind": "receipt",
            "label": label,
            "practice_id": case_world.p,
            "operation": operation,
            "key": key,
            "key_hash": _race_key_hash(operation, key),
            "abort": abort,
        }
    )


def _race_raw_status_spec(
    case_world,
    label,
    target_id,
    *,
    status_before,
    status_after,
    orm_preflush_version=1,
    expected_version=2,
):
    return MappingProxyType(
        {
            "kind": "raw-status",
            "label": label,
            "practice_id": case_world.p,
            "operation": RACE_RAW_STATUS_FAMILY,
            "key": None,
            "key_hash": None,
            "abort": False,
            "target_id": target_id,
            "status_before": status_before,
            "status_after": status_after,
            "orm_preflush_version": orm_preflush_version,
            "expected_version": expected_version,
        }
    )


def _race_status_value(value):
    return getattr(value, "value", value)


def _race_create_proposal(
    client,
    headers,
    case_world,
    *,
    proposal_key,
    patient_label,
    practitioner_id,
    location_id,
    start,
    minutes=30,
):
    before = case_world.snapshot()
    response = client.post(
        CREATE_PROPOSAL_ENDPOINT,
        headers=_confirmation_key_headers(headers, proposal_key),
        json={
            "patient_name_provisional": patient_label,
            "practitioner_id": str(practitioner_id),
            "location_id": None if location_id is None else str(location_id),
            "start_time": start.isoformat(),
            "duration_minutes": minutes,
        },
    )
    assert response.status_code == 200
    proposal = response.json()
    assert proposal["intent"] == "create_appointment"
    assert proposal["safe"] is True
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "proposal"
    assert proposal["blocks"] == []
    assert proposal["confirm_endpoint"] == CREATE_CONFIRM_ENDPOINT
    assert proposal["create_proposal_freshness_id"]
    assert proposal["signed_confirmation_evidence_required"] is True
    assert proposal["signed_confirmation_evidence"]
    confirmation = deepcopy(proposal["confirm_payload"])
    assert confirmation["confirmed"] is False
    assert confirmation["create_proposal"]["command"] == proposal["command"]
    assert confirmation["create_proposal_freshness_id"] == proposal[
        "create_proposal_freshness_id"
    ]
    assert confirmation["signed_confirmation_evidence"] == proposal[
        "signed_confirmation_evidence"
    ]
    confirmation["confirmed"] = True
    assert case_world.snapshot() == before
    return proposal, confirmation


def _race_create_call(client, headers, proposal, confirmation, key):
    return lambda: _confirm_create(
        client,
        headers,
        proposal["confirm_endpoint"],
        key,
        confirmation,
    )


@contextmanager
def _race_before_commit_gate(case_world, specs, deadline):
    """Hold one exact real command after its complete graph is staged."""
    labels = tuple(spec["label"] for spec in specs)
    assert labels == tuple(dict.fromkeys(labels))
    state = {
        "lock": threading.Lock(),
        "release_first": threading.Event(),
        "staged_events": {label: threading.Event() for label in labels},
        "calls": {label: 0 for label in labels},
        "sessions": {},
        "staged_connections": {},
        "pids": {},
        "blockers": {},
        "staged": {},
        "commits": [],
        "physical_rollbacks": [],
        "connection_rollbacks": [],
        "soft_rollbacks": [],
    }

    def match(session):
        matches = []
        for spec in specs:
            for candidate in session.identity_map.values():
                table = getattr(type(candidate), "__tablename__", None)
                if spec["kind"] == "receipt":
                    if table != "appointment_command_idempotency":
                        continue
                    matched = (
                        candidate.practice_id == spec["practice_id"]
                        and candidate.operation_id == spec["operation"]
                        and candidate.idempotency_key_hash == spec["key_hash"]
                    )
                else:
                    assert spec["kind"] == "raw-status"
                    if table != "appointments":
                        continue
                    matched = (
                        candidate.id == spec["target_id"]
                        and candidate.practice_id == spec["practice_id"]
                        and _race_status_value(candidate.status)
                        == spec["status_after"]
                        # _write_audit() has already flushed the physical
                        # UPDATE, whose installed BEFORE UPDATE trigger owns
                        # OLD+1.  The ORM identity is not configured with a
                        # server_onupdate fetch and still carries OLD here;
                        # the transaction-local SQL read below must see NEW.
                        and candidate.appointment_state_version
                        == spec["orm_preflush_version"]
                    )
                if matched:
                    matches.append((spec, candidate))
        assert len(matches) <= 1, "one Session cannot own two reviewed race commands"
        return None if not matches else matches[0]

    def before_commit(session):
        if session.get_bind() is not case_world.runtime.engine:
            return
        matched = match(session)
        if matched is None:
            return
        spec, marked = matched
        label = spec["label"]

        # SQLAlchemy 2.0.50 invokes before_commit before its automatic flush.
        # Flush explicitly, then inspect the actual transaction-local graph.
        session.flush()
        if spec["kind"] == "receipt":
            receipt = session.execute(
                text(
                    """
                    SELECT to_jsonb(t)
                    FROM public.appointment_command_idempotency AS t
                    WHERE t.id = :receipt AND t.practice_id = :practice
                    """
                ),
                {"receipt": marked.id, "practice": case_world.p},
            ).scalar_one()
            target_id = receipt["target_appointment_id"]
        else:
            receipt = None
            target_id = spec["target_id"]
        target = session.execute(
            text(
                """
                SELECT to_jsonb(t)
                FROM public.appointments AS t
                WHERE t.id = :target AND t.practice_id = :practice
                """
            ),
            {"target": target_id, "practice": case_world.p},
        ).scalar_one()
        if spec["kind"] == "receipt":
            audit = session.execute(
                text(
                    """
                    SELECT to_jsonb(t)
                    FROM public.appointment_audit_log AS t
                    WHERE t.id = :audit AND t.practice_id = :practice
                    """
                ),
                {"audit": receipt["audit_log_id"], "practice": case_world.p},
            ).scalar_one()
        else:
            audit = session.execute(
                text(
                    """
                    SELECT to_jsonb(t)
                    FROM public.appointment_audit_log AS t
                    WHERE t.practice_id = :practice
                      AND t.appointment_id = :target
                      AND t.action = 'status_change'
                      AND t.command_id IS NULL
                    """
                ),
                {
                    "practice": case_world.p,
                    "target": spec["target_id"],
                },
            ).scalar_one()
        backend = session.execute(
            text(
                """
                SELECT pg_backend_pid() AS pid,
                       pg_blocking_pids(pg_backend_pid()) AS blockers
                """
            )
        ).mappings().one()

        if spec["kind"] == "receipt":
            assert receipt["operation_id"] == spec["operation"]
            assert receipt["idempotency_key_hash"] == spec["key_hash"]
            assert receipt["state"] == "completed"
            assert receipt["result_kind"] == "confirmed_write"
            assert receipt["target_appointment_id"] == target["id"]
            assert receipt["audit_log_id"] == audit["id"]
            assert audit["command_id"] == receipt["id"]
        else:
            assert target["id"] == str(spec["target_id"])
            assert target["status"] == spec["status_after"]
            assert target["appointment_state_version"] == spec["expected_version"]
            assert audit["status_before"] == spec["status_before"]
            assert audit["status_after"] == spec["status_after"]
            assert audit["command_id"] is None
        assert audit["appointment_id"] == target["id"]
        with state["lock"]:
            assert state["calls"][label] == 0
            state["calls"][label] += 1
        with state["lock"]:
            state["sessions"][label] = session
            state["staged_connections"][label] = session.connection()
            state["pids"][label] = backend["pid"]
            state["blockers"][label] = tuple(backend["blockers"])
            state["staged"][label] = MappingProxyType(
                {"appointment": target, "audit": audit, "receipt": receipt}
            )
        state["staged_events"][label].set()

        if label == "first":
            if not state["release_first"].wait(_remaining(deadline)):
                raise AssertionError("first command gate exceeded the one test deadline")
            if spec["abort"]:
                if spec["operation"] == RACE_STATUS_OPERATION:
                    raise StatusConfirmPhysicalError(
                        "authored command-race abort after complete staging"
                    )
                raise CommandRaceCommitAbort(
                    "authored create-command abort after complete staging"
                )

    def label_for(session):
        with state["lock"]:
            labels_for_session = [
                label
                for label, candidate in state["sessions"].items()
                if candidate is session
            ]
        assert len(labels_for_session) <= 1
        return None if not labels_for_session else labels_for_session[0]

    def after_commit(session):
        label = label_for(session)
        if label is not None:
            with state["lock"]:
                state["commits"].append(label)

    def connection_rollback(connection):
        # A propagated create commit fault reaches request-dependency close().
        # SQLAlchemy closes the exact Connection transaction there without
        # emitting Session.after_rollback/after_soft_rollback.  Binding the
        # Connection captured at the staged boundary proves the real rollback
        # without adding a test-side Session.rollback().
        with state["lock"]:
            labels_for_connection = [
                label
                for label, candidate in state["staged_connections"].items()
                if candidate is connection
            ]
        assert len(labels_for_connection) <= 1
        if labels_for_connection:
            with state["lock"]:
                state["connection_rollbacks"].append(labels_for_connection[0])

    def after_rollback(session):
        label = label_for(session)
        if label is not None:
            with state["lock"]:
                state["physical_rollbacks"].append(label)

    def after_soft_rollback(session, previous_transaction):
        label = label_for(session)
        if label is not None:
            with state["lock"]:
                state["soft_rollbacks"].append(
                    (label, previous_transaction.parent is not None)
                )

    listeners = (
        (Session, "before_commit", before_commit),
        (Session, "after_commit", after_commit),
        (case_world.runtime.engine, "rollback", connection_rollback),
        (Session, "after_rollback", after_rollback),
        (Session, "after_soft_rollback", after_soft_rollback),
    )
    for target, name, listener in listeners:
        event.listen(target, name, listener)
    try:
        yield state
    finally:
        state["release_first"].set()
        for target, name, listener in reversed(listeners):
            event.remove(target, name, listener)
        with state["lock"]:
            state["sessions"].clear()
            state["staged_connections"].clear()


def _race_wait_for_event(event, finished, result, deadline, message):
    while not event.is_set() and _remaining(deadline) > 0:
        if finished.is_set():
            break
        event.wait(min(0.02, _remaining(deadline)))
    if "error" in result:
        raise result["error"]
    assert event.is_set(), message


def _run_command_race(
    case_world,
    first_call,
    second_call,
    specs,
    *,
    second_boundary,
    expected_first_error=None,
):
    """Run two real HTTP commands under one absolute deadline."""
    deadline = time.monotonic() + case_world.runtime.test_deadline_seconds
    results = [{}, {}]
    finished = [threading.Event(), threading.Event()]
    threads = []

    def start(index, call):
        def run():
            try:
                results[index]["response"] = call()
            except BaseException as error:
                results[index]["error"] = error
            finally:
                finished[index].set()

        thread = threading.Thread(
            target=run,
            name=f"appointment-command-race-{index + 1}",
            daemon=False,
        )
        thread.start()
        threads.append(thread)
        return thread

    observation = None
    with _race_before_commit_gate(case_world, specs, deadline) as gate:
        start(0, first_call)
        try:
            assert all(not thread.daemon for thread in threads)
            phase_deadline = deadline - case_world.runtime.wait_timeout_seconds
            _race_wait_for_event(
                gate["staged_events"]["first"],
                finished[0],
                results[0],
                phase_deadline,
                "first real command did not reach its staged commit boundary",
            )
            first_pid = gate["pids"]["first"]
            assert gate["blockers"]["first"] == ()

            start(1, second_call)
            assert all(not thread.daemon for thread in threads)
            if second_boundary == "database-wait":
                waiting_pid = _observe_application_wait_for_blocker(
                    case_world,
                    first_pid,
                    finished[1],
                    deadline=phase_deadline,
                )
                assert waiting_pid != first_pid
                assert not finished[1].is_set()
                observation = MappingProxyType(
                    {"waiting_pid": waiting_pid, "blocking_pid": first_pid}
                )
            else:
                assert second_boundary in {
                    "completed-command",
                    "early-public-result",
                }
                _race_wait_for_event(
                    finished[1],
                    finished[1],
                    results[1],
                    phase_deadline,
                    "second public command did not finish while first remained staged",
                )
                if second_boundary == "completed-command":
                    assert gate["staged_events"]["second"].is_set()
                    assert gate["blockers"]["second"] == ()
                else:
                    assert not gate["staged_events"]["second"].is_set()
            assert not finished[0].is_set(), (
                "first command left its staged boundary before the scheduled release"
            )
            gate["release_first"].set()
        finally:
            gate["release_first"].set()
            for thread in threads:
                thread.join(timeout=_remaining(deadline))
            assert not any(thread.is_alive() for thread in threads), (
                "command writer remains alive; outer database disposal must not race it"
            )
            assert all(finished[index].is_set() for index in range(len(threads)))

    if expected_first_error is None:
        if "error" in results[0]:
            raise results[0]["error"]
        assert "response" in results[0]
        first_result = results[0]["response"]
    else:
        assert "response" not in results[0]
        first_result = results[0].get("error")
        assert isinstance(first_result, expected_first_error)
    if "error" in results[1]:
        raise results[1]["error"]
    assert "response" in results[1]
    return first_result, results[1]["response"], gate, observation


def _assert_race_gate_outcomes(gate, *, first, second):
    assert gate["calls"]["first"] == 1
    if first == "commit":
        assert gate["commits"].count("first") == 1
        assert "first" not in gate["physical_rollbacks"]
        assert "first" not in gate["connection_rollbacks"]
        assert not [item for item in gate["soft_rollbacks"] if item[0] == "first"]
    elif first == "abort":
        assert "first" not in gate["commits"]
        assert gate["physical_rollbacks"].count("first") == 1
        assert gate["connection_rollbacks"].count("first") == 1
        assert [item for item in gate["soft_rollbacks"] if item[0] == "first"] == [
            ("first", False)
        ]
    else:
        assert first == "propagated-abort"
        assert "first" not in gate["commits"]
        # Session.close() owns this cleanup path; only the exact Connection
        # rollback event is expected for SQLAlchemy 2.0.50.
        assert "first" not in gate["physical_rollbacks"]
        assert gate["connection_rollbacks"].count("first") == 1
        assert not [item for item in gate["soft_rollbacks"] if item[0] == "first"]

    if second == "commit":
        assert gate["calls"]["second"] == 1
        assert gate["commits"].count("second") == 1
        assert "second" not in gate["physical_rollbacks"]
        assert "second" not in gate["connection_rollbacks"]
        assert not [item for item in gate["soft_rollbacks"] if item[0] == "second"]
    else:
        assert second in {"blocked", "early-blocked"}
        assert gate["calls"]["second"] == 0
        assert "second" not in gate["commits"]
        assert "second" not in gate["physical_rollbacks"]
        assert "second" not in gate["connection_rollbacks"]
        assert not [item for item in gate["soft_rollbacks"] if item[0] == "second"]


def _race_assert_status_abort(response):
    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "status_confirm_transaction_unavailable",
            "message": "The status confirmation did not commit.",
        }
    }


def _race_assert_conflict(response, family, *, create_revalidation=False):
    assert response.status_code == 200
    body = response.json()
    if family == "create":
        _assert_blocked_create_confirmation(body)
        assert body["intent"] == "confirm_create_appointment"
    elif family == "update":
        _assert_blocked_confirmation(body, "confirm_update_appointment")
    else:
        assert family == "status"
        _assert_blocked_confirmation(body, "confirm_status_appointment")
    block_codes = [item["code"] for item in body["blocks"]]
    if create_revalidation:
        assert family == "create"
        assert block_codes == [
            "appointment_conflict",
            "create_proposal_revalidation_blocked",
        ]
    else:
        assert block_codes[0] == "appointment_conflict"
    assert any(item["code"] == "appointment_conflict" for item in body["blocks"])
    assert body["appointment"] is None
    return body


def _race_assert_graph(
    snapshot,
    spec,
    *,
    target_id,
    action,
    expected_version,
    actual_body,
    status_before=None,
    status_after=None,
    private_status_receipt=False,
):
    receipts = [
        row
        for row in _snapshot_rows(snapshot, "appointment_command_idempotency")
        if row["operation_id"] == spec["operation"]
        and row["idempotency_key_hash"] == spec["key_hash"]
    ]
    assert len(receipts) == 1
    receipt = receipts[0]
    audits = [
        row
        for row in _snapshot_rows(snapshot, "appointment_audit_log")
        if row["command_id"] == receipt["id"]
    ]
    assert len(audits) == 1
    audit = audits[0]
    target = _snapshot_row(snapshot, "appointments", target_id)
    assert receipt["state"] == "completed"
    assert receipt["result_kind"] == "confirmed_write"
    assert receipt["response_status_code"] == 200
    assert receipt["response_body_json"] == actual_body
    assert receipt["target_appointment_id"] == str(target_id)
    assert receipt["audit_log_id"] == audit["id"]
    assert audit["appointment_id"] == str(target_id)
    assert audit["action"] == action
    assert target["appointment_state_version"] == expected_version
    if private_status_receipt:
        assert receipt["completed_receipt_version"] == 1
        assert receipt["pre_state_version"] == expected_version - 1
        assert receipt["post_state_version"] == expected_version
        assert receipt["response_body_canonical_bytes"]
        assert receipt["session_binding_digest"]
    else:
        assert receipt["completed_receipt_version"] is None
        assert receipt["pre_state_version"] is None
        assert receipt["post_state_version"] is None
        assert receipt["response_body_canonical_bytes"] is None
        assert receipt["session_binding_digest"] is None
    if status_before is not None:
        assert audit["status_before"] == status_before
    if status_after is not None:
        assert audit["status_after"] == status_after
        assert target["status"] == status_after
    return target, audit, receipt


def _race_assert_created_appointment(target, public_appointment, proposal):
    command = proposal["command"]
    assert target["id"] == public_appointment["id"]
    assert target["practice_id"] == public_appointment["practice_id"]
    assert target["patient_name_provisional"] == command[
        "patient_name_provisional"
    ] == public_appointment["patient_name_provisional"]
    assert target["practitioner_id"] == command["practitioner_id"] == (
        public_appointment["practitioner_id"]
    )
    assert target["location_id"] == command["location_id"] == (
        public_appointment["location_id"]
    )
    assert target["duration_minutes"] == command["duration_minutes"] == (
        public_appointment["duration_minutes"]
    )
    assert target["status"] == public_appointment["status"] == "Booked"
    assert target["appointment_date"] == public_appointment["appointment_date"]
    assert target["start_time_local"] == public_appointment["start_time_local"]
    target_start = _confirmation_utc(_confirmation_datetime(target["start_time"]))
    command_start = _confirmation_utc(_confirmation_datetime(command["start_time"]))
    public_start = _confirmation_utc(
        _confirmation_datetime(public_appointment["start_time"])
    )
    assert target_start == command_start == public_start


def _race_assert_raw_status_graph(snapshot, spec):
    assert spec["kind"] == "raw-status"
    target = _snapshot_row(snapshot, "appointments", spec["target_id"])
    audits = [
        row
        for row in _snapshot_rows(snapshot, "appointment_audit_log")
        if row["appointment_id"] == str(spec["target_id"])
        and row["action"] == "status_change"
        and row["status_before"] == spec["status_before"]
        and row["status_after"] == spec["status_after"]
        and row["command_id"] is None
    ]
    assert len(audits) == 1
    assert target["status"] == spec["status_after"]
    assert target["appointment_state_version"] == spec["expected_version"]
    return target, audits[0]


def _race_assert_only_receipts(snapshot, specs):
    receipts = _snapshot_rows(snapshot, "appointment_command_idempotency")
    expected = {(spec["operation"], spec["key_hash"]) for spec in specs}
    observed = {(row["operation_id"], row["idempotency_key_hash"]) for row in receipts}
    assert observed == expected
    assert len(receipts) == len(expected)


@pytest.mark.parametrize(
    "site_pair,reverse",
    [
        pytest.param(("l1", "l2"), False, id="APT-R1-command-sites-forward"),
        pytest.param(("l1", "l2"), True, id="APT-R1-command-sites-reverse"),
        pytest.param(("none", "l1"), False, id="APT-R1-command-null-forward"),
        pytest.param(("none", "l1"), True, id="APT-R1-command-null-reverse"),
    ],
)
def test_r1_signed_creates_have_one_command_winner(
    appointment_http_client,
    case_world,
    site_pair,
    reverse,
):
    client, headers = appointment_http_client
    locations = [_raw_site(case_world, name) for name in site_pair]
    if reverse:
        locations.reverse()
    first_key = "apt-r1-command-first"
    second_key = "apt-r1-command-second"
    first_proposal, first_confirmation = _race_create_proposal(
        client,
        headers,
        case_world,
        proposal_key="apt-r1-first-proposal",
        patient_label="Synthetic R1 First Command",
        practitioner_id=case_world.r,
        location_id=locations[0],
        start=case_world.start,
    )
    second_proposal, second_confirmation = _race_create_proposal(
        client,
        headers,
        case_world,
        proposal_key="apt-r1-second-proposal",
        patient_label="Synthetic R1 Second Command",
        practitioner_id=case_world.r,
        location_id=locations[1],
        start=case_world.start + timedelta(minutes=15),
    )
    before = case_world.snapshot()
    first_spec = _race_command_spec(
        case_world, "first", RACE_CREATE_OPERATION, first_key
    )
    second_spec = _race_command_spec(
        case_world, "second", RACE_CREATE_OPERATION, second_key
    )

    first_response, second_response, gate, observation = _run_command_race(
        case_world,
        _race_create_call(
            client, headers, first_proposal, first_confirmation, first_key
        ),
        _race_create_call(
            client, headers, second_proposal, second_confirmation, second_key
        ),
        (first_spec, second_spec),
        second_boundary="database-wait",
    )

    assert observation is not None
    _assert_race_gate_outcomes(gate, first="commit", second="blocked")
    assert first_response.status_code == 200
    first_body = first_response.json()
    _assert_confirmed_create_confirmation(first_body, case_world.start)
    _race_assert_conflict(second_response, "create")
    after = case_world.snapshot()
    assert len(_snapshot_rows(after, "appointments")) == 1
    assert len(_snapshot_rows(after, "appointment_audit_log")) == 1
    winner_id = UUID(first_body["appointment"]["id"])
    winner, _, _ = _race_assert_graph(
        after,
        first_spec,
        target_id=winner_id,
        action="create",
        expected_version=1,
        actual_body=first_body,
    )
    _race_assert_created_appointment(
        winner, first_body["appointment"], first_proposal
    )
    _race_assert_only_receipts(after, (first_spec,))
    assert after != before


@pytest.mark.parametrize(
    "operation",
    [
        pytest.param("move", id="APT-R2-command-create-v-move"),
        pytest.param("resize", id="APT-R2-command-create-v-resize"),
        pytest.param("reactivate", id="APT-R2-command-create-v-reactivate"),
        pytest.param("both-reactivate", id="APT-R2-command-two-reactivations"),
    ],
)
def test_r2_public_occupancy_commands_preserve_the_loser(
    appointment_http_client,
    case_world,
    operation,
):
    client, headers = appointment_http_client
    first_key = "apt-r2-command-first"
    second_key = "apt-r2-command-second"

    if operation == "move":
        loser = case_world.row(
            "r2-command-move-target",
            location_id=None,
            start=case_world.start + timedelta(minutes=60),
        )
        _insert_and_commit(case_world, loser)
        _, second_confirmation = _actual_update_confirmation(
            client,
            headers,
            loser["id"],
            {"start_time": case_world.start.isoformat()},
            proposal_key="apt-r2-move-proposal",
        )
        second_call = lambda: _confirm_update(
            client, headers, second_key, second_confirmation
        )
        second_operation = RACE_UPDATE_OPERATION
        second_family = "update"
    elif operation == "resize":
        loser = case_world.row(
            "r2-command-resize-target",
            location_id=None,
            start=case_world.start - timedelta(minutes=30),
            minutes=30,
        )
        _insert_and_commit(case_world, loser)
        _, second_confirmation = _actual_update_confirmation(
            client,
            headers,
            loser["id"],
            {"duration_minutes": 60},
            proposal_key="apt-r2-resize-proposal",
        )
        second_call = lambda: _confirm_update(
            client, headers, second_key, second_confirmation
        )
        second_operation = RACE_UPDATE_OPERATION
        second_family = "update"
    elif operation == "reactivate":
        loser = case_world.row(
            "r2-command-reactivation-target",
            location_id=None,
            status="Cancelled",
        )
        _insert_and_commit(case_world, loser)
        second_call = lambda: client.patch(
            f"{RAW_APPOINTMENTS_ENDPOINT}/{loser['id']}/status",
            headers=headers,
            json={"status": "Booked"},
        )
        second_operation = RACE_RAW_STATUS_FAMILY
        second_family = "raw-status"
    else:
        assert operation == "both-reactivate"
        first_target = case_world.row(
            "r2-command-first-reactivation",
            location_id=case_world.l1,
            status="Cancelled",
        )
        loser = case_world.row(
            "r2-command-second-reactivation",
            location_id=None,
            status="NoShow",
        )
        _insert_and_commit(case_world, first_target)
        _insert_and_commit(case_world, loser)
        first_call = lambda: client.patch(
            f"{RAW_APPOINTMENTS_ENDPOINT}/{first_target['id']}/status",
            headers=headers,
            json={"status": "Booked"},
        )
        second_call = lambda: client.patch(
            f"{RAW_APPOINTMENTS_ENDPOINT}/{loser['id']}/status",
            headers=headers,
            json={"status": "Booked"},
        )
        first_operation = RACE_RAW_STATUS_FAMILY
        second_operation = RACE_RAW_STATUS_FAMILY
        second_family = "raw-status"

    if operation != "both-reactivate":
        first_proposal, first_confirmation = _race_create_proposal(
            client,
            headers,
            case_world,
            proposal_key="apt-r2-create-proposal",
            patient_label="Synthetic R2 Create Command",
            practitioner_id=case_world.r,
            location_id=case_world.l1,
            start=case_world.start,
        )
        first_call = _race_create_call(
            client, headers, first_proposal, first_confirmation, first_key
        )
        first_operation = RACE_CREATE_OPERATION

    before = case_world.snapshot()
    loser_before = _snapshot_row(before, "appointments", loser["id"])
    if first_operation == RACE_RAW_STATUS_FAMILY:
        first_target_before = _snapshot_row(
            before, "appointments", first_target["id"]
        )
        assert first_target_before["appointment_state_version"] == 1
        first_spec = _race_raw_status_spec(
            case_world,
            "first",
            first_target["id"],
            status_before="Cancelled",
            status_after="Booked",
        )
    else:
        first_spec = _race_command_spec(
            case_world, "first", first_operation, first_key
        )
    if second_operation == RACE_RAW_STATUS_FAMILY:
        assert loser_before["appointment_state_version"] == 1
        second_spec = _race_raw_status_spec(
            case_world,
            "second",
            loser["id"],
            status_before=loser_before["status"],
            status_after="Booked",
        )
    else:
        second_spec = _race_command_spec(
            case_world, "second", second_operation, second_key
        )
    first_response, second_response, gate, observation = _run_command_race(
        case_world,
        first_call,
        second_call,
        (first_spec, second_spec),
        second_boundary="database-wait",
    )

    assert observation is not None
    _assert_race_gate_outcomes(gate, first="commit", second="blocked")
    after = case_world.snapshot()
    loser_after = _snapshot_row(after, "appointments", loser["id"])
    assert loser_after == loser_before
    if second_operation == RACE_RAW_STATUS_FAMILY:
        assert loser_after["appointment_state_version"] == 1
    assert len(_snapshot_rows(after, "appointment_audit_log")) == 1
    if first_operation == RACE_RAW_STATUS_FAMILY:
        assert first_response.status_code == 200
        first_body = first_response.json()
        assert first_body["id"] == str(first_target["id"])
        assert first_body["status"] == "Booked"
        raw_target_after, _ = _race_assert_raw_status_graph(after, first_spec)
        expected_raw_target = {
            **first_target_before,
            "status": "Booked",
            "appointment_state_version": (
                first_target_before["appointment_state_version"] + 1
            ),
        }
        assert raw_target_after == expected_raw_target
        _race_assert_only_receipts(after, ())
        winner = first_body
    else:
        assert first_response.status_code == 200
        first_body = first_response.json()
        _assert_confirmed_create_confirmation(first_body, case_world.start)
        created_target, _, _ = _race_assert_graph(
            after,
            first_spec,
            target_id=UUID(first_body["appointment"]["id"]),
            action="create",
            expected_version=1,
            actual_body=first_body,
        )
        _race_assert_created_appointment(
            created_target, first_body["appointment"], first_proposal
        )
        _race_assert_only_receipts(after, (first_spec,))
        winner = first_body["appointment"]
    if second_family == "raw-status":
        _assert_raw_collision(second_response, winner)
    else:
        _race_assert_conflict(second_response, second_family)
    assert len(_snapshot_rows(after, "appointments")) == 2


@pytest.mark.parametrize(
    "_case",
    [pytest.param(None, id="APT-R3-command-aborted-create-releases-create")],
)
def test_r3_aborted_signed_create_releases_pending_signed_create(
    appointment_http_client,
    case_world,
    _case,
):
    client, headers = appointment_http_client
    first_key = "apt-r3-aborted-create-confirm"
    second_key = "apt-r3-pending-create-confirm"
    first_proposal, first_confirmation = _race_create_proposal(
        client,
        headers,
        case_world,
        proposal_key="apt-r3-first-create-proposal",
        patient_label="Synthetic R3 Aborted Create",
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
    )
    second_proposal, second_confirmation = _race_create_proposal(
        client,
        headers,
        case_world,
        proposal_key="apt-r3-create-proposal",
        patient_label="Synthetic R3 Pending Create",
        practitioner_id=case_world.r,
        location_id=None,
        start=case_world.start + timedelta(minutes=15),
    )
    before = case_world.snapshot()
    first_spec = _race_command_spec(
        case_world,
        "first",
        RACE_CREATE_OPERATION,
        first_key,
        abort=True,
    )
    second_spec = _race_command_spec(
        case_world, "second", RACE_CREATE_OPERATION, second_key
    )

    first_error, second_response, gate, observation = _run_command_race(
        case_world,
        _race_create_call(
            client, headers, first_proposal, first_confirmation, first_key
        ),
        _race_create_call(
            client, headers, second_proposal, second_confirmation, second_key
        ),
        (first_spec, second_spec),
        second_boundary="database-wait",
        expected_first_error=CommandRaceCommitAbort,
    )

    assert observation is not None
    _assert_race_gate_outcomes(gate, first="propagated-abort", second="commit")
    assert str(first_error) == "authored create-command abort after complete staging"
    assert second_response.status_code == 200
    second_body = second_response.json()
    _assert_confirmed_create_confirmation(
        second_body, case_world.start + timedelta(minutes=15)
    )
    staged_first = gate["staged"]["first"]
    assert staged_first["appointment"]["status"] == "Booked"
    assert staged_first["appointment"]["appointment_state_version"] == 1
    assert staged_first["audit"]["action"] == "create"
    staged_first_receipt = staged_first["receipt"]
    assert staged_first_receipt["state"] == "completed"
    assert staged_first_receipt["response_status_code"] == 200
    staged_first_body = staged_first_receipt["response_body_json"]
    assert staged_first_body["appointment"]["id"] == staged_first["appointment"]["id"]
    assert staged_first_receipt["completed_receipt_version"] is None
    assert staged_first_receipt["pre_state_version"] is None
    assert staged_first_receipt["post_state_version"] is None
    assert staged_first_receipt["response_body_canonical_bytes"] is None
    assert staged_first_receipt["session_binding_digest"] is None
    _race_assert_created_appointment(
        staged_first["appointment"],
        staged_first_body["appointment"],
        first_proposal,
    )
    aborted_target_id = staged_first["appointment"]["id"]
    after = case_world.snapshot()
    assert aborted_target_id not in {
        row["id"] for row in _snapshot_rows(after, "appointments")
    }
    assert len(_snapshot_rows(after, "appointments")) == 1
    assert len(_snapshot_rows(after, "appointment_audit_log")) == 1
    second_target, _, _ = _race_assert_graph(
        after,
        second_spec,
        target_id=UUID(second_body["appointment"]["id"]),
        action="create",
        expected_version=1,
        actual_body=second_body,
    )
    _race_assert_created_appointment(
        second_target, second_body["appointment"], second_proposal
    )
    _race_assert_only_receipts(after, (second_spec,))
    assert after != before


@pytest.mark.parametrize(
    "release",
    [
        pytest.param("commit", id="APT-R4-command-cancellation-commit"),
        pytest.param("rollback", id="APT-R4-command-cancellation-rollback"),
    ],
)
def test_r4_signed_cancellation_and_create_have_a_valid_serial_result(
    appointment_http_client,
    case_world,
    release,
):
    client, headers = appointment_http_client
    # Mint real signed create evidence while the interval is genuinely free.
    # The fixture then establishes the booked incumbent before the cancellation
    # proposal; no client-authored freshness or signature is fabricated.
    create_proposal, create_confirmation = _race_create_proposal(
        client,
        headers,
        case_world,
        proposal_key="apt-r4-create-proposal-before-incumbent",
        patient_label="Synthetic R4 Competing Create",
        practitioner_id=case_world.r,
        location_id=None,
        start=case_world.start,
    )
    incumbent = case_world.row(
        "r4-command-incumbent",
        location_id=case_world.l1,
        status="Booked",
    )
    _insert_and_commit(case_world, incumbent)
    first_key = "apt-r4-cancellation-confirm"
    pending_key = "apt-r4-pending-create-confirm"
    followup_key = "apt-r4-followup-create-confirm"
    _, cancellation_confirmation = _actual_status_confirmation(
        client,
        headers,
        incumbent["id"],
        {"status": "Cancelled"},
        proposal_key="apt-r4-cancellation-proposal",
    )
    before = case_world.snapshot()
    incumbent_before = _snapshot_row(before, "appointments", incumbent["id"])
    first_spec = _race_command_spec(
        case_world,
        "first",
        RACE_STATUS_OPERATION,
        first_key,
        abort=release == "rollback",
    )
    pending_spec = _race_command_spec(
        case_world, "second", RACE_CREATE_OPERATION, pending_key
    )

    first_response, pending_response, gate, observation = _run_command_race(
        case_world,
        lambda: _confirm_status(
            client, headers, first_key, cancellation_confirmation
        ),
        _race_create_call(
            client,
            headers,
            create_proposal,
            create_confirmation,
            pending_key,
        ),
        (first_spec, pending_spec),
        second_boundary="early-public-result",
    )

    assert observation is None
    _assert_race_gate_outcomes(
        gate,
        first="commit" if release == "commit" else "abort",
        second="early-blocked",
    )
    _race_assert_conflict(
        pending_response,
        "create",
        create_revalidation=True,
    )
    assert gate["staged"]["first"]["appointment"]["status"] == "Cancelled"
    if release == "commit":
        assert first_response.status_code == 200
        first_body = first_response.json()
        _assert_confirmed_status(first_body)
    else:
        _race_assert_status_abort(first_response)

    # A distinct command after the cancellation resolves demonstrates released
    # versus retained occupancy.  It is explicit test traffic, never a retry.
    followup_response = _confirm_create(
        client,
        headers,
        create_proposal["confirm_endpoint"],
        followup_key,
        create_confirmation,
    )
    if release == "commit":
        assert followup_response.status_code == 200
        followup_body = followup_response.json()
        _assert_confirmed_create_confirmation(followup_body, case_world.start)
        after = case_world.snapshot()
        assert len(_snapshot_rows(after, "appointments")) == 2
        assert len(_snapshot_rows(after, "appointment_audit_log")) == 2
        followup_spec = _race_command_spec(
            case_world, "followup", RACE_CREATE_OPERATION, followup_key
        )
        cancelled_target, _, _ = _race_assert_graph(
            after,
            first_spec,
            target_id=incumbent["id"],
            action="status_change",
            expected_version=2,
            actual_body=first_body,
            status_before="Booked",
            status_after="Cancelled",
            private_status_receipt=True,
        )
        assert cancelled_target == {
            **incumbent_before,
            "status": "Cancelled",
            "appointment_state_version": (
                incumbent_before["appointment_state_version"] + 1
            ),
        }
        followup_target, _, _ = _race_assert_graph(
            after,
            followup_spec,
            target_id=UUID(followup_body["appointment"]["id"]),
            action="create",
            expected_version=1,
            actual_body=followup_body,
        )
        _race_assert_created_appointment(
            followup_target, followup_body["appointment"], create_proposal
        )
        _race_assert_only_receipts(after, (first_spec, followup_spec))
    else:
        _race_assert_conflict(
            followup_response,
            "create",
            create_revalidation=True,
        )
        assert case_world.snapshot() == before


@pytest.mark.parametrize(
    "kind",
    [
        pytest.param("adjacent", id="APT-R5-command-adjacent"),
        pytest.param("different-practitioner", id="APT-R5-command-different-practitioner"),
    ],
)
def test_r5_nonconflicting_signed_commands_commit_while_both_are_staged(
    appointment_http_client,
    case_world,
    kind,
):
    client, headers = appointment_http_client
    second_start = (
        case_world.start + timedelta(minutes=30)
        if kind == "adjacent"
        else case_world.start
    )
    second_practitioner = case_world.r if kind == "adjacent" else case_world.r2
    first_key = "apt-r5-first-create-confirm"
    second_key = "apt-r5-second-create-confirm"
    first_proposal, first_confirmation = _race_create_proposal(
        client,
        headers,
        case_world,
        proposal_key="apt-r5-first-create-proposal",
        patient_label="Synthetic R5 First Command",
        practitioner_id=case_world.r,
        location_id=case_world.l1,
        start=case_world.start,
    )
    second_proposal, second_confirmation = _race_create_proposal(
        client,
        headers,
        case_world,
        proposal_key="apt-r5-second-create-proposal",
        patient_label="Synthetic R5 Second Command",
        practitioner_id=second_practitioner,
        location_id=None,
        start=second_start,
    )
    before = case_world.snapshot()
    first_spec = _race_command_spec(
        case_world, "first", RACE_CREATE_OPERATION, first_key
    )
    second_spec = _race_command_spec(
        case_world, "second", RACE_CREATE_OPERATION, second_key
    )
    first_response, second_response, gate, observation = _run_command_race(
        case_world,
        _race_create_call(
            client, headers, first_proposal, first_confirmation, first_key
        ),
        _race_create_call(
            client, headers, second_proposal, second_confirmation, second_key
        ),
        (first_spec, second_spec),
        second_boundary="completed-command",
    )

    assert observation is None
    _assert_race_gate_outcomes(gate, first="commit", second="commit")
    assert first_response.status_code == second_response.status_code == 200
    first_body = first_response.json()
    second_body = second_response.json()
    _assert_confirmed_create_confirmation(first_body, case_world.start)
    _assert_confirmed_create_confirmation(second_body, second_start)
    assert first_body["appointment"]["id"] != second_body["appointment"]["id"]
    after = case_world.snapshot()
    assert len(_snapshot_rows(after, "appointments")) == 2
    assert len(_snapshot_rows(after, "appointment_audit_log")) == 2
    first_target, _, _ = _race_assert_graph(
        after,
        first_spec,
        target_id=UUID(first_body["appointment"]["id"]),
        action="create",
        expected_version=1,
        actual_body=first_body,
    )
    second_target, _, _ = _race_assert_graph(
        after,
        second_spec,
        target_id=UUID(second_body["appointment"]["id"]),
        action="create",
        expected_version=1,
        actual_body=second_body,
    )
    _race_assert_created_appointment(
        first_target, first_body["appointment"], first_proposal
    )
    _race_assert_created_appointment(
        second_target, second_body["appointment"], second_proposal
    )
    _race_assert_only_receipts(after, (first_spec, second_spec))
    assert after != before
