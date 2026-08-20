# Node fixture attempt 001 canonical-JSON recovery

Date: 2026-08-21

Timestamp: 2026-08-21T09:04:02.5098041+10:00 (Australia/Brisbane)

Attempt source: `3a12bb88e23cb90a7f7a0ea38c8a67cd9542b2fa`.

## Exact negative result

Four serial Node 24.18.0 observers imported only authored local fixture
packages through the generated wrapper. All four caught the identical thrown
JavaScript object. The pre-existing-sidecar scenario retained its exact bytes,
all stdout/stderr byte counts were zero, all disposable roots were absent at
terminal readback, and Harness/broker/worker/model/provider counts were zero.

The three expected diagnostics were semantically safe but rejected by the
Python reader with exactly `diagnostic_canonical_bytes_required`. The wrapper's
`JSON.stringify` preserved JavaScript insertion order while canonical reader
bytes use recursive lexical key order.

## Bounded correction

The frozen plan admits only one correction for this result: an opt-in recursive
key-sorting serializer applied to the already sanitized diagnostic immediately
before `JSON.stringify`. The accepted default wrapper mode remains byte-
identical for historical evidence. The correction changes no diagnostic key,
enum, traversal, exclusive write, import target, rethrow or terminal rule.

Attempt 001 remains immutable negative evidence. Attempt 002 requires a new
exact source, fresh preexecution receipt and the same four serial scenarios.
No DSH import, native Harness, DeepSeek/model/provider or product authority is
opened.
