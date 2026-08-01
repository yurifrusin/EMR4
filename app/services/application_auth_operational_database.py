"""Credential-free bounded pool factory for the synthetic auth runtime."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.services.application_auth_database_role import (
    require_login_role_identifier,
    require_runtime_role_identifier,
)


@dataclass(frozen=True)
class ApplicationAuthPoolPolicy:
    pool_size: int = 2
    max_overflow: int = 1
    pool_timeout_seconds: float = 1.0
    pool_recycle_seconds: int = 300
    login_connection_limit: int = 4

    def __post_init__(self) -> None:
        if not 1 <= self.pool_size <= 16:
            raise ValueError("auth pool_size outside 1..16")
        if not 0 <= self.max_overflow <= 8:
            raise ValueError("auth max_overflow outside 0..8")
        if not 0.05 <= self.pool_timeout_seconds <= 10.0:
            raise ValueError("auth pool timeout outside 0.05..10 seconds")
        if not 30 <= self.pool_recycle_seconds <= 3600:
            raise ValueError("auth pool recycle outside 30..3600 seconds")
        if not 1 <= self.login_connection_limit <= 32:
            raise ValueError("login connection limit outside 1..32")
        if self.pool_size + self.max_overflow > self.login_connection_limit:
            raise ValueError("auth pool maximum exceeds login connection limit")


def create_application_auth_engine(
    database_url: str,
    *,
    login_role: str,
    capability_role: str,
    policy: ApplicationAuthPoolPolicy | None = None,
) -> Engine:
    """Build a finite QueuePool and enter the exact NOLOGIN capability role."""

    login = require_login_role_identifier(login_role)
    role = require_runtime_role_identifier(capability_role)
    bounded = policy or ApplicationAuthPoolPolicy()
    target = make_url(database_url)
    if target.get_backend_name() != "postgresql":
        raise ValueError("application-auth operational pool requires PostgreSQL")
    if target.username != login:
        raise ValueError("database URL user must be the exact deployment login role")
    engine = create_engine(
        target,
        pool_size=bounded.pool_size,
        max_overflow=bounded.max_overflow,
        pool_timeout=bounded.pool_timeout_seconds,
        pool_recycle=bounded.pool_recycle_seconds,
        pool_pre_ping=True,
        pool_use_lifo=True,
        pool_reset_on_return="rollback",
    )

    @event.listens_for(engine, "checkout")
    def _enter_capability_role(dbapi_connection, _record, _proxy) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute(f'SET ROLE "{role}"')
        finally:
            cursor.close()

    return engine


def create_application_auth_session_factory(engine: Engine):
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine,
    )


__all__ = [
    "ApplicationAuthPoolPolicy",
    "create_application_auth_engine",
    "create_application_auth_session_factory",
]
