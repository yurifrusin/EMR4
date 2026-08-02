"""Exact NOLOGIN capability-role contract for the OIDC attempt store.

PostgreSQL roles are cluster scoped, so Alembic does not create this role and
the dormant application code never executes these statements. Disposable
acceptance creates one exact task role, enters it with ``SET ROLE``, and drops
it after the owned database is removed.
"""

from __future__ import annotations

import re


ATTEMPT_TABLE = "application_identity_oidc_authorization_attempts"
_ROLE_IDENTIFIER = re.compile(
    r"^emr4_oidc_attempt_runtime_[a-z0-9_]{8,40}$"
)
_LOGIN_ROLE_IDENTIFIER = re.compile(
    r"^emr4_oidc_attempt_login_[a-z0-9_]{8,40}$"
)


def require_oidc_attempt_runtime_role_identifier(role_name: str) -> str:
    if not isinstance(role_name, str) or not _ROLE_IDENTIFIER.fullmatch(role_name):
        raise ValueError("OIDC attempt runtime role is outside the task-safe allowlist")
    return role_name


def require_oidc_attempt_login_role_identifier(role_name: str) -> str:
    if not isinstance(role_name, str) or not _LOGIN_ROLE_IDENTIFIER.fullmatch(
        role_name
    ):
        raise ValueError("OIDC attempt login role is outside the task-safe allowlist")
    return role_name


def create_oidc_attempt_deployment_login_statements(
    login_role_name: str,
    capability_role_name: str,
    *,
    connection_limit: int,
) -> tuple[str, ...]:
    """Return the inert credential-free LOGIN/capability separation contract."""

    login = require_oidc_attempt_login_role_identifier(login_role_name)
    capability = require_oidc_attempt_runtime_role_identifier(capability_role_name)
    if not 1 <= connection_limit <= 16:
        raise ValueError("OIDC attempt login connection limit is outside 1..16")
    quoted_login = f'"{login}"'
    quoted_capability = f'"{capability}"'
    return (
        f"CREATE ROLE {quoted_login} LOGIN PASSWORD NULL NOSUPERUSER "
        "NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS "
        f"CONNECTION LIMIT {connection_limit}",
        f"GRANT {quoted_capability} TO {quoted_login}",
    )


def create_oidc_attempt_runtime_role_statements(role_name: str) -> tuple[str, ...]:
    """Return the credential-free least-privilege role/grant contract."""

    role = require_oidc_attempt_runtime_role_identifier(role_name)
    quoted_role = f'"{role}"'
    quoted_table = f'public."{ATTEMPT_TABLE}"'
    return (
        f"CREATE ROLE {quoted_role} NOLOGIN NOSUPERUSER NOCREATEDB "
        "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS",
        f"ALTER ROLE {quoted_role} SET row_security = on",
        f"ALTER ROLE {quoted_role} SET statement_timeout = '5s'",
        f"ALTER ROLE {quoted_role} SET lock_timeout = '2s'",
        f"ALTER ROLE {quoted_role} SET idle_in_transaction_session_timeout = '5s'",
        f"REVOKE ALL ON TABLE {quoted_table} FROM PUBLIC",
        f"GRANT USAGE ON SCHEMA public TO {quoted_role}",
        f"GRANT SELECT, INSERT, DELETE ON TABLE {quoted_table} TO {quoted_role}",
    )


def drop_oidc_attempt_runtime_role_statement(role_name: str) -> str:
    role = require_oidc_attempt_runtime_role_identifier(role_name)
    return f'DROP ROLE "{role}"'


def drop_oidc_attempt_login_role_statement(role_name: str) -> str:
    role = require_oidc_attempt_login_role_identifier(role_name)
    return f'DROP ROLE "{role}"'


__all__ = [
    "ATTEMPT_TABLE",
    "create_oidc_attempt_deployment_login_statements",
    "create_oidc_attempt_runtime_role_statements",
    "drop_oidc_attempt_login_role_statement",
    "drop_oidc_attempt_runtime_role_statement",
    "require_oidc_attempt_login_role_identifier",
    "require_oidc_attempt_runtime_role_identifier",
]
