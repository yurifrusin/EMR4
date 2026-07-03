# plan-claude-claude-sprint-n3-unified-evidence-gated-confirm-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-n3-unified-evidence-gated-confirm-contract` |
| Status | accepted |
| Created | 2026-07-03 20:31 +1000 |
| Source HEAD | `097ac41` |

## Plan Summary

One backend-owned deterministic gate (app/services/diary/confirm_gate.py) that fuses reception policy + staleness + staged-proposal presence into a single ConfirmAffordanceDecision, so stale/advisory-only/model-only/no-candidate/schedule-blocked state can never authorize confirm-grade booking UI. Pure contract, no routes/UI.

## My Understanding

Diary/reception domain already emits independent typed signals (evaluate_reception_context in diary/policy.py: can_prepare_proposal/must_block_confirmation/advisory_warnings_only/search_ran_no_candidates/roster_unavailable/must_ask_clarification; check_staleness in bernie_turn_evidence.py: fresh/stale/mismatched-ref-date; envelopes.py already guards confirm-grade at the envelope level). Nothing fuses these into a single backend-owned decision on whether a booking proposal may expose confirm-grade UI. Callers hand-combining these is the failure surface. N3 adds one deterministic gate over already-typed evidence.

## Intended Surface / Boundary

New pure-contract module app/services/diary/confirm_gate.py with evaluate_confirm_affordance(...) returning typed ConfirmAffordanceDecision (confirm_grade_allowed bool, gate enum, blocking_reason_codes, schedule_reason_codes). Bernie facade app/services/bernie/confirm_gate.py + __init__ re-exports, mirroring existing policy.py/evidence.py facade pattern. No DB/network/wall-clock/LLM. Backend/domain contract ONLY: no router, diary grid, taskpane, command centre, envelope schema, booking slot, status cell, or waiting room change. Nothing rendered changes.

## Out Of Scope

No implementation before plan gate. No route/endpoint wiring of the gate (future integration slice unless explicitly approved). No UI/diary-grid/booking-slot/status/waiting-room change. No envelope schema change. No GraphRAG/K1, no persisted server-side sessions, no auto-mode, no booking write-path change, no migration, no broad API review.

## Files I Expect To Edit

app/services/diary/confirm_gate.py (new); app/services/bernie/confirm_gate.py (new facade); app/services/bernie/__init__.py (add re-exports); tests/test_diary_confirm_gate.py (new).

## Implementation Steps

1) Define ConfirmAffordanceGate enum (allowed, blocked_stale, blocked_advisory_only, blocked_model_uncertain, blocked_no_candidates, blocked_schedule_or_roster, blocked_guardrail, blocked_no_proposal) and ConfirmAffordanceDecision pydantic model. 2) Implement evaluate_confirm_affordance(policy, *, staleness=None, has_staged_proposal) fail-closed: confirm-grade allowed ONLY when policy.can_prepare_proposal AND staged proposal exists AND staleness (if given) is fresh AND no block condition (must_block_confirmation, advisory_warnings_only, must_ask_clarification, search_ran_no_candidates, roster_unavailable, availability==blocked); any missing/None evidence blocks. 3) Preserve semantic distinctness (stale blocks as blocked_stale, never collapses to no_candidates) and pass schedule_reason_codes through. 4) Add Bernie facade + __init__ exports. 5) Focused tests: allowed happy path, each block reason in isolation, precedence when multiple block, None/absent staleness fail-closed, absent staged proposal blocks, reason-code passthrough.

## Visual / Behavioural Acceptance Checks

No rendered surface changes; additive typed contract. confirm_grade_allowed True only for fresh, proposal-ready, non-advisory, non-uncertain, candidate-backed, schedule-clear state; every other state False with a distinct gate. pytest tests/test_diary_confirm_gate.py -q green; python -m compileall app/services/diary app/services/bernie; git diff --check. Full suite/review smoke deferred to implementation (no UI contract touched).

## Risks / Ambiguities

1) check_staleness treats missing echoed freshness id as fresh (Sprint 104 back-compat); gate must NOT inherit that leniency for confirm-grade - has_staged_proposal/fresh evidence are explicit inputs and gate fails closed when absent. Flag whether Codex wants a stricter require-non-None-freshness-id posture. 2) Gate is inert until a future sprint wires it into confirm-bernie route/UI - that integration is deliberately out of scope. 3) Complementary to, not a replacement for, envelope-level confirm-grade guard; kept a separate module to avoid altering envelope schemas.

## Codex Plan Review

- Review result: Accepted by Ariadne with a narrow integration amendment.
  The pure diary-domain confirm gate is the correct foundation, but N3 must not
  stop with an inert contract if scoped implementation bandwidth remains.
- Required changes before implementation: implement the pure gate as planned,
  then wire it narrowly into the Bernie staff-review payload so
  `confirm_endpoint` and `confirm_payload` are present only when the backend
  gate allows confirm-grade UI. Add schema/test coverage for the emitted
  `confirm_affordance`. Keep the actual booking write path, persistence,
  GraphRAG/K1, auto-mode, and broad API redesign out of scope.
- Approved to proceed: yes, release with `complete sprint task`.
