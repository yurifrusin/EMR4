# plan-codex-codex-sprint-r4-deepseek-past-date-hardening

| Item | Value |
|---|---|
| To | codex |
| From | codex (DeepSeek Flash worker) |
| Branch | `codex/sprint-r4-past-date-hardening` |
| Source Task | `codex-sprint-r4-deepseek-past-date-hardening` |
| Status | submitted |
| Created | 2026-07-05 15:35 +1000 |
| Source HEAD | `20a420f` |

## Plan Summary

Add a past-date guard to `normalize_slot_search_command()` that blocks absolute dates before the reference_date with a typed `past_date` block issue. The normalizer is the earliest shared gate for all three flows (interpret context resolution, supervised booking, slot-search-from-command). Existing `safe=False` handling in all callers propagates the block correctly without router-level changes. Followed by focused tests for normalizer, interpret route, and supervised booking route.

## My Understanding

The current `normalize_slot_search_command()` already accepts a `reference_date` parameter but only uses it for resolving relative tokens ("today"/"tomorrow"). Absolute ISO dates (e.g. "2026-07-01") pass through without temporal grounding — the function treats them as valid regardless of whether they precede the reference date.

Downstream:
- `SlotSearchProposalIn.validate_date_range()` validates only `date_to >= date_from` and the 14-day ceiling — no past-date check.
- `evaluate_same_day_window()` returns `kind="not_same_day"` for past absolute dates, which is silently ignored by both callers (confidence-policy temporal axis at line ~3705 and supervised booking flow at line ~5614).
- `_build_slot_search_proposal()` iterates schedule dates unconditionally — it would search for slots on a past date.

The cleanest gate is the normalizer:
- It is pure (no DB, no LLM, no side effects)
- It already receives `reference_date` from all callers
- It is called by all four entry points: interpret context resolution, supervised booking, POST /proposals/slot-search/normalized, and POST /proposals/slot-search
- Existing `safe=False` handling in all downstream paths correctly returns blocked results with typed issue codes

Only the confidence-policy temporal axis has a cosmetic issue: it would show `band="assume"` (because `has_explicit_date=True`) even when the normalizer blocks the past date. The overall decision is correct (lattice-min "block" from slot_validity axis) but the temporal axis is misleading. A one-line refinement can fix this.

## Intended Surface / Boundary

### Affected (must change)
- `app/services/bernie_slot_normalizer.py` — `normalize_slot_search_command()`: add past-date block when `date_from < reference_date`
- `app/routers/appointments.py` — `_resolve_bernie_interpretation_context()`: add past-date temporal check so the temporal axis shows `band="block"` for past explicit dates

### Must NOT change
- `app/services/diary/temporal.py` — keep `evaluate_same_day_window()` as pure same-day logic; no new kind values
- `app/routers/appointments.py` — `_build_slot_search_proposal()` and `_bernie_supervised_booking_wrapper()`: normalizer gate is sufficient; the existing `not normalization.safe` check at line ~5585 already returns `_bernie_supervised_blocked()` correctly
- `app/schemas/appointments.py` — no schema changes; `AppointmentProposalIssue` already supports arbitrary `code` values with `severity="blocked"`
- D8 collision hardening (`test_bernie_d8_collision_source_hardening.py`, `has_existing_booking_on_requested_day`, `build_patient_booking_context`) — unchanged
- Diary UI, taskpane, Word assets
- Live provider calls, confirm/create logic, appointment mutation endpoints

## Out Of Scope

- Any router-level changes beyond the confidence-policy temporal axis refinement
- Changes to `SlotSearchProposalIn.validate_date_range()` (keep it focused on range-consistency)
- Changes to `evaluate_same_day_window()` or `app/services/diary/temporal.py`
- Changes to `_build_slot_search_proposal()`, booking creation, status updates, cancel
- D8 cap overflow / source-self-exclusion logic
- Broad session store or session policy redesign
- Diary UI, taskpane, Command Centre, Word templates
- Any confirm/create-proposal mutation paths
- Live provider/Longcat/Gemini calls

## Files I Expect To Edit

1. `app/services/bernie_slot_normalizer.py` — Add ~6 lines: past-date check in `normalize_slot_search_command()` after `date_from` parsing, before "Require mandatory fields"
2. `app/routers/appointments.py` — Add ~6 lines in `_resolve_bernie_interpretation_context()`: past-date check in temporal axis after same-day window evaluation
3. `tests/test_bernie_slot_normalizer.py` — Add 2-3 unit tests: past absolute date blocked, past date with date_to, past date without reference_date passes (backward compat)
4. `tests/test_bernie_confidence_policy.py` — Add 1 route-level test: past explicit date in interpret flow returns blocked with temporal axis showing block
5. `tests/test_bernie_supervised_booking_wrapper.py` — Add 1 route-level test: past explicit date in supervised flow returns blocked

## Implementation Steps

1. **Normalizer gate** — In `normalize_slot_search_command()` after `date_from` is parsed (line ~140 in bernie_slot_normalizer.py), before "Require mandatory fields":

   ```
   if date_from is not None and reference_date is not None and date_from < reference_date:
       blocks.append(_issue("past_date", "blocked", f"date_from {date_from} is before reference date {reference_date}."))
   ```

   The existing "Require mandatory fields" check (after this) already returns `safe=False` when `blocks` is non-empty. No other path change needed.

2. **Temporal axis refinement** — In `_resolve_bernie_interpretation_context()` (router), after the same-day `window_fully_past` / `clamp_earliest` checks (~line 3737), add:

   ```
   if resolved_date is not None and clinic_now.date() > resolved_date:
       temporal_band = "block"
       temporal_basis = f"The requested date ({resolved_date}) is before today ({clinic_now.date()})."
   ```

   This ensures the temporal axis shows `band="block"` for past dates even though normalization already blocks. The overall decision is already correct without this, but the temporal axis would otherwise misleadingly show `"assume"`.

3. **Normalizer unit tests** — In `test_bernie_slot_normalizer.py`:

   - `test_past_absolute_date_blocked`: `date_from="2026-06-01"` with `reference_date=date(2026,7,1)` ? `safe=False`, first block code == "past_date"
   - `test_past_date_with_future_date_to_still_blocked`: past `date_from` with future `date_to` ? still blocked because `date_from` itself is past
   - `test_today_and_tomorrow_work_unchanged`: existing tests pass; also verify `"today"` resolves to `reference_date` which equals itself ? not past ? allowed

4. **Interpret route test** — In `test_bernie_confidence_policy.py`:

   - `test_past_date_interpret_returns_blocked`: POST to interpret endpoint with `date_from` in the past relative to `reference_date` ? `safe=False`, `result="blocked"`, temporal axis shows `band="block"`

5. **Supervised route test** — In `test_bernie_supervised_booking_wrapper.py`:

   - `test_past_date_supervised_returns_blocked`: POST to supervised endpoint with `date_from` in the past ? `safe=False`, `result="blocked"`, `normalization.blocks[0].code == "past_date"`

6. **Existing behavior preservation** — Run existing D8 collision tests (`test_bernie_d8_collision_source_hardening.py`, `test_bernie_d8_patient_collision_source_hardening.py`) to confirm they remain green. Same-day `window_fully_past` tests (`test_bernie_temporal_policy.py`) unchanged.

## Visual / Behavioural Acceptance Checks

- Any absolute `date_from` before `reference_date` returns `safe=False` with `blocks[0].code == "past_date"` and `summary` containing "before reference date"
- "today" resolves to `reference_date`, which equals `reference_date` ? not before ? allowed (same-day behavior preserved)
- Future dates unchanged — `date(2026, 8, 1)` with `reference_date=date(2026, 7, 1)` passes normalization as today
- No change to same-day `window_fully_past` behavior (returns "ask" in confidence policy, "clinic_day_exhausted" in supervised flow)
- No change to D8 collision tests — same patient collision logic, same cap, same self-exclusion
- Interpret route shows temporal axis `band="block"` for past explicit dates
- Supervised route returns blocked with `past_date` issue code
- No changes to `_build_slot_search_proposal`, diary frames, session events, confirm gate, or appointment mutation

## Risks / Ambiguities

- **reference_date vs clinic_now**: The normalizer uses the caller-supplied `reference_date` (which is set during Bernie session creation to the clinic-local date). The router temporal check uses `clinic_now` from `_clinic_local_now()`. These should always agree in practice. If they differ (e.g. session straddles midnight), the normalizer gate uses `reference_date` (the session anchor) which is the stricter check.
- **`date_to` without `date_from`**: Not possible — `SlotSearchProposalIn` defaults `date_to = date_from` when absent. If `date_from` is past, the whole range is past. No edge case.
- **Past accept via slot-search endpoint**: `POST /proposals/slot-search` (line 4810) calls `normalize_slot_search_command(body, reference_date=reference_date)`. The `reference_date` comes from a query param `reference_date: Optional[date_type] = Query(default=None)`. If omitted, no past-date check runs. This is acceptable because the interpret and supervised flows always supply `reference_date`. The direct slot-search endpoint is a developer/admin affordance.
- **Backward compat**: The check only fires when `reference_date is not None`. Existing callers that omit `reference_date` (none in practice after the Bernie session refactoring) would retain existing behavior. All current call sites pass `reference_date`.

## Verification

After implementation (after `complete sprint task` approval):

```powershell
# Normalizer unit tests
pytest tests/test_bernie_slot_normalizer.py -v -k "past" --no-header -q

# Interpret route confidence policy test
pytest tests/test_bernie_confidence_policy.py -v -k "past_date" --no-header -q

# Supervised booking wrapper test
pytest tests/test_bernie_supervised_booking_wrapper.py -v -k "past_date" --no-header -q

# Existing D8 collision tests (must stay green)
pytest tests/test_bernie_d8_collision_source_hardening.py -v --no-header -q
pytest tests/test_bernie_d8_patient_collision_source_hardening.py -v --no-header -q

# Existing temporal policy tests (must stay green)
pytest tests/test_bernie_temporal_policy.py -v --no-header -q

# py_compile touched files
python -m py_compile app/services/bernie_slot_normalizer.py
python -m py_compile app/routers/appointments.py
```

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

