# Integrated-runner accepted guard-graph materialization failure report

Date: 2026-08-22

Timestamp: 2026-08-22T19:57:09.0815687+10:00 (Australia/Brisbane)

Result: `fixture_result_rejected`

The single permitted provider-free Node fixture was consumed. The process
exited 0 with 756 stdout bytes, zero stderr bytes and no retained stream
content. The controller rejected the typed result because it did not equal the
frozen success vector. No retry, resume, fallback or second fixture is
authorised.

The retained stdout SHA-256 is
`6e75c083f6b42d5c828d53c7f16a11ae09897023bf0a8139abde615c674225ff`.
A provisional process-free calculation found that the source-defined success
JSON with `preset_root_reads: 4` and `hook_installations: 5` has exactly those
756 bytes and that hash, whereas the contract expected only the weaker root
floor and exactly three hook installations. This is diagnosis evidence only;
it is not accepted terminal evidence and does not reclassify the consumed
attempt.

The disposable root is absent. Native Harness, broker, worker, model,
provider, network, database, Docker and product-target counts remain zero.
