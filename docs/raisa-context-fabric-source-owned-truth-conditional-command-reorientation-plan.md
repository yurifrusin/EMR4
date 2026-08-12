# Raisa Context Fabric source-owned-truth reorientation plan

Date: 2026-08-12

Source HEAD: `0a5c9d336f7e7cba08fddb94ab0233e399474cb8`

Status: `frozen_for_provider_free_architecture_execution`

## Purpose

Freeze the smallest safe programme reorientation after the stopped CF-D2
restart/unknown-commit work. Correctness belongs to source-owned atomic
conditional commands. The Context Fabric remains an expiring read-only
projection, and committed events remain acceleration hints that cause fresh
authorised reads. Restart-safe cue delivery is retained as a later named
extension rather than a prerequisite for correct writes.

## Selected boundary

This tranche is repository-only architecture over authored-synthetic examples.
It separates four proofs that a client or Bureau must not conflate:

1. a backend-minted freshness precondition;
2. distinct human or policy confirmation evidence where required;
3. command idempotency identity; and
4. append-only audit evidence and deterministic readback.

For update, status and delete, the command service must lock the target row and
recompute current truth before mutation. Create has no target row, so it must
instead fence the relevant schedule-conflict domain, use a canonical lock
order, and retain the final database conflict check. A token alone never
closes the time-of-check/time-of-use race.

Legacy raw compatibility routes remain mounted and unchanged in this tranche.
Their eventual migration is to the same backend conditional-command kernel,
without pretending that implicit freshness is equivalent to explicit human
confirmation.

## Owned files

- `docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-plan.md`
- `docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-architecture.md`
- `docs/security/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-threat-model-delta.md`
- `orchestration/continuity/raisa-context-fabric-source-owned-truth-conditional-command-reorientation/architecture-contract.json`
- `orchestration/continuity/raisa-context-fabric-source-owned-truth-conditional-command-reorientation/architecture-contract.schema.json`
- `scripts/raisa_context_fabric_source_owned_truth_reorientation_acceptance.py`
- `tests/test_raisa_context_fabric_source_owned_truth_reorientation.py`
- bounded amendments to the Context Fabric direction, implementation plan and
  API Spine compatibility map;
- exact receipts, review, closeout, Yuri mailbox summary, Continuity/Compass
  updater and focused continuity tests if this architecture passes.

## Forbidden surfaces

- no runtime route, broker, adapter, watcher, listener or worker change;
- no database, source, migration, trigger, transaction or persistence action;
- no patient, clinical, product-derived, financial or licensed content;
- no provider/model call before deterministic readiness and no provider-derived
  architecture authority;
- no credential, IAM, metadata, network, executable tool, command or write;
- no deployment, production, release, Pages or protected-ref movement; and
- no broad Git staging or staging of `docs/branding/` or unrelated untracked
  files.

## Deterministic acceptance

The tranche passes only when:

1. one closed schema validates one closed normative contract;
2. current source truth, Context Fabric frames, cue delivery and commands have
   disjoint authority statements;
3. events cannot prove current truth, authority or command success;
4. every command family requires current authority and an atomic precondition;
5. create uses a schedule-conflict-domain fence rather than a nonexistent row
   lock;
6. freshness, confirmation, idempotency and audit remain distinct;
7. exact winner, replay, stale, conflict, revoked and validation outcomes are
   typed and fail closed;
8. legacy compatibility migration preserves ordinary user workflows while
   converging on the conditional-command kernel;
9. later Durable Event and Cue Delivery is named with CF-D1 retained as
   evidence and CF-D2 reopened only under a new observability-first plan;
10. at least sixteen independent hostile mutations are rejected;
11. focused tests, repository static checks and Git whitespace pass; and
12. protected refs and all pre-existing untracked files remain unchanged.

## Next safe descendant

After acceptance, the next safe descendant is a provider-free, unmounted
conditional-command admission rehearsal. It may exercise authored-synthetic
preconditions, locks, outcomes and legacy-route classifications only. It may
not change a route, open a database, consume a real event or issue a command.
