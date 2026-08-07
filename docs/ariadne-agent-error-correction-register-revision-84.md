# Ariadne agent-error register revision 84

Date: 2026-08-08

Status: inert-DDL implementation recovery admitted; five process incidents corrected

Revision 84 adds AER-0087 through AER-0091 for the inert PostgreSQL durability
rehearsal.

AER-0087 records an invalid DeepSeek adapter-probe method in the first worker
predispatch state. Ariadne stopped dispatch; a distinct corrected state passed
before the worker launched.

AER-0088 records that the first DeepSeek implementation returned
`candidate_ready` while broad lowering, cardinality, isolation, delete,
canonicalization, ownership and recognizer defects remained. It was not
committed or accepted; one bounded correction was permitted.

AER-0089 records that the corrected implementation again returned
`candidate_ready` after 58 passing tests, but Sol review found material
PostgreSQL-16 representability defects: nullable empty counts, dependency and
trigger-grammar errors, incomplete owners, six impossible trigger-row `xmin`
references, non-producer appointment rejection and an unknown-lock fallback.
The worker lane was closed. Sol froze one recovery, obtained an independent
plan pass, implemented eight fragment-sealed transforms, passed 62 merged
tests and obtained a fresh exact-commit Gemini pass with no P0-P3 finding.

AER-0090 and AER-0091 record two verifier-preflight HEAD-entry errors: first an
abbreviated plan commit, then a guessed full implementation commit. Both were
caught before model dispatch and corrected from literal `git rev-parse HEAD`
output. Their recurrence adds a durable rule: never manually expand or infer a
commit hash for verifier binding.

Revision 84 contains 91 bounded incidents. All are corrected or contained; no
incident is open. These rows describe observed workflow failures only and do
not support provider or model quality comparisons.
