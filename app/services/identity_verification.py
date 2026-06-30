"""Non-mutating identity-verification adapter contracts.

These contracts prepare EMR4 for Medicare Online OPV/PVM, DVA, HI/IHI, or other
practice-approved identity checks without binding Bernie or the Diary UI to a
specific external provider. The default adapter fails closed and performs no
network access.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Protocol
import uuid

from pydantic import BaseModel, ConfigDict, Field


class IdentityVerificationMethod(str, Enum):
    OPV = "opv"
    PVM = "pvm"
    PVF = "pvf"
    OVV = "ovv"
    IHI = "ihi"


class IdentityVerificationStatus(str, Enum):
    VERIFIED = "verified"
    NOT_VERIFIED = "not_verified"
    NEEDS_MORE_INFORMATION = "needs_more_information"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    DISABLED = "disabled"


class IdentityVerificationRequest(BaseModel):
    """Minimal patient identity data for a non-mutating verification attempt."""

    patient_id: uuid.UUID | None = None
    practice_id: uuid.UUID
    method: IdentityVerificationMethod
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    medicare_number: str | None = None
    medicare_irn: str | None = None
    dva_number: str | None = None
    ihi_number: str | None = None
    service_date: date | None = None
    consent_confirmed: bool = False
    source_surface: str = "bernie_booking_review"


class IdentityVerificationResult(BaseModel):
    """Provider-neutral, PHI-minimised verification result for staff review."""

    model_config = ConfigDict(extra="forbid")

    method: IdentityVerificationMethod
    status: IdentityVerificationStatus
    verified: bool = False
    reason_code: str
    message: str
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    matched_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    provider: str = "disabled"
    raw_response_stored: bool = False

    def to_context_frame(self) -> dict[str, object]:
        return {
            "type": "identity_verification",
            "method": self.method.value,
            "status": self.status.value,
            "verified": self.verified,
            "reason_code": self.reason_code,
            "matched_fields": self.matched_fields,
            "warnings": self.warnings,
            "provider": self.provider,
        }


class IdentityVerificationAdapter(Protocol):
    provider: str

    def verify(self, request: IdentityVerificationRequest) -> IdentityVerificationResult:
        """Run a non-mutating identity verification check."""


class DisabledIdentityVerificationAdapter:
    provider = "disabled"

    def verify(self, request: IdentityVerificationRequest) -> IdentityVerificationResult:
        return IdentityVerificationResult(
            method=request.method,
            status=IdentityVerificationStatus.DISABLED,
            verified=False,
            reason_code="identity_verification_disabled",
            message="Identity verification adapter is disabled.",
            provider=self.provider,
        )


class DeterministicIdentityVerificationAdapter:
    """Test/dev adapter that verifies only when required local fields are present."""

    provider = "deterministic"

    def verify(self, request: IdentityVerificationRequest) -> IdentityVerificationResult:
        required_fields = ["first_name", "last_name", "date_of_birth"]
        if request.method in {
            IdentityVerificationMethod.OPV,
            IdentityVerificationMethod.PVM,
        }:
            required_fields.extend(["medicare_number", "medicare_irn"])
        elif request.method == IdentityVerificationMethod.OVV:
            required_fields.append("dva_number")
        elif request.method == IdentityVerificationMethod.IHI:
            required_fields.append("ihi_number")

        missing = [
            field_name
            for field_name in required_fields
            if getattr(request, field_name) in (None, "")
        ]
        if not request.consent_confirmed:
            missing.append("consent_confirmed")

        if missing:
            return IdentityVerificationResult(
                method=request.method,
                status=IdentityVerificationStatus.NEEDS_MORE_INFORMATION,
                verified=False,
                reason_code="missing_identity_verification_inputs",
                message="Identity verification requires additional fields before it can run.",
                matched_fields=[
                    field_name for field_name in required_fields if field_name not in missing
                ],
                warnings=[f"missing:{field_name}" for field_name in missing],
                provider=self.provider,
            )

        return IdentityVerificationResult(
            method=request.method,
            status=IdentityVerificationStatus.VERIFIED,
            verified=True,
            reason_code="deterministic_identity_match",
            message="Deterministic dev adapter verified that required fields were supplied.",
            matched_fields=required_fields,
            provider=self.provider,
        )

