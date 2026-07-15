# LC4R10 Sol Acceptance

## Decision

**DECISION: pass**

GPT Sol accepts the LC4R10 recovered implementation at reviewed source head
`01d7ac1882e92e5f461f6e333515a24d80e40bde`. LC4R10 closes the frozen 53
clarification and 40 replay contract populations without parser remediation.

## Accepted contract and evidence

- clarification: 53, `9496e23c6f339603`;
- replay: 40, `defe4c59877753e9`;
- combined disjoint population: 93, `d8d138cb267b4304`;
- complete composed contract: 93/93 pass;
- semantic counts: `880/814/672/154/330/835`;
- safety: 1,152/1,152 and 2,304/2,304 over two repeats;
- deterministic variance: zero over 2,304 samples;
- corpus hash:
  `sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195`;
- focused recovery tests: 20/20;
- focused scale/entity gate: 21/21 including the LC4R10 suite;
- source generator and report check: pass with byte-for-byte regeneration;
- exact changed scenario population: 93/93, with no unexpected or missing
  scenario change.

`expected_outcome_kind` is required but nullable. Explicit null outcomes are
deterministically delta-free. The 53 resolved dialogues use authored
create/move/resize/cancel templates, while the 40 replay cases implement the
contracted reversal, candidate-selection, T1-backed valid create, and
fail-closed policies. The scaled evaluator now losslessly preserves
`action_negated` across repeat reconstruction.

## Worker and recovery decision

DeepSeek V4 Flash/high ran once through Claude Code `--bare`. Its self-certified
pass disclosed only 22/93 complete scorer passes and 37/93 outcome matches,
rewrote every group, and broadened `_01` behavior beyond the frozen selection.
This was a conceptual taxonomy failure. Sol correctly opened no Flash
correction loop, preserved the worker artifact, and invoked the recovery lease.
Every accepted amendment is recorded in
`lc4r10-sol-recovery-amendment.md`.

## Independent veto

Gemini 3.5 Flash/medium ran through a fresh Antigravity project bound to exact
head `01d7ac1882e92e5f461f6e333515a24d80e40bde`. It independently reran the
LC4R10 checker and focused tests, reviewed schema nullability, selection
isolation, replay policy, expected-field isolation, negation preservation,
semantic/safety/variance evidence, recovery provenance, and protected
boundaries. It returned `DECISION: pass` without moving the reviewed head.

Gemini's prose counted 26 historical supersession nodes. Sol did not spend a
second provider loop correcting that mechanical statement. A direct safe
development-only run of the six implicated modules enumerated exactly 22
failures:

- three earlier committed-report equality nodes;
- five LC4R7 queue/report nodes;
- three LC4R8 intermediate-contract nodes; and
- eleven LC4R9 intermediate-contract nodes.

The corrected count matches the Sol serial gate's deselection list. The
reviewer's exact-head product findings and pass decision remain valid; the
original discrepancy is preserved in the review artifact.

## Serial preservation gate

The final explicit serial development gate covered 15 safe modules: scenario
schema, semantic extraction, candidate generation, both composed evaluators,
LC4 scale and scaled evaluation, LC4R3, LC4R7-LC4R10, and T3.1-T3.4 shadow
corpus/runner/live-gate scaffolding. It completed with **831 passes** after
narrowly deselecting the 22 historical equality/queue nodes listed above.
Those nodes intentionally assert immutable pre-reconciliation reports or
intermediate blocker populations; no historical report was regenerated.

## Boundaries and next decision

Protected holdout v1 was not opened, enumerated, searched, imported, run,
regenerated, evaluated, hash-checked, inferred from, or reused. Historical
diary material was not inspected. No parser/extraction change, T3.5 provider,
route/API, database, UI, deployment, release, memory, confirmation, or
live/write authority was opened. T3.1-T3.4 remain intact and blocked by
default; `check_in` remains planned-not-implemented.

With development-corpus reconciliation complete and no independently supported
parser gap remaining, the next step is now the documented user decision
boundary: approve either a new holdout version or an explicit holdout-v1 reuse
policy before LC5 certification work. T3.5 remains a separate deferred gate.
