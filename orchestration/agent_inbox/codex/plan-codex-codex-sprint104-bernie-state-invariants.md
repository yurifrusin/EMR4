# plan-codex-codex-sprint104-bernie-state-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint104-bernie-state-invariants` |
| Source Task | `codex-sprint104-bernie-state-invariants` |
| Status | integrated |
| Created | 2026-07-02 15:37 +1000 |
| Source HEAD | `e6031d7` |

## Plan Summary

Sprint 104 Bernie state invariants and acceptance harness plan

## My Understanding

Bernie Sprint 104 should turn the current Sprint 100 booking-session state into a fuller event-driven conversational workflow. The current code already has a shallow Diary-side BernieSession with immutable referenceDate, candidateSnapshot, selectedCandidateIndex, staged preview, confirmation state, and legacy global sync, plus a backend date transition table and Sprint 100 tests. Sprint 104 should add explicit memory for turns, stale context, patient recognition versus details verification, patient_booking_context freshness, candidate/proposal ownership, no-slot suggestions, and confirmation evidence. This worker should not implement backend or UI code; the useful output is a precise invariant and acceptance-harness plan that Ariadne can use to judge Claude and Antigravity plans before release.

## Intended Surface / Boundary

Plan only. Intended future implementation surface: app/services/bernie_transition_table.py and tests/test_bernie_transition_table.py for pure state-transition rules; tests/test_bernie_sprint104_state_memory.py or equivalent backend/API contract tests for session/request/context invariants; review/test_diary_smoke.py plus route-intercepted fixtures for Diary chat/clarification UI acceptance. Visually affected surface is only the Bernie panel inside docs/diary and the optional staged booking preview on the diary grid. Nearby surfaces that must not change: booking create/edit modal, appointment cards, status/waiting-room controls, diary grid layout, resource admin, taskpane, Command Centre, and broad API-spine structure.

## Out Of Scope

No production edits in this plan-gate submission. For the sprint itself: no XState/runtime dependency, no broad root-to-branch API rewrite, no live provider/browser manual testing as worker scope, no limited auto-mode, no voice/headset/Caller ID, no Medicare/HI/IHI/PVM/OPV implementation, no weakening of staff confirmation, no patient details verification requirement for ordinary booking recognition, and no dumping broad diary context into prompts.

## Files I Expect To Edit

Expected implementation files after approval: app/schemas/appointments.py for explicit memory/context response/request fields if Claude owns them; app/routers/appointments.py for supervised/interpret envelope plumbing and patient_booking_context fetch contract if accepted; app/services/bernie_transition_table.py for pure transition/state helper functions; app/services/bernie_slot_normalizer.py only if state-memory metadata must feed existing normalization; tests/test_bernie_transition_table.py; new tests/test_bernie_sprint104_state_memory.py or tests/test_bernie_sprint104_patient_context.py; docs/diary/diary.js/html/css for Antigravity chat surface and stale-state rendering; review/test_diary_smoke.py and possibly review/checks_diary.json for deterministic route-intercepted UI gates. This plan packet itself changes only orchestration/agent_inbox coordination files.

## Implementation Steps

1. Define a small Sprint 104 statechart table before implementation: INACTIVE -> CONTEXT_SELECTION -> INSTRUCTION_ENTRY -> INTERPRETING -> CLARIFICATION_NEEDED or CONTEXT_ENRICHMENT -> SEARCHING_SLOTS -> NO_SLOTS or CANDIDATE_SELECTION -> SLOT_PREVIEW -> CONFIRMING -> CONFIRMED, with STALE_CONTEXT and CANCELLED/RESET transitions from every active state. Treat diary Today/Prev/Next/date picker/Refresh, patient selection, candidate selection, proposal preview, cancel, choose-another-time, and confirm as named events.
2. Add pure invariants in the transition helper: request_reference_date is immutable per session; visible_diary_date may change but never redefines the active request; a new staff prompt/clarification turn appends to turn history and invalidates downstream interpretation/snapshot/proposal unless it is explicitly a clarification against current state; candidate snapshots and proposals carry owner ids such as session_id, turn_id, context_snapshot_id, patient_booking_context_id, and candidate_snapshot_id.
3. Separate patient recognition from details verification: unique high-confidence practice patient recognition can let ordinary booking continue; ambiguous/low-confidence candidates require a staff choice/clarification; Medicare/HI/IHI/PVM/OPV details verification stays out of Sprint 104 and must not block ordinary recognised-patient booking.
4. Define patient_booking_context as a compact deterministic context frame fetched only after patient recognition. Required freshness metadata: patient_id, generated_at, lookback/lookahead, recent/future bookings, derived signals, and stale reason. It must not be a broad diary dump and must not be fetched for ambiguous candidates.
5. Define no-slot states as first-class outputs. NO_SLOTS/CLINIC_DAY_EXHAUSTED must render direct copy plus typed clickable alternatives, e.g. next available that day, same window another practitioner, next business day/Monday afternoon. Suggestions become new events/turns, not string hacks.
6. Require stale-state clearing rules: Today/Prev/Next/date picker and Refresh keep the Bernie panel open but invalidate response/candidate/proposal unless the current event is previewing an owned absolute candidate; selected appointment/context changes reset recognition/context; confirmation must fail safely if confirm payload is stale or does not match selected candidate/proposal evidence.
7. Extend backend tests first with deterministic fake-provider or route-level checks: immutable reference date across clarification; visible diary navigation after candidate preview does not re-resolve relative date; patient_booking_context fetched after recognised patient and not for ambiguous patient; stale candidate/proposal confirm blocked; no-slot response includes suggestions; interpret/supervised paths still write no Appointment/Audit rows before confirm.
8. Extend UI/review harness with route-intercepted smoke checks: text input behaves as chat/new-turn input after Bernie responds; clarification answer uses prior session memory; Choose another time reuses candidate snapshot with zero interpret/search calls; Refresh/navigation clears stale preview and disables confirm; no-slot suggestions are clickable and issue typed next-transition payloads; confirmed state shows compact success and removes confirm controls.
9. Keep release gates honest: label fake/route-intercepted checks as such; keep Margaret Thompson / Dr Shera ordinary prompt as a blocking gate for any implementation touching booking interpretation/candidate/confirmation surfaces; require live-provider evidence only when Ariadne chooses to run live checks after implementation.
10. Resubmission criteria: reject worker plans that let diary navigation become semantic input, reuse a stale single prompt as the active request, treat recognition as national-identifier verification, send broad diary context to the LLM, allow confirm from stale/mismatched candidate evidence, hide no-slot alternatives behind generic failure copy, or introduce limited auto-mode in Sprint 104.

## Visual / Behavioural Acceptance Checks

Transition sketch: INSTRUCTION_SUBMITTED locks session_id/request_reference_date/turn_id; INTERPRETED stores command_snapshot; CLARIFICATION_REQUIRED stores question and awaits STAFF_CLARIFICATION_PROVIDED; PATIENT_RECOGNISED triggers PATIENT_BOOKING_CONTEXT_FETCHED; SLOTS_FOUND stores candidate_snapshot_id; CANDIDATE_SELECTED stages absolute selected_candidate and proposal_id; CHOOSE_ANOTHER_TIME returns to same candidate_snapshot_id without reinterpret/search; DIARY_NAVIGATED/REFRESH_REQUESTED marks stale_context and clears preview/confirm; STAFF_CONFIRMED writes only if session_id, turn_id, candidate_snapshot_id, selected_candidate, proposal_id, and confirmation evidence still match.
Concrete invariants: no stale prompt reuse; no relative date re-resolution after first interpretation; no candidate selected outside its snapshot; no confirm without explicit staff event; no confirm if proposal_fresh=false; patient_booking_context generated only for recognised patient_id and includes freshness metadata; no-slot states are not empty candidate_selection states; ordinary copy excludes raw snake_case/UUIDs outside Details.
Fixture scenarios: Margaret Thompson / Dr Shera today after 2 before 3:45; after 3 today at 20:40 returns no-slot/another-day suggestions; after 3 tomorrow then preview navigates diary without making tomorrow move again; Choose another time does not call interpret/search; Refresh after preview clears staged card and confirm button; ambiguous Margaret/Maggie asks recognition clarification before patient_booking_context; recognised Margaret with existing future follow-up surfaces compact existing booking context; no slots in requested window offers clickable next alternatives; stale confirm after roster/diary refresh is blocked with typed stale copy.
Required test names to ask workers for: test_sprint104_reference_date_survives_clarification_turn, test_sprint104_diary_navigation_marks_proposal_stale_not_semantic, test_sprint104_choose_another_time_reuses_candidate_snapshot_without_network_calls, test_sprint104_patient_booking_context_requires_recognised_patient, test_sprint104_patient_recognition_not_details_verification, test_sprint104_no_slot_state_returns_clickable_suggestions, test_sprint104_stale_confirm_payload_is_blocked, test_sprint104_confirm_success_records_evidence_and_clears_controls, test_sprint104_chat_turn_input_clears_old_prompt_state, test_sprint104_no_broad_diary_context_in_interpret_payload.
Acceptance gates: focused pytest for transition/helper/API invariants; route-intercepted review/test_diary_smoke.py cases for UI transitions; node --check docs/diary/diary.js and asset version checks if assets change; no appointment/audit write before confirm; route-intercepted versus live labels preserved.

## Risks / Ambiguities

Risk: Sprint 100 already introduced frontend state while legacy globals remain; Sprint 104 should plan either a narrow compatibility bridge or a cleanup boundary so two sources of truth do not drift. Risk: patient_booking_context could become a privacy/cost problem if implemented as broad context; the invariant must constrain it to compact deterministic frames. Risk: no-slot alternatives can accidentally become prompt strings rather than typed transitions; require payload assertions. Risk: confirmation freshness may need backend-owned identifiers or hashes; otherwise UI-only freshness is too easy to bypass. Dissent: do not add XState yet; the project should harvest two or three concrete state-machine sprints before choosing a runtime or doing the broad API-spine review.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
