# Threat-model delta — unmounted status-confirm product adapter

Date: 2026-08-13

Timestamp: 2026-08-13T10:12:35+10:00 (Australia/Brisbane)

## New seam

One unmounted service will translate authenticated application facts into the
accepted status-confirm composition. It receives a bearer value already
admitted by the authentication dependency, an authenticated user, the exact
proposal-confirm body, an opaque server-minted proposal-version binding,
explicit secrets and an injected fresh command-session factory. No router
imports it in this tranche.

## Threats and controls

| Threat | Required control |
|---|---|
| Client invents a session identity | Derive the only session reference with keyed HMAC over the authenticated bearer; expose no raw bearer. |
| Post-write replay observes a new version and changes the idempotency digest | Build initial admission from verified signed proposal state plus a separate HMAC binding over its evidence signature and proposal-time version; never substitute the later live snapshot before replay classification. |
| Client tampers with or swaps the proposal-time version | Exact schema/key checks, positive integer version, evidence-signature binding and constant-time HMAC verification before transaction construction. |
| Request transaction nests or leaks stale tenant context | Use a distinct injected command session and restore transaction-local practice context before RLS-protected access. |
| Disabled or role-changed actor wins after waiting | Fresh actor lookup on both physical authority checks; exact active/practice/role match or 403 with rollback. |
| Waiting-area union enters the status seam | Concrete type/intent/kind discrimination before transaction construction. |
| Proposal-time state survives a lock wait | Rebuild state version, freshness, warnings and terminal policy from the locked appointment; a changed locked request stops while exact replay retains the original signed request. |
| Warning acknowledgement is weakened | Require unique exact set equality among locked required, proposed and confirmed warning codes. |
| Effect escapes the locked target | Stage only on the physical decision's appointment and require target/practice/public projection equality. |
| Audit or private receipt separates from mutation | One transaction, one command-bound audit identity, canonical full envelope and adjacent version are mandatory before commit. |
| Replay re-executes the mutation | Replay may release only validated stored canonical bytes; effect count remains one. |
| Rehearsal touches product state or credentials | Fake command session/transaction only; no config, SessionLocal, server, route, database, provider or network. |

## Residual boundary

This tranche cannot prove request-dependency wiring, actual RLS behavior or
HTTP byte delivery. Those remain later separately gated route and database
rehearsals. A pass grants no runtime, product-data, command, deployment or
release authority.

The current route does not carry the new opaque proposal-version binding. Its
future transport is deliberately left to the separate route-wiring tranche;
this rehearsal proves only the unmounted adapter's verification and use of that
server-minted value.
