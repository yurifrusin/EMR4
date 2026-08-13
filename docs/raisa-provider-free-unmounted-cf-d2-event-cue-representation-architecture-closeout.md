# Provider-free unmounted CF-D2 event and cue representation architecture closeout

Date: 2026-08-13

Timestamp: 2026-08-13T17:46:24+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `16ec7993ee3c46d83772f47aa7dab61fc1fcb7ed`

Result: `raisa_provider_free_unmounted_cf_d2_event_cue_representation_architecture_pass`

## Outcome

The accepted event/cue semantics now have a small relational home without
opening a database. Seven abstract relations represent only opaque partition
coordinates, immutable classification receipts, payload-free refresh
obligations, contiguous checkpoints, dispatch attempts and fresh-read
reconciliation receipts.

The architecture separates representability from enforcement. Keys,
references and row checks can reject malformed identities and payloads. Five
explicit future transaction protocols must still prove atomic receipt/
obligation creation, safe pending-only coalescing, contiguous checkpoint
movement, fenced ordered dispatch and delivered-only reconciliation. Current
Diary truth and command authority remain external and superior.

## Verification

- all seven exact relation shapes and five protocol descriptions pass their
  closed JSON Schema and semantic gate;
- all 12 authored-synthetic row families pass;
- all 52 hostile contract variants and 28 hostile row variants fail closed;
- canonical contracts and row fixtures remain byte-stable across hostile
  evaluation;
- 92 focused representation/admission/observability/source-truth/API/latch
  checks pass;
- Ruff passes;
- the canonical fast profile passes 193 tests and compilation of 209 maintained
  Python sources, Diary JavaScript syntax and Git whitespace; and
- exact source and origin task branch are published at
  `16ec7993ee3c46d83772f47aa7dab61fc1fcb7ed`, with local/origin `master` and
  `handoff/current` unchanged at protected
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

No external worker or provider was selected. The relation contract, semantic
classification and row fixtures form one tightly coupled bounded architecture
artifact, so Sol retained it under the worker-economy rule.

## Claim boundary

This proves only inert representability. It generated no SQL and proves no
PostgreSQL type, catalogue, foreign key, transaction, lock, isolation,
concurrency, source observation, persistence, restart, unknown commit, delivery
transport, timing, retention, rotation, purge, application wiring,
product-data safety, deployment or production behavior.

Events and cues remain acceleration hints. They cannot update Reception One or
authorize a command. A consumer still performs a fresh authorised read, and
every consequential command still checks current authority and source truth.

## Next tranche

The next dependency-satisfied tranche is the exact provider-free unmounted
inert-DDL lowering. It may render deterministic SQL text from these seven
relations and verify structural coverage only. It receives no database
connection, migration execution, source access, watcher, persistence,
operational retention, restart, delivery, command or product data.

Protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient clients, real identity, provider/ADC, credentials/IAM/network,
executable tools, commands/writes, deployment, production, release, Pages and
protected refs remain closed. `docs/branding/` and all unrelated untracked
files remain preserved and excluded.
