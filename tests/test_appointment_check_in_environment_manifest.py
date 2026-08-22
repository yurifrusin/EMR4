"""Focused contract scaffold for the check-in environment manifest normalizer."""

from app.services.appointment_check_in_environment_manifest import (
    MANIFEST_MAX_BYTES,
    MANIFEST_SCHEMA_VERSION,
    MANIFEST_SLOT_IDS,
    ManifestNormalizationResult,
)


def test_manifest_normalizer_public_scaffold_is_frozen() -> None:
    assert MANIFEST_SCHEMA_VERSION == "emr4.check-in-ordinary-environment-manifest.v1"
    assert MANIFEST_MAX_BYTES == 32_768
    assert MANIFEST_SLOT_IDS == (
        "database_connection_credential",
        "application_token_signing_key",
        "admission_snapshot_verification_key",
    )
    assert set(ManifestNormalizationResult.__dataclass_fields__) == {
        "outcome",
        "reason_code",
        "manifest_digest",
        "manifest",
    }
