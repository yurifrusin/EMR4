# LC4V4D2 Sol Acceptance

Date: 2026-07-15

Decision: `semantic_remediation_valid_with_d1_quarantine`

Conductor, recovery, taxonomy, acceptance, and integration owner: GPT Sol.
Bounded implementation worker: DeepSeek V4 Flash/high through Claude Code
`--bare`. Independent veto reviewer: Gemini 3.5 Flash/high through a fresh
Antigravity project. DeepSeek Pro was not used.

## Exact evidence

- Frozen D2 contract: `c8f015962ecc836d2c0b2a25426ea1114e8c1ccb`.
- DeepSeek candidate: `9b9d86e0` (adopted as untrusted candidate at
  `5ba29ef0f3e03a6128e5e0a34bad1c4d40f36f20`).
- Sol recovered semantic/evidence source: `0c898662b123a27f8b87e2e992abf34a72299134`.
- Exact source commit named by the report:
  `862c34bbda6d2544c63263155d9e3915d5b557df`.
- Exact recovered report head independently reviewed by Gemini:
  `13d95c186a6e6d54f90a32fcf8440baed9608a9e`.
- D1 frozen report hash:
  `sha256:1527b99359dc76e831d7eabf49fff022781faf5d248c436bde6e022f30eff84d`.
- D1 raw 23-case selection hash:
  `sha256:1b254ae627e26b1b301b660628d90f39dce5e0364afc0cfcf4c4855fb6531f02`.
- Audited valid 20-case selection hash:
  `sha256:0badec28ad533b630786d245e5ab47dee5655b83239869f7d0a2d12a8935d105`.
- Complete D2 report hash:
  `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`.

## D1 incident and scope correction

D2 discovered three internally contradictory D1 oracle rows. Sol independently
proved them from ordinary authored utterances, spans, labels, and normalized
values. Corrected duration retained the old value, negated duration retained a
value, and an explicit elliptical duration was labelled omitted. The frozen D1
fixture and report remain unchanged as provenance, while
`lc4v4d1-sol-acceptance-amendment.md` supersedes their interpretation.

The audited D1 baseline is therefore 3 authoring-invalid, 20 parser gaps, 12
policy-contract gaps, and 25 supported passes. This is a correction of evidence
scope, not a weakened oracle: the three invalid rows are quarantined rather
than made to pass, and only the exact remaining 20 were eligible for repair.

## Remediation result

All 20 valid utterance-level interpretation gaps close. The current diagnostic
is 3 quarantined authoring-invalid, zero parser gaps, 20 policy-contract gaps,
zero scorer/planned-unavailable cases, and 37 supported passes. The 57 valid
probes produced 114 complete repeat observations with zero variance.

The repair adds bounded composable behavior for omitted required patient
identity, explicit entity alternatives and exclusions, duration ambiguity and
negation, correction, later clarification, elliptical carry, session restart,
request reversal, move-target normalization, resize recognition, and
practitioner possessives. Safe/unsafe pairs retain identical base semantics.
False-positive guards cover ordinary alternatives and non-reversal uses of
`disregard` and `forget that`.

No new parser gap appears. All 25 previously supported rows remain supported.
The five mismatched diary joins remain policy-contract gaps. No replay, scorer,
policy table, provider, route, database, UI, deployment, or write authority was
changed.

## Worker failure and Sol recovery

DeepSeek correctly surfaced the three oracle contradictions and supplied useful
semantic candidates, but returned `candidate_complete` while representing them
as three remaining parser gaps. Its evaluator hard-coded validity/counts,
misrepresented before-state fields, used a vacuous diary-join preservation
test, and allowed completion with unresolved nominal targets. Its first
reversal/restart patterns were also over-broad.

Sol did not open a Flash correction loop. Under the recovery lease, Sol made
the grammar request-local, added direct positive and false-positive tests,
introduced cross-field authoring validation, recomputed the complete frozen D1
report, proved the quarantine, compared exact before/after evidence, and made
the decision and hash fail closed over the complete payload. The preserved
details are in `lc4v4d2-sol-recovery-amendment.md`.

## Verification and veto

- Focused semantic plus D1/D2 suite: 203/203 passed serially.
- Adjacent deterministic interpretation/replay/scorer preservation gate:
  182/182 selected nodes passed serially.
- Two immutable historical exact-report nodes were deliberately deselected;
  neither historical artifact was regenerated.
- `git diff --check` passed.
- Gemini independently reproduced 203/203 tests, all relevant hashes and
  counts, the three authoring contradictions, zero variance, false-positive
  boundaries, safety-pair invariants, and protected-boundary compliance on
  exact head `13d95c18`, then returned `DECISION: pass` in
  `orchestration/agent_inbox/antigravity/lc4v4d2-independent-review.md`.

## Authority decision

LC4V4D2 semantic remediation is accepted. Deterministic utterance-parser repair
for this bounded D1 selection is complete. The 20 current policy-contract gaps
are not parser failures and are not accepted product behavior; they form the
candidate population for a separately frozen LC4V4D3 policy/state-join tranche.

LC4V4 remains an aggregate `certification_fail`; no protected holdout may be
rerun or interpreted case-by-case. Holdouts v1-v4 remain sealed. T3.1-T3.4
remain blocked; T3.5, providers, historical-diary expansion, routes/APIs,
database/UI work, deployment, release, and all runtime write authority remain
deferred.
