# Bernie Stage 1 Tranche D — Sol Acceptance

Date: 2026-07-19

Reasoning level: `Sol High`

Decision: `revision_required`

Stage 1 decision: **no `stage1_pass`**

## Rehydration and source binding

This fresh Tranche D context read the live handover, every acceptance document
named by the Current Baton, the frozen Stage 1 plan and Sol review, the current
strategic transition review, the protected-evidence and user-decision
boundaries, the API Spine sources required by the EMR4 API Steward, and the
exact R2 evidence packet.

`HEAD`, local `master`, local `handoff/current`, `origin/master`, and
`origin/handoff/current` were fetched and verified at
`2d3fa717d612add9d1f871daf9e899751c5d210c` before acceptance. The fresh
receipt is
`orchestration/agent_inbox/codex/bernie-stage1-tranche-d-rehydration-receipt.json`,
SHA-256
`c1282c50f79540fdb5a2c5f27210223c4e3dd98e1b1413b2283d479bd76d234e`.
It names all five mandatory sources:

1. `live_handover_current_baton`;
2. `current_authority_allocation`;
3. `active_plan_and_acceptance`;
4. `protected_evidence_boundaries`; and
5. `git_refs_and_worktree`.

The final verifier-acceptance preflight also passed with the same five-source
binding at
`orchestration/agent_inbox/codex/bernie-stage1-tranche-d-preacceptance-receipt.json`,
SHA-256
`ce9b93f5622c1ed73f1d591141d8af03719526c33820c9434fb58159c079d7b9`.

No protected holdout, historical-diary material, blocked external corpus,
provider, cloud, PII, production, deployment, release, or Stage 2 surface was
opened.

## Evidence judgment

The R2 product evidence remains internally consistent for S0-S6. Direct
Tranche D readback reproduced the preserved disposable database invariant:
exactly one appointment, one appointment audit, and one appointment command
idempotency row remain. Every recorded R2 artifact and screenshot SHA-256
binding reproduced exactly.

The S7 scope note is resolved without changing the frozen acceptance meaning.
Tranche D built an exact-node allowlist from the already named
`review/test_diary_smoke.py`, first verified that the file contained no
protected-path reference, and invoked all 115 named test functions explicitly.
They expanded to the full 139 route-intercepted Diary cases and all passed.
This is `route_intercepted_browser` regression evidence only. The live S3
duplicate result remains separately labelled
`live_local_browser_backend_postgres`.

No Extra High escalation was needed for S7 because the missing whole-file
coverage was supplied mechanically; no failed gate was overridden and no
acceptance meaning was revised.

The S6 screenshot is correctly hash-bound but shows the staged proposal before
the conflicting confirmation rather than the terminal typed conflict copy.
The terminal conflict and zero-write outcome therefore rely on the sanitized
R2 packet and database counts, not on that screenshot alone.

## API Spine assessment

The bounded product path preserves the accepted mixed spine:

- interpretation, context retrieval, slot search, selection, and proposal are
  non-mutating;
- `POST /api/v1/appointments/proposals/create/confirm-bernie` remains the sole
  Stage 1 mutation;
- explicit staff confirmation, signed/fresh proposal evidence, idempotency,
  backend revalidation, audit, and the typed receipt remain at the command
  boundary; and
- GraphQL has no mutation authority and neither the fake provider nor the Diary
  client writes the appointment.

The complete explicitly named API Spine, accessibility, and booking-classifier
batch passed 81/81. Python compilation, exact artifact hashes, and
`git diff --check` also passed. Bandit reported no high-severity finding; its
medium findings are confined to the disposable local harness's dialect-quoted
table inventory and fixed loopback `urlopen` calls.

## Exact unresolved G10 gate

The frozen plan requires the Sprint 98 confirmation/release gates,
signed-confirmation and idempotency tests, supervised-booking and confirmed-flow
harnesses, API Spine tests, full Diary smoke, security checks, and formatting
checks to pass. The current candidate does not satisfy that complete regression
gate.

The clean-candidate serial runs produced:

- core Sprint 98, signed-evidence, idempotency, and freshness batch: 62 passed,
  1 failed;
- supervised-booking, interpretation, receipt, wrapper, and confirmed-flow
  batch: 55 passed, 8 failed;
- API Spine, accessibility, and classifier batch: 81 passed, 0 failed; and
- full explicitly named Diary smoke: 139 passed, 0 failed.

The nine failing nodes are:

1. `tests/test_bernie_sprint98_release_gates.py::test_confirm_bernie_invalid_practitioner_returns_typed_failure_not_not_found` — the historical test omits the now-mandatory `Idempotency-Key` and receives the correct typed HTTP 400 command-boundary refusal before its intended practitioner assertion.
2. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_wrapper_confirmation_ready_evidence_confirms_exactly_one_write` — the fixed 2026-06-22 reference date is stale on 2026-07-19, so setup returns `blocked`.
3. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_wrapper_staff_review_confirm_payload_confirms_after_explicit_approval` — the same stale-date setup blocks.
4. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_wrapper_confirmation_ready_but_confirmed_false_writes_nothing` — the same stale-date setup blocks.
5. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_wrapper_confirmation_stale_conflict_revalidates_and_writes_nothing` — the same stale-date setup blocks.
6. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_non_confirmation_ready_selection_evidence_cannot_write` — the historical confirm helper omits the mandatory idempotency header.
7. `tests/test_bernie_confirmed_flow_review_harness.py::test_confirmed_bernie_flow_writes_only_at_explicit_successful_confirmation` — the fixed 2026-06-22 selection is no longer safe because it is in the past.
8. `tests/test_bernie_confirmed_flow_review_harness.py::test_unconfirmed_bernie_flow_writes_no_appointment_or_audit` — the same stale-date setup fails.
9. `tests/test_bernie_confirmed_flow_review_harness.py::test_blocked_bernie_confirmation_writes_no_appointment_or_audit` — the same stale-date setup fails.

A bounded exploratory maintenance attempt added the missing headers and pinned
the historical harness clock. It exposed additional drift in signed/legacy
audit-evidence expectations and uncommitted conflict-fixture transaction
expectations. Every exploratory test edit was reverted; the three historical
test files match their committed blobs exactly.

These failures appear to be historical harness drift rather than a reproduced
R2 product defect, but the only documented baseline exception in `AGENTS.md`
is a different runtime-isolation node. High therefore cannot disregard these
failures, narrow the frozen minimum regression gate, or claim `stage1_pass`.
Doing so would be a failed-gate override and would trigger Extra High under the
materiality rule.

## Disposition

Stage 1 remains paused at `revision_required`. No commit, push, protected-ref
movement, deployment, release, provider call, cloud mutation, or Stage 2 work
was performed.

The required non-PHI paused closeout notification was delivered successfully;
Pushover request ID: `955ce92a-c3b9-4ccb-af26-7cf397c876b0`.

The next permitted work is a fresh, bounded Stage 1-only regression-harness
maintenance tranche. It must freeze the nine clean-candidate failures, align
historical dates and mandatory idempotency headers with the current contracts,
reconcile signed/legacy audit-evidence and fixture-transaction expectations
without weakening product checks, rerun the complete explicit regression set,
and then return to a fresh Tranche D acceptance. Stage 2 remains a new Yuri
decision and is not authorized by this result.
