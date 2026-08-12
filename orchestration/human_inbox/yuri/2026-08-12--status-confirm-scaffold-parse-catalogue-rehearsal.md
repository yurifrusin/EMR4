# Status-confirm PostgreSQL scaffold rehearsal — lay and technical closeout

Date: 2026-08-12

Result: **passed**

## Lay summary

The new appointment-status safety structure has now been accepted by a real,
temporary PostgreSQL 16 server—not merely by source inspection. In a completely
isolated synthetic database, PostgreSQL installed the intended version counter,
private completion receipt and automatic increment rule. It rejected invalid
versions and malformed receipts, admitted the intended shapes, rolled every
probe back and was then removed completely.

This still changes nothing in the live application. No route was mounted, no
real appointment was read or written, and no product, patient, provider or
credential data was used.

## Technical summary

- exact source: `bccc64f87eb0c1ae755b642fb6c4eb082298051d`
- result: `raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal_pass`
- environment: cached `postgres:16-bookworm`, `--network none`, no host port,
  tmpfs storage, no bind/named volume, fixed limits and exact-ID cleanup
- admission: exact Alembic range, head `w2x3y4z5a6b7`, six columns, three
  constraints, one trigger function and one enabled trigger
- probes: 9/9 passed and rolled back; expected rejection states were `23514`
  and `22003`
- contract: eight bound sources and 80/80 hostile mutations
- tests: 13 focused plus 35 current scaffold/API-contract checks passed; one
  historical Sprint 138 assertion is stale at the unchanged baseline and was
  neither relied on nor changed

The next planned tranche is the equally isolated behavior/transaction
rehearsal: current-authority and lock order, atomic appointment/audit/receipt
commit, idempotent replay, response-loss recovery and outer rollback. Routes,
real data and production remain closed.
