# Reception One Receptionist-first v6.2 Provider-free Sol Acceptance

Status: accepted for the separately gated occupied cohort
Recorded: 2026-07-30

## Decision

The provider-free v6.2 desk-context tranche passes its frozen acceptance
contract. It may advance to a revision-bound read-only cloud preflight and, if
that preflight passes, the authorised Sydney Vertex cohort.

This acceptance does not itself authorise product provider wiring, real data,
database reads, appointment writes, confirmation, deployment or release.

## Evidence

- all twenty-four original v6 authored-synthetic request frames are present,
  including all nine v6.0 passes;
- every desk context validates, includes only the selected appointment and at
  most two grounded mentions, and excludes the rest of the Diary;
- `b-move-shift` receives a readable, request-local and binding-linked Margaret
  appointment;
- the model task and desk context are canonically hashed and independently
  recomputed by the broker and proofreader;
- missing, changed or authority-expanded context fails closed;
- all twenty-four deterministic reference forms are admitted;
- the fourteen reconstructable historical v6 wrong forms remain rejected by
  the unchanged v6.1 recognized-intent assertion;
- the two-turn real-isolation rehearsal rejected the deliberately wrong first
  form and admitted the corrected replacement against the same context packet;
- both cells were non-root, read-only, network-none, mount-free,
  credential-free and residue-free; and
- the product provider boundary remains disabled with no database, memory,
  RAG, historical Diary or route behaviour change.

Primary artifacts:

- `scripts/reception_one_receptionist_first_v62.py`
- `scripts/reception_one_receptionist_first_v62_cohort.py`
- `scripts/reception_one_receptionist_first_v62_cell.py`
- `scripts/reception_one_receptionist_first_v62_isolation.py`
- `orchestration/continuity/reception-one-receptionist-first-v62/desk-context.schema.json`
- `orchestration/continuity/reception-one-receptionist-first-v62/turn-input.schema.json`
- `orchestration/continuity/reception-one-receptionist-first-v62/provider-blocked-evidence.json`
- `orchestration/continuity/reception-one-receptionist-first-v62/real-isolation-evidence.json`
- `tests/test_reception_one_receptionist_first_v62.py`

## Verification

- 233 focused and relevant regression/API Spine/Ariadne tests passed;
- both repository readiness reports passed with
  `runtime_or_provider_wiring_ready=false`, `default_provider=disabled`,
  `live_provider_enabled=false`, `provider_calls_performed=false`, no database
  access, no memory/RAG access and no historical Diary access;
- JSON/schema parsing and Python compilation passed;
- real-isolation cleanup independently reported no owned containers, images or
  temporary context; and
- no provider call or credential read occurred during provider-free
  acceptance.

## Occupied boundary

The occupied cohort remains exactly bound to `gemini-2.5-flash`, project
`bernie-emr4-dev`, the exact Bernie impersonated service account, keyless ADC,
`australia-southeast1` and
`australia-southeast1-aiplatform.googleapis.com`. It includes twenty-four
primary calls and at most one terminal second call per case, never more than
forty-eight calls or USD 1. No prompt, schema, proofreader or generation-setting
change is permitted once the cohort starts.

Continuity and Compass must now advance together, bind the provider-free
acceptance, render and validate before the first occupied call.

## Claim limit

This proves a bounded provider-free desk-context and proofreader symmetry over
the reused authored-synthetic development cohort. It does not prove model
generalisation, production fitness, Australian physical or sovereign
processing, or safety for product-derived, patient, health, clinical,
protected or historical data.
