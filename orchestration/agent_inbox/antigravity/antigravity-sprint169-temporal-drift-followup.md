# Sprint 169 Review Packet: Temporal Drift Follow-up Scenario

- **Date:** 2026-07-07
- **Author:** Antigravity
- **Project:** EMR4 Centaur
- **Workspace:** `C:/Users/sarashera/emr4`
- **Target Fixture:** [interpret_context_temporal_drift_followup.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_context_temporal_drift_followup.yaml)
- **Documentation Update:** [README.md](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/README.md)

---

## 1. Executive Summary

This review packet evaluates the uncommitted Sprint 169 changes, specifically:
1. The new fake-provider route-level scenario fixture `interpret_context_temporal_drift_followup` designed to test relative-date corrections that resolve against a changed turn reference date while preserving threaded context.
2. The corresponding update in the test corpus documentation ([README.md](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/README.md)).

All 24 tests in `tests/bernie_scenarios/` pass successfully (23 passed, 1 expected failure `harness_demo_clarification_merge_xfail.yaml` as per test suite definitions), proving that the new temporal drift logic works exactly as intended under the fake provider and does not introduce regressions.

---

## 2. Detailed Turn-by-Turn Analysis

### Turn 1: Initial Booking Instruction
* **Instruction:** `"Book Margaret Thompson with Dr Shera next Tuesday at 09:00 for 20 minutes"`
* **Reference Date:** `2026-07-08` (Wednesday)
* **Context Frames:** `[]` (Empty, representing the beginning of a conversation)
* **Execution & Assertions:**
  - Status is `200 OK`.
  - The patient name resolves to `{patient_id}` and practitioner name resolves to `{practitioner_id}`.
  - The natural relative date phrase `"next Tuesday"` is resolved relative to the reference date `2026-07-08`. Since Wednesday is weekday index 2 and Tuesday is index 1, `resolve_weekday_date` in [temporal.py](file:///C:/Users/sarashera/emr4/app/services/diary/temporal.py) calculates `days_ahead = (1 - 2) % 7 = 6`. This yields `2026-07-14`.
  - The command candidate date matches `2026-07-14`, time matches `09:00`, and duration matches `20` minutes.
  - The backend stores a `requested_appointment` context frame in the response payload.

### Turn 2: Follow-up Instruction with Temporal Drift
* **Instruction:** `"Actually make it tomorrow"`
* **Reference Date:** `2026-07-09` (Thursday)
* **Context Frames:** Omitted in input.
* **Execution & Assertions:**
  - Because `context_frames` is omitted in the test definition, the replay harness in [replay.py](file:///C:/Users/sarashera/emr4/tests/bernie_scenarios/replay.py) auto-threads the prior turn's `requested_appointment` context frame.
  - The new instruction `"Actually make it tomorrow"` is parsed. The word `"tomorrow"` is captured as a relative date phrase by `DATE_RE` in [temporal.py](file:///C:/Users/sarashera/emr4/app/services/diary/temporal.py).
  - Crucially, the turn's reference date has drifted to `2026-07-09`.
  - In [bernie_slot_normalizer.py](file:///C:/Users/sarashera/emr4/app/services/bernie_slot_normalizer.py), `_parse_date` resolves `"tomorrow"` against the new reference date (`2026-07-09`), successfully yielding `2026-07-10`.
  - Since the follow-up instruction only specifies a new date ("tomorrow"), the other fields (patient, practitioner, start time, duration) are missing from the raw parse.
  - In [appointments.py](file:///C:/Users/sarashera/emr4/app/routers/appointments.py), `_resolve_bernie_interpretation_context` merges the missing fields from the prior context frame. The merged fields are recorded, generating a `clarification_merge` assumption:
    `"assumptions.0.field": "clarification_merge"`.
  - The preserved fields (`patient_id`, `practitioner_id`, `earliest_time`, `duration_minutes`) are verified by the harness to ensure they have not drifted from their Turn 1 values.
  - Normalization constraint assert confirms `normalization.constraint.date_from` resolves to `"2026-07-10"`.

---

## 3. Key Design & Architectural Highlights

### A. Automatic Context Threading
The replay engine dynamically checks for `context_frames` in the scenario input. When omitted, it fetches the preceding turn's `requested_appointment` frame from `last_interpret_response`. This accurately simulates the frontend SPA taskpane behavior where the frontend sends the current state history back to the backend on subsequent turns.

### B. Temporal Reference Date Independence
By passing the active turn's `reference_date` (`2026-07-09`) to the interpreter and normalizer, the system avoids stale calculation bugs (which would have calculated "tomorrow" from the initial date `2026-07-08` as `2026-07-09` instead of `2026-07-10`). This ensures relative temporal drift is resolved correctly based on the current context of the utterance.

### C. "New-Reply-Wins" Merger Logic
During the context merge phase, the new instruction's properties take absolute precedence over the prior frame's properties. Because the user specified a new date ("tomorrow"), the old date (`2026-07-14`) is discarded, while other non-clashing fields (like `earliest_time` and `duration_minutes`) are successfully merged.

---

## 4. Test Verification Summary

The test suite was run via `.venv\Scripts\pytest tests/bernie_scenarios/ -v` on the local workspace environment.

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\sarashera\emr4
configfile: pyproject.toml
plugins: anyio-4.14.0
collected 24 items

tests\bernie_scenarios\test_scenario_replay.py .x......................  [100%]
================= 23 passed, 1 xfailed, 2 warnings in 10.62s ==================
```

The test `test_bernie_scenario_replay[interpret_context_temporal_drift_followup]` executes and passes successfully, confirming:
- Status code is `200` for both turns.
- `command_candidate.date_from` is resolved to `"tomorrow"` in the raw command output.
- `normalization.constraint.date_from` is resolved to `"2026-07-10"` in the normalized output.
- The `clarification_merge` assumption is correctly injected.
- All forbidden outcomes (writes to database or provider calls) are prevented.
