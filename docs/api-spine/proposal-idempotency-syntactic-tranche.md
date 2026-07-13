# Proposal Idempotency Syntactic Tranche

| Item | Value |
|---|---|
| Tranche | S19-S21 |
| Boundary | Appointment proposal commands only |
| Authority | Syntactic request discipline; no replay or write authority |
| Status | Approved for bounded implementation |

## Goal

Align the four canonical appointment proposal routes with the existing OpenAPI
contract by requiring a nonblank `Idempotency-Key`. Proposal evaluation remains
deterministic and non-mutating. Only confirmation routes may use the durable
appointment command replay ledger.

## Sprint Split

- **S19:** share the proposal-key validator and bind it to create, update,
  status, and delete proposal routes. Preserve `400 idempotency_key_required`.
- **S20:** add focused dynamic and static coverage for missing, blank, and
  present keys across all four families. Prove proposals do not claim or
  complete replay-ledger entries and do not acquire appointment-write authority.
- **S21:** reconcile API Spine continuity/drift artifacts and run focused
  appointment plus API Spine acceptance.

## Boundaries

- Do not change confirmation route behavior or durable replay semantics.
- Do not change raw compatibility write routes.
- Do not add a model, migration, GraphQL mutation, provider call, external
  client, historical-diary/H-series input, memory/RAG/GraphRAG wiring,
  deployment behavior, or new write authority.
- `/proposals/waiting-area/{appointment_id}` is not one of the four canonical
  OpenAPI proposal paths and remains deliberately unchanged pending a separate
  client-readiness decision.

## Acceptance

- all four canonical proposal families reject missing or blank keys with the
  typed error and accept a nonblank key;
- proposal execution creates no appointment command replay-ledger entry;
- proposal handlers contain no `claim_appointment_command()` or
  `complete_appointment_command()` call;
- existing confirmation idempotency and raw compatibility boundaries remain
  green;
- the continuity index distinguishes syntactic proposal discipline from
  confirmation replay enforcement.

## Allocation

- DeepSeek V4 Pro: coordinator review only.
- DeepSeek V4 Flash: bounded route, test, and continuity implementation in an
  isolated worktree.
- Sol: API-boundary review, correction, protected-master integration, commit,
  push, and closeout.
- Gemini review is not allocated because this tranche has one tightly coupled
  backend contract surface rather than a distinct independent UX/adversarial
  lane.
