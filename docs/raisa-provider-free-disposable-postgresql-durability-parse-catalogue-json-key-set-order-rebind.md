# Disposable PostgreSQL parse/catalogue JSON key-set order rebind

Date: 2026-08-09

Status: characterization preserved; exact-digest reproduction pending

## Boundary

Renderer 2.0.13 changed only the deterministic ordering of seven fixed
`JSON_KEYS_EXACT` expected arrays. The corrected inert artifact is bound to
source `f620f31e4576003855afe824a385a86badf77120`, remains exactly 412
statements and 1,391,670 canonical LF bytes, and has SHA-256
`sha256:f4479c772f144973c1a1f373e16e0bcb3543fea6128c8054a282316ce5d02714`.
Its render-manifest file SHA-256 is
`sha256:d414fb3f0c9d5b8075e913f5608b6146b7b9ee43eb849c9272ccf48df3a2c706`.

This rebind is catalogue evidence only. It does not execute any entry point,
trigger, policy, application route or command.

## Non-accepting characterization

The first newly owned networkless PostgreSQL 16 run used contract mode
`characterization_only` at canonical contract SHA-256
`sha256:c351ddf9d8f64141d3226b772114c7b2d74bc652268ec4ed12b248e05078da72`.
It returned the required non-pass `catalogue_characterization_required` under
attempt `6033b191fdfb084894b58514`. The artifact installed atomically after the
fixed rollback case, and all seventeen allowlisted query digests were recorded.
The fifteen value-bearing digests, excluding the environment-bound `server`
and `extensions` facts, are now copied exactly into the fixed rehearsal
contract in `exact_digest_bound` mode at canonical SHA-256
`sha256:0037d3d2b11d25cb46b691e6962409b9bf025fe91b3aa1d928b0ac0a29ec0d74`.

The immutable characterization evidence has file SHA-256
`sha256:9e5338986fb4dea8ad5c7f0f0a96e624a525c93e127d507f651e68ca2b5b02b0`.
Exact container
`ef4ca866ac143928bdc59e31f2013c2a57d1f9f4896052a1a42b223e945a8aad`
was removed and exact-ID inspection independently returned the documented
absent condition.

## Required independent reproduction

The characterized digests do not accept themselves. After deterministic
contract/schema, historical-evidence, harness, Ruff and diff checks pass, a
fresh five-source receipt must bind one distinct newly owned
`postgres:16-bookworm` container with `--pull=never`, `--network=none`, no
ports or mounts, container-local tmpfs and exact-ID cleanup. Only exact
reproduction of all fifteen fixed digests may create a new parse/catalogue
pass and become a behavior-contract parent.

## Closed surfaces

This rebind grants no behavior acceptance, behavior attempt, applied Alembic
migration, operational database or credentials, source observation,
watcher/listener/feed, application/API/Diary wiring, patient/clinical/product
or protected data, provider call, command/write, deployment, production,
release, Pages or protected-ref movement.
