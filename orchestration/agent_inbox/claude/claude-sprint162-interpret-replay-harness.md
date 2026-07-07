# Claude Sprint 162 - Interpret Replay Harness Advice

## Mission

Advise Sprint 162 implementation after Fable's sequencing recommendation:
extend the existing Bernie scenario replay harness with an `interpret` action
instead of creating a new harness.

## Claude CLI Invocation

Claude was consulted via:

```powershell
claude --model sonnet --effort medium --permission-mode acceptEdits -p "<Sprint 162 implementation advice prompt>"
```

## Accepted Advice

- Add `interpret` to the existing executable scenario action set.
- Post interpret turns to
  `/api/v1/appointments/proposals/bernie/interpret-booking-instruction`.
- Force `settings.bernie_booking_interpreter_provider = "fake"` in scenario
  replay.
- Thread `requested_appointment` frames from one interpret turn into the next
  when `context_frames` is omitted.
- Let fixtures use `context_frames: []` to force a fresh turn.
- Reuse the existing `tests/bernie_scenarios` loader/replay machinery.
- Add natural-phrasing fixtures covering clarification, change requests,
  selected-slot pivot, confirm-required boundary, and no-write assertions.
- Keep all evidence labelled `fake-provider, route-level`, not live-provider or
  provider-quality evidence.

## Boundary

No runtime provider wiring, provider dry-run wiring, memory/RAG/GraphRAG,
H15/H-series runtime imports, broad trove processing, GraphQL mutation, or
model-to-database writes were proposed or accepted.

