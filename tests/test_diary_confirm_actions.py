from app.services.bernie_turn_evidence import (
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
    mint_signed_confirmation_evidence,
)
from app.services.diary.capabilities import get_bernie_capability
from app.services.diary.confirm_actions import (
    DIARY_CONFIRM_ACTIONS,
    DiaryConfirmAction,
    get_diary_confirm_action,
)


def test_diary_confirm_actions_pin_current_endpoints_and_evidence_purposes():
    expected = {
        DiaryConfirmAction.staff_create: (
            "/api/v1/appointments/proposals/create/confirm",
            SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
        ),
        DiaryConfirmAction.bernie_create: (
            "/api/v1/appointments/proposals/create/confirm-bernie",
            SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
        ),
        DiaryConfirmAction.update: (
            "/api/v1/appointments/proposals/update/confirm",
            SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
        ),
        DiaryConfirmAction.status: (
            "/api/v1/appointments/proposals/status-confirm",
            SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
        ),
        DiaryConfirmAction.delete: (
            "/api/v1/appointments/proposals/delete-confirm",
            SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
        ),
    }

    assert set(DIARY_CONFIRM_ACTIONS) == set(expected)
    for action, (endpoint, purpose) in expected.items():
        descriptor = get_diary_confirm_action(action)
        assert descriptor.endpoint == endpoint
        assert descriptor.evidence_purpose == purpose


def test_diary_confirm_action_blocked_issue_payload_matches_route_contract():
    issue = get_diary_confirm_action(DiaryConfirmAction.update).blocked_issue_payload(
        "signed_evidence_required",
        "Signed update confirmation evidence is required.",
    )

    assert issue == {
        "code": "signed_evidence_required",
        "severity": "blocked",
        "message": "Signed update confirmation evidence is required.",
    }


def test_confirm_booking_capability_points_to_descriptor_endpoint():
    capability = get_bernie_capability("confirm_booking")

    assert capability is not None
    assert capability.implemented_as == (
        f"POST {get_diary_confirm_action(DiaryConfirmAction.bernie_create).endpoint}"
    )


from app.services.diary.confirm_actions import (
    verify_signed_confirmation_evidence_block,
)


DUMMY_SECRET = "test-secret-for-verify"
DUMMY_PAYLOAD = {"appointment_id": "test-123", "action": "test"}
DUMMY_PURPOSE = SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE
AUDIT_TAG = "test_signed_confirmation_evidence_verified"


def _block_builder(code, message):
    return {"code": code, "severity": "blocked", "message": message}


def _valid_evidence():
    return mint_signed_confirmation_evidence(
        payload=DUMMY_PAYLOAD,
        evidence_purpose=DUMMY_PURPOSE,
        secret=DUMMY_SECRET,
    )


def _invalid_evidence():
    ev = _valid_evidence()
    ev["payload"] = {"tampered": True}
    return ev


class TestVerifySignedConfirmationEvidenceBlock:
    def test_valid_evidence_returns_audit_tag(self):
        audit_tag, blocks = verify_signed_confirmation_evidence_block(
            evidence=_valid_evidence(),
            evidence_required=True,
            expected_payload=DUMMY_PAYLOAD,
            expected_purpose=DUMMY_PURPOSE,
            block_builder=_block_builder,
            audit_tag=AUDIT_TAG,
            secret=DUMMY_SECRET,
        )
        assert audit_tag == AUDIT_TAG
        assert blocks == []

    def test_invalid_evidence_returns_block(self):
        audit_tag, blocks = verify_signed_confirmation_evidence_block(
            evidence=_invalid_evidence(),
            evidence_required=True,
            expected_payload=DUMMY_PAYLOAD,
            expected_purpose=DUMMY_PURPOSE,
            block_builder=_block_builder,
            audit_tag=AUDIT_TAG,
            secret=DUMMY_SECRET,
        )
        assert audit_tag is None
        assert len(blocks) == 1
        assert blocks[0]["severity"] == "blocked"

    def test_required_evidence_missing_falls_to_verify(self):
        audit_tag, blocks = verify_signed_confirmation_evidence_block(
            evidence=None,
            evidence_required=True,
            expected_payload=DUMMY_PAYLOAD,
            expected_purpose=DUMMY_PURPOSE,
            block_builder=_block_builder,
            audit_tag=AUDIT_TAG,
            missing_message="Custom missing message.",
            secret=DUMMY_SECRET,
        )
        assert audit_tag is None
        assert blocks[0]["code"] == "signed_evidence_missing"

    def test_optional_evidence_missing_returns_block(self):
        audit_tag, blocks = verify_signed_confirmation_evidence_block(
            evidence=None,
            evidence_required=False,
            expected_payload=DUMMY_PAYLOAD,
            expected_purpose=DUMMY_PURPOSE,
            block_builder=_block_builder,
            audit_tag=AUDIT_TAG,
            secret=DUMMY_SECRET,
        )
        assert audit_tag is None
        assert blocks[0]["code"] == "signed_evidence_required"

    def test_valid_evidence_optional_returns_audit_tag(self):
        audit_tag, blocks = verify_signed_confirmation_evidence_block(
            evidence=_valid_evidence(),
            evidence_required=False,
            expected_payload=DUMMY_PAYLOAD,
            expected_purpose=DUMMY_PURPOSE,
            block_builder=_block_builder,
            audit_tag=AUDIT_TAG,
            secret=DUMMY_SECRET,
        )
        assert audit_tag == AUDIT_TAG
        assert blocks == []
