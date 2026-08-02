"""Strict request/response schemas for the provider-free OIDC transport."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

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


class GenericOIDCError(_StrictOIDCTransportModel):
    error: Literal["authentication_failed", "authentication_temporarily_unavailable"]


__all__ = [
    "GenericOIDCError",
    "MicrosoftOIDCStartRequest",
    "MicrosoftOIDCStartResponse",
]
