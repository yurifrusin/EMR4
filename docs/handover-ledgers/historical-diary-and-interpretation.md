# Historical Diary and Interpretation Ledger

## Raw historical diary boundary

Yuri holds roughly 58,000 original diary snapshots. Raw files may contain PHI
and must remain local and ignored under `local_data/historical-diary-trove/`.
Do not commit them, transmit them to an external model/provider, retrieve from
them at runtime, or fine-tune on them.

H1-H21 established read-only local extraction, neutral aggregate validation,
timeline/event summaries, and derived neutral graphs. R26-R30 separated the
source-safe H-series profile layer, native Diary action grammar, and synthetic
replay consumer from Bernie executable scenarios.

Yuri approved H15 on 2026-07-06 only for the bounded payload in
`docs/historical-diary-trove-h15-approved-gate.json`. That approval does not
authorize broad 58k-file processing, provider transmission, runtime memory,
RAG/GraphRAG, database writes, or corpus promotion beyond its stated scope.

## Interpretation harness

H40-H69 built provider-free authored-fixture interpretation, projected frames,
consistency guards, aggregate reporting, readiness checks, runtime gates,
isolation guards, and proposal-surface checks. Current runtime/provider/trove
access remains blocked. H69 also made legacy worker packet polling tolerant of
non-UTF-8 bytes; it did not open product authority.

The native backend remains authoritative for availability, collisions,
patient/practitioner identity, status transitions, signed confirmation,
mutations, audit, and route permissions. Bernie may explain, clarify, select
bounded read requests, and propose actions; it may not invent codes, assume an
ambiguous entity, claim a completed write, or bypass staff confirmation.

## Primary documents

- `docs/historical-diary-trove-plan.md`
- `docs/historical-diary-trove-h15-approved-gate.json`
- `docs/historical-diary-trove-h15-approval-decision.md`
- `docs/bernie-interpretation-harness-scaffold.md`
- `docs/bernie-interpretation-harness-runtime-gate.json`
- `orchestration/bernie_release_gates.md`
- `docs/receptionist_review_r29.md`
- `docs/receptionist_review_r30.md`

The immutable pre-compaction handover contains the full H1-H69 chronological
ledger and exact historical counts.
