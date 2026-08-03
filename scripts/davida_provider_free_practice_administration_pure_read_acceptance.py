"""Disposable live-local PostgreSQL proof for the Davida pure-read context desk.

Provider-free, in-process, backend-only, authored-synthetic. Uses one unique
allowlisted disposable PostgreSQL database, the current Alembic head and the
existing finite product-read LOGIN/NOLOGIN role builders (no new role class or
auth policy). Proves the exact active-practitioner precedent plus the new pure
active-location projection through the product capability session and composes
one deterministic minimal context frame.

Evidence label: ``provider_free_in_process_backend_postgres``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.tenancy import (  # noqa: E402
    Practice,
    PracticeLocation,
    Practitioner,
    User,
    UserRole,
)
from app.schemas.practice import PractitionerOut  # noqa: E402
from app.schemas.practice_administration import (  # noqa: E402
    ActivePracticeLocationOut,
)
from app.services.application_auth_product_read_database_role import (  # noqa: E402
    create_product_read_capability_statements,
    create_product_read_login_statements,
    drop_product_read_role_statement,
)
from app.services.application_auth_product_read_operational import (  # noqa: E402
    ProductReadPoolPolicy,
    create_product_read_engine,
    create_product_read_session_factory,
)
from app.services.auth_service import hash_password  # noqa: E402
from app.services.practice.active_location_directory_read import (  # noqa: E402
    list_active_location_directory,
)
from app.services.practice.practice_administration_context_desk import (  # noqa: E402
    compose_practice_administration_context,
    ResourceReferenceBinding,
    ResourceReferenceRegistry,
)
from app.services.practice.practitioner_directory_read import (  # noqa: E402
    list_practitioner_directory,
)
from scripts.raisa_postgresql_oidc_operational_connection_boundary_acceptance import (  # noqa: E402
    _base_database_url,
    _require_alembic,
    _role_absent,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "davida-provider-free-practice-administration-pure-read"
    / "provider-free-in-process-backend-postgres-evidence.json"
)
RESULT = "provider_free_practice_administration_pure_read_pass"
EVIDENCE_LABEL = "provider_free_in_process_backend_postgres"
MIGRATION_HEAD = "u0v1w2x3y4z5"
PARENT_HEAD = "t9u0v1w2x3y4"
DATABASE_PATTERN = re.compile(
    r"^emr4_davida_pure_read_acceptance_[0-9a-f]{12}$"
)
PRODUCT_LOGIN_PATTERN = re.compile(r"^emr4_product_read_login_[a-z0-9_]{8,40}$")
PRODUCT_CAPABILITY_PATTERN = re.compile(
    r"^emr4_product_read_runtime_[a-z0-9_]{8,40}$"
)
UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)
DML_DDL_RE = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|GRANT|REVOKE|TRUNCATE|COPY)",
    re.IGNORECASE,
)
NOW = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)
PRACTICE_REF = "practice_synth_primary"
PRINCIPAL_REF = "principal_synth_primary"
CORRELATION_ID = "correlation-davida-pure-read-primary"
EMPTY_PRACTICE_REF = "practice_synth_empty"
EMPTY_PRINCIPAL_REF = "principal_synth_empty"
EMPTY_CORRELATION_ID = "correlation-davida-pure-read-empty"
BOUND_PRACTICE_REF = "practice_synth_bound"
BOUND_PRINCIPAL_REF = "principal_synth_bound"
BOUND_CORRELATION_ID = "correlation-davida-pure-read-bound"
TABLE_NAMES = ("practices", "practice_locations", "practitioners", "users")
BOUND_LOCATION_COUNT = 205
EXPECTED_ORDERED_PRIMARY_LOCATIONS = (
    "Alpha Clinic",
    "Midtown Clinic",
    "Zebra Clinic",
)


class AcceptanceFailure(RuntimeError):
    pass


def _database_exists(maintenance: Engine, name: str) -> bool:
    with maintenance.connect() as connection:
        return bool(
            connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": name},
            ).scalar_one_or_none()
        )


def _create_database(maintenance: Engine, name: str) -> None:
    if not DATABASE_PATTERN.fullmatch(name) or _database_exists(maintenance, name):
        raise AcceptanceFailure("unsafe_or_preexisting_database")
    with maintenance.connect() as connection:
        quoted = connection.dialect.identifier_preparer.quote(name)
        connection.execute(text(f"CREATE DATABASE {quoted}"))


def _drop_database(maintenance: Engine, name: str) -> bool:
    if not DATABASE_PATTERN.fullmatch(name):
        raise AcceptanceFailure("unsafe_database_cleanup_name")
    with maintenance.connect() as connection:
        connection.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :name AND pid <> pg_backend_pid()"
            ),
            {"name": name},
        )
        if _database_exists(maintenance, name):
            quoted = connection.dialect.identifier_preparer.quote(name)
            connection.execute(text(f"DROP DATABASE {quoted}"))
    return not _database_exists(maintenance, name)


def _probe_sqlstate(engine: Engine, statement: str) -> str | None:
    try:
        with engine.connect() as connection:
            connection.execute(text(statement)).first()
    except DBAPIError as exc:
        return getattr(exc.orig, "sqlstate", None) or getattr(
            exc.orig, "pgcode", None
        )
    return None


def _drop_role(
    maintenance: Engine,
    role_name: str,
    *,
    kind: str,
) -> bool:
    patterns = {
        "product_login": PRODUCT_LOGIN_PATTERN,
        "product_capability": PRODUCT_CAPABILITY_PATTERN,
    }
    if kind not in patterns or not patterns[kind].fullmatch(role_name):
        raise AcceptanceFailure("unsafe_role_cleanup_name")
    with maintenance.begin() as connection:
        present = connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
            {"name": role_name},
        ).scalar_one_or_none()
        if present is not None:
            connection.execute(text(drop_product_read_role_statement(role_name)))
    return _role_absent(maintenance, role_name)


def _table_snapshot(owner: Engine, table_name: str) -> tuple[int, str]:
    with owner.connect() as connection:
        row = connection.execute(
            text(
                "SELECT count(*), COALESCE("
                "md5(string_agg(row_to_json(t)::text, '|' "
                "ORDER BY row_to_json(t)::text)), 'empty') "
                f"FROM {table_name} t"
            )
        ).one()
    return int(row[0]), str(row[1])


def _seed(owner_factory: sessionmaker[Session]) -> dict[str, Any]:
    with owner_factory() as db, db.begin():
        primary = Practice(name="Authored Synthetic Primary")
        foreign = Practice(name="Authored Synthetic Foreign")
        empty = Practice(name="Authored Synthetic Empty")
        bound = Practice(name="Authored Synthetic Bound")
        db.add_all((primary, foreign, empty, bound))
        db.flush()

        alpha_loc = PracticeLocation(
            practice_id=primary.id, name="Alpha Clinic", is_active=True
        )
        midtown_loc = PracticeLocation(
            practice_id=primary.id, name="Midtown Clinic", is_active=True
        )
        zebra_loc = PracticeLocation(
            practice_id=primary.id, name="Zebra Clinic", is_active=True
        )
        inactive_loc = PracticeLocation(
            practice_id=primary.id, name="Inactive Clinic", is_active=False
        )
        db.add_all((alpha_loc, midtown_loc, zebra_loc, inactive_loc))
        db.flush()

        alpha_prac = Practitioner(
            practice_id=primary.id,
            first_name="Alpha",
            last_name="Synthetic",
            specialty="GP",
            default_location_id=alpha_loc.id,
            is_active=True,
        )
        beta_prac = Practitioner(
            practice_id=primary.id,
            first_name="Beta",
            last_name="Synthetic",
            specialty="GP",
            is_active=True,
        )
        inactive_prac = Practitioner(
            practice_id=primary.id,
            first_name="Inactive",
            last_name="Synthetic",
            specialty="GP",
            is_active=False,
        )
        db.add_all((alpha_prac, beta_prac, inactive_prac))
        db.flush()

        foreign_loc = PracticeLocation(
            practice_id=foreign.id, name="Foreign Clinic", is_active=True
        )
        foreign_prac = Practitioner(
            practice_id=foreign.id,
            first_name="Foreign",
            last_name="Synthetic",
            specialty="GP",
            is_active=True,
        )
        db.add_all((foreign_loc, foreign_prac))
        db.flush()

        bound_locations = [
            PracticeLocation(
                practice_id=bound.id,
                name=f"Bound Clinic {i:03d}",
                is_active=True,
            )
            for i in range(1, BOUND_LOCATION_COUNT + 1)
        ]
        db.add_all(bound_locations)
        db.flush()

        primary_user = User(
            practice_id=primary.id,
            email="gp-primary@authored-synthetic.invalid",
            password_hash=hash_password("AuthoredSyntheticOnly1!"),
            role=UserRole.GP,
            practitioner_id=alpha_prac.id,
            is_active=True,
        )
        foreign_user = User(
            practice_id=foreign.id,
            email="gp-foreign@authored-synthetic.invalid",
            password_hash=hash_password("AuthoredSyntheticOnly1!"),
            role=UserRole.GP,
            practitioner_id=foreign_prac.id,
            is_active=True,
        )
        empty_user = User(
            practice_id=empty.id,
            email="gp-empty@authored-synthetic.invalid",
            password_hash=hash_password("AuthoredSyntheticOnly1!"),
            role=UserRole.GP,
            is_active=True,
        )
        bound_user = User(
            practice_id=bound.id,
            email="gp-bound@authored-synthetic.invalid",
            password_hash=hash_password("AuthoredSyntheticOnly1!"),
            role=UserRole.GP,
            is_active=True,
        )
        db.add_all((primary_user, foreign_user, empty_user, bound_user))
        db.flush()

        return {
            "primary_id": primary.id,
            "foreign_id": foreign.id,
            "empty_id": empty.id,
            "bound_id": bound.id,
            "alpha_location_id": alpha_loc.id,
            "midtown_location_id": midtown_loc.id,
            "zebra_location_id": zebra_loc.id,
            "inactive_location_id": inactive_loc.id,
            "alpha_practitioner_id": alpha_prac.id,
            "beta_practitioner_id": beta_prac.id,
            "inactive_practitioner_id": inactive_prac.id,
            "foreign_location_id": foreign_loc.id,
            "foreign_practitioner_id": foreign_prac.id,
            "bound_location_ids": [loc.id for loc in bound_locations],
            "primary_user_id": primary_user.id,
            "foreign_user_id": foreign_user.id,
            "empty_user_id": empty_user.id,
            "bound_user_id": bound_user.id,
            "primary_expected_location_ids": [
                alpha_loc.id,
                midtown_loc.id,
                zebra_loc.id,
            ],
            "primary_expected_practitioner_ids": {
                alpha_prac.id,
                beta_prac.id,
            },
        }


def _build_registry(
    practitioner_rows: list[PractitionerOut],
    location_rows: list[ActivePracticeLocationOut],
    *,
    practice_ref: str,
) -> ResourceReferenceRegistry:
    bindings: list[ResourceReferenceBinding] = []
    for index, practitioner in enumerate(practitioner_rows, start=1):
        bindings.append(
            ResourceReferenceBinding(
                kind="practitioner",
                resource_id=practitioner.id,
                reference=f"prac_synth_{index:04d}",
                practice_ref=practice_ref,
            )
        )
    for index, location in enumerate(location_rows, start=1):
        bindings.append(
            ResourceReferenceBinding(
                kind="location",
                resource_id=location.id,
                reference=f"loc_synth_{index:04d}",
                practice_ref=practice_ref,
            )
        )
    return ResourceReferenceRegistry.build(bindings)


def _sensitive_values(seeded: dict[str, Any]) -> list[str]:
    values: list[str] = []

    def add(value: Any) -> None:
        if isinstance(value, uuid.UUID):
            values.append(str(value))
        elif isinstance(value, str):
            values.append(value)

    for value in seeded.values():
        if isinstance(value, (list, tuple)):
            for item in value:
                add(item)
        elif isinstance(value, set):
            for item in value:
                add(item)
        else:
            add(value)
    return values


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    suffix = secrets.token_hex(6)
    database_name = f"emr4_davida_pure_read_acceptance_{suffix}"
    product_login = f"emr4_product_read_login_{suffix}"
    product_capability = f"emr4_product_read_runtime_{suffix}"
    product_password = secrets.token_urlsafe(36)
    base = _base_database_url()
    target = base.set(database=database_name)
    product_target = target.set(
        username=product_login,
        password=product_password,
    )
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner: Engine | None = None
    product_engine: Engine | None = None
    direct_product_login_engine: Engine | None = None
    database_created = False
    created_roles: list[tuple[str, str]] = []
    raw_values: list[str] = []
    failure_type: str | None = None
    stage = "preflight"
    evidence: dict[str, Any] = {
        "schema_version": (
            "emr4.davida.provider-free-practice-administration-pure-read."
            "evidence.v1"
        ),
        "result": "revision_required",
        "evidence_label": EVIDENCE_LABEL,
        "data_class": "authored_synthetic",
        "default_off": True,
        "cleanup": {
            "database_absent_after": False,
            "task_roles_absent_after": False,
        },
    }
    try:
        if not all(
            (
                DATABASE_PATTERN.fullmatch(database_name),
                PRODUCT_LOGIN_PATTERN.fullmatch(product_login),
                PRODUCT_CAPABILITY_PATTERN.fullmatch(product_capability),
            )
        ):
            raise AcceptanceFailure("generated_identifier_invalid")
        _create_database(maintenance, database_name)
        database_created = True
        stage = "migration"
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        _require_alembic(target, "downgrade", PARENT_HEAD)
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        _require_alembic(target, "check")
        if MIGRATION_HEAD not in current:
            raise AcceptanceFailure("migration_head_mismatch")

        owner = create_engine(target, pool_pre_ping=True)
        owner_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=owner,
        )
        stage = "roles"
        with owner.begin() as connection:
            for statement in create_product_read_capability_statements(
                product_capability
            ):
                connection.execute(text(statement))
            created_roles.append((product_capability, "product_capability"))
            for statement in create_product_read_login_statements(
                product_login,
                product_capability,
                connection_limit=2,
            ):
                connection.execute(text(statement))
            created_roles.append((product_login, "product_login"))
            connection.execute(
                text(
                    f'ALTER ROLE "{product_login}" PASSWORD '
                    f"'{product_password}'"
                )
            )

        stage = "seed"
        seeded = _seed(owner_factory)
        raw_values = _sensitive_values(seeded)
        before_snapshot = {
            name: _table_snapshot(owner, name) for name in TABLE_NAMES
        }

        product_engine = create_product_read_engine(
            product_target,
            login_role=product_login,
            capability_role=product_capability,
            policy=ProductReadPoolPolicy(
                pool_size=2,
                max_overflow=0,
                login_connection_limit=2,
            ),
        )
        product_factory = create_product_read_session_factory(product_engine)

        stage = "product_reads"
        captured_statements: list[str] = []

        @event.listens_for(product_engine, "before_cursor_execute")
        def _capture(
            conn,
            cursor,
            statement: str,
            parameters,
            context,
            executemany: bool,
        ) -> None:
            captured_statements.append(statement)

        primary_user = User(
            id=seeded["primary_user_id"],
            practice_id=seeded["primary_id"],
            role=UserRole.GP,
            practitioner_id=seeded["alpha_practitioner_id"],
            is_active=True,
        )
        foreign_user = User(
            id=seeded["foreign_user_id"],
            practice_id=seeded["foreign_id"],
            role=UserRole.GP,
            practitioner_id=seeded["foreign_practitioner_id"],
            is_active=True,
        )
        empty_user = User(
            id=seeded["empty_user_id"],
            practice_id=seeded["empty_id"],
            role=UserRole.GP,
            is_active=True,
        )
        bound_user = User(
            id=seeded["bound_user_id"],
            practice_id=seeded["bound_id"],
            role=UserRole.GP,
            is_active=True,
        )

        with product_factory() as db:
            practitioner_rows = list_practitioner_directory(
                db=db,
                current_user=primary_user,
                active_only=True,
            )
            location_rows = list_active_location_directory(
                db=db,
                current_user=primary_user,
            )
            foreign_practitioner_rows = list_practitioner_directory(
                db=db,
                current_user=foreign_user,
                active_only=True,
            )
            foreign_location_rows = list_active_location_directory(
                db=db,
                current_user=foreign_user,
            )
            empty_practitioner_rows = list_practitioner_directory(
                db=db,
                current_user=empty_user,
                active_only=True,
            )
            empty_location_rows = list_active_location_directory(
                db=db,
                current_user=empty_user,
            )
            bound_location_rows = list_active_location_directory(
                db=db,
                current_user=bound_user,
            )
            session_state = {
                "new": len(db.new),
                "dirty": len(db.dirty),
                "deleted": len(db.deleted),
            }
        event.remove(product_engine, "before_cursor_execute", _capture)

        after_snapshot = {
            name: _table_snapshot(owner, name) for name in TABLE_NAMES
        }

        stage = "context_frame"
        primary_registry = _build_registry(
            practitioner_rows,
            location_rows,
            practice_ref=PRACTICE_REF,
        )
        frame_one = compose_practice_administration_context(
            practitioners=practitioner_rows,
            active_locations=location_rows,
            practice_ref=PRACTICE_REF,
            principal_ref=PRINCIPAL_REF,
            correlation_id=CORRELATION_ID,
            observed_at=NOW,
            resource_references=primary_registry,
        )
        frame_two = compose_practice_administration_context(
            practitioners=practitioner_rows,
            active_locations=location_rows,
            practice_ref=PRACTICE_REF,
            principal_ref=PRINCIPAL_REF,
            correlation_id=CORRELATION_ID,
            observed_at=NOW,
            resource_references=primary_registry,
        )
        frame = frame_one
        deterministic_frame = frame_one == frame_two
        revision_payload = {
            key: value
            for key, value in frame.items()
            if key != "content_revision"
        }
        recomputed_revision = hashlib.sha256(
            json.dumps(
                revision_payload,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        revision_matches = recomputed_revision == frame["content_revision"]
        frame_serialized = json.dumps(frame, sort_keys=True)
        no_uuid_in_frame = UUID_RE.search(frame_serialized) is None
        context_schema_path = (
            ROOT
            / "orchestration"
            / "continuity"
            / "davida-provider-free-practice-administration-pure-read"
            / "context-contract.schema.json"
        )
        import jsonschema  # noqa: PLC0415

        jsonschema.Draft202012Validator(
            json.loads(context_schema_path.read_text(encoding="utf-8"))
        ).validate(frame)

        empty_registry = ResourceReferenceRegistry.build([])
        empty_frame = compose_practice_administration_context(
            practitioners=[],
            active_locations=[],
            practice_ref=EMPTY_PRACTICE_REF,
            principal_ref=EMPTY_PRINCIPAL_REF,
            correlation_id=EMPTY_CORRELATION_ID,
            observed_at=NOW,
            resource_references=empty_registry,
        )
        empty_frame_counts = (
            empty_frame["frames"]["practitioners"]["count"],
            empty_frame["frames"]["locations"]["count"],
        )
        bound_registry = ResourceReferenceRegistry.build(
            [
                ResourceReferenceBinding(
                    kind="location",
                    resource_id=location.id,
                    reference=f"loc_synth_{index:04d}",
                    practice_ref=BOUND_PRACTICE_REF,
                )
                for index, location in enumerate(
                    bound_location_rows, start=1
                )
            ]
        )
        bound_frame = compose_practice_administration_context(
            practitioners=[],
            active_locations=bound_location_rows,
            practice_ref=BOUND_PRACTICE_REF,
            principal_ref=BOUND_PRINCIPAL_REF,
            correlation_id=BOUND_CORRELATION_ID,
            observed_at=NOW,
            resource_references=bound_registry,
        )
        bound_frame_location_count = bound_frame["frames"]["locations"]["count"]

        stage = "assertions"
        expected_location_ids = [
            str(value) for value in seeded["primary_expected_location_ids"]
        ]
        actual_location_ids = [str(location.id) for location in location_rows]
        actual_location_names = [location.name for location in location_rows]
        foreign_location_ids = {
            str(location.id) for location in foreign_location_rows
        }
        expected_practitioner_ids = {
            str(value) for value in seeded["primary_expected_practitioner_ids"]
        }
        actual_practitioner_ids = {
            str(practitioner.id) for practitioner in practitioner_rows
        }

        exact_location_fields = all(
            set(location.model_dump().keys()) == {"id", "name"}
            for location in location_rows
        )
        ordered_by_name_id = (
            actual_location_names == list(EXPECTED_ORDERED_PRIMARY_LOCATIONS)
            and actual_location_ids == expected_location_ids
        )
        inactive_location_excluded = (
            str(seeded["inactive_location_id"])
            not in actual_location_ids
        )
        inactive_practitioner_excluded = (
            str(seeded["inactive_practitioner_id"])
            not in actual_practitioner_ids
        )
        tenant_isolation = (
            str(seeded["foreign_location_id"])
            not in actual_location_ids
            and str(seeded["foreign_practitioner_id"])
            not in actual_practitioner_ids
            and foreign_location_ids
            == {str(seeded["foreign_location_id"])}
            and len(foreign_practitioner_rows) == 1
        )
        empty_behavior = (
            len(empty_practitioner_rows) == 0
            and len(empty_location_rows) == 0
            and empty_frame_counts == (0, 0)
        )
        bounds_behavior = (
            len(bound_location_rows) == 200
            and bound_frame_location_count == 200
        )
        dml_or_ddl_statements = [
            statement
            for statement in captured_statements
            if DML_DDL_RE.match(statement)
        ]
        select_only = (
            not dml_or_ddl_statements
            and any(
                "FROM practice_locations" in statement.upper()
                for statement in captured_statements
            )
            and any(
                "FROM practitioners" in statement.upper()
                for statement in captured_statements
            )
        )
        tables_unchanged = before_snapshot == after_snapshot
        session_state_clean = (
            session_state["new"] == 0
            and session_state["dirty"] == 0
            and session_state["deleted"] == 0
        )
        observed_expiry_seconds = (
            datetime.fromisoformat(frame["expires_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(
                frame["observed_at"].replace("Z", "+00:00")
            )
        ).total_seconds()
        authority_ceiling_all_false = all(
            value is False for value in frame["authority_ceiling"].values()
        )
        labels_exact = (
            frame["labels"]["minimal"] is True
            and frame["labels"]["non_authoritative"] is True
            and frame["labels"]["database_truth_authoritative"] is True
        )
        blocked_sources_exact = frame["blocked_sources"] == [
            {
                "name": "diary_rooms",
                "path": "GET /api/v1/diary/rooms",
                "reason": "normalizes_and_commits_during_nominal_read",
            },
            {
                "name": "diary_waiting_areas",
                "path": "GET /api/v1/diary/waiting-areas",
                "reason": "normalizes_and_commits_during_nominal_read",
            },
            {
                "name": "appointment_waiting_room_queue",
                "path": "GET /api/v1/appointments/waiting-room",
                "reason": "patient_linked_appointment_queue_closed_data",
            },
        ]
        practitioner_source_exact = (
            frame["frames"]["practitioners"]["source"]
            == "app.services.practice.practitioner_directory_read."
            "list_practitioner_directory"
        )
        location_source_exact = (
            frame["frames"]["locations"]["source"]
            == "app.services.practice.active_location_directory_read."
            "list_active_location_directory"
        )
        labels_frames_exact = (
            frame["frames"]["practitioners"]["label"] == "live_api_fact"
            and frame["frames"]["practitioners"]["projection"] == "pure"
            and frame["frames"]["practitioners"]["active_only"] is True
            and frame["frames"]["locations"]["label"] == "live_api_fact"
            and frame["frames"]["locations"]["projection"] == "pure"
            and frame["frames"]["locations"]["active_only"] is True
        )

        stage = "privilege_denials"
        direct_product_login_engine = create_engine(product_target)
        role_probe_states = {
            "product_capability_insert_practitioner": _probe_sqlstate(
                product_engine,
                "INSERT INTO practitioners (id, practice_id, first_name, "
                "last_name, is_active) VALUES "
                "('11111111-1111-1111-1111-111111111111', "
                "'22222222-2222-2222-2222-222222222222', 'X', 'Y', true)",
            ),
            "product_capability_update_practitioners": _probe_sqlstate(
                product_engine,
                "UPDATE practitioners SET is_active = false",
            ),
            "product_capability_delete_locations": _probe_sqlstate(
                product_engine,
                "DELETE FROM practice_locations",
            ),
            "product_capability_sensitive_users_email": _probe_sqlstate(
                product_engine,
                "SELECT email FROM users LIMIT 1",
            ),
            "product_capability_sensitive_practitioner_provider": _probe_sqlstate(
                product_engine,
                "SELECT provider_number FROM practitioners LIMIT 1",
            ),
            "product_login_direct_directory": _probe_sqlstate(
                direct_product_login_engine,
                "SELECT id FROM practitioners LIMIT 1",
            ),
        }
        all_privilege_denied = set(role_probe_states.values()) == {"42501"}

        passed = all(
            (
                exact_location_fields,
                ordered_by_name_id,
                inactive_location_excluded,
                inactive_practitioner_excluded,
                tenant_isolation,
                empty_behavior,
                bounds_behavior,
                select_only,
                tables_unchanged,
                session_state_clean,
                observed_expiry_seconds == 120,
                deterministic_frame,
                revision_matches,
                no_uuid_in_frame,
                authority_ceiling_all_false,
                labels_exact,
                labels_frames_exact,
                blocked_sources_exact,
                practitioner_source_exact,
                location_source_exact,
                all_privilege_denied,
            )
        )
        evidence.update(
            {
                "result": RESULT if passed else "revision_required",
                "migration_head": MIGRATION_HEAD,
                "projection": {
                    "active_location_schema_fields": ["id", "name"],
                    "active_location_max_rows": 200,
                    "location_service_pure": True,
                    "practitioner_service_pure": True,
                    "active_only": True,
                    "route_or_graphql_added": False,
                },
                "tenant_isolation": {
                    "foreign_rows_excluded": tenant_isolation,
                },
                "active_only_behavior": {
                    "primary_active_locations": len(location_rows),
                    "inactive_location_excluded": inactive_location_excluded,
                    "inactive_practitioner_excluded": inactive_practitioner_excluded,
                    "primary_active_practitioners": len(practitioner_rows),
                },
                "ordering": {
                    "ordered_by_name_id": ordered_by_name_id,
                    "ordered_names_sha256": hashlib.sha256(
                        "|".join(actual_location_names).encode("utf-8")
                    ).hexdigest(),
                },
                "empty_behavior": {
                    "empty_practice_practitioners": len(empty_practitioner_rows),
                    "empty_practice_locations": len(empty_location_rows),
                    "empty_frame_counts": list(empty_frame_counts),
                },
                "bounds_behavior": {
                    "seeded_active_locations": BOUND_LOCATION_COUNT,
                    "returned_locations": len(bound_location_rows),
                    "bound_frame_location_count": bound_frame_location_count,
                },
                "context_frame": {
                    "schema_version": frame["schema_version"],
                    "data_class": frame["data_class"],
                    "observed_expiry_interval_seconds": int(
                        observed_expiry_seconds
                    ),
                    "practitioner_frame_count": frame["frames"]["practitioners"][
                        "count"
                    ],
                    "location_frame_count": frame["frames"]["locations"]["count"],
                    "deterministic_frame": deterministic_frame,
                    "content_revision": frame["content_revision"],
                    "revision_recompute_matches": revision_matches,
                    "no_uuid_emitted": no_uuid_in_frame,
                    "opaque_references": True,
                    "authority_ceiling_all_false": authority_ceiling_all_false,
                    "blocked_sources_exact": blocked_sources_exact,
                    "labels_exact": labels_exact,
                    "labels_frames_exact": labels_frames_exact,
                    "frame_schema_valid": True,
                },
                "select_only": {
                    "dml_or_ddl_statements": len(dml_or_ddl_statements),
                    "captured_statements": len(captured_statements),
                    "select_reads_present": select_only,
                },
                "session_state": session_state,
                "table_integrity": {
                    "unchanged": tables_unchanged,
                    "tables": {
                        name: {
                            "count": after_snapshot[name][0],
                            "hash": after_snapshot[name][1],
                        }
                        for name in TABLE_NAMES
                    },
                },
                "privilege_denials": {
                    "probe_count": len(role_probe_states),
                    "all_insufficient_privilege": all_privilege_denied,
                },
                "claim_limits": [
                    "This proves one default-off provider-free authored-synthetic active practitioner/location pure-read projection and one deterministic minimal context frame through disposable PostgreSQL and the existing finite product-read roles.",
                    "It does not establish patient/clinical read safety, real identity, any route or GraphQL field, proposal/apply authority, provider use, deployment, production or release readiness.",
                ],
            }
        )
        serialized = json.dumps(evidence, sort_keys=True)
        sensitive_values = list(raw_values)
        sensitive_values.extend(
            (
                database_name,
                product_login,
                product_capability,
                product_password,
                PRACTICE_REF,
                PRINCIPAL_REF,
                CORRELATION_ID,
                EMPTY_PRACTICE_REF,
                EMPTY_PRINCIPAL_REF,
                EMPTY_CORRELATION_ID,
                BOUND_PRACTICE_REF,
                BOUND_PRINCIPAL_REF,
                BOUND_CORRELATION_ID,
            )
        )
        sensitive_values.extend(
            (
                "Authored Synthetic Primary",
                "Authored Synthetic Foreign",
                "Authored Synthetic Empty",
                "Authored Synthetic Bound",
                "Alpha Clinic",
                "Midtown Clinic",
                "Zebra Clinic",
                "Inactive Clinic",
                "Foreign Clinic",
                "Alpha Synthetic",
                "Beta Synthetic",
                "Inactive Synthetic",
                "Foreign Synthetic",
                "gp-primary@authored-synthetic.invalid",
                "gp-foreign@authored-synthetic.invalid",
                "gp-empty@authored-synthetic.invalid",
                "gp-bound@authored-synthetic.invalid",
            )
        )
        sensitive_values.extend(
            f"Bound Clinic {index:03d}" for index in range(1, 206)
        )
        evidence_sensitive_match_count = sum(
            value in serialized for value in sensitive_values
        )
        evidence["evidence_sensitive_match_count"] = evidence_sensitive_match_count
        if evidence_sensitive_match_count:
            raise AcceptanceFailure("sensitive_value_in_evidence")
        if not passed:
            raise AcceptanceFailure("one_or_more_acceptance_gates_failed")
    except Exception as exc:
        failure_type = type(exc).__name__
        evidence["result"] = "revision_required"
        evidence["failure_type"] = failure_type
        evidence["failure_stage"] = stage
        if isinstance(exc, AcceptanceFailure):
            evidence["failure_code"] = str(exc)
    finally:
        for engine in (direct_product_login_engine, product_engine, owner):
            if engine is not None:
                engine.dispose()
        if database_created:
            try:
                evidence["cleanup"]["database_absent_after"] = _drop_database(
                    maintenance,
                    database_name,
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["database_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["database_absent_after"] = True
        role_absence: list[bool] = []
        for role_name, kind in reversed(created_roles):
            try:
                role_absence.append(
                    _drop_role(
                        maintenance,
                        role_name,
                        kind=kind,
                    )
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["role_failure_type"] = type(
                    cleanup_exc
                ).__name__
                role_absence.append(False)
        evidence["cleanup"]["task_roles_absent_after"] = all(role_absence)
        maintenance.dispose()

    evidence["cleanup"]["passed"] = all(evidence["cleanup"].values())
    if not evidence["cleanup"]["passed"]:
        evidence["result"] = "revision_required"
    evidence["passed"] = (
        evidence["result"] == RESULT
        and evidence["cleanup"]["passed"]
        and failure_type is None
    )
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args()
    evidence = run_acceptance(output_path=args.output)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
