# Status-confirm product-adapter rehearsal — lay and technical closeout

Date: 2026-08-13

Timestamp: 2026-08-13T10:44:05+10:00 (Australia/Brisbane)

## Lay summary

The missing bridge between authenticated application state and the already
proved safe database-command seam now works in a sealed rehearsal. It checks
that the person still has authority, allows only the intended appointment-status
action, rechecks the appointment after waiting, and keeps the appointment
change, audit trail and replay receipt tied together.

The rehearsal also caught and repaired a subtle lost-response problem. The
existing signed proposal did not remember the appointment's database version.
Without that, retrying after a successful but unseen response could look like a
different request. A small server-signed version token now preserves the
original generation without trusting the browser or weakening the fresh lock
check.

What became possible is a concrete application adapter ready for real disposable
database integration testing. What remains deliberately closed is the actual
HTTP route, product data, production runtime and UI behavior.

## Technical summary

Exact result:
`raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal_pass`
at source `b728b903c99fa35f231df04ba68263533261121a`.

The adapter provides HMAC bearer minimisation, exact status-union admission,
transaction-local practice-context restoration, two fresh actor checks, signed
proposal snapshot verification, proposal-version HMAC binding, locked
freshness/warning/terminal reconstruction and one status/audit/adjacent-version
effect feeding the accepted canonical private-receipt composition.

All thirteen frozen hashes, 84/84 hostile mutations, 118 focused checks and the
193-test fast profile pass. There were zero route calls, database connections,
provider/network calls or product/patient records. The existing route is
unchanged and does not import the adapter.

## Place in the programme and next work

This is the application layer between the Context Fabric/source-truth policy and
the already accepted physical command/receipt seam. The next tranche is a
provider-free disposable PostgreSQL-16 rehearsal of this exact adapter, still
off-route. If that passes, route wiring/mounting is the final core
infrastructure gate before the work can return to visible Diary UI behavior.

Yuri's attention is not required; standing uninterrupted-development authority
applies.
