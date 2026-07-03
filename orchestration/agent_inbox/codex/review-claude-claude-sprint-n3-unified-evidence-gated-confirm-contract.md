# review-claude-claude-sprint-n3-unified-evidence-gated-confirm-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-n3-unified-evidence-gated-confirm-contract` |
| Status | integrated |

## Review Request

claude-sprint-n3-unified-evidence-gated-confirm-contract ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-n3-unified-evidence-gated-confirm-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated with bounded Ariadne hotfixes. Added the
  `can_show_confirm_ui` serialized alias to the backend decision, updated the
  Diary UI to consume backend-owned confirm affordance state, and added focused
  smoke/regression coverage.
- Follow-up required: Later signed-evidence/session work should make the
  staff-review gate consume explicit staleness evidence rather than relying on
  final confirm-route revalidation plus UI stale-preview clearing.
