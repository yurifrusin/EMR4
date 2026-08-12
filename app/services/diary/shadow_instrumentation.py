"""Globally-disabled typed scaffold for raw-route shadow instrumentation.

The application generation in this module cannot be enabled. The types make
the accepted boundary testable without creating an observer or diagnostic sink.
"""

from __future__ import annotations

from collections.abc import Callable
from contextvars import ContextVar, Token
from dataclasses import dataclass
import hashlib
import re
from typing import Protocol


RAW_COMPAT_CREATE_SHADOW_ADAPTER_ID = "raw_compat_create"
RAW_COMPAT_UPDATE_SHADOW_ADAPTER_ID = "raw_compat_update"
RAW_COMPAT_STATUS_SHADOW_ADAPTER_ID = "raw_compat_status"
RAW_COMPAT_DELETE_SHADOW_ADAPTER_ID = "raw_compat_delete"

SHADOW_ROUTE_ADAPTER_IDS = frozenset(
    {
        RAW_COMPAT_CREATE_SHADOW_ADAPTER_ID,
        RAW_COMPAT_UPDATE_SHADOW_ADAPTER_ID,
        RAW_COMPAT_STATUS_SHADOW_ADAPTER_ID,
        RAW_COMPAT_DELETE_SHADOW_ADAPTER_ID,
    }
)
_STRUCTURAL_TOKEN = re.compile(r"^[A-Za-z0-9_.:@/+\-]{1,160}$")
_DISABLED_GENERATION_CANONICAL = (
    "emr4.shadow-instrumentation-generation.v1|current|disabled|"
    "practice=[]|route=[]|digest-key-reference=null"
)
DEFAULT_DISABLED_GENERATION_DIGEST = hashlib.sha256(
    _DISABLED_GENERATION_CANONICAL.encode("ascii")
).hexdigest()


class ShadowInstrumentationClosed(RuntimeError):
    """Raised by a deliberately closed scaffold capability."""


@dataclass(frozen=True, slots=True)
class ShadowInstrumentationGeneration:
    """An immutable process-start generation that is closed in this tranche."""

    schema_version: str = "emr4.shadow-instrumentation-generation.v1"
    generation_digest: str = DEFAULT_DISABLED_GENERATION_DIGEST
    status: str = "current"
    global_enabled: bool = False
    practice_scope_digests: tuple[str, ...] = ()
    route_adapter_ids: tuple[str, ...] = ()
    digest_key_reference: str | None = None

    def __post_init__(self) -> None:
        if self.schema_version != "emr4.shadow-instrumentation-generation.v1":
            raise ValueError("unsupported shadow generation schema")
        if self.status != "current":
            raise ValueError("shadow generation must be current")
        if self.global_enabled:
            raise ValueError("enabled shadow generation is not admitted")
        if self.practice_scope_digests:
            raise ValueError("practice shadow allowlist must remain empty")
        if self.route_adapter_ids:
            raise ValueError("route shadow allowlist must remain empty")
        if self.digest_key_reference is not None:
            raise ValueError("digest key reference is not admitted")


DEFAULT_DISABLED_SHADOW_GENERATION = ShadowInstrumentationGeneration()


class ShadowGenerationReader(Protocol):
    def current(self) -> ShadowInstrumentationGeneration: ...


@dataclass(frozen=True, slots=True)
class StaticShadowGenerationReader:
    generation: ShadowInstrumentationGeneration = DEFAULT_DISABLED_SHADOW_GENERATION

    def current(self) -> ShadowInstrumentationGeneration:
        return self.generation


class ExternalShadowDisableLatch:
    """A monotonic, disable-only latch for the process generation."""

    __slots__ = ("_disabled",)

    def __init__(self) -> None:
        self._disabled = False

    @property
    def disabled(self) -> bool:
        return self._disabled

    def disable(self) -> None:
        self._disabled = True


@dataclass(frozen=True, slots=True)
class ServerOwnedShadowRequestContext:
    """Future context seam; no application provider exists in this tranche."""

    practice_id: str
    actor_id: str
    actor_role: str
    authenticated_session_reference: str
    server_correlation_reference: str


class ServerOwnedShadowContextProvider(Protocol):
    def __call__(self) -> ServerOwnedShadowRequestContext | None: ...


class ShadowDigestPort(Protocol):
    """Future digest seam; no concrete key-bearing implementation exists."""

    def digest(self, *, domain: str, tokens: tuple[str, ...]) -> str: ...


@dataclass(frozen=True, slots=True)
class ShadowProjectionMaterial:
    """Closed structural material; no free-text or response field is exposed."""

    route_adapter_id: str
    canonical_operation_id: str
    purpose: str
    target_shape: str
    target_tokens: tuple[str, ...]
    conflict_domain_tokens: tuple[str, ...]
    command_tokens: tuple[str, ...]
    precondition_version: int | None
    precondition_tokens: tuple[str, ...]
    confirmation_mode: str | None
    confirmation_reference_tokens: tuple[str, ...]
    idempotency_key_tokens: tuple[str, ...]
    canonicalization_version: str
    request_shape_tokens: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ShadowRouteProjection:
    schema_version: str
    architecture_generation_digest: str
    route_adapter_id: str
    canonical_operation_id: str
    practice_scope_digest: str
    actor_digest: str
    actor_role: str
    session_digest: str
    purpose: str
    target_shape: str
    target_digest: str
    conflict_domain_digest: str
    command_digest: str
    precondition_present: bool
    precondition_version: int | None
    precondition_digest: str | None
    confirmation_present: bool
    confirmation_mode: str | None
    confirmation_reference_digest: str | None
    idempotency_present: bool
    idempotency_key_digest: str | None
    canonicalization_version: str
    correlation_digest: str
    request_shape_digest: str


def _validate_tokens(label: str, tokens: tuple[str, ...], *, allow_empty: bool = False) -> None:
    if not tokens and not allow_empty:
        raise ValueError(f"{label} requires at least one structural token")
    if any(_STRUCTURAL_TOKEN.fullmatch(token) is None for token in tokens):
        raise ValueError(f"{label} contains a non-structural token")


def build_shadow_route_projection(
    *,
    generation: ShadowInstrumentationGeneration,
    context: ServerOwnedShadowRequestContext,
    material: ShadowProjectionMaterial,
    digest_port: ShadowDigestPort,
) -> ShadowRouteProjection:
    """Build the exact minimized projection from authored structural material."""

    if material.route_adapter_id not in SHADOW_ROUTE_ADAPTER_IDS:
        raise ValueError("unknown raw compatibility route adapter")
    for label, value in (
        ("practice_id", context.practice_id),
        ("actor_id", context.actor_id),
        ("actor_role", context.actor_role),
        ("session_reference", context.authenticated_session_reference),
        ("correlation_reference", context.server_correlation_reference),
        ("canonical_operation_id", material.canonical_operation_id),
        ("purpose", material.purpose),
        ("target_shape", material.target_shape),
        ("canonicalization_version", material.canonicalization_version),
    ):
        _validate_tokens(label, (value,))
    for label, tokens in (
        ("target", material.target_tokens),
        ("conflict_domain", material.conflict_domain_tokens),
        ("command", material.command_tokens),
        ("request_shape", material.request_shape_tokens),
    ):
        _validate_tokens(label, tokens)
    for label, tokens in (
        ("precondition", material.precondition_tokens),
        ("confirmation", material.confirmation_reference_tokens),
        ("idempotency", material.idempotency_key_tokens),
    ):
        _validate_tokens(label, tokens, allow_empty=True)
    if (material.precondition_version is None) != (not material.precondition_tokens):
        raise ValueError("precondition version and tokens must be jointly present")
    if (material.confirmation_mode is None) != (
        not material.confirmation_reference_tokens
    ):
        raise ValueError("confirmation mode and reference must be jointly present")
    if material.confirmation_mode is not None:
        _validate_tokens("confirmation_mode", (material.confirmation_mode,))

    def digest(domain: str, *tokens: str) -> str:
        return digest_port.digest(domain=domain, tokens=tuple(tokens))

    precondition_present = bool(material.precondition_tokens)
    confirmation_present = bool(material.confirmation_reference_tokens)
    idempotency_present = bool(material.idempotency_key_tokens)
    return ShadowRouteProjection(
        schema_version="emr4.shadow-route-projection.v1",
        architecture_generation_digest=generation.generation_digest,
        route_adapter_id=material.route_adapter_id,
        canonical_operation_id=material.canonical_operation_id,
        practice_scope_digest=digest("practice", context.practice_id),
        actor_digest=digest("actor", context.actor_id),
        actor_role=context.actor_role,
        session_digest=digest("session", context.authenticated_session_reference),
        purpose=material.purpose,
        target_shape=material.target_shape,
        target_digest=digest("target", *material.target_tokens),
        conflict_domain_digest=digest(
            "conflict_domain", *material.conflict_domain_tokens
        ),
        command_digest=digest("command", *material.command_tokens),
        precondition_present=precondition_present,
        precondition_version=material.precondition_version,
        precondition_digest=(
            digest("precondition", *material.precondition_tokens)
            if precondition_present
            else None
        ),
        confirmation_present=confirmation_present,
        confirmation_mode=material.confirmation_mode,
        confirmation_reference_digest=(
            digest("confirmation", *material.confirmation_reference_tokens)
            if confirmation_present
            else None
        ),
        idempotency_present=idempotency_present,
        idempotency_key_digest=(
            digest("idempotency", *material.idempotency_key_tokens)
            if idempotency_present
            else None
        ),
        canonicalization_version=material.canonicalization_version,
        correlation_digest=digest(
            "correlation", context.server_correlation_reference
        ),
        request_shape_digest=digest(
            "request_shape", *material.request_shape_tokens
        ),
    )


class ShadowRequestCell:
    """Single-assignment, take-and-clear same-request projection cell."""

    __slots__ = ("_assigned", "_projection")

    def __init__(self) -> None:
        self._assigned = False
        self._projection: ShadowRouteProjection | None = None

    @property
    def assigned(self) -> bool:
        return self._assigned

    def store(self, projection: ShadowRouteProjection) -> None:
        if self._assigned:
            raise ShadowInstrumentationClosed("shadow request cell already assigned")
        self._projection = projection
        self._assigned = True

    def take(self) -> ShadowRouteProjection | None:
        projection = self._projection
        self._projection = None
        return projection


class ShadowOfferPort(Protocol):
    def offer_nowait(self, projection: ShadowRouteProjection) -> None: ...


class ClosedShadowOfferPort:
    """The sole application offer implementation; it is not a sink."""

    def offer_nowait(self, projection: ShadowRouteProjection) -> None:
        del projection
        raise ShadowInstrumentationClosed("shadow offer port is closed")


_REQUEST_CELL: ContextVar[ShadowRequestCell | None] = ContextVar(
    "emr4_shadow_request_cell", default=None
)


class ShadowInstrumentationRuntime:
    """Fail-closed route and after-send scaffold with no admitted generation."""

    __slots__ = ("_generation_reader", "_disable_latch", "_offer_port")

    def __init__(
        self,
        *,
        generation_reader: ShadowGenerationReader,
        disable_latch: ExternalShadowDisableLatch,
        offer_port: ShadowOfferPort,
    ) -> None:
        self._generation_reader = generation_reader
        self._disable_latch = disable_latch
        self._offer_port = offer_port

    def current_generation(self) -> ShadowInstrumentationGeneration | None:
        try:
            return self._generation_reader.current()
        except Exception:
            return None

    def is_globally_enabled(self) -> bool:
        generation = self.current_generation()
        return bool(
            generation is not None
            and generation.status == "current"
            and generation.global_enabled
            and not self._disable_latch.disabled
        )

    def try_stage(
        self,
        route_adapter_id: str,
        *,
        context_supplier: Callable[[], ServerOwnedShadowRequestContext | None]
        | None = None,
        projection_supplier: Callable[
            [ShadowInstrumentationGeneration, ServerOwnedShadowRequestContext],
            ShadowRouteProjection,
        ]
        | None = None,
    ) -> None:
        """Return before suppliers/cell access while the generation is disabled."""

        del route_adapter_id, context_supplier, projection_supplier
        if not self.is_globally_enabled():
            return
        # Enabled staging requires a separately reviewed descendant.
        return

    def bind_request_cell(self) -> tuple[Token, ShadowRequestCell]:
        cell = ShadowRequestCell()
        return _REQUEST_CELL.set(cell), cell

    def reset_request_cell(self, token: Token) -> None:
        _REQUEST_CELL.reset(token)

    def current_request_cell(self) -> ShadowRequestCell | None:
        return _REQUEST_CELL.get()

    def offer_staged_after_send(self, cell: ShadowRequestCell) -> None:
        projection = cell.take()
        if projection is None:
            return
        try:
            self._offer_port.offer_nowait(projection)
        except Exception:
            return


shadow_instrumentation_runtime = ShadowInstrumentationRuntime(
    generation_reader=StaticShadowGenerationReader(),
    disable_latch=ExternalShadowDisableLatch(),
    offer_port=ClosedShadowOfferPort(),
)
