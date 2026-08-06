# Ariadne agent-error register revision 41

Date: 2026-08-06

Status: source-specific durability schema recovery active

## AER-0048 recorded

AER-0048 preserves the rejected source-specific durability architecture at
`92cf76b17bbab276df701ee1e0af0da77e1768a9`. Its prose and canonical contract
described the correct payload-free, practice-bound and atomic design, but the
Draft 2020-12 schema treated five safety-critical tuples as arbitrary bounded
string arrays. The focused tests asserted required subsets and scalar ceilings,
so prohibited field addition or tenancy/atomic-member substitution could still
validate.

The fresh exact-head veto found no P0 or P2 and passed all 83 checks, but its P1
blocks acceptance. The named Sol recovery lease permits only exact schema tuple
closure, direct append/remove/replace/reorder adversarial tests and incident
evidence. A fresh no-finding veto is required before correction or closeout.

Revision 41 contains 48 bounded incidents: 36 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0048 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
