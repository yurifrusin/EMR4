# Bernie Synthetic Silver All-192 Coherence Audit Closeout

Date: 2026-07-17

Status: `partial_pass_with_quarantine`

## Outcome

The authorized audit evaluated every one of the 192 originally admitted
synthetic receptionist-to-Bernie Silver rows without using product-parser
output to decide admission. The frozen pre-repair result was 85 coherent and
107 invalid rows.

Sol made exactly 12 candidate-text repairs:

- eight resize variants now state explicitly that the instruction is a resize;
  and
- four schedule-anaphora variants refer to a diary request rather than an
  appointment.

Candidate IDs, seed hashes, evidence coordinates, provenance, authority, and
all frozen source semantics remained unchanged. Five repaired rows had no
other defect and became coherent. Seven repaired rows also inherit an oracle
conflict and remain quarantined.

Final current admission is:

- coherent and admitted: 90/192;
- quarantined: 102/192;
- rejected: 0/192.

The original 192-row candidate and admission are preserved as immutable
historical evidence. Current admission is separately bound by
`tests/fixtures/bernie_synthetic_noise/admission_coherent.json`.

## Why 102 rows remain quarantined

Primary final dispositions are:

| Primary decision | Rows |
|---|---:|
| `quarantine_oracle_policy_conflict` | 78 |
| `quarantine_entity_transition_conflict` | 16 |
| `quarantine_replay_contract_conflict` | 8 |

The policy-conflicted rows combine `request_clarification` with no
clarification contract and a successful outcome or mutation delta. The
entity-transition rows withdraw the whole action while their oracle still
expects it to execute. The replay-conflicted rows either pair mutation tools
with no outcome/delta or pair `existing_booking_found` with a creation delta.

These contradictions cannot be cured by rewriting surface dialogue while
preserving the frozen source anchor. They were quarantined rather than hidden
through parser, policy, replay, scorer, or oracle changes.

All 24 clarification-form rows and all 24 reversal-form rows are absent from
current admission. A future balanced corpus therefore requires new coherent
anchors; it cannot simply relabel the quarantined rows.

## Exact evidence

- pre-repair report hash:
  `sha256:616f6180108776991096f4e90d5454a99aa313471fe97591d6d527175b17c79a`;
- final audit report hash:
  `sha256:4e2f3a5dd3632a8d5f927a2d42a203a909673d89d6406ded886eb37bbbfabd80`;
- repaired 192-row candidate hash:
  `sha256:4ac2b4705a49b9f394351ce523808e9c6b06c8cabd9cc2f4b1f6db6b5fe116f8`;
- coherent admission hash:
  `sha256:55b5c968fa066fc0830e9c80781b0ded1e13520b6f206a41fee9dd0e027687cd`;
- accepted-population robustness report hash:
  `sha256:040a661d0b2f14ee1d8e4b15dd151aa9af09fa09960e1984164106a6f6ba58c2`.

The 90 admitted rows ran twice through the unchanged interpreter, replay, and
scorer: 4/90 pass every product dimension, safety is 180/180, and variance is
zero. This is diagnostic product evidence only. It does not authorize parser
repair or make the coherent rows Gold.

## Verification and independent veto

- exact artifact regeneration passes;
- 220 focused semantic, corpus, audit, parser, robustness, recovery, and
  handover tests pass;
- 316 broader ordinary-development preservation tests pass after excluding
  exactly two immutable historical report-regeneration assertions;
- `git diff --check` passes; and
- fresh Gemini 3.5 Flash independently accepted the contradiction taxonomy,
  verified exactly 12 text changes, reproduced every count and hash, ran 18/18
  review tests, and returned `DECISION: pass` with `PROTECTED_ACCESS: false`.

## Disposition and next decision

The useful next corpus step is a v2 anchor set built only from internally
coherent semantic/policy/replay contracts, restoring balanced clarification
and reversal coverage before further parser work. Authoring replacement
anchors changes the corpus contract and requires Yuri's next decision.

No protected holdout, historical diary, external corpus, product provider,
runtime, route, API, database, UI, confirmation, deployment, release, or write
surface was accessed or changed.

DECISION: partial_pass_with_quarantine
ACCEPT: 90
QUARANTINE: 102
REJECT: 0
ACCEPTED_ROBUSTNESS_COMPLETE: 4/90
SAFETY_PASS: 180/180
VARIANCE: 0
PROTECTED_ACCESS: false
