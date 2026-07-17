# Bernie Synthetic Silver All-192 Coherence Audit Contract

Date: 2026-07-17

Status: `accepted_partial_pass_with_quarantine`

Authority: Yuri's bounded corpus/admission audit and repair authorization

## Objective

Audit every admitted synthetic receptionist-to-Bernie Silver candidate for
surfaced semantic-evidence completeness and internal oracle, clarification-
policy, entity-transition, and replay-contract coherence. Quarantine invalid
rows or regenerate them without changing their frozen ordinary-development
semantic anchors.

This is corpus engineering. It does not authorize parser, policy, replay,
scorer, runtime, provider-adapter, API, route, database, UI, confirmation,
deployment, release, Gold, certification, or write-authority changes.

## Frozen inputs

- audit source head before row inspection:
  `7c51e574930962ae83e721e3766fcbbee26d6013`;
- accepted candidate canonical hash:
  `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`;
- accepted candidate Git blob:
  `f0eadc06d8aa873b96eec77bcc94f305c0ad919b`;
- semantic-seed Git blob:
  `38448ea31b001ade21e1953234695be789503c48`;
- admission Git blob:
  `162be3a0f1f9778b1b3e299115737fd31797809b`;
- accepted post-remediation full-Silver report hash:
  `sha256:b0d7072884b2d8331fbc233de797c112bf11503a04cdd5ce95ad69c327feacc8`.

The audit population is exactly the 192 records currently admitted by
`tests/fixtures/bernie_synthetic_noise/admission.json`. No protected fixture,
manifest, seal, receipt, support module, or per-case report may be opened,
listed, searched, hashed, imported, or used.

## Coherence rules

A row is coherent only when all of the following hold:

1. Its dialogue and exact evidence spans surface every semantic value required
   to distinguish the frozen action, entity state, temporal relation,
   normalized value, correction, negation, ambiguity, and dialogue transition.
2. Ellipsis or anaphora may recover a value only from the same candidate's
   preceding receptionist turns; the source oracle cannot supply hidden facts.
3. A correction explicitly identifies the replaced field and replacement
   value. A reversal explicitly withdraws the action represented by the anchor.
4. Expected clarification state, interpretation tools, replay tools, and diary
   delta/outcome must agree with the surfaced dialogue and frozen semantics.
5. A candidate may be noisy, but its meaning must remain determinately aligned
   with its source seed for a competent receptionist reading the turns in order.
6. No audit or repair may make a row pass by feeding expected fields into the
   interpreter, weakening scoring, inventing hidden values, or changing the
   ordinary-development source oracle.

## Per-row decisions

The durable audit assigns exactly one primary decision:

- `accept_coherent`: all coherence rules pass;
- `quarantine_missing_surfaced_evidence`: required semantic evidence is absent
  or not locally recoverable;
- `quarantine_oracle_policy_conflict`: clarification or tool expectations
  contradict the surfaced meaning;
- `quarantine_entity_transition_conflict`: correction, negation, ambiguity, or
  state-transition expectations contradict the surfaced meaning;
- `quarantine_replay_contract_conflict`: expected outcome or delta vocabulary/
  shape contradicts the surfaced action; or
- `reject_semantic_corruption`: the dialogue changes the frozen semantic anchor
  or introduces unsupported clinical, identity, authority, or diary facts.

Secondary findings may be recorded, but one failure cannot conceal another.
Current parser output is diagnostic only and cannot determine whether a row is
coherent.

## Ordered method

1. Verify every frozen hash and admission binding before reading candidate rows.
2. Build a deterministic auditor that joins each candidate only to its named
   seed and ordinary-development source scenario.
3. Audit all 192 rows and preserve a per-row report with no protected data.
4. Freeze the pre-repair classification counts and selection hash.
5. Regenerate only quarantined rows whose frozen semantics can be surfaced
   without a product-policy choice. Preserve candidate IDs, source bindings,
   generator provenance, Silver status, and closed authority.
6. Re-run mechanical validation and the coherence audit. Rows that cannot be
   repaired without changing oracle or product behavior remain quarantined in
   a new admission decision.
7. Run the full 192-candidate robustness evaluator, focused corpus/parser tests,
   and ordinary-development preservation tests serially.
8. Obtain a fresh independent exact-candidate veto before Sol acceptance.

## Acceptance

- `coherence_pass`: 192/192 rows are coherent after bounded regeneration,
  mechanical validity passes, safety remains perfect, variance remains zero,
  and independent review passes.
- `partial_pass_with_quarantine`: every admitted row is coherent, unresolved
  invalid rows are explicitly quarantined, safety remains perfect, variance is
  zero, and independent review passes.
- `revision_required`: input binding, audit completeness, admission binding,
  safety, variance, or independent review fails.

Neither pass state promotes Silver to Gold or changes V10 certification.

## Boundaries

Protected V1-V10 remain sealed. Historical diary and external corpus material
remain inaccessible. External development reviewers may receive only the exact
synthetic candidate, ordinary-development bindings, contract, tests, and audit
artifacts; they receive no integration authority and may not certify their own
work.

## Accepted evidence

The audit closes as `partial_pass_with_quarantine`: 90/192 rows are admitted as
coherent and 102/192 are explicitly quarantined. Exact final report hash is
`sha256:4e2f3a5dd3632a8d5f927a2d42a203a909673d89d6406ded886eb37bbbfabd80`.
Fresh Gemini independently reproduced the taxonomy, 12 text-only repairs,
90/102 admission split, all hashes, safety, variance, and tests and returned
`DECISION: pass` on source code head `5649c9b1`.
