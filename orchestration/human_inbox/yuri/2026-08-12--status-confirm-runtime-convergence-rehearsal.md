# Status-confirm runtime convergence rehearsal

Date: 2026-08-12

Result: `raisa_provider_free_unmounted_status_confirm_runtime_convergence_rehearsal_pass`

Source: `a1629f2441e2bdb350d00c6d6016e94123ff0d8d`

## Lay summary

The proposed safety mechanism has now been made to behave like a small model of
the real command path, without touching the application or a database. It
handled 24 cases covering stale confirmation, changed authority, missing
appointments, warning changes, concurrent attempts, partial failures and a
lost response followed by retry.

Only the legitimate winner received the ribbon: every accepted effect produced
one appointment change, one attributable audit and one reusable receipt. A
loser, stale caller or revoked caller could neither repeat the change nor learn
a stored result it was no longer allowed to see. All 88 deliberate corruptions
of the contract were rejected.

One old Sprint 138 test was found to expect that the update route still lacked
an idempotency header. Later accepted work added that header, so the old
assertion is stale. I preserved both the test and route and recorded the issue;
the final 139-test contract/continuity packet passes.

## Technical summary

The pure state machine reproduces all 24 frozen participant outcomes and exact
final status/version, mutation, audit, receipt and disclosure counts. It proves
the accepted decision order, authority-before-idempotency rule, exact warning
and evidence equality, terminal deferral, three rollback points, same/different
digest races, post-commit `delivery_unknown` and digest-identical stored replay.

The focused suite passes 15/15, the final bounded
lineage/continuity/Compass/API/baton packet passes 139/139, and 88/88 hostile
mutations fail closed. No application or database module was imported.

## Deliberately closed

Physical state-version and receipt storage, migration/backfill, ORM/service
wiring, real PostgreSQL locks and concurrency, mounted route behavior,
provider/ADC use, product or patient data, watchers/events, commands,
deployment, production, release, Pages and protected refs remain closed.

## Place in Raisa and next work

This moves the source-owned-truth direction from architecture into executable
but still unmounted evidence. The next tranche is a provider-free read-only
physical representability review of the exact model, migration and service
surfaces needed for the semantic state version, private receipt and ordered
lock boundary. It cannot edit or execute them.

Yuri attention required: `no`.
