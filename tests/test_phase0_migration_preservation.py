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
import json
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
    connection.exec_driver_sql("SET LOCAL search_path TO public, pg_catalog, pg_temp")
    queries = {
        "relations": """SELECT n.nspname, c.relname, c.relkind, c.relpersistence,
            c.relrowsecurity, c.relforcerowsecurity, c.oid
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2""",
        "columns": """SELECT n.nspname, c.relname, a.attnum, a.attname,
            format_type(a.atttypid, a.atttypmod), a.attnotnull,
            pg_get_expr(d.adbin, d.adrelid), a.attidentity, a.attgenerated,
            a.atttypid, a.atttypmod, tn.nspname, t.typname, t.typtype,
            a.attcollation, cn.nspname, co.collname, e.extname, en.nspname
            FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_type t ON t.oid = a.atttypid JOIN pg_namespace tn ON tn.oid = t.typnamespace
            LEFT JOIN pg_collation co ON co.oid = a.attcollation
            LEFT JOIN pg_namespace cn ON cn.oid = co.collnamespace
            LEFT JOIN pg_depend ed ON ed.classid = 'pg_type'::regclass AND ed.objid = t.oid
              AND ed.refclassid = 'pg_extension'::regclass AND ed.deptype = 'e'
            LEFT JOIN pg_extension e ON e.oid = ed.refobjid
            LEFT JOIN pg_namespace en ON en.oid = e.extnamespace
            LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
            WHERE n.nspname IN ('public', 'phase0_shared')
              AND a.attnum > 0 AND NOT a.attisdropped ORDER BY 1, 2, 3""",
        "constraints": """SELECT n.nspname, c.relname, k.conname,
            pg_get_constraintdef(k.oid), k.oid, k.contype, k.conrelid, k.conindid,
            k.conkey, k.confrelid, k.confkey, k.confupdtype, k.confdeltype, k.confmatchtype,
            k.condeferrable, k.condeferred, k.convalidated, k.conislocal, k.coninhcount, k.conparentid
            FROM pg_constraint k JOIN pg_class c ON c.oid = k.conrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2, 3""",
        "indexes": """SELECT n.nspname, c.relname, ic.relname, i.indexrelid, i.indrelid,
            pg_get_indexdef(i.indexrelid), am.amname, i.indisunique, i.indisprimary,
            i.indisexclusion, i.indimmediate, i.indisvalid, i.indisready, i.indislive,
            i.indnullsnotdistinct, i.indnkeyatts, i.indnatts, i.indkey::smallint[],
            i.indoption::smallint[], i.indclass::oid[], i.indcollation::oid[],
            pg_get_expr(i.indexprs, i.indrelid), pg_get_expr(i.indpred, i.indrelid)
            FROM pg_index i JOIN pg_class c ON c.oid = i.indrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_class ic ON ic.oid = i.indexrelid JOIN pg_am am ON am.oid = ic.relam
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2, 3""",
        "index_key_semantics": """SELECT n.nspname, c.relname, ic.relname, x.ord,
            ns.nspname, oc.opcname, nt.nspname, t.typname, oc.opcdefault,
            am.amname, nf.nspname, f.opfname,
            nc.nspname, co.collname
            FROM pg_index i JOIN pg_class c ON c.oid = i.indrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_class ic ON ic.oid = i.indexrelid
            CROSS JOIN LATERAL unnest(i.indclass) WITH ORDINALITY x(oid, ord)
            JOIN pg_opclass oc ON oc.oid = x.oid JOIN pg_namespace ns ON ns.oid = oc.opcnamespace
            JOIN pg_type t ON t.oid = oc.opcintype JOIN pg_namespace nt ON nt.oid = t.typnamespace
            JOIN pg_am am ON am.oid = oc.opcmethod JOIN pg_opfamily f ON f.oid = oc.opcfamily
            JOIN pg_namespace nf ON nf.oid = f.opfnamespace
            LEFT JOIN pg_collation co ON co.oid = i.indcollation[(x.ord - 1)::integer]
            LEFT JOIN pg_namespace nc ON nc.oid = co.collnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2, 3, 4""",
        "column_slots": """SELECT n.nspname, c.relname, a.attnum, a.attname, a.attisdropped
            FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') AND a.attnum > 0
            ORDER BY 1, 2, 3""",
        "collations": """SELECT n.nspname, c.collname, c.oid, c.collprovider,
            c.collisdeterministic, c.collencoding, c.collcollate, c.collctype,
            c.colliculocale, c.collversion
            FROM pg_collation c JOIN pg_namespace n ON n.oid = c.collnamespace
            WHERE n.nspname IN ('public', 'phase0_shared') ORDER BY 1, 2""",
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

    def _constraint_name(self, connection, table, kind, keys):
        names = connection.execute(sa.text("""
            SELECT k.conname FROM pg_constraint k
            WHERE k.conrelid = to_regclass(:table) AND k.contype = :kind
              AND ARRAY(SELECT a.attname::text FROM unnest(k.conkey) WITH ORDINALITY x(num, ord)
                        JOIN pg_attribute a ON a.attrelid = k.conrelid AND a.attnum = x.num
                        ORDER BY x.ord) = CAST(:keys AS text[])
        """), {"table": "public." + table, "kind": kind, "keys": list(keys)}).scalars().all()
        self.assertEqual(len(names), 1)
        return connection.dialect.identifier_preparer.quote_identifier(names[0])

    def _assert_shape_valid(self):
        # Exercise the real comparator, with its original transaction/lock envelope.
        before = self._state()
        with self.engine.begin() as connection:
            if not getattr(type(self), "_runtime_identity_emitted", False):
                row = connection.execute(sa.text("""
                    SELECT current_setting('server_version_num'), version(), e.extversion,
                           en.nspname, tn.nspname, t.typname, d.deptype
                    FROM pg_extension e JOIN pg_namespace en ON en.oid = e.extnamespace
                    JOIN pg_depend d ON d.refclassid = 'pg_extension'::regclass
                      AND d.refobjid = e.oid AND d.classid = 'pg_type'::regclass AND d.deptype = 'e'
                    JOIN pg_type t ON t.oid = d.objid JOIN pg_namespace tn ON tn.oid = t.typnamespace
                    WHERE e.extname = 'vector' AND t.typname = 'vector'
                """)).one()
                print(json.dumps({"phase0_runtime_identity": dict(zip(
                    ("server_version_num", "version", "vector_extversion", "extension_namespace",
                     "type_namespace", "type_name", "membership_deptype"), row))}, sort_keys=True), flush=True)
                type(self)._runtime_identity_emitted = True
            with Operations.context(MigrationContext.configure(connection)):
                with self.revision._preservation_transaction():
                    self.revision._lock_tables(self.revision._public_tables())
                    self.revision._validate_post_upgrade_shape()
        self.assertEqual(before, self._state())

    def _assert_guard_refuses(self, category, table):
        before = self._state()
        ddl = []

        def record(connection, cursor, statement, parameters, context, executemany):
            if statement.lstrip().split(None, 1)[0].upper() in {"ALTER", "CREATE", "DROP", "TRUNCATE"}:
                ddl.append(statement)

        sa.event.listen(self.engine, "before_cursor_execute", record)
        try:
            with self.assertRaisesRegex(RuntimeError,
                    f"^Phase-0 refuses unexpected post-upgrade {category} in {table}:"):
                self._run("downgrade")
        finally:
            sa.event.remove(self.engine, "before_cursor_execute", record)
        self.assertEqual(ddl, [], "The actual Alembic downgrade must refuse before reversal DDL")
        self.assertEqual(before, self._state())
        self.assertEqual(self._version(), [ROOT_REVISION])

    def test_downgrade_accepts_generated_names_and_changed_physical_order(self):
        self._run()
        self._assert_shape_valid()
        with self.engine.begin() as connection:
            for table, kind, keys, new_name in (
                ("patients", "f", ("practice_id",), "phase0_renamed_patient_fk"),
                ("users", "u", ("email",), "phase0_renamed_email_uq"),
            ):
                name = self._constraint_name(connection, table, kind, keys)
                connection.exec_driver_sql(f'ALTER TABLE public.{table} RENAME CONSTRAINT {name} TO {new_name}')
            original = connection.exec_driver_sql("SELECT attnum FROM pg_attribute WHERE attrelid = 'public.practices'::regclass AND attname = 'abn'").scalar_one()
            connection.exec_driver_sql("ALTER TABLE public.practices DROP COLUMN abn")
            connection.exec_driver_sql("ALTER TABLE public.practices ADD COLUMN abn varchar(20)")
            changed = connection.exec_driver_sql("SELECT attnum, atttypid, atttypmod, attnotnull, atthasdef FROM pg_attribute WHERE attrelid = 'public.practices'::regclass AND attname = 'abn'").one()
            self.assertNotEqual(original, changed[0])
            self.assertEqual(changed[1], connection.exec_driver_sql("SELECT 'pg_catalog.varchar'::regtype::oid").scalar_one())
            self.assertEqual(tuple(changed[2:]), (24, False, False))
            self.assertTrue(connection.exec_driver_sql(f"SELECT attisdropped FROM pg_attribute WHERE attrelid = 'public.practices'::regclass AND attnum = {original}").scalar_one())
        self._assert_shape_valid()
        self._run("downgrade")
        self.assertEqual(self._version(), [])
        self._run()
        self._assert_shape_valid()
        self.assertEqual(self._version(), [ROOT_REVISION])
        self._run("downgrade")

    def test_downgrade_refuses_column_set_and_record_changes(self):
        for mutate, undo, observe, expected in (
            ("ADD COLUMN phase0_extra text", "DROP COLUMN phase0_extra",
             "SELECT count(*) FROM pg_attribute WHERE attrelid='public.practices'::regclass AND attname='phase0_extra' AND NOT attisdropped", 1),
            ("ALTER COLUMN abn TYPE varchar(21)", "ALTER COLUMN abn TYPE varchar(20)",
             "SELECT atttypmod FROM pg_attribute WHERE attrelid='public.practices'::regclass AND attname='abn'", 25),
        ):
            with self.subTest(mutation=mutate):
                self._run()
                self._assert_shape_valid()
                with self.engine.begin() as connection:
                    connection.exec_driver_sql("ALTER TABLE public.practices " + mutate)
                    self.assertEqual(connection.exec_driver_sql(observe).scalar_one(), expected)
                self._assert_guard_refuses("columns", "practices")
                with self.engine.begin() as connection:
                    connection.exec_driver_sql("ALTER TABLE public.practices " + undo)
                self._assert_shape_valid()
                self._run("downgrade")

    def test_downgrade_refuses_column_collation_change(self):
        self._run()
        self._assert_shape_valid()
        with self.engine.begin() as connection:
            connection.exec_driver_sql('CREATE COLLATION public.phase0_test_collation FROM pg_catalog."C"')
            connection.exec_driver_sql("ALTER TABLE public.practices ALTER COLUMN abn TYPE varchar(20) COLLATE public.phase0_test_collation")
            self.assertTrue(connection.exec_driver_sql("SELECT a.attcollation <> t.typcollation FROM pg_attribute a JOIN pg_type t ON t.oid=a.atttypid WHERE a.attrelid='public.practices'::regclass AND a.attname='abn'").scalar_one())
        self._assert_guard_refuses("columns", "practices")

    def test_downgrade_refuses_fk_target_action_timing_and_validation(self):
        for target, suffix, field, value in (
            ("phase0_shared.practices", "", "confrelid::regclass::text", "phase0_shared.practices"),
            ("public.practices", "ON DELETE CASCADE", "confdeltype", "c"),
            ("public.practices", "DEFERRABLE INITIALLY DEFERRED", "condeferred", True),
            ("public.practices", "NOT VALID", "convalidated", False),
        ):
            with self.subTest(target=target, suffix=suffix):
                self._run()
                self._assert_shape_valid()
                with self.engine.begin() as connection:
                    if target.startswith("phase0_shared"):
                        connection.exec_driver_sql("CREATE SCHEMA phase0_shared")
                        connection.exec_driver_sql("CREATE TABLE phase0_shared.practices(id uuid PRIMARY KEY)")
                    name = self._constraint_name(connection, "appointment_types", "f", ("practice_id",))
                    connection.exec_driver_sql(f"ALTER TABLE public.appointment_types DROP CONSTRAINT {name}")
                    connection.exec_driver_sql(f"ALTER TABLE public.appointment_types ADD CONSTRAINT phase0_changed_fk FOREIGN KEY(practice_id) REFERENCES {target}(id) {suffix}")
                    self.assertEqual(connection.exec_driver_sql(f"SELECT {field} FROM pg_constraint WHERE conrelid='public.appointment_types'::regclass AND conname='phase0_changed_fk'").scalar_one(), value)
                self._assert_guard_refuses("constraints", "appointment_types")
                with self.engine.begin() as connection:
                    connection.exec_driver_sql("ALTER TABLE public.appointment_types DROP CONSTRAINT phase0_changed_fk")
                    connection.exec_driver_sql("ALTER TABLE public.appointment_types ADD FOREIGN KEY(practice_id) REFERENCES public.practices(id)")
                    if target.startswith("phase0_shared"):
                        connection.exec_driver_sql("DROP TABLE phase0_shared.practices")
                        connection.exec_driver_sql("DROP SCHEMA phase0_shared")
                self._assert_shape_valid()
                self._run("downgrade")

    def test_downgrade_refuses_unique_constraint_timing_change(self):
        self._run()
        self._assert_shape_valid()
        with self.engine.begin() as connection:
            name = self._constraint_name(connection, "users", "u", ("email",))
            connection.exec_driver_sql(f"ALTER TABLE public.users DROP CONSTRAINT {name}")
            connection.exec_driver_sql("ALTER TABLE public.users ADD CONSTRAINT phase0_changed_uq UNIQUE(email) DEFERRABLE INITIALLY DEFERRED")
            self.assertTrue(connection.exec_driver_sql("SELECT condeferred FROM pg_constraint WHERE conrelid='public.users'::regclass AND conname='phase0_changed_uq'").scalar_one())
            self.assertFalse(connection.exec_driver_sql("SELECT indisunique FROM pg_index WHERE indexrelid='public.ix_users_email'::regclass").scalar_one())
        self._assert_guard_refuses("constraints", "users")

    def test_downgrade_refuses_standalone_index_set_and_order_changes(self):
        for changed_order in (False, True):
            with self.subTest(changed_order=changed_order):
                self._run()
                self._assert_shape_valid()
                with self.engine.begin() as connection:
                    if changed_order:
                        connection.exec_driver_sql("DROP INDEX public.ix_schedule_overrides_practitioner_id_date")
                        connection.exec_driver_sql("CREATE INDEX ix_schedule_overrides_practitioner_id_date ON public.schedule_overrides(date, practitioner_id)")
                        keys = connection.exec_driver_sql("SELECT ARRAY(SELECT a.attname::text FROM unnest(i.indkey) WITH ORDINALITY x(num, ord) JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=x.num ORDER BY x.ord) FROM pg_index i WHERE i.indexrelid='public.ix_schedule_overrides_practitioner_id_date'::regclass").scalar_one()
                        self.assertEqual(keys, ["date", "practitioner_id"])
                    else:
                        connection.exec_driver_sql("CREATE INDEX ix_phase0_extra_practice_abn ON public.practices(abn)")
                        self.assertFalse(connection.exec_driver_sql("SELECT EXISTS(SELECT 1 FROM pg_constraint WHERE contype IN ('p','u') AND conindid='public.ix_phase0_extra_practice_abn'::regclass)").scalar_one())
                self._assert_guard_refuses("indexes", "schedule_overrides" if changed_order else "practices")
                with self.engine.begin() as connection:
                    if changed_order:
                        connection.exec_driver_sql("DROP INDEX public.ix_schedule_overrides_practitioner_id_date")
                        connection.exec_driver_sql("CREATE INDEX ix_schedule_overrides_practitioner_id_date ON public.schedule_overrides(practitioner_id, date)")
                    else:
                        connection.exec_driver_sql("DROP INDEX public.ix_phase0_extra_practice_abn")
                self._assert_shape_valid()
                self._run("downgrade")

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
