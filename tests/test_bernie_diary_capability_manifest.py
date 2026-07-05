from dataclasses import FrozenInstanceError

import pytest

from app.models.appointments import AppointmentStatus
from app.schemas.appointments import STATUS_REASON_CODES
from app.services.diary.capabilities import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapabilityTier,
    get_bernie_capability,
)
from app.services.diary.capability_manifest import (
    MANIFEST_SCHEMA_VERSION,
    build_bernie_diary_capability_manifest,
)
from app.services.diary.confirm_actions import DIARY_CONFIRM_ACTIONS, DiaryConfirmAction
from app.services.diary.envelopes import DiaryActionAuthor
from app.services.diary.outcomes import BernieBookingOutcomeKind
from app.services.diary.schedule_explanations import DiaryScheduleExplanationReason


def test_manifest_has_expected_schema_and_authority_statement():
    manifest = build_bernie_diary_capability_manifest()

    assert manifest["schema_version"] == MANIFEST_SCHEMA_VERSION
    assert "read-only context" in manifest["authority_statement"]
    assert "cannot authorize writes" in manifest["authority_statement"]
    assert "schema-literate, not code-authoritative" in manifest["principles"][0]


def test_manifest_appointment_statuses_match_backend_enum():
    manifest = build_bernie_diary_capability_manifest()

    assert manifest["entities"]["appointment_statuses"]["values"] == [
        status.value for status in AppointmentStatus
    ]
    assert manifest["entities"]["appointment_statuses"]["authority"] == "source_of_truth"


def test_manifest_reason_codes_match_backend_sources():
    manifest = build_bernie_diary_capability_manifest()

    assert manifest["reason_codes"]["appointment_status_reason_codes"] == sorted(STATUS_REASON_CODES)
    assert manifest["reason_codes"]["statuses_requiring_reason_code"] == ["Cancelled", "NoShow", "DNA"]
    assert manifest["reason_codes"]["schedule_reason_codes"] == [
        reason.value for reason in DiaryScheduleExplanationReason
    ]
    assert "frontend" in manifest["reason_codes"]["drift_note"].lower()


def test_manifest_capabilities_are_source_derived_and_non_authoritative():
    manifest = build_bernie_diary_capability_manifest()
    manifest_capabilities = manifest["capabilities"]["items"]

    assert len(manifest_capabilities) == len(BERNIE_CAPABILITY_REGISTRY)
    assert manifest["capabilities"]["authority"] == "declared_not_enforced"
    assert "future work" in manifest["capabilities"]["note"]

    registry_by_name = {capability.name: capability for capability in BERNIE_CAPABILITY_REGISTRY}
    manifest_by_name = {capability["name"]: capability for capability in manifest_capabilities}
    assert set(manifest_by_name) == set(registry_by_name)

    for name, capability in registry_by_name.items():
        row = manifest_by_name[name]
        assert row["tier"] == capability.tier.value
        assert row["summary"] == capability.summary
        assert row["requires_staff_confirmation"] is capability.requires_staff_confirmation
        assert row["allowed_authors"] == [author.value for author in capability.allowed_authors]


def test_capability_registry_entries_are_frozen_and_unique():
    names = [capability.name for capability in BERNIE_CAPABILITY_REGISTRY]
    assert len(names) == len(set(names))

    with pytest.raises(FrozenInstanceError):
        BERNIE_CAPABILITY_REGISTRY[0].summary = "mutable"

    for capability in BERNIE_CAPABILITY_REGISTRY:
        assert capability.name and capability.name.isidentifier()
        assert isinstance(capability.tier, BernieCapabilityTier)
        assert capability.summary
        assert all(isinstance(author, DiaryActionAuthor) for author in capability.allowed_authors)
        assert get_bernie_capability(capability.name) is capability

    assert get_bernie_capability("not_a_capability") is None


def test_confirm_capabilities_are_staff_only_and_bridge_to_signed_gate():
    confirm_capabilities = [
        capability for capability in BERNIE_CAPABILITY_REGISTRY
        if capability.tier == BernieCapabilityTier.confirm
    ]
    assert confirm_capabilities

    for capability in confirm_capabilities:
        assert capability.requires_staff_confirmation is True
        assert capability.allowed_authors == (DiaryActionAuthor.staff_ui,)
        assert DiaryActionAuthor.bernie not in capability.allowed_authors

    confirm_booking = get_bernie_capability("confirm_booking")
    assert confirm_booking is not None
    assert DIARY_CONFIRM_ACTIONS[DiaryConfirmAction.bernie_create].endpoint in confirm_booking.implemented_as


def test_non_confirm_capabilities_cannot_claim_write_authority():
    for capability in BERNIE_CAPABILITY_REGISTRY:
        assert not hasattr(capability, "writes_authorized")
        assert not hasattr(capability, "evidence_refs")
        assert not hasattr(capability, "freshness_id")
        if capability.tier == BernieCapabilityTier.read_only:
            assert capability.requires_staff_confirmation is False
        if capability.tier == BernieCapabilityTier.meta:
            assert capability.requires_staff_confirmation is False
        if capability.tier == BernieCapabilityTier.propose:
            assert capability.requires_staff_confirmation is True
            summary = capability.summary.lower()
            assert "proposal" in summary or "prepare" in summary
            assert "writes nothing" in summary or "for staff review" in summary


def test_manifest_outcomes_cover_backend_outcome_enum():
    manifest = build_bernie_diary_capability_manifest()

    assert manifest["outcomes"]["kinds"] == [
        outcome.value for outcome in BernieBookingOutcomeKind
    ]
    assert set(manifest["outcomes"]["outcome_session_states"]) == {
        outcome.value for outcome in BernieBookingOutcomeKind
    }
    assert manifest["outcomes"]["authority"] == "deterministic_guard"
    assert "report-only" in manifest["outcomes"]["note"]


def test_manifest_confirmation_sequence_is_the_only_write_boundary():
    manifest = build_bernie_diary_capability_manifest()
    sequence = {entry["type"]: entry for entry in manifest["confirmation_boundaries"]["envelope_sequence"]}

    assert sequence["intent"]["writes_authorized"] is False
    assert sequence["proposal"]["writes_authorized"] is False
    assert sequence["suggestion"]["writes_authorized"] is False
    assert sequence["confirmation"]["writes_authorized"] is True
    assert sequence["confirmation"]["requires_staff_confirmation"] is True
    assert manifest["confirmation_boundaries"]["authority"] == "staff_confirmation_required"


def test_manifest_explicitly_lists_non_authority_boundaries():
    manifest = build_bernie_diary_capability_manifest()
    boundaries = " ".join(manifest["non_authority_boundaries"]).lower()

    assert "rbac" in boundaries
    assert "availability" in boundaries
    assert "signed confirmation evidence" in boundaries
    assert "display copy" in boundaries
    assert "raw patient data" in boundaries
