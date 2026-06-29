"""
Enterprise identity seam for Access AI.

This does not integrate with WorkOS, Cloud Identity, SAML, SCIM, or FGA directly.
It defines the narrow mapping contract those systems must feed: external groups
or org roles become EMR4-owned Access AI roles, and all authorization still
flows through entitlements.py.
"""
from dataclasses import dataclass
from enum import Enum

from app.services.ai.entitlements import AiAccessRole


class ExternalIdentityProvider(str, Enum):
    CLOUD_IDENTITY = "cloud_identity"
    WORKOS = "workos"
    OIDC = "oidc"
    SAML = "saml"
    INTERNAL = "internal"


@dataclass(frozen=True)
class ExternalIdentityRoleMapping:
    provider: ExternalIdentityProvider
    external_group: str
    access_ai_role: str


DEFAULT_EXTERNAL_ROLE_MAPPINGS: tuple[ExternalIdentityRoleMapping, ...] = (
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.CLOUD_IDENTITY,
        external_group="access-ai-clinical@littlestardigital.com",
        access_ai_role=AiAccessRole.CLINICAL_USER,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.CLOUD_IDENTITY,
        external_group="access-ai-reception@littlestardigital.com",
        access_ai_role=AiAccessRole.RECEPTION_USER,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.CLOUD_IDENTITY,
        external_group="access-ai-reception-supervisors@littlestardigital.com",
        access_ai_role=AiAccessRole.RECEPTION_SUPERVISOR,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.CLOUD_IDENTITY,
        external_group="access-ai-dev-operators@littlestardigital.com",
        access_ai_role=AiAccessRole.DEV_OPERATOR,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.CLOUD_IDENTITY,
        external_group="access-ai-platform-admins@littlestardigital.com",
        access_ai_role=AiAccessRole.PLATFORM_ADMIN,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.CLOUD_IDENTITY,
        external_group="access-ai-disabled@littlestardigital.com",
        access_ai_role=AiAccessRole.DISABLED,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.WORKOS,
        external_group="access_ai:clinical",
        access_ai_role=AiAccessRole.CLINICAL_USER,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.WORKOS,
        external_group="access_ai:reception",
        access_ai_role=AiAccessRole.RECEPTION_USER,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.WORKOS,
        external_group="access_ai:reception_supervisor",
        access_ai_role=AiAccessRole.RECEPTION_SUPERVISOR,
    ),
    ExternalIdentityRoleMapping(
        provider=ExternalIdentityProvider.WORKOS,
        external_group="access_ai:disabled",
        access_ai_role=AiAccessRole.DISABLED,
    ),
)


def access_roles_from_external_groups(
    provider: ExternalIdentityProvider,
    external_groups: tuple[str, ...],
    *,
    mappings: tuple[ExternalIdentityRoleMapping, ...] = DEFAULT_EXTERNAL_ROLE_MAPPINGS,
) -> tuple[str, ...]:
    normalized_groups = {group.strip().lower() for group in external_groups if group.strip()}
    roles: list[str] = []
    for mapping in mappings:
        if mapping.provider is not provider:
            continue
        if mapping.external_group.lower() not in normalized_groups:
            continue
        if mapping.access_ai_role not in roles:
            roles.append(mapping.access_ai_role)
    return tuple(roles)
