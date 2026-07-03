"""Bounded-domain facade for Bernie turn/freshness evidence helpers.

Re-exports the deterministic freshness-id and staleness-gate helpers from the
legacy flat module. The implementation stays in
``app.services.bernie_turn_evidence`` for this extraction slice.
"""

from app.services.bernie_turn_evidence import (
    SIGNED_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_CONFIRMATION_EVIDENCE_VERSION,
    SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE,
    SignedEvidenceResult,
    StalenessResult,
    StalenessVerdict,
    check_staleness,
    compute_candidate_freshness_id,
    compute_proposal_freshness_id,
    mint_signed_confirmation_evidence,
    mint_session_id,
    mint_turn_id,
    verify_signed_confirmation_evidence,
)

__all__ = [
    "SIGNED_CONFIRMATION_EVIDENCE_PURPOSE",
    "SIGNED_CONFIRMATION_EVIDENCE_VERSION",
    "SIGNED_STAFF_CREATE_CONFIRMATION_EVIDENCE_PURPOSE",
    "SIGNED_UPDATE_CONFIRMATION_EVIDENCE_PURPOSE",
    "SignedEvidenceResult",
    "StalenessResult",
    "StalenessVerdict",
    "check_staleness",
    "compute_candidate_freshness_id",
    "compute_proposal_freshness_id",
    "mint_signed_confirmation_evidence",
    "mint_session_id",
    "mint_turn_id",
    "verify_signed_confirmation_evidence",
]
