# Sol acceptance — generation-lock parse characterization

Date: 2026-08-10

Decision: `accepted_for_exact_digest_binding_review`

## Runtime result

Exactly one fixed no-argument run used the already-local immutable image
`postgres:16-bookworm` at
`sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8`.
It created one newly owned, pull-never, networkless, no-port, no-mount,
tmpfs-only PostgreSQL 16 container and returned the expected non-accepting
result `catalogue_characterization_required`.

- attempt: `7ab702e5fa8cd5c75a7a8e6c`
- exact container:
  `aa3d7ccc5a542e2a4531d371405e9ceeee091b0372edeacd1643b76478a87496`
- cleanup: `cleanup_verified`
- removed: `true`
- harness absence: `true`
- independent exact-ID `docker container inspect`: exit 1, exact
  `No such container`
- elapsed: 9172 ms

Immutable evidence is
`orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence-generation-lock-rls-characterization.json`
at SHA-256
`78c157c72243036d395c3bcff30f778fa8b1032bb98eec9a32b37110efbcf536`.

## Catalogue reconciliation

The complete catalogue retained the exact population of 32 types, 18
relations, 252 columns, 81 constraints, four indexes, 45 policies, 24
functions, 14 triggers and eight roles. Against the immediately preceding
accepted admission-row-shape exact reproduction, fourteen of the fifteen
acceptance-bound query digests are unchanged. The sole delta is `policies`,
exactly matching the reviewed `pol_cf_06_update` generation-lock RLS repair.

The apparent three-digest difference against the older mutable accepted parse
alias was investigated before binding: `functions` and `function_acl` already
match the immediately preceding accepted admission-row-shape generation. They
are not generation-lock deltas. No contradictory catalogue change remains.

The current contract now binds all fifteen observed acceptance digests in
`exact_digest_bound` mode with canonical SHA-256
`dbedcaf7628a68859412d898e86292b2366209941d18f58363c45174b6fc60ba`.
Focused deterministic checks pass 140/140 plus Ruff and diff validation.

## Protected evidence preservation

- mutable accepted parse evidence remains
  `97d1385c6b617890cb0f155122e30eb283d49e42af1d44db385a2b9f4a9c2bec`;
- immutable historical parse failure remains
  `3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c`;
- mutable accepted behavior evidence remains
  `09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`.

Byte-exact external backups exist under the run-specific temporary backup
directory recorded in the execution output. The generic characterization
target did not alias any protected evidence path.

## Authority boundary

This acceptance permits only deterministic validation and one fresh exact-HEAD
Gemini 3.6 Flash/high veto of the exact-digest binding. Only a passing veto may
open one later exact reproduction run in a newly owned disposable container.

It grants no behavior execution, applied migration, operational database or
credential, watcher/listener/feed, patient/product/clinical data, provider,
application/API/Diary command or write, deployment, production, release,
Pages or protected-ref movement.
