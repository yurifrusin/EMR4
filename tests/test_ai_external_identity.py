import asyncio

from app.services.ai.access_service import AccessAiRequest, AccessAiService
from app.services.ai.audit_events import AiAuditSourceSurface
from app.services.ai.entitlements import (
    AiAccessRole,
    AiActorContext,
    decide_ai_entitlement,
)
from app.services.ai.external_identity import (
    ExternalIdentityAttribute,
    ExternalIdentityAttributeMapping,
    ExternalIdentityProvider,
    ExternalIdentityRoleMapping,
    access_roles_from_external_attributes,
    access_roles_from_external_groups,
    access_roles_from_external_identity,
)
from app.services.ai.contracts import AiCapability, AiMethod


class FakeProvider:
    def __init__(self):
        self.calls = 0

    def generate_json(self, contents, temperature: float) -> dict:
        self.calls += 1
        return {"ok": True}


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


def test_external_group_mapping_is_provider_scoped_and_does_not_cross_grant():
    roles = access_roles_from_external_groups(
        ExternalIdentityProvider.WORKOS,
        ("access-ai-clinical@littlestardigital.com", "access_ai:reception"),
    )

    assert roles == (AiAccessRole.RECEPTION_USER,)


def test_invalid_configured_group_role_is_not_emitted():
    roles = access_roles_from_external_groups(
        ExternalIdentityProvider.WORKOS,
        ("access_ai:superuser",),
        mappings=(
            ExternalIdentityRoleMapping(
                provider=ExternalIdentityProvider.WORKOS,
                external_group="access_ai:superuser",
                access_ai_role="ai.superuser",
            ),
        ),
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


def test_workos_fga_like_attributes_map_only_exact_allowlisted_values():
    roles = access_roles_from_external_attributes(
        ExternalIdentityProvider.WORKOS,
        (
            ExternalIdentityAttribute("access_ai.role", "reception"),
            ExternalIdentityAttribute("access_ai.role", "platform_admin"),
            ExternalIdentityAttribute("fga.can_invoke_any_ai", "true"),
            ExternalIdentityAttribute("access_ai.role", " clinical "),
        ),
    )

    assert roles == (AiAccessRole.CLINICAL_USER, AiAccessRole.RECEPTION_USER)


def test_fga_like_attributes_feed_entitlement_without_expanding_authority():
    roles = access_roles_from_external_identity(
        ExternalIdentityProvider.WORKOS,
        external_attributes=(
            ExternalIdentityAttribute("access_ai.role", "reception"),
        ),
    )
    actor = AiActorContext(
        user_id=None,
        practice_id=None,
        roles=roles,
        environment="dev",
    )

    allowed = decide_ai_entitlement(
        actor,
        AiCapability.BERNIE_BOOKING_PREPARE_PROPOSAL,
        AiMethod.INVOKE,
    )
    blocked = decide_ai_entitlement(
        actor,
        AiCapability.PROVIDER_LIVE_SMOKE,
        AiMethod.LIVE_SMOKE,
    )

    assert allowed.allowed is True
    assert allowed.matched_role == AiAccessRole.RECEPTION_USER
    assert blocked.allowed is False
    assert blocked.reason == "role_not_allowed"


def test_unknown_fga_like_attributes_grant_no_roles_and_fail_closed():
    roles = access_roles_from_external_identity(
        ExternalIdentityProvider.WORKOS,
        external_attributes=(
            ExternalIdentityAttribute("fga.relation", "owner"),
            ExternalIdentityAttribute("resource", "ai_capability:*"),
            ExternalIdentityAttribute("access_ai.role", "admin"),
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
        AiCapability.BERNIE_BOOKING_INTERPRET,
        AiMethod.INVOKE,
    )

    assert roles == ()
    assert decision.allowed is False
    assert decision.reason == "role_not_allowed"


def test_unmapped_external_identity_blocks_access_ai_before_provider_call():
    roles = access_roles_from_external_identity(
        ExternalIdentityProvider.WORKOS,
        external_groups=("employees",),
        external_attributes=(
            ExternalIdentityAttribute("fga.can_invoke_any_ai", "true"),
        ),
    )
    provider = FakeProvider()
    service = AccessAiService(provider)

    result = asyncio.run(service.invoke(
        AccessAiRequest(
            actor=AiActorContext(
                user_id=None,
                practice_id=None,
                roles=roles,
                environment="dev",
            ),
            capability=AiCapability.BERNIE_BOOKING_INTERPRET,
            method=AiMethod.INVOKE,
            contents={"input": "non-phi fixture"},
            source_surface=AiAuditSourceSurface.API,
        )
    ))

    assert result.allowed is False
    assert result.denial_reason == "role_not_allowed"
    assert provider.calls == 0


def test_invalid_configured_attribute_role_is_not_emitted():
    roles = access_roles_from_external_attributes(
        ExternalIdentityProvider.WORKOS,
        (ExternalIdentityAttribute("access_ai.role", "root"),),
        mappings=(
            ExternalIdentityAttributeMapping(
                provider=ExternalIdentityProvider.WORKOS,
                attribute="access_ai.role",
                value="root",
                access_ai_role="ai.root",
            ),
        ),
    )

    assert roles == ()


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


def test_external_disabled_attribute_overrides_group_and_attribute_grants():
    roles = access_roles_from_external_identity(
        ExternalIdentityProvider.WORKOS,
        external_groups=("access_ai:reception",),
        external_attributes=(
            ExternalIdentityAttribute("access_ai.role", "clinical"),
            ExternalIdentityAttribute("access_ai.disabled", "true"),
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
        AiCapability.CLINICAL_EXTRACTION,
        AiMethod.INVOKE,
    )

    assert roles == (
        AiAccessRole.RECEPTION_USER,
        AiAccessRole.CLINICAL_USER,
        AiAccessRole.DISABLED,
    )
    assert decision.allowed is False
    assert decision.reason == "actor_disabled"
