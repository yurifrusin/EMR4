# Ariadne agent error and correction register revision 121

Date: 2026-08-09

Status: bounded review-control correction candidate

Revision 121 adds AER-0144 and AER-0145 and brings the register to 145 bounded
incidents with zero open incidents.

## AER-0144 — review packet carried three mistyped full identifiers

The first explicit-`xmin`-alias veto packet copied the correct prefixes but
mistyped the full structural-contract SHA and two disposable-container cleanup
IDs. The reviewed candidate itself remained correct and the protected refs did
not move, but the packet's exact decision rule could not support acceptance.

Sol's mandatory post-review reconciliation detected the mismatch before any
database rehearsal. The packet and resulting receipt remain preserved as
negative evidence. Their successor must mechanically copy the three full
values from the candidate JSON; prefix agreement is never sufficient for a
cryptographic or exact-cleanup claim.

## AER-0145 — verifier passed despite packet/candidate contradiction

The first Gemini receipt reported the candidate's correct full identifiers,
yet returned terminal `pass` even though those values contradicted the packet's
frozen expectations. Because the packet explicitly required `fail` for a wrong
evidence hash or coordinate, the decision was internally inadmissible.

Sol rejected the pass. A distinct fresh Antigravity project must review a
corrected exact-head packet before the behavior rehearsal can become eligible.
Verifier acceptance continues to require machine reconciliation against both
the candidate and the review packet; agreement with one cannot cure a
contradiction with the other.
