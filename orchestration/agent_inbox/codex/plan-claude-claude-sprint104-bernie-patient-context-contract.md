# plan-claude-claude-sprint104-bernie-patient-context-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint104-bernie-patient-context-contract` |
| Status | integrated |
| Created | 2026-07-02 15:31 +1000 |
| Source HEAD | `e6031d7` |

## Plan Summary

Add a deterministic, read-only patient_booking_context service plus compact recent/future booking summary schemas, a typed no-slot suggestion contract, and additive state-memory/freshness fields to Bernie booking responses. Backend/API only, plan-gated. Context is fetched ONLY after exact patient recognition; availability stays deterministic; no mutation before staff confirmation; no live-Gemini dependency in tests.

## My Understanding

Sprint 104 turns Bernie from a single-prompt panel into an explicit conversational workflow. This packet owns the backend/API slice: (1) after a patient is recognized (exact register match yielding patient_id in app/routers/appointments.py::_resolve_patient_from_instruction), provide a compact patient_booking_context of recent past and upcoming future appointments plus derived signals (notably an existing-future-follow-up warning) WITHOUT dumping the whole diary or interpreting clinical note text; (2) define a typed no-slot suggestion response contract distinct from the existing clinic_day_exhausted signal so an empty candidate list returns structured next-step suggestions rather than free text; (3) add additive conversational state-memory/freshness fields (the immutable request_reference_date echo already exists; add context generated_at plus a stale/freshness derivation) so the UI can detect and clear stale state. Recognition (do we know who this is) stays separate from details verification (DOB/identity check before linking): booking context is keyed strictly on a recognized patient_id and fuzzy/ambiguous candidates (band=ask) get NO booking history. Existing gates preserved: DisabledBookingInstructionInterpreter default, staff confirmation as the only mutation path, no LLM/provider call on the deterministic path.

## Intended Surface / Boundary

Backend/API only. Affected: app/schemas/appointments.py (new Bernie context + suggestion + freshness schema classes and additive fields on existing Bernie output models), app/routers/appointments.py (wire recognized-patient context into interpret + supervised-booking responses; add no-slot suggestion builder), a new app/services/bernie_patient_context.py (pure read-only query/derivation service), seed.py (add deterministic past + future sample appointments for the dev patient), and new focused tests under tests/. Nearby surfaces that MUST NOT change: Diary UI (docs/diary/*), taskpane, Command Centre, appointment mutation semantics, the confirm-create proposal gate, bernie_booking_interpreter.py provider selection/fallback behaviour, and clinic_day_exhausted semantics (the no-slot suggestion contract is additive and distinct).

## Out Of Scope

Any production code before approval; Diary chat/clarification UI (Antigravity workstream); transition-table/statechart invariant harness (Codex worker workstream); broad root-to-branch API rewrite; XState or any runtime state-machine dependency; voice/headset/Caller ID; Medicare/HI/IHI/PVM/OPV; limited Bernie auto-mode; privileged agent-only write paths; clinical interpretation of appointment reason/notes text (context lists structured metadata only); changing the default interpreter provider from disabled; any appointment mutation, audit write, or LLM call on the deterministic context/suggestion path.

## Files I Expect To Edit

app/schemas/appointments.py (add BernieBookingContextEntry, BerniePatientBookingContext, BernieSlotSuggestion, BernieContextFreshness; add optional patient_booking_context + context_freshness fields to BernieBookingInstructionInterpretOut and BernieSupervisedBookingOut; add optional suggestions to the no-slot result). app/services/bernie_patient_context.py (NEW: build_patient_booking_context(db, practice_id, patient_id, reference_date) -> BerniePatientBookingContext; pure read-only, practice-scoped, capped counts, derived has_future_booking / existing_future_follow_up warning, relative labels). app/routers/appointments.py (invoke context builder only when _resolve_patient_from_instruction returns a recognized patient_id; add _build_no_slot_suggestions(); populate freshness fields). seed.py (add one recent past Completed appt + one upcoming future appt for the dev patient, idempotent). tests/test_bernie_patient_context.py (NEW). tests/test_bernie_no_slot_suggestions.py (NEW). Extend tests/test_bernie_interpret_booking_instruction.py and tests/test_bernie_supervised_booking_wrapper.py for the additive fields.

## Implementation Steps

1. Add schemas: BernieBookingContextEntry (appointment_date, relative_label, status, practitioner_display, appointment_type_name, duration_minutes; NO reason/notes text), BerniePatientBookingContext (patient_key, recent_bookings capped ~3, future_bookings capped ~3, has_future_booking, existing_future_follow_up flag, counts, reference_date, generated_at), BernieContextFreshness (reference_date, generated_at, stale bool + basis), BernieSlotSuggestion (kind Literal e.g. next_available_day/widen_time_window/alternate_practitioner, human summary, typed non-mutating params, requires_confirmation True). 2. Add additive optional fields (default None / default_factory) to BernieBookingInstructionInterpretOut and BernieSupervisedBookingOut so existing callers/tests stay green. 3. Add optional suggestions:list[BernieSlotSuggestion] to the empty-candidate no-slot path (NOT clinic_day_exhausted). 4. Create bernie_patient_context.py: pure read-only, practice-scoped Appointment query by patient_id, split past vs future against reference_date, order + cap, derive has_future_booking and an existing_future_follow_up AppointmentProposalIssue (warning severity), deterministic relative labels; no mutation/audit/LLM. 5. Router wiring: after _resolve_patient_from_instruction yields a recognized patient_id (exact-match assume band ONLY, never fuzzy/ambiguous), attach patient_booking_context and the existing-future-follow-up warning; set context_freshness. 6. Add _build_no_slot_suggestions() and attach when slot search returns zero candidates but the clinic day is not exhausted. 7. Update seed.py with deterministic past+future fixtures. 8. Write tests. 9. Run verification. 10. Fill Completion Notes and submit.

## Visual / Behavioural Acceptance Checks

Behavioural (API/JSON, not UI): recognized-patient interpret response includes patient_booking_context with capped recent+future entries; fuzzy/ambiguous/no-match responses include NO patient_booking_context (recognition/verification split preserved). A patient with an upcoming appointment yields has_future_booking True and an existing_future_follow_up warning issue. A slot search with zero candidates (day not exhausted) returns typed suggestions with requires_confirmation True and no free-text-only reply; clinic_day_exhausted still behaves as today and is not replaced. context_freshness echoes the immutable request_reference_date and marks stale when a mismatching reference_date is supplied. No response on the deterministic path performs any DB write, audit write, or provider/LLM call (assert via no-network fake provider + no new rows). Availability remains deterministic (no Gemini dependency in any test). Named tests: test_bernie_patient_context.py::{test_recognized_patient_returns_context, test_fuzzy_candidate_has_no_context, test_existing_future_follow_up_warning, test_recent_and_future_capped, test_context_no_db_or_llm_writes}; test_bernie_no_slot_suggestions.py::{test_zero_candidates_returns_typed_suggestions, test_suggestions_require_confirmation, test_clinic_day_exhausted_unchanged}; freshness: test_context_freshness_echoes_reference_date, test_stale_reference_date_flagged.

## Risks / Ambiguities

1. Attachment point: interpret endpoint vs supervised-booking wrapper vs both - plan adds optional fields to both output models, wires minimally, confirms with Codex which is authoritative. 2. Cap sizes and relative-label wording are product choices; propose 3+3 and simple labels, open to Codex tuning. 3. PHI exposure: booking context only after exact recognition, never for unconfirmed fuzzy identity; no reason/notes text included. 4. No-slot suggestions must stay distinct from clinic_day_exhausted; keep additive. 5. Additive-only schema changes keep existing Bernie tests green; no migration expected (read-only over existing Appointment table). 6. seed.py fixture dates should be relative to run date to stay meaningful and idempotent.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
