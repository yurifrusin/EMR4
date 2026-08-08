# Disposable PostgreSQL parse/catalogue digest-nullability recovery

Date: 2026-08-08

Status: runtime-closed rebind candidate

The independently accepted artifact repair at
`580c1d05ed150cdfd63549f1a35e61c72a41cb20` changes only effective
`digest_sha256` domain nullability. The parse/catalogue contract is rebound to
its 1,404,420 bytes and SHA-256
`sha256:9407b8b641488b8c48ad51ef58c7ca2c3c15e83dca89da58de8f5726aef69f65`.

The prior PostgreSQL evidence remains immutable evidence about the preceding
artifact and cannot establish the revised artifact. After deterministic checks
and a fresh exact-HEAD veto, exactly one contained parse/catalogue rehearsal may
run with the existing fixed `postgres:16-bookworm`, pull-never, network-none,
no-port, no-mount, tmpfs-only and exact-cleanup profile.

A pass establishes PostgreSQL 16 parse, atomic installation and catalogue shape
for this revised inert artifact only. It grants no application migration,
behavior acceptance, product database, provider, patient/clinical data, runtime
wiring, deployment, Pages, release or protected-ref authority.
