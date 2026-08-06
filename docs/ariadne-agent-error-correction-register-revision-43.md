# Ariadne agent-error register revision 43

Date: 2026-08-06

Status: durability state-machine plan recovery active

## AER-0049 recorded

AER-0049 preserves the rejected rehearsal plan at
`e07cb708bd1b36e01b22cae0911ee75829110681`. The first plan correctly froze the
core immutable transition algebra, but it did not prove that retention saw the
complete non-consumed-generation census, proposed deriving a recovery
coordinate from integrity-invalid candidate state, and stopped at static key
interval validation rather than rehearsing the parent architecture's atomic
future-position-fenced rotation and predecessor-key overlap.

The exact-head plan challenge passed 62 serial checks and found no P0 or P2,
but its three P1 findings block implementation. The named Sol recovery lease is
limited to a complete integrity-bound census, a separately trusted recovery
anchor with terminal handling for corrupt state, an exact atomic position-
fenced rotation transition, direct adversarial plan tests and incident
evidence. A fresh no-finding review is required before implementation.

Revision 43 contains 49 bounded incidents: 37 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0049 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
