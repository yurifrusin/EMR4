# Context Fabric durability admission-row-shape recovery

Date: 2026-08-10

Status: candidate parent recovery; database runtime remains closed

## Failure preserved

Behavior attempt 034 is immutable at
`provider-free-behavior-transaction-failure-evidence-034.json`, SHA-256
`68d61a9c55c800ca1670c6e0e7cde3e720486a82e2125649f64375844c09262a`.
It reached `BTR-E03` and PostgreSQL rejected the first PRIMARY admission insert
with SQLSTATE `23514`. Zero scenarios were admitted. The exact owned disposable
container was removed and its absence verified, and the accepted mutable
behavior evidence was restored byte-exactly.

## Deterministic diagnosis

Structural constraint `ck_cf_04_02` defines two disjoint row shapes:

- PRIMARY requires all five release-outcome fields and forbids both attempted
  admission digest and conflict reason.
- CONFLICT requires attempted admission digest and conflict reason and forbids
  all five release-outcome fields.

The accepted body generator used one shared binding population for both kinds.
It therefore supplied `attempted_admission_digest` on PRIMARY rows and supplied
PRIMARY-only outcome fields on CONFLICT rows. Five insert-or-reload winner
predicates also used ordinary equality against typed null values, which cannot
establish SQL null equality.

The diagnosis is bound to source HEAD
`df5352fb6964cad6e15195cfe8c9e17346a061b4`, the historical body contract,
structural contract, entry-program source and inert DDL. It opened no second
database run.

## Bounded repair

The generator now emits kind-specific admission projections. PRIMARY receives
only the five required outcome fields; CONFLICT receives only attempted digest
and conflict reason. Every opposite-shape field is a typed null. The shared
winner builder now lowers every typed-null equality requirement to `IS NULL`
and retains ordinary equality for non-null values.

The regenerated canonical body contract SHA-256 is
`sha256:d60eb4bd018a5f9180985db10f9b18c92d797b45844fbba345871085da4834c3`.

Candidate-independent tests enumerate both exact row shapes and all null-bound
winner predicates. They reject any `EQ` comparison whose expected binding is a
typed null. No structural constraint, SQLSTATE, function authority, principal,
RLS policy, scenario expectation or safety boundary is weakened.

## Parent recovery sequence

Before another behavior run, the changed entry-program source must regenerate
and verify the canonical body contract, body schema, inert DDL, render manifest
and lowering contract. The parse/catalogue proof must then be rebound and pass
in a newly owned networkless disposable PostgreSQL 16 container. The unchanged
twenty behavior scenarios must be rebound to that accepted parent, pass their
full deterministic packet and receive a fresh exact-HEAD Gemini 3.6 Flash/high
veto before one new fixed-path behavior attempt.

## Closed boundaries

This recovery opens no applied migration, operational database or credential,
watcher/listener/feed/source wiring, application/API/Diary command or write,
provider or product data, patient or clinical data, deployment, production,
release, Pages or protected-ref movement.
