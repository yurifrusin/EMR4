"""Registered-envelope authority policy seam.

Validates that a registered action name in a diary envelope is authored by a
permitted author and is compatible with the envelope type (proposal, suggestion,
confirmation).  Unknown free-string action names pass through without enforcement.

This module is pure domain logic: no routers, DB, providers, or network.
It imports from capabilities.py and action_grammar.py only — no top-level import
cycle with envelopes.py because envelopes.py uses lazy imports to call back here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.services.diary.action_grammar import (
    DIARY_ACTION_GRAMMAR,
    action_verb_for_envelope,
)
from app.services.diary.capabilities import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapabilityTier,
    get_bernie_capability,
)
from app.services.diary.envelopes import DiaryActionAuthor


@dataclass(frozen=True)
class EnvelopeAuthorityDecision:
    """Result of validating an envelope's registered-name authority.

    Fields
    ------
    action_registered:
        True when the action_name maps to a known grammar verb whose
        capability_name resolves in BERNIE_CAPABILITY_REGISTRY.
    author_authorized:
        True when the author is in the capability's allowed_authors list.
        None when action_registered is False.
    tier_compatible:
        True when the envelope type is compatible with the capability tier.
        None when action_registered is False.
    reason:
        Human-readable summary of the decision or rejection cause.
    """

    action_registered: bool
    author_authorized: bool | None
    tier_compatible: bool | None
    reason: str


def validate_envelope_authority(
    envelope_type: str,
    action_name: str,
    author: DiaryActionAuthor,
) -> EnvelopeAuthorityDecision:
    """Validate a registered action name's author and envelope-type compatibility.

    Unknown action names (not in the grammar vocabulary or not linked to a
    registered capability) pass through without enforcement.

    Args:
        envelope_type: The envelope type literal e.g. ``"proposal"``,
            ``"suggestion"``, ``"confirmation"``, ``"intent"``.
        action_name: The free-string action_name from the envelope.
        author: The DiaryActionAuthor of the envelope.

    Returns:
        EnvelopeAuthorityDecision summarising the validation result.

    Raises:
        ValueError: When a registered action has an unauthorised author or an
            incompatible envelope-type / capability-tier combination.
    """
    # Step 1: resolve action_name to a grammar verb
    verb = action_verb_for_envelope(action_name)
    if verb is None:
        return EnvelopeAuthorityDecision(
            action_registered=False,
            author_authorized=None,
            tier_compatible=None,
            reason=f"Unknown action_name '{action_name}': not found in grammar vocabulary",
        )

    # Step 2: check whether the verb has a registered capability_name
    desc = DIARY_ACTION_GRAMMAR[verb]
    if desc.capability_name is None:
        return EnvelopeAuthorityDecision(
            action_registered=False,
            author_authorized=None,
            tier_compatible=None,
            reason=f"Verb '{verb.value}' has no registered capability_name",
        )

    # Step 3: resolve the capability in the registry
    capability = get_bernie_capability(desc.capability_name)
    if capability is None:
        return EnvelopeAuthorityDecision(
            action_registered=False,
            author_authorized=None,
            tier_compatible=None,
            reason=(
                f"capability_name '{desc.capability_name}' for verb '{verb.value}' "
                "not found in BERNIE_CAPABILITY_REGISTRY"
            ),
        )

    # Step 4: validate author against allowed_authors
    if author not in capability.allowed_authors:
        raise ValueError(
            f"Author '{author.value}' is not permitted for registered action "
            f"'{action_name}' (capability '{capability.name}').  "
            f"Allowed authors: {[a.value for a in capability.allowed_authors]}."
        )

    # Step 5: validate envelope type against capability tier
    envelope_type_lower = envelope_type.lower()
    tier = capability.tier

    if envelope_type_lower == "proposal":
        if tier is not BernieCapabilityTier.propose:
            raise ValueError(
                f"Registered action '{action_name}' (capability '{capability.name}', "
                f"tier '{tier.value}') is not propose-tier and cannot be used in a "
                "'proposal' envelope."
            )
    elif envelope_type_lower == "suggestion":
        if tier not in (BernieCapabilityTier.read_only, BernieCapabilityTier.meta):
            raise ValueError(
                f"Registered action '{action_name}' (capability '{capability.name}', "
                f"tier '{tier.value}') is not read-only or meta and cannot be used "
                "in a 'suggestion' envelope."
            )
    elif envelope_type_lower == "confirmation":
        if tier is not BernieCapabilityTier.confirm:
            raise ValueError(
                f"Registered action '{action_name}' (capability '{capability.name}', "
                f"tier '{tier.value}') is not confirm-tier and cannot be used in a "
                "'confirmation' envelope."
            )
    # intent and other envelope types have no tier restriction

    return EnvelopeAuthorityDecision(
        action_registered=True,
        author_authorized=True,
        tier_compatible=True,
        reason=(
            f"Authorized: action '{action_name}' (capability '{capability.name}', "
            f"tier '{tier.value}') is compatible with '{envelope_type}' envelope "
            f"authored by '{author.value}'."
        ),
    )


__all__ = [
    "EnvelopeAuthorityDecision",
    "validate_envelope_authority",
]
