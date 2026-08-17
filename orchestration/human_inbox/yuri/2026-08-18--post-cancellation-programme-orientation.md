# Post-cancellation programme orientation — lay and technical summary

Date: 2026-08-18

Timestamp: 2026-08-18T04:57:36+10:00 (Australia/Brisbane)

Status: accepted

## Lay summary

Raisa's two first-party Diary views now agree on booking, rescheduling, status
and cancellation through the same truth-owning backend mechanisms. The next
useful question is what “check in” should mean.

Today the ordinary Diary and Reception One can mark an appointment `Arrived`.
There is also a more specialized, switched-off check-in path that can place the
patient into a waiting area at the same time. Meanwhile, an older internal
action map still says dedicated check-in is not implemented. Building another
button before reconciling those meanings could give one human phrase two
different authoritative effects.

The next tranche will therefore compare these paths and decide their proper
relationship before changing the product. No choice has yet been made between
using the specialized path, formally binding check-in to general status, or
keeping both for clearly non-overlapping purposes.

## Technical summary

The accepted repository-static matrix compares create, update, status,
waiting-area, delete/cancel, A5.1 check-in and link-patient families. It selects
`raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review`.

The successor will compare exact request, confirmation, authority, freshness,
idempotency, mutation, audit, event, receipt and readback contracts; separate
reusable deterministic kernel from A5.1-only admission; and resolve the static
`{appointment_id}` versus FastAPI `{appointment_id:uuid}` contract spelling.
It may inspect but not edit product, API Spine, Diary, migration or product-test
source.

Eleven new checks, 107 existing API/static checks, the 200-test canonical fast
profile and one fresh seven-command Gemini 3.7 Flash/high veto pass. The six
unchanged endpoint-coverage failures are retained negative evidence for the
next review, not candidate regressions. No runtime, database, provider,
product/patient/clinical data, deployment, release, Pages or protected ref was
opened.
