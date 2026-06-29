"""
Access AI entitlement checks.

This module is intentionally static for the first Access AI sprint. It gives
model invocation code a single fail-closed policy decision point before we wire
the same contract to Cloud Identity groups, WorkOS org roles, or database-backed
practice entitlements.
"""
from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from app.models.tenancy import User, UserRole
from app.services.ai.contracts import AiCapability, AiMethod
from app.services.ai.registry import UnknownAiCapabilityError, get_capability_metadata


class AiAccessRole:
    DISABLED = "ai.disabled"
    PLATFORM_ADMIN = "ai.platform_admin"
    DEV_OPERATOR = "ai.dev_operator"
    CLINICAL_USER = "ai.clinical_user"
    RECEPTION_USER = "ai.reception_user"
    RECEPTION_SUPERVISOR = "ai.reception_supervisor"


@dataclass(frozen=True)
class AiActorContext:
    user_id: UUID | None
    practice_id: UUID | None
    roles: tuple[str, ...]
    environment: str = "dev"


@dataclass(frozen=True)
class AiEntitlementDecision:
    allowed: bool
    reason: str
    capability: AiCapability | str
    method: AiMethod | str
    environment: str
    matched_role: str | None = None


_CLINICAL_CAPABILITIES = frozenset(
    {
        AiCapability.CLINICAL_EXTRACTION,
        AiCapability.AUDIO_SCRIBE,
        AiCapability.LETTER_DRAFTING,
        AiCapability.CLINICAL_KNOWLEDGE_QUERY,
    }
)

_RECEPTION_CAPABILITIES = frozenset(
    {
        AiCapability.BERNIE_BOOKING_INTERPRET,
        AiCapability.BERNIE_BOOKING_SUGGEST_SLOTS,
        AiCapability.BERNIE_BOOKING_PREPARE_PROPOSAL,
    }
)

_ROLE_CAPABILITY_ALLOWLIST: dict[str, frozenset[AiCapability]] = {
    AiAccessRole.PLATFORM_ADMIN: frozenset(AiCapability),
    AiAccessRole.DEV_OPERATOR: frozenset({AiCapability.PROVIDER_LIVE_SMOKE}),
    AiAccessRole.CLINICAL_USER: _CLINICAL_CAPABILITIES,
    AiAccessRole.RECEPTION_USER: _RECEPTION_CAPABILITIES,
    AiAccessRole.RECEPTION_SUPERVISOR: _RECEPTION_CAPABILITIES,
}

_PRACTICE_ROLE_DEFAULTS: dict[UserRole, tuple[str, ...]] = {
    UserRole.GP: (AiAccessRole.CLINICAL_USER,),
    UserRole.Nurse: (AiAccessRole.CLINICAL_USER,),
    UserRole.Receptionist: (AiAccessRole.RECEPTION_USER,),
    UserRole.Admin: (AiAccessRole.CLINICAL_USER, AiAccessRole.RECEPTION_SUPERVISOR),
    UserRole.PracticeOwner: (
        AiAccessRole.CLINICAL_USER,
        AiAccessRole.RECEPTION_SUPERVISOR,
        AiAccessRole.DEV_OPERATOR,
    ),
}


def roles_for_practice_user(user: User) -> tuple[str, ...]:
    """Map today's practice roles onto the Access AI role vocabulary."""
    if not user.role:
        return ()
    return _PRACTICE_ROLE_DEFAULTS.get(user.role, ())


def actor_context_from_user(
    user: User,
    *,
    extra_roles: Iterable[str] = (),
    environment: str = "dev",
) -> AiActorContext:
    roles = tuple(dict.fromkeys((*roles_for_practice_user(user), *extra_roles)))
    return AiActorContext(
        user_id=user.id,
        practice_id=user.practice_id,
        roles=roles,
        environment=environment,
    )


def decide_ai_entitlement(
    actor: AiActorContext,
    capability: AiCapability | str,
    method: AiMethod | str,
    *,
    environment: str | None = None,
) -> AiEntitlementDecision:
    requested_environment = environment or actor.environment

    try:
        normalized_capability = AiCapability(capability)
    except ValueError:
        return AiEntitlementDecision(
            allowed=False,
            reason="unknown_capability",
            capability=capability,
            method=method,
            environment=requested_environment,
        )

    try:
        normalized_method = AiMethod(method)
    except ValueError:
        return AiEntitlementDecision(
            allowed=False,
            reason="unknown_method",
            capability=normalized_capability,
            method=method,
            environment=requested_environment,
        )

    try:
        metadata = get_capability_metadata(normalized_capability)
    except UnknownAiCapabilityError:
        return AiEntitlementDecision(
            allowed=False,
            reason="unknown_capability",
            capability=normalized_capability,
            method=normalized_method,
            environment=requested_environment,
        )

    if AiAccessRole.DISABLED in actor.roles:
        return AiEntitlementDecision(
            allowed=False,
            reason="actor_disabled",
            capability=normalized_capability,
            method=normalized_method,
            environment=requested_environment,
        )

    if normalized_method not in metadata.allowed_methods:
        return AiEntitlementDecision(
            allowed=False,
            reason="method_not_allowed",
            capability=normalized_capability,
            method=normalized_method,
            environment=requested_environment,
        )

    if requested_environment not in metadata.allowed_environments:
        return AiEntitlementDecision(
            allowed=False,
            reason="environment_not_allowed",
            capability=normalized_capability,
            method=normalized_method,
            environment=requested_environment,
        )

    for role in actor.roles:
        allowed_capabilities = _ROLE_CAPABILITY_ALLOWLIST.get(role)
        if allowed_capabilities and normalized_capability in allowed_capabilities:
            return AiEntitlementDecision(
                allowed=True,
                reason="allowed",
                capability=normalized_capability,
                method=normalized_method,
                environment=requested_environment,
                matched_role=role,
            )

    return AiEntitlementDecision(
        allowed=False,
        reason="role_not_allowed",
        capability=normalized_capability,
        method=normalized_method,
        environment=requested_environment,
    )
