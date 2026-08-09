# Provider-free durability JSON key-set order recovery

Date: 2026-08-09

Status: deterministic renderer repair and non-accepting catalogue
characterization pass; exact catalogue reproduction and behavior runtime closed

## Preserved failure

Behavior attempt 026 admitted the UUID-minimum-repaired artifact and stopped
at `BTR-E02` with repository SQLSTATE `CF103` in
`emr4_context_fabric.project_update_confirm_reschedule_v1`, reported at
function line 85. Zero of twenty scenarios completed. Its newly owned
networkless PostgreSQL 16 container
`964146e15d418897436af1196204707b88d32756b7efe831ae9b9b4e08c66e84`
was removed and exact-ID absence was independently observed. Immutable failure
evidence is byte-identical to the failed mutable artifact at SHA-256
`sha256:6365e2f52a08f45a564764a280b2fe83ac3cae8bd2dd0af31708a1696231c56a`.

The bounded repository diagnosis used no additional database container and
persisted no raw PostgreSQL error. It bound the exact predecessor artifact,
immutable body source and attempt-026 coordinate. PostgreSQL's reported line
maps to the event-membership assertion `p12` and its sole `JSON_KEYS_EXACT`
expression.

## Root cause

`JSON_KEYS_EXACT` already sorts the actual keys returned by
`jsonb_object_keys` lexicographically. Renderer 2.0.12 emitted the fixed
expected key array in the body contract's declaration order instead of the
same canonical order. The event's exact six-key set was therefore compared as:

- actual: `appointment_id`, `end_time`, `location_id`, `practitioner_id`,
  `reason_codes`, `start_time`;
- expected: `appointment_id`, `practitioner_id`, `location_id`, `start_time`,
  `end_time`, `reason_codes`.

The set membership was correct but the ordered arrays were unequal, so the
fail-closed guard returned `CF103`. This is a repository renderer defect, not
a PostgreSQL, provider, model or environment failure.

## Exact recovery

Renderer 2.0.13 lexicographically canonicalizes the already fixed, unique
expected key list before emitting the typed `pg_catalog.text[]` literal. It
does not add, remove, rename or accept a caller-selected key. The actual side
retains `array_agg(... ORDER BY k.k)`, null handling remains closed, and array
equality continues to reject every missing or additional JSON key.

The immutable body program, its seven `JSON_KEYS_EXACT` uses, SQLSTATEs,
transaction effects, entry points, roles, policies, triggers and all twenty
behavior scenarios are unchanged. Deterministic hostile tests prove that
different declaration orders render identically, the expected literal is
canonical, the predecessor ordering is absent, and exactly seven artifact
guards receive the same semantic correction.

The renderer source is bound at
`f620f31e4576003855afe824a385a86badf77120`. The regenerated inert artifact
remains 412 statements and 1,391,670 canonical
LF bytes at SHA-256
`sha256:f4479c772f144973c1a1f373e16e0bcb3543fea6128c8054a282316ce5d02714`.
Its render-manifest file SHA-256 is
`sha256:d414fb3f0c9d5b8075e913f5608b6146b7b9ee43eb849c9272ccf48df3a2c706`.

## Required proof sequence

Before another behavior attempt:

1. failure preservation, deterministic diagnosis, renderer and hostile tests
   pass;
2. one newly owned networkless PostgreSQL 16 characterization run records the
   new artifact's catalogue digests and is removed;
3. the exact parse contract is rebound and reproduced in a distinct newly
   owned exact-bound container;
4. the behavior contract's six parents are rebound to that accepted parse
   source while all twenty scenarios remain byte-identical;
5. the complete deterministic packet and one fresh exact-HEAD Gemini 3.6
   Flash/high veto pass; and
6. only then may one newly owned behavior attempt 027 run with exact cleanup.

Any later rejection continues the same evidence-backed diagnose-repair-rerun
sequence. It cannot authorize scenario deletion, key-set weakening, raw SQL,
superuser substitution, RLS/trigger disablement or operational runtime.

## Catalogue characterization result

The required characterization completed as the non-accepting result
`catalogue_characterization_required` under attempt
`6033b191fdfb084894b58514`. Its immutable evidence file has SHA-256
`sha256:9e5338986fb4dea8ad5c7f0f0a96e624a525c93e127d507f651e68ca2b5b02b0`.
It recorded all seventeen allowlisted query digests, including fifteen
value-bearing digests now fixed in the exact-bound descendant contract.

Exact owned container
`ef4ca866ac143928bdc59e31f2013c2a57d1f9f4896052a1a42b223e945a8aad`
was removed and exact-ID absence was independently observed. This result does
not accept the new artifact. A distinct newly owned networkless container must
reproduce the exact digests before the parse prerequisite or behavior contract
can be rebound.

## Claim boundary

This recovery proves only deterministic exact JSON key-set comparison in an
inert artifact and closed authored-synthetic rehearsal. It grants no applied
migration, operational database, product or patient data, provider,
API/Diary wiring, watcher/listener/feed, command/write, deployment,
production, release, Pages or protected-ref authority.
