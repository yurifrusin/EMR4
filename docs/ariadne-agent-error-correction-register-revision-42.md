# Ariadne agent-error register revision 42

Date: 2026-08-06

Status: source-specific durability schema recovery accepted by fresh veto

## AER-0048 corrected

AER-0048 preserves the rejected source-specific durability architecture at
`92cf76b17bbab276df701ee1e0af0da77e1768a9`, whose generic bounded string-array
schema admitted safety-critical list substitution despite passing canonical
tests.

Under the named Sol recovery lease, all seven payload, audit, producer,
checkpoint and atomic-transaction tuples became exact ordered schema constants.
Focused tests now mutate append, removal, replacement and ordering for every
tuple. A genuinely fresh exact-head review at
`14e8d3257b9531601260bef094c73e08a9c7b92d` rejected all 28 independent
mutations, passed 160 serial checks and found no P0-P2 issue. AER-0048 therefore
closes only through the recovery lease plus that fresh veto.

Revision 42 contains 48 bounded incidents: 36 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
No incident remains open. Counts remain workflow-improvement signals and do not
establish model, provider, transport or role causation.
