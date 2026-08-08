# Ariadne agent error and correction register revision 94

Date: 2026-08-08

Status: accepted register correction

Revision 94 adds AER-0114 and brings the register to 114 bounded incidents.

## AER-0114 — first-effective behavior boundary mismatch

The accepted disposable PostgreSQL behavior plan froze two trigger scenarios
whose expected branches were not reachable under their own exact principals
and grants. `context_producer` could not update the Fabric alias in `BTR-T03`,
so native privilege denial would precede its alias trigger. The same-transaction
event deletion in `BTR-T02` is deliberately rejected by the immediate event
guard as `F_IMMUTABLE` / `CF601`, before the draft's later deferred `CF603`.

Sol detected both by tracing each rendered action through the accepted grant,
RLS, function-owner and trigger ordering before any container or database was
started. The planning candidate was revised rather than weakened:

- `BTR-T03` now exercises the producer-reachable committed-event immutable
  guard and adds no Fabric privilege; and
- `BTR-T02` now binds the actual immediate `F_IMMUTABLE` / `CF601`, while
  `BTR-T01` remains the distinct deferred temporal-bijection `CF603` proof.

The durable prevention control is a first-effective-boundary trace for every
future database behavior scenario before its SQLSTATE is frozen. The trace must
cover relation privilege, RLS, function ownership and trigger ordering under
the exact scenario principal.

No runtime evidence was emitted. The corrected implementation remains closed
until deterministic checks and a fresh exact-HEAD independent veto pass.
