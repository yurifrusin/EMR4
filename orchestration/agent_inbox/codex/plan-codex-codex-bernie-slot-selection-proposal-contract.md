# plan-codex-codex-bernie-slot-selection-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-slot-selection-proposal` |
| Source Task | `codex-bernie-slot-selection-proposal-contract` |
| Status | pending_plan_review |
| Created | 2026-06-26 23:40 +1000 |
| Source HEAD | `ec1e5ae` |

## Plan Summary

Plan backend-only Bernie slot-selection proposal contract

## My Understanding

Role: codex-worker. Worker Name: Cicero. Worker Branch: codex/bernie-slot-selection-proposal. After explicit approval only, add a supervised backend contract that lets a staff-facing Bernie flow choose one candidate from normalized slot-search results and turn it into create-proposal-compatible evidence. The route must remain non-mutating: no appointment creation, no confirmation, no audit rows, and no Gemini/LLM calls.

## Intended Surface / Boundary

Backend appointments proposal API only, likely under app/routers/appointments.py and app/schemas/appointments.py. Behavioural surface is a typed API response/payload, not a diary card, diary grid, slot visual, panel, waiting room, taskpane, or Command Centre surface. Nearby slot-search normalized and appointment create-proposal endpoints must remain compatible and unchanged except for shared helper reuse if needed.

## Out Of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing or calls, autonomous execution, actual appointment create/edit/status/cancel/delete confirmation, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless unexpectedly required, DB-backed natural-language name resolution, and broad scheduling redesign.

## Files I Expect To Edit

Expected after approval: app/schemas/appointments.py for SlotSelectionProposal input/output schemas; app/routers/appointments.py for a narrow /proposals/slot-search/select-style route/helper reusing existing create proposal validation; tests/test_slot_selection_proposal.py for focused contract tests. Possibly touch tests/test_slot_search_normalized_execution.py or tests/test_appointment_proposals.py only if shared compatibility needs explicit regression coverage. No docs/runtime/UI files during implementation unless Ariadne expands scope.

## Implementation Steps

1. Inspect existing SlotSearchCommandExecutionOut, SlotSearchProposalOut, SlotCandidate, AppointmentCreateProposalIn, and create-proposal helper flow. 2. Define a request shape that accepts either normalized search execution evidence plus selected candidate index/identity or explicit candidate selection plus required create fields. 3. Validate selected candidate consistency for date, time, duration, practitioner, location, patient/provisional patient, and appointment type constraints. 4. Build create-proposal-compatible command/evidence and call/reuse non-mutating create-proposal validation only, returning safe/proposal/blocked warnings and blocks for staff review. 5. Add tests proving happy path, mismatched candidate blocks, conflict/break/provisional warnings as applicable, auth/practice scoping, no appointment/audit writes, and no LLM calls. 6. Run focused compile/test/diff verification and submit through protocol.

## Visual / Behavioural Acceptance Checks

Plan-gate acceptance: this packet states codex-worker/Cicero/codex/bernie-slot-selection-proposal and backend-only supervised non-mutating scope. Post-approval behavioural acceptance: selecting a valid candidate returns create-proposal-compatible evidence for staff review; mismatched or unsafe selections return blocks/warnings; existing normalized slot-search and create-proposal routes still pass; database Appointment and audit rows are unchanged; no LLM/Gemini code path is imported or called; no visual diary/taskpane behaviour changes.

## Risks / Ambiguities

Need to avoid duplicating create-proposal validation logic or silently bypassing conflict/break/provisional warning semantics. Need a crisp identity check for selected candidates because normalized slot-search candidates may be reconstructed client-side. Naming of the route/schema should not imply execution or booking. If existing create-proposal validation is not factored for reuse, keep the smallest safe helper refactor and cover compatibility with adjacent tests.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
