# Disposable PostgreSQL parse/catalogue admission-receiver binding-RLS rebind

Date: 2026-08-10

Status: nonaccepting characterization passed; exact reproduction pending

The fixed parse/catalogue harness is rebound to renderer 2.0.17 source commit
`30ff6b01a54c339e3045977cda909628841fe57e` and its inert artifact:

- `1,419,573 canonical LF bytes`;
- statement count `421`;
- SQL SHA-256
  `sha256:1d53c7ac1cd9a9fb19faafcca0ebcf8dacadf238f62df873d2d3fc78c657b407`;
- manifest SHA-256
  `sha256:2042eb8055cc55cd7cb4396093a897b4df5f86c5a1910dbca677a241c2d7325b`.

The temporary characterization-only rehearsal contract has canonical SHA-256
`sha256:8cb7862d66ce805d8af2d4aea96e8e46df92040cfc44a263da6d3245b5a3f02c`.
It contains no expected catalogue digest and cannot produce acceptance. Its
only permitted purpose is to measure the exact PostgreSQL 16 catalogue delta
caused by the policy predicate change before a distinct exact reproduction.

One newly owned networkless PostgreSQL 16 characterization returned the
required nonaccepting result `catalogue_characterization_required` as attempt
`bef2c8193761c8bcee4e5af2`. Its immutable evidence SHA-256 is
`sha256:41f065c805fdc3cc140ded68baf180bfd88ae3c34bbcd962cc140e9d359d814d`.
Exact container
`a1d64af025b200578f73cb020e357befc8176969534fd8a006eb3dfe137952e4`
was removed and exact-ID absence verified. Relative to the prior accepted
catalogue, only the `policies` digest changed, to
`sha256:5bd0a6629eaa4a734e01d786781ea62121e887581b38558b33677bd79c752a0f`.
All fourteen other acceptance digests are unchanged.

The resulting exact-digest contract has canonical SHA-256
`sha256:cf746ed8824ef8853677020e90083c2b4bfe1b4096a36ad7735cfeabf0eb4b91`.
It is not accepted until a new, distinct container independently reproduces
every fixed digest and cleans up exactly.

Any eligible run is limited to one newly owned `postgres:16-bookworm`
container with `--pull=never`, `--network=none`, no port or mount, tmpfs data,
the four empty authored-synthetic prerequisite relations and exact-ID cleanup.
It must not list or touch any unrelated container. No function/trigger/RLS
behavior, applied migration, operational database or credential, watcher/feed,
patient/clinical/product data, provider call, application wiring, command,
deployment, release, Pages or protected-ref authority is opened.
