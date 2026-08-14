# Ariadne agent error and correction register — revision 278

Date: 2026-08-15

Timestamp: 2026-08-15T04:45:56+10:00 (Australia/Brisbane)

Revision 278 records AER-0317. The register now contains 317 bounded known
incidents, all corrected or contained by an explicit control.

AER-0317 records a closeout-only Continuity contract-evidence mapping error.
Sol's first node referenced product artifacts that were not an admitted
contract evidence category, then failed to link the tranche closeout required
by the committed-reschedule contract. The continuity report gate stopped both
attempts before handover, plan or active-operation-latch acceptance.

No product source, accepted candidate, provider call, protected evidence or
protected ref changed. Sol read the two reused contracts' exact
`required_evidence_types`, linked node tests and the closeout through their
matching categories, reran the idempotent updater and passed all seven
continuity tests. Future updaters must reconcile contract paths with node
evidence categories before their first execution.
