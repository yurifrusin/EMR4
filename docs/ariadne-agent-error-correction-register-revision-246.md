# Ariadne agent error and correction register — revision 246

Date: 2026-08-11

Revision 246 records and contains AER-0279. The register now contains 279
bounded known incidents.

## AER-0279 — CF-D2 attempt 002 stopped before its first restart

Attempt 002 passed all ten fixed authored-synthetic fixture preconditions, then
stopped before the first scenario record or `SIGKILL` with the minimized code
`scenario/unexpected_terminal_success`. Whole-document validation and exact
owned-container cleanup passed; provider, product-read, product-command and
external-network counters were zero.

The failure envelope does not distinguish the first coordinator terminal
mismatch from the following recovery-anchor terminal mismatch. Attempt 001 and
the plan's one mechanical recovery allowance are already consumed. No further
diagnostic runtime, repair or retry is inferred.

Attempt 002 remains immutable. CF-D2 releases no crash/restart or unknown-
commit success, and the dependent key-rotation plus retention/purge rehearsal
does not start. Yuri must choose whether to authorise a new narrowly reviewed
CF-D2 recovery descendant or close CF-D2 as unproved and select another
independent direction.
