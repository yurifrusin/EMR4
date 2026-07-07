# Sprint 163 Interpret Edge Fixtures Review Packet

- **Author**: Antigravity/Gemini Worker Lane
- **Date**: 2026-07-07
- **Target File**: [antigravity-sprint163-interpret-edge-fixtures.md](file:///C:/Users/sarashera/emr4/orchestration/agent_inbox/antigravity/antigravity-sprint163-interpret-edge-fixtures.md)
- **Status / Verdict**: **APPROVED WITH POLISH**

---

## 1. Executive Summary & Verdict

We have reviewed the uncommitted changes in [C:/Users/sarashera/emr4](file:///C:/Users/sarashera/emr4) comprising four new executable receptionist scenario fixtures and an updated [README.md](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/README.md).

These fixtures represent high-value, high-fidelity prompt-edge cases that directly verify the API route contract's correctness after Sprint 162. They are verified locally using Pytest, and all tests pass successfully without any validation or parsing errors.

We issue a verdict of **APPROVED WITH POLISH**. No blocking findings were identified. We recommend applying the minor polish points listed in Section 6 below during commit stage.

---

## 2. Reviewed Scope

The following files were reviewed:
1. **[README.md](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/README.md)**: Updated to outline the new edge-contract slices and clarify the route-level behavior for unknown patient name resolution.
2. **[interpret_empty_instruction_fail_closed.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_empty_instruction_fail_closed.yaml)**: Asserts validation failures (`422`) on empty instructions before provider routing.
3. **[interpret_unknown_patient_name_without_id.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_unknown_patient_name_without_id.yaml)**: Verifies that bookings with unregistered patient names produce slot-search command candidates with a `null` patient ID rather than fabricating an ID or mutating state.
4. **[interpret_visible_diary_date_context.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_visible_diary_date_context.yaml)**: Verifies context frame resolution using the visible diary date for partial instructions.
5. **[interpret_turn_reference_date_drift.yaml](file:///C:/Users/sarashera/emr4/tests/fixtures/bernie_scenarios/interpret_turn_reference_date_drift.yaml)**: Tests state robustness under reference-date drift between turns.

---

## 3. Product & Receptionist Usability Assessment

From a receptionist workflow and clinical safety perspective, these fixtures validate crucial features:
- **Empty Prompts**: Users frequently trigger accidental empty inputs (e.g. clicking enter/send prematurely). Fail-closed rejection is required to save provider token usage and prevent erroneous state machine advancement.
- **Unknown/New Patients**: In a busy clinic, booking a new patient who does not yet have a record in the database is normal. Allowing the system to search for slots first (by setting `patient_id: null`) before requiring patient registration represents a smooth, natural workflow. It avoids inventing mock IDs, which would lead to database corruption.
- **Visible Diary Context**: Receptionists constantly rely on the open diary page on their screens when requesting bookings (e.g., "Book Margaret with Dr Shera at 9:00" while looking at next Thursday). Utilizing the `visible_diary_page` context frame prevents repetitive and frustrating prompt wording.
- **Clock and Drift Control**: Clinic workstations are prone to reference-date drift, and multi-turn sessions can span across midnight. Passing explicit `reference_date` on a per-turn basis ensures relative days (like "today" or "tomorrow") resolve accurately without relying on local system clock state.

---

## 4. Honest Edge-Contract Labels & Provider Boundaries

- **No Overclaiming**: The fixtures are correctly marked with `"provider_metadata.provider": fake` and `"provider_metadata.live_provider": false` under their expectations. This prevents live LLM capability overclaiming by keeping the tests bounded to route/harness capability verification.
- **Validation Separations**: Fail-closed checks (such as the empty instruction check) verify that local API validations occur prior to making expensive downstream AI provider calls.
- **Write Protections**: All fixtures assert `appointment_written: false` and `audit_written: false`, verifying that the non-mutating `interpret` endpoint behaves as a read-only intent parser.

---

## 5. Gate Integrity & Boundary Assessment

The reviewed changes adhere strictly to the sandbox boundaries:
- **No Trove Imports**: The fixtures reference only baseline development mocks (`practice`, `practitioner`, `gp_user`, `patient`, `schedule`). No raw trove JSON or H-series profile directories are referenced.
- **No Memory Dependencies**: RAG/GraphRAG mechanisms, Access AI, and semantic memory layers are not utilized.
- **No Semantic Gates (H15)**: The fixtures are purely synthetic, avoiding any semantic labelling or fixture promotions that would bypass the Yuri-approved H15 gate.

---

## 6. Accepted Polish

We suggest the following minor, non-blocking improvements:
1. **Sentinel Patient Naming**: In `interpret_unknown_patient_name_without_id.yaml`, the patient name is `"Alice Nonexistent"`. While this is an excellent sentinel to prevent accidental database matches, adding a comment or description clarifying that this is a deliberate sentinel name for testing unknown matching makes the test-suite easier to maintain for future developers.
   - **Accepted by Codex**: the fixture was renamed from `interpret_unknown_patient_name_clarifies.yaml` to `interpret_unknown_patient_name_without_id.yaml`, and the description now calls the name an unknown sentinel patient name.
2. **Description Alignment**: In `interpret_unknown_patient_name_without_id.yaml`, the description mentions:
   > "A known practitioner and date with an unknown patient name may still produce a slot-search command, but it must not invent a patient record."
   
   To be precise, the returned envelope contains a *command candidate* (specifically, `command_candidate` in the response body), which is later resolved/run. Aligning the description's wording to state "may still produce a slot-search command candidate" makes the API-level expectation perfectly clear.
   - **Accepted by Codex**: the fixture description now says "slot-search command candidate."

---

## 7. Deferred Suggestions

- **Multi-Day Context Resolution**: For future sprints, we recommend adding fixtures that test combining multiple context frames (e.g., a `visible_diary_page` date combined with a `selected_diary_appointment` date) to verify precedence rules in the transition table.
- **Temporal Drift Bounds**: Test how the system handles large reference date changes (e.g. drift of 1+ year) to ensure normalization warnings are raised.
