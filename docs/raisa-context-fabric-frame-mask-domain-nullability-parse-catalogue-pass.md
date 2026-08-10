# Context Fabric frame-mask nullability parse/catalogue pass

Date: 2026-08-08

Status: fresh disposable PostgreSQL parse/catalogue gate passed; behavior gate remains closed

The independently accepted frame-mask domain recovery passed its first and only
fresh disposable PostgreSQL parse/catalogue rehearsal. Attempt
`9e006c12fcdea5844c2fe4ad` admitted the 424-statement inert SQL artifact, matched
every exact catalogue digest, verified rollback behavior, removed its owned
container and independently confirmed exact-ID absence.

The immutable pass is bound as follows:

- evidence SHA-256: `4583c8b0bca881964ba9a337cfd1b5c9ae535ad7cc78c06766f844ffe95d998a`;
- inert SQL SHA-256: `fc1c00ab7209a6689f4de29a14a134719a0110dfd3b556172781384332af41fa`;
- parse/catalogue contract SHA-256: `2993e547050212054b512f3ad5c6a9adaa64130f40f9cc93beb735079d28d840`;
- frame-mask type digest: `sha256:b7244669f109b81a3907c2f7a5397a253e8a374e261177a7567042d064c25c90`;
- container ID: `508b4adbc840710d801f2a281bfb883eb17cf81c112b5a8194139c9f0901c485`.

The historical canonical parse evidence remains byte-exact at SHA-256
`97d1385c6b617890cb0f155122e30eb283d49e42af1d44db385a2b9f4a9c2bec`;
the new result is preserved under a distinct immutable filename.

This result proves only the bounded provider-free parse, catalogue, rollback and
cleanup properties of the authored-synthetic artifact. It grants no application
migration, operational database, watcher/feed, runtime wiring, provider,
patient/clinical/product data, deployment, release, Pages or protected-ref
authority. The next gate is a deterministic behavior-contract rebind followed by
fresh independent review before any new behavior rehearsal.
