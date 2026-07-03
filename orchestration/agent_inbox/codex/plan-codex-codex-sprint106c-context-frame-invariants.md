# plan-codex-codex-sprint106c-context-frame-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex-worker |
| Branch | `codex/current` |
| Source Task | `codex-sprint106c-context-frame-invariants` |
| Status | accepted |
| Created | 2026-07-03 13:20 +1000 |
| Source HEAD | `61014e1` |

## Plan Summary

Plan deterministic invariant and harness coverage for Bernie typed context frames so world facts, advisories, stale evidence, roster/schedule availability, true no-slot outcomes, and model uncertainty cannot collapse into the same UI or API state.

## My Understanding

Sprint 106C is plan-only. The later implementation should add invariant and harness coverage for Bernie typed context frames so Bernie can separate world facts from advice and uncertainty: real no-slot, roster unavailable, stale state, future-appointment advisory, and model uncertainty must not collapse into the same "no matching times" outcome.

## Intended Surface / Boundary

Backend test/harness surface first, with UI smoke only if the frame contract is rendered in the Diary panel. No production edits in this planning step.

## Out Of Scope

No persisted Bernie session table, migrations, frontend state-machine migration, autonomous booking, live-provider proof, broad router rewrite, or public JSON breaking change.

## Files Expected To Edit Later

- New: `tests/test_bernie_context_frame_invariants.py`
- Likely extend: `tests/test_bernie_supervised_booking_wrapper.py`
- Likely extend: `tests/test_bernie_no_slot_suggestions.py`
- Likely extend: `tests/test_bernie_confidence_policy.py`
- Possibly extend: `tests/test_bernie_domain_package.py`
- Possibly extend: `review/test_diary_smoke.py` only for receptionist render guards
- Possibly production later, after approval: `app/services/bernie/context.py` or a new `app/services/bernie/frames.py`, plus additive schema exports in `app/schemas/appointments.py`

## Implementation Steps

1. Define a pure context-frame invariant harness with fixture frames for:
   - `slot_search.no_candidates` with roster/schedule available: true no-slot.
   - `roster.unavailable` / `schedule.unavailable`: practitioner not rostered, no schedule, or day off.
   - `state.stale`: reference date, turn ref, candidate freshness, or proposal freshness mismatch.
   - `patient.future_booking_advisory`: existing future appointment warning that must not block slot search by itself.
   - `model.uncertainty`: confidence/axis ask state that requires clarification, not no-slot copy.
2. Add assertions that each frame has stable taxonomy fields: `type`, `status`, `basis`, `source`, `reference_date`, `fresh_for_turn_ref` or equivalent freshness evidence, and non-PHI compact payloads.
3. Extend supervised-booking/no-slot tests so zero candidates are classified only when slot search actually ran against a valid roster/schedule window.
4. Add router-level tests proving roster/schedule unavailable does not return ordinary "Bernie found these times" or "no matching free times" as if slots were searched.
5. Add confidence-policy tests proving model uncertainty produces clarification/ask bands, not no-slot, stale, or roster diagnostics.
6. Add or update the existing Diary smoke render guard only if the UI consumes/display frames: advisory future appointment text must coexist with no-slot or candidates without masquerading as either.

## Acceptance Checks

- Focused backend pytest for new/changed Bernie tests passes.
- Existing focused suites still pass: `tests/test_bernie_confidence_policy.py`, `tests/test_bernie_no_slot_suggestions.py`, `tests/test_bernie_supervised_booking_wrapper.py`, `tests/test_bernie_domain_package.py`.
- If UI touched later: `pytest review/test_diary_smoke.py -q` passes.
- No DB writes on interpret, context-frame assembly, no-slot, advisory, or stale-state paths.
- Margaret Thompson / Dr Shera release-gate prompt remains covered and not relabelled as live unless non-intercepted.

## Risks / Ambiguities

The main ambiguity is whether "roster unavailable" should be a block, an ask, or a typed no-slot sibling. Ariadne recommendation: keep it distinct from true no-slot and phrase it as schedule/roster information, not availability exhaustion.

## Codex Plan Review

- Review result: Accepted. This plan provides the deterministic testing spine Sprint 106C needs and complements, rather than duplicates, the backend contract and Diary UX plans.
- Required changes before implementation: Align exact frame type/reason-code names with the accepted backend contract plan before writing tests. Do not add UI smoke coverage unless the implementation actually changes Diary rendering.
- Approved to proceed: yes, after the backend context-frame contract plan is accepted and Ariadne releases implementation.
