"""Strict request/response schemas for the provider-free OIDC transport."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.services.application_identity_oidc_adapter import ReturnTarget, Surface


class _StrictOIDCTransportModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MicrosoftOIDCStartRequest(_StrictOIDCTransportModel):
    surface: Surface
    return_target: ReturnTarget


class MicrosoftOIDCStartResponse(_StrictOIDCTransportModel):
    status: Literal["authorization_required"] = "authorization_required"
    authorization_uri: str
    attempt_expires_at: datetime


class OIDCAdmissionGrantRedeemRequest(_StrictOIDCTransportModel):
    admission_grant: str = Field(
        min_length=43,
        max_length=43,
        pattern=r"^[A-Za-z0-9_-]{43}$",
    )
    surface: Surface


class OIDCAdmissionGrantRedeemResponse(_StrictOIDCTransportModel):
    status: Literal["authenticated"] = "authenticated"
    surface: Surface
    csrf_token: str
    session_expires_at: datetime
    surface_idle_expires_at: datetime


class GenericOIDCError(_StrictOIDCTransportModel):
    error: Literal["authentication_failed", "authentication_temporarily_unavailable"]


__all__ = [
    "GenericOIDCError",
    "MicrosoftOIDCStartRequest",
    "MicrosoftOIDCStartResponse",
    "OIDCAdmissionGrantRedeemRequest",
    "OIDCAdmissionGrantRedeemResponse",
]
