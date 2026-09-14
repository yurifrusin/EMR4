"""Synthetic PostgreSQL preservation regressions, independent of the app/conftest.

Run this file directly, or collect it with unittest. Required environment:
  EMR4_PHASE0_TEST_URL=postgresql+psycopg://.../emr4_phase0_control
  EMR4_PHASE0_TEST_DISPOSABLE=yes

The endpoint must be an explicitly provisioned disposable cluster with pgvector
available and a CREATEDB role. Each test creates and removes its own random
database; the supplied control database is never cleared. All fixture records
are synthetic. No application/provider imports or subprocesses are used.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import unittest
import uuid

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.util import CommandError
import sqlalchemy as sa


ROOT_REVISION = "d4787e8e3629"
REVISION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic" / "versions" / "d4787e8e3629_phase_0_baseline.py"
)
CORE_TABLES = {
    "patients", "encounters", "mbs_claims", "clinical_diagnoses", "prescriptions",
}
DIRECTORY_TABLES = {"mbs_directory", "snomed_directory"}
SENTINEL_ID = "00000000-0000-0000-0000-000000000101"

# Independent SQL definitions: do not call the candidate's bootstrap helpers.
LEGACY_DDL = (
    "CREATE EXTENSION vector",
    """CREATE TABLE public.patients (
        id uuid PRIMARY KEY, first_name varchar(100) NOT NULL,
        last_name varchar(100) NOT NULL, date_of_birth date NOT NULL,
        medicare_number varchar(20), ihi_number varchar(20))""",
    """CREATE TABLE public.encounters (
        id uuid PRIMARY KEY, patient_id uuid REFERENCES public.patients(id),
        google_doc_id varchar(255) NOT NULL,
        consultation_date timestamptz DEFAULT CURRENT_TIMESTAMP,
        is_finalized boolean, consultation_type varchar(255),
        raw_document_text text, document_embedding vector(768))""",
    """CREATE TABLE public.mbs_claims (
        id uuid PRIMARY KEY, encounter_id uuid REFERENCES public.encounters(id),
        item_number varchar(10) NOT NULL, description text, status varchar(20))""",
    """CREATE TABLE public.clinical_diagnoses (
        id uuid PRIMARY KEY, patient_id uuid REFERENCES public.patients(id),
        encounter_id uuid REFERENCES public.encounters(id),
        term varchar(255) NOT NULL, snomed_ct_au_code varchar(50))""",
    """CREATE TABLE public.prescriptions (
        id uuid PRIMARY KEY, patient_id uuid REFERENCES public.patients(id),
        encounter_id uuid REFERENCES public.encounters(id),
        drug_name varchar(255) NOT NULL, dosage_text text, is_active boolean)""",
)
DIRECTORY_DDL = (
    """CREATE TABLE public.mbs_directory (
        item_number varchar(10) PRIMARY KEY, description text NOT NULL,
        fee varchar(20))""",
    """CREATE TABLE public.snomed_directory (
        concept_id varchar(50) PRIMARY KEY, term varchar(255) NOT NULL)""",
    """INSERT INTO public.mbs_directory VALUES
        ('TEST001', 'Synthetic MBS preservation sentinel', '12.34')""",
    """INSERT INTO public.snomed_directory VALUES
        ('TEST-SNOMED', 'Synthetic terminology preservation sentinel')""",
)
CORE_INSERTS = {
    "patients": """INSERT INTO public.patients
        (id, first_name, last_name, date_of_birth, medicare_number)
        VALUES (:id, 'Synthetic', 'Sentinel', '2000-01-01', 'TEST-ONLY')""",
    "encounters": """INSERT INTO public.encounters
        (id, google_doc_id, raw_document_text)
        VALUES (:id, 'synthetic-doc', 'Synthetic encounter sentinel')""",
    "mbs_claims": """INSERT INTO public.mbs_claims
        (id, item_number, description, status)
        VALUES (:id, 'TEST001', 'Synthetic claim sentinel', 'legacy-sentinel')""",
    "clinical_diagnoses": """INSERT INTO public.clinical_diagnoses
        (id, term, snomed_ct_au_code)
        VALUES (:id, 'Synthetic diagnosis sentinel', 'TEST-SNOMED')""",
    "prescriptions": """INSERT INTO public.prescriptions
        (id, drug_name, dosage_text)
        VALUES (:id, 'Synthetic non-drug sentinel', 'TEST ONLY')""",
}


def _snapshot(connection):
    """Capture schema, enums/extensions and every synthetic row, including version."""
    queries = {
        "relations": """SELECT n.nspname, c.relname, c.relkind, c.relpersistence,
            c.relrowsecurity, c.relforcerowsecurity
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2""",
        "columns": """SELECT n.nspname, c.relname, a.attnum, a.attname,
            format_type(a.atttypid, a.atttypmod), a.attnotnull,
            pg_get_expr(d.adbin, d.adrelid), a.attidentity, a.attgenerated
            FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
            WHERE n.nspname IN ('public', 'phase0_shared')
              AND a.attnum > 0 AND NOT a.attisdropped ORDER BY 1, 2, 3""",
        "constraints": """SELECT n.nspname, c.relname, k.conname,
            pg_get_constraintdef(k.oid)
            FROM pg_constraint k JOIN pg_class c ON c.oid = k.conrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2, 3""",
        "types": """SELECT n.nspname, t.typname, t.typtype, t.oid
            FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2""",
        "enums": """SELECT n.nspname, t.typname, e.enumsortorder, e.enumlabel
            FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid
            JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2, 3""",
        "extensions": "SELECT extname, extversion, extnamespace FROM pg_extension ORDER BY 1",
    }
    result = {
        name: [tuple(row) for row in connection.execute(sa.text(sql))]
        for name, sql in queries.items()
    }
    tables = connection.execute(sa.text("""
        SELECT n.nspname, c.relname FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname IN ('public', 'phase0_shared') AND c.relkind = 'r'
        ORDER BY 1, 2
    """)).all()
    result["rows"] = {}
    quote = connection.dialect.identifier_preparer.quote_identifier
    for schema, table in tables:
        qualified = f"{quote(schema)}.{quote(table)}"
        result["rows"][(schema, table)] = list(connection.execute(sa.text(
            f"SELECT to_jsonb(t)::text FROM {qualified} t ORDER BY to_jsonb(t)::text"
        )).scalars())
    return result


class Phase0MigrationPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url_text = os.environ.get("EMR4_PHASE0_TEST_URL")
        if not url_text or os.environ.get("EMR4_PHASE0_TEST_DISPOSABLE") != "yes":
            raise unittest.SkipTest("Explicit disposable PostgreSQL endpoint not supplied")
        cls.control_url = sa.engine.make_url(url_text)
        if (cls.control_url.get_backend_name() != "postgresql"
                or not (cls.control_url.database or "").startswith("emr4_phase0_")):
            raise RuntimeError("Refusing endpoint without emr4_phase0_ disposable database name")
        cls.control = sa.create_engine(cls.control_url, poolclass=sa.pool.NullPool)
        with cls.control.connect() as connection:
            actual = connection.execute(sa.text("SELECT current_database()")).scalar_one()
            if actual != cls.control_url.database:
                raise RuntimeError("Disposable endpoint database identity mismatch")
        cls.script_tmp = tempfile.TemporaryDirectory(prefix="phase0-alembic-")
        cls.script_dir = Path(cls.script_tmp.name)
        (cls.script_dir / "versions").mkdir()
        shutil.copyfile(REVISION_PATH, cls.script_dir / "versions" / REVISION_PATH.name)
        (cls.script_dir / "env.py").write_text(
            "from alembic import context\n"
            "connection = context.config.attributes['connection']\n"
            "context.configure(connection=connection, transactional_ddl=True)\n"
            "with context.begin_transaction():\n"
            "    context.run_migrations()\n",
            encoding="utf-8",
        )
        spec = importlib.util.spec_from_file_location("phase0_candidate", REVISION_PATH)
        cls.revision = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.revision)

    @classmethod
    def tearDownClass(cls):
        cls.control.dispose()
        cls.script_tmp.cleanup()

    def setUp(self):
        self.database = f"emr4_phase0_{uuid.uuid4().hex}"
        with self.control.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            connection.exec_driver_sql(f'CREATE DATABASE "{self.database}" TEMPLATE template0')
        self.engine = sa.create_engine(
            self.control_url.set(database=self.database), poolclass=sa.pool.NullPool,
            connect_args={"options": "-c statement_timeout=20000 -c lock_timeout=6000"},
        )

    def tearDown(self):
        self.engine.dispose()
        with self.control.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            connection.exec_driver_sql("SET statement_timeout = '20s'")
            connection.exec_driver_sql(f'DROP DATABASE "{self.database}"')

    def _command(self, connection, direction="upgrade"):
        config = Config()
        config.set_main_option("script_location", str(self.script_dir))
        config.attributes["connection"] = connection
        if direction == "upgrade":
            command.upgrade(config, ROOT_REVISION)
        else:
            command.downgrade(config, "base")

    def _run(self, direction="upgrade", isolation="READ COMMITTED"):
        with self.engine.connect().execution_options(isolation_level=isolation) as connection:
            with connection.begin():
                self._command(connection, direction)

    def _state(self):
        with self.engine.connect() as connection:
            return _snapshot(connection)

    def _legacy(self, directories=True):
        with self.engine.begin() as connection:
            for sql in LEGACY_DDL:
                connection.exec_driver_sql(sql)
            if directories:
                for sql in DIRECTORY_DDL:
                    connection.exec_driver_sql(sql)

    def _assert_refused_unchanged(self, direction="upgrade", match="Phase-0", isolation="READ COMMITTED"):
        before = self._state()
        with self.assertRaisesRegex((RuntimeError, sa.exc.DBAPIError), match):
            self._run(direction, isolation)
        self.assertEqual(before, self._state())

    def _version(self):
        with self.engine.connect() as connection:
            return list(connection.execute(sa.text("SELECT version_num FROM alembic_version")).scalars())

    def test_fresh_cycle_repeats_and_preserves_unrelated_enum_and_domain(self):
        with self.engine.begin() as connection:
            connection.exec_driver_sql("CREATE TYPE public.unrelated_mood AS ENUM ('quiet', 'active')")
            connection.exec_driver_sql("CREATE DOMAIN public.unrelated_domain AS public.unrelated_mood")
            original_oid = connection.execute(sa.text("SELECT 'public.unrelated_mood'::regtype::oid")).scalar_one()
        for _ in range(2):
            self._run()
            self.assertEqual(self._version(), [ROOT_REVISION])
            self._run("downgrade")
            self.assertEqual(self._version(), [])
            with self.engine.connect() as connection:
                self.assertEqual(sa.inspect(connection).get_table_names(schema="public"), ["alembic_version"])
                enums = sa.inspect(connection).get_enums(schema="public")
                self.assertEqual([item["name"] for item in enums], ["unrelated_mood"])
                self.assertEqual(connection.execute(sa.text(
                    "SELECT 'public.unrelated_mood'::regtype::oid"
                )).scalar_one(), original_oid)
                self.assertIsNotNone(connection.execute(sa.text(
                    "SELECT to_regtype('public.unrelated_domain')"
                )).scalar_one())

    def test_empty_legacy_core_preserves_directory_rows_both_directions(self):
        self._legacy()
        before_rows = self._state()["rows"]
        for _ in range(2):
            self._run()
            self.assertEqual(self._version(), [ROOT_REVISION])
            for name in DIRECTORY_TABLES:
                self.assertEqual(before_rows[("public", name)], self._state()["rows"][("public", name)])
            self._run("downgrade")
            self.assertEqual(self._version(), [])
            with self.engine.connect() as connection:
                self.assertEqual(
                    set(sa.inspect(connection).get_table_names(schema="public")),
                    CORE_TABLES | DIRECTORY_TABLES | {"alembic_version"},
                )
                self.assertEqual(sa.inspect(connection).get_enums(schema="public"), [])
            for name, rows in before_rows.items():
                self.assertEqual(rows, self._state()["rows"][name])

    def test_missing_legacy_directories_are_created_and_retained_on_downgrade(self):
        self._legacy(directories=False)
        self._run()
        with self.engine.begin() as connection:
            for sql in DIRECTORY_DDL[2:]:
                connection.exec_driver_sql(sql)
        directory_rows = self._state()["rows"]
        self._run("downgrade")
        for name in DIRECTORY_TABLES:
            self.assertEqual(directory_rows[("public", name)], self._state()["rows"][("public", name)])
        self._run()

    def test_each_populated_legacy_core_is_refused_without_changes(self):
        self._legacy()
        for name, sql in CORE_INSERTS.items():
            with self.subTest(table=name):
                with self.engine.begin() as connection:
                    connection.execute(sa.text(sql), {"id": SENTINEL_ID})
                self._assert_refused_unchanged(match=f"populated table {name}")
                with self.engine.begin() as connection:
                    connection.exec_driver_sql(f'DELETE FROM public."{name}"')

    def test_partial_core_schema_refuses_without_creating_other_tables(self):
        with self.engine.begin() as connection:
            connection.exec_driver_sql(LEGACY_DDL[1])
            connection.execute(sa.text(CORE_INSERTS["patients"]), {"id": SENTINEL_ID})
        self._assert_refused_unchanged(match="incomplete or unexpected legacy tables")

    def test_unknown_relation_prevents_fresh_detection(self):
        with self.engine.begin() as connection:
            connection.exec_driver_sql("CREATE VIEW public.unrelated_view AS SELECT 'synthetic'::text AS value")
        self._assert_refused_unchanged(match="unexpected public relation")

    def test_unknown_table_and_rows_are_preserved_on_refusal(self):
        with self.engine.begin() as connection:
            connection.exec_driver_sql("CREATE TABLE public.unrelated_records (value text)")
            connection.exec_driver_sql("INSERT INTO public.unrelated_records VALUES ('synthetic sentinel')")
        self._assert_refused_unchanged(match="incomplete or unexpected legacy tables")

    def test_unrecognised_legacy_column_shape_is_refused(self):
        self._legacy()
        with self.engine.begin() as connection:
            connection.exec_driver_sql("ALTER TABLE public.mbs_claims ADD COLUMN legacy_extra text")
        self._assert_refused_unchanged(match="unexpected legacy columns")

    def test_rls_legacy_shape_is_refused_even_for_bypassrls_role(self):
        self._legacy()
        with self.engine.begin() as connection:
            connection.execute(sa.text(CORE_INSERTS["patients"]), {"id": SENTINEL_ID})
            connection.exec_driver_sql("ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY")
            connection.exec_driver_sql("ALTER TABLE public.patients FORCE ROW LEVEL SECURITY")
        self._assert_refused_unchanged(match="unexpected public relation")

    def test_preexisting_revision_enum_name_is_preserved_and_refused(self):
        with self.engine.begin() as connection:
            connection.exec_driver_sql("CREATE TYPE public.gptier AS ENUM ('external-original')")
        self._assert_refused_unchanged(match="pre-existing revision type name")

    def test_historical_unproven_marker_is_not_downgrade_authority(self):
        self._run()
        with self.engine.begin() as connection:
            connection.exec_driver_sql('DROP TYPE public.emr4_phase0_empty_bootstrap_marker')
            connection.exec_driver_sql("CREATE TYPE public.emr4_phase0_empty_bootstrap_marker AS ENUM ('empty')")
        self._assert_refused_unchanged("downgrade", "without recognised revision ownership")

    def test_same_name_replacement_of_owned_enum_is_preserved_and_refused(self):
        self._run()
        with self.engine.begin() as connection:
            connection.exec_driver_sql("ALTER TYPE public.gptier RENAME TO moved_original_gptier")
            connection.exec_driver_sql("CREATE TYPE public.gptier AS ENUM ('unrelated-replacement')")
        self._assert_refused_unchanged("downgrade", "without recognised revision ownership")

    def test_unsupported_version_is_preserved_and_refused(self):
        with self.engine.begin() as connection:
            connection.exec_driver_sql("CREATE TABLE public.alembic_version (version_num varchar(32) PRIMARY KEY)")
            connection.exec_driver_sql("INSERT INTO public.alembic_version VALUES ('unknown_legacy_revision')")
        before = self._state()
        with self.assertRaises(CommandError):
            self._run()
        self.assertEqual(before, self._state())

    def test_populated_fresh_bootstrap_directories_prevent_downgrade(self):
        self._run()
        for name, insert in zip(("mbs_directory", "snomed_directory"), DIRECTORY_DDL[2:]):
            with self.subTest(table=name):
                with self.engine.begin() as connection:
                    connection.exec_driver_sql(insert)
                self._assert_refused_unchanged("downgrade", f"populated table {name}")
                with self.engine.begin() as connection:
                    connection.exec_driver_sql(f'DELETE FROM public."{name}"')

    def test_post_upgrade_practice_records_prevent_downgrade(self):
        self._run()
        with self.engine.begin() as connection:
            connection.execute(sa.text(
                "INSERT INTO practices (id, name) VALUES (:id, 'Synthetic practice sentinel')"
            ), {"id": SENTINEL_ID})
        self._assert_refused_unchanged("downgrade", "populated table practices")

    def test_post_upgrade_patient_records_prevent_column_loss(self):
        self._run()
        with self.engine.begin() as connection:
            connection.execute(sa.text(
                "INSERT INTO practices (id, name) VALUES (:id, 'Synthetic practice sentinel')"
            ), {"id": SENTINEL_ID})
            connection.execute(sa.text("""INSERT INTO patients
                (id, practice_id, first_name, last_name, date_of_birth, email)
                VALUES (:id, :id, 'Synthetic', 'Sentinel', '2000-01-01', 'synthetic@example.invalid')"""),
                {"id": SENTINEL_ID})
        self._assert_refused_unchanged("downgrade", "populated table patients")

    def test_shared_owned_enum_dependency_rolls_back_late_downgrade_failure(self):
        self._run()
        with self.engine.begin() as connection:
            connection.exec_driver_sql("CREATE SCHEMA phase0_shared")
            connection.exec_driver_sql("CREATE TABLE phase0_shared.external_records (tier public.gptier)")
            connection.exec_driver_sql("INSERT INTO phase0_shared.external_records VALUES ('Tier2')")
        self._assert_refused_unchanged("downgrade", "depend")
        self.assertEqual(self._version(), [ROOT_REVISION])

    def test_caught_late_refusal_restores_savepoint_and_keeps_outer_transaction_usable(self):
        self._run()
        with self.engine.begin() as connection:
            connection.exec_driver_sql("CREATE SCHEMA phase0_shared")
            connection.exec_driver_sql("CREATE TABLE phase0_shared.external_records (tier public.gptier)")
            connection.exec_driver_sql("INSERT INTO phase0_shared.external_records VALUES ('Tier2')")
        before = self._state()
        with self.engine.begin() as connection:
            context = MigrationContext.configure(connection)
            with Operations.context(context):
                with self.assertRaises(sa.exc.DBAPIError):
                    self.revision.downgrade()
            self.assertEqual(before, _snapshot(connection))
            self.assertEqual(connection.execute(sa.text("SELECT 1")).scalar_one(), 1)
        self.assertEqual(before, self._state())

    def test_write_blocking_locks_remain_held_until_outer_commit(self):
        self._legacy()
        with self.engine.begin() as connection:
            self._command(connection)
            held = set(connection.execute(sa.text("""
                SELECT c.relname FROM pg_locks l JOIN pg_class c ON c.oid = l.relation
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE l.pid = pg_backend_pid() AND l.granted
                  AND l.mode = 'AccessExclusiveLock' AND n.nspname = 'public'
            """)).scalars())
            self.assertTrue((CORE_TABLES | DIRECTORY_TABLES) <= held)
            self.assertTrue(connection.execute(sa.text("""
                SELECT EXISTS (SELECT 1 FROM pg_locks
                WHERE pid = pg_backend_pid() AND granted
                  AND relation = 'pg_catalog.pg_type'::regclass
                  AND mode = 'ShareRowExclusiveLock')
            """)).scalar_one())

    def test_repeatable_read_and_serializable_are_refused_in_both_directions(self):
        for isolation in ("REPEATABLE READ", "SERIALIZABLE"):
            with self.subTest(direction="upgrade", isolation=isolation):
                self._assert_refused_unchanged(isolation=isolation, match="READ COMMITTED")
        self._run()
        for isolation in ("REPEATABLE READ", "SERIALIZABLE"):
            with self.subTest(direction="downgrade", isolation=isolation):
                self._assert_refused_unchanged("downgrade", "READ COMMITTED", isolation)

    def test_direct_operations_autocommit_is_refused_before_any_ddl(self):
        before = self._state()
        with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            context = MigrationContext.configure(connection)
            with Operations.context(context):
                with self.assertRaisesRegex(RuntimeError, "non-autocommit transaction"):
                    self.revision.upgrade()
        self.assertEqual(before, self._state())

    def test_writer_commit_before_lock_is_seen_and_preserved(self):
        self._legacy()
        result = {}
        started = threading.Event()
        writer = self.engine.connect()
        writer_tx = writer.begin()
        writer.execute(sa.text(CORE_INSERTS["patients"]), {"id": SENTINEL_ID})

        def migrate():
            try:
                with self.engine.begin() as connection:
                    result["pid"] = connection.execute(sa.text("SELECT pg_backend_pid()")).scalar_one()
                    started.set()
                    self._command(connection)
                result["completed"] = True
            except Exception as exc:
                result["error"] = exc

        worker = threading.Thread(target=migrate, daemon=True)
        worker.start()
        try:
            self.assertTrue(started.wait(3), "Migration thread did not begin")
            deadline = time.monotonic() + 3
            waiting = False
            with self.engine.connect() as observer:
                while time.monotonic() < deadline:
                    waiting = bool(observer.execute(sa.text(
                        "SELECT cardinality(pg_blocking_pids(:pid)) > 0"
                    ), {"pid": result["pid"]}).scalar_one())
                    if waiting:
                        break
                    time.sleep(0.02)
            self.assertTrue(waiting, "Migration did not wait on the synthetic writer lock")
            writer_tx.commit()
            worker.join(10)
            self.assertFalse(worker.is_alive(), "Migration did not finish after writer commit")
            self.assertIsInstance(result.get("error"), RuntimeError)
            self.assertIn("populated table patients", str(result["error"]))
            with self.engine.connect() as connection:
                self.assertEqual(connection.execute(sa.text("SELECT count(*) FROM patients")).scalar_one(), 1)
                self.assertIsNone(connection.execute(sa.text("SELECT to_regclass('public.practices')")).scalar_one())
                self.assertIsNone(connection.execute(sa.text("SELECT to_regclass('public.alembic_version')")).scalar_one())
        finally:
            if writer_tx.is_active:
                writer_tx.rollback()
            writer.close()
            worker.join(22)

    def test_lock_timeout_refuses_without_schema_or_record_changes(self):
        self._legacy()
        before = self._state()
        with self.engine.connect() as writer:
            with writer.begin():
                writer.exec_driver_sql("LOCK TABLE patients IN ROW EXCLUSIVE MODE")
                started = time.monotonic()
                with self.assertRaises(sa.exc.DBAPIError):
                    self._run()
                self.assertLess(time.monotonic() - started, 12)
        self.assertEqual(before, self._state())

    def test_concurrent_enum_replacement_cannot_cross_ownership_and_drop(self):
        self._run()
        original_rows = self._state()["rows"]
        with self.engine.connect() as connection:
            original_oid = connection.execute(sa.text("SELECT 'public.gptier'::regtype::oid")).scalar_one()
        migration = {}
        administrator = {}
        migration_started = threading.Event()
        administrator_started = threading.Event()
        writer = self.engine.connect()
        writer_tx = writer.begin()
        writer.exec_driver_sql("LOCK TABLE patients IN ROW EXCLUSIVE MODE")

        def migrate():
            try:
                with self.engine.begin() as connection:
                    migration["pid"] = connection.execute(sa.text("SELECT pg_backend_pid()")).scalar_one()
                    migration_started.set()
                    self._command(connection, "downgrade")
                migration["completed"] = True
            except Exception as exc:
                migration["error"] = exc

        def replace_enum():
            try:
                with self.engine.begin() as connection:
                    administrator["pid"] = connection.execute(sa.text("SELECT pg_backend_pid()")).scalar_one()
                    administrator_started.set()
                    connection.exec_driver_sql("ALTER TYPE public.gptier RENAME TO moved_racing_gptier")
                    connection.exec_driver_sql("CREATE TYPE public.gptier AS ENUM ('external-racing-sentinel')")
                administrator["completed"] = True
            except Exception as exc:
                administrator["error"] = exc

        def waits_on_lock(pid):
            deadline = time.monotonic() + 3
            with self.engine.connect() as observer:
                while time.monotonic() < deadline:
                    if observer.execute(sa.text(
                        "SELECT cardinality(pg_blocking_pids(:pid)) > 0"
                    ), {"pid": pid}).scalar_one():
                        return True
                    time.sleep(0.02)
            return False

        worker = threading.Thread(target=migrate, daemon=True)
        ddl_worker = threading.Thread(target=replace_enum, daemon=True)
        worker.start()
        ddl_started = False
        try:
            self.assertTrue(migration_started.wait(3))
            self.assertTrue(waits_on_lock(migration["pid"]), "Downgrade must wait on the synthetic table writer")
            ddl_worker.start()
            ddl_started = True
            self.assertTrue(administrator_started.wait(3))
            self.assertTrue(waits_on_lock(administrator["pid"]), "Type replacement must wait behind catalog exclusion")
            writer_tx.commit()
            worker.join(12)
            ddl_worker.join(12)
            self.assertFalse(worker.is_alive() or ddl_worker.is_alive())
            if migration.get("completed"):
                self.assertIsInstance(administrator.get("error"), sa.exc.DBAPIError)
                self.assertFalse(administrator.get("completed", False))
                self.assertEqual(self._version(), [])
                with self.engine.connect() as connection:
                    self.assertIsNone(connection.execute(sa.text(
                        "SELECT to_regtype('public.gptier')"
                    )).scalar_one())
            else:
                # Refuse an unfinished writer or a bounded lock-order conflict;
                # neither path may lose an enum replacement or make a partial
                # schema/version transition.
                error = migration.get("error")
                if isinstance(error, RuntimeError):
                    self.assertIn("other active writer transactions", str(error))
                else:
                    self.assertIsInstance(error, sa.exc.DBAPIError)
                    sqlstate = getattr(error.orig, "pgcode", None) or getattr(error.orig, "sqlstate", None)
                    self.assertIn(sqlstate, {"55P03", "40P01"})
                self.assertEqual(self._version(), [ROOT_REVISION])
                self.assertEqual(original_rows, self._state()["rows"])
                with self.engine.connect() as connection:
                    self.assertEqual(connection.execute(sa.text(
                        "SELECT count(*) FROM pg_type WHERE oid = :oid"
                    ), {"oid": original_oid}).scalar_one(), 1)
                    self.assertIsNotNone(connection.execute(sa.text(
                        "SELECT to_regclass('public.practices')"
                    )).scalar_one())
                    if administrator.get("completed"):
                        self.assertEqual(connection.execute(sa.text(
                            "SELECT 'external-racing-sentinel'::public.gptier::text"
                        )).scalar_one(), "external-racing-sentinel")
                    else:
                        self.assertIsInstance(administrator.get("error"), sa.exc.DBAPIError)
                        self.assertEqual(connection.execute(sa.text(
                            "SELECT 'public.gptier'::regtype::oid"
                        )).scalar_one(), original_oid)
        finally:
            if writer_tx.is_active:
                writer_tx.rollback()
            writer.close()
            worker.join(22)
            if ddl_started:
                ddl_worker.join(22)

    def test_uncommitted_prior_enum_replacement_refuses_before_ownership(self):
        self._run()
        before = self._state()
        with self.engine.connect() as connection:
            original_oid = connection.execute(sa.text("SELECT 'public.gptier'::regtype::oid")).scalar_one()
        with self.engine.begin() as administrator:
            # Both statements finish, but the transaction deliberately remains
            # uncommitted while another connection attempts the migration.
            administrator.exec_driver_sql("ALTER TYPE public.gptier RENAME TO moved_uncommitted_gptier")
            administrator.exec_driver_sql("CREATE TYPE public.gptier AS ENUM ('prior-writer-sentinel')")
            self._assert_refused_unchanged("downgrade", "other active writer transactions")
            self.assertEqual(before, self._state())
            self.assertEqual(self._version(), [ROOT_REVISION])
        with self.engine.connect() as connection:
            self.assertEqual(connection.execute(sa.text(
                "SELECT 'public.moved_uncommitted_gptier'::regtype::oid"
            )).scalar_one(), original_oid)
            self.assertEqual(connection.execute(sa.text(
                "SELECT 'prior-writer-sentinel'::public.gptier::text"
            )).scalar_one(), "prior-writer-sentinel")
        self.assertEqual(before["rows"], self._state()["rows"])
        self._assert_refused_unchanged("downgrade", "without recognised revision ownership")


if __name__ == "__main__":
    unittest.main(verbosity=2)
