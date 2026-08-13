# Provider-free disposable PostgreSQL status-confirm product-adapter integration rehearsal closeout

Date: 2026-08-13

Timestamp: 2026-08-13T11:39:46+10:00 (Australia/Brisbane)

Result: `raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal_pass`

Source commit: `553d38c37af86ceefc7b4315b8eaa171d405ab95`

## Decision

The exact accepted unmounted status-confirm product adapter now passes against
one owned disposable PostgreSQL 16 server under a restricted non-superuser,
non-`BYPASSRLS` application role. The result closes the database-integration
gap identified by the route-mounting readiness review. Route convergence itself
remains closed.

The adapter now establishes transaction-local practice context in the physical
seam's exact-practice callback before the appointment lock and restores it
before both current-actor reads. It also normalizes the already-admitted
canonical text target to UUID only at the physical transaction boundary. The
signed proposal, admitted request digest and stored response bytes do not
change.

## PostgreSQL evidence

One cached `postgres:16-bookworm` container ran on an owned Docker internal
network with no published port, tmpfs-only data, no mount, one CPU, 512 MiB,
128 processes and no restart policy. The host used only the accepted fixed
IPv4-loopback relay to the captured exact container ID. Every bounded attempt
proved exact container and network absence in `finally`.

The disposable application role had exact table privileges plus column-only
`UPDATE(id)` on practices, which PostgreSQL requires for the existing `FOR
SHARE` practice lock. Forced RLS protected appointments, users, practitioners,
idempotency receipts and audit rows. Practices remained exact-ID readable so
the transaction could establish its tenant setting before reaching any
practice-scoped table.

All twelve frozen scenarios pass:

1. one Booked-to-Confirmed mutation, audit and v1 receipt commit at the
   adjacent database-owned version;
2. response-loss retry releases byte-identical stored bytes with no second
   effect;
3. a different tenant has zero visibility across all five RLS tables;
4. an inactive actor stops before a claim;
5. revocation between the two checks rolls back the claim and simulated
   revocation;
6. practice/target mismatch returns the closed unavailable outcome;
7. stale proposal generation stops and rolls back;
8. tampered binding stops before command-session construction;
9. failed practitioner projection rolls back mutation, audit and receipt;
10. a terminal transition requires the exact warning and clears the waiting
    area atomically;
11. wrong current database role stops without an effect; and
12. the transaction-local tenant setting is absent outside both commit and
    rollback boundaries on the pooled connection.

## Recovery findings

The bounded attempts produced three useful integration corrections:

- the catalogue checker initially named the accepted adjacent-version trigger
  incorrectly; the server had installed the correct trigger throughout;
- PostgreSQL requires an UPDATE privilege to acquire the practice row lock, so
  the disposable role received only column-level `UPDATE(id)`; and
- canonical JSON target text and ORM UUID identity compared unequal on replay,
  so the adapter now performs a single validated UUID conversion at the
  physical boundary.

A final unpublished in-memory pass was withheld because the new evidence JSON
schema had a missing closing brace. The corrected schema and a fully fresh run
then released the accepted evidence. No failed attempt left a container or
network behind.

## Verification

- 104 of 104 hostile contract mutations fail closed;
- all 12 disposable PostgreSQL scenarios pass;
- 34 direct adapter/plan/integration tests pass;
- 112 current-lineage focused status-confirm, latch and baton tests pass;
- the canonical fast profile passes Ruff, maintained-source compilation over
  209 files, 193 tests, Diary JavaScript syntax and Git whitespace; and
- exact source-commit inspection and `git diff --check` pass.

Two deliberately historical continuity assertions for the earlier bare
behavior rehearsal still claim that old node is current. They were already
superseded by the accepted product-adapter node, are excluded from the
canonical maintained set, and were not rewritten inside this frozen source
boundary.

No external worker or provider was used. Durable evidence contains no SQL,
connection URL, password, bearer, response body, runtime ID, unrestricted row,
patient/product value or real-person data.

## Narrowest next tranche

Freeze one provider-free, authored-synthetic route-convergence tranche for the
existing authenticated `/appointments/proposals/status-confirm` family. It
must replace the legacy route-local write path with the accepted product
adapter, carry the opaque proposal-version binding without granting client
authority, preserve the status-only boundary, return exact stored replay bytes
and prove the canonical API alias decision with disposable local PostgreSQL.

That next tranche may edit and locally exercise the route and its exact schema,
dependency and API-contract surfaces. It may use only authored-synthetic
fixtures in an owned disposable database. It grants no patient/clinical or
operational product data, provider, credential/IAM change, external network,
deployment, production, release, Pages or protected-ref movement. Diary UI
wiring remains the next dependency-satisfied direction after route convergence.
