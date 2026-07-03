"""Compatibility facade for diary-domain capability catalog contracts."""

from app.services.diary.capabilities import (
    BERNIE_CAPABILITY_REGISTRY,
    BernieCapability,
    BernieCapabilityTier,
    get_bernie_capability,
)

__all__ = [
    "BernieCapability",
    "BernieCapabilityTier",
    "BERNIE_CAPABILITY_REGISTRY",
    "get_bernie_capability",
]
