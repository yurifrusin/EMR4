# Durability inert DDL admission-receiver binding-RLS rebind

Date: 2026-08-10

Status: deterministic inert-artifact regeneration candidate; execution closed

Renderer 2.0.17 now binds structural contract
`sha256:ff64b568d65d243ad5bb3dd8159063f47732b0b360efcc12f58d3b28ceb00d9a`
and body contract
`sha256:edbc7f2361f8b5a2812dcff2a7cdf81bef7bd2a6d280be5a9023571c5121508e`.
The body differs from its predecessor only by the structural parent digest;
all typed body programs remain unchanged.

The regenerated inert SQL changes only the rendered `pol_cf_17_select`
predicate plus deterministic provenance and artifact digests. The policy
admits exactly `context_schema_owner` or `context_admission_receiver` as
`current_user`, then still requires `database_login = session_user` and the
same transaction-time active interval. Forced RLS, existing direct privileges,
the distinct non-login admission owner and every other statement remain
unchanged.

The artifact is still unmounted, inert evidence only. No migration is applied
and no database, product/patient, watcher/feed, provider, application/API/
Diary, command, deployment, release, Pages or protected-ref surface is opened.
