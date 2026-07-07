# Bernie Prompt-Thread Fake-Provider Backend Pass

Date: 2026-07-07

## Position

This packet records the narrow non-intercepted fake-provider backend pass that
follows the authored Bernie/Diary prompt-thread fixture tranche readiness packet.

The evidence is still fake-provider, route-level backend evidence. It is not
live-provider evidence and does not prove model quality.

## Gate Checks

Before the backend pass, the readiness check returned:

```json
{
  "runtime_or_provider_wiring_ready": false,
  "raw_trove_access_ready": false,
  "runtime_gate_decision": "blocked",
  "runtime_gate_pause_required": false,
  "sprint_engine_state": "continuing"
}
```

The provider-boundary report returned:

```json
{
  "default_provider": "disabled",
  "runtime_or_provider_wiring_ready": false,
  "live_provider_enabled": false,
  "provider_calls_performed": false,
  "route_behavior_changed": false,
  "database_access_performed": false,
  "memory_or_rag_access_performed": false,
  "historical_diary_material_access_performed": false
}
```

These are the required blocked/false values for this pass. No provider,
runtime, memory, H15/H-series, historical diary, GraphQL, or model-write gate
changed.

Proposal-surface guard citation:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`
- `default_provider=disabled`
- `live_provider_enabled=false`
- `provider_calls_performed=false`
- `route_behavior_changed=false`
- `database_access_performed=false`
- `memory_or_rag_access_performed=false`
- `historical_diary_material_access_performed=false`

## Backend Pass

The replay harness posts each executable scenario turn to the real FastAPI test
client endpoint:

`POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction`

For interpret turns, the harness configures:

- `settings.bernie_booking_interpreter_provider = "fake"`;
- a monkeypatch guard that raises if `app.services.ai.service._get_default_provider`
  is called; and
- row-count checks for `Appointment` and `AppointmentAuditLog`.

This means the pass exercises the backend route and resolver stack with the
deterministic fake interpreter, while failing closed on accidental live-provider
construction or unexpected appointment/audit writes.

## Verification

Commands run:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
git diff --check
```

Results:

- readiness check stayed blocked/false and `sprint_engine_state=continuing`;
- provider-boundary report stayed disabled/false with no route/provider/DB/
  memory/trove changes;
- scenario replay passed as `.x..........................`;
- fixture integrity passed as `8 passed, 1 skipped`;
- `git diff --check` passed.

## Conclusion

The authored prompt-thread corpus is now covered by a narrow fake-provider
backend pass. The next sprint should either:

- add a small report/guard that prevents future closeouts from mislabelling this
  evidence as live-provider evidence; or
- choose the next bounded backend-readiness step while keeping all closed gates
  blocked/false.

Do not proceed to live provider, provider dry-run, runtime memory, H15/H-series,
historical diary, GraphQL mutation, or model-to-database-write work without a
separate reviewed gate change.
