# plan-codex-codex-sprint105-bernie-turn-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint105-bernie-turn-invariants` |
| Source Task | `codex-sprint105-bernie-turn-invariants` |
| Status | pending_plan_review |
| Created | 2026-07-02 23:32 +1000 |
| Source HEAD | `0e9438b` |

## Plan Summary

Sprint 105 invariant harness for Bernie typed turns, freshness evidence, and stale-confirm gates

## My Understanding

Sprint 105 needs an independent acceptance model, not another backend or UI implementation. I will define executable invariants proving Bernie chat/session behaviour is represented as typed backend-visible turns/events: turn ids are unique and ordered, event kinds move through allowed transitions, request_reference_date is immutable for the session/turn chain, no-slot suggestion clicks are typed events rather than reinterpreted free text, candidate/proposal evidence is fresh and inspectable, confirmation evidence matches the current proposal, stale navigation/refresh blocks confirmation, and no appointment mutation happens before an authorized current confirmation. This plan also gives Ariadne concrete merge/rejection gates for Claude backend/API and Antigravity Diary UI submissions.

## Intended Surface / Boundary

Primary eventual surface is test/review harness only: a new backend contract test file such as tests/test_bernie_sprint105_turn_contract.py, with narrow additions to tests/test_bernie_sprint104_state_memory.py only if existing fixtures are the better anchor, plus review/test_diary_smoke.py for deterministic Diary/Bernie UI checks. The affected UI surface is only the Bernie chat/proposal panel and its typed suggestion/confirm controls inside the Diary app; the diary grid, booking slot rendering, appointment cards, stacking/overlap layout, waiting room tabs, and status controls must not visually or behaviourally change except as test targets. No production app/, docs/diary runtime, migrations, or runtime docs are changed during this plan gate.

## Out Of Scope

No production code before plan approval. I will not duplicate Claude's backend implementation or Antigravity's UI implementation, introduce a statechart runtime dependency, launch the broad API-spine review, build auto-mode/voice/headset/Caller ID/Medicare verification, weaken staff confirmation, or add any agent-only write path. I will not change appointment mutation semantics except to specify tests that prove mutations remain blocked until current typed confirmation succeeds.

## Files I Expect To Edit

Expected after implementation approval: tests/test_bernie_sprint105_turn_contract.py as the preferred new invariant suite; possibly tests/test_bernie_sprint104_state_memory.py for shared Sprint 104 fixtures/regressions; review/test_diary_smoke.py for stable route-intercepted UI contract checks; optional orchestration/sprint_closeout.md or orchestration notes only if Ariadne asks for closeout documentation. Plan gate changes are limited to orchestration plan/review packet files created by the helper and the source task packet completion notes.

## Implementation Steps

1. Inspect existing Sprint 104 backend tests, Bernie appointment schemas/router/service paths, and review/test_diary_smoke.py to reuse fixtures without widening production scope.
2. Define a transition/event table for allowed typed events: staff_instruction -> bernie_interpreted; staff_instruction -> clarification_requested -> staff_clarification -> bernie_interpreted; bernie_interpreted -> no_slot_suggestions_returned -> no_slot_suggestion_selected -> candidates_returned; candidates_returned -> candidate_selected -> proposal_previewed -> confirm_attempted -> confirm_accepted or confirm_rejected_stale. Navigation/refresh/context_change events may invalidate candidates/proposals but must not silently mutate appointments.
3. Define invariant assertions: turn_id uniqueness and monotonic order within session; event_id uniqueness; parent_turn_id or previous_turn_id linkage where present; immutable request_reference_date across clarifications, no-slot selections, refreshes, and relative-date wording; event_kind enum rejects unknown strings; candidate_snapshot_id/hash changes when search inputs or slot list evidence changes; proposal_snapshot_id/hash is derived from selected candidate absolute date/time/practitioner/patient/duration/reason; confirm requires matching current session_id, turn_id, proposal id/hash, and authorization evidence; stale/mismatched evidence returns a typed rejection and performs no appointment write.
4. Add backend fixture design names for implementation: sprint105_turn_chain_reference_date_fixture, sprint105_no_slot_typed_suggestion_fixture, sprint105_candidate_snapshot_v1_v2_fixture, sprint105_stale_confirm_after_navigation_fixture, sprint105_stale_confirm_after_refresh_fixture, and sprint105_proposal_hash_mismatch_fixture.
5. Plan backend tests: test_turn_ids_are_unique_ordered_and_linked; test_reference_date_is_immutable_across_clarification_turns; test_no_slot_suggestion_selection_is_typed_and_not_reinterpreted_as_free_text; test_candidate_snapshot_hash_changes_when_slot_evidence_changes; test_confirm_requires_current_proposal_evidence; test_stale_confirm_after_navigation_is_rejected_without_mutation; test_stale_confirm_after_refresh_is_rejected_without_mutation; test_no_appointment_created_before_authorized_confirmation.
6. Plan UI smoke checks with route interception and compact structured output: clicking a no-slot suggestion emits a typed suggestion payload; selecting a candidate stores/display current candidate/proposal evidence; navigating date, Prev/Next/Today, date picker, or Refresh disables/clears stale confirm; confirm uses the current proposal evidence rather than recomputing from visible copy; ordinary mode does not leak raw snake_case/debug hashes unless Details is intentionally opened.
7. Encode Sprint 104 live-failure regressions as expected failure modes: old proposal can remain visible after diary navigation; refresh can leave confirm enabled for a previous candidate; relative 'tomorrow' can drift if reference date is recomputed; no-slot suggestion text can be resubmitted as ambiguous free text; candidate list and proposal preview can lose proof of which slot snapshot they came from.
8. Give Ariadne acceptance gates: Claude must provide typed schemas/enums/evidence fields and failing-then-passing backend tests for stale confirmation and no-write invariants; Antigravity must emit typed UI events, clear/disable stale proposal state on navigation/refresh, preserve calm Bernie panel copy, and add deterministic review harness coverage. Reject or request resubmission if either branch relies on visible text parsing, current clock reinterpretation, route-intercept-only 'live' claims, silent fallback mutation, or broad unrelated layout/API refactors.

## Visual / Behavioural Acceptance Checks

Backend acceptance: focused pytest for the Sprint 105 turn contract passes; stale confirmation fixtures prove no appointment row/proposal mutation is created on mismatch; request_reference_date remains the original absolute clinic date for the whole turn chain; candidate/proposal freshness evidence is present in API responses and required on confirm; no-slot suggestions are first-class typed events; unknown event kinds and stale proposal ids/hashes are rejected with typed errors.
UI/review acceptance: review/test_diary_smoke.py proves the Bernie panel emits typed no-slot suggestion, candidate selection, proposal preview, and confirm payloads; Confirm is unavailable or returns a stale-state recovery message after Today/Prev/Next/date picker/Refresh changes the diary context; compact ordinary mode remains receptionist-friendly, with technical evidence only in Details; no regressions to diary grid, appointment cards, slot stacking, waiting room, or status controls.
Acceptance gates for worker submissions: Claude is accepted only if its schemas/tests make stale confirm rejection impossible to bypass and preserve no-write-before-confirm. Antigravity is accepted only if its UI sends typed events end to end, does not reconstruct confirmation from DOM/copy, and includes deterministic smoke coverage. Both are rejected for production changes outside their packets, missing fixture coverage for Sprint 104 failures, mutable relative dates, hidden agent-only write paths, or lack of evidence fields Ariadne can inspect.

## Risks / Ambiguities

The exact evidence shape may differ between Claude and Antigravity plans, so Ariadne may need to normalize names such as candidate_snapshot_id versus candidate_evidence_hash before implementation release. UI route-intercept tests can prove payload shape and stale-control behaviour but not true live-provider semantics; any live-provider claim must still include configured-provider evidence. Too much state machinery would slow this sprint, so the harness should use simple transition tables and typed enums rather than adding a runtime statechart dependency.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
