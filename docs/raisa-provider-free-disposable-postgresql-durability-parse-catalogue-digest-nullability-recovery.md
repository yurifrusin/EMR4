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

The first re-bound run admitted the revised artifact and reached catalogue
comparison, then failed closed because the frozen `types` query digest still
encoded the old domain-level not-null flag. Its mismatch detail digest is
exactly the digest of query id `types`; all other catalogue expectations remain
unchanged. The repaired contract binds the deterministically derived `types`
digest `sha256:864bc5fb6d068f01c6e44c6ca95b3c188b7b74c10839ffd83f2e64b48e172243`.
Another run remains closed until fresh deterministic and exact-HEAD independent
acceptance.

That first replacement digest was derived from an incomplete simplified type
projection and the resulting contained run failed closed at the same `types`
comparison. A full reconstruction of all 32 PostgreSQL type rows now anchors
itself by reproducing the original accepted characterization digest exactly;
changing only `digest_sha256.domain_not_null` from `true` to `false` produces
`sha256:8ec5eddfcb4cd14d62f783bfcfeb02004204630510b8913ce769a1c49a2135af`.
The failed owned container was again removed and its absence verified. No
further run is eligible before deterministic checks and a fresh exact-HEAD veto.

A pass establishes PostgreSQL 16 parse, atomic installation and catalogue shape
for this revised inert artifact only. It grants no application migration,
behavior acceptance, product database, provider, patient/clinical data, runtime
wiring, deployment, Pages, release or protected-ref authority.
