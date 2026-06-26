# plan-codex-codex-bernie-supervised-booking-wrapper-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-supervised-booking-wrapper` |
| Branch | `codex/bernie-supervised-booking-wrapper` |
| Source Task | `codex-bernie-supervised-booking-wrapper-contract` |
| Status | integrated |
| Created | 2026-06-27 01:49 +1000 |
| Source HEAD | `6b92ee9` |

## Plan Summary

Thin backend-only supervised Bernie wrapper plan

## My Understanding

Implement, after approval only, one deterministic backend wrapper contract that accepts typed Bernie booking command input, normalizes it with the existing slot-search normalizer, executes the existing normalized slot-search proposal path only when safe, and either returns candidate slots for staff selection or, when a supervised selection is supplied, returns existing create-proposal evidence ready for the existing confirm-bernie endpoint. The wrapper must remain proposal/intake-only: no LLM/Gemini/provider calls, no direct appointment creation, no confirmation, no appointment/audit writes, and no UI/runtime work.

## Intended Surface / Boundary

Backend appointments API/schemas only, likely under /api/v1/appointments/proposals as a new Bernie supervised booking wrapper endpoint plus helper and schemas. Affected surface is API JSON contract for typed command intake/proposal composition. Visually adjacent words like cards, slots, stacking, panels, waiting room, diary grid, booking slot, and status refer only to backend slot candidate data; no diary grid, waiting-room UI, taskpane, Command Centre, or visible booking panels change.

## Out Of Scope

UI, diary/taskpane/Command Centre changes, natural-language parsing, autonomous runtime execution, Gemini/LLM/provider calls, direct appointment writes, confirmation writes, SMS, billing, resource admin, migrations unless unavoidable, appointment/audit redesign, and any change to existing normalize/search/selection/confirm semantics beyond small reusable helper extraction if strictly needed.

## Files I Expect To Edit

Expected production files after approval: app/schemas/appointments.py for typed wrapper input and discriminated output models; app/routers/appointments.py for a thin route/helper composing normalize_slot_search_command, _build_slot_search_proposal, and existing slot-selection/create-proposal helpers. Expected tests: new focused tests/test_bernie_supervised_booking_wrapper.py or similarly named backend contract tests, plus adjacent existing Bernie proposal tests. Coordination-only files during plan gate: this task packet and generated plan packet.

## Implementation Steps

1. Define wrapper request shape with SlotSearchCommandIn, explicit reference_date, optional supervised selection fields/create context matching SlotSelectionProposalIn, and a mode/discriminator that distinguishes candidate-search intake from selected-slot proposal preparation. 2. Define response models with stable intent/discriminator: blocked normalization/search result, candidate-selection-required result carrying SlotSearchCommandExecutionOut/SlotSearchProposalOut candidates, or confirmation-ready result carrying SlotSelectionProposalOut/AppointmentCreateProposalOut for confirm-bernie. 3. Add a route/helper that calls normalize_slot_search_command first, returns blocked response without schedule/conflict evaluation when normalization is unsafe, calls _build_slot_search_proposal only when safe, and calls existing slot-selection/create-proposal helper semantics only when a supervised selected candidate/index is present. 4. Preserve role/practice scoping via existing MUTATING_APPOINTMENT_ROLES dependency and existing _ensure_* guards inside reused helpers. 5. Keep implementation source free of generate_content/Gemini/provider hooks and mutation calls such as db.add, db.commit, appointment creation, audit writes, or confirm route calls. 6. Add focused tests for auth, explicit reference_date, blocked normalization no search, candidate-selection response, selected-slot confirmation-ready response, conflict/block propagation, cross-practice guard, non-mutation row counts, no-LLM/provider/source proof, and compatibility with confirm-bernie evidence shape.

## Visual / Behavioural Acceptance Checks

Backend-only JSON contract exists and composes existing deterministic behaviours without changing UI. Safe command without selection returns candidate slots for staff selection and requires no confirmation/write. Safe command with valid supervised selection returns create-proposal evidence compatible with /proposals/create/confirm-bernie but does not confirm or write. Blocked normalization/search/selection returns discriminated blocked responses with evidence. Existing normalize, normalized search, slot-selection, confirm-Bernie, and appointment proposal tests still pass. Verification after approval: py_compile touched Python; focused wrapper tests; rerun tests/test_bernie_confirmed_flow_review_harness.py, tests/test_bernie_confirm_create_proposal.py, tests/test_slot_search_normalized_execution.py, tests/test_slot_selection_proposal.py, tests/test_appointment_proposals.py; git diff --check.

## Risks / Ambiguities

Response-shape naming needs Ariadne approval so future Bernie UI/runtime can depend on the discriminator without churn. Existing slot-selection route currently accepts client-supplied search evidence; the wrapper can reduce foot-guns by composing fresh normalization/search in one request, but it should not introduce server persistence. Need care that selected candidate matching does not bypass current conflict revalidation and that no helper extraction accidentally alters Sprint 40-45 contracts. If a schema union/discriminator is awkward in current Pydantic/FastAPI patterns, prefer explicit optional branches over broad redesign.

## Codex Plan Review

- Review result: Accepted by Ariadne; backend-only non-mutating scope, response discriminator, auth/practice scoping, and verification plan were appropriate.
- Required changes before implementation: none.
- Approved to proceed: yes; implementation released with exact `complete sprint task`.
