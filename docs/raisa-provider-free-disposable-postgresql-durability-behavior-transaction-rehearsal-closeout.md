# Provider-free disposable PostgreSQL durability behavior/transaction rehearsal closeout

Date: 2026-08-08

Result:
`raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_pass`

Accepted independently reviewed evidence source HEAD:
`f3383dc4099b4ee590014bea62dddb146f5d2a16`

Immutable pass evidence SHA-256:
`26c6dec802e46dec055c1c42aecc97df9942180014fc9fa410f96e1305798200`

## Accepted result

The first server-executed Context Fabric durability behavior experiment now
passes all twenty frozen authored-synthetic scenarios in one newly owned,
networkless, mountless, portless, tmpfs-backed local PostgreSQL 16 container.
The exact category reconciliation is six entry-point, four idempotency, three
RLS/privilege, four trigger and three rollback scenarios. Every expected
outcome, SQLSTATE, bounded readback and forbidden-effect check passed in the
contract's original order.

The result binds the accepted 424-statement inert SQL at SHA-256
`dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`,
render manifest
`2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`
and canonical behavior contract
`43b25bd7509439f069643dcb0ae8e62e27002834fe9903d84e7478486b452615`.

The important recovered paths are now server-proven. BTR-I02 admits a primary,
then reloads the same winner across later read-committed transactions without
using the server-authored admission timestamp as semantic identity. BTR-B03
applies the coordinator to the first contiguous rollback fixture position,
observes `RECEIPT_APPLIED`, raises fixed `P0001`, and proves that every
coordinator effect rolled back while the earlier primary admission remained.

Exact container
`4bbb33f427d5b006aecc38e6a1901c61d5581a69ed825b24d6266948b26702a6`
was reverified, removed and independently confirmed absent. No call followed
success. The mutable behavior evidence alias was restored byte-for-byte to its
protected pre-run SHA-256
`09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`.
The protected parse aliases likewise remain unchanged.

## Independent verification

Fresh Gemini 3.6 Flash/high review in clean short worktree `r182` recomputed the
immutable evidence seal and all parent seals, validated twenty-of-twenty
scenario reconciliation, replay and rollback details, schema admission, exact
cleanup, AER-0238 and protected refs. It passed 498/498 focused tests, Ruff
check, Ruff format and diff checks with no P0-P2 finding and an unchanged clean
postflight.

An earlier recovery veto correctly rejected a worktree-local interpreter
assumption and one unformatted assertion before attempt 048. Its repaired
descendant passed 113/113 tests. That veto consumed no database attempt.

## Issues exposed and resolved

Behavior attempts 001-047 remain immutable fail-closed evidence. They exposed
real source, renderer, PostgreSQL representability, evidence, harness and test-
fixture defects without admitting a partial behavior result. The final recovery
removed the server-authored `admitted_at` timestamp from cross-transaction
winner identity while preserving database-authored audit time, and corrected
the BTR-B03 fixture to use the first contiguous position.

The first whole-document validation of the immutable pass then exposed
AER-0238: nested stderr digests were emitted in the repository-standard
`sha256:` form while one schema leaf expected a bare hash. The immutable pass
was not rewritten. The schema now reuses the existing prefixed digest
definition, a hostile bare digest is rejected and the exact sealed evidence
validates as a whole document. AER revision 204 records 238 bounded incidents,
all closed.

## Claim boundary

This is high-assurance evidence for the selected serial entry-point, trigger,
RLS, idempotency and outer-transaction rollback slice. It is not a claim of
literal infallibility. It does not prove concurrent producer/coordinator races,
serializable retry policy, crash restart, unknown commit, key rotation,
retention execution, purge recovery, performance, monitoring or operational
availability.

No Alembic migration was applied. No operational database, application/API/
Diary wiring, outbox feed, watcher, listener, product or patient data, clinical
data, provider call, command, deployment, production, release, Pages rebuild or
protected-ref movement was opened.

## Programme handoff

The provider-free serial Context Fabric database-durability sequence is now
closed successfully. The next recommended tranche is the already requested
read-only codebase architectural-health and conformance review: reconstruct the
as-built system, trace critical authority/transaction paths, distinguish
current from accepted-unmounted/future/retired state and propose architectural
fitness functions. It should produce findings only, not a broad refactor.

After that pulse, the planned Agent Execution Surface and Containment Gate is
the dependency-satisfied prerequisite before any occupied Bureau receives real
product-derived context or executable capability. Yuri requested a pause after
this closeout, so neither next tranche starts here.
