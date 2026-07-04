# plan-claude-claude-sprint-d5-route-builder-search-horizon-threading

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-d5-route-builder-search-horizon-threading` |
| Status | pending_plan_review |
| Created | 2026-07-04 16:08 +1000 |
| Source HEAD | `a12e4e3` |

## Plan Summary

Thread the D4 metadata-only search_horizon into BernieSlotSearchFrame inside _build_bernie_reception_context by deriving same_day vs advance from the normalized target date vs the request reference_date. Additive, backend-only, no outcome-semantics change.

## My Understanding

Sprint D4 added an optional metadata-only field search_horizon: Literal['same_day','advance']|None to BernieSlotSearchFrame (app/services/diary/frames.py:104). It is deliberately unused by policy/outcome logic: a real slot search that ran and found zero candidates classifies as searched_no_candidates -> no_matching_times regardless of horizon (Ariadne amendment; enforced by tests/test_bernie_d4_diary_domain_frames_policy.py). D4 stopped short of populating the field from the route because 'the route needs to know the horizon'. In fact the route builder _build_bernie_reception_context (app/routers/appointments.py:2759) already receives normalization (a SlotSearchCommandResult whose constraint.date_from is the target search date) and reference_date (the immutable request reference date). Horizon is therefore derivable purely from data already in hand: same_day when the target date == reference_date; advance when target date > reference_date; None (unknown) otherwise. Only the SlotSearchFrame instances produced when a search actually ran should carry the tag.

## Intended Surface / Boundary

Backend domain/route only. Surface: app/routers/appointments.py _build_bernie_reception_context and a small new pure helper _derive_search_horizon. New focused test module under tests/. The words 'slot', 'candidates', and 'search' here refer only to typed BernieSlotSearchFrame metadata assembled server-side; NO visible diary grid, booking-slot card, waiting-room, or status UI is touched. diary.js/diary.html/diary.css, taskpane, and Command Centre must not change. Policy (app/services/diary/policy.py) and outcome classification (app/services/diary/outcomes.py, schedule_explanations.py) must not change.

## Out Of Scope

No frontend/UI/taskpane/diary.js/CSS. No GraphRAG or practice-knowledge retrieval changes. No persisted session tables or migrations. No new schema fields (search_horizon already exists from D4). No change to policy predicates or outcome/schedule-explanation classification. Do NOT downgrade a genuine future/advance searched_no_candidates to advisory - it stays no_matching_times. No user-facing copy changes. No broad appointment API review.

## Files I Expect To Edit

app/routers/appointments.py (add _derive_search_horizon helper; set search_horizon on the searched_with_candidates and searched_no_candidates frames, and optionally the blocked-with-result frame, inside _build_bernie_reception_context). tests/test_bernie_d5_route_builder_search_horizon.py (new focused tests). No edit expected to app/services/diary/frames.py (field already present) or any policy/outcome module.

## Implementation Steps

1. Add a pure helper _derive_search_horizon(reference_date, normalization) -> Literal['same_day','advance']|None near _build_bernie_reception_context. Rule: if normalization and normalization.constraint and normalization.constraint.date_from is not None: return 'same_day' if date_from == reference_date, 'advance' if date_from > reference_date, else None (past/ambiguous). Otherwise None. Range searches are labelled by date_from (start). 2. In _build_bernie_reception_context, when search_ran, compute horizon once and pass search_horizon=horizon to the BernieSlotSearchFrame constructions for searched_with_candidates (line ~2893) and searched_no_candidates (line ~2906); also set it on the blocked-with-result frame (~2880) which had a real target date. Leave the not_run/no-schedule frame (~2865) and the missing-result blocked frame (~2873) at None because no search executed against a resolved date. 3. Do not read search_horizon anywhere in policy/outcome - it stays metadata-only. 4. Add tests calling _build_bernie_reception_context directly (no DB/route/client) with a crafted SlotSearchCommandResult+SlotSearchProposalOut proving same_day/advance/None tags and that outcome classification via evaluate_reception_context+classify_booking_outcome is unchanged. 5. Run verification (py_compile, focused pytest, git diff --check).

## Visual / Behavioural Acceptance Checks

Route-built frame from a same-day normalization (constraint.date_from == reference_date) carries search_horizon='same_day' on the slot_search frame. Advance date (date_from > reference_date) -> 'advance'. Missing/None constraint or past date -> None. A route-built searched_no_candidates frame still classifies as no_matching_times / no_availability regardless of horizon (policy predicate search_ran_no_candidates unchanged). Existing D4 frame/policy tests, diary schedule-explanation tests, and Bernie booking-outcome tests all pass unchanged. py_compile clean on touched files; git diff --check clean. No diary asset/version bump (no UI change).

## Risks / Ambiguities

1. Date-range searches (date_from..date_to spanning forward) are labelled by their start date; a range starting today reads as same_day. This is metadata-only and does not affect outcomes; documented in the helper. 2. Past date_from is mapped to None rather than a fabricated label to avoid mislabeling; such requests should not occur for forward booking searches. 3. The interpret route passes normalization but does not run a search (search_ran=False), so it emits no slot_search frame and no horizon - intentional. 4. Must guard against reading search_horizon in any policy path; verified none does today. 5. If Codex prefers horizon NOT set on the blocked-with-result frame, that is a trivial narrowing - flag for reviewer preference.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
