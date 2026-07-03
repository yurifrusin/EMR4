# plan-codex-codex-sprint-n12-explanation-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-n12-explanation-invariants` |
| Status | integrated |
| Created | 2026-07-04 04:58 +1000 |
| Source HEAD | `4d95981` |

## Plan Summary

Plan adversarial tests for explanation payload authority boundaries

## My Understanding

Sprint N12 should plan tests for richer roster/schedule explanation payloads before implementation. The core invariant is that explanation payloads can inform staff copy and suggest next actions, but they are not authoritative for confirmation, slot truth, roster truth, route/search evidence, or session freshness. Confirmation remains gated by selected-slot/create-proposal evidence and current session revision; no-slot and roster-unavailable states remain driven by typed policy/search frames rather than friendly explanatory text.

## Intended Surface / Boundary

Plan-only coordination artifact for backend and review-harness invariant targets: tests/test_bernie_booking_outcomes.py, tests/test_bernie_supervised_booking_wrapper.py, tests/test_diary_schedule_explanations.py, tests/test_bernie_context_frames.py, and review/test_diary_smoke.py. Behavioural surface is the Bernie supervised booking outcome/review payload and Diary Bernie review panel copy. Nearby surfaces that must not change during planning: diary grid appointment cards/slots stacking, waiting room/status controls, booking modal, patient/taskpane UI, migrations, runtime docs, and production app code.

## Out Of Scope

No production code before approval; no app/, docs/diary runtime JS/CSS/HTML, migrations, persisted sessions, GraphRAG/K1b route wiring, auto-mode, broad API rewrite, live PHI, master/handoff movement, or frontend visual redesign in the plan gate.

## Files I Expect To Edit

Plan gate: coordination files only, especially the task packet and generated plan/review packet. After approval only: add focused tests in tests/test_diary_schedule_explanations.py, tests/test_bernie_context_frames.py, tests/test_bernie_booking_outcomes.py, tests/test_bernie_supervised_booking_wrapper.py, and review/test_diary_smoke.py if UI smoke coverage is needed; production code only if tests expose a tiny gap and Ariadne approves implementation.

## Implementation Steps

1. Add schedule-explanation domain tests proving structural explanation reasons cannot synthesize searched no-slot truth without a slot_search frame, and cannot invent roster presence/absence beyond typed evidence. 2. Add context-frame/outcome tests for precedence: stale/hard-block dominates explanation, roster-unavailable remains distinct from searched-zero-candidate, advisory explanations stay advisory-only, and friendly copy cannot flip can_confirm or requires_confirmation. 3. Add supervised-wrapper tests with adversarial payloads: explanation claims available slots while search returned zero; explanation suggests confirm while selected_slot/confirm_payload evidence is missing; explanation says no roster while route/search evidence has candidates; stale revision plus selected-slot-looking explanation suppresses confirm. 4. Add Diary smoke invariant only if the rendered review payload consumes these fields: visible copy may come from typed explanation payloads, but confirm button and selected-slot panel render only from confirmation-ready evidence; stale navigation/session revision clears or blocks stale explanation state. 5. Keep test names explicit and negative: no_invented_no_slot, no_invented_roster, advisory_only_boundary, selected_slot_evidence_gating, stale_session_revision, and typed_copy_source. 6. Run focused pytest subsets and the review harness subset when implementation is later approved, plus py_compile/node checks if production Python/JS changes become necessary and git diff --check.

## Visual / Behavioural Acceptance Checks

Plan acceptance: Ariadne can see a concrete negative-test map for no invented no-slot, no invented roster, advisory-only boundary, selected-slot evidence gating, stale session revision, and friendly copy sourced from typed payloads. Later implementation acceptance: backend tests fail if explanation text/payload grants confirmation, overrides route/search truth, rewrites roster truth, or hides stale state; Diary smoke fails if explanatory copy creates selected-slot/confirm affordances or leaves stale explanation visible after date/session changes. No visual change is expected except any deliberately asserted Bernie review-panel copy sourced from typed payloads.

## Risks / Ambiguities

Risk: the exact rich explanation schema may not exist yet, so tests may need to target current typed reason/evidence frames first and leave TODO-shaped assertions only if Ariadne wants schema-first implementation. Risk: review/test_diary_smoke.py is large and slow; prefer narrow parameterized smoke cases or backend-only invariants unless UI rendering consumes new fields. Risk: advisory-only wording is subtle: advisory with valid selected-slot evidence may coexist with confirm readiness, but advisory payload alone must never create confirm readiness. Ambiguity: whether stale-state confusion is represented by N5/N6 session revision, signed confirm evidence freshness, or both; plan should cover both if the existing helpers make that cheap.

## Codex Plan Review

- Review result: Accepted and implemented by Ariadne.
- Required changes before implementation: Add display-only schedule explanation
  payload tests and Diary confirm-gating negative tests.
- Approved to proceed: yes.
