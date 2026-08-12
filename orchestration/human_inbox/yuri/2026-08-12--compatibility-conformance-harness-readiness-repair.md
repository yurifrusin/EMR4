# Compatibility conformance-harness readiness repair

Date: 2026-08-12

## Lay summary

The old appointment compatibility test suite is dependable again. All 311
tests now pass. Nothing in the running application changed: the repair updated
only test clocks, dates and the idempotency headers that the product already
requires.

The practical gain is confidence. We can now use this suite as a clean safety
net while designing the first status transaction kernel, instead of confusing
expired test appointments with real behavior regressions.

## Technical summary

At exact source `48c1821af79f9d22b7c029fdbba8c4f984d239e5`,
the same collection moved from 266 pass / 45 fail to 311/311. The 45 repaired
cases match the frozen census: 33 temporal fixtures and 12 missing proposal
`Idempotency-Key` cases. Two additional structural tests prove the eight-file
boundary, unchanged application tree and unchanged status-code assertion set,
for a source-bound 313/313 run. The canonical 191-test profile also passes.

## Issues resolved

- fixed June/July 2026 appointment values can no longer decay into past-date
  failures;
- same-day morning tests no longer depend on the wall clock during the run;
- successful status/delete proposal fixtures now satisfy the existing
  idempotency contract; and
- deliberately invalid proposal cases retain their original validation
  precedence.

## Deliberately closed

No application behavior, raw route, kernel runtime, schedule fence, observer,
sink, operational database/source/watcher/event, product/patient data,
provider, credential, command/write, deployment, production, release, Pages or
protected ref opened.

## Place in the Raisa direction

This clears a reliability obstruction between the compatibility-consumer
inventory and the first safe transaction-kernel proof. It does not itself move
a route; it makes the evidence used to judge later movement trustworthy.

## Next tranche

Proceeding under standing authority to the provider-free unmounted status
transaction-kernel protocol rehearsal: authored-synthetic transaction schedules
only, with authority-first evaluation, canonical locking, atomic mutation/audit/
receipt behavior and typed loser outcomes.

Yuri's attention is not required.
