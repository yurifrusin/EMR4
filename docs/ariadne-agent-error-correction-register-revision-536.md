# Ariadne agent error and correction register — revision 536

Date: 2026-08-19

Timestamp: 2026-08-19T07:18:30.9672439+10:00 (Australia/Brisbane)

Status: rejected draft preserved; superseded by revision 537

## Change from revision 535

AER-0622 preserves the rejected revision-535 draft. AER-0620 and AER-0621
shared one attempt ID even though their resource identities differed. The
register requires a shared attempt to have one exact actor/resource envelope.

The correction gives AER-0621 a distinct attempt ID while preserving the two
failures' explicit peer links. Revision 536 then regenerates the committed
pattern report through its exact output path.

## Register state

Revision 536 contains 622 bounded incidents. All are corrected or contained;
none is open. AER-0622 adds recurrence signature
`operator.register_attempt_identity_spanned_distinct_resource_envelopes`.

## Clockwork consequence

The candidate cost is now six failure-induced reruns, a 57.143 percent
reduction against fourteen and one rerun below the frozen maximum. The shared
clockwork itself still rejects all fourteen gauges; the remaining cost arose in
manual construction and legacy-register closeout around it.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.

## Rejection

The deterministic generator rejected this draft because the now-distinct
AER-0620 and AER-0621 attempt identities retained cross-attempt peer links.
Revision 537 derives peer lists from the final attempt grouping and clears both.
