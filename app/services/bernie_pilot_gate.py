import uuid
from dataclasses import dataclass

from app.models.tenancy import User


BERNIE_STAFF_REVIEW_SURFACE = "bernie_staff_review"


@dataclass(frozen=True)
class BerniePilotEligibility:
    surface: str
    enabled: bool
    eligible: bool
    reason: str
    practice_allowed: bool
    user_allowed: bool


def _parse_uuid_allowlist(raw_value: str | None) -> set[uuid.UUID]:
    allowed: set[uuid.UUID] = set()
    if not raw_value:
        return allowed
    for item in raw_value.replace(";", ",").split(","):
        value = item.strip()
        if not value:
            continue
        try:
            allowed.add(uuid.UUID(value))
        except ValueError:
            continue
    return allowed


def evaluate_bernie_pilot_eligibility(
    *,
    enabled: bool,
    practice_allowlist: str | None,
    user_allowlist: str | None,
    current_user: User,
) -> BerniePilotEligibility:
    practice_ids = _parse_uuid_allowlist(practice_allowlist)
    user_ids = _parse_uuid_allowlist(user_allowlist)

    practice_allowed = current_user.practice_id in practice_ids
    user_allowed = current_user.id in user_ids

    if not enabled:
        return BerniePilotEligibility(
            surface=BERNIE_STAFF_REVIEW_SURFACE,
            enabled=False,
            eligible=False,
            reason="pilot_disabled",
            practice_allowed=practice_allowed,
            user_allowed=user_allowed,
        )

    if not practice_ids and not user_ids:
        return BerniePilotEligibility(
            surface=BERNIE_STAFF_REVIEW_SURFACE,
            enabled=True,
            eligible=False,
            reason="no_allowlist_match",
            practice_allowed=False,
            user_allowed=False,
        )

    if practice_allowed or user_allowed:
        return BerniePilotEligibility(
            surface=BERNIE_STAFF_REVIEW_SURFACE,
            enabled=True,
            eligible=True,
            reason="allowlist_match",
            practice_allowed=practice_allowed,
            user_allowed=user_allowed,
        )

    return BerniePilotEligibility(
        surface=BERNIE_STAFF_REVIEW_SURFACE,
        enabled=True,
        eligible=False,
        reason="no_allowlist_match",
        practice_allowed=False,
        user_allowed=False,
    )
