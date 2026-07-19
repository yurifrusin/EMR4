# Bernie Stage 1 Regression-Harness Maintenance Plan

Date: 2026-07-19

Status: `frozen_for_execution`

Reasoning level: `Sol Extra High`

Authority: the Current Baton and
`orchestration/agent_inbox/codex/bernie-stage1-tranche-d-sol-acceptance.md`
permit one fresh bounded Stage 1-only maintenance tranche before Tranche D is
reaccepted. This plan does not revise the frozen Stage 1 product claim or
authorize Stage 2.

## Five-source rehydration

The fresh tranche read `AGENTS.md`, all 35 Current Baton acceptance artifacts,
the frozen Stage 1 plan and Sol review, the strategic transition review, the
protected-evidence and user-decision boundaries, and the appointment-first API
Spine sources required by the EMR4 API Steward.

`HEAD`, local `master`, local `handoff/current`, `origin/master`, and
`origin/handoff/current` were verified at
`2d3fa717d612add9d1f871daf9e899751c5d210c`. The fresh receipt is
`orchestration/agent_inbox/codex/bernie-stage1-regression-harness-maintenance-rehydration-receipt.json`.
It names all five mandatory sources:

1. `live_handover_current_baton`;
2. `current_authority_allocation`;
3. `active_plan_and_acceptance`;
4. `protected_evidence_boundaries`; and
5. `git_refs_and_worktree`.

## Frozen clean-candidate baseline

Before maintenance, the three owned historical harness files exactly matched
their committed `HEAD` blobs:

| File | Git blob |
|---|---|
| `tests/test_bernie_sprint98_release_gates.py` | `80c7598f9177dce8959d94192b50d262aba96753` |
| `tests/test_bernie_wrapper_confirmation_review_harness.py` | `7498a24c88aad47a0255edbe3f83344806beb0b6` |
| `tests/test_bernie_confirmed_flow_review_harness.py` | `609847bf72bb6339a5181359955663be5b46d311` |

An exact serial run of the following nine nodes returned `9 failed`:

1. `tests/test_bernie_sprint98_release_gates.py::test_confirm_bernie_invalid_practitioner_returns_typed_failure_not_not_found`;
2. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_wrapper_confirmation_ready_evidence_confirms_exactly_one_write`;
3. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_wrapper_staff_review_confirm_payload_confirms_after_explicit_approval`;
4. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_wrapper_confirmation_ready_but_confirmed_false_writes_nothing`;
5. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_wrapper_confirmation_stale_conflict_revalidates_and_writes_nothing`;
6. `tests/test_bernie_wrapper_confirmation_review_harness.py::test_non_confirmation_ready_selection_evidence_cannot_write`;
7. `tests/test_bernie_confirmed_flow_review_harness.py::test_confirmed_bernie_flow_writes_only_at_explicit_successful_confirmation`;
8. `tests/test_bernie_confirmed_flow_review_harness.py::test_unconfirmed_bernie_flow_writes_no_appointment_or_audit`; and
9. `tests/test_bernie_confirmed_flow_review_harness.py::test_blocked_bernie_confirmation_writes_no_appointment_or_audit`.

The first and sixth nodes received the current typed HTTP 400
`idempotency_key_required` boundary because the historical clients omitted the
mandatory header. Nodes two through five were blocked because their fixed
2026-06-22 reference date was evaluated against the 2026-07-19 clinic date.
Nodes seven through nine likewise rejected the now-past selected slot.

## Owned maintenance

Only the three frozen test files above are owned for code edits. The bounded
maintenance may:

- pin each historical harness's clinic clock to its already fixed
  `REFERENCE_DATE`, preserving the authored Monday roster/slot and conflict
  fixture rather than moving the product clock or weakening freshness checks;
- emit an explicit, nonblank `Idempotency-Key` on every `confirm-bernie`
  request, preserving the current command boundary;
- align signed versus legacy confirmation audit-evidence assertions with the
  evidence actually supplied by each historical client; and
- commit the synthetic competing-appointment fixture before invoking the HTTP
  confirmation route so a route-level rollback cannot erase test setup that is
  meant to represent already-authoritative database state.

The maintenance must not edit application code, schemas, migrations, Diary/UI
code, provider/runtime code, API Spine contracts, policy, replay, scorer,
protected evidence, historical diary material, or Stage 2 surfaces.

## Non-weakening invariants

The maintained harness must continue to prove:

- proposal/search/select paths are non-mutating;
- the successful path requires explicit `confirmed=true`, valid signed or
  explicitly legacy evidence, and a mandatory idempotency key;
- success creates exactly one appointment and one matching appointment audit;
- invalid practitioner, unsafe evidence, `confirmed=false`, and a conflicting
  slot remain typed blocked outcomes with no appointment/audit write;
- no AI provider or autonomous execution path is used; and
- the exact Stage 1 evidence labels and REST-command authority boundary remain
  unchanged.

## Acceptance

This maintenance passes only if:

1. the exact nine-node population passes after the bounded edits;
2. all three owned harness files pass in full;
3. the complete explicit G10 regression population from the frozen Stage 1
   plan passes serially, with only the separately documented runtime-isolation
   baseline excluded if it is in the selected population;
4. the full 139-case route-intercepted Diary population still passes through
   the protected-safe exact-node allowlist;
5. API Spine, security, syntax, artifact-binding, and whitespace checks pass;
6. the preserved Stage 1 database remains exactly one appointment, one audit,
   and one completed idempotency row; and
7. fresh Tranche D acceptance, not this maintenance tranche, makes the final
   `stage1_pass` or `revision_required` decision.

Any product-code requirement, weakened safety assertion, contradictory
evidence, or material policy/authority choice stops this tranche for Yuri.
