from datetime import date
import uuid

from app.services.identity_verification import (
    DeterministicIdentityVerificationAdapter,
    DisabledIdentityVerificationAdapter,
    IdentityVerificationMethod,
    IdentityVerificationRequest,
    IdentityVerificationStatus,
)


def _request(**overrides):
    body = {
        "practice_id": uuid.uuid4(),
        "method": IdentityVerificationMethod.OPV,
        "first_name": "Margaret",
        "last_name": "Thompson",
        "date_of_birth": date(1955, 3, 20),
        "medicare_number": "2958303372",
        "medicare_irn": "1",
        "consent_confirmed": True,
    }
    body.update(overrides)
    return IdentityVerificationRequest(**body)


def test_disabled_identity_adapter_fails_closed_without_network_call():
    result = DisabledIdentityVerificationAdapter().verify(_request())

    assert result.status == IdentityVerificationStatus.DISABLED
    assert result.verified is False
    assert result.reason_code == "identity_verification_disabled"
    assert result.raw_response_stored is False


def test_deterministic_identity_adapter_returns_context_frame():
    result = DeterministicIdentityVerificationAdapter().verify(_request())

    assert result.status == IdentityVerificationStatus.VERIFIED
    assert result.verified is True
    assert result.matched_fields == [
        "first_name",
        "last_name",
        "date_of_birth",
        "medicare_number",
        "medicare_irn",
    ]
    assert result.to_context_frame() == {
        "type": "identity_verification",
        "method": "opv",
        "status": "verified",
        "verified": True,
        "reason_code": "deterministic_identity_match",
        "matched_fields": result.matched_fields,
        "warnings": [],
        "provider": "deterministic",
    }


def test_deterministic_identity_adapter_requires_consent_and_identifiers():
    result = DeterministicIdentityVerificationAdapter().verify(_request(
        medicare_irn=None,
        consent_confirmed=False,
    ))

    assert result.status == IdentityVerificationStatus.NEEDS_MORE_INFORMATION
    assert result.verified is False
    assert "missing:medicare_irn" in result.warnings
    assert "missing:consent_confirmed" in result.warnings

