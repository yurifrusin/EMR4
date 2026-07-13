# Task Packet: LC1 DW1 — Complete Temporal Through-Path

Role: DeepSeek Flash Worker (implementation owner)
Model: `deepseek-v4-flash` / high
Branch: `codex/lc1-dw1-temporal-foundation`
Source Plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-lc1-semantic-foundation-v2.md`

## Mission

Implement the complete LC1 temporal relation through-path: parser, schemas,
normalizer pass-through, interpreter wiring, slot-search consumer widening, and
supervised duplicate classifier gating. Fix the `tomorrow at 3pm` regression.

## Boundary

- Additive only: no deletion of existing patterns, no removal of existing
  behaviour, no breaking changes to existing callers.
- All new fields are `Optional[str]` with backward-compatible defaults.
- No provider calls, no live prompts, no route wiring changes (only
  consumer-side window adjustments within existing slot-search logic), no
  database writes, no confirmation/write authority changes.
- Do not touch: `app/services/bernie/scenario_spec.py` (DW2),
  `app/services/bernie/language_normalization.py` (DW2), T3 eval code, scenario
  fixtures, migrations, routes (except the slot-search consumer).

## Implementation Steps

### Step 1: Add temporal patterns to `app/services/diary/temporal.py`

1. Add `_AT_TIME_RE` pattern matching `at 3pm`, `at 3 pm`, `at 3.00pm`,
   `at 15:00`, `at 3:00pm`, `at 3:00 pm`.

2. Add `_ABOUT_TIME_RE` pattern matching `around 3pm`, `about 3pm`,
   `around 3 pm`, `about 3 pm`, `around 15:00`, `about 15:00`.

3. Define `TemporalRelationKind` as a string `Literal`:

```python
TemporalRelationKind = Literal[
    "exact", "not_before", "not_after", "interval", "approximate", "unspecified"
]
```

4. Add a `TemporalExtraction` dataclass:

```python
@dataclass(frozen=True)
class TemporalExtraction:
    earliest: str | None = None  
    latest: str | None = None
    temporal_relation: TemporalRelationKind = "unspecified"
```

5. Update `extract_natural_time_constraints` to return `TemporalExtraction`
   instead of `tuple[str | None, str | None]`. The new function must:

   - Check `_BETWEEN_TIME_RE` first → `temporal_relation="interval"`
   - Check `_AT_TIME_RE` → `temporal_relation="exact"` with `earliest=latest=parsed_time`
   - Check `_ABOUT_TIME_RE` → `temporal_relation="approximate"` with
     `earliest=parsed_time-30min`, `latest=parsed_time+30min`
   - Check `_AFTER_TIME_RE` → `temporal_relation="not_before"`, `earliest=parsed_time`
   - Check `_BEFORE_TIME_RE` → `temporal_relation="not_after"`, `latest=parsed_time`
   - If only HH:MM positional fallback produces a time with no operator match →
     `temporal_relation="unspecified"`
   - `BETWEEN` takes priority over `AT`, which takes priority over `ABOUT`,
     which takes priority over separate `AFTER`/`BEFORE`

6. Add `infer_temporal_relation(earliest, latest) → TemporalRelationKind` for
   legacy callers that only have raw time bounds: `earliest==latest` → `exact`,
   only earliest → `not_before`, only latest → `not_after`, both different →
   `interval`, none → `unspecified`.

7. Preserve backward compatibility: the existing function signature accepting
   raw instruction and returning a tuple should continue to work internally;
   add the new return type as the primary export and update callers. Or,
   change the return type to `TemporalExtraction` and update the two callers
   (`bernie_booking_interpreter.py` and any test imports).

8. Add `parse_time_fragment` support for the "pm" suffix attached to times
   with dots like `3.00pm` → `15:00`.

9. Update `__all__` to export new symbols.

### Step 2: Add `temporal_relation` to schemas

In `app/schemas/appointments.py`:

1. Add `temporal_relation: Optional[str] = None` to `SlotSearchCommandIn`
   (after line ~742, before `patient_id`). Since `model_config = ConfigDict(extra="ignore")`
   is already set, this is backward-compatible.

2. Add `temporal_relation: Optional[str] = None` to `SlotSearchProposalIn`
   (after line ~683, before `patient_id`).

### Step 3: Pass `temporal_relation` through the normalizer

In `app/services/bernie_slot_normalizer.py`, function
`normalize_slot_search_command`:

1. Read `temporal_relation` from `payload.temporal_relation` (already
   accessible as an attribute since it's on `SlotSearchCommandIn`).

2. Pass it through to the `SlotSearchProposalIn` constructor:

```python
constraint = SlotSearchProposalIn(
    ...
    temporal_relation=payload.temporal_relation,
    ...
)
```

### Step 4: Wire the interpreter to extract and set `temporal_relation`

In `app/services/bernie_booking_interpreter.py`, function
`_extract_fake_command`:

1. After line ~384 (where `_extract_natural_time_constraints` is called),
   update to consume `TemporalExtraction`:

```python
nat_extraction = _extract_natural_time_constraints(instruction)
if "earliest_time" not in values and nat_extraction.earliest:
    values["earliest_time"] = nat_extraction.earliest
if "latest_time" not in values and nat_extraction.latest:
    values["latest_time"] = nat_extraction.latest
if "temporal_relation" not in values:
    values["temporal_relation"] = nat_extraction.temporal_relation
```

2. Update the import of `_extract_natural_time_constraints` — the function
   signature changes.

3. Positional HH:MM fallback (lines ~391-395) must also set
   `temporal_relation="unspecified"` when no explicit operator was matched.

### Step 5: Widen the slot-search window for `exact`

In the slot-search route or service (the consumer that builds the ORM query
from `SlotSearchProposalIn`):

1. When `temporal_relation == "exact"` (or inferred as `exact` via
   `infer_temporal_relation` for legacy commands):
   - Keep `earliest_time` as-is
   - Set `latest_time = earliest_time + timedelta(minutes=5)` (the minimum
     slot unit)
   - This ensures the half-open search `[earliest, latest)` captures the exact-time
     slot

2. When `temporal_relation == "approximate"`:
   - The ±30 minute window is already set in the extraction; pass through unchanged

3. For all other relations, use the bounds as-is (existing behaviour).

Locate the slot-search consumer — likely in `app/routers/appointments.py` or
`app/services/diary/` — and identify where `SlotSearchProposalIn` is consumed
to build the ORM query. Add the widening there.

If the slot-search consumer code is complex or unclear, add the widening in a
new pure helper function `adjust_search_window_for_relation(constraint:
SlotSearchProposalIn) -> SlotSearchProposalIn` in `app/services/diary/temporal.py`
and call it from the route before the ORM query.

### Step 6: Gate duplicate classification on `temporal_relation`

In the supervised duplicate classifier (likely in `app/services/diary/` or
the supervised booking route):

1. Only `temporal_relation == "exact"` can produce `existing_booking_found`.
2. `approximate`, `unspecified`, `not_before`, `not_after`, and `interval` must
   NOT produce `existing_booking_found` even if a booking happens to exist in
   the window.
3. Add a test that proves `approximate` finds a booking in the window but does
   NOT classify it as an exact duplicate.

### Step 7: Tests

In `tests/test_bernie_temporal_policy.py`:

1. Test `_AT_TIME_RE` matches all variants: `at 3pm`, `at 3 pm`, `at 3.00pm`,
   `at 15:00`, `at 3:00pm`, `at 3:00 pm`.
2. Test `_ABOUT_TIME_RE` matches `around 3pm`, `about 3pm`, `around 15:00`,
   `about 15:00`.
3. Test `extract_natural_time_constraints` returns correct
   `TemporalExtraction` for each operator.
4. Test `infer_temporal_relation` for all edge cases.
5. Test time-form variants with dots: `3.00pm` → `15:00`.
6. Test `approximate` window: `around 3pm` → earliest `14:30`, latest `15:30`.
7. Test `unspecified`: bare `3pm` with no operator → `unspecified`.
8. Test that `at 3pm` no longer produces `None, None`.
9. Test backward compatibility: legacy commands without `temporal_relation`
   are inferred correctly.
10. Test that `SlotSearchCommandIn` accepts `temporal_relation` as a string.

## Out of Scope

- Scenario spec, language normalization, coverage lattice (DW2).
- Independent review artifact (DW3).
- T3 evaluation code changes.
- Routes, provider calls, database writes, confirmation authority.
- `app/services/bernie/normalizer.py` (the slot-normalizer facade).
- `app/services/bernie/scenario_spec.py`.
- `app/services/bernie/language_normalization.py`.

## Acceptance Checks

```powershell
# 7. All temporal tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_temporal_policy.py -q

# 8. All existing smoke tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_smoke_bernie_interpreter_script.py -q

# (Also run the smoke interpreter checks listed in the V2 plan DW1 acceptance section)
```

## Submit Instructions

When complete, from this worktree run:

```powershell
python scripts\agent_worktrees.py submit --agent deepcode --commit-message "LC1 DW1: complete temporal through-path with TemporalRelation end-to-end threading" --message "Temporal relation threaded from parser through schemas, normalizer, interpreter, slot-search consumer, and duplicate classifier. at/around/about operators implemented. approximate and unspecified defined and tested."
```
