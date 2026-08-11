# Ariadne agent error and correction register — revision 230

Date: 2026-08-11

Revision 230 adds AER-0265. The register now contains 265 bounded known
incidents.

## AER-0265 — AES-C5 two-destination manifest violated AES-C0

The first frozen AES-C5 plan assigned the local authoritative read and Sydney
provider inference to one immutable generation with two destinations even
though the accepted AES-C0 contract permits exactly one destination per
generation. The first provider-free candidate exposed the conflict but bypassed
the AES-C1 schema validator and evaluated the invalid packet directly. Sol
rejected it before any product, database, credential, cloud or provider action.

The corrected plan uses two separately immutable single-grant,
single-destination generations with no lease or budget transfer. The provider
generation is created only after the source generation is exhausted and
revoked, and binds the fresh minimized frame digest. Both attempts must pass
the complete inherited AES-C1 schema validator before evaluation. The same
recovery rebinds optional `roleLabel` and nullable/object `defaultLocation` to
the exact application response contract.
