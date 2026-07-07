# Sprint 160 - Bernie/Diary Review Readiness

## Verdict

Pause after Sprint 160 for Yuri to run a meaningful hands-on Diary/Bernie
review, provided the verification commands below pass. The useful review target
is the supervised receptionist workflow and staff-facing copy, not live-provider
or production-readiness proof.

## Why This Is Worth Reviewing Now

The recent API-spine sprints closed the last known confirm-client idempotency
header gap across ordinary create-confirm, ordinary update-confirm, and the
Bernie tool-intent update-confirm path. That means Yuri can now review the
Bernie/Diary interaction loop with the main staff-confirmed write paths aligned
to the current command/idempotency pattern.

This is still a supervised proposal-and-confirm workflow:

- the exact standing release-gate prompt is
  `Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45`;
- candidate selection and confirmation must remain visibly staff-controlled;
- route-intercepted checks are useful deterministic coverage, but are not live
  backend or live provider evidence;
- live-provider evidence is not claimed unless provider metadata proves
  `live_provider: true`.

## Gate Evidence To Run

Run the standing interpretation readiness gate before treating this as review
ready:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
```

Expected current values:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`

Run the provider-boundary readiness report before making any
live-provider, provider prompt wiring, or provider dry-run wiring claim:

```powershell
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

Expected current values:

- `default_provider=disabled`
- `runtime_or_provider_wiring_ready=false`
- `live_provider_enabled=false`
- `provider_calls_performed=false`
- `route_behavior_changed=false`
- `database_access_performed=false`
- `memory_or_rag_access_performed=false`
- `historical_diary_material_access_performed=false`

Run the deterministic fake-provider interpreter check for the ordinary prompt:

```powershell
.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py --instruction "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45" --reference-date 2026-07-01 --expect-result clarification_required --expect-earliest-time 14:00 --expect-latest-time 15:45 --expect-mode mocked
```

This fake-provider script proves the ordinary names-only phrase parses the time
window honestly and with redacted compact output. It does not prove deterministic
patient or practitioner ID resolution from names alone.

Run the route-intercepted Diary check for the same review loop:

```powershell
.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_bernie_route_intercepted_selected_slot_can_return_to_candidates -q
```

This check is explicitly `route-intercepted`. It proves that the browser flow can
render candidates, stage a selected booking, return to the candidate list, stage
a different slot, and avoid raw practitioner/internal error copy in the
deterministic harness. It does not prove live backend or live provider behavior.

## What Yuri Should Look For

During hands-on Diary review, focus on whether the workflow feels like a
competent receptionist assistant:

- Bernie understands the ordinary appointment request well enough to parse the
  requested time window and, in the Diary review flow, show useful candidate
  times once deterministic review context is present.
- The panel clearly distinguishes proposed/staged booking state from a completed
  booking.
- Staff can change the selected time before confirming.
- Confirmation copy is calm, specific, and does not surface raw IDs,
  `snake_case` internals, or generic `Not Found` failures.
- Any uncertainty asks for staff clarification instead of guessing.

## Still Closed

This review does not open:

- runtime route wiring from the provider-free interpretation harness;
- provider prompt wiring or provider dry-run wiring;
- live-provider enablement;
- memory/RAG/GraphRAG use;
- H15/H-series runtime imports;
- historical diary material access or broad trove processing;
- GraphQL mutations or model-to-database writes.

## After Yuri's Review

If the review feels good, the next implementation strategy is to keep moving
from deterministic, staff-confirmed appointment proposals toward narrower live
backend/provider evidence. If Yuri sees workflow friction, fix that before
opening live-provider or memory gates.
