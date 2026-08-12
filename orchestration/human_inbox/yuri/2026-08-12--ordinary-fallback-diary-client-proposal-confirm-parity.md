# Ordinary/fallback Diary client proposal-confirm parity

Date: 2026-08-12

Result: passed

## Lay summary

The Diary no longer has a hidden escape hatch from the safer two-step booking
flow into the old direct-write routes. All seven such paths are gone. If the
backend cannot provide valid confirmation evidence, the Diary stops and asks
the receptionist to refresh; it does not quietly try an older write route.

This also closes the important race on the second Save click: if a warning was
shown and the appointment slot becomes unavailable before confirmation, the
fresh block wins and nothing is written. A status selected while creating or
editing a booking now goes through its own checked confirmation step. If the
booking itself succeeded but that status step did not, the Diary says so
plainly rather than pretending the whole action rolled back.

The old backend routes have not been removed. They remain available for any
unidentified import, recovery or external consumer until those obligations are
separately understood.

## Technical summary

- exact source: `78cbcca756476fddfd0fda4b4d1241f195b21ab6`;
- result: `raisa_provider_free_ordinary_fallback_diary_client_proposal_confirm_parity_pass`;
- seven inventoried native raw call sites reduced to zero;
- proposal `Idempotency-Key` coverage now includes update, drag/resize, status,
  waiting-area, delete and post-base status requests;
- fresh blocks are evaluated on every proposal response and changed warning
  codes require renewed review;
- create/update follow-up status and delete-404 fallback use signed status
  confirm;
- 8 tranche tests, all 142 Diary browser tests, 242 focused backend/API tests
  and the canonical 191-test fast profile pass; and
- raw compatibility route decorators, handlers, evidence signals and default
  `audit` mode are unchanged.

Deliberately closed: external-consumer conclusions, compatibility-route
retirement, raw-route kernel implementation, create schedule fencing, shadow
enablement, product-data observation, database/source/watcher/event access,
provider calls, deployment, production, release, Pages and protected refs.

Next under standing authority: a provider-free compatibility-consumer and
kernel-convergence admission review. It will inventory remaining repository and
system obligations and freeze the first safe convergence slice without changing
any route.
