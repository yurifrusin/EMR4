# DeepSeek Harness structured startup diagnostic seam — lay and technical summary

Date: 2026-08-21

## Lay summary

The new diagnostic mechanism is accepted at source
`af22b3e7b2ce3ece15dd6d8530688d19380c1403`. Instead of trying to remember
more error phrases, a future launcher can take a small, safe reading directly
from the JavaScript error before Harness turns it into text. It records only a
few approved categories and still lets the original failure happen normally.

Nothing was rerun: no Harness, DeepSeek, broker or provider was contacted, and
attempt 003 remains honestly unclassified. The next safe test is to exercise
the wrapper with invented local failing modules in Node, without importing
Harness. That will tell us whether the designed gear really writes, sanitizes,
rethrows and cleans up as intended.

The canonical clockwork acceptance is bound at full source
`4b09bc3665bed77ed7d8cd6f50dc793d1e35d2de` after the byte-exact rollback
lease was recorded.

## Technical summary

The candidate binds six installed `@deepseek-ai/dsh` rc.7 source files and
freezes a generated ESM wrapper around `await import(bin.js)`. The wrapper
allows at most six cause nodes, seven error kinds, a closed Node/Cordis code
allowlist, three `ConfigFileError` stages, four source-message coordinates and
bounded aggregate shapes. It uses one `wx` sidecar write, reads no stack,
retains no dynamic string/path, and rethrows the identical value.

A separate v2 pre-HMR terminal and future controller envelope avoid changing
the accepted v1 terminal or consumed controller. Eleven hostile fixtures and
52 focused provider-free tests pass; Ruff, compilation and deterministic
source re-check pass. Recovery counts are zero for Node, Harness, broker,
worker, model, provider and raw attempt-stream access.

Six low-severity workflow corrections were caught fail-closed: the first draft
crossed the accepted-source boundary, the first suite repeated a known stale
historical equality selection, the first closeout intent used two invalid
schema shapes, and the first restored receipt repeated machine-owned Git IDs in
prose. A follow-up check also rejected two freehand incident-stage labels.
The first publication then omitted one explicit closed-boundary token; its
postcondition failed and the clockwork restored the previous generation byte-
exactly. Register revision 579 records all six; protected state and the final
accepted sources remain unchanged.
