"""Bounded-domain facade for the deterministic Bernie slot-search normalizer.

Re-exports the pure normalizer from the legacy flat module. The implementation
stays in ``app.services.bernie_slot_normalizer`` for this extraction slice.
"""

from app.services.bernie_slot_normalizer import normalize_slot_search_command

__all__ = ["normalize_slot_search_command"]
