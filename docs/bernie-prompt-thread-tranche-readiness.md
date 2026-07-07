# Bernie Prompt-Thread Tranche Readiness

Date: 2026-07-07

## Position

This packet closes the authored Bernie/Diary prompt-thread fixture tranche that
started after the Sprint 160 review-readiness pause and followed the Fable
ordering: prove native prompt-thread/context behavior through deterministic
fake-provider replay before moving toward broader runtime or provider evidence.

The tranche sits in Programme 2D Reception Copilot Readiness and Programme 2G
Bernie API Spine review-readiness. It is guardrail hardening, not live-provider
enablement.

## Covered Behaviors

The executable `interpret_*` scenario corpus now covers:

- first-pass full booking instructions and clarification replies;
- empty instruction fail-closed behavior;
- unknown patient names without invented patient IDs;
- visible diary date context;
- selected proposal, selected diary appointment, and visible diary date
  precedence;
- omitted-date fallback when no usable context exists;
- omitted `context_frames` auto-threading through prior requested-appointment
  frames;
- explicit `context_frames: []` reset behavior;
- practitioner override while other fields thread forward;
- patient-only multi-field-missing clarification;
- temporal-drift follow-ups where current-turn relative dates resolve against
  the current turn reference date;
- reset/no-merge follow-ups where restated patient/date do not inherit
  practitioner, time, or duration;
- explicit caller-supplied `requested_appointment` context frames; and
- requested appointments originally derived from multiple diary context frames
  threading on omitted context and clearing on explicit empty context.

## Current Evidence

The current replay evidence is provider-free route-level fake-provider testing:

```powershell
.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q
```

The latest Sprint 173 run passed as:

- scenario replay: `.x..........................`
- integrity: `8 passed, 1 skipped`

The pre-existing xfail remains outside this tranche.

## Gates Still Closed

This tranche does not authorize:

- live provider calls;
- provider prompt or dry-run wiring;
- runtime route wiring from the provider-free interpretation harness;
- memory, RAG, or GraphRAG;
- H15/H-series runtime imports;
- historical diary material access;
- GraphQL mutations; or
- model-to-database writes.

Proposal-surface guard citation:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

Expected closed values:

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

## Remaining Fixture-Only Edges

The following edges are known but not blockers for moving to a narrow
non-intercepted fake-provider backend pass:

- an earlier turn-level `reference_date` reset/reload simulation;
- standalone default-duration contract coverage;
- non-interpret action behavior when extra `context_frames` keys are present.

These can remain future fixture hardening unless the backend pass reveals an
actual route/runtime mismatch.

## Recommended Next Step

Run a narrow non-intercepted fake-provider backend pass against the authored
prompt-thread corpus. The pass should keep the provider setting fake, use no
live provider, perform no appointment/audit writes except where a future
explicit confirmation fixture requires it, and report exact route responses.

Acceptance for that next pass:

- provider metadata remains `provider: fake` and `live_provider: false`;
- no AI provider construction occurs;
- no appointment or audit rows are written by interpret-only cases;
- relative dates continue to resolve from the current turn reference date;
- explicit `context_frames: []` remains a hard reset signal;
- omitted `context_frames` remains the only auto-threading path in the replay
  harness; and
- any divergence is captured as a bounded fixture or route-contract follow-up,
  not patched by opening broader provider/runtime gates.
