import uuid

from app.models.tenancy import UserRole
from app.services.ai.contracts import AiCapability, AiMethod
from app.services.ai.entitlements import (
    AiAccessRole,
    AiActorContext,
    actor_context_from_user,
    decide_ai_entitlement,
)


class DummyUser:
    id = uuid.uuid4()
    practice_id = uuid.uuid4()

    def __init__(self, role):
        self.role = role


def actor(*roles: str, environment: str = "dev") -> AiActorContext:
    return AiActorContext(
        user_id=uuid.uuid4(),
        practice_id=uuid.uuid4(),
        roles=roles,
        environment=environment,
    )


def test_gp_practice_role_maps_to_clinical_access_only():
    context = actor_context_from_user(DummyUser(UserRole.GP))

    clinical = decide_ai_entitlement(
        context,
        AiCapability.AUDIO_SCRIBE,
        AiMethod.INVOKE,
    )
    reception = decide_ai_entitlement(
        context,
        AiCapability.BERNIE_BOOKING_INTERPRET,
        AiMethod.INVOKE,
    )

    assert clinical.allowed is True
    assert clinical.matched_role == AiAccessRole.CLINICAL_USER
    assert reception.allowed is False
    assert reception.reason == "role_not_allowed"


def test_reception_user_can_prepare_bernie_proposal_but_not_clinical_scribe():
    context = actor_context_from_user(DummyUser(UserRole.Receptionist))

    proposal = decide_ai_entitlement(
        context,
        AiCapability.BERNIE_BOOKING_PREPARE_PROPOSAL,
        AiMethod.INVOKE,
    )
    clinical = decide_ai_entitlement(
        context,
        AiCapability.CLINICAL_EXTRACTION,
        AiMethod.INVOKE,
    )

    assert proposal.allowed is True
    assert proposal.matched_role == AiAccessRole.RECEPTION_USER
    assert clinical.allowed is False
    assert clinical.reason == "role_not_allowed"


def test_admin_maps_to_clinical_and_reception_supervisor_access():
    context = actor_context_from_user(DummyUser(UserRole.Admin))

    clinical = decide_ai_entitlement(
        context,
        AiCapability.LETTER_DRAFTING,
        AiMethod.DRY_RUN,
    )
    reception = decide_ai_entitlement(
        context,
        AiCapability.BERNIE_BOOKING_SUGGEST_SLOTS,
        AiMethod.INVOKE,
    )

    assert clinical.allowed is True
    assert reception.allowed is True
    assert reception.matched_role == AiAccessRole.RECEPTION_SUPERVISOR


def test_dev_operator_can_run_provider_live_smoke_only_in_dev():
    context = actor(AiAccessRole.DEV_OPERATOR)

    dev_decision = decide_ai_entitlement(
        context,
        AiCapability.PROVIDER_LIVE_SMOKE,
        AiMethod.LIVE_SMOKE,
    )
    prod_decision = decide_ai_entitlement(
        context,
        AiCapability.PROVIDER_LIVE_SMOKE,
        AiMethod.LIVE_SMOKE,
        environment="prod",
    )

    assert dev_decision.allowed is True
    assert prod_decision.allowed is False
    assert prod_decision.reason == "environment_not_allowed"


def test_disabled_role_overrides_other_roles():
    context = actor(AiAccessRole.DISABLED, AiAccessRole.PLATFORM_ADMIN)

    decision = decide_ai_entitlement(
        context,
        AiCapability.CLINICAL_EXTRACTION,
        AiMethod.INVOKE,
    )

    assert decision.allowed is False
    assert decision.reason == "actor_disabled"


def test_unknown_capability_and_unknown_method_fail_closed():
    context = actor(AiAccessRole.PLATFORM_ADMIN)

    unknown_capability = decide_ai_entitlement(context, "unknown.capability", AiMethod.INVOKE)
    unknown_method = decide_ai_entitlement(
        context,
        AiCapability.CLINICAL_EXTRACTION,
        "delete_everything",
    )

    assert unknown_capability.allowed is False
    assert unknown_capability.reason == "unknown_capability"
    assert unknown_method.allowed is False
    assert unknown_method.reason == "unknown_method"


def test_registry_method_allowlist_is_enforced_before_role_allowlist():
    context = actor(AiAccessRole.RECEPTION_USER)

    decision = decide_ai_entitlement(
        context,
        AiCapability.BERNIE_BOOKING_INTERPRET,
        AiMethod.LIVE_SMOKE,
    )

    assert decision.allowed is False
    assert decision.reason == "method_not_allowed"
