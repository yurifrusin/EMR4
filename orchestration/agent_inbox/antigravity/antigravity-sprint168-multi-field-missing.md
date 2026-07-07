# Sprint 168 Review — Multi-Field Missing Details in Context Threading Review Packet

- **Author**: Antigravity/Gemini Worker Lane
- **Date**: 2026-07-07
- **Target File**: [antigravity-sprint168-multi-field-missing.md](file:///C:/Users/sarashera/emr4/orchestration/agent_inbox/antigravity/antigravity-sprint168-multi-field-missing.md)
- **Status / Verdict**: **ACCEPTED / APPROVED** (Verdict: ACCEPTED — no blockers)

---

## 1. Executive Summary & Verdict

We have completed the Sprint 168 review of the uncommitted changes in [C:/Users/sarashera/emr4](file:///C:/Users/sarashera/emr4). This review evaluates the implementation of multi-field missing detail prompting and practitioner UUID validation for correctness, regression risk, safety gate compliance, and completeness of test coverage.

The implementation introduces two key changes in the clinical backend routing:
1. **Prioritization of Structured Missing Fields**: Clarifying copy generation now prioritizes structured missing fields (such as doctor/nurse and day) over generic temporal clarification. This ensures that when multiple crucial booking fields are missing from a patient-only request without context, EMR4 asks for both practitioner and date coherently (e.g., *"I need the doctor or nurse, and the day before I search."*) instead of only requesting the date.
2. **Robust Practitioner Validation**: The pre-resolution step checks if `command_values["practitioner_id"]` is a valid UUID text instead of just a truthy check. This preserves live-provider-style payloads that populate the field with practitioner names (such as "Dr. Shera") rather than database UUIDs. It allows name resolution to run on instruction tokens, gather the correct warnings/assumptions/axis, and mapping the correct practitioner.

The changes are mathematically and logically sound, and all test suites verify clean execution:
- The new scenario fixture [interpret_multi_field_missing_no_context.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_multi_field_missing_no_context.yaml) executes successfully.
- Safety, provider, database, and trove boundaries remain fully respected and locked.

We issue a verdict of **ACCEPTED / APPROVED**. No blocking findings were identified.

---

## 2. Reviewed Scope

The review evaluated the following uncommitted changes:
1. **[appointments.py](file:///C:/Users/sarashera/emr4/app/routers/appointments.py)**:
   - Updated the practitioner pre-resolution guard within [_resolve_bernie_interpretation_context](file:///C:/Users/sarashera/emr4/app/routers/appointments.py#L3728) to run when `practitioner_id` is empty or non-UUID (using `_valid_uuid_text`).
   - Prioritized the structured missing fields clarifying question ([_bernie_clarifying_question](file:///C:/Users/sarashera/emr4/app/routers/appointments.py#L3688)) over the generic `temporal_clarifying` copy at [appointments.py#L4124](file:///C:/Users/sarashera/emr4/app/routers/appointments.py#L4124).
2. **[interpret_multi_field_missing_no_context.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_multi_field_missing_no_context.yaml)**:
   - Added a new single-turn receptionist scenario verifying that booking a patient without context frames results in `clarification_required` with both `practitioner_id` and `date_from` listed in `missing_fields` and asks the composite clarifying question: *"I need the doctor or nurse, and the day before I search."*
3. **[tests/fixtures/bernie_scenarios/README.md](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/README.md)**:
   - Updated scenario documentation to cover multi-field-missing contract specifications.

---

## 3. Correctness & Edge-Case Assessment

### 3.1. Structured Missing Fields Prioritization
Previously, the backend checked and populated `clarifying` using `temporal_clarifying` first:
```python
    clarifying: Optional[str] = temporal_clarifying
    if not clarifying:
        clarifying = _bernie_clarifying_question(missing_fields)
```
If a request lacked a date, `temporal_clarifying` was populated with `"Which day would you like me to check?"` or a date-transition question. If a practitioner was also missing, `_bernie_clarifying_question` was bypassed, hiding the missing practitioner warning.

By switching the priority order:
```python
    clarifying: Optional[str] = _bernie_clarifying_question(missing_fields)
    if not clarifying:
        clarifying = temporal_clarifying
```
The system checks if any required fields are missing. If so, `_bernie_clarifying_question(missing_fields)` generates a composite question summarizing all missing inputs. Only if all required fields are structurally present does it fall back to other temporal checks (like same-day past window checks) or patient candidates. This behaves correctly and prevents partial/misleading prompts.

### 3.2. Practitioner Validation for Non-UUID Values
The transition from checking `if not command_values.get("practitioner_id")` to `if not _valid_uuid_text(command_values.get("practitioner_id"))` ensures that:
- If the practitioner ID is absent or is a non-UUID name string (e.g. `"Dr. Shera"` from live-provider-style output), the pre-resolution pass runs.
- The pre-resolution step searches the user instruction text for matching practitioner tokens, which resolves to the database practitioner UUID if found.
- The downstream validation at [appointments.py#L3765](file:///C:/Users/sarashera/emr4/app/routers/appointments.py#L3765) cleanly wipes any invalid non-UUID strings in `command_values["practitioner_id"]` to `None` and maps the pre-resolved UUID (or triggers context fallbacks).
- This is robust because it prevents non-UUID strings from skipping practitioner resolution and throwing UUID validation errors later in the DB model or route response.

---

## 4. Harness & Fixture Integration

- **Verification Scenario**: The new scenario [interpret_multi_field_missing_no_context.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_multi_field_missing_no_context.yaml) executes Turn 1 correctly:
  - Input: *"Book Margaret Thompson"* with no context frames.
  - Resolved `command_candidate.patient_id` matches `{patient_id}`.
  - `command_candidate.practitioner_id` and `command_candidate.date_from` are `null`.
  - `missing_fields` returns `["practitioner_id", "date_from"]`.
  - `clarifying_question` matches `"I need the doctor or nurse, and the day before I search."`.
- **Integrity**: The test suite confirms that this scenario passes standard validation without calling any real providers or modifying state.

---

## 5. Gate Integrity & Boundary Assessment

All architectural boundaries and gates remain intact:
- **No Live Provider Calls**: Mock model configurations remain locked. No live provider queries were made during test runs.
- **No Database Writes**: Test execution verifies that neither appointments nor audit records are written (`appointment_written: false`, `audit_written: false`).
- **No Trove/RAG/Memory Access**: No historical diary streams, H15 semantic candidate builder scripts, or GraphRAG memory structures are imported or run.

---

## 6. Verification Results

All verification checks executed successfully:
1. **Scenario Replay Tests**:
   `pytest tests/bernie_scenarios/ -v` -> `22 passed, 1 xfailed` (represented as `.x.....................`)
2. **Scenario Integrity Validator**:
   `pytest tests/test_bernie_scenario_integrity.py -v` -> `8 passed, 1 skipped`
3. **Bernie Interpretation Readiness Check**:
   `scripts/bernie_interpretation_readiness_check.py` -> `runtime_or_provider_wiring_ready=false`, `runtime_gate_decision="blocked"`.
4. **Provider Boundary Readiness Report**:
   `scripts/bernie_provider_boundary_readiness_report.py` -> `live_provider_enabled=false`, `provider_calls_performed=false`, `database_access_performed=false`, `memory_or_rag_access_performed=false`.
5. **Leakage Lint**:
   `scripts/historical_diary_leakage_lint.py` -> `historical diary leakage lint safe`
6. **Whitespace Check**:
   `git diff --check` -> Passed (clean).

---

## 7. Low-Risk Notes

- **Inferred Practitioner Behavior**:
  If a live-provider payload sends a practitioner name placeholder (e.g. `"Dr. Shera"`), but the name is not found in the user's current instruction tokens, the pre-resolution pass returns `None`. Downstream, the placeholder name is wiped to `None` (since it is not a valid UUID), and the system falls back to inferring the practitioner from today's context/prior appointments for the named patient. This is correct, as it ensures user instruction naming always takes priority, with smart context inference acting as the fallback.
