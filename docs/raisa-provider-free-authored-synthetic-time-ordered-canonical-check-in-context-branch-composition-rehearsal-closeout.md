# Raisa provider-free authored-synthetic time-ordered canonical check-in-context branch composition rehearsal — closeout

Date: 2026-08-24

Timestamp: 2026-08-24T16:22:26.0503913+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

Exact reviewed candidate: `203f297d610ee30ce6c9d50243999ed4a8041df4`

## Lay outcome

The check-in adapter now has a compact set of synthetic stories in which the
world changes between proposal and action. Thirty cases do the work of a
120-case full grid while still pairing every kind of appointment/waiting-area
change with every authority/evidence change and every execution outcome.

This shows, for example, that an earlier idempotency replay wins before a later
authority or appointment change is consulted; that revoked authority, stale
proposals, invalid evidence and changed waiting-area topology stop at their
proper boundaries; and that rollback or uncertain commit/readback conditions
never become a false success.

The historical trove was not read. It no longer supplies these stories: they
are deliberately authored synthetic cases based on the gap identified by the
preceding review.

## Technical outcome

- exact decision
  `accepted_provider_free_authored_synthetic_pairwise_composition_rehearsal`;
- 30 scenarios at the mathematical lower bound, covering 20 source/authority,
  30 source/outcome and 24 authority/outcome pairs (74 total);
- all 16 frozen unmasked witness checks pass;
- grouped idempotency coverage includes three conflict and two in-progress
  cells;
- exact replay returns before lock/readback; precommit failure restores the
  transaction-entry snapshot; commit/readback uncertainty returns
  `committed: null` with no receipt;
- 72 hostile contract mutations rejected;
- 14 exact-HEAD focused and 264 combined adapter, default-off route, API Spine,
  clockwork, predecessor and handover test nodes passed;
- Ruff, compileall, generated-output idempotence and `git diff --check` pass;
  and
- the adapter Git blob remains exact
  `6955dec2e31e14c0ae4847acba22f9fb0087715b`.

The API Spine boundary remains unchanged: confirmation, practice-scoped
authority, idempotency, audit/event planning and readback stay backend-owned;
the rehearsal's committed-event observation never becomes an actuator.

One bounded register incident records four contained workflow corrections:
an over-broad privacy substring, an over-broad serial-receipt evidence-root
list, a yielded pytest handle that was not retained and a descriptive incident
state outside the clockwork's closed vocabulary. The corrected controls all
pass and did not change the exact committed candidate.

## Continuing boundary

The next read-only tranche may compare this in-memory temporal evidence with
already tracked default-off route, disposable PostgreSQL rollback/unknown-
commit and runtime role/tenant evidence to identify one honest incremental
operational gap. It may not execute a route or database or reopen historical
data.

No product, adapter, schema, route, database, client, configuration,
ordinary-practice activation, provider/model/network, production, deployment,
release, Pages, protected evidence or protected-ref movement is opened.
Local/origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.
