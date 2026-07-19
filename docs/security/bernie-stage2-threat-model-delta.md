# Bernie Stage 2 Focused Threat-Model Delta

Date: 2026-07-19

Scope: local synthetic durable authority for the existing appointment-create
vertical only

Decision: `frozen_for_stage2_implementation`

## Assets and trust boundaries

The protected assets are the authoritative appointment row, staff identity and
practice scope, retained Bernie semantic session state, one-time confirmation
authority, command idempotency response, append-only audit evidence, and the
correlation joining those records.

Trust boundaries are:

1. Diary/client input to authenticated FastAPI routes;
2. authenticated user and signed JWT claims to current database identity;
3. FastAPI/SQLAlchemy transaction to PostgreSQL tenant context and RLS;
4. proposal-only Bernie state to the human-confirmed REST command;
5. process memory to restart-safe PostgreSQL session/event state; and
6. retained session detail to the approved expiry/cleanup boundary.

The client controls event ids, idempotency keys, expected revisions, structured
payloads, confirmation requests, and retry timing. The server controls tenant
context, state transitions, payload screening, canonical hashes, row locks,
revalidation, writes, audit, receipts, and retention timestamps.

## Threats, controls, and evidence

| Threat | Required control | Acceptance evidence |
|---|---|---|
| Concurrent same-key confirmation creates duplicates | Atomic `ON CONFLICT` claim plus ledger-first lock order and one encompassing transaction | Two independent transactions produce one appointment/audit/ledger/outcome and one replay |
| Concurrent session revisions both advance | Owned session row lock, exact expected revision, unique session/result revision | One accepted transition and one stale-revision rejection |
| Crash splits session, appointment, audit, and command state | Single commit boundary for successful confirmation; full rollback on injected failure | Pre-commit fault leaves no partial effect; retry succeeds once |
| Restart loses semantic state or replay response | Durable snapshot/event rows and completed stored response | Fresh SQLAlchemy/store instances reproduce state, events, and receipt |
| Cross-practice read/write or opaque-id grafting | Route ownership predicates, JWT/database-practice match, transaction-local tenant context, forced RLS, and composite practice/id foreign keys | Cross-practice HTTP rejection, direct restricted-role RLS denial, and `23503` for foreign session/appointment/command/audit references |
| Audit evidence is rewritten or removed | Insert/select RLS plus database trigger rejecting update/delete | Direct mutation attempts fail; correlation remains readable |
| Command/audit drift | Reciprocal one-to-one command/audit ids, target appointment link, completed-create check, server-derived receipt ids | Exact command/appointment/audit/session/receipt comparison |
| Raw instruction, patient label, secret, or key persists | Key screening, bounded structured JSON, raw-key HMAC, no provider content | Rejection tests and schema/readback prove forbidden material absent |
| Stale token sets another tenant context | Compare signed token practice with current database user; set context from database user | Mismatched claim returns 401 before scoped data access |
| Session detail outlives approved need | Sliding 24-hour incomplete expiry, 30-day completed expiry, batch-bounded locked purge | Boundary-time and selective purge tests |

## Security invariants

- No client event or Bernie outcome can directly create an appointment.
- `confirmed` remains reachable only through server-owned confirmation outcome
  after explicit staff confirmation and backend revalidation.
- Missing tenant context returns no RLS-visible rows and permits no writes.
- An otherwise valid same-practice row cannot reference another practice's
  session, appointment, command, or audit id.
- Raw idempotency keys and raw instruction/transcript content are never stored.
- A completed appointment-create command has a target appointment, direct audit
  link, reciprocal audit command id, response hash/body, and server-derived
  receipt.
- Session retention cleanup cannot delete the minimal appointment, audit, or
  completed command/receipt evidence.

## Residual boundaries

This tranche does not claim production readiness. The local database owner is a
superuser, so RLS is proved under an isolated restricted role rather than by
provisioning a production runtime account. Real PII, at-rest field encryption,
production key management, browser token storage, production retention,
deployment, monitoring, incident response, backup/restore, and Australian
production residency require later decisions and evidence.

The local proof sets the custom tenant context through authenticated
application code. A future production runtime-role design must also prevent
untrusted SQL or a compromised database session from choosing an arbitrary
custom setting; this tranche does not claim that production control.

Providers, protected holdouts, historical diary material, external corpora,
new appointment actions, GraphQL mutations, and autonomous confirmation are
outside this threat-model delta and remain closed.
