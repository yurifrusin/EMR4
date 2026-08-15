# Provider-free unmounted delete-confirm conditional-command kernel architecture and admission rehearsal plan

Date: 2026-08-15

Timestamp: 2026-08-15T11:50:49+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_unmounted_execution`

Task baseline: `12cda23eb69e9d4451ea23cc437989769e8073ac`

Target result: `raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_pass`

Reasoning level: Extra High for architecture freeze; High for mechanical
implementation, verification and closeout within this frozen boundary.

## Purpose

Close the exact destructive-command assurance gap found by the accepted
Reception One cancellation readiness review. Define and deterministically
rehearse one future dedicated delete-confirm transaction that owns locked
appointment truth, current staff authority, explicit confirmation, signed
proposal evidence, idempotency, reason preservation, audit, receipt completion
and fresh authorised readback.

The tranche is a pure authored-synthetic protocol. It imports, mounts and
executes no application route, database, product client, provider or command.

## API Spine classification

- Boundary: destructive REST/OpenAPI appointment command mutation.
- Canonical operation: `confirmAppointmentDeleteProposal`.
- Canonical family: dedicated `delete-confirm`, never status-confirm or raw
  compatibility delete.
- GraphQL: read-only and irrelevant to command authority.
- Events: acceleration hints only; never truth, authority, confirmation or
  command-success evidence.
- Evidence label: `authored_synthetic_provider_free_unmounted_protocol`.

## Frozen transaction contract

1. Authentication and route-role prechecks may reject early but never grant
   final cancellation authority.
2. A command-owned transaction locks one practice authority fence, then the
   exact practice-scoped appointment, then the operation-scoped idempotency
   record. The canonical order is `practice -> appointment ->
   idempotency_record`; the unused schedule-domain lock is skipped, not moved.
3. The backend freshly checks actor activity, exact practice binding, current
   role and cancellation capability after the appointment lock and again while
   all locks are held. The abstract practice fence represents authority
   stability only; a later physical-design gate must prove its database mapping.
4. Replay/conflict classification occurs only after current authority and
   target non-disclosure checks.
5. New execution requires `confirmed=true`, exact required warning
   acknowledgements, authentic unexpired signed evidence and exact binding of
   practice, actor, session, operation, appointment, pre-state version/status,
   waiting-area state, existing reason state, proposed reason fields, command
   digest and proposal freshness.
6. `status_reason_code` is required for new dedicated cancellation ingress and
   must be a current `Cancelled` reason code. `cancellation_reason` is optional,
   at most 500 characters, and preserved exactly after admission. Historical
   raw-route permissiveness is not inherited.
7. A first success atomically changes status to `Cancelled`, clears the waiting
   area, preserves both proposed reason fields, advances one state version,
   appends one attributable delete audit and completes one minimized receipt.
8. Every denial or injected pre-commit failure rolls back the claim and all
   appointment, audit and receipt effects. A lost response after commit does
   not roll back; same-key/same-digest retry returns the original receipt with
   no second mutation or audit.
9. The transaction returns a minimal command receipt. A separate fresh
   practice/action/resource-authorised read obtains display truth after commit;
   readback denial cannot undo or conceal the committed receipt.
10. Raw delete and delete-to-status fallback are separate labelled ingress
    candidates. Neither directly enters or weakens this kernel, and neither
    creates a second cancellation kernel.

## Required authored-synthetic scenarios

The closed packet must include at least:

- clean cancellation with and without a waiting-area assignment;
- structured reason required/invalid and optional free-text preservation;
- missing, false, tampered, expired or binding-mismatched confirmation evidence;
- stale status, state version, waiting area, existing reason or proposed reason;
- inactive actor, revoked role/capability, cross-practice target and target
  absence, all before receipt disclosure;
- same-key/same-digest replay and same-key/different-digest conflict;
- overlapping different-key attempts against one pre-state, with one commit and
  one stale loser;
- authority loss while waiting for locks;
- failures after staged mutation, audit and receipt;
- response loss after commit followed by effect-free replay;
- post-commit readback with current authority and readback denied after later
  revocation; and
- direct raw-delete, status-fallback, event-evidence and model-confirmation
  attempts rejected before command evaluation.

## Owned artifacts

- this plan, architecture and threat-model delta;
- one closed contract, JSON Schema and deterministic evidence packet under
  `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission/`;
- one pure Python validator/simulator;
- focused deterministic and plan guards;
- exact Ariadne receipts, independent review, closeout, Sol acceptance, Yuri
  mailbox summary and Continuity/Compass lifecycle artifacts after passing.

## Acceptance

The tranche passes only if:

1. the fresh five-source Ariadne receipt passes;
2. the packet validates against a closed schema and exact source hashes;
3. all canonical decision scenarios return their exact admission, outcome,
   non-disclosure, planned-effect and readback shapes;
4. all schedules use the exact lock order and recheck current authority before
   replay disclosure and immediately before first effect;
5. only a first `committed` result changes the synthetic appointment, audit and
   receipt state, and all three publish atomically;
6. same-key replay, different-key overlap, revoked-authority waiting,
   pre-commit rollback and post-commit response-loss schedules pass;
7. the committed appointment, audit and receipt preserve the exact structured
   and optional free-text cancellation reasons and clear waiting-area state;
8. fresh readback is separately authorised and never used as transaction proof;
9. raw delete, status fallback, events and model/channel confirmation cannot
   invoke or satisfy the dedicated kernel;
10. at least 40 independent hostile mutations fail closed;
11. focused API Spine and cancellation tests, canonical repository checks and
    whitespace pass;
12. one fresh Gemini 3.6 Flash/high exact-candidate veto passes after
    deterministic admission; and
13. protected refs, `docs/branding/` and every unrelated untracked file remain
    unchanged.

## Parallelism-efficacy allocation

- **Sol:** freezes architecture, acceptance, source bindings, worker packet,
  candidate admission, recovery, closeout, Continuity/Compass and Git.
- **DeepSeek V4 Flash/high:** after plan freeze, receives one bounded mechanical
  package for the pure simulator, closed contract/schema and focused tests. It
  receives no architecture, acceptance, integration or Git-push authority.
- **Gemini 3.6 Flash/high:** reserved for one fresh exact-candidate veto after
  deterministic admission.
- **Native subagents:** declined; the compact state machine and shared owned
  files leave no independent package with positive net leverage.

Reassess at implementation packet freeze, material recovery, pre-verifier and
closeout.

## Recovery

One bounded DeepSeek correction is permitted only for a mechanical defect that
does not change the frozen order, reason policy, outcomes or claim boundary. A
conceptual defect transfers immediately to Sol under the recovery lease.
Deterministic failure forbids Gemini admission until repaired and rerun.

## Forbidden surfaces and claim boundary

No application import/edit, mounted route, OpenAPI/GraphQL/schema change,
database driver/source/transaction, watcher/event runtime, product client/UI,
provider/model call except the final authorised read-only veto, patient/product/
clinical/protected data, credential/IAM/network, executable product tool,
command/write, deployment, production, release, Pages or protected-ref action.

A pass proves only the closed abstract contract and in-memory schedules. It does
not prove PostgreSQL representation, real locking/concurrency, mounted-route
convergence, product behavior, Reception One cancellation UI or production
readiness. The next safe gate, if this passes, is a provider-free unmounted
delete-confirm physical representability review.
