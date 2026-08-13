# Provider-free unmounted CF-D2 event and cue admission rehearsal closeout

Date: 2026-08-13

Timestamp: 2026-08-13T17:00:06+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `a7c6f7a66b06fbc065ae8a6eede7fa8baaee1b6b`

Result: `raisa_provider_free_unmounted_cf_d2_event_cue_admission_rehearsal_pass`

## Outcome

The smaller CF-D2 design now has executable, provider-free admission semantics
without pretending to have a runtime. One pure in-memory state machine proves
when an authored-synthetic event position, terminal classification and
payload-free cue obligation may enter state, when they must be rejected, and
when the checkpoint may advance.

The proof keeps the source-owned-truth correction intact. Events and cues are
acceleration hints. They cannot provide appointment truth, update Reception
One directly or prove a command succeeded. A delivered cue supports only one
fresh authorised scoped read attempt; every consequential command still
rechecks current authority and source truth.

## Behavior proved

- Exact duplicates reuse the original immutable receipt and obligation.
- Divergent reuse of an occupied position returns `identity_conflict` without
  changing any normalized state.
- Out-of-order positions may be retained, but the checkpoint stops at the
  first missing lower position and advances only after the gap is filled.
- `cue_required` admits receipt and obligation atomically; a deliberate
  obligation gap admits neither.
- Suppressed and rejected terminal receipts can advance a contiguous
  checkpoint but create no cue.
- Only adjacent pending obligations with the same partition, consumer and
  reason coalesce; exact lower and upper positions are preserved.
- A stale lease generation is fenced without mutation.
- Unknown and cross-epoch lag remain nonnumeric; zero is possible only as an
  exact same-epoch calculation.
- Projection refresh and local-state clearing require a delivered obligation,
  authorised scope and a completed fresh read. Authorization, source and stale-
  session failures retain the truthful old display.

## Verification

- all 22 frozen canonical scenarios pass;
- all 60 hostile contract and candidate variants fail closed;
- every denied hostile candidate retains an identical complete state digest;
- the parent CF-D2 observability contract and API Spine authority gate pass;
- 91 focused admission/observability/source-truth/API/latch checks pass;
- Ruff passes;
- the canonical fast profile passes 193 tests and compilation of 209 maintained
  Python sources, Diary JavaScript syntax and Git whitespace; and
- exact source and origin task branch are published at
  `a7c6f7a66b06fbc065ae8a6eede7fa8baaee1b6b`, with local/origin `master` and
  `handoff/current` unchanged at protected
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

No external worker or provider was selected. The plan, state engine and hostile
gate are one tightly coupled deterministic artifact, so Sol retained the work
under the worker-economy rule.

## Claim boundary

This proves only pure admission behavior. Repository JSON evidence is a test
artifact, not persisted operational state. The tranche proves no database
representation, transaction, source observation, listener, process ownership,
restart, unknown commit, dispatch transport, latency, retention, rotation,
purge, application wiring, product-data safety, deployment or production.

## Next tranche

The next dependency-satisfied tranche is a provider-free unmounted event/cue
representation architecture. It will lower the already-proved facts and
transitions into an inert relational design and deterministic representability
checks only. It receives no database connection, migration execution, watcher,
source access, persistence, restart, delivery, command or product data.

Protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient clients, real identity, operational retention, provider/ADC,
credentials/IAM/network, executable tools, commands/writes, deployment,
production, release, Pages and protected refs remain closed. `docs/branding/`
and all unrelated untracked files remain preserved and excluded.
