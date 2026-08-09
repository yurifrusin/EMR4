# Provider-free durability UUID minimum recovery

Date: 2026-08-09

Status: bounded typed renderer recovery candidate; behavior runtime closed

## Preserved failure

Behavior attempt 025 admitted the repaired interval artifact and again stopped
at `BTR-E02` with SQLSTATE `42883`. Zero of twenty scenarios completed. Its
newly owned container
`43bf5d122670f424821cf00511d2ee21404f0b66c4d19ead9e0bdbf45ea833da`
was removed and exact-ID absence was independently observed. Immutable failure
evidence is byte-identical to the failed mutable artifact at SHA-256
`sha256:b963933df05c418456fdc1e101a7254a617ba743a4cb4b03888caf0aac547ba2`.

The first attempt-025 diagnostic replay cleaned up but its historical fixed
symbol allowlist did not classify the remaining error. It released no raw text
or conclusion. A corrected repository-bounded classifier then required every
other fixed prerequisite symbol to resolve, confirmed that the repaired
integer-times-interval signature remained absent and was not executed, and
released only `repository_function::pg_catalog.min`. Raw error text was hashed
but not persisted. Its distinct container
`cc989b3cf10ee7fac12c38adb33b069497229efd41f287fee13b99fc1cd93ac9`
was removed and exact-ID absence was independently verified.

## Root cause

The renderer's typed `MIN_FIELD` opcode always emitted
`pg_catalog.min(s.<field>)`. That is valid for the two existing `bigint`
checkpoint-position uses, but the appointment and event guard recovery also
constructs two renderer-owned `MIN_FIELD` expressions whose field type is
`pg_catalog.uuid`. PostgreSQL 16 does not expose the `min(uuid)` aggregate, so
the first appointment update in `BTR-E02` failed inside the guard before the
scenario could complete.

## Exact recovery

Renderer 2.0.12 is type-directed:

- `MIN_FIELD` of `pg_catalog.bigint` retains `pg_catalog.min`;
- `MIN_FIELD` of `pg_catalog.uuid` lowers to one deterministic typed ordered
  selection over the same unnested set using `ORDER BY ... ASC NULLS LAST
  LIMIT 1`; and
- every other `MIN_FIELD` result type fails renderer admission.

The ordered selection is equivalent to aggregate minimum for the admitted
nonempty UUID binding set while also preserving aggregate-style null handling:
ascending PostgreSQL order places nulls last, so the first non-null UUID is
selected when one exists. The independent recognizer rejects reintroduction of
`pg_catalog.min(s.stream_id)`, and hostile tests preserve the two bigint uses.

The deterministic regenerated artifact remains 412 statements and is
1,391,670 canonical LF bytes at SHA-256
`sha256:eeabfc39bf0b0c1073f57e97835440b394391161bec3ddc62be6e186fd7af6d8`.
Its render-manifest file SHA-256 is
`sha256:4e3d80f2855bcf97f9e0fdce9630b42b9f2b67454df77e6954cbb79e8e3aac11`.
The immutable structural and body parents, policies, functions, triggers,
entry points, SQLSTATEs, effects and twenty behavior scenarios are unchanged.

## Required proof sequence

Before another behavior attempt:

1. focused renderer, hostile-recognizer, failure-preservation and diagnosis
   tests pass;
2. one newly owned networkless PostgreSQL 16 characterization run records the
   new artifact's catalogue digests and is removed;
3. the exact parse contract is rebound and reproduced in a distinct newly
   owned exact-bound container;
4. the behavior contract's six parents are rebound to that accepted parse
   source while all twenty scenarios remain byte-identical;
5. the complete deterministic packet and one fresh exact-HEAD Gemini 3.6
   Flash/high veto pass; and
6. only then may one newly owned behavior attempt 026 run with exact cleanup.

Any later rejection continues the same evidence-backed diagnose-repair-rerun
sequence. It cannot authorize scenario deletion, raw SQL, superuser
substitution, RLS/trigger disablement or operational runtime.

## Claim boundary

This recovery proves only type-valid UUID minimum lowering in a deterministic
inert artifact and closed authored-synthetic rehearsal. It grants no applied
migration, operational database, product or patient data, provider, API/Diary
wiring, watcher/listener/feed, command/write, deployment, production, release,
Pages or protected-ref authority.
