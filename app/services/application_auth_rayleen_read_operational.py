"""Finite hardened PostgreSQL pool for the exact Rayleen A4 read role."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.orm import Session, sessionmaker

from app.services.application_auth_rayleen_read_database_role import (
    require_rayleen_read_capability_role,
    require_rayleen_read_login_role,
)


_REJECTED_URL_QUERY_KEYS = frozenset(
    {"options", "role", "service", "servicefile", "passfile"}
)


@dataclass(frozen=True)
class RayleenReadPoolPolicy:
    pool_size: int = 2
    max_overflow: int = 0
    pool_timeout_seconds: float = 1.0
    pool_recycle_seconds: int = 300
    login_connection_limit: int = 2

    def __post_init__(self) -> None:
        if not 1 <= self.pool_size <= 2:
            raise ValueError("Rayleen read pool size is outside 1..2")
        if self.max_overflow != 0:
            raise ValueError("Rayleen read pool overflow must be zero")
        if not 0.05 <= self.pool_timeout_seconds <= 5.0:
            raise ValueError("Rayleen read pool timeout is outside 0.05..5")
        if not 30 <= self.pool_recycle_seconds <= 3600:
            raise ValueError("Rayleen read pool recycle is outside 30..3600")
        if not 1 <= self.login_connection_limit <= 4:
            raise ValueError("Rayleen read login limit is outside 1..4")
        if self.pool_size > self.login_connection_limit:
            raise ValueError("Rayleen read pool exceeds login limit")


def create_rayleen_read_engine(
    database_url: str | URL,
    *,
    login_role: str,
    capability_role: str,
    policy: RayleenReadPoolPolicy | None = None,
) -> Engine:
    login = require_rayleen_read_login_role(login_role)
    capability = require_rayleen_read_capability_role(capability_role)
    bounded = policy or RayleenReadPoolPolicy()
    target = make_url(database_url)
    if target.get_backend_name() != "postgresql":
        raise ValueError("Rayleen read pool requires PostgreSQL")
    if target.username != login:
        raise ValueError("database URL user must be the exact Rayleen login")
    if _REJECTED_URL_QUERY_KEYS.intersection(key.lower() for key in target.query):
        raise ValueError("database URL contains a prohibited session option")

    engine = create_engine(
        target,
        pool_size=bounded.pool_size,
        max_overflow=0,
        pool_timeout=bounded.pool_timeout_seconds,
        pool_recycle=bounded.pool_recycle_seconds,
        pool_pre_ping=True,
        pool_use_lifo=True,
        pool_reset_on_return=None,
    )

    @event.listens_for(engine, "checkout")
    def _enter_and_verify_capability(dbapi_connection, _record, _proxy) -> None:
        try:
            _rollback(dbapi_connection)
            with dbapi_connection.cursor() as cursor:
                cursor.execute("RESET ROLE")
                cursor.execute("RESET ALL")
                cursor.execute(f'SET ROLE "{capability}"')
                cursor.execute("SET row_security = on")
                cursor.execute("SET statement_timeout = '5s'")
                cursor.execute("SET lock_timeout = '2s'")
                cursor.execute("SET idle_in_transaction_session_timeout = '5s'")
                cursor.execute(
                    "SELECT session_user, current_user, "
                    "current_setting('row_security') = 'on'"
                )
                observed = cursor.fetchone()
            if observed != (login, capability, True):
                raise DisconnectionError("Rayleen read checkout verification failed")
            dbapi_connection.commit()
        except Exception:
            _rollback(dbapi_connection)
            raise

    @event.listens_for(engine, "reset")
    def _reset_login(dbapi_connection, _record, reset_state) -> None:
        if reset_state.terminate_only:
            return
        try:
            _rollback(dbapi_connection)
            with dbapi_connection.cursor() as cursor:
                cursor.execute("RESET ROLE")
                cursor.execute("RESET ALL")
                cursor.execute("SELECT session_user, current_user")
                observed = cursor.fetchone()
            if observed != (login, login):
                raise DisconnectionError("Rayleen read pool reset failed")
            dbapi_connection.commit()
        except Exception:
            _rollback(dbapi_connection)
            raise

    return engine


def create_rayleen_read_session_factory(engine: Engine) -> Callable[[], Session]:
    if not isinstance(engine, Engine):
        raise TypeError("Rayleen read session factory requires an engine")
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine,
    )


def _rollback(dbapi_connection) -> None:
    try:
        dbapi_connection.rollback()
    except Exception:
        raise DisconnectionError("Rayleen read rollback failed") from None


__all__ = [
    "RayleenReadPoolPolicy",
    "create_rayleen_read_engine",
    "create_rayleen_read_session_factory",
]
