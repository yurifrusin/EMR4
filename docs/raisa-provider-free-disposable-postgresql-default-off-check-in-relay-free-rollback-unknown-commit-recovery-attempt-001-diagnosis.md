# Relay-free check-in rollback/unknown-commit recovery attempt 001 diagnosis

Date: 2026-08-19

Status: `failed_closed_cleanup_recovered_no_rerun`

Execution source: `5adbf56b886cb1107dc8c18723c791e4e566c2fd`

## Exact result

The one execution authorised by the frozen plan failed before PostgreSQL
started. The internal network passed ownership/profile admission. The server
container was created but did not pass `_create_server` profile admission, so
the lifecycle contains no server-admitted, credential-delivery, readiness,
role, SQL, transaction or readback stage.

No credential was delivered, no database process started, no product or
ordinary-practice surface was touched, no success was released and retry count
is zero.

## Cleanup recovery

The helper raised before returning the newly created server ID to the outer
lifecycle. Outer cleanup therefore treated the server as absent, removed the
captured empty network and reported one matching owned resource. The remaining
object was still in Docker `Created` state.

Read-only inspection found exactly one matching object. Before deletion, the
full 64-character ID shape, exact name prefix, exact cached image, harness
label, 32-character ownership nonce, never-started state, zero published ports
and zero bind mounts were verified. Only that exact full ID was removed.
Post-recovery matching container and network counts are both zero.

The sanitized recovery record intentionally excludes the Docker ID, name and
nonce. The immutable attempt failure retains `cleanup_incomplete`; the paired
recovery record proves the later exact cleanup and does not rewrite history.

## Control defects

1. `_create_server` acquired an owned Docker object before the caller could
   register the ID. A subsequent profile rejection therefore lost cleanup
   ownership at the outer level.
2. Final cleanup replaced the earlier primary error with
   `cleanup/exact_cleanup_unverified`, so the exact failed profile predicate was
   not retained in the sanitized artifact.
3. The new predicate indexed the network attachment by expected network name.
   The accepted predecessor predicate instead requires exactly one attached
   network and compares its `NetworkID`. The exact failed leaf was not retained,
   so name-key fragility is a bounded diagnosis, not asserted as proven root
   cause.

## Narrow repair

Without another Docker or database execution:

- reduce network admission to exactly one attachment whose `NetworkID` matches
  the captured ID;
- derive closed per-predicate booleans so a future mismatch has a sanitized
  coordinate;
- make each acquisition helper clean an exactly owned object before raising if
  it cannot return ownership to the caller;
- retain the primary failure coordinate and report cleanup as a separate
  disposition; and
- add pure fixtures for name-key independence, pre-return ownership cleanup and
  primary-error preservation.

Attempt 001 is consumed. The frozen plan authorises no rerun. A later occupied
proof requires a newly frozen execution authority after this repair has passed
deterministic and independent review gates.
