# Provider-free unmounted status-confirm product-adapter rehearsal closeout

Date: 2026-08-13

Timestamp: 2026-08-13T10:44:05+10:00 (Australia/Brisbane)

Result: `raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal_pass`

Source commit: `b728b903c99fa35f231df04ba68263533261121a`

## Decision

The four coupled application-owned blockers identified by the readiness review
now pass together in one provider-free, unmounted adapter contract. The adapter:

- derives a minimized 64-character server-session reference from the already
  authenticated bearer without storing or releasing the bearer;
- admits only the status proposal family and restores tenant context before two
  fresh current-authority checks in an injected command session;
- verifies the signed proposal snapshot, reconstructs locked warning and
  terminal policy, and rejects a changed locked request generation; and
- stages the exact locked status effect, one attributable audit and the
  adjacent database-owned version required by the accepted private receipt.

The resulting public envelope is complete and canonically stored. A retry after
the simulated response is lost releases byte-identical stored bytes and performs
no second mutation or audit.

## Proposal-version recovery

Implementation discovery exposed one important omission in the accepted product
proposal evidence: it does not include `appointment_state_version`. Reading the
live version again after a successful write would change the idempotency request
digest and incorrectly turn a legitimate lost-response retry into a conflict;
ignoring the version would weaken stale-generation protection.

The accepted recovery is a separate opaque server-minted HMAC binding over the
exact signed-evidence signature and its positive proposal-time version. Initial
admission is therefore stable across replay, while the locked execution request
must still reproduce the same actual version. The current route does not carry
this binding and was not edited; its future transport remains part of the route
wiring gate.

## Evidence

- all thirteen frozen inputs remain hash-exact;
- `app/routers/appointments.py` remains hash-exact and contains no import of the
  new adapter;
- 84 of 84 hostile admission mutations fail closed;
- 27 new adapter/plan/evidence tests pass;
- the 118-test focused adapter, composition, physical, readiness, idempotency,
  latch and baton group passes;
- the canonical fast profile passes Ruff, maintained-source compilation over
  209 files, 193 tests, Diary JavaScript syntax and Git whitespace; and
- the evidence records zero route calls, database connections, provider calls,
  network calls and product/patient records.

No external worker or model was used. This tightly coupled adapter and recovery
remained Sol-owned under the provider-free boundary.

## Claim boundary

This proves authored-synthetic, in-process behavior of one application-owned
adapter over the accepted unmounted composition. It does not prove real
PostgreSQL/RLS behavior, request-dependency wiring, an HTTP route, concurrency,
restart, crash, unknown commit or UI behavior.

No route edit/mount/call, real database/source, product/patient data, provider,
credential, network, command authority, deployment, production, release, Pages
or protected-ref authority is opened.

## Narrowest next tranche

The next safe infrastructure gate is one provider-free disposable PostgreSQL-16
integration rehearsal for this exact product adapter and accepted physical seam.
It should prove transaction-local tenant restoration, both live actor checks,
the one mutation/one audit/private-receipt write set and exact replay against
authored-synthetic rows, with complete owned cleanup. It remains off-route.

After that database-backed adapter gate, the remaining core step before visible
UI work is the separately frozen route-wiring/mounting tranche, including the
new proposal-version binding and exact stored-byte HTTP delivery.
