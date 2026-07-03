# plan-codex-codex-sprint106c-bernie-context-frame-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex-worker |
| Branch | `codex/current` |
| Source Task | `claude-sprint106c-bernie-context-frame-contract` |
| Status | integrated |
| Created | 2026-07-03 13:28 +1000 |
| Source HEAD | `61014e1` |

## Plan Summary

Replace the blocked Claude/Fable lane with a Codex backend/domain plan for Bernie typed receptionist context frames and a reception-skill policy layer, preserving public compatibility and staff-confirmed booking safety.

## My Understanding

Sprint 106C should introduce typed Bernie receptionist context frames and a reception-skill policy layer, without changing production behavior yet beyond additive backend contracts when implemented later. The goal is to stop passing vague `context_frames: list[dict]` around as loosely trusted evidence, and instead give Bernie a deterministic, typed pre-response frame that separates:

- requested appointment facts
- roster/schedule facts
- patient booking context
- slot-search facts
- advisory warnings
- stale evidence
- model uncertainty
- hard guardrail outcomes

The model may speak more naturally from this frame, but deterministic backend logic remains authoritative. Bernie must not autonomously book. Existing future-appointment warnings stay advisory unless a deterministic guardrail applies. "No slots" must only be emitted after an actual slot search ran. "Roster unavailable/no schedule" must remain distinct from true searched-and-empty availability.

## Intended Surface / Boundary

Backend/domain only.

Primary implementation should live in the bounded Bernie package, probably new files such as:

- `app/services/bernie/frames.py`
- `app/services/bernie/policy.py`

Router changes should be thin adapters in `app/routers/appointments.py`, replacing scattered response assembly with calls into the frame/policy helpers. Existing public JSON must remain compatible: any new response fields should be optional/additive, or versioned with defaults. Current `context_frames: list[dict]` input should continue to validate.

The plan should avoid a giant per-scenario transition table. Use typed facts plus policy predicates instead: frame builders collect evidence, policy classifies it, router returns the existing response shapes.

## Out Of Scope

No persisted Bernie session DB table or Alembic migration. No autonomous booking or auto-confirm. No Diary UI implementation. No broad API-spine rewrite. No provider migration. No new LLM behavior required for correctness. No PHI/log-retention change. No removal of existing backwards-compatible fields.

## Files Expected To Edit Later

- `app/services/bernie/frames.py`
- `app/services/bernie/policy.py`
- `app/services/bernie/__init__.py`
- `app/schemas/appointments.py`
- `app/routers/appointments.py`
- `tests/test_bernie_context_frames.py`
- `tests/test_bernie_reception_policy.py`
- Possibly focused updates to existing `tests/test_bernie_*` and `tests/test_slot_*`

Avoid moving large router logic wholesale unless needed.

## Implementation Steps

1. Add typed frame schemas. Define Pydantic models/Literals for frame categories such as `requested_appointment`, `roster_schedule`, `patient_booking_context`, `slot_search`, `advisory_warning`, `stale_evidence`, `model_uncertainty`, and `guardrail_outcome`.
2. Add an aggregate context object, e.g. `BernieReceptionContextFrameSet` with `schema_version`, `reference_date`, `requested`, `roster`, `patient_context`, `slot_search`, `warnings`, `stale_evidence`, `uncertainty`, and `guardrails`.
3. Preserve public compatibility. Keep inbound `context_frames: list[dict]` accepted. Add typed parsed/derived frames as optional response fields, or keep them internal initially and expose only if Ariadne wants the contract visible now.
4. Extract frame building from router facts. Build frames from current known values: interpreted command, normalization result, identity evidence, patient booking context, same-day temporal decision, slot-search proposal, no-slot suggestions, and freshness state.
5. Add reception-skill policy helpers. Policy should return deterministic outcomes like `can_search_slots`, `must_ask_clarification`, `can_offer_candidates`, `can_prepare_proposal`, `must_block_confirmation`, `advisory_warnings_only`, `roster_unavailable`, and `search_ran_no_candidates`.
6. Wire interpreter and supervised-booking paths lightly. `interpret-booking-instruction` should use typed frames for patient/future warnings and model uncertainty, but still not search slots or mutate. `supervised-booking` should use typed frames to distinguish blocked normalization, roster unavailable, searched/no candidates, clinic-day exhausted, and confirmation-ready states.
7. Keep future appointment warning advisory. Existing future bookings should produce typed advisory warnings only. They must not block a different-day slot, must not cause "no slot", and must not suppress candidate output.
8. Add tests before or with implementation.

## Visual / Behavioural Acceptance Checks

No visual UI change required in this backend slice.

Behaviourally, existing Bernie happy paths should stay stable:

- interpret endpoint remains read-only
- supervised-booking endpoint remains read-only until confirm
- confirm endpoint remains the only Bernie booking write path
- existing response JSON fields remain present
- no new hard block from model confidence alone
- no false no-slot state without a completed slot search
- roster unavailable/no schedule remains typed separately from true no-slot
- future-appointment warning is advisory unless backed by deterministic same-day/requested-day policy

## Risks / Ambiguities

The largest risk is adding another abstraction while `appointments.py` still owns a lot of assembly. Keep the first implementation small and test-backed.

There is also a naming risk: "slot", "card", "panel", and "waiting room" are visually loaded. This backend work should refer to `slot_search.candidates` and `staff_review` only, not diary layout cards or waiting-room panels.

The frame contract should not become a giant nested state machine. Use typed evidence plus small deterministic predicates, not scenario spaghetti.

## Recommended Implementation Split

1. Backend contract slice: add frame and policy models/helpers with pure tests.
2. Router adapter slice: wire typed frames into interpret and supervised-booking paths, preserving JSON compatibility.
3. Behavioural regression slice: add focused endpoint tests for no-slot/search-ran, roster-unavailable, advisory future bookings, stale evidence, and no-mutation guarantees.

## Codex Plan Review

- Review result: Accepted as the replacement backend/domain plan for the blocked Claude lane.
- Required changes before implementation: Implement the backend contract slice first. Keep route integration additive and thin; do not turn this into a broad appointments-router rewrite.
- Approved to proceed: yes.
