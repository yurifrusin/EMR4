"""Bounded-domain facade for Bernie turn/freshness evidence helpers.

Re-exports the deterministic freshness-id and staleness-gate helpers from the
legacy flat module. The implementation stays in
``app.services.bernie_turn_evidence`` for this extraction slice.
"""

from app.services.bernie_turn_evidence import (
    StalenessResult,
    StalenessVerdict,
    check_staleness,
    compute_candidate_freshness_id,
    compute_proposal_freshness_id,
    mint_session_id,
    mint_turn_id,
)

__all__ = [
    "StalenessResult",
    "StalenessVerdict",
    "check_staleness",
    "compute_candidate_freshness_id",
    "compute_proposal_freshness_id",
    "mint_session_id",
    "mint_turn_id",
]
