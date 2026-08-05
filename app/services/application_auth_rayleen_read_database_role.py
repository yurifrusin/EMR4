"""Distinct least-privilege PostgreSQL roles for the Rayleen A4 read."""

from __future__ import annotations

import re


_LOGIN = re.compile(r"^emr4_rayleen_read_login_[a-z0-9_]{8,40}$")
_CAPABILITY = re.compile(r"^emr4_rayleen_read_runtime_[a-z0-9_]{8,40}$")


def require_rayleen_read_login_role(role_name: str) -> str:
    return _require(role_name, _LOGIN, "Rayleen read login")


def require_rayleen_read_capability_role(role_name: str) -> str:
    return _require(role_name, _CAPABILITY, "Rayleen read capability")


def create_rayleen_read_capability_statements(role_name: str) -> tuple[str, ...]:
    role = require_rayleen_read_capability_role(role_name)
    quoted = f'"{role}"'
    return (
        f"CREATE ROLE {quoted} NOLOGIN NOSUPERUSER NOCREATEDB "
        "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS",
        f"ALTER ROLE {quoted} SET row_security = on",
        f"ALTER ROLE {quoted} SET statement_timeout = '5s'",
        f"ALTER ROLE {quoted} SET lock_timeout = '2s'",
        f"ALTER ROLE {quoted} SET idle_in_transaction_session_timeout = '5s'",
        f"GRANT USAGE ON SCHEMA public TO {quoted}",
        f"GRANT SELECT (id, practice_id, role, practitioner_id, is_active) "
        f"ON TABLE public.users TO {quoted}",
        f"GRANT SELECT (id, practice_id, name, is_active) "
        f"ON TABLE public.practice_locations TO {quoted}",
        f"GRANT SELECT (id, timezone) ON TABLE public.practices TO {quoted}",
        f"GRANT SELECT (id, practice_id, location_id, practitioner_id, status, "
        f"start_time, appointment_date, start_time_local, waiting_area_id, "
        f"queue_position) ON TABLE public.appointments TO {quoted}",
        f"GRANT SELECT (practice_id, appointment_id, action, status_after, "
        f"created_at) ON TABLE public.appointment_audit_log TO {quoted}",
    )


def create_rayleen_read_login_statements(
    login_role_name: str,
    capability_role_name: str,
    *,
    connection_limit: int = 2,
) -> tuple[str, ...]:
    login = require_rayleen_read_login_role(login_role_name)
    capability = require_rayleen_read_capability_role(capability_role_name)
    if not 1 <= connection_limit <= 4:
        raise ValueError("Rayleen read connection limit is outside 1..4")
    return (
        f'CREATE ROLE "{login}" LOGIN PASSWORD NULL NOSUPERUSER NOCREATEDB '
        "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS "
        f"CONNECTION LIMIT {connection_limit}",
        f'GRANT "{capability}" TO "{login}"',
    )


def drop_rayleen_read_role_statement(role_name: str) -> str:
    if not isinstance(role_name, str) or not (
        _LOGIN.fullmatch(role_name) or _CAPABILITY.fullmatch(role_name)
    ):
        raise ValueError("Rayleen read role is outside the task-safe allowlist")
    return f'DROP ROLE "{role_name}"'


def _require(value: str, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f"{label} role is outside the task-safe allowlist")
    return value


__all__ = [
    "create_rayleen_read_capability_statements",
    "create_rayleen_read_login_statements",
    "drop_rayleen_read_role_statement",
    "require_rayleen_read_capability_role",
    "require_rayleen_read_login_role",
]
