# claude-sprint-n3-unified-evidence-gated-confirm-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 3c751c8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n3-unified-evidence-gated-confirm-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n3-unified-evidence-gated-confirm-contract --commit-message "Sprint N3 unified evidence gated confirm contract" --message "claude-sprint-n3-unified-evidence-gated-confirm-contract ready for Codex review"` |

## Mission

Plan Sprint N3 backend/domain work for a unified evidence-gated confirm/review affordance contract. Define the diary-domain conditions under which a booking proposal may expose confirm-grade UI, preserving that stale, advisory-only, model-only, no-slot, or schedule-blocked state cannot show confirm/review affordances.

## Scope

### In Scope

Plan only first. app/services/diary and app/services/bernie domain contracts, reception policy evidence fields, tests for confirm-grade vs advisory-only state, and compatibility facades as needed. Keep route/UI changes scoped as future integration unless explicitly approved after plan review.

### Out of Scope

No implementation before plan gate, no GraphRAG/K1, no persisted server-side sessions, no auto-mode, no booking write-path changes, no broad API review, no migration, no UI redesign.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Plan packet first. Later implementation should run focused diary/bernie domain tests, compileall for app/services/diary app/services/bernie, review smoke checks if any UI contract is touched, and git diff --check.

## Merge Criteria

A precise implementation plan that defines one backend-owned evidence gate for confirm-grade booking UI and prevents stale/advisory/model-only state from authorizing confirmation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW app/services/diary/confirm_gate.py — ConfirmAffordanceGate enum, ConfirmAffordanceDecision Pydantic model, evaluate_confirm_affordance(policy, *, staleness=None, has_staged_proposal) fail-closed gate. Pure contract: no DB, no network, no LLM.
  - NEW app/services/bernie/confirm_gate.py — Bernie facade re-exporting from diary confirm_gate; matches existing evidence.py/policy.py facade pattern.
  - EDIT app/services/diary/__init__.py — added ConfirmAffordanceDecision, ConfirmAffordanceGate, evaluate_confirm_affordance to imports and __all__.
  - EDIT app/services/bernie/__init__.py — added re-exports and __all__ entries for the three gate symbols.
  - EDIT app/schemas/appointments.py — imported ConfirmAffordanceDecision from diary; added confirm_affordance: Optional[ConfirmAffordanceDecision] = None field to BernieStaffReviewPayload.
  - EDIT app/routers/appointments.py — imported BernieReceptionPolicyDecision, ConfirmAffordanceDecision, ConfirmAffordanceGate, evaluate_confirm_affordance from app.services.bernie. In _bernie_staff_review_payload: builds synthetic BernieReceptionPolicyDecision from result/blocks/warnings/selection_proposal, calls evaluate_confirm_affordance, gates confirm_endpoint/confirm_payload on gate_decision.confirm_grade_allowed (replacing confirmation_ready for that guard), emits confirm_affordance=gate_decision on every BernieStaffReviewPayload response.
  - NEW tests/test_diary_confirm_gate.py — 22 tests: allowed happy path, allowed with staleness=None, each of 6 block reasons in isolation, precedence (guardrail > stale > advisory > model_uncertain > roster > no_candidates > no_proposal), reason-code passthrough on block and allowed, Bernie facade parity, bernie package and diary package export checks.
- Verification run:
  - python -m compileall app/services/diary app/services/bernie app/schemas app/routers: OK (no output = clean)
  - pytest tests/test_diary_confirm_gate.py -v: 22 passed in 4.73s (Python 3.14.6, pytest 8.4.2)
  - Regression suite — test_bernie_domain_package, test_diary_schedule_explanations, test_diary_action_envelopes, test_bernie_supervised_booking_wrapper: 66 passed in 16.22s, no failures
  - git diff --check: clean
- Remaining risks:
  - advisory_warnings_only is set to False in the synthetic policy built inside _bernie_staff_review_payload. This means advisory warnings alongside a valid staged proposal do not block confirm-grade UI, preserving current behavior. If a future sprint decides advisory warnings should block confirm affordance even with a proposal, the gate flag in the synthetic policy must be revisited.
  - staleness=None is passed from _bernie_staff_review_payload since the function does not receive a StalenessResult. Staleness validation continues to be enforced separately at the confirm-bernie route (check_staleness called there). The gate does not double-check staleness at the staff-review surface.
  - The synthetic policy's schedule_reason_codes is always [] (no parsing at this level); blocking_reason_codes includes block and warning codes. This is informational only; the gate's blocking decision does not depend on schedule_reason_codes.
  - Gate is confirmed inert for blocked/candidate_selection_required/clinic_day_exhausted results: gate always returns blocked_* for those, matching existing behavior where confirm_endpoint is None.
