from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-channel-neutral-patient-interaction-foundation-plan.md"
ARCHITECTURE = ROOT / "docs" / "raisa-channel-neutral-patient-interaction-foundation-architecture.md"
THREAT_MODEL = (
    ROOT
    / "docs"
    / "security"
    / "raisa-channel-neutral-patient-interaction-foundation-threat-model-delta.md"
)


def test_plan_and_design_documents_have_date_timestamp_and_closed_status() -> None:
    for path in (PLAN, ARCHITECTURE, THREAT_MODEL):
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-13" in text
        assert "Timestamp: 2026-08-13T" in text
        assert "+10:00 (Australia/Brisbane)" in text
        assert "provider-free" in text.lower()
    assert "Status: frozen" in PLAN.read_text(encoding="utf-8")
    assert "unmounted" in ARCHITECTURE.read_text(encoding="utf-8").lower()


def test_plan_freezes_exact_identity_assurance_and_recovery_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "passkey_first_not_passkey_only" in text
    assert "A domain patient record, IHI, Medicare number" in text
    assert "Email is not an out-of-band authenticator" in text
    assert "Recovery must support multiple bound authenticators" in text
    assert "PatientIdentityBinding" in text
    assert "IdentityAssuranceDecision" in text
    assert "PatientRecoveryCase" in text
    assert "at least 60 hostile mutations" in text


def test_plan_keeps_external_clients_runtime_and_authority_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "No application runtime, OpenAPI route, GraphQL schema" in text
    assert "No protected evidence, patient/clinical/product data" in text
    assert "provider call" in text
    assert "command/write" in text
    assert "protected-ref movement" in text
    assert "`docs/branding/`" in text
    assert "staging is explicit-path only" in normalized


def test_architecture_preserves_api_spine_and_channel_neutrality() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")

    assert "REST/OpenAPI commands" in text
    assert "channel delivery and webhook events" in text
    assert "transport deduplication" in text.lower()
    assert "not a command idempotency key" in text.lower()
    assert "Plain text is the universal representation" in text
    assert "generic command tunnel" in text
    assert "patient never gives the assistant an EMR credential" in text


def test_threat_model_names_high_risk_patient_identity_failures() -> None:
    text = THREAT_MODEL.read_text(encoding="utf-8")

    for threat in (
        "Account or patient enumeration",
        "Recycled number, SIM swap or port-out",
        "Phishing or relay",
        "Stale candidate race",
        "Cross-practice confused deputy",
        "Recovery takeover",
        "Passkey sync-fabric recovery compromise",
        "Webhook forgery",
        "Prompt injection from message content",
        "Notification over-disclosure",
    ):
        assert threat in text
