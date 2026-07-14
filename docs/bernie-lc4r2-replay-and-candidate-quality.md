# LC4R2 — Replay Consequences and Candidate-Quality Firewall

Date: 2026-07-14

Final disposition: accepted as a safety-first diagnostic closeout by GPT Sol
after independent Gemini 3.5 Flash review.

## Oracle-free replay consequences

`deterministic_replay()` now derives outcomes, tool use, appointment/audit
deltas, and simulated-write metadata only from:

- `InterpretationObservation`;
- explicit synthetic diary state and reference date; and
- bounded action/outcome policy.

It does not read or branch on expected outcome, tool, appointment delta, audit
delta, clarification, provenance, or adjudication fields. The scorer remains
the only layer that compares observations with the Silver candidate contract.

All six actions have action-specific outcomes and mutation shapes:

| Action/state | Outcome | Appointment change type |
|---|---|---|
| create / empty | `appointment_created` | `created` |
| create / exact duplicate | `existing_booking_found` | prior `created` evidence only |
| create / overlap | `candidate_selection_required` | none |
| move | `appointment_moved` | `moved` |
| resize | `appointment_resized` | `resized` |
| cancel | `appointment_cancelled` | `cancelled` |
| status change | `appointment_status_changed` | `status_changed` |
| explain schedule | `schedule_explained` | none |
| clarification | `clarification_required` | none |
| unsafe/refused | `instruction_refused` | none |

Terminal, stale, concurrent, no-slot, roster-absent, break, and elapsed-window
states fail closed where the synthetic contract cannot establish safe
execution. Explicit negation/reversal produces no mutation outcome or delta.
`is_simulated_confirmed_write` is evaluation metadata derived from replayed
deltas, never from an expected delta, and performs no real write.

## Candidate-quality firewall

The development-only audit runs over the same 1,152 Silver/pending scale
records used for current metrics, with two deterministic repeats. It separates:

- `aligned_pass`;
- `aligned_failure`;
- `surface_contract_conflict`; and
- `unsupported_or_ambiguous_surface`.

Current two-repeat classification is:

| Category | Samples |
|---|---:|
| aligned pass | 0 |
| aligned failure | 1,180 |
| surface-contract conflict | 1,072 |
| unsupported/ambiguous | 52 |

These are discovery categories, not Gold adjudication. Silver conflicts do not
reduce Gold coverage gaps. A separate LC2 reference audit remains labelled as
15 candidates / 30 samples and is not used to explain the scale partition.

Rule counts are uncapped aggregates, while safe examples are independently
capped. Dimension attribution reports passed/failed totals and partitions each
failure into conflict, unsupported, or aligned buckets. Repeat variance is
measured from observation/safety fingerprints rather than asserted.

## Development evidence

One-repeat metrics against the accepted LC4R1 base are:

| Dimension | LC4R1 | LC4R2 | Delta |
|---|---:|---:|---:|
| downstream outcome | 50/1,152 | 197/1,152 | +147 |
| interpretation tools | 592/1,152 | 592/1,152 | 0 |
| replay tools | 592/1,152 | 592/1,152 | 0 |
| clarification | 610/1,152 | 610/1,152 | 0 |
| authority | 642/1,152 | 642/1,152 | 0 |
| appointment deltas | 212/1,152 | 209/1,152 | -3 |
| audit deltas | 192/1,152 | 192/1,152 | 0 |
| safety | 1,152/1,152 | 1,152/1,152 | 0 |

Every semantic-field pass count is unchanged from LC4R1:

- intended action: 720;
- action semantics: 674;
- temporal relation: 628;
- normalized values: 101;
- entity semantics: 255; and
- clarification: 642.

The only lost appointment-delta passes are
`lc4_dw1_dev_mt_001_03`, `lc4_dw1_dev_mt_002_03`, and
`lc4_dw1_dev_mt_013_03`. Each has empty seeded appointment state and ends with
“never mind / not needed,” while its Silver label still expects a created
appointment. LC4R1 passed those records only by inventing an earlier write from
date/time text. Removing that heuristic is a fail-closed safety correction, not
a product regression and not permission to hide the remaining aligned gaps.

The deterministic v3 report is
`docs/bernie-lc4r-development-gap-report.json`, with corpus hash
`f73a35b8843beb66` and report hash `cba97acd3f23d2ec`.

## Acceptance history

DeepSeek Flash's original and revised worker artifacts are preserved. Its final
decision remained `revision_required` because the original score-based
conflict-only exception was not met. Sol adopted the branch under the recovery
lease, fixed only a disposable-worktree path in a report test, proved the exact
three safety-correction records, and applied a narrow revised acceptance:

- safety must remain 1,152/1,152;
- repeat variance must measure zero;
- all LC4R1 semantic-field counts must be preserved;
- all six-action and expected-field mutation regressions must pass;
- the report must expose rather than erase aligned/unsupported failures;
- no protected evidence or runtime/write boundary may open; and
- an independent Gemini veto review must pass.

Gemini 3.5 Flash returned `DECISION: pass` at reviewed head `1c41d3b6` and
independently reproduced 49 replay tests, 33 audit tests, the exact LC1 route
regression, report check, eight rehydration tests, 89 composed tests with one
deselection, the blocked shadow gate, and a clean diff.

The frozen pre-LC4R exact-report regeneration check is deliberately not
regenerated in LC4R. It is historical baseline evidence and now drifts because
the evaluator changed. The LC4R2 v3 report is the owned current artifact.

## Boundaries and next step

No protected holdout, provider, route/API, database, UI, deployment, historical
diary, memory/RAG/GraphRAG, T3.5 adapter, or live/write authority was opened.
T3.1-T3.4 remain preserved and blocked by default.

LC4R2 makes replay consequences safer and makes the scale failures honest; it
does not establish broad language completeness. LC4R3 should target a bounded
set of the remaining aligned semantic failures without editing Silver fixtures
to manufacture passes or using protected holdout evidence.
