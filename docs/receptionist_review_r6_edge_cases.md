# codex-sprint-r6-temporal-edge-scout — Plan Packet

| Item | Value |
|---|---|
| Role | codex-worker |
| Worker Name | Shen (DeepSeek Flash) |
| Worker Branch | codex/sprint-r6-temporal-edge-scout |
| Status | plan-pending-review |

## My Understanding

Scout the temporal edge-case surface for Sprint R6 without overlapping Claude's main implementation lane. Audit the three layers — pure temporal policy (pp/services/diary/temporal.py), slot normalizer past-date guard (pp/services/bernie_slot_normalizer.py), and route-level same-day window handling (pp/routers/appointments.py, two paths: propose_bernie_interpret_booking_instruction and propose_bernie_supervised_booking) — then produce a priority-ordered edge-case matrix with expected outcomes and recommendations for Ariadne/Claude.

## Intended Surface / Boundary

- **Temporal policy pure functions**: evaluate_same_day_window(), parse_time_fragment(), extract_natural_time_constraints()
- **Slot normalizer past-date check**: _parse_date() + 
ormalize_slot_search_command() — absolute-past-date blocking
- **Interpret path (≈ line 3670–3830)**: Same-day temporal band assignment in propose_bernie_interpret_booking_instruction
- **Supervised path (≈ line 5569–5820)**: Same-day propose_bernie_supervised_booking window checks

**Must not change**: Diary UI, taskpane/Word assets, raw appointment mutation, DB migrations, Bernie session-store internals, LLM prompts, practice knowledge substrate, no-slot suggestion flow, diary grid rendering, waiting-area status paths.

## Files I Will Create (plan artifact only, no production code)

| File | Purpose |
|---|---|
| docs/receptionist_review_r6_edge_cases.md | Edge-case matrix with priority, boundary description, expected outcome, and implementation recommendation |

## Edge-Case Matrix (Scout Results)

### Category A: Should Fix Now (route-level bug)

| # | Edge Case | Layer | Description | Expected Behaviour | Risk |
|---|---|---|---|---|---|
| A1 | window_fully_past with only latest_time set | Interpret path (line 3718) | User says "Book today before 10 AM" at 10:30 AM. evaluate_same_day_window() returns window_fully_past, but guard at L3718 requires _earliest is not None AND _latest is not None. Since no earliest was given, the "ask" band is never set, and the request proceeds as if the window is still open. | Should upgrade to "ask" band: "That time has already passed today." | Medium — user confusion, but supervised path (which the UI uses) is not affected. Interpret path currently powers the LLM-band backend. |

### Category B: Should Fix Now (missing coverage)

| # | Edge Case | Layer | Description | Expected Behaviour | Risk |
|---|---|---|---|---|---|
| B1 | clamp_earliest without latest_time in interpret path — missing basis copy | Interpret path (line 3728–3744) | When clamp_earliest fires and _latest is not None, the basis says "clamped because partly passed" (good). When _latest is None (open-ended), basis says "open-ended start time had already passed" (also good). But if both earliest and latest are None after clamping, the 	emporal_clarifying is not updated. | Minor copy clarification may be swallowed. | Low — correct clamp behaviour, only the clarifying question might be stale. |
| B2 | Same-day latest_time == now_time exact boundary | Supervisor path (line 5734) | User says "Book today before 10 AM" and now is exactly 10:00. evaluate_same_day_window returns window_fully_past (since 10:00 <= 10:00). The supervised path correctly short-circuits. Covered. | Already covered. | None. |
| B3 | date_to crosses midnight into the past | Slot normalizer | If date_from is today but date_to is yesterday (impossible by validation, but worth noting). SlotSearchProposalIn.validate_date_range() catches date_to < date_from. | Already covered. | None. |
| B4 | "today" + eference_date is in the past | Route intake | Session's eference_date is a past date (stale session). The past-date guard catches absolute dates < reference_date, but "today" resolves to the reference_date, which is in the past relative to wall-clock time, but passes the guard. Same-day window check would also pass because today == reference_date. This is the intended stale-session behaviour — session freshness guards handle this via session_reference_date_stale / stale_session_revision. | Already covered via session freshness. | None. |

### Category C: Worth Adding Executable Fixtures

| # | Edge Case | Layer | Description | Recommendation |
|---|---|---|---|---|
| C1 | Same-day open-ended "after X" passes 24-hour boundary | Pure + route | If clinic_now is 23:00 and user says "after 10 AM", clamp_earliest sets earliest to 23:00. Still on the same day, correct. If clinic_now is 00:01 and user said "after 10 AM yesterday", the resolved_date would be today (not yesterday), so same-day check returns 
ot_same_day. This is correct — the temporal policy is day-agnostic within the pure function. | No gap found; consider an integration-level assertion. |
| C2 | Same-day window_fully_past supervised path with open-ended latest only | Supervised path | User says "Book today before 10 AM" (latest only), clinic_now 10:30. The pure function returns window_fully_past. The supervised path at line 5734 catches ALL window_fully_past cases (doesn't check _earliest), so it correctly short-circuits. | Already covered — verify with an executable scenario. |
| C3 | Exact-now earliest boundary | Pure + supervised | earliest_time == now_time → ok (strict < for clamp). At the exact boundary, the slot is bookable. | Already covered by unit test 	est_same_day_window_ok_at_exact_earliest_boundary. |
| C4 | date_to exceeds 14-day ceiling | Supervised path | If user's slot search spans >14 days, SlotSearchProposalIn clamps. Normalizer does not test this explicitly. | Low risk; validation is in the schema. |

### Category D: Defer / Document Only

| # | Edge Case | Layer | Description | Recommendation |
|---|---|---|---|---|
| D1 | Raw mutation date-policy separate from slot search | Product policy | Whether a clinic can backdate an appointment creation (e.g., "create an appointment from yesterday"). The current system blocks past-date slot searches but does not block raw appointment creation with a past date. | Defer to product policy sprint. |
| D2 | Timezone boundary at clinic-local midnight | Pure + route | If a same-day request is received at 23:59 and the slot search runs at 00:01 in the same timezone, the date has changed. The same-day check returns 
ot_same_day correctly. But if the request was made at 23:59 and confirmed at 00:01, the reference_date from the session (previous day) would mismatch the current day in the freshness check. | Already covered via stale_reference_date / session_reference_date_stale. |

## Implementation Recommendation

0. **Fix A1 first** — it is the only genuine route-level gap found. The fix is a one-line change: relax the _earliest is not None condition at line 3718 to also handle latest_time only:

`python
# Current (gap):
if (
    same_day_decision.kind == "window_fully_past"
    and _earliest is not None
    and _latest is not None
):
# Proposed:
if (
    same_day_decision.kind == "window_fully_past"
    and (_latest is not None)
):
`

This catches both "between X and Y" (both set) and "before Y" (latest only). The "ask" band copy is already generic: "Same-day request: the requested time window has already passed today."

1. Add window_fully_past tests for the supervised path with only-latest (C2) — the code handles it, but there is no executable test asserting it short-circuits without running slot search.

2. Everything else in Category C-D is either already covered, correctly deferred, or low risk.

## Out of Scope (Repeated for Clarity)

Production code edits, CI config, GitHub Pages, Diary UI, taskpane/Word assets, raw appointment mutation, DB migrations, session-store internals, LLM prompting, practice knowledge advisory substrate, diary grid rendering, waiting-area panels, booking slots rendering.

## Acceptance Checks

- Edge-case matrix is complete and internally consistent.
- Each edge case identifies the layer, route, and expected behaviour.
- The interpret path gap (A1) is clearly documented with a proposed fix.
- No production files are modified.

## Risks / Ambiguities

- The interpret path gap (A1) was identified via static analysis of the route code. It has not been runtime-verified — the proposed one-line fix may need minor copy adjustments.
- The supervised path behaviour for window_fully_past with only-latest was traced statically; an executable scenario fixture would confirm.
- 14-day ceiling enforcement is in the schema validation (SlotSearchProposalIn) — not exercised by normalizer tests, but schema-enforced.

