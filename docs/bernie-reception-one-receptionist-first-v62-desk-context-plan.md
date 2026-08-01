# Reception One Receptionist-first v6.2 Desk Context

Status: complete; occupied evaluation failed closed at 21/24 exact outcomes
Recorded: 2026-07-30

## Purpose

v6.2 is a separately versioned development descendant of the accepted v6.1
targeted repair. It does not revise or rescore v6 or v6.1.

The v6.1 request gave the deterministic parser and proofreader the complete
authored-synthetic frame, while the model saw the utterance and an opaque
`binding:selected_appointment` row. It did not receive a readable account of
the selected appointment, current Diary focus, context freshness or the role of
earlier utterances. v6.2 removes that asymmetry without sending the whole Diary.

## Typed desk context

The broker constructs one deterministic `desk_context` inside the hashed model
task. It contains only:

- the current authored-synthetic Diary reference date and practice scope;
- up to four ordered recent reception-staff utterances;
- the one staff-selected appointment, when present, with its request-local
  patient and practitioner display labels, date, time, duration and status;
- the request-local grounded patient and practitioner mentions;
- context revision, observation time and expiry;
- explicit source and authority labels; and
- the resolution precedence and context-only/no-command boundary.

The context is typed, minimal, source-labelled, freshness-bound and
non-authoritative. It excludes the rest of the practice Diary, unrelated
appointments, raw database results, historical diary material, patient or
clinical history, memory, RAG and GraphRAG.

The complete task, including `desk_context`, is canonically hashed. The broker
validates it before the provider request. The proofreader receives the same
frozen turn input, recomputes the desk context from the same frame, and requires
the model-side and proofreader-side task and context hashes to match before any
typed value can be admitted.

## Reference resolution

The receptionist instruction uses this precedence:

1. the latest explicit staff instruction;
2. the bounded correction ticket, if this is the terminal correction turn;
3. earlier utterances in the same bounded dialogue;
4. the staff-selected Diary context; and
5. clarification only when the reference remains unresolved.

Explicit create language is not converted into a move merely because an
appointment is selected. Conversely, a move, resize, cancellation or status
instruction may use the matching selected appointment without asking the staff
to repeat already supplied context.

The model still fills only the closed typed form. Readable desk-context values
are not copied into executable fields; the form continues to use request-local
binding codes and earlier typed outputs. Natural receptionist speech remains a
separate audit channel and is never parsed into the form.

## Full regression cohort

At Yuri's direction, v6.2 evaluates all twenty-four frozen v6
authored-synthetic request cases, including the nine that passed v6.0. This is a
development regression cohort, not a fresh holdout.

Each case receives:

- one primary call; and
- at most one terminal second call, used either for the existing closed
  proofreader correction ticket or an exact same-request replay after a
  pre-schema no-candidate result.

The absolute occupied ceiling is forty-eight calls and USD 1. Each call uses a
distinct one-use ledger. A case stops after the first exact admitted result or
its terminal second result. No prompt, task schema, output schema, generation
setting or proofreader change is permitted after the occupied cohort starts.

## Frozen provider boundary

- provider/model: Google Cloud Vertex AI `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: keyless impersonated ADC only;
- location: `australia-southeast1`;
- hostname: `australia-southeast1-aiplatform.googleapis.com`;
- data: authored-synthetic only;
- temperature: `0`;
- thinking budget: `1024`;
- hidden thought content excluded;
- no API key, service-account key, global endpoint or fallback;
- no tools, function calling, grounding, retrieval or cache creation;
- no product/database access, real data, confirmation, write, delivery,
  deployment or release.

The repository readiness checks remain:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

They are expected to report
`runtime_or_provider_wiring_ready=false`, `raw_trove_access_ready=false`,
`runtime_gate_decision=blocked`, `default_provider=disabled`,
`live_provider_enabled=false`, `provider_calls_performed=false`,
`route_behavior_changed=false`, `database_access_performed=false`,
`memory_or_rag_access_performed=false`, and
`historical_diary_material_access_performed=false`. The v6.2 occupied
evaluation is a separate one-use rehearsal authority, not product provider
wiring.

## Provider-free acceptance

Before any occupied call:

1. all twenty-four desk contexts validate and contain no unrelated Diary rows;
2. the selected appointment is readable and binding-linked for
   `b-move-shift`;
3. multi-utterance correction context preserves order and current-turn
   precedence;
4. context, task and proofreader hashes match;
5. any context tamper, missing provenance, stale revision, authority expansion
   or model/proofreader mismatch fails closed;
6. all twenty-four deterministic reference forms remain admissible;
7. the fourteen reconstructable v6 semantic misses remain rejected by the v6.1
   assertion;
8. the nine v6.0 passes are covered as explicit non-regression cases;
9. a two-turn provider-free real-isolation rehearsal passes with non-root,
   read-only, network-none, credential-free cells and no residue;
10. focused, repository-only, API Spine, schema, compilation and static checks
    pass; and
11. Continuity and Compass advance together and their rendered report
    validates.

## Occupied acceptance

The occupied result passes only if all twenty-four terminal case dispositions
match their frozen deterministic oracle, every opened ledger is consumed, the
USD 1 and forty-eight-call ceilings are respected, and cleanup and independent
residue checks pass. Otherwise it fails closed and releases no unverified
draft.

## Claim limit

This tranche can compare the complete reused authored-synthetic cohort after a
typed local-context repair through the configured and observed Sydney
locational request path. It cannot prove independent generalisation,
production fitness, Australian physical or sovereign processing, or safety for
real, product-derived, patient, health, clinical, protected or historical data.
