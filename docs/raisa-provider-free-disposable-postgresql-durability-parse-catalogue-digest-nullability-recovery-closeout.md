# Provider-free disposable PostgreSQL parse/catalogue digest-nullability recovery closeout

Date: 2026-08-08

Result:
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`

Accepted runtime source HEAD:
`06b8f55837457518b39de0bdbea71b60a2c6f921`

Terminal attempt: `02c203b477a0ff1006d08665`

## Accepted result

One fixed, provider-free, network-isolated local PostgreSQL 16 server accepted
the recovered durability artifact as a single installation transaction. The
artifact is exactly 1,404,420 canonical LF bytes and 412 statements at
`sha256:9407b8b641488b8c48ad51ef58c7ca2c3c15e83dca89da58de8f5726aef69f65`.
Its parse contract is bound at
`sha256:b1900c96779ff4225be286b51e0c8ecd0b6034177f08deff9d415e9a10c822cb`.

The deliberate invalid-suffix copy returned exact SQLSTATE `42601`, left zero
Fabric schemas and zero accepted roles, and the unchanged canonical artifact
then installed atomically. Exact read-only catalogue reconciliation matched
eight roles, thirty-two types, eighteen Fabric tables, 252 selected columns,
eighty-one non-trigger constraints, four indexes, forty-four policies,
twenty-four functions and fourteen triggers. All exact query digests matched;
the recovered `types` digest is
`sha256:8ec5eddfcb4cd14d62f783bfcfeb02004204630510b8913ce769a1c49a2135af`.

## Recovery evidence

Two earlier contained attempts had already proved atomic installation, then
failed closed at the sole `types` digest. Their exact owned containers were
removed and their absence verified. The final correction reconstructed all 32
PostgreSQL type rows, first reproduced the predecessor characterization digest
exactly, and proved the only row-level delta was
`digest_sha256.domain_not_null: true -> false`.

The terminal attempt used the already-local `postgres:16-bookworm` image with
pull disabled, network disabled, no host port, no mount and tmpfs-only storage.
It removed exact owned container
`ff4d0fabee78a3070bb6caa5c95e5d726050bda02764979a22e25ef178ea5530`
and verified absence.

The fresh exact-HEAD Gemini review passed the full-projection repair and left
its worktree clean. One sentence in that receipt later repeated the obsolete
artifact digest despite the receipt elsewhere naming the current digest and
all prescribed checks passing. AER-0127 preserves and rejects that sentence as
authoritative evidence. This closeout relies on the canonical contract, schema-
validated runtime evidence and deterministic local readback.

## Claim boundary and next descendant

This proves PostgreSQL-16 parsing, atomic installation/rollback and exact
catalogue shape for the recovered authored-synthetic durability artifact only.
It proves no function, trigger, RLS, idempotency or transaction behavior.

The next safe descendant is the already planned exact twenty-scenario,
provider-free behavior/transaction rehearsal after its six parent bindings are
rebound and independently accepted. Application migration or wiring,
operational credentials, patient/product data, providers, deployment,
production, Pages and protected refs remain closed.
