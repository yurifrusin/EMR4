# Bernie Synthetic Silver Robustness Baseline Contract

Date: 2026-07-17

Status: `accepted_baseline_complete`

Authority: Yuri's development-only baseline authorization

## Objective

Measure the current deterministic Bernie interpretation and replay path against
the 192 admitted synthetic receptionist-to-assistant Silver candidates before
changing parser, policy, replay, or product behaviour.

This is diagnostic ordinary-development evidence. It may identify candidate
gaps, but it does not authorize remediation, Gold promotion, certification,
runtime/provider activation, API/database/UI work, confirmation, deployment,
release, or diary write authority.

## Frozen inputs

- Source commit: `4ac0a901f24aa71ff8968d6729e30f832d31863e`
- Candidate canonical hash:
  `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`
- Candidate Git blob: `f0eadc06d8aa873b96eec77bcc94f305c0ad919b`
- Semantic-seed Git blob: `38448ea31b001ade21e1953234695be789503c48`
- Admission Git blob: `162be3a0f1f9778b1b3e299115737fd31797809b`

Current deterministic path bindings:

- semantic extraction: `efa5b9584e6614f47f653106ce1d49532c258e46`;
- interpretation/replay: `af976a19590d974b8f3a60701085c8a8f298bd39`;
- composed scorer: `692a774e53ba79644f039bade559705f9910469a`;
- development loader: `b54dfe0e25d92d2eba0df45cb32e97ddc28467c7`;
- scenario contract: `fda836d543248828f3780749c146a3ca6ab3b89d`.

The evaluator must fail closed if any candidate, seed, admission, source
scenario ID/hash, count, or authority binding differs.

## Evaluation method

1. Load only the ordinary LC4 development corpus through
   `DevelopmentOnlyLoader`.
2. Reconstruct each candidate as a `ReceptionScenarioSpec` by taking the
   original ordinary-development scenario as the semantic/diary oracle and
   replacing only dialogue turns, source spans, candidate identity, and
   language metadata.
3. Run the current `deterministic_interpret`, `deterministic_replay`, and
   `score_interpretation_replay_pair` path twice per candidate.
4. Compare all semantic, clarification, policy, replay, delta, authority, and
   safety dimensions without feeding expected values into interpretation.
5. Emit aggregate counts and every failing candidate ID with exact expected
   and observed values. Do not include source utterances in the report.
6. Require zero repeat variance; variance invalidates the baseline.

The report must break results down by action, dialogue form, noise level,
failure layer, semantic field, and diagnostic category:

- action extraction;
- temporal/normalization;
- entity semantics;
- ambiguity/clarification;
- policy projection;
- replay/integration; and
- safety.

## Decision rules

- `baseline_complete`: all 192 candidates and 384 observations were evaluated,
  inputs remained exact, safety stayed closed, and repeat variance is zero.
- `revision_required`: evidence binding, completeness, safety, or variance
  fails.

`baseline_complete` does not mean every product dimension passed. Product
failures are the intended diagnostic output and must be preserved without
repair in this sprint. Any material parser or clarification-policy choice
returns to Yuri before implementation.

## Protected and product boundaries

Protected V1-V10 fixtures, supports, manifests, seals, receipts, and case
reports remain inaccessible. Historical diary and external corpus material
remain inaccessible. The evaluation is provider-free and performs no real
diary mutation.

During initial file discovery, a broad filename command emitted names of some
protected-path files despite the intended content globs. No protected file was
opened, read, hashed, imported, or used, and the names provide no case labels.
This metadata-only incident is contained here and grants no reuse authority.

## Accepted evidence

The exact report at
`docs/bernie-synthetic-silver-robustness-baseline-report.json` has report hash
`sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5`.
A fresh Gemini 3.5 Flash project independently reproduced the input bindings,
adapter, evaluator path, counts, safety, variance, and evidence/product
decision distinction and returned `DECISION: pass`.
