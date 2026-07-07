# Sprint 171 DeepSeek Review — Reset/No-Prior Context Fixture Matrix

**Reviewer:** DeepSeek Flash adversarial lane  
**Date:** 2026-07-07  
**Verdict:** Gaps found — see recommendations below. No blocking issues for Sprint 171.

## Scope Reviewed

- `interpret_context_temporal_drift_followup.yaml`
- `interpret_context_temporal_drift_reset_no_merge.yaml`
- `interpret_context_frames_auto_thread_vs_empty.yaml`
- `interpret_no_prior_frame_no_merge.yaml`
- All adjacent `interpret_*` fixtures in `tests/fixtures/bernie_scenarios/`
- `tests/bernie_scenarios/replay.py` and `tests/bernie_scenarios/loader.py`

## Findings

### 1. No fixture tests explicit `requested_appointment` frames in `context_frames`

All fixtures pass either `[]`, `visible_diary_page`, `selected_diary_appointment`, `selected_proposal`, or omit `context_frames`. There is no fixture that passes a pre-built `requested_appointment` frame as explicit context input. If the receptionist UI ever replays a prior session frame (via template or copy-forward), there is no coverage that the backend accepts and respects it.

**Recommendation:** Add `interpret_explicit_requested_appointment_frame.yaml` — a single-turn fixture that passes a `requested_appointment` frame with `patient_id`, `practitioner_id`, `date_from`, etc. as explicit context and expects `result: interpreted` without needing to repeat those fields in the instruction text.

### 2. No fixture tests `context_frames: []` against multi-frame context

The `interpret_context_frames_auto_thread_vs_empty.yaml` fixture proves that `[]` clears a single prior `requested_appointment` frame. But context can contain multiple frame types (requested_appointment + slot_search + visible_diary_page + selected_proposal). There is no fixture proving that `[]` clears all frame types, not just the first one.

**Recommendation:** Add `interpret_context_reset_multi_frame.yaml`. Turn 1: interpret with `visible_diary_page` + `selected_proposal` context. Turn 2: interpret with `context_frames: []` and a partial instruction. Expect all prior frame-derived fields (patient, practitioner, date) to be null in the second turn.

### 3. `interpret_no_prior_frame_no_merge` is a single-turn fixture

The description says "without a prior frame remains clarification_required instead of inheriting stale context", but the fixture only has one turn. A single `context_frames: []` turn with a partial instruction is covered by `interpret_multi_field_missing_no_context.yaml`. The valuable assertion is missing: that a *subsequent* turn with `context_frames: []` does not inherit stale context from the prior turn. This is already tested by the third turn in `interpret_context_frames_auto_thread_vs_empty.yaml`, but the name and description of `interpret_no_prior_frame_no_merge` overpromises.

**Recommendation:** Either extend the fixture to a second turn (proving the explicit `[]` blocks cross-turn threading), or rename it to clarify it's testing first-turn "no prior frame" only. A two-turn version would prove: turn 1 full instruction with `context_frames: []` → turn 2 bare practitioner instruction with `context_frames: []` → `result: clarification_required` and `date_from: null`.

### 4. No fixture tests `context_frames: []` across different reference dates

All reset-scenario fixtures use the same turn-level reference_date as the fixture-level date or monotonically advance by 1 day. There is no test that `context_frames: []` resets properly when the turn-level reference_date is *earlier* than the fixture-level date (simulating a reload from an older cached session state).

**Recommendation:** Add `interpret_context_reset_with_earlier_reference_date.yaml`. Turn 1 (ref_date=2026-07-08, context_frames: []): full instruction. Turn 2 (ref_date=2026-07-05, context_frames: []): "Book Margaret Thompson next Tuesday at 09:00". Expect date_from from ref_date 2026-07-05 (2026-07-07, not 2026-07-14).

### 5. Missing: `duration_minutes: 15` default contract is untested for reset

In `interpret_context_temporal_drift_reset_no_merge.yaml`, the second turn expects `duration_minutes: 15` when none is specified. This asserts a specific default value. There is no standalone fixture that proves this default is applied consistently when all other fields are null/unknown.

**Recommendation:** Add `interpret_context_default_duration.yaml`. Single-turn interpret with `context_frames: []` and instruction "Book an appointment for tomorrow at 10:00" (no patient/practitioner). Expect `duration_minutes: 15` in the result (or confirm the system default value).

### 6. No fixture proves `context_frames` on non-interpret actions

The loader validates `KNOWN_ACTIONS` only. `normalize`, `search`, `select`, and `confirm` turns silently ignore any `context_frames` in their input. No fixture tests that extra `context_frames` on a `normalize` or `search` turn does not crash, inject, or leak context. This is a test-only gap (production code isn't affected), but it means a future schema change could add context_frames to search actions without a regression guard.

**Recommendation:** (Low priority) Add `harness_demo_search_with_context_frames_ignored.yaml` in the `harness_demo_*` ownership lane that passes `context_frames: [...]` on a search turn and asserts it is silently consumed (no error, no candidate change).

### 7. False-positive surface in `preserved_fields` mechanism

`replay.py` snapshots `preserved_fields` after turn 1 and checks they don't drift in subsequent turns. This detects value *changes* but does not prove the values came from threading rather than from the fake provider independently producing the same output. The actual threading assertion is in the fixture's `expect.fields` (e.g., turn 2 expects `patient_id: "{patient_id}"` without repeating it in the input). The `preserved_fields` guard is a defense-in-depth check that catches unintended drift.

**No recommendation, but Ariadne should be aware** that if the fake provider output ever changes independently (e.g., a new routing path), `preserved_fields` may fail even if threading is correct, requiring a fixture-level update.

## Summary Table

| # | Gap | Fixture | Risk | Action |
|---|---|---|---|---|
| 1 | No explicit `requested_appointment` frame passed | Missing | Medium | Add fixture |
| 2 | `context_frames: []` against multi-frame context untested | Missing | Low | Add fixture |
| 3 | `no_prior_frame_no_merge` single-turn only | Existing | Low | Extend or rename |
| 4 | No earlier reference_date reset test | Missing | Medium | Add fixture |
| 5 | Default duration untested in reset scenario | Missing | Low | Add fixture |
| 6 | Non-interpret context_frames untested | Missing | Very Low | Optional |
| 7 | `preserved_fields` false-positive surface | Existing | Noted | Awareness only |

## Gate Compliance

All recommended fixtures are test-only YAML additions under `tests/fixtures/bernie_scenarios/`. No production code, route wiring, provider calls, database writes, memory/RAG/GraphRAG access, H15/H-series runtime imports, or historical diary material access is required. All fixtures would assert `forbidden_outcomes: [provider_called, appointment_written, audit_written]`.

## Changed Files

This review artifact only — no fixture files were created or modified. Ariadne may implement recommendations in the Sprint 171 fixture batch.
