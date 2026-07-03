# plan-codex-codex-sprint-n11-outcome-invariant-review

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-n11-outcome-invariant-review` |
| Status | integrated |
| Created | 2026-07-04 04:36 +1000 |
| Source HEAD | `a555434` |

## Plan Summary

N11 outcome invariant review plan

## My Understanding

N11 should prove route-computed schedule/search facts remain authoritative across reception policy, typed booking outcome, server-session transitions, confirm affordance, and Diary rendering. The key adversarial cases are practitioner not rostered, roster unavailable versus true searched-zero-slot no_matching_times, slot search not silently skipped into no-slot, advisory retrieval remaining advisory-only, stale session revision preservation, and confirmation staying evidence-gated.

## Intended Surface / Boundary

Backend diary/Bernie domain contract seams and focused Diary review harness only: app/services/diary schedule_explanations, policy, outcomes, confirm_gate; app/services/bernie session/session_store facades as needed; app/routers/appointments.py supervised booking route and staff review payload; app/schemas/appointments.py only if a read-only schema field is missing; docs/diary/diary.js only for render-state/confirm-affordance guard fixes; review/test_diary_smoke.py only for structural UI assertions.

## Out Of Scope

No production code during plan gate. No persisted session table, GraphRAG, auto-mode, broad UI redesign, taskpane or Command Centre work, migrations, root-to-branch API review, live-provider rewrite, or allowing retrieval/advisory knowledge to set roster truth, slot truth, policy blocks, session state, or confirm authority.

## Files I Expect To Edit

Expected implementation files after approval: tests/test_diary_schedule_explanations.py; tests/test_bernie_context_frames.py or tests/test_diary_action_boundary_contracts.py; tests/test_bernie_booking_outcomes.py; tests/test_bernie_supervised_booking_wrapper.py; tests/test_bernie_route_outcome_events.py; tests/test_diary_confirm_gate.py; review/test_diary_smoke.py; possibly app/services/diary/policy.py, app/services/diary/outcomes.py, app/services/diary/schedule_explanations.py, app/services/diary/confirm_gate.py, app/routers/appointments.py, docs/diary/diary.js. Avoid schema changes unless tests prove current envelopes cannot express the invariant.

## Implementation Steps

1. Add pure invariant tests proving schedule structural reasons outrank searched_no_candidates, and no_matching_times requires both roster/schedule available and an actual slot_search searched_no_candidates frame. 2. Add policy/outcome tests for practitioner-not-rostered and roster-unavailable cases where search_ran_no_candidates is also present, asserting roster_unavailable outcome, no_slot session target, and no confirm grant. 3. Add supervised-booking route tests for no practitioner schedule: response reception_policy.availability=roster_unavailable, outcome.kind=roster_unavailable, staff_review.confirm_affordance.gate=blocked_schedule_or_roster, confirm payload absent, session append target no_slot, and route payload reason distinguishes slot_search_skipped_no_schedule from true no_matching_slots. 4. Add a true searched-zero-slot test with roster/schedule present but no candidates, asserting outcome.kind=no_matching_times, schedule_reason_codes searched_no_candidates, suggestions allowed, and confirm blocked as no candidates. 5. Add stale expected_revision route/session test proving a stale server outcome append does not advance/rewrite the session snapshot and does not fabricate confirmation_ready or confirm payload in the client-visible response. 6. Add/adjust Diary smoke assertions for route-intercepted payloads: outcome.kind drives roster_unavailable versus no_slots; confirm button is absent/hidden unless confirm_affordance.can_show_confirm_ui or confirm_grade_allowed is true; stale session conflict keeps confirmation disabled until refresh. 7. If tests reveal drift, make smallest fixes: use the real evaluated reception policy when building staff_review.confirm_affordance instead of a synthetic policy where possible, assert outcome/state consistency at each route branch, and preserve backend outcome/state as render truth in diary.js.

## Visual / Behavioural Acceptance Checks

Adversarial checks pass: practitioner not rostered renders roster/schedule unavailable, not no matching times; roster unavailable is distinct from searched zero slots; availability search is not skipped into no-slot without explicit roster-gap evidence; advisory-only retrieval cannot affect roster/search/policy/session/confirm decisions; stale session revision is preserved and blocks confirmation; confirmation remains evidence-gated by signed evidence, session binding, fresh revision, staged proposal, and backend confirm_affordance. Visual surface affected is only the Bernie review panel inside the Diary grid; appointment cards, diary grid layout/stacking, waiting room, status controls, taskpane, and Command Centre must not change.

## Risks / Ambiguities

The main risk is that staff_review currently builds a synthetic confirm-gate policy while outcome classification uses the richer reception policy; implementation should either align the gate to the real policy or pin tests proving no contradiction. Existing legacy fallbacks in diary.js can still infer no_slots from empty candidate lists, so tests must prefer outcome/reception_policy when present. Some route tests may need precise dev fixture schedules to distinguish roster absence from fully booked or zero-slot search without brittle clock dependence.

## Codex Plan Review

- Review result: Accepted and folded into Ariadne implementation.
- Required changes before implementation: Apply the smallest backend/UI repairs needed by focused adversarial tests; do not add schema/migration/persistence work.
- Approved to proceed: yes
