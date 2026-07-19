"""Exercise Stage 2 RLS and append-only audit controls on a disposable database."""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, make_url
from sqlalchemy.exc import DBAPIError


EXPECTED_DATABASE = "gp_pms_stage2_migration"
SCOPED_TABLES = (
    "bernie_booking_sessions",
    "bernie_session_events",
    "appointments",
    "appointment_audit_log",
    "appointment_command_idempotency",
)


def _expect_database_error(
    connection: Connection,
    operation: Callable[[], Any],
    *,
    expected_codes: set[str],
) -> str:
    savepoint = connection.begin_nested()
    try:
        operation()
    except DBAPIError as exc:
        savepoint.rollback()
        code = str(getattr(exc.orig, "pgcode", None) or getattr(exc.orig, "sqlstate", None))
        if code not in expected_codes:
            raise AssertionError(
                f"Expected PostgreSQL code in {sorted(expected_codes)}, received {code}."
            ) from exc
        return code
    savepoint.rollback()
    raise AssertionError("Expected the database operation to fail.")


def _set_practice_context(connection: Connection, practice_id: uuid.UUID | None) -> None:
    connection.execute(
        text("SELECT set_config('app.current_practice_id', :value, true)"),
        {"value": "" if practice_id is None else str(practice_id)},
    )


def _count_scoped_rows(connection: Connection) -> dict[str, int]:
    return {
        table_name: int(
            connection.execute(text(f'SELECT count(*) FROM "{table_name}"')).scalar_one()
        )
        for table_name in SCOPED_TABLES
    }


def run_acceptance(database_url: str) -> dict[str, Any]:
    url = make_url(database_url)
    if url.database != EXPECTED_DATABASE:
        raise ValueError(
            f"Refusing database {url.database!r}; this probe requires {EXPECTED_DATABASE!r}."
        )

    engine = create_engine(database_url)
    role_name = f"emr4_stage2_rls_probe_{uuid.uuid4().hex[:12]}"
    practice_a = uuid.uuid4()
    practice_b = uuid.uuid4()
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    practitioner_a = uuid.uuid4()
    practitioner_b = uuid.uuid4()
    appointment_a = uuid.uuid4()
    appointment_b = uuid.uuid4()
    audit_a = uuid.uuid4()
    audit_b = uuid.uuid4()
    command_a = uuid.uuid4()
    command_b = uuid.uuid4()
    session_a = f"stage2-rls-a-{uuid.uuid4().hex}"
    session_b = f"stage2-rls-b-{uuid.uuid4().hex}"
    event_a = uuid.uuid4()
    event_b = uuid.uuid4()
    now = datetime.now(timezone.utc)
    result: dict[str, Any] = {
        "database": EXPECTED_DATABASE,
        "role_attributes": {
            "login": False,
            "superuser": False,
            "bypass_rls": False,
        },
    }

    with engine.connect() as connection:
        outer = connection.begin()
        try:
            connection.execute(text(f"CREATE ROLE {role_name} NOLOGIN NOSUPERUSER NOBYPASSRLS"))
            connection.execute(text(f"GRANT USAGE ON SCHEMA public TO {role_name}"))
            connection.execute(
                text(
                    "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "
                    + ", ".join(f'"{table_name}"' for table_name in SCOPED_TABLES)
                    + f" TO {role_name}"
                )
            )

            for practice_id, label in ((practice_a, "A"), (practice_b, "B")):
                connection.execute(
                    text("INSERT INTO practices (id, name) VALUES (:id, :name)"),
                    {"id": practice_id, "name": f"Stage 2 synthetic practice {label}"},
                )
            for user_id, practice_id, label in (
                (user_a, practice_a, "a"),
                (user_b, practice_b, "b"),
            ):
                connection.execute(
                    text(
                        "INSERT INTO users (id, practice_id, email, password_hash, role) "
                        "VALUES (:id, :practice_id, :email, :password_hash, 'GP')"
                    ),
                    {
                        "id": user_id,
                        "practice_id": practice_id,
                        "email": f"stage2-rls-{label}-{uuid.uuid4().hex}@synthetic.invalid",
                        "password_hash": "synthetic-not-a-login-secret",
                    },
                )
            for practitioner_id, practice_id, label in (
                (practitioner_a, practice_a, "A"),
                (practitioner_b, practice_b, "B"),
            ):
                connection.execute(
                    text(
                        "INSERT INTO practitioners (id, practice_id, first_name, last_name) "
                        "VALUES (:id, :practice_id, :first_name, 'Synthetic')"
                    ),
                    {
                        "id": practitioner_id,
                        "practice_id": practice_id,
                        "first_name": f"Stage2{label}",
                    },
                )
            for appointment_id, practice_id, practitioner_id, user_id in (
                (appointment_a, practice_a, practitioner_a, user_a),
                (appointment_b, practice_b, practitioner_b, user_b),
            ):
                connection.execute(
                    text(
                        "INSERT INTO appointments "
                        "(id, practice_id, practitioner_id, booked_by, start_time, "
                        " appointment_date, start_time_local, duration_minutes, status, booked_via) "
                        "VALUES (:id, :practice_id, :practitioner_id, :user_id, :start_time, "
                        " :appointment_date, :start_time_local, 15, 'Booked', 'Receptionist')"
                    ),
                    {
                        "id": appointment_id,
                        "practice_id": practice_id,
                        "practitioner_id": practitioner_id,
                        "user_id": user_id,
                        "start_time": now,
                        "appointment_date": now.date(),
                        "start_time_local": now.time().replace(tzinfo=None),
                    },
                )
            for audit_id, practice_id, appointment_id, user_id in (
                (audit_a, practice_a, appointment_a, user_a),
                (audit_b, practice_b, appointment_b, user_b),
            ):
                connection.execute(
                    text(
                        "INSERT INTO appointment_audit_log "
                        "(id, practice_id, appointment_id, confirmed_by_user_id, action) "
                        "VALUES (:id, :practice_id, :appointment_id, :user_id, 'create')"
                    ),
                    {
                        "id": audit_id,
                        "practice_id": practice_id,
                        "appointment_id": appointment_id,
                        "user_id": user_id,
                    },
                )
            for command_id, practice_id, user_id, label in (
                (command_a, practice_a, user_a, "a"),
                (command_b, practice_b, user_b, "b"),
            ):
                connection.execute(
                    text(
                        "INSERT INTO appointment_command_idempotency "
                        "(id, practice_id, actor_user_id, actor_role, operation_id, route_family, "
                        " idempotency_key_hash, request_body_hash, state) "
                        "VALUES (:id, :practice_id, :actor_user_id, 'GP', :operation_id, "
                        " :route_family, :key_hash, :body_hash, 'in_progress')"
                    ),
                    {
                        "id": command_id,
                        "practice_id": practice_id,
                        "actor_user_id": str(user_id),
                        "operation_id": f"stage2RlsProbe{label}",
                        "route_family": "stage2-rls-probe",
                        "key_hash": label * 64,
                        "body_hash": label * 64,
                    },
                )
            for session_id, practice_id, user_id, label in (
                (session_a, practice_a, user_a, "a"),
                (session_b, practice_b, user_b, "b"),
            ):
                connection.execute(
                    text(
                        "INSERT INTO bernie_booking_sessions "
                        "(session_id, practice_id, staff_user_id, surface_id, state, expires_at) "
                        "VALUES (:session_id, :practice_id, :user_id, :surface_id, "
                        " 'instruction_entry', :expires_at)"
                    ),
                    {
                        "session_id": session_id,
                        "practice_id": practice_id,
                        "user_id": user_id,
                        "surface_id": f"stage2-rls-{label}",
                        "expires_at": now + timedelta(hours=24),
                    },
                )
            for event_id, session_id, practice_id, label in (
                (event_a, session_a, practice_a, "a"),
                (event_b, session_b, practice_b, "b"),
            ):
                connection.execute(
                    text(
                        "INSERT INTO bernie_session_events "
                        "(id, practice_id, session_id, event_id, event_type, session_revision, "
                        " turn_index, occurred_at, expected_revision, payload_hash, payload) "
                        "VALUES (:id, :practice_id, :session_id, :event_id, 'staff_instruction', "
                        " 1, 0, :occurred_at, 0, :payload_hash, '{}'::jsonb)"
                    ),
                    {
                        "id": event_id,
                        "practice_id": practice_id,
                        "session_id": session_id,
                        "event_id": f"stage2-rls-{label}-event",
                        "occurred_at": now,
                        "payload_hash": label * 64,
                    },
                )

            result["owner_update_sqlstate"] = _expect_database_error(
                connection,
                lambda: connection.execute(
                    text("UPDATE appointment_audit_log SET confirmed_warnings='[]'::jsonb WHERE id=:id"),
                    {"id": audit_a},
                ),
                expected_codes={"55000"},
            )
            result["owner_delete_sqlstate"] = _expect_database_error(
                connection,
                lambda: connection.execute(
                    text("DELETE FROM appointment_audit_log WHERE id=:id"),
                    {"id": audit_a},
                ),
                expected_codes={"55000"},
            )

            connection.execute(text(f"SET LOCAL ROLE {role_name}"))
            _set_practice_context(connection, None)
            missing_context_counts = _count_scoped_rows(connection)
            if any(missing_context_counts.values()):
                raise AssertionError(f"RLS did not fail closed without context: {missing_context_counts}")
            result["missing_context_counts"] = missing_context_counts

            _set_practice_context(connection, practice_a)
            practice_a_counts = _count_scoped_rows(connection)
            if any(count != 1 for count in practice_a_counts.values()):
                raise AssertionError(f"Practice A did not see exactly its fixture rows: {practice_a_counts}")
            result["practice_a_counts"] = practice_a_counts

            foreign_ids = {
                "bernie_booking_sessions": ("session_id", session_b),
                "bernie_session_events": ("id", event_b),
                "appointments": ("id", appointment_b),
                "appointment_audit_log": ("id", audit_b),
                "appointment_command_idempotency": ("id", command_b),
            }
            foreign_visible = {}
            for table_name, (column_name, value) in foreign_ids.items():
                foreign_visible[table_name] = int(
                    connection.execute(
                        text(
                            f'SELECT count(*) FROM "{table_name}" '
                            f'WHERE "{column_name}"=:value'
                        ),
                        {"value": value},
                    ).scalar_one()
                )
            if any(foreign_visible.values()):
                raise AssertionError(f"Cross-practice rows were visible: {foreign_visible}")
            result["foreign_visible_counts"] = foreign_visible

            foreign_update = connection.execute(
                text("UPDATE appointments SET reason='blocked-cross-practice' WHERE id=:id"),
                {"id": appointment_b},
            ).rowcount
            if foreign_update != 0:
                raise AssertionError("Cross-practice appointment update was not hidden by RLS.")
            result["foreign_update_rowcount"] = foreign_update

            result["foreign_insert_sqlstate"] = _expect_database_error(
                connection,
                lambda: connection.execute(
                    text(
                        "INSERT INTO bernie_booking_sessions "
                        "(session_id, practice_id, staff_user_id, surface_id, state, expires_at) "
                        "VALUES (:session_id, :practice_id, :user_id, 'cross-practice', "
                        " 'instruction_entry', :expires_at)"
                    ),
                    {
                        "session_id": f"stage2-cross-{uuid.uuid4().hex}",
                        "practice_id": practice_b,
                        "user_id": user_b,
                        "expires_at": now + timedelta(hours=24),
                    },
                ),
                expected_codes={"42501"},
            )

            cross_reference_sqlstates = {}
            cross_reference_sqlstates["event_to_foreign_session"] = (
                _expect_database_error(
                    connection,
                    lambda: connection.execute(
                        text(
                            "INSERT INTO bernie_session_events "
                            "(id, practice_id, session_id, event_id, event_type, "
                            " session_revision, turn_index, occurred_at, expected_revision, "
                            " payload_hash, payload) "
                            "VALUES (:id, :practice_id, :session_id, :event_id, "
                            " 'staff_instruction', 2, 0, :occurred_at, 1, "
                            " :payload_hash, '{}'::jsonb)"
                        ),
                        {
                            "id": uuid.uuid4(),
                            "practice_id": practice_a,
                            "session_id": session_b,
                            "event_id": f"stage2-cross-event-{uuid.uuid4().hex}",
                            "occurred_at": now,
                            "payload_hash": "c" * 64,
                        },
                    ),
                    expected_codes={"23503"},
                )
            )
            cross_reference_sqlstates["audit_to_foreign_appointment"] = (
                _expect_database_error(
                    connection,
                    lambda: connection.execute(
                        text(
                            "INSERT INTO appointment_audit_log "
                            "(id, practice_id, appointment_id, confirmed_by_user_id, action) "
                            "VALUES (:id, :practice_id, :appointment_id, :user_id, 'create')"
                        ),
                        {
                            "id": uuid.uuid4(),
                            "practice_id": practice_a,
                            "appointment_id": appointment_b,
                            "user_id": user_a,
                        },
                    ),
                    expected_codes={"23503"},
                )
            )
            cross_reference_sqlstates["audit_to_foreign_command"] = (
                _expect_database_error(
                    connection,
                    lambda: connection.execute(
                        text(
                            "INSERT INTO appointment_audit_log "
                            "(id, practice_id, appointment_id, confirmed_by_user_id, "
                            " action, command_id) "
                            "VALUES (:id, :practice_id, :appointment_id, :user_id, "
                            " 'create', :command_id)"
                        ),
                        {
                            "id": uuid.uuid4(),
                            "practice_id": practice_a,
                            "appointment_id": appointment_a,
                            "user_id": user_a,
                            "command_id": command_b,
                        },
                    ),
                    expected_codes={"23503"},
                )
            )
            cross_reference_sqlstates["command_to_foreign_appointment"] = (
                _expect_database_error(
                    connection,
                    lambda: connection.execute(
                        text(
                            "UPDATE appointment_command_idempotency "
                            "SET target_appointment_id=:appointment_id WHERE id=:command_id"
                        ),
                        {"appointment_id": appointment_b, "command_id": command_a},
                    ),
                    expected_codes={"23503"},
                )
            )
            cross_reference_sqlstates["command_to_foreign_audit"] = (
                _expect_database_error(
                    connection,
                    lambda: connection.execute(
                        text(
                            "UPDATE appointment_command_idempotency "
                            "SET audit_log_id=:audit_id WHERE id=:command_id"
                        ),
                        {"audit_id": audit_b, "command_id": command_a},
                    ),
                    expected_codes={"23503"},
                )
            )
            result["cross_practice_reference_sqlstates"] = cross_reference_sqlstates

            own_appointment = uuid.uuid4()
            connection.execute(
                text(
                    "INSERT INTO appointments "
                    "(id, practice_id, practitioner_id, booked_by, start_time, appointment_date, "
                    " start_time_local, duration_minutes, status, booked_via) "
                    "VALUES (:id, :practice_id, :practitioner_id, :user_id, :start_time, "
                    " :appointment_date, :start_time_local, 15, 'Booked', 'Receptionist')"
                ),
                {
                    "id": own_appointment,
                    "practice_id": practice_a,
                    "practitioner_id": practitioner_a,
                    "user_id": user_a,
                    "start_time": now + timedelta(minutes=30),
                    "appointment_date": now.date(),
                    "start_time_local": (now + timedelta(minutes=30)).time().replace(tzinfo=None),
                },
            )
            own_audit = uuid.uuid4()
            connection.execute(
                text(
                    "INSERT INTO appointment_audit_log "
                    "(id, practice_id, appointment_id, confirmed_by_user_id, action) "
                    "VALUES (:id, :practice_id, :appointment_id, :user_id, 'create')"
                ),
                {
                    "id": own_audit,
                    "practice_id": practice_a,
                    "appointment_id": own_appointment,
                    "user_id": user_a,
                },
            )
            result["practice_scoped_insert_visible"] = int(
                connection.execute(
                    text("SELECT count(*) FROM appointment_audit_log WHERE id=:id"),
                    {"id": own_audit},
                ).scalar_one()
            )
            if result["practice_scoped_insert_visible"] != 1:
                raise AssertionError("Practice-scoped audit insert was not visible.")

            deleted_session_rows = connection.execute(
                text("DELETE FROM bernie_booking_sessions WHERE session_id=:session_id"),
                {"session_id": session_a},
            ).rowcount
            remaining_event_rows = int(
                connection.execute(
                    text("SELECT count(*) FROM bernie_session_events WHERE session_id=:session_id"),
                    {"session_id": session_a},
                ).scalar_one()
            )
            if deleted_session_rows != 1 or remaining_event_rows != 0:
                raise AssertionError(
                    "Practice-scoped retention delete did not cascade session event detail."
                )
            result["practice_scoped_retention_delete"] = {
                "session_rows": deleted_session_rows,
                "remaining_event_rows": remaining_event_rows,
            }

            connection.execute(text("RESET ROLE"))
            result["status"] = "pass"
        finally:
            if connection.in_transaction():
                try:
                    connection.execute(text("RESET ROLE"))
                except DBAPIError:
                    # A failed probe may abort the transaction before RESET;
                    # the unconditional outer rollback still restores state.
                    pass
                outer.rollback()

    with engine.connect() as verification:
        role_exists = bool(
            verification.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname=:role_name"),
                {"role_name": role_name},
            ).scalar_one_or_none()
        )
        fixture_exists = bool(
            verification.execute(
                text("SELECT 1 FROM practices WHERE id=:practice_id"),
                {"practice_id": practice_a},
            ).scalar_one_or_none()
        )
    engine.dispose()
    if role_exists or fixture_exists:
        raise AssertionError(
            f"Probe cleanup failed: role_exists={role_exists}, fixture_exists={fixture_exists}."
        )
    result["transactional_cleanup"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    args = parser.parse_args()
    print(json.dumps(run_acceptance(args.database_url), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
