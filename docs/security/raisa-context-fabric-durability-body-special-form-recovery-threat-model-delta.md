# Context Fabric durability body special-form recovery threat-model delta

Date: 2026-08-08

Status: bounded recovery delta; no runtime or product authority

## Changed surface

Only deterministic PostgreSQL text lowering changes. The renderer replaces the
invalid namespace-qualified `pg_catalog.coalesce(...)` spelling with the valid
unqualified `COALESCE(...)` special form and rejects any recurrence before an
artifact can be accepted.

## Preserved properties

- No relation, column, role, grant, policy, function signature, trigger,
  entry-point effect, digest input, ordering expression, SQLSTATE, transaction
  boundary, or behavior scenario is added or removed.
- Every callable function remains explicitly qualified; only the non-callable
  PostgreSQL grammar form is unqualified.
- The accepted body contract and twenty-scenario behavior contract remain
  unchanged until their exact artifact bindings are deliberately rebound.
- Attempt 017 retains only bounded failure coordinates and digests and proves
  exact cleanup; no raw SQL values or stderr prose are released.

## Closed surfaces

No application migration, operational database or credential, source watcher,
listener or feed, application/API/Diary wiring, patient, clinical, product or
protected data, provider/model call, external retrieval, tool command, product
write, deployment, production, release, Pages rebuild, or protected-ref
movement is opened.
