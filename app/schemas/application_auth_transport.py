"""Bounded authored-synthetic schemas for the shared-auth transport."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.services.application_auth_runtime import Surface


_OPAQUE_PATTERN = r"^[A-Za-z0-9._~-]{43,128}$"
_CORRELATION_PATTERN = r"^correlation-[a-z0-9-]{1,64}$"
_PKCE_CHALLENGE_PATTERN = r"^[A-Za-z0-9_-]{43}$"


class _StrictTransportModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SurfaceRequest(_StrictTransportModel):
    surface: Surface
    correlation_id: str | None = Field(
        default=None,
        pattern=_CORRELATION_PATTERN,
        max_length=76,
    )


class SyntheticSessionRequest(SurfaceRequest):
    bootstrap_credential: str = Field(
        min_length=43,
        max_length=128,
        pattern=_OPAQUE_PATTERN,
    )


class ExchangeIssueRequest(_StrictTransportModel):
    source_surface: Literal[Surface.WORD_DESKTOP, Surface.WORD_ONLINE]
    target_surface: Literal[Surface.NATIVE_DIARY]
    target_origin: str = Field(min_length=9, max_length=255)
    state: str = Field(min_length=16, max_length=256)
    nonce: str = Field(min_length=16, max_length=256)
    pkce_challenge: str = Field(
        min_length=43,
        max_length=43,
        pattern=_PKCE_CHALLENGE_PATTERN,
    )
    correlation_id: str | None = Field(
        default=None,
        pattern=_CORRELATION_PATTERN,
        max_length=76,
    )


class ExchangeRedeemRequest(_StrictTransportModel):
    exchange_code: str = Field(
        min_length=43,
        max_length=128,
        pattern=_OPAQUE_PATTERN,
    )
    source_surface: Literal[Surface.WORD_DESKTOP, Surface.WORD_ONLINE]
    target_surface: Literal[Surface.NATIVE_DIARY]
    source_origin: str = Field(min_length=9, max_length=255)
    state: str = Field(min_length=16, max_length=256)
    nonce: str = Field(min_length=16, max_length=256)
    pkce_verifier: str = Field(
        min_length=43,
        max_length=128,
        pattern=_OPAQUE_PATTERN,
    )
    correlation_id: str | None = Field(
        default=None,
        pattern=_CORRELATION_PATTERN,
        max_length=76,
    )


class CsrfResponse(_StrictTransportModel):
    csrf_token: str
    surface: Surface


class SessionResponse(_StrictTransportModel):
    status: str = "authenticated"
    surface: Surface
    csrf_token: str
    surface_idle_expires_at: datetime


class ValidatedSessionResponse(_StrictTransportModel):
    status: str = "authenticated"
    surface: Surface
    current_backend_role: str
    authority_source: str = "emr4_backend"
    data_class: str = "authored_synthetic"
    surface_idle_expires_at: datetime


class ExchangeIssueResponse(_StrictTransportModel):
    exchange_code: str
    target_surface: Surface
    expires_at: datetime


__all__ = [
    "CsrfResponse",
    "ExchangeIssueRequest",
    "ExchangeIssueResponse",
    "ExchangeRedeemRequest",
    "SessionResponse",
    "SurfaceRequest",
    "SyntheticSessionRequest",
    "ValidatedSessionResponse",
]
