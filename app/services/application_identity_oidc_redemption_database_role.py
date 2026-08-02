"""Exact least-authority role contract for OIDC grant redemption.

The statements are inert until a task operator provisions unique roles. The
migration creates no cluster-scoped role or credential.
"""

from __future__ import annotations

import re


REDEMPTION_FUNCTION = (
    "public.emr4_redeem_application_identity_federation_grant("
    "text, text, text, text, text, text, timestamptz)"
)
FEDERATION_BINDING_TABLE = "application_identity_federation_bindings"
FEDERATION_GRANT_TABLE = "application_identity_federation_admission_grants"
FEDERATION_AUDIT_TABLE = "application_identity_federation_audit_events"
FEDERATION_AUDIT_SEQUENCE = "application_identity_federation_audit_events_id_seq"
PRINCIPAL_TRUTH_TABLE = "application_auth_synthetic_principal_truth"
APPLICATION_AUTH_STATE_TABLES = (
    "application_auth_principal_generations",
    "application_auth_parent_sessions",
    "application_auth_surface_sessions",
    "application_auth_exchange_grants",
)
APPLICATION_AUTH_AUDIT_TABLE = "application_auth_audit_events"
APPLICATION_AUTH_AUDIT_SEQUENCE = "application_auth_audit_events_id_seq"

_LOGIN_ROLE = re.compile(r"^emr4_oidc_redemption_login_[a-z0-9_]{8,40}$")
_CALL_ROLE = re.compile(r"^emr4_oidc_redemption_call_[a-z0-9_]{8,40}$")
_OWNER_ROLE = re.compile(r"^emr4_oidc_redemption_owner_[a-z0-9_]{8,40}$")


def require_redemption_login_role(role_name: str) -> str:
    return _require_role(role_name, _LOGIN_ROLE, "redemption login")


def require_redemption_call_role(role_name: str) -> str:
    return _require_role(role_name, _CALL_ROLE, "redemption call")


def require_redemption_owner_role(role_name: str) -> str:
    return _require_role(role_name, _OWNER_ROLE, "redemption owner")


def create_redemption_capability_statements(
    *,
    call_role: str,
    owner_role: str,
) -> tuple[str, ...]:
    """Create the execution/session capability and ungranted function owner."""

    caller = require_redemption_call_role(call_role)
    owner = require_redemption_owner_role(owner_role)
    quoted_caller = f'"{caller}"'
    quoted_owner = f'"{owner}"'
    binding = f'public."{FEDERATION_BINDING_TABLE}"'
    grant = f'public."{FEDERATION_GRANT_TABLE}"'
    federation_audit = f'public."{FEDERATION_AUDIT_TABLE}"'
    truth = f'public."{PRINCIPAL_TRUTH_TABLE}"'
    auth_state = ", ".join(
        f'public."{table}"' for table in APPLICATION_AUTH_STATE_TABLES
    )
    auth_audit = f'public."{APPLICATION_AUTH_AUDIT_TABLE}"'
    hardening = (
        "SET row_security = on",
        "SET statement_timeout = '5s'",
        "SET lock_timeout = '2s'",
        "SET idle_in_transaction_session_timeout = '5s'",
    )
    statements: list[str] = []
    for quoted in (quoted_owner, quoted_caller):
        statements.append(
            f"CREATE ROLE {quoted} NOLOGIN NOSUPERUSER NOCREATEDB "
            "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS"
        )
        statements.extend(f"ALTER ROLE {quoted} {setting}" for setting in hardening)
    statements.extend(
        (
            f"REVOKE ALL ON TABLE {binding}, {grant}, {federation_audit}, "
            f"{truth}, {auth_state}, {auth_audit} FROM PUBLIC",
            f"REVOKE ALL ON SEQUENCE public.\"{FEDERATION_AUDIT_SEQUENCE}\", "
            f"public.\"{APPLICATION_AUTH_AUDIT_SEQUENCE}\" FROM PUBLIC",
            f"REVOKE ALL ON FUNCTION {REDEMPTION_FUNCTION} FROM PUBLIC",
            f"ALTER FUNCTION {REDEMPTION_FUNCTION} OWNER TO {quoted_owner}",
            f"GRANT USAGE ON SCHEMA public TO {quoted_owner}",
            f"GRANT SELECT ON TABLE {binding}, {grant}, {truth} TO {quoted_owner}",
            f"GRANT UPDATE (updated_at) ON TABLE {binding}, {truth} "
            f"TO {quoted_owner}",
            f"GRANT UPDATE (status, version, consumed_at) ON TABLE {grant} "
            f"TO {quoted_owner}",
            f"GRANT INSERT ON TABLE {federation_audit} TO {quoted_owner}",
            f"GRANT USAGE, SELECT ON SEQUENCE "
            f"public.\"{FEDERATION_AUDIT_SEQUENCE}\" TO {quoted_owner}",
            f"GRANT USAGE ON SCHEMA public TO {quoted_caller}",
            f"GRANT EXECUTE ON FUNCTION {REDEMPTION_FUNCTION} TO {quoted_caller}",
            f"GRANT SELECT, INSERT, UPDATE ON TABLE {auth_state} TO {quoted_caller}",
            f"GRANT SELECT, INSERT ON TABLE {auth_audit} TO {quoted_caller}",
            f"GRANT USAGE, SELECT ON SEQUENCE "
            f"public.\"{APPLICATION_AUTH_AUDIT_SEQUENCE}\" TO {quoted_caller}",
        )
    )
    return tuple(statements)


def create_redemption_login_statements(
    login_role: str,
    *,
    call_role: str,
    connection_limit: int,
) -> tuple[str, ...]:
    login = require_redemption_login_role(login_role)
    caller = require_redemption_call_role(call_role)
    if not 1 <= connection_limit <= 16:
        raise ValueError("redemption login connection limit is outside 1..16")
    quoted_login = f'"{login}"'
    return (
        f"CREATE ROLE {quoted_login} LOGIN PASSWORD NULL NOSUPERUSER "
        "NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS "
        f"CONNECTION LIMIT {connection_limit}",
        f'GRANT "{caller}" TO {quoted_login}',
    )


def drop_redemption_role_statement(role_name: str) -> str:
    if not isinstance(role_name, str) or not any(
        pattern.fullmatch(role_name)
        for pattern in (_LOGIN_ROLE, _CALL_ROLE, _OWNER_ROLE)
    ):
        raise ValueError("redemption role is outside the task-safe allowlist")
    return f'DROP ROLE "{role_name}"'


def _require_role(role_name: str, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(role_name, str) or not pattern.fullmatch(role_name):
        raise ValueError(f"{label} role is outside the task-safe allowlist")
    return role_name


__all__ = [
    "APPLICATION_AUTH_AUDIT_SEQUENCE",
    "APPLICATION_AUTH_AUDIT_TABLE",
    "APPLICATION_AUTH_STATE_TABLES",
    "FEDERATION_AUDIT_SEQUENCE",
    "FEDERATION_AUDIT_TABLE",
    "FEDERATION_BINDING_TABLE",
    "FEDERATION_GRANT_TABLE",
    "PRINCIPAL_TRUTH_TABLE",
    "REDEMPTION_FUNCTION",
    "create_redemption_capability_statements",
    "create_redemption_login_statements",
    "drop_redemption_role_statement",
    "require_redemption_call_role",
    "require_redemption_login_role",
    "require_redemption_owner_role",
]
