# Threat-model delta: relay-free profile call-site and pre-registry cleanup conformance repair

Date: 2026-08-19

Timestamp: 2026-08-19T23:56:00+10:00 (Australia/Brisbane)

Status: `frozen`

This provider-free deterministic repair closes the two invocation and cleanup
gaps exposed by consumed attempt 003. It authorises no Docker or database
execution and grants no product or ordinary-practice authority.

## Assets and trust boundaries

- Immutable attempts 001 through 003 and Created-state evidence.
- Exact corrected network, credential and ownership-nonce semantics.
- Two real creation-to-profile call sites.
- One shared exact-ownership cleanup helper.
- Mocked deterministic Docker command and inspect boundaries only.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A predicate signature changes without updating real callers | AST plus mocked real-call tests require the exact captured `network_name` and every other closed keyword at both call sites. |
| An exception after create strands an object before registry admission | Both creation functions wrap the complete post-create admission interval and invoke the shared exact-ownership cleanup before propagating. |
| Cleanup removes a foreign object | One inspected row, full resolved ID, candidate relation, exact generated name, image, harness label, nonce, Created state and not-running state are mandatory. |
| Abbreviated Docker ID is treated as exact identity | The listing/candidate value may locate inspection only; removal uses the inspected full 64-character ID after exact relation validation. |
| Cleanup absence is assumed from a command return | A post-removal inspect must fail for the exact full ID; otherwise cleanup is unverified. |
| Cleanup hides the primary failure | Known closed failures are preserved after verified cleanup; unknown exceptions receive a distinct cleaned coordinate; cleanup uncertainty dominates both. |
| Mock tests accidentally perform occupied work | Docker execution is monkeypatched and source/command inspection denies process, credential, PostgreSQL and database paths in this tranche. |
| Attempt 003 is silently repaired or rerun | Its exact source, hashes, counts and artifacts are bound and immutable; this operation has no execution authority. |
| The repair broadens containment or product behavior | Existing predicate, transaction, route, API, configuration and client bytes remain unchanged outside the exact allowlist. |

## Residual limits

The repair proves deterministic invocation compatibility and cleanup behavior
under closed fault injection. It does not prove Docker runtime behavior,
PostgreSQL startup, credential delivery, transaction rollback, unknown-response
readback, concurrency, production safety or ordinary-practice readiness.

## Closed boundaries

No Docker object, container start/attach, credential, PostgreSQL, SQL, database,
provider call before a deterministic exact candidate, product/API/config/client
change, product/patient/clinical/protected data, ordinary-practice enablement,
deployment, release, Pages or protected-ref movement is authorised.
