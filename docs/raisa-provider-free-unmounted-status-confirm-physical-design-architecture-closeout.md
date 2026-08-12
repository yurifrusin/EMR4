# Provider-free unmounted status-confirm physical-design architecture closeout

Date: 2026-08-12

Result: `raisa_provider_free_unmounted_status_confirm_physical_design_architecture_pass`

Source: `826aad11c29007b13eaa377e3f7ea494cc82ce70`

Implementation authority: `false`

Reasoning level: material architecture / Extra High

## Accepted result

The three representability gaps now have one narrow additive physical design:

- PostgreSQL owns a positive `BIGINT` appointment revision. New and cutover
  rows start at one; a synchronous `BEFORE UPDATE` invariant advances every
  committed appointment-row update and callers cannot select or suppress it.
- The existing command-idempotency table gains a versioned private receipt:
  five nullable-for-legacy fields capture receipt version, a 32-byte opaque
  session HMAC, pre/post state versions and the exact canonical response bytes.
- Existing receipts are not fabricated into the new meaning. A legacy match is
  `legacy_receipt_not_replayable` and discloses no stored result.
- Both initial delivery and retry replay use one exact stored UTF-8 JSON byte
  buffer. JSONB remains inspectable but is not the delivery authority.
- One `READ COMMITTED` transaction holds practice `FOR SHARE`, then the
  practice-scoped appointment `FOR UPDATE`, then the idempotency row
  `FOR UPDATE`. Target and authority checks precede classification or replay.

The public OpenAPI response remains unchanged. GraphQL gains no mutation;
events remain acceleration hints without command authority. The database
trigger is only a synchronous row invariant, not a watcher or event mechanism.

## Verification

- all eleven exact source hashes pass;
- the closed JSON schema and every frozen design decision validate;
- all 91 hostile mutations fail closed;
- the focused architecture file passes 16/16 tests;
- the bounded architecture/status-lineage/API/register/Compass/baton packet
  passes 413/413 tests; and
- Ruff and Git whitespace checks pass.

Two initial focused failures were mechanical Markdown line-wrap assertions.
Only the tests were normalized; no frozen design field or claim changed.

## Claim and authority boundary

This proves a coherent unmounted physical design, not executable DDL, ORM or
service code, PostgreSQL behavior, a mounted route, operational rollout or
production safety.

No application/model/migration/service/route source was edited or imported.
No executable DDL, database, SQL, real transaction/lock, provider/ADC,
credential/browser authorization, product/patient data, watcher/event, product
command, deployment, production, release, Pages or protected ref was opened.
`docs/branding/` and all unrelated untracked paths were preserved and excluded.

## Next tranche

The next dependency-satisfied tranche is a provider-free unmounted
status-confirm physical schema-and-transaction scaffold implementation. It may
lower this exact contract into an exact allowlisted model, inert Alembic
migration and unmounted service helper plus deterministic static tests.

Route mounting, migration/database execution, real locks, product/patient data,
providers/credentials, watchers/events, product commands, deployment,
production, release, Pages and protected refs remain closed.
