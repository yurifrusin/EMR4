# LC4R2 Replay Consequence and Candidate-Quality Firewall — Sprint Contract

Date: 2026-07-14

Active planner, semantic owner, acceptance owner, and protected integrator:
GPT Sol. Planning mode remains `sol_direct_routine`. LC4R2 is the next bounded
development-only sprint after accepted LC4R1 and changes no runtime authority.

Settings fingerprint:
`sha256:0dce975ccb05026a186df59313345590af2552a2364c944606ada9372dc617dd`

## Direction-dialogue disposition

Skipped. LC4R1 established the oracle-free semantic boundary and exposed the
next root problem: replay handles only create/duplicate/overlap consequences,
while Silver/pending surface/label contradictions are mixed with genuine
interpreter failures. DeepSeek V4 Flash/high through Claude Code `--bare` owns
the bounded implementation lane. Sol owns any recovery amendment and final
acceptance. Gemini review is risk-triggered if the candidate changes safety or
simulated-write classification.

## Protected evidence boundary

Use only ordinary LC1-LC4 development fixtures and authored regressions. Do not
read, list in detail, import, load, regenerate, evaluate, hash-check, infer from,
or tune against any protected holdout fixture, support module, seal receipt, or
report. No historical diary material, external dataset, network/provider call,
PHI, memory, RAG, or GraphRAG is permitted.

The 1,152 LC4 development records remain Silver/pending discovery evidence.
They are not parser or replay authority. Contradictory surface/contract pairs
must be classified and reported, not made to pass by copying their expected
outcomes, tools, values, or deltas.

## Baseline

After LC4R1, one-repeat development evidence is:

```text
complete 0/1152
downstream outcome 50/1152
interpretation tools 592/1152
replay tools 592/1152
full clarification 610/1152
authority 642/1152
appointment deltas 212/1152
audit deltas 192/1152
safety 1152/1152
```

## Objective A — Oracle-free replay consequences

Refactor deterministic replay so its outcomes, tools, deltas, and simulated
write classification derive only from:

- the `InterpretationObservation`;
- explicit synthetic current-state inputs (`diary_state`,
  `initial_diary_state`, reference date); and
- bounded action/outcome policy tables.

Replay logic must not read or branch on `expected_outcome_kind`,
`expected_tool_sequence`, `expected_appointment_deltas`,
`expected_audit_deltas`, expected clarification, provenance/adjudication, or
any candidate/holdout label. The scorer may compare the completed observation
to expected fields after replay.

Cover all six current diary actions with action-specific consequences:

- create: exact duplicate -> `existing_booking_found`; overlap ->
  `candidate_selection_required`; safe creatable state ->
  `appointment_created`;
- move -> `appointment_moved`;
- resize -> `appointment_resized`;
- cancel -> `appointment_cancelled`;
- status change -> `appointment_status_changed`;
- explain -> `schedule_explained`.

Clarification remains `clarification_required`; unsafe positive demands remain
`instruction_refused`; an explicitly negated/reversed action must not produce a
mutation outcome or mutation delta. States where the current synthetic contract
does not establish safe action execution must fail closed rather than copying a
Silver expected success.

Replay tool sequences must be derived from the interpretation's action-specific
selection and must not introduce a tool absent from that selection. Delta
builders must use observed normalized values/entity resolution plus bounded
synthetic IDs. Create/move/resize/cancel/status-change deltas and audit events
must have distinct change types; explain/clarify/refuse/negation produce no new
mutation delta unless an authored stateful regression independently establishes
an earlier completed turn.

`is_simulated_confirmed_write` is evaluation metadata only. It must derive from
the observed bounded replay action/deltas and never from the presence of an
expected delta. No actual route, database, appointment, or audit write occurs.

## Objective B — Candidate-quality firewall and gap report

Add a deterministic development-only audit that separates at least:

- `aligned_failure`: surface evidence supports the candidate contract and the
  interpreter/replay still disagrees;
- `surface_contract_conflict`: explicit action, temporal operator, point/bound,
  duration, correction, or negation evidence contradicts the Silver label;
- `unsupported_or_ambiguous_surface`: the bounded parser cannot establish which
  side is correct; and
- `aligned_pass`.

The audit may use the scenario only as the candidate contract being audited;
it must never feed a label back into interpretation or replay. Every conflict
record must carry a deterministic rule ID and only bounded development case IDs
and safe authored-synthetic excerpts/evidence. Aggregate counts must be stable
under shuffled input. Silver/pending conflicts remain discovery evidence and do
not reduce adjudicated coverage gaps.

Emit a committed machine-readable development report and a concise document.
The report must include baseline/current replay dimensions, category/rule
counts, aligned-subset scores, conflict examples under a fixed cap, corpus/report
hashes, provenance/adjudication counts, and an explicit statement that no
protected holdout was accessed. It must not claim broad language completeness.

## Owned implementation surface

The DeepSeek worker may:

- edit replay helpers in
  `app/services/bernie/composed_corpus_evaluator.py`;
- add one development-only audit module under `app/services/bernie/`;
- add one report script under `scripts/`;
- add focused authored tests and a development report fixture/artifact under
  `docs/`; and
- add one implementation note and one completion artifact.

It must not edit the LC4 scale generator/fixtures, protected-holdout code,
scenario schema, runtime interpreter/provider, routes, API/OpenAPI/GraphQL,
database/migrations, UI, deployment, T3 gates, AGENTS.md, or LC4R1 artifacts.

## Required tests

Tests must prove:

- each action maps to the correct outcome/tool/delta/audit shape without any
  expected-field read;
- clarify, refuse, negated, duplicate, overlap, and safe create cases;
- changing every expected field while holding utterances/state fixed cannot
  change interpretation or replay observations;
- simulated-write classification is unchanged when expected deltas are removed
  or mutated;
- stateful refusal never creates a second delta;
- conflict rules detect explicit operator/value/action contradictions, do not
  mislabel aligned cases, and are deterministic under shuffled input;
- the report is development-only, bounded, hash-stable, and preserves candidate
  versus adjudicated evidence separation; and
- no authority/write/provider/holdout boundary opens.

## Acceptance

Sol will rerun authored tests, the LC1 route regression, LC3/LC4 composed gates,
the report check, T1/T2/T3.1-T3.4 gates proportionate to touched surfaces, the
blocked shadow gate, and `git diff --check`.

Acceptance requires:

- 1,152/1,152 development safety passes and zero repeat variance;
- no decrease from the LC4R1 semantic field counts;
- strict improvement in downstream outcome, replay tools, appointment deltas,
  and audit deltas on the full development partition, or an evidence-backed
  explanation that a dimension is capped solely by reported candidate
  conflicts while all aligned authored regressions pass;
- every aligned authored replay regression passing;
- no expected-answer echo or expected-delta-derived simulated authority;
- a deterministic candidate-quality report that keeps Silver/pending conflicts
  separate from Gold/adjudicated gaps; and
- no holdout/provider/route/DB/UI/write/T3.5 change.

Pause only for an explicit user stop or a documented sealed-holdout,
historical-data, external-provider/data, material licence/cost, API/route,
database, confirmation/write, deployment, or release boundary.

Sprint engine state: continuing.
