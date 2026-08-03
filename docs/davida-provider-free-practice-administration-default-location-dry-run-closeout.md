# Closeout: Davida default-location dry-run proposal

Date: 2026-08-03

Result: `provider_free_practice_administration_default_location_dry_run_pass`

## Accepted result

Davida now has one provider-free, unoccupied and unmounted deterministic dry
run for exactly `PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION`. It consumes one
accepted practice-administration context and one canonical selector-only
candidate, resolves one opaque active practitioner and location, and releases
only a context-derived before/after `proposal_candidate` with
`status=dry_run_only`.

Current-null is preserved and same-location rejects as `no_change`. Context,
scope, revision, freshness, reference-kind and canonical-type failures reject
atomically with no partial proposal, repair or retry. Human confirmation is
required, while command-ready, confirmation, apply, write, provider, model,
database, network and model-to-database authority remain false.

## Evidence, repair and verification

- Native bounded implementation produced initial candidate
  `83f41e5e66689ca6504aa8c2dcfc34b8bf6d78ec`.
- Root review found three exported but producer-unreachable rejection reasons.
  Separate repair `6281ad35b7c744ae7f1cf8a7de8df7bc7aaec7c2`
  narrowed the public union and contract to exactly fourteen reachable reasons
  without weakening schema or context-boundary admission.
- Root-generated evidence candidate
  `21e11b33e2c873be0ee2b12db0e57b599e24c8a1` records 60/60 cases, zero
  failures, 2 released and 54 rejected. Its final task-branch replay is
  `8692d100` after implementation replay `a3b23bc9` and repair replay
  `3e2f9247`.
- The first fresh Gemini review returned `pass` but was rejected as evidence
  because it ran an unlisted evidence-writing command and falsely described
  25/25 cases. The candidate stayed clean. A genuinely fresh corrected Gemini
  3.6 Flash/high project ran only the listed checks, reported the exact 60-case
  accounting, reproduced 140 tests and Ruff/diff/ref checks, returned one
  `pass`, and left the exact candidate unchanged.
- The integrated pair passed 289 serial tests. The evidence reproduced
  byte-for-byte at SHA-256
  `6a997f496108ef78d09369a7d0838ee3ba8c2116e14c6cf99da08d47792ce6b1`;
  Ruff and `git diff --check` passed.

## Claims not made

This establishes no occupied Davida model, generated natural-language
interpretation, memory/RAG, database/network/clock, mounted route, GraphQL
mutation, REST command, confirmation evidence/envelope, idempotency,
concurrency control, audit/outbox write, actual apply, real identity/data,
patient/clinical/document data, deployment, production or release.

Protected refs/evidence and `docs/branding/` remained untouched. The product
Continuity/Compass map remains 206/187 because this result is unmounted and
effect-free.

## Next bounded lane step

The next safe candidate is architecture-only: freeze the backend-owned REST
proposal-to-confirm boundary for a future default-location change, including
fresh authorization, expected aggregate version, idempotency, atomic audit/
outbox and exact stale/replay rejection. It must remain non-executing and grant
no actual administrative apply/write authority; implementing or mounting that
command remains a material Yuri-owned gate.
