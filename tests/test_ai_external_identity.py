from app.services.ai.entitlements import (
    AiAccessRole,
    AiActorContext,
    decide_ai_entitlement,
)
from app.services.ai.external_identity import (
    ExternalIdentityProvider,
    access_roles_from_external_groups,
)
from app.services.ai.contracts import AiCapability, AiMethod


def test_cloud_identity_groups_map_to_access_ai_roles_case_insensitively():
    roles = access_roles_from_external_groups(
        ExternalIdentityProvider.CLOUD_IDENTITY,
        (
            "ACCESS-AI-CLINICAL@LITTLESTARDIGITAL.COM",
            "access-ai-reception-supervisors@littlestardigital.com",
        ),
    )

    assert roles == (AiAccessRole.CLINICAL_USER, AiAccessRole.RECEPTION_SUPERVISOR)


def test_unknown_external_groups_grant_no_access_roles():
    roles = access_roles_from_external_groups(
        ExternalIdentityProvider.CLOUD_IDENTITY,
        ("domain-users@littlestardigital.com", "random-group"),
    )

    assert roles == ()


def test_workos_style_roles_can_feed_same_entitlement_contract():
    roles = access_roles_from_external_groups(
        ExternalIdentityProvider.WORKOS,
        ("access_ai:reception",),
    )
    actor = AiActorContext(
        user_id=None,
        practice_id=None,
        roles=roles,
        environment="dev",
    )

    allowed = decide_ai_entitlement(
        actor,
        AiCapability.BERNIE_BOOKING_INTERPRET,
        AiMethod.INVOKE,
    )
    blocked = decide_ai_entitlement(
        actor,
        AiCapability.CLINICAL_EXTRACTION,
        AiMethod.INVOKE,
    )

    assert allowed.allowed is True
    assert blocked.allowed is False
    assert blocked.reason == "role_not_allowed"


def test_external_disabled_group_still_fails_closed_through_entitlement():
    roles = access_roles_from_external_groups(
        ExternalIdentityProvider.CLOUD_IDENTITY,
        (
            "access-ai-platform-admins@littlestardigital.com",
            "access-ai-disabled@littlestardigital.com",
        ),
    )
    actor = AiActorContext(
        user_id=None,
        practice_id=None,
        roles=roles,
        environment="dev",
    )

    decision = decide_ai_entitlement(
        actor,
        AiCapability.PROVIDER_LIVE_SMOKE,
        AiMethod.LIVE_SMOKE,
    )

    assert decision.allowed is False
    assert decision.reason == "actor_disabled"
