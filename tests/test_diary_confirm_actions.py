from app.services.bernie_turn_evidence import (
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_CONFIRMATION_EVIDENCE_VERSION,
    mint_signed_confirmation_evidence,
)
from app.services.diary.capabilities import get_bernie_capability
from app.services.diary.confirm_actions import (
    DIARY_CONFIRM_ACTIONS,
    DiaryConfirmAction,
    get_diary_confirm_action,
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
    """Focused unit tests for the shared evidence-verification helper."""

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
        """Tampered payload fails verification and produces a block."""
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
        """When evidence is required but None, the helper falls through to
        verify_signed_confirmation_evidence(None, ...) which returns
        signed_evidence_missing — matching original route behaviour."""
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
        """When not required and absent, the helper blocks — caller must
        handle the optional pattern with its own guard."""
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
