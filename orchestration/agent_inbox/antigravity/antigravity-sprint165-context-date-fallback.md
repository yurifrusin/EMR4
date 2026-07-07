# Sprint 165 Context Date Fallback Review Packet

- **Author**: Antigravity/Gemini Worker Lane
- **Date**: 2026-07-07
- **Target File**: [antigravity-sprint165-context-date-fallback.md](file:///C:/Users/sarashera/emr4/orchestration/agent_inbox/antigravity/antigravity-sprint165-context-date-fallback.md)
- **Status / Verdict**: **APPROVED**

---

## 1. Executive Summary & Verdict

We have reviewed the uncommitted changes in [C:/Users/sarashera/emr4](file:///C:/Users/sarashera/emr4) comprising one new executable receptionist scenario fixture and an updated [README.md](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/README.md).

The new fixture represents a high-value contract test that verifies the context fallback rule:
- When a booking instruction omits the date and no diary or session context is provided, Bernie must return `clarification_required` and explicitly ask for the missing date instead of guessing, assuming a default date (like today/tomorrow), or utilizing reference date context.

All tests have been successfully verified locally via Pytest using the [test_bernie_scenario_integrity.py](file:///C:/Users/sarashera/emr4/tests/test_bernie_scenario_integrity.py) integrity suite and the [test_scenario_replay.py](file:///C:/Users/sarashera/emr4/tests/bernie_scenarios/test_scenario_replay.py) execution harness.

We issue a verdict of **APPROVED**. No blocking findings were identified, and no polish adjustments are required.

---

## 2. Reviewed Scope

The following files were reviewed:
1. **[README.md](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/README.md)**: Updated to document the new `context-fallback prompts`.
2. **[interpret_context_date_missing_no_context.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_context_date_missing_no_context.yaml)**: Verifies that when a booking request contains patient, practitioner, time, and duration but omits a date and passes `context_frames: []`, the system returns `clarification_required` asking for the date.

---

## 3. Product & Receptionist Usability Assessment

From a receptionist workflow and clinical safety perspective, the fallback behavior is correctly designed:
- **No Guessing**: Guessing a date when the receptionist omits it (and provides no UI context like an active view or selected appointment) is extremely dangerous in clinical systems. It can lead to booking appointments on arbitrary dates without the patient's or receptionist's explicit consent.
- **Clear Prompting**: Returning `clarification_required` with the clarifying question `"Which day would you like me to check?"` aligns perfectly with product usability.
- **Null Safety**: Ensuring `command_candidate.date_from` is `null` ensures the system downstream cannot proceed with slot selection using a guessed date.

This fallback logic is cleanly implemented at the end of `resolve_booking_date_transition` in [bernie_transition_table.py](file:///C:/Users/sarashera/emr4/app/services/bernie_transition_table.py#L106-L111):
```python
    return DateResolutionTransition(
        transition_id="date.ask_missing_context",
        action="ask",
        basis="No date was supplied and no diary/session date context was available.",
        clarifying_question="Which day would you like me to check?",
    )
```
And matched to the user-facing string in [appointments.py](file:///C:/Users/sarashera/emr4/app/routers/appointments.py#L3702-L3703):
```python
        if missing_fields[0] == "date_from":
            return "Which day would you like me to check?"
```

---

## 4. Honest Edge-Contract Labels & Provider Boundaries

- **No Overclaiming**: The fixture uses `"provider_metadata.provider": fake` and `"provider_metadata.live_provider": false`, confirming it verifies only local routing/normalizer contract rules instead of pretending to evaluate live model intelligence.
- **Provider Protection**: The execution harness strictly intercepts provider calls, listing `provider_called` under `forbidden_outcomes`.
- **No Side Effects**: The fixture enforces `appointment_written: false` and `audit_written: false` under `forbidden_outcomes` and `expected` to ensure that interpretation remains a non-mutating action.

---

## 5. Gate Integrity & Boundary Assessment

The reviewed changes adhere strictly to EMR4 sandbox boundaries:
- **No Trove/H-series Profiles**: The fixture uses baseline development seed data. It does not import or couple to raw trove historical diary files or H-series profile schemas.
- **No Semantic Promotion (H15)**: The fixture does not touch semantic gate structures or promote H15 semantic appointments.
- **No Database/Memory Coupling**: RAG/GraphRAG mechanisms, Access AI, and semantic memory layers are not imported or coupled.

---

## 6. Accepted Polish & Deferred Suggestions

### Polish
No outstanding polish points are identified. The README updates and scenario YAML are clean and match the directory's standard naming and structuring conventions.

### Deferred Suggestions
- **Multi-Field Clarification**: If both the practitioner and the date are missing, verify that the system returns both in `missing_fields` and produces a combined clarifying question (e.g., `"I need the doctor or nurse, and the day before I search."`). This could be covered in a future boundary scenario.
