# Disposable PostgreSQL parse/catalogue generation-lock RLS rebind

Date: 2026-08-10

Status: characterization passed with exact-ID cleanup; deterministic exact-
digest binding candidate pending fresh independent review.

The independently accepted source commit
`e115f6f4cb31df1131c5c67d24f3a475a2ca6127` regenerates the inert durability
artifact as 1,435,252 canonical LF bytes with SHA-256
`sha256:aa26f92671a18d927e423f9d7df80973a19a87f32d49d85cc3f3d55f6808e8e9`.
Its 421 statements and all object populations remain fixed. The only catalogue
delta expected is the existing `pol_cf_06_update` predicate admitting ordered
`COORDINATOR, LIFECYCLE` in USING and WITH CHECK.

The parse contract was deliberately rebound in `characterization_only` mode
with an empty expected digest map and passed deterministic plus fresh
independent exact-HEAD review. Exactly one newly owned networkless, pull-never,
tmpfs-only PostgreSQL 16 container then returned
`catalogue_characterization_required`, characterized the complete catalogue,
and was removed as exact container
`aa3d7ccc5a542e2a4531d371405e9ceeee091b0372edeacd1643b76478a87496`
with independent exact-ID absence confirmed.

Immutable characterization evidence is
`orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence-generation-lock-rls-characterization.json`
at SHA-256
`78c157c72243036d395c3bcff30f778fa8b1032bb98eec9a32b37110efbcf536`.
Its exact fifteen bound query digests differ from the immediately preceding
accepted admission-row-shape reproduction only in `policies`; the function and
function-ACL digests already matched that accepted parent generation. Object
populations remain unchanged at 32 types, 18 relations, 252 columns, 81
constraints, four indexes, 45 policies, 24 functions, 14 triggers and eight
roles.

The contract now binds those fifteen exact observed digests in
`exact_digest_bound` mode at canonical SHA-256
`dbedcaf7628a68859412d898e86292b2366209941d18f58363c45174b6fc60ba`.
Fresh deterministic checks and one fresh exact-HEAD independent veto are still
required before one exact reproduction run.

The accepted mutable parse evidence, protected historical failure and mutable
behavior evidence remained byte-exact at their frozen hashes; characterization
used its own non-aliasing evidence path.

No applied migration, operational database, source watcher/listener/feed,
product/patient/clinical data, provider call, application/API/Diary command,
deployment, production, release, Pages or protected-ref authority is opened.
