"""Exact PostgreSQL capability-role contract for shared application auth.

PostgreSQL roles are cluster scoped, so Alembic does not create this role.
The statements are intentionally unexecuted by the application. Acceptance
uses a uniquely named task role in a disposable local database and removes it.
"""

from __future__ import annotations

import re


_ROLE_IDENTIFIER = re.compile(
    r"^emr4_application_auth_runtime_[a-z0-9_]{8,40}$"
)
_LOGIN_ROLE_IDENTIFIER = re.compile(
    r"^emr4_application_auth_login_[a-z0-9_]{8,40}$"
)

STATE_TABLES = (
    "application_auth_principal_generations",
    "application_auth_parent_sessions",
    "application_auth_surface_sessions",
    "application_auth_exchange_grants",
)
AUDIT_TABLE = "application_auth_audit_events"
AUDIT_SEQUENCE = "application_auth_audit_events_id_seq"
RESOLVER_SIGNATURE = (
    "public.emr4_resolve_application_auth_principal(text, text)"
)


def require_runtime_role_identifier(role_name: str) -> str:
    if not isinstance(role_name, str) or not _ROLE_IDENTIFIER.fullmatch(role_name):
        raise ValueError("runtime role name is outside the task-safe allowlist")
    return role_name


def require_login_role_identifier(role_name: str) -> str:
    if not isinstance(role_name, str) or not _LOGIN_ROLE_IDENTIFIER.fullmatch(role_name):
        raise ValueError("login role name is outside the task-safe allowlist")
    return role_name


def create_deployment_login_role_statements(
    login_role_name: str,
    capability_role_name: str,
    *,
    connection_limit: int = 4,
) -> tuple[str, ...]:
    """Return an inert credential-free login/capability separation contract."""

    login = require_login_role_identifier(login_role_name)
    capability = require_runtime_role_identifier(capability_role_name)
    if not 1 <= connection_limit <= 32:
        raise ValueError("login connection limit outside 1..32")
    quoted_login = f'"{login}"'
    quoted_capability = f'"{capability}"'
    return (
        f"CREATE ROLE {quoted_login} LOGIN PASSWORD NULL NOSUPERUSER "
        "NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS "
        f"CONNECTION LIMIT {connection_limit}",
        f"GRANT {quoted_capability} TO {quoted_login}",
    )


def create_runtime_role_statements(role_name: str) -> tuple[str, ...]:
    """Return the complete exact least-privilege role/grant contract."""

    role = require_runtime_role_identifier(role_name)
    quoted_role = f'"{role}"'
    state_tables = ", ".join(f'public."{table}"' for table in STATE_TABLES)
    all_tables = ", ".join(
        [state_tables, f'public."{AUDIT_TABLE}"']
    )
    return (
        f"CREATE ROLE {quoted_role} NOLOGIN NOSUPERUSER NOCREATEDB "
        "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS",
        f"ALTER ROLE {quoted_role} SET row_security = on",
        f"ALTER ROLE {quoted_role} SET statement_timeout = '5s'",
        f"ALTER ROLE {quoted_role} SET lock_timeout = '2s'",
        f"ALTER ROLE {quoted_role} SET idle_in_transaction_session_timeout = '5s'",
        f"REVOKE ALL ON TABLE {all_tables} FROM PUBLIC",
        f"REVOKE ALL ON SEQUENCE public.\"{AUDIT_SEQUENCE}\" FROM PUBLIC",
        f"REVOKE ALL ON FUNCTION {RESOLVER_SIGNATURE} FROM PUBLIC",
        f"GRANT USAGE ON SCHEMA public TO {quoted_role}",
        f"GRANT SELECT, INSERT, UPDATE ON TABLE {state_tables} TO {quoted_role}",
        f"GRANT SELECT, INSERT ON TABLE public.\"{AUDIT_TABLE}\" TO {quoted_role}",
        f"GRANT USAGE, SELECT ON SEQUENCE public.\"{AUDIT_SEQUENCE}\" TO {quoted_role}",
        f"GRANT EXECUTE ON FUNCTION {RESOLVER_SIGNATURE} TO {quoted_role}",
    )


def drop_runtime_role_statement(role_name: str) -> str:
    role = require_runtime_role_identifier(role_name)
    return f'DROP ROLE "{role}"'


def drop_login_role_statement(role_name: str) -> str:
    role = require_login_role_identifier(role_name)
    return f'DROP ROLE "{role}"'


__all__ = [
    "AUDIT_SEQUENCE",
    "AUDIT_TABLE",
    "RESOLVER_SIGNATURE",
    "STATE_TABLES",
    "create_runtime_role_statements",
    "create_deployment_login_role_statements",
    "drop_login_role_statement",
    "drop_runtime_role_statement",
    "require_login_role_identifier",
    "require_runtime_role_identifier",
]
