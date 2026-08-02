"""Dormant operational boundary for the PostgreSQL OIDC attempt store.

This module defines a finite deployment-LOGIN pool and a credential-free key
provider seam. It is intentionally not imported by an application router.
"""

from __future__ import annotations

import hmac
import re
from dataclasses import dataclass
from typing import Callable, Protocol

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.orm import Session, sessionmaker

from app.services.application_identity_oidc_adapter import MAX_ATTEMPTS
from app.services.application_identity_oidc_attempt_database_role import (
    require_oidc_attempt_login_role_identifier,
    require_oidc_attempt_runtime_role_identifier,
)
from app.services.application_identity_oidc_attempt_store import (
    AuthorizationAttemptDigestKeyring,
    FernetAuthorizationAttemptCipher,
    PostgresAuthorizationAttemptStore,
)


_KEY_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
_PROVIDER_NAMESPACE = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")
_SECRET_REFERENCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/@:-]{2,255}$")
_REJECTED_URL_QUERY_KEYS = frozenset(
    {"options", "role", "service", "servicefile", "passfile"}
)
_MAX_KEYS = 4


@dataclass(frozen=True)
class OIDCAttemptPoolPolicy:
    pool_size: int = 2
    max_overflow: int = 0
    pool_timeout_seconds: float = 1.0
    pool_recycle_seconds: int = 300
    login_connection_limit: int = 2

    def __post_init__(self) -> None:
        if not 1 <= self.pool_size <= 8:
            raise ValueError("OIDC attempt pool size is outside 1..8")
        if not 0 <= self.max_overflow <= 4:
            raise ValueError("OIDC attempt pool overflow is outside 0..4")
        if not 0.05 <= self.pool_timeout_seconds <= 5.0:
            raise ValueError("OIDC attempt pool timeout is outside 0.05..5 seconds")
        if not 30 <= self.pool_recycle_seconds <= 3600:
            raise ValueError("OIDC attempt pool recycle is outside 30..3600 seconds")
        if not 1 <= self.login_connection_limit <= 16:
            raise ValueError("OIDC attempt LOGIN connection limit is outside 1..16")
        if self.pool_size + self.max_overflow > self.login_connection_limit:
            raise ValueError("OIDC attempt pool maximum exceeds LOGIN connection limit")


@dataclass(frozen=True)
class AuthorizationAttemptSecretReference:
    provider_namespace: str
    reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.provider_namespace, str) or not _PROVIDER_NAMESPACE.fullmatch(
            self.provider_namespace
        ):
            raise ValueError("authorization-attempt secret provider is invalid")
        if (
            not isinstance(self.reference, str)
            or not _SECRET_REFERENCE.fullmatch(self.reference)
            or "://" in self.reference
            or "=" in self.reference
        ):
            raise ValueError("authorization-attempt secret reference is invalid")


@dataclass(frozen=True)
class AuthorizationAttemptKeyReference:
    key_id: str
    secret: AuthorizationAttemptSecretReference

    def __post_init__(self) -> None:
        if not isinstance(self.key_id, str) or not _KEY_ID.fullmatch(self.key_id):
            raise ValueError("authorization-attempt key identifier is invalid")
        if not isinstance(self.secret, AuthorizationAttemptSecretReference):
            raise TypeError("authorization-attempt key requires a secret reference")


@dataclass(frozen=True)
class AuthorizationAttemptRuntimeKeyConfiguration:
    provider_namespace: str
    active_cipher_key_id: str
    cipher_keys: tuple[AuthorizationAttemptKeyReference, ...]
    active_digest_key_id: str
    digest_keys: tuple[AuthorizationAttemptKeyReference, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.provider_namespace, str) or not _PROVIDER_NAMESPACE.fullmatch(
            self.provider_namespace
        ):
            raise ValueError("authorization-attempt key provider is invalid")
        cipher = _validated_key_references(
            active_key_id=self.active_cipher_key_id,
            references=self.cipher_keys,
            provider_namespace=self.provider_namespace,
        )
        digest = _validated_key_references(
            active_key_id=self.active_digest_key_id,
            references=self.digest_keys,
            provider_namespace=self.provider_namespace,
        )
        all_references = [item.secret.reference for item in (*cipher, *digest)]
        if len(set(all_references)) != len(all_references):
            raise ValueError("authorization-attempt secret references must be unique")


class AuthorizationAttemptSecretProvider(Protocol):
    @property
    def provider_namespace(self) -> str:
        raise NotImplementedError

    def resolve_bytes(self, reference: AuthorizationAttemptSecretReference) -> bytes:
        raise NotImplementedError


@dataclass(frozen=True)
class ResolvedAuthorizationAttemptCryptography:
    cipher: FernetAuthorizationAttemptCipher
    digest_keyring: AuthorizationAttemptDigestKeyring


@dataclass(frozen=True)
class OIDCAttemptOperationalConfiguration:
    login_role: str
    capability_role: str
    pool: OIDCAttemptPoolPolicy
    keys: AuthorizationAttemptRuntimeKeyConfiguration
    max_attempts: int = MAX_ATTEMPTS

    def __post_init__(self) -> None:
        require_oidc_attempt_login_role_identifier(self.login_role)
        require_oidc_attempt_runtime_role_identifier(self.capability_role)
        if not isinstance(self.pool, OIDCAttemptPoolPolicy):
            raise TypeError("OIDC attempt operational config requires a pool policy")
        if not isinstance(self.keys, AuthorizationAttemptRuntimeKeyConfiguration):
            raise TypeError("OIDC attempt operational config requires key references")
        if not 1 <= self.max_attempts <= MAX_ATTEMPTS:
            raise ValueError("OIDC attempt runtime capacity exceeds frozen bound")


@dataclass(frozen=True)
class PostgresAuthorizationAttemptRuntime:
    engine: Engine
    session_factory: Callable[[], Session]
    store: PostgresAuthorizationAttemptStore

    def dispose(self) -> None:
        self.engine.dispose()


def create_oidc_attempt_operational_engine(
    database_url: str | URL,
    *,
    login_role: str,
    capability_role: str,
    policy: OIDCAttemptPoolPolicy | None = None,
) -> Engine:
    """Create a finite pool with verified role entry and return-time cleanup."""

    login = require_oidc_attempt_login_role_identifier(login_role)
    capability = require_oidc_attempt_runtime_role_identifier(capability_role)
    bounded = policy or OIDCAttemptPoolPolicy()
    target = make_url(database_url)
    if target.get_backend_name() != "postgresql":
        raise ValueError("OIDC attempt operational pool requires PostgreSQL")
    if target.username != login:
        raise ValueError("database URL user must be the exact OIDC attempt LOGIN")
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
    def _enter_capability_role(dbapi_connection, _record, _proxy) -> None:
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
                raise DisconnectionError("OIDC attempt pool checkout verification failed")
            dbapi_connection.commit()
        except Exception:
            _rollback(dbapi_connection)
            raise

    @event.listens_for(engine, "reset")
    def _reset_to_login(dbapi_connection, _record, reset_state) -> None:
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
                raise DisconnectionError("OIDC attempt pool reset verification failed")
            dbapi_connection.commit()
        except Exception:
            _rollback(dbapi_connection)
            raise

    return engine


def create_oidc_attempt_session_factory(engine: Engine) -> Callable[[], Session]:
    if not isinstance(engine, Engine):
        raise TypeError("OIDC attempt session factory requires an engine")
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine,
    )


def resolve_authorization_attempt_cryptography(
    configuration: AuthorizationAttemptRuntimeKeyConfiguration,
    provider: AuthorizationAttemptSecretProvider,
) -> ResolvedAuthorizationAttemptCryptography:
    if not isinstance(configuration, AuthorizationAttemptRuntimeKeyConfiguration):
        raise TypeError("authorization-attempt key configuration is required")
    try:
        namespace = provider.provider_namespace
    except Exception:
        raise ValueError("authorization-attempt secret provider is unavailable") from None
    if namespace != configuration.provider_namespace:
        raise ValueError("authorization-attempt secret provider mismatch")

    cipher_material = _resolve_keyset(provider, configuration.cipher_keys)
    digest_material = _resolve_keyset(provider, configuration.digest_keys)
    if any(
        len(left) == len(right) and hmac.compare_digest(left, right)
        for left in cipher_material.values()
        for right in digest_material.values()
    ):
        raise ValueError("authorization-attempt cipher and digest keys must be separate")
    try:
        cipher = FernetAuthorizationAttemptCipher(
            active_key_id=configuration.active_cipher_key_id,
            keys=cipher_material,
        )
        digest_keyring = AuthorizationAttemptDigestKeyring(
            active_key_id=configuration.active_digest_key_id,
            keys=digest_material,
        )
    except (TypeError, ValueError):
        raise ValueError("authorization-attempt resolved key material is invalid") from None
    return ResolvedAuthorizationAttemptCryptography(
        cipher=cipher,
        digest_keyring=digest_keyring,
    )


def build_postgres_authorization_attempt_runtime(
    database_url: str | URL,
    *,
    configuration: OIDCAttemptOperationalConfiguration,
    secret_provider: AuthorizationAttemptSecretProvider,
) -> PostgresAuthorizationAttemptRuntime:
    if not isinstance(configuration, OIDCAttemptOperationalConfiguration):
        raise TypeError("OIDC attempt operational configuration is required")
    cryptography = resolve_authorization_attempt_cryptography(
        configuration.keys,
        secret_provider,
    )
    engine = create_oidc_attempt_operational_engine(
        database_url,
        login_role=configuration.login_role,
        capability_role=configuration.capability_role,
        policy=configuration.pool,
    )
    session_factory = create_oidc_attempt_session_factory(engine)
    store = PostgresAuthorizationAttemptStore(
        session_factory=session_factory,
        cipher=cryptography.cipher,
        digest_keyring=cryptography.digest_keyring,
        max_attempts=configuration.max_attempts,
    )
    return PostgresAuthorizationAttemptRuntime(
        engine=engine,
        session_factory=session_factory,
        store=store,
    )


def _validated_key_references(
    *,
    active_key_id: str,
    references: tuple[AuthorizationAttemptKeyReference, ...],
    provider_namespace: str,
) -> tuple[AuthorizationAttemptKeyReference, ...]:
    if not isinstance(references, tuple) or not 1 <= len(references) <= _MAX_KEYS:
        raise ValueError("authorization-attempt keyset requires one to four references")
    if any(not isinstance(item, AuthorizationAttemptKeyReference) for item in references):
        raise TypeError("authorization-attempt keyset contains an invalid reference")
    key_ids = [item.key_id for item in references]
    if len(set(key_ids)) != len(key_ids) or active_key_id not in key_ids:
        raise ValueError("authorization-attempt keyset identifiers are invalid")
    if any(item.secret.provider_namespace != provider_namespace for item in references):
        raise ValueError("authorization-attempt keyset provider is inconsistent")
    return references


def _resolve_keyset(
    provider: AuthorizationAttemptSecretProvider,
    references: tuple[AuthorizationAttemptKeyReference, ...],
) -> dict[str, bytes]:
    resolved: dict[str, bytes] = {}
    for item in references:
        try:
            material = provider.resolve_bytes(item.secret)
        except Exception:
            raise ValueError("authorization-attempt secret resolution failed") from None
        if not isinstance(material, bytes) or not 32 <= len(material) <= 128:
            raise ValueError("authorization-attempt resolved key material is invalid")
        if any(
            len(existing) == len(material)
            and hmac.compare_digest(existing, material)
            for existing in resolved.values()
        ):
            raise ValueError("authorization-attempt resolved key material is duplicated")
        resolved[item.key_id] = bytes(material)
    return resolved


def _rollback(dbapi_connection) -> None:
    try:
        dbapi_connection.rollback()
    except Exception:
        raise DisconnectionError("OIDC attempt connection rollback failed") from None


__all__ = [
    "AuthorizationAttemptKeyReference",
    "AuthorizationAttemptRuntimeKeyConfiguration",
    "AuthorizationAttemptSecretProvider",
    "AuthorizationAttemptSecretReference",
    "OIDCAttemptOperationalConfiguration",
    "OIDCAttemptPoolPolicy",
    "PostgresAuthorizationAttemptRuntime",
    "ResolvedAuthorizationAttemptCryptography",
    "build_postgres_authorization_attempt_runtime",
    "create_oidc_attempt_operational_engine",
    "create_oidc_attempt_session_factory",
    "resolve_authorization_attempt_cryptography",
]
