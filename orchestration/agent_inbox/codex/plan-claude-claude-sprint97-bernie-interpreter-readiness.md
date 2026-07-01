# plan-claude-claude-sprint97-bernie-interpreter-readiness

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint97-bernie-interpreter-readiness` |
| Status | integrated |
| Created | 2026-07-01 09:46 +1000 |
| Source HEAD | `028e2a0` |

## Plan Summary

Fix the Bernie booking-instruction interpreter so a plain receptionist prompt such as "Make an appointment for Margaret Thompson after 3 today with Dr Shera" is not blocked solely because the live LLM interpreter provider is unavailable. Add a deterministic local fallback plus an explicit, unmissable provider-readiness contract. The interpret path stays read-only, never searches slots, never creates or confirms appointments, never writes appointment audit rows, and keeps confirmed writes behind the existing confirm endpoint. No DB schema change, no migration.

## My Understanding

Flow today: `POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction` calls `get_booking_instruction_interpreter(settings.bernie_booking_interpreter_provider).interpret(...)`, then the router helper `_resolve_bernie_interpretation_context(...)` does the DB-backed work: it resolves practitioner/patient NAMES to IDs (`_resolve_practitioner_from_instruction` / `_resolve_patient_from_instruction`), defaults a generic request to 15 minutes, re-normalizes, and recomputes safe/result/blocks. That resolver is the only place with DB access; the service module is deliberately DB-free and non-mutating.

Key defect: `_resolve_bernie_interpretation_context` early-returns when `result.command_candidate is None`. The default provider is `"disabled"` (returns `command_candidate=None`, intentionally blocked). But in the intended live posture `provider="gemini_vertex"`, when the live provider raises or is denied, `GeminiVertexBookingInstructionInterpreter.interpret()` catches and returns `_live_blocked_response(...)` which ALSO has `command_candidate=None`. So the router resolver is skipped and the prompt is blocked purely because the LLM is down, even though the deterministic `FakeBookingInstructionInterpreter` plus router name/duration resolution already produce a valid interpreted result for the very same prompt (proven by `test_fake_provider_resolves_practice_names_as_optional_context`).

So the mission prompt does NOT need the LLM: `date_from="today"` (DATE_RE), practitioner from "Dr Shera" and patient from "Margaret Thompson" (router DB resolution), duration defaulted to 15. The only LLM-only nicety is parsing "after 3" into `earliest_time`; the deterministic `TIME_RE` only matches HH:MM, so "after 3" simply yields no `earliest_time` constraint (NOT a block). Note: `bernie_slot_normalizer._parse_time` BLOCKS on any non-ISO time, so any deterministic time guess must emit HH:MM or None, never raw words.

Therefore the fix is (1) a deterministic fallback that runs the same local extractor when the live provider is unavailable, so `command_candidate` is populated and the router resolver runs, and (2) a provider-readiness contract surfaced in metadata and the smoke script so "live provider not actually ready" is impossible to miss in release checks. Both must remain non-mutating and clearly labelled as a degraded/fallback path so staff and audit can tell live vs deterministic apart.

## Intended Surface / Boundary

Backend service plus API contract only. Affected surfaces:
- `app/services/bernie_booking_interpreter.py` (fallback plus readiness helper)
- `app/config.py` (one new setting)
- `app/schemas/appointments.py` (`BernieBookingInterpreterMetadata` literals; optional readiness field only if needed)
- `app/routers/appointments.py` (interpret endpoint / `_resolve_bernie_interpretation_context` only)
- `scripts/smoke_bernie_interpreter.py` (readiness check)
- Bernie interpret tests

The non-mutating interpret endpoint stays read-only. Confirm/create proposal endpoints and their write paths are NOT touched. No diary grid, no waiting-room, no booking slot cards, no taskpane, no Command Centre, no frontend. No DB schema, no migration.

## Out Of Scope

Production code edits before plan approval. Diary frontend, taskpane, Command Centre, any UI. Live phone system / Caller ID. Medicare / OPV / PVM / IHI. GCP console setup or new paid provider integration. Broad `implementation_plan` rewrite. Any weakening of human confirmation gates — the interpret endpoint must never become a write path, and the deterministic fallback must not auto-book. No change to `confirm_bernie_create_proposal` or appointment creation.

## Files I Expect To Edit

- `app/config.py`: add `bernie_booking_interpreter_fallback` (default `"deterministic"`) gating fallback on live-unavailable.
- `app/services/bernie_booking_interpreter.py`: when the GeminiVertex live path is unavailable/denied, optionally delegate to the deterministic extractor (the `FakeBookingInstructionInterpreter` logic) instead of returning a no-command block; tag `provider_metadata` `mode="fallback_deterministic"`, `live_provider=False`, add safety flag `live_interpreter_unavailable` and a warning issue. Add a readiness helper `booking_interpreter_readiness()` that reports the configured provider, whether a live provider can be constructed WITHOUT sending text, and whether fallback is enabled.
- `app/schemas/appointments.py`: extend `BernieBookingInterpreterMetadata` literals (add `"fallback_deterministic"` to `mode`); add optional readiness fields only if the contract needs them.
- `app/routers/appointments.py`: ensure a fallback `command_candidate` flows through `_resolve_bernie_interpretation_context` (it already does once `command_candidate` is non-None); preserve/propagate the `live_interpreter_unavailable` warning so the response makes the degraded path obvious.
- `scripts/smoke_bernie_interpreter.py`: add a `--check-readiness` mode (and an `--expect-ready` style assertion) that fails non-zero when `provider="gemini_vertex"` is configured but not ready and fallback is off — the release-check signal. Keep live calls gated behind `--allow-live`.
- `tests/test_bernie_interpret_booking_instruction.py` (and/or a new `tests/test_bernie_interpreter_readiness.py`): see Acceptance Checks.

## Implementation Steps

1. Add setting `bernie_booking_interpreter_fallback: str = "deterministic"` to `app/config.py` (values `"deterministic"` or `"off"`). Default keeps simple prompts working; `"off"` preserves strict fail-closed.
2. In `bernie_booking_interpreter.py`, factor the deterministic command-building (`_extract_fake_command` plus normalization) so both `FakeBookingInstructionInterpreter` and a fallback can call it. In `GeminiVertexBookingInstructionInterpreter.interpret`, on the except/denied branch, if `settings` fallback == `"deterministic"`: build the deterministic `command_candidate` and return an interpreted-or-clarification envelope with `provider_metadata.provider="gemini_vertex"`, `mode="fallback_deterministic"`, `live_provider=False`, plus safety flag `live_interpreter_unavailable` and a warning issue `live_interpreter_unavailable`. If fallback == `"off"`: keep the current `_live_blocked_response`.
3. Crucially, the fallback must return a non-None `command_candidate` so the router resolver runs name/duration resolution exactly as for the fake path. Do NOT duplicate DB resolution in the service (keep the service DB-free).
4. Extend `BernieBookingInterpreterMetadata` `mode` Literal to include `"fallback_deterministic"`. Confirm `SlotSearchCommandIn` permissive typing already accepts the deterministic command.
5. Preserve the `live_interpreter_unavailable` warning/flag through `_resolve_bernie_interpretation_context` so it is visible in the final response (and thus to staff UI and audit).
6. Add `booking_interpreter_readiness()` returning a small typed/dict report: configured provider, fallback setting, `live_constructible` (probe provider construction only, never invoke), and a boolean `release_ok` (False when provider is live but not constructible and fallback is off). Wire it into `smoke_bernie_interpreter.py --check-readiness` with a non-zero exit when `release_ok` is False.
7. Keep all autonomous-booking language as warning-only (existing behaviour); do not block on "make an appointment".
8. Update/extend tests (below). Run focused pytest plus the smoke plus backend compile checks.

## Visual / Behavioural Acceptance Checks

No visual surface changes (no cards, slots, panels, waiting room, diary grid, or status colours are touched). Behavioural checks:

- With `provider="gemini_vertex"` and the live provider unavailable (factory raises), `POST` interpret with "Make an appointment for Margaret Thompson after 3 today with Dr Shera" returns `result="interpreted"`, `safe=true`, `command_candidate.practitioner_id == Dr Shera id`, `patient_id == Margaret id`, duration defaulted to 15, `provider_metadata.mode="fallback_deterministic"`, `live_provider=false`, and a `live_interpreter_unavailable` warning/flag is present. Zero `Appointment` and `AppointmentAuditLog` writes; `AccessAiAuditLog` limited to the bounded denial/unavailable record (or none for the deterministic fallback).
- With `fallback="off"`, the same unavailable-provider case still fails closed with `booking_interpreter_provider_unavailable` (back-compat).
- Readiness: smoke `--check-readiness` exits non-zero when `provider="gemini_vertex"` but not constructible and `fallback="off"`; exits zero when `fallback="deterministic"` or the provider is constructible.
- No raw practitioner/patient UUIDs required in the prompt for the happy path (names resolve).
- Existing tests for disabled/fake/mocked-live, autonomous-language-as-warning, summary PHI redaction, and the no-mutation source assertions still pass.

## Risks / Ambiguities

- The "after 3" time constraint is dropped by the deterministic fallback (`TIME_RE` only matches HH:MM); the booking simply is not pre-narrowed to after 15:00. Acceptable and safe (staff still confirm). Optionally add a bounded natural-time parser ("after 3", "3 pm", "3.45", "before 4") that emits HH:MM, gated as a separate optional step since `normalizer._parse_time` BLOCKS on non-ISO input.
- Fallback could mask a real outage; mitigated by the explicit metadata mode, the `live_interpreter_unavailable` flag, and the readiness release-check so the outage is loud, not silent.
- Audit: must ensure the fallback path does not write a misleading `allowed` `AccessAiAuditLog`; only the bounded denial/unavailable event (if any) should persist. Tests assert audit counts.
- Metadata Literal change is additive; confirm no consumer pins `mode` to the old three values.
- Migration rationale: none required; no model/column/table change, purely a settings flag plus an additive schema Literal.
- Dissent option for Codex: a readiness-contract-only design (no auto-fallback; surface a clear actionable block plus a readiness gate) is safer against silent degradation but does NOT satisfy the merge criterion "simple prompt path pass" when live is down. Recommendation: fallback default ON with loud signalling; expose `fallback="off"` for sites that require strict live-only.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
