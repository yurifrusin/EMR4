# Provider-free disposable PostgreSQL durability restart/unknown-commit stop closeout

Date: 2026-08-11

Result: `stopped_without_pass`

Last accepted durability position: Continuity 243 / Compass 225 (CF-D1)

## Outcome

CF-D2 releases no crash/restart or unknown-commit success.

Immutable attempt 001 failed during fixture setup before any measured scenario
or `SIGKILL`. A setup-only characterization identified successor admission
before predecessor progress. The one bounded mechanical correction permitted
by the frozen plan moved successor admission to the exact R01 and R03 scenario
boundaries and changed no accepted SQL or durability semantics.

Immutable attempt 002 at source
`28cd0ce6639fd831960c57d5289b08f3d36ca3fb` passed all ten fixed setup
preconditions, then stopped before the first scenario record or restart with
minimized failure `scenario/unexpected_terminal_success`. The closed envelope
cannot distinguish the first coordinator terminal mismatch from the following
anchor terminal mismatch. No result is guessed from that ambiguity.

Attempt-002 evidence SHA-256 is
`a7e88a267d597ba41d245df926a66ddb6bd98cf000afc46f269871b48604d6b6`.
Whole-document validation passes. Its exact owned container was removed and
proven absent. `SIGKILL`, provider, product-read, product-command and external-
network counts are all zero.

## Authority stop

The frozen plan's mechanical-correction allowance is consumed. There is no
authority for another characterization, repair, runtime attempt, key-rotation
or retention/purge tranche. AER-0278 and AER-0279 preserve the stops at register
revision 246.

Yuri must choose one of two programme directions:

1. authorise a fresh narrow CF-D2 recovery descendant that first separates
   every measured terminal coordinate, freezes its own review/rerun allowance
   and obtains the review level required by the diagnosed change; or
2. close CF-D2 as unproved and select another independent direction.

All real/product/patient/clinical data, operational database/source or watcher
access, provider use, credentials, reusable runtime, tools/commands,
deployment, production, release, Pages and protected refs remain closed.
