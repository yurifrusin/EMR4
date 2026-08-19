# Sol acceptance — check-in runtime-role and tenant-isolation attestation rehearsal

Date: 2026-08-19

Timestamp: 2026-08-19T16:42:31.0085024+10:00 (Australia/Brisbane)

Decision: **accept**

GPT Sol's substantive acceptance is limited to exact reviewed candidate
`6a2832575e9b4df5c40a13984db7281e79814a94` and the following claims:

1. one uniquely named disposable local PostgreSQL 16 instance carried only an
   authored-synthetic manifest, tenant identifiers, probe relation and
   ephemeral credentials;
2. the dynamic login role was non-owner, `NOBYPASSRLS`, non-superuser,
   non-inheriting, without create/replication capabilities, memberships,
   product privileges or owned objects;
3. the admin-owned probe had enabled and forced RLS with matching tenant
   `USING` and `WITH CHECK` predicates;
4. same-tenant reads and writes succeeded while cross-tenant read/update/
   delete returned zero, cross-tenant insert and admin-role escalation failed
   with exact SQLSTATE `42501`, and tenant context did not leak;
5. all 12 scenarios passed, 302 contract and 159 manifest hostile mutations
   denied with zero escapes, and the released closed evidence contains no
   password, DSN, raw output, Docker name or local path;
6. the role was absent before teardown and the captured container and network
   IDs were absent afterward;
7. `ordinary_admission_release_count` is zero and no ordinary-practice,
   product/config/API/client/status/waiting-area behavior changed; and
8. Gemini 3.7 Flash/high passed its independent ten-command veto at the exact
   unchanged clean candidate.

The clockwork replay-fixture repair is accepted as test-only workflow
self-correction: exact historical source
`f98baaa5c57cfcf00f8d2e6cd0d1113d4a59ed6e` now owns historical fault replay,
while live zero-drift validation remains separate. It grants no product or
governance publication authority.

The five generation-stale historical mutable-current assertions are excluded
exactly as recorded in the frozen plan. Their immutable tranche evidence
remains covered; canonical state was not rewritten to satisfy predecessor
literals.

No live secret or rotation, existing/product database, product data,
ordinary-practice admission, rollback/unknown-commit recovery, occupied
DeepSeek HMR, production runtime, deployment, release, Pages or protected
integration is accepted.

The one pointer-last live tick passed at generation
`gen-503aa76307da93745abbca25f209a6841118660d02cb171ea576f4eaede5c7f5`,
lease sequence 4 and Continuity 334 / Compass 316, with zero drift, zero
caller-derived fields, zero bespoke updater runs, ten clockwork-owned surfaces
and zero dual-owned surfaces. The successor latch now names only the provider-
free disposable PostgreSQL rollback/unknown-commit recovery rehearsal. No
protected ref moved.

The non-PHI continuing Pushover notification succeeded with request
`70fee954-0528-44b2-8961-f93c60828818`.
