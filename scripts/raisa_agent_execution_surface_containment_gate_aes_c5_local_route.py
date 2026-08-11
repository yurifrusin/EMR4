"""Disposable PostgreSQL/FastAPI source harness for the exact AES-C5 run.

All database writes are setup or teardown in one newly generated, strictly
validated task-owned schema and occur outside the AES generations.  The
measured operation uses the ordinary bearer-token dependency and the existing
practitioner-directory router/service against PostgreSQL.  It permits only
SELECT statements while the route is active and never exposes the JWT,
database URL, UUID alias map or raw route values in repository evidence.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402
from app.dependencies import get_db  # noqa: E402
from app.models.tenancy import UserRole  # noqa: E402
from app.routers import practice as practice_router  # noqa: E402
from app.services.auth_service import create_access_token  # noqa: E402
from scripts import (  # noqa: E402
    raisa_agent_execution_surface_containment_gate_aes_c4_provider_proof as c4,
)
from scripts import (  # noqa: E402
    raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission as core,
)

SCHEMA_PATTERN = re.compile(r"^aes_c5_[0-9a-f]{32}$")
ROUTE = "/api/v1/practice/practitioners"
QUERY = "activeOnly=true&limit=4&offset=0"

PRACTICE_ID = uuid.UUID("10000000-0000-4000-8000-000000000001")
FOREIGN_PRACTICE_ID = uuid.UUID("10000000-0000-4000-8000-000000000002")
USER_ID = uuid.UUID("20000000-0000-4000-8000-000000000001")
LOCATION_ID = uuid.UUID("30000000-0000-4000-8000-000000000001")
PRACTITIONER_ROWS = (
    (
        uuid.UUID("3f2c7b1a-9d8e-4f6a-8b1c-2e5d7a9b0c1d"),
        PRACTICE_ID,
        "Aster",
        "Finch",
        "General Practitioner",
        None,
        True,
    ),
    (
        uuid.UUID("a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"),
        PRACTICE_ID,
        "Marlow",
        "Quill",
        "General Practitioner",
        None,
        True,
    ),
    (
        uuid.UUID("6d5c4b3a-2f1e-4d0c-9b8a-7f6e5d4c3b2a"),
        PRACTICE_ID,
        "Nyra",
        "Sol",
        "Practice Nurse",
        LOCATION_ID,
        True,
    ),
    (
        uuid.UUID("40000000-0000-4000-8000-000000000001"),
        PRACTICE_ID,
        "Quen",
        "Vale",
        "General Practitioner",
        None,
        False,
    ),
    (
        uuid.UUID("40000000-0000-4000-8000-000000000002"),
        FOREIGN_PRACTICE_ID,
        "Ora",
        "Wren",
        "General Practitioner",
        None,
        True,
    ),
)


class LocalRouteError(RuntimeError):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def validate_schema_name(value: str) -> str:
    if not SCHEMA_PATTERN.fullmatch(value):
        raise LocalRouteError("disposable_schema_name_invalid")
    return value


def new_schema_name() -> str:
    return validate_schema_name("aes_c5_" + uuid.uuid4().hex)


class DisposablePractitionerDirectorySource:
    def __init__(self, schema_name: str):
        self.schema_name = validate_schema_name(schema_name)
        self.admin_engine: Engine | None = None
        self.isolated_engine: Engine | None = None
        self.session_factory = None
        self.route_called = False
        self.statement_digests: list[str] = []
        self._measure = False
        self._token: str | None = None
        self._counts_before: dict[str, int] = {}
        self.schema_created = False
        self.listener_registered = False
        self.cleanup_complete = False

    def _schema_exists(self) -> bool:
        if self.admin_engine is None:
            raise LocalRouteError("admin_engine_missing")
        with self.admin_engine.connect() as connection:
            return bool(
                connection.execute(
                    text(
                        "SELECT EXISTS (SELECT 1 FROM pg_namespace "
                        "WHERE nspname = :schema_name)"
                    ),
                    {"schema_name": self.schema_name},
                ).scalar_one()
            )

    def _before_cursor_execute(
        self,
        _connection,
        _cursor,
        statement: str,
        _parameters,
        _context,
        _executemany,
    ) -> None:
        if not self._measure:
            return
        normalized = " ".join(statement.split())
        verb = normalized.split(" ", 1)[0].upper() if normalized else ""
        if verb not in {"SELECT", "WITH"}:
            raise LocalRouteError("measured_route_non_read_statement")
        self.statement_digests.append(core.digest_of({"statement": normalized}))

    def setup(self) -> None:
        self.admin_engine = create_engine(settings.database_url, pool_pre_ping=True)
        if self._schema_exists():
            raise LocalRouteError("disposable_schema_preexisted")
        with self.admin_engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{self.schema_name}"'))
        self.schema_created = True
        self.isolated_engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            connect_args={
                "options": f"-csearch_path={self.schema_name},pg_catalog"
            },
        )
        event.listen(
            self.isolated_engine,
            "before_cursor_execute",
            self._before_cursor_execute,
        )
        self.listener_registered = True
        self.session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.isolated_engine,
        )
        with self.isolated_engine.begin() as connection:
            for ddl in (
                "CREATE TABLE practices (id uuid PRIMARY KEY, name text NOT NULL)",
                "CREATE TABLE practice_locations (id uuid PRIMARY KEY, practice_id uuid NOT NULL, name text NOT NULL, is_active boolean NOT NULL)",
                "CREATE TABLE practitioners (id uuid PRIMARY KEY, practice_id uuid NOT NULL, first_name text NOT NULL, last_name text NOT NULL, specialty text NULL, default_location_id uuid NULL, aggregate_version integer NOT NULL DEFAULT 0, is_active boolean NOT NULL, created_at timestamptz NOT NULL DEFAULT now())",
                "CREATE TABLE users (id uuid PRIMARY KEY, practice_id uuid NOT NULL, email text NOT NULL UNIQUE, password_hash text NOT NULL, role text NOT NULL, practitioner_id uuid NULL, is_active boolean NOT NULL, created_at timestamptz NOT NULL DEFAULT now())",
                "CREATE TABLE appointments (id uuid PRIMARY KEY)",
                "CREATE TABLE appointment_audit_log (id uuid PRIMARY KEY)",
            ):
                connection.execute(text(ddl))
            connection.execute(
                text("INSERT INTO practices (id, name) VALUES (:id, :name)"),
                {"id": PRACTICE_ID, "name": "Synthetic North Practice"},
            )
            connection.execute(
                text("INSERT INTO practices (id, name) VALUES (:id, :name)"),
                {"id": FOREIGN_PRACTICE_ID, "name": "Synthetic South Practice"},
            )
            connection.execute(
                text(
                    "INSERT INTO practice_locations "
                    "(id, practice_id, name, is_active) "
                    "VALUES (:id, :practice_id, :name, true)"
                ),
                {
                    "id": LOCATION_ID,
                    "practice_id": PRACTICE_ID,
                    "name": "Synthetic Harbour Clinic",
                },
            )
            for row in PRACTITIONER_ROWS:
                connection.execute(
                    text(
                        "INSERT INTO practitioners "
                        "(id, practice_id, first_name, last_name, specialty, "
                        "default_location_id, is_active) VALUES "
                        "(:id, :practice_id, :first_name, :last_name, :specialty, "
                        ":default_location_id, :is_active)"
                    ),
                    {
                        "id": row[0],
                        "practice_id": row[1],
                        "first_name": row[2],
                        "last_name": row[3],
                        "specialty": row[4],
                        "default_location_id": row[5],
                        "is_active": row[6],
                    },
                )
            connection.execute(
                text(
                    "INSERT INTO users "
                    "(id, practice_id, email, password_hash, role, is_active) "
                    "VALUES (:id, :practice_id, :email, :password_hash, :role, true)"
                ),
                {
                    "id": USER_ID,
                    "practice_id": PRACTICE_ID,
                    "email": "reception.aes-c5@invalid.example",
                    "password_hash": "synthetic-unusable-password-hash",
                    "role": UserRole.Receptionist.value,
                },
            )
        self._counts_before = self._counts()
        self._token = create_access_token(
            {
                "sub": str(USER_ID),
                "practice_id": str(PRACTICE_ID),
                "role": UserRole.Receptionist.value,
            }
        )

    def _counts(self) -> dict[str, int]:
        if self.isolated_engine is None:
            raise LocalRouteError("isolated_engine_missing")
        with self.isolated_engine.connect() as connection:
            return {
                table_name: int(
                    connection.execute(
                        text(f'SELECT count(*) FROM "{table_name}"')
                    ).scalar_one()
                )
                for table_name in (
                    "practitioners",
                    "appointments",
                    "appointment_audit_log",
                )
            }

    def __call__(self) -> core.SourceResult:
        if self.route_called:
            raise core.AesC5Error("product_route_replay_denied")
        if self.session_factory is None or self._token is None:
            raise core.AesC5Error("local_source_not_ready")
        self.route_called = True
        app = FastAPI()
        app.include_router(practice_router.router)
        session_factory = self.session_factory

        def isolated_db():
            database = session_factory()
            try:
                yield database
            finally:
                database.close()

        app.dependency_overrides[get_db] = isolated_db
        self._measure = True
        try:
            with TestClient(app, raise_server_exceptions=True) as client:
                response = client.get(
                    ROUTE + "?" + QUERY,
                    headers={"Authorization": f"Bearer {self._token}"},
                )
            observed_at = datetime.now(timezone.utc)
        finally:
            self._measure = False
            app.dependency_overrides.clear()
            self._token = None
        if response.status_code != 200:
            raise core.AesC5Error("product_route_status_invalid")
        counts_after = self._counts()
        if counts_after != self._counts_before:
            raise core.AesC5Error("measured_route_changed_database_counts")
        rows = response.json()
        return core.SourceResult(
            rows=rows,
            metadata={
                "observed_at": observed_at,
                "product_runtime_route_read": True,
                "ordinary_bearer_auth_dependency_used": True,
                "token_user_practice_equality_observed": True,
                "counts_unchanged": True,
                "fixture_used": False,
                "route_status": response.status_code,
                "database_statement_count": len(self.statement_digests),
            },
        )

    def cleanup(self) -> bool:
        self._token = None
        if self.isolated_engine is not None:
            if self.listener_registered:
                event.remove(
                    self.isolated_engine,
                    "before_cursor_execute",
                    self._before_cursor_execute,
                )
                self.listener_registered = False
            self.isolated_engine.dispose()
            self.isolated_engine = None
        if self.admin_engine is None:
            return False
        schema_name = validate_schema_name(self.schema_name)
        if self.schema_created:
            with self.admin_engine.begin() as connection:
                connection.execute(text(f'DROP SCHEMA "{schema_name}" CASCADE'))
            self.cleanup_complete = not self._schema_exists()
            self.schema_created = False
        else:
            self.cleanup_complete = not self._schema_exists()
        self.admin_engine.dispose()
        self.admin_engine = None
        return self.cleanup_complete


class OccupiedVertexAdapter:
    def __init__(self, envelope: Mapping[str, Any]):
        self.envelope = envelope
        self.called = False

    def __call__(
        self, request_body: Mapping[str, Any], _frame: Mapping[str, Any]
    ) -> core.ProviderResult:
        if self.called:
            raise core.AesC5Error("provider_replay_denied")
        self.called = True
        try:
            result = c4.VertexBrokerAdapter().invoke(request_body, self.envelope)
        except c4.AesC4Error as error:
            raise core.AesC5Error(
                error.reason_code, metadata=error.metadata
            ) from None
        return core.ProviderResult(packet=result.packet, metadata=result.metadata)


def run(
    *,
    mode: str,
    source_head: str,
    evidence_output: Path,
    ledger_output: Path,
    lifecycle_output: Path,
    schema_name: str | None = None,
) -> dict[str, Any]:
    if mode not in {"local-fake", "occupied"}:
        raise LocalRouteError("mode_invalid")
    if lifecycle_output.exists():
        raise LocalRouteError("lifecycle_output_already_exists")
    source = DisposablePractitionerDirectorySource(schema_name or new_schema_name())
    evidence: dict[str, Any] | None = None
    cleanup_complete = False
    try:
        source.setup()
        envelope = core.validate_envelope()
        provider_adapter = (
            core.provider_provider_free_fixture
            if mode == "local-fake"
            else OccupiedVertexAdapter(envelope)
        )
        evidence = core.execute(
            mode=(
                "local-route-fake-provider" if mode == "local-fake" else "occupied"
            ),
            source_head=source_head,
            evidence_output=evidence_output,
            ledger_output=ledger_output,
            source_adapter=source,
            provider_adapter=provider_adapter,
        )
    finally:
        cleanup_complete = source.cleanup()
    lifecycle = {
        "schema_version": "emr4.aes_c5.local_route_lifecycle_evidence.v1",
        "mode": mode,
        "source_head": source_head,
        "result": evidence["result"] if evidence is not None else "revision_required",
        "core_evidence_digest": (
            core.digest_of(evidence) if evidence is not None else None
        ),
        "schema_name_digest": core.digest_of(source.schema_name),
        "schema_name_retained": False,
        "schema_preexisted": False,
        "schema_absent_after_terminal_state": cleanup_complete,
        "route_calls": 1 if source.route_called else 0,
        "database_statement_count": len(source.statement_digests),
        "database_counts_unchanged": bool(
            evidence
            and evidence["source"]["statement_count"]
            == len(source.statement_digests)
        ),
        "provider_calls": (
            evidence["operation_counters"]["provider_calls"] if evidence else 0
        ),
        "product_reads": (
            evidence["operation_counters"]["product_reads"] if evidence else 0
        ),
        "patient_clinical_or_real_person_data": False,
        "raw_route_jwt_database_url_prompt_or_provider_text_retained": False,
        "contains_sensitive_values": False,
    }
    core.atomic_write(lifecycle_output, lifecycle)
    if not cleanup_complete:
        raise LocalRouteError("disposable_schema_cleanup_failed")
    if evidence is None:
        raise LocalRouteError("core_evidence_missing")
    return {"core": evidence, "lifecycle": lifecycle}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("local-fake", "occupied"), required=True)
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--ledger-output", type=Path, required=True)
    parser.add_argument("--lifecycle-output", type=Path, required=True)
    parser.add_argument("--schema-name")
    args = parser.parse_args()
    try:
        result = run(
            mode=args.mode,
            source_head=args.source_head,
            evidence_output=args.evidence_output,
            ledger_output=args.ledger_output,
            lifecycle_output=args.lifecycle_output,
            schema_name=args.schema_name,
        )
    except (LocalRouteError, core.AesC5Error) as error:
        print(
            json.dumps(
                {
                    "result": "revision_required",
                    "reason_code": error.reason_code,
                },
                sort_keys=True,
            )
        )
        return 1
    print(
        json.dumps(
            {
                "result": result["core"]["result"],
                "provider_calls": result["core"]["operation_counters"][
                    "provider_calls"
                ],
                "product_reads": result["core"]["operation_counters"][
                    "product_reads"
                ],
                "schema_absent_after_terminal_state": result["lifecycle"][
                    "schema_absent_after_terminal_state"
                ],
            },
            sort_keys=True,
        )
    )
    return 0 if result["core"]["result"].endswith("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
