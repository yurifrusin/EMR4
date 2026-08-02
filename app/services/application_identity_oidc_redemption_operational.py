"""Dormant finite-pool boundary for atomic OIDC grant redemption."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.orm import Session, sessionmaker

from app.services.application_identity_oidc_redemption_database_role import (
    require_redemption_call_role,
    require_redemption_login_role,
)


_REJECTED_URL_QUERY_KEYS = frozenset(
    {"options", "role", "service", "servicefile", "passfile"}
)


@dataclass(frozen=True)
class OIDCAdmissionRedemptionPoolPolicy:
    pool_size: int = 2
    max_overflow: int = 0
    pool_timeout_seconds: float = 1.0
    pool_recycle_seconds: int = 300
    login_connection_limit: int = 2

    def __post_init__(self) -> None:
        if not 1 <= self.pool_size <= 8:
            raise ValueError("redemption pool size is outside 1..8")
        if not 0 <= self.max_overflow <= 4:
            raise ValueError("redemption pool overflow is outside 0..4")
        if not 0.05 <= self.pool_timeout_seconds <= 5.0:
            raise ValueError("redemption pool timeout is outside 0.05..5 seconds")
        if not 30 <= self.pool_recycle_seconds <= 3600:
            raise ValueError("redemption pool recycle is outside 30..3600 seconds")
        if not 1 <= self.login_connection_limit <= 16:
            raise ValueError("redemption login limit is outside 1..16")
        if self.pool_size + self.max_overflow > self.login_connection_limit:
            raise ValueError("redemption pool maximum exceeds login limit")


def create_oidc_admission_redemption_engine(
    database_url: str | URL,
    *,
    login_role: str,
    call_role: str,
    policy: OIDCAdmissionRedemptionPoolPolicy | None = None,
) -> Engine:
    login = require_redemption_login_role(login_role)
    caller = require_redemption_call_role(call_role)
    bounded = policy or OIDCAdmissionRedemptionPoolPolicy()
    target = make_url(database_url)
    if target.get_backend_name() != "postgresql":
        raise ValueError("redemption pool requires PostgreSQL")
    if target.username != login:
        raise ValueError("database URL user must be the exact redemption login")
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
    def _enter_and_verify_call_role(dbapi_connection, _record, _proxy) -> None:
        try:
            _rollback(dbapi_connection)
            with dbapi_connection.cursor() as cursor:
                cursor.execute("RESET ROLE")
                cursor.execute("RESET ALL")
                cursor.execute(f'SET ROLE "{caller}"')
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
            if observed != (login, caller, True, True, True, True):
                raise DisconnectionError("redemption checkout verification failed")
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
                raise DisconnectionError("redemption pool reset failed")
            dbapi_connection.commit()
        except Exception:
            _rollback(dbapi_connection)
            raise

    return engine


def create_oidc_admission_redemption_session_factory(
    engine: Engine,
) -> Callable[[], Session]:
    if not isinstance(engine, Engine):
        raise TypeError("redemption session factory requires an engine")
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
        raise DisconnectionError("redemption connection rollback failed") from None


__all__ = [
    "OIDCAdmissionRedemptionPoolPolicy",
    "create_oidc_admission_redemption_engine",
    "create_oidc_admission_redemption_session_factory",
]
