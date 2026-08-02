"""Exact PostgreSQL role contract for OIDC binding and admission grants.

The statements are inert until an operator provisions uniquely named roles.
Alembic intentionally does not create cluster-scoped roles or credentials.
"""

from __future__ import annotations

import re


BINDING_TABLE = "application_identity_federation_bindings"
AUDIT_TABLE = "application_identity_federation_audit_events"
AUDIT_SEQUENCE = "application_identity_federation_audit_events_id_seq"
GRANT_TABLE = "application_identity_federation_admission_grants"
RESOLVER_SIGNATURE = (
    "public.emr4_resolve_application_identity_federation_binding("
    "text, text, text, text, text, text, text, text, text)"
)
GRANT_AUDIT_TRIGGER_SIGNATURE = (
    "public.emr4_app_id_fed_grant_required_audit()"
)

_LOGIN_ROLE = re.compile(r"^emr4_oidc_binding_login_[a-z0-9_]{8,40}$")
_RESOLVER_CALL_ROLE = re.compile(
    r"^emr4_oidc_binding_resolver_call_[a-z0-9_]{8,40}$"
)
_RESOLVER_OWNER_ROLE = re.compile(
    r"^emr4_oidc_binding_resolver_owner_[a-z0-9_]{8,40}$"
)
_GRANT_ISSUER_ROLE = re.compile(
    r"^emr4_oidc_grant_issuer_[a-z0-9_]{8,40}$"
)


def require_binding_login_role(role_name: str) -> str:
    return _require_role(role_name, _LOGIN_ROLE, "binding login")


def require_binding_resolver_call_role(role_name: str) -> str:
    return _require_role(role_name, _RESOLVER_CALL_ROLE, "resolver-call")


def require_binding_resolver_owner_role(role_name: str) -> str:
    return _require_role(role_name, _RESOLVER_OWNER_ROLE, "resolver-owner")


def require_grant_issuer_role(role_name: str) -> str:
    return _require_role(role_name, _GRANT_ISSUER_ROLE, "grant-issuer")


def create_binding_admission_capability_statements(
    *,
    resolver_call_role: str,
    resolver_owner_role: str,
    grant_issuer_role: str,
) -> tuple[str, ...]:
    """Create and wire the three credential-free least-authority roles."""

    caller = require_binding_resolver_call_role(resolver_call_role)
    owner = require_binding_resolver_owner_role(resolver_owner_role)
    issuer = require_grant_issuer_role(grant_issuer_role)
    quoted_caller = f'"{caller}"'
    quoted_owner = f'"{owner}"'
    quoted_issuer = f'"{issuer}"'
    audit = f'public."{AUDIT_TABLE}"'
    binding = f'public."{BINDING_TABLE}"'
    grant = f'public."{GRANT_TABLE}"'
    audit_sequence = f'public."{AUDIT_SEQUENCE}"'
    hardening = (
        "SET row_security = on",
        "SET statement_timeout = '5s'",
        "SET lock_timeout = '2s'",
        "SET idle_in_transaction_session_timeout = '5s'",
    )
    statements: list[str] = []
    for quoted in (quoted_owner, quoted_caller, quoted_issuer):
        statements.append(
            f"CREATE ROLE {quoted} NOLOGIN NOSUPERUSER NOCREATEDB "
            "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS"
        )
        statements.extend(f"ALTER ROLE {quoted} {setting}" for setting in hardening)
    statements.extend(
        (
            f"REVOKE ALL ON TABLE {binding}, {audit}, {grant} FROM PUBLIC",
            f"REVOKE ALL ON SEQUENCE {audit_sequence} FROM PUBLIC",
            f"REVOKE ALL ON FUNCTION {RESOLVER_SIGNATURE} FROM PUBLIC",
            f"REVOKE ALL ON FUNCTION {GRANT_AUDIT_TRIGGER_SIGNATURE} FROM PUBLIC",
            f"ALTER FUNCTION {RESOLVER_SIGNATURE} OWNER TO {quoted_owner}",
            f"ALTER FUNCTION {GRANT_AUDIT_TRIGGER_SIGNATURE} OWNER TO {quoted_owner}",
            f"GRANT USAGE ON SCHEMA public TO {quoted_owner}",
            f"GRANT SELECT ON TABLE {binding} TO {quoted_owner}",
            f"GRANT INSERT ON TABLE {audit} TO {quoted_owner}",
            f"GRANT USAGE, SELECT ON SEQUENCE {audit_sequence} TO {quoted_owner}",
            f"GRANT USAGE ON SCHEMA public TO {quoted_caller}",
            f"GRANT EXECUTE ON FUNCTION {RESOLVER_SIGNATURE} TO {quoted_caller}",
            f"GRANT USAGE ON SCHEMA public TO {quoted_issuer}",
            f"GRANT SELECT, INSERT ON TABLE {grant} TO {quoted_issuer}",
        )
    )
    return tuple(statements)


def create_binding_admission_login_statements(
    login_role: str,
    *,
    resolver_call_role: str,
    grant_issuer_role: str,
    connection_limit: int,
) -> tuple[str, ...]:
    login = require_binding_login_role(login_role)
    caller = require_binding_resolver_call_role(resolver_call_role)
    issuer = require_grant_issuer_role(grant_issuer_role)
    if not 1 <= connection_limit <= 16:
        raise ValueError("binding login connection limit is outside 1..16")
    quoted_login = f'"{login}"'
    return (
        f"CREATE ROLE {quoted_login} LOGIN PASSWORD NULL NOSUPERUSER "
        "NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS "
        f"CONNECTION LIMIT {connection_limit}",
        f'GRANT "{caller}" TO {quoted_login}',
        f'GRANT "{issuer}" TO {quoted_login}',
    )


def drop_binding_admission_role_statement(role_name: str) -> str:
    validators = (
        _LOGIN_ROLE,
        _RESOLVER_CALL_ROLE,
        _RESOLVER_OWNER_ROLE,
        _GRANT_ISSUER_ROLE,
    )
    if not isinstance(role_name, str) or not any(
        pattern.fullmatch(role_name) for pattern in validators
    ):
        raise ValueError("binding admission role is outside the task-safe allowlist")
    return f'DROP ROLE "{role_name}"'


def _require_role(role_name: str, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(role_name, str) or not pattern.fullmatch(role_name):
        raise ValueError(f"{label} role is outside the task-safe allowlist")
    return role_name


__all__ = [
    "AUDIT_SEQUENCE",
    "AUDIT_TABLE",
    "BINDING_TABLE",
    "GRANT_TABLE",
    "GRANT_AUDIT_TRIGGER_SIGNATURE",
    "RESOLVER_SIGNATURE",
    "create_binding_admission_capability_statements",
    "create_binding_admission_login_statements",
    "drop_binding_admission_role_statement",
    "require_binding_login_role",
    "require_binding_resolver_call_role",
    "require_binding_resolver_owner_role",
    "require_grant_issuer_role",
]
