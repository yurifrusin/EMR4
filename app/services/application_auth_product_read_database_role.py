"""Exact PostgreSQL role contract for the bounded product read."""

from __future__ import annotations

import re


_LOGIN_ROLE = re.compile(r"^emr4_product_read_login_[a-z0-9_]{8,40}$")
_CAPABILITY_ROLE = re.compile(
    r"^emr4_product_read_runtime_[a-z0-9_]{8,40}$"
)


def require_product_read_login_role(role_name: str) -> str:
    return _require_role(role_name, _LOGIN_ROLE, "product-read login")


def require_product_read_capability_role(role_name: str) -> str:
    return _require_role(
        role_name,
        _CAPABILITY_ROLE,
        "product-read capability",
    )


def create_product_read_capability_statements(
    role_name: str,
) -> tuple[str, ...]:
    role = require_product_read_capability_role(role_name)
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
        f"GRANT SELECT (id, practice_id, first_name, last_name, specialty, "
        f"default_location_id, is_active) ON TABLE public.practitioners "
        f"TO {quoted}",
        f"GRANT SELECT (id, practice_id, name, is_active) "
        f"ON TABLE public.practice_locations TO {quoted}",
    )


def create_product_read_login_statements(
    login_role_name: str,
    capability_role_name: str,
    *,
    connection_limit: int = 2,
) -> tuple[str, ...]:
    login = require_product_read_login_role(login_role_name)
    capability = require_product_read_capability_role(capability_role_name)
    if not 1 <= connection_limit <= 8:
        raise ValueError("product-read connection limit is outside 1..8")
    return (
        f'CREATE ROLE "{login}" LOGIN PASSWORD NULL NOSUPERUSER '
        "NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS "
        f"CONNECTION LIMIT {connection_limit}",
        f'GRANT "{capability}" TO "{login}"',
    )


def drop_product_read_role_statement(role_name: str) -> str:
    if not isinstance(role_name, str) or not (
        _LOGIN_ROLE.fullmatch(role_name)
        or _CAPABILITY_ROLE.fullmatch(role_name)
    ):
        raise ValueError("product-read role is outside the task-safe allowlist")
    return f'DROP ROLE "{role_name}"'


def _require_role(
    role_name: str,
    pattern: re.Pattern[str],
    label: str,
) -> str:
    if not isinstance(role_name, str) or not pattern.fullmatch(role_name):
        raise ValueError(f"{label} role is outside the task-safe allowlist")
    return role_name


__all__ = [
    "create_product_read_capability_statements",
    "create_product_read_login_statements",
    "drop_product_read_role_statement",
    "require_product_read_capability_role",
    "require_product_read_login_role",
]
