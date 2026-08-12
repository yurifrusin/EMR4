# Provider-free unmounted status-confirm physical schema-and-transaction scaffold closeout

Date: 2026-08-12

Result: `raisa_provider_free_unmounted_status_confirm_physical_schema_transaction_scaffold_pass`

Source: `b36b8a455b70d8bc3e99b5e5dd84a8237375ff3c`

Runtime authority: `false`

Reasoning level: material security/transaction implementation / Extra High

## Accepted result

The accepted physical design now has one narrow source embodiment:

- `Appointment` maps a positive non-null database-owned `BIGINT` state version
  with baseline one.
- `AppointmentCommandIdempotency` maps the five nullable-for-legacy private
  receipt fields and exact conditional v1 completion constraints.
- one inert Alembic descendant of sole observed head `v1w2x3y4z5b6` performs
  the seven-phase cutover, installs the synchronous before-update invariant,
  rejects overflow and fails downgrade closed after any v1 receipt exists;
- pure helpers produce fixed-order canonical UTF-8 response bytes, raw 32-byte
  domain-separated length-framed session HMACs and constant-time response
  integrity decisions; and
- an unmounted context-manager seam composes one bounded `READ COMMITTED`
  transaction with practice `FOR SHARE`, appointment `FOR UPDATE`, conflict-safe
  idempotency insertion/`FOR UPDATE`, and current-authority checks before access
  and classification.

The seam cannot silently become a command. A future caller must stage a complete
appointment/audit/v1-receipt write set while it holds a `new_command` decision;
otherwise the seam raises and rolls the transaction back. No existing route
imports it.

## Verification

- all 16 exact source/implementation bindings pass;
- all 80 hostile contract mutations fail closed;
- focused scaffold tests pass 11/11;
- the current descendant/convergence/register/baton/source-state packet passes
  274/274;
- Ruff and Git whitespace checks pass; and
- the public appointment-command OpenAPI hash remains unchanged.

The first focused run exposed only a Python 3.14 dynamic-test-loader registration
issue; the second exposed a stale expected HMAC test vector. Both were repaired
mechanically without changing the frozen algorithm. A first closeout receipt
used the unapproved `pre_acceptance` event and correctly returned
`revision_required`; that pair is retained and the corrected `pre_commit`
receipt passes.

Historical representability/design builders deliberately bind the pre-scaffold
model hash and assert that these fields are absent. Their fresh-builder failures
after this descendant source change are expected immutable-evidence behavior,
not a regression or current acceptance gate.

## Claim and authority boundary

This proves a statically coherent unmounted schema/transaction scaffold. It does
not prove that PostgreSQL parses or installs the migration, that catalogues or
triggers match, that real locks/rollbacks work, or that any route behaves
correctly.

No migration, database or SQL was executed; no real lock or route was opened;
no provider, ADC, credential, browser authorization, product/patient data,
watcher/event authority or product command was used. Nothing was deployed or
released; Pages and protected refs did not move. `docs/branding/` and every
unrelated untracked file were preserved and excluded.

## Next tranche

The next dependency-satisfied tranche is a provider-free disposable
PostgreSQL status-confirm scaffold parse/catalogue rehearsal. It may install
only this exact migration in an owned empty disposable PostgreSQL instance,
inspect exact catalogues and exercise transactionally rolled-back authored-
synthetic DDL invariants. Route mounting, durable/product data, application
commands and production remain separately closed.
