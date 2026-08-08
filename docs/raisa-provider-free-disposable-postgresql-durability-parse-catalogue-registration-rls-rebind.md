# Disposable PostgreSQL parse/catalogue registration-RLS rebind

Date: 2026-08-08

Status: bounded catalogue characterization candidate; behavior remains closed

The exact parse/catalogue rehearsal is rebound to source commit
`2c22d6f56d0081ebfae5a5585088381e1219d7f8`, whose canonical inert SQL is
1,402,659 LF bytes with SHA-256
`sha256:34d321adce220a94473e3cd74173f7b0ffc37441b2e4dd24699ca18b86c7e760`.
It contains exactly 412 statements.

The structural repair adds `LIFECYCLE` only to the six exact forced-RLS
`SELECT` or `INSERT` predicates needed by the already accepted generation-
registration entry point. Matching `UPDATE` policies and every direct grant,
function body, trigger, role, relation and privilege ceiling remain unchanged.

Because PostgreSQL owns the canonical rendering of `pg_policies`, one
networkless disposable characterization is required before the revised policy
digest can be independently bound. Characterization cannot pass the parse gate
and its evidence must prove exact-ID cleanup. After binding the observed policy
digest, a second newly owned container must reproduce all exact catalogue
digests before any behavior contract or scenario is eligible.

This rebind opens neither behavior nor an applied migration. It grants no
application, API, Diary, product-data, provider, tool, command, deployment,
release, Pages or protected-ref authority.
