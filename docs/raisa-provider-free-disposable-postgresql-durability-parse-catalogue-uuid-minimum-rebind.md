# Provider-free disposable PostgreSQL parse/catalogue UUID-minimum rebind

Date: 2026-08-09

Status: exact-bound PostgreSQL 16 reproduction passed; source commit pending

## Purpose

Bind the disposable PostgreSQL 16 parse/catalogue harness to renderer 2.0.12
source `c97ea3eb935997ace3586aa2ff52cf33dabbfd6a` and its 412-statement,
1,391,670-canonical-LF-byte inert artifact at SHA-256
`sha256:eeabfc39bf0b0c1073f57e97835440b394391161bec3ddc62be6e186fd7af6d8`.
The render-manifest file SHA-256 is
`sha256:4e3d80f2855bcf97f9e0fdce9630b42b9f2b67454df77e6954cbb79e8e3aac11`.
The exact catalogue parent has 1,391,670 canonical LF bytes and statement
count `412`.

The only intended SQL semantic change from the preceding accepted interval
artifact is replacement of the two UUID `pg_catalog.min(s.stream_id)` calls
with typed ascending `NULLS LAST LIMIT 1` selection. The two bigint
`pg_catalog.min(s.last_contiguous_position)` calls and every catalogue object,
role, grant, policy, trigger, entry point, SQLSTATE and typed body parent remain
unchanged.

## Two-run rule

The first newly owned networkless container is characterization only. It may
record catalogue digests but cannot be accepted. After exact digests are bound
into the contract, a separate newly owned container must reproduce them under
exact mode and verify exact-ID cleanup. Only that second pass can become the
accepted parse source for the behavior contract.

No function/trigger behavior, RLS behavior, application migration/runtime,
provider/product contact, patient/product/protected data, command/write,
deployment, release, Pages or protected-ref authority is granted.

## Exact reproduction

The separate exact-bound attempt `988bb667765158c33e219d8d` reproduced the
fifteen accepted catalogue query digests and emitted pass evidence at SHA-256
`f14c406ca460ba893e66fed3150e759f63d9631c976a95fbb03faae7f1f381c8`.
Exact owned container
`d1fa9e1501b07e5079e9bb6c9325e67399dd36ee922795e346fac07120bcc95b`
was removed and exact-ID absence was independently verified.
