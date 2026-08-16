# Delete-confirm HTTP/PostgreSQL integration rehearsal — paired closeout

Date: 2026-08-17

Timestamp: 2026-08-17T09:22:02.9442094+10:00 (Australia/Brisbane)

Status: accepted; sprint engine continuing into the authorised harness review

## Lay summary

Raisa's safe appointment-cancellation path has now been exercised end to end
through its real local HTTP route and a real but disposable PostgreSQL 16
database containing only invented test records. A valid confirmation cancelled
once, recorded the audit and private receipt together, replayed safely after a
simulated lost response, denied revoked and cross-practice requests, and rolled
everything back when a required database completion condition was deliberately
broken. Nothing reached a provider or a product database, and the disposable
database resources were removed afterwards.

This closes the proof gap between the previously accepted route and database
pieces. It does not yet make cancellation a production or visible Reception
One feature.

## Technical summary

At exact reviewed candidate
`fe5dbcb31b06b027285aa84ee3cafb4fbbffb9db`, all 12 DHI scenarios and 135/135
hostile mutations passed. The non-superuser/non-`BYPASSRLS` application role,
forced RLS over eight tables, six selected constraints, four selected triggers,
transaction-local tenant context, two fresh-connection context absence,
public/private byte separation, independent replay stability, zero second and
rollback effects, and exact Docker cleanup all passed. Focused, route/physical,
register, API Spine/Diary and maintenance profiles passed. One clean
eight-command Gemini 3.7 Flash/high veto returned exactly one `pass`.

## Issues

The tranche exposed genuine product integration defects and several workflow
frictions. All were contained and registered through AER-0378. Of particular
interest for the next review are repeated hand-written Git hash mistakes,
validation commands whose shell composition could hide an earlier failure,
wrong pytest conftest/serial-lock envelopes, and an omitted inherited Docker
profile field.

## Deliberately closed

Raw compatibility `DELETE`, real/product/patient/clinical data, reusable
runtime authority, visible UI, concurrency/crash recovery, provider and
credential work, deployment, production, release, Pages and protected refs
remain closed. `docs/branding/` and every unrelated untracked file remain
preserved.

## Place in Raisa

The deterministic backend truth kernel now has local HTTP/PostgreSQL evidence
for proposal, authority recheck, atomic cancellation, audit, private receipt
and safe public projection. Reception One and future adapters can remain thin
clients of that truth rather than owning cancellation semantics themselves.

## Next tranche

Before further product work, review recent Ariadne effectiveness and the new
DeepSeek Harness. Verify its authentication/subscription model, assess
adaptation versus migration, and implement only the highest-leverage repairs.
Current evidence strongly suggests that lack of ChatGPT-subscription access
makes conductor migration unattractive, while some visibility and execution
mechanisms may still be worth borrowing.

Yuri attention required: no.
