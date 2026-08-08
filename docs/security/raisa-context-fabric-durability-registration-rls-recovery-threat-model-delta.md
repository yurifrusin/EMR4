# Context Fabric durability registration RLS recovery threat-model delta

Date: 2026-08-08

Status: bounded architecture correction; no runtime or product authority

## Changed surface

Forced-RLS predicates for three Fabric relations now admit the already
authorised `LIFECYCLE` session only for the exact operations required to create
and replay a generation's initial state: stream-head, frame-generation and
invalidation-watermark `SELECT`/`INSERT`.

## Security argument

- Authorization remains derived from the exact active
  practice/source/stream binding and stable `session_user` through
  `session_binding_allows_v1`.
- The security-definer owner does not bypass forced RLS and no predicate admits
  an unbound lifecycle login.
- `LIFECYCLE` is not added to the three corresponding `UPDATE` policies, so it
  cannot take over producer stream progression or coordinator frame/watermark
  transitions.
- No direct relation privilege, function execute grant, role membership,
  inheritance, `BYPASSRLS`, schema creation or owner authority changes.
- The behavior harness retains its exact cross-practice, forbidden-operation,
  replay and rollback attacks; no expected outcome or SQLSTATE is weakened.

## Closed surfaces

No application migration, operational database or credential, durable volume,
source watcher/listener/feed, application/API/Diary wiring, patient, clinical,
product or protected data, provider/model call, external retrieval, tool or
product command, deployment, production, release, Pages rebuild or protected-
ref movement is opened.
