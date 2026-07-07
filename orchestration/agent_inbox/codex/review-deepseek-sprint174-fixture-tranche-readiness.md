# Sprint 174 DeepSeek Review — Authored Prompt-Thread Fixture Tranche Readiness

**Reviewer:** DeepSeek Flash adversarial lane  
**Date:** 2026-07-07  
**Verdict:** Ready for narrow non-intercepted fake-provider backend pass — with documented gaps and a pause condition.

## Scope Reviewed

- `tests/fixtures/bernie_scenarios/interpret_*.yaml` (25 authored synthetic fixtures)
- `tests/fixtures/bernie_scenarios/README.md`
- `tests/bernie_scenarios/replay.py`, `loader.py`, `README.md`, `test_scenario_replay.py`
- `tests/fixtures/bernie_interpretation_harness/*.json` (5 fixture files, 44 cases)
- `orchestration/sprint_closeout.md` (Sprint 162–173 entries)
- `orchestration/bernie_release_gates.md`
- `orchestration/agent_inbox/codex/review-deepseek-sprint162-*.md` through `review-deepseek-sprint171-*.md`
- `AGENTS.md` (baton state)

## 1. Covered Behaviours

All 25 `interpret_*` fixtures pass against the deterministic fake-provider replay harness. Verified behaviour groups:

| Group | Fixtures | Status |
|---|---|---|
| Full natural language resolution | `interpret_full_request_names` | ✅ |
| Confirm-required no-write boundary | `interpret_confirm_required_boundary` | ✅ |
| Unknown patient without invented ID | `interpret_unknown_patient_name_without_id` | ✅ |
| Interpret → search → select pivot | `interpret_search_select_pivot` | ✅ |
| Empty instruction fail-closed | `interpret_empty_instruction_fail_closed` | ✅ |
| Absolute past-date blocked | `interpret_absolute_past_date_blocked` | ✅ |
| Visible diary date context | `interpret_visible_diary_date_context` | ✅ |
| Clarification practitioner merge | `interpret_clarification_practitioner_merge` | ✅ |
| Field override (date/time/duration) | `interpret_change_*_new_reply_wins` (3 fixtures) | ✅ |
| Context date precedence hierachy | `interpret_context_date_precedence_*` (2 fixtures) | ✅ |
| Context date missing fallback | `interpret_context_date_missing_no_context` | ✅ |
| Context auto-thread vs explicit reset | `interpret_context_frames_auto_thread_vs_empty` | ✅ |
| Multi-frame source reset | `interpret_context_multi_frame_source_reset` | ✅ |
| Practitioner change/override | `interpret_context_practitioner_*` (2 fixtures) | ✅ |
| Reset: patient+date, no practitioner inherit | `interpret_context_reset_patient_date_no_practitioner` | ✅ |
| Temporal drift follow-up | `interpret_context_temporal_drift_followup` | ✅ |
| Temporal drift reset no-merge | `interpret_context_temporal_drift_reset_no_merge` | ✅ |
| Explicit requested_appointment frame | `interpret_explicit_requested_appointment_frame` | ✅ |
| Multi-field missing no context | `interpret_multi_field_missing_no_context` | ✅ |
| No prior frame no merge | `interpret_no_prior_frame_no_merge` | ✅ |
| Reference date drift | `interpret_turn_reference_date_drift` | ✅ |

## 2. Remaining Fixture-Only Gaps (Non-Blocking)

These are residual Sprint 171 DeepSeek recommendations not yet converted:

| # | Gap | Original | Risk | Current Status |
|---|---|---|---|---|
| 1 | Explicit `requested_appointment` frame → ✅ resolved by Sprint 172 | Sprint 171 #1 | — | Closed |
| 2 | `context_frames: []` against multi-frame context → ✅ resolved by Sprint 173 | Sprint 171 #2 | — | Closed |
| 3 | `interpret_no_prior_frame_no_merge` still single-turn (description tightened, not extended) | Sprint 171 #3 | Low — first-turn context:[] coverage is adequate via `interpret_multi_field_missing_no_context` | Open |
| 4 | No fixture tests `context_frames: []` across different/earlier reference dates | Sprint 171 #4 | Medium — runtime could silently merge stale context across session reloads | Open |
| 5 | Default `duration_minutes: 15` untested in reset scenario | Sprint 171 #5 | Low — covered implicitly by adjacent fixtures | Open |
| 6 | Non-interpret actions silently ignore `context_frames` | Sprint 171 #6 | Very Low — optional harness_demo_* candidate | Open |

## 3. Prerequisites for Non-Intercepted Fake-Provider Backend Pass

A *narrow* backend pass (i.e. hitting the real interpret endpoint with the fake provider configured, not intercepting routes) is feasible now because:

1. **Harness already calls the real endpoint:** `replay.py` POSTs to `/api/v1/appointments/proposals/bernie/interpret-booking-instruction` with `settings.bernie_booking_interpreter_provider = "fake"` enforced via `monkeypatch`.
2. **No-Live-Provider guard is built in:** `_install_forbidden_ai_provider_guard` prevents any accidental provider call during replay.
3. **Readiness stack reports blocked:** H55's `bernie_interpretation_readiness_check.py` correctly reports `runtime_or_provider_wiring_ready=false`, `raw_trove_access_ready=false`, `runtime_gate_decision=blocked`.
4. **Release gates require readiness check before any provider wiring:** `bernie_release_gates.md` mandates the readiness command before runtime route wiring, provider wiring, memory, or trove access.

### Must-Stay-False Conditions

Before any sprint proposes a non-intercepted fake-provider backend pass, verify these remain false:

| Condition | Source | Current Value |
|---|---|---|
| `runtime_or_provider_wiring_ready` | H55 readiness check | `false` |
| `raw_trove_access_ready` | H55 readiness check | `false` |
| `runtime_gate_decision` | H53 gate JSON | `blocked` |
| `default_provider` | provider-boundary report | `disabled` |
| `live_provider_enabled` | provider-boundary report | `false` |
| `provider_calls_performed` | provider-boundary report | `false` |
| `route_behavior_changed` | provider-boundary report | `false` |

### Gap That a Backend Pass Would Uncover

A non-intercepted pass — where tests hit the actual endpoint without route-level monkeypatching the provider (just the fake provider config) — would exercise:
- Request validation and deserialization paths
- JSON serialization of the interpret response
- Actual endpoint routing (not Pytest test client stubs)
- Schema migration compatibility (if the endpoint has evolved)

However, the existing pytest client test already covers all of these. A true backend pass would need to run against a deployed or containerized instance, which would require:
- A running backend
- Database availability
- Practitioner/patient/schedule seeding

## 4. Pause Conditions

The sprint engine must pause for explicit review if any of these change during the backend pass:

1. **Readiness values drift:** `runtime_or_provider_wiring_ready` becomes `true`, `runtime_gate_decision` becomes anything other than `blocked`, or `raw_trove_access_ready` becomes `true`.
2. **Provider boundary report changes:** `default_provider` changes from `disabled`, or `provider_calls_performed` becomes `true`.
3. **A backend pass attempts live-provider routing** instead of staying with the `fake` provider.
4. **Memory/RAG/GraphRAG, H15/H-series runtime imports, or historical diary material access** are proposed as part of a backend pass.
5. **The Sprint 171 gaps #3–6** are proposed as sprint-scope blockers rather than tracked-but-deferred items.

## 5. Verdict

**READY — with documented gaps.**

The authored Bernie prompt-thread fixture tranche (25 `interpret_*` YAML fixtures + 44 interpretation harness cases across 5 fixture files) is broadly ready for a narrow non-intercepted fake-provider backend pass. The 3 remaining fixture-only gaps (#3, #4, #5) are non-blocking; they are test-coverage additions, not correctness defects.

The backend pass must:
- Stay provider-free (fake provider only, guarded by existing monkeypatch)
- Stay runtime-gate-blocked (no memory/RAG/GraphRAG, no historical diary material, no H15/H-series runtime imports)
- Pass the readiness command before being proposed
- Be explicitly labeled as "fake-provider, route-level" evidence — not live-backend or live-provider

No pause is required unless the above conditions change. The sprint engine can continue normally.

## Changed Files

This review artifact only — `orchestration/agent_inbox/codex/review-deepseek-sprint174-fixture-tranche-readiness.md`
