# Ariadne agent error and correction register — revision 535

Date: 2026-08-19

Timestamp: 2026-08-19T07:18:30.9672439+10:00 (Australia/Brisbane)

Status: rejected draft preserved; superseded by revision 536

## Change from revision 534

AER-0620 and AER-0621 preserve the complete register suite's two failures in
one execution. The register command omitted its explicit `--output` argument,
so validation succeeded without rewriting the committed pattern report. A test
append also split the preceding AER-0615 function and stranded its remaining
assertions under a scope with no `incident` variable.

The correction explicitly generates the committed pattern report, restores the
function boundary, updates all direct counts and then reruns the complete file.

## Register state

Revision 535 contains 621 bounded incidents. All are corrected or contained;
none is open. The two new recurrence signatures distinguish omitted generator
output from a split test-function boundary.

## Clockwork consequence

This one failed suite advances the latch-derived candidate cost from four to
five reruns, a 64.286 percent reduction against fourteen. It remains within the
seven-rerun threshold, while showing that the legacy register projection is
still outside the new shared clock and still costly.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.

## Rejection

The deterministic generator rejected this draft because AER-0620 and AER-0621
shared an attempt ID while naming distinct resource identities. Revision 536
preserves the shared verification invocation through peer links while assigning
distinct actor envelopes distinct attempt IDs.
