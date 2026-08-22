# Check-in relay-free recovery attempt 008

Date: 2026-08-23

Timestamp: 2026-08-23T07:19:39.9791037+10:00 (Australia/Brisbane)

Yuri attention required: `no`

## Lay summary

This is the clearest evidence yet that we are moving inward toward the goal
rather than merely enlarging the clockwork. The machinery made us satisfy nine
named conditions before the database lever became available. Once it did, the
single permitted rehearsal passed in 7.4 seconds. There was no retry, resume or
fallback.

The rehearsal deliberately rolled one check-in transaction back and observed
nothing persisted. It then committed a different one while deliberately losing
the caller's final response. Instead of guessing or retrying, a fresh restricted
read observed exactly one matching effect, receipt and audit entry, no
duplicate and no visibility into the other synthetic practice. Everything
temporary was removed.

The workflow was not magically error-free. One earlier publication-phase test
needed a phase-aware expectation, one long test invocation's session handle was
not retained and had to be recaptured in smaller packets, and one PowerShell
guard had a colon-interpolation typo. All three are being registered. The
important difference is that none spent a database run: the only occupied run
passed once.

## Technical summary

Exact occupied source is
`9f37ede79a915172e449c1f2d19bdba3eb592b44`; terminal commit is
`0e50f7f48d9c8622341a1679db507de78b1260a5`. The closed envelope records one
invocation, zero retry/resume/fallback, no ambiguous success, no ordinary
admission, no product record, and preserved `cleanup_verified`.

P06-P14 passed. The repaired base matched all 67 prospective/runtime paths and
rejected 66 hostile forbidden-field mutations before Docker. Contract,
manifest, state and classifier hostile gates passed. The task branch was
origin-aligned, the exact cached PostgreSQL image matched, zero owned resources
existed before and after, and the checkpoint published with zero drift or dual
ownership. API-Spine and route-contract review passed 52/52 with no source
change.

## Deliberately closed

Dedicated check-in remains default-off. No ordinary-practice enablement, API or
client change, generic-status `Arrived`, waiting-area movement, product/patient/
clinical data, provider/worker, reusable runtime, production, deployment,
release, Pages or protected ref moved. `docs/branding/` and all unrelated
untracked files remain preserved.

## Place in Raisa's direction

This closes the bounded transaction-evidence gap behind a future ordinary
check-in decision. It demonstrates the backend-owned pattern Raisa needs:
uncertain transport never becomes authority; current source truth,
idempotency, audit, tenant policy and exact readback decide the outcome.

## Next

The engine is continuing to a provider-free read-only twelve-dimension
convergence review. That review may mark the transaction dimension satisfied,
but it must retain the separate operational environment/secret-posture gap and
cannot enable ordinary practice. No decision from Yuri is needed.
