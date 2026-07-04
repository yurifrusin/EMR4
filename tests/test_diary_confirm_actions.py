from app.services.bernie_turn_evidence import (
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_DELETE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_STATUS_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
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
