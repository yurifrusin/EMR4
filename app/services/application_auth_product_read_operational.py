"""Finite hardened pool for the exact-column practitioner-directory read."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.orm import Session, sessionmaker

from app.services.application_auth_product_read_database_role import (
    require_product_read_capability_role,
    require_product_read_login_role,
)


_REJECTED_URL_QUERY_KEYS = frozenset(
    {"options", "role", "service", "servicefile", "passfile"}
)


@dataclass(frozen=True)
class ProductReadPoolPolicy:
    pool_size: int = 2
    max_overflow: int = 0
    pool_timeout_seconds: float = 1.0
    pool_recycle_seconds: int = 300
    login_connection_limit: int = 2

    def __post_init__(self) -> None:
        if not 1 <= self.pool_size <= 4:
            raise ValueError("product-read pool size is outside 1..4")
        if not 0 <= self.max_overflow <= 2:
            raise ValueError("product-read overflow is outside 0..2")
        if not 0.05 <= self.pool_timeout_seconds <= 5.0:
            raise ValueError("product-read pool timeout is outside 0.05..5")
        if not 30 <= self.pool_recycle_seconds <= 3600:
            raise ValueError("product-read recycle is outside 30..3600")
        if not 1 <= self.login_connection_limit <= 8:
            raise ValueError("product-read login limit is outside 1..8")
        if self.pool_size + self.max_overflow > self.login_connection_limit:
            raise ValueError("product-read pool maximum exceeds login limit")


def create_product_read_engine(
    database_url: str | URL,
    *,
    login_role: str,
    capability_role: str,
    policy: ProductReadPoolPolicy | None = None,
) -> Engine:
    login = require_product_read_login_role(login_role)
    capability = require_product_read_capability_role(capability_role)
    bounded = policy or ProductReadPoolPolicy()
    target = make_url(database_url)
    if target.get_backend_name() != "postgresql":
        raise ValueError("product-read pool requires PostgreSQL")
    if target.username != login:
        raise ValueError("database URL user must be the exact product-read login")
    if _REJECTED_URL_QUERY_KEYS.intersection(key.lower() for key in target.query):
        raise ValueError("database URL contains a prohibited session option")

    engine = create_engine(
        target,
        pool_size=bounded.pool_size,
        max_overflow=bounded.max_overflow,
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
                    "current_setting('row_security') = 'on', "
                    "current_setting('statement_timeout')::interval = "
                    "INTERVAL '5 seconds', "
                    "current_setting('lock_timeout')::interval = "
                    "INTERVAL '2 seconds', "
                    "current_setting('idle_in_transaction_session_timeout')::interval = "
                    "INTERVAL '5 seconds'"
                )
                observed = cursor.fetchone()
            if observed != (login, capability, True, True, True, True):
                raise DisconnectionError("product-read checkout verification failed")
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
                raise DisconnectionError("product-read pool reset failed")
            dbapi_connection.commit()
        except Exception:
            _rollback(dbapi_connection)
            raise

    return engine


def create_product_read_session_factory(
    engine: Engine,
) -> Callable[[], Session]:
    if not isinstance(engine, Engine):
        raise TypeError("product-read session factory requires an engine")
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
        raise DisconnectionError(
            "product-read connection rollback failed"
        ) from None


__all__ = [
    "ProductReadPoolPolicy",
    "create_product_read_engine",
    "create_product_read_session_factory",
]
