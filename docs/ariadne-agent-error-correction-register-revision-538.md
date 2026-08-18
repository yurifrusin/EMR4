# Ariadne agent error and correction register — revision 538

Date: 2026-08-19

Timestamp: 2026-08-19T07:18:30.9672439+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 537

AER-0624 preserves the causally invalid seven-rerun generation. Its manifest
changed as verification counters accrued, but its acknowledged event tip was
identical to the earlier two-rerun generation because those counters lived only
in a readings projection. The paperwork advanced while the clock hand did not.

The correction binds the digest of all workflow retry counters into the event
payload and derives attempt ordinal from their sum. An exact hostile test now
proves that changing a counter without re-hashing the tick fails closed.

## Register state

Revision 538 contains 624 bounded incidents. All are corrected or contained;
none is open. AER-0624 adds recurrence signature
`repository.clockwork_retry_projection_not_bound_into_causal_tick`.

## Efficacy consequence

The correction creates the eighth failure-induced rerun. The rehearsal therefore
fails its frozen maximum of seven: 42.857 percent reduction against fourteen,
not the required 50 percent. The corrected engine remains useful evidence, but
this tranche is not accepted and no exact-candidate Gemini veto is dispatched.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
