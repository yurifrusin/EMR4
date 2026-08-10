# Threat-model delta: receipt-lock RLS recovery

Date: 2026-08-08

Status: candidate structural repair; runtime remains closed

## Changed surface

Only the repository-local structural RLS catalogue gains one lock-visibility
policy. The typed function program, entry points, role grants, direct relation
privileges, immutable-receipt invariant and behavior scenario population do not
change.

## Threats and controls

| Threat | Control |
|---|---|
| A legitimate coordinator cannot lock an existing receipt during idempotent replay and reports false absence | Add exact COORDINATOR `USING` visibility for the contracted row lock |
| Lock visibility accidentally creates receipt mutation authority | Use UPDATE policy only for PostgreSQL lock semantics, retain zero direct DML, and require `WITH CHECK` to repeat the exact binding predicate followed by `AND FALSE` |
| Another capability gains unnecessary lock authority | Admit exactly COORDINATOR; exclude OBSERVER, RETENTION and all unlisted capabilities |
| A broad predicate crosses practice or source boundaries | Reuse the existing session-user, practice, source-contract and transaction-time binding helper without widening |
| Structural and generated artifacts silently diverge | Mirror the closed policy in the structural schema, reseal parents, regenerate DDL/manifest, and require exact recognizer and catalogue reproduction |
| A scenario edit hides the regression | Preserve exact twenty-scenario bytes, order, category counts and population digest |
| A changed candidate reaches another disposable run without challenge | Require deterministic tests and one fresh exact-HEAD Gemini 3.6 Flash/high veto before the next behavior attempt |

## Residual boundary

This does not prove crash recovery, concurrency under production load,
long-lived persistence, operational watchers/feeds, application wiring or
clinical/product-data suitability. Those gates remain closed.
