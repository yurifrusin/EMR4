# Ariadne agent-error register revision 45

Date: 2026-08-06

Status: durability state-machine implementation recovery pending fresh veto

## AER-0050 opened

AER-0050 preserves the rejected implementation candidate at
`2054500a44fbea21d87ecd65b7e7ed5a83492394`. Its fresh exact-head veto found
that resealing could admit reordered or digest-reused receipts, forged or
reordered audit chains and broken receipt/audit links, and that an incomplete
generation census could self-authorize retention by echoing its own replacement
digests.

Sol invoked the plan's named recovery lease. The pending correction validates
canonical receipt and audit ordering, unique receipt digests and audit ids,
genesis/previous-record audit chaining, exact receipt/audit linkage and a
separately typed backend-authored retention anchor with exact generation
membership. Direct resealed and self-echo adversarial tests now pass locally,
but the incident remains open until a genuinely fresh exact-head veto accepts
the corrected candidate.

Revision 45 contains 50 bounded incidents: 38 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0050 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
