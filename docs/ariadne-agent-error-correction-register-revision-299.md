# Ariadne agent error and correction register — revision 299

Date: 2026-08-15

Timestamp: 2026-08-15T22:21:44+10:00 (Australia/Brisbane)

Revision 299 records AER-0338. The register now contains 338 bounded known
incidents, all corrected or contained by an explicit control.

AER-0338 preserves a pre-existing API Spine expectation drift that Sol's plan
preflight omitted. The worker exposed the mandatory legacy status-scaffold
test's expected OpenAPI SHA-256
`c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6`,
while the unchanged current appointment-command OpenAPI is
`c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a`.

Sol reproduced the identical 10-pass/one-failure result at plan source
`d500f1f86a83695cee0c2aac93aa2e2735e8f799` and worker candidate
`bc0b8adcdc9f1c11bb69abe1514677a92d17f9c7`. The legacy test and OpenAPI were
unchanged between them, so this is not a candidate regression.

The frozen repair is one test-only digest substitution from `c388…` to the
unchanged current `c549…`; it authorizes no product or OpenAPI change. The
mandatory legacy suite must then pass separately before candidate admission.
Future plans run every required legacy regression at the exact plan source so
pre-existing expectation drift is separated before worker evaluation.
