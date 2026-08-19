# Provider-free disposable PostgreSQL check-in runtime-role and tenant-isolation attestation closeout

Date: 2026-08-19

Timestamp: 2026-08-19T16:42:31.0085024+10:00 (Australia/Brisbane)

Status: **accepted**

## Result

Exact reviewed candidate
`6a2832575e9b4df5c40a13984db7281e79814a94` proves the frozen logical check-in
runtime role in one uniquely named, locally controlled, disposable PostgreSQL
16 instance using only authored-synthetic identifiers.

The ephemeral physical login role was catalogue-observed as
`NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`, `NOREPLICATION` and
`NOBYPASSRLS`, with zero memberships, zero owned databases/schemas/relations/
functions, zero policy bindings and zero product-relation privileges. It had
only database connect, probe-schema usage and `SELECT`, `INSERT`, `UPDATE`,
`DELETE` on one admin-owned synthetic probe table.

The probe had RLS enabled and forced, with matching `USING` and `WITH CHECK`
expressions around a transaction-local tenant setting. Same-tenant A read,
insert and update and same-tenant B read succeeded. Cross-tenant read, update
and delete returned zero; cross-tenant insert and attempted admin `SET ROLE`
failed with exact SQLSTATE `42501`; an absent tenant setting saw zero rows and
the setting was absent after transaction completion.

The physical role was dropped and observed absent before teardown. The relay
stopped and the captured exact container and network IDs were observed absent.
No matching harness-labelled container or network remained.

## Evidence and independent veto

- Exact candidate: `6a2832575e9b4df5c40a13984db7281e79814a94`.
- One disposable PostgreSQL execution passed on its first run with all 12
  scenarios and exact cleanup.
- Eleven exact source bindings matched.
- 302/302 hostile contract mutations and 159/159 hostile manifest mutations
  denied with zero escapes.
- Released attestation and parent evidence validated against closed Draft
  2020-12 schemas; the parent digest exactly binds the attestation bytes.
- `ordinary_admission_release_count` remained zero.
- Focused tests passed 19/19. The material surrounding suite passed 145 tests
  with the five plan-recorded predecessor-current assertions deselected. The
  repaired clockwork fault/idempotency suite passed 6/6.
- Ruff, compilation, JSON/schema validation, whitespace checks, fresh
  five-source receipts and the live zero-drift clockwork reading passed.
- One fresh Gemini 3.7 Flash/high read-only veto passed all ten exact commands
  at the unchanged clean candidate and reported no P0-P2 finding or boundary
  violation.

## Clockwork efficiency correction

Four clockwork fault-replay tests were genuinely coupled to mutable `HEAD`.
After later accepted ticks, they attempted to apply the historical successor-
resolution intent to the live environment-architecture latch and failed at
`tick_active_operation`. The narrow repair pins their private replay
worktrees to exact full-Git fixture
`f98baaa5c57cfcf00f8d2e6cd0d1113d4a59ed6e`. All pre-pointer fault points,
post-pointer commitment, stale predecessor denial and byte-exact rollback
remain exercised; the live clockwork still receives its separate zero-drift
check. This removes a recurring procedural rerun without weakening coverage or
changing canonical state.

## Honest efficacy reading

- Ariadne rehydration receipts: preplanning, post-compaction and candidate
  precommit passed; one verifier-predispatch draft failed before dispatch on a
  non-schema `ready` disposition and a wrongly attached workspace identity,
  then the corrected receipt passed.
- Static construction attempts: four focused pre-live pytest attempts, of
  which the first three exposed only brittle Markdown literals; one compile
  warning exposed and corrected an invalid escape; one JSON parse exposed and
  corrected a missing attestation-schema brace.
- Disposable PostgreSQL executions: 1 attempted / 1 passed / 1 exact cleanup;
  no retry.
- Broad local surrounding attempts: one exposed the already-known historical
  readiness latch literal; one explicit Continuity probe exposed four
  predecessor-current assertions; both exclusions are frozen in the plan.
- Clockwork-suite attempts after candidate construction: one broad attempt
  exposed four mutable-HEAD replay defects; one focused repaired run passed.
- Candidate commits: 1. Gemini provider review runs: 1, passed. Gemini command
  results: 10/10 zero exit. Reviewer retries: 0.
- An initial direct-file launcher help invocation failed locally because the
  module package path was absent; the module-form help and the one occupied
  review then passed. No provider call was consumed by the help error.
- New agent-error-register incidents: 0. The construction and preflight
  corrections are retained here as efficacy evidence; no rejected model
  decision, worktree postcondition breach, external transport failure or
  protected-boundary breach occurred.
- Bespoke Continuity updater runs: 0. Manual canonical derived-field edits: 0.
- Live clockwork publication attempts/successes: 1/1. The fourth pointer-last
  tick selected generation/bundle
  `503aa76307da93745abbca25f209a6841118660d02cb171ea576f4eaede5c7f5`,
  predecessor
  `gen-a7b3f1fc6696f535ef4f7d5e0d5b99c89f19bdc87546e5b4cf242b3b7483e88d`,
  lease sequence 4, Continuity 334 / Compass 316, ten owned surfaces, zero
  dual-owned surfaces, four retired legacy-writer classes, zero drift, zero
  caller-derived fields, zero bespoke updater runs and one publication.

## Boundaries and next tranche

The evidence proves physical representability for one authored-synthetic
restricted role and RLS policy only. It does not prove live secret custody or
rotation, an existing/product database, product-schema grants, ordinary-
practice admission, rollback, unknown-commit recovery, production RLS or
operator response.

No feature flag, authored-synthetic allowlist, product/config/API/client,
generic-status `Arrived`, action grammar, waiting-area behavior, product/
patient/appointment/clinical/protected data, occupied DeepSeek HMR, production
runtime, deployment, release, Pages or protected ref changed. Local/origin
`master` and `handoff/current` remain
`2e34bdad732fdab32fbf778280b3d3c70d66d602`; `docs/branding/` and all unrelated
untracked files remain preserved.

The next dependency-satisfied tranche is
`raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal`.
It may use only a newly frozen authored-synthetic disposable transaction probe
to distinguish committed, rolled-back and ambiguous outcomes and prove
fail-closed recovery without duplicate ordinary release. It opens no product
command, ordinary practice, real secret, persistent role or production
authority.

The live clockwork selected exact candidate
`6a2832575e9b4df5c40a13984db7281e79814a94` at generation
`gen-503aa76307da93745abbca25f209a6841118660d02cb171ea576f4eaede5c7f5`,
Continuity 334 / Compass 316 and lease sequence 4. Its successor latch is now
the rollback/unknown-commit rehearsal. The non-PHI continuing Pushover
notification succeeded with request
`70fee954-0528-44b2-8961-f93c60828818`.
