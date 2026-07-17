# Bernie Synthetic Silver Robustness Baseline Closeout

Date: 2026-07-17

Status: `baseline_complete_product_gap_observed`

## Outcome

The current deterministic Bernie interpreter was evaluated without repair
against all 192 admitted synthetic receptionist-to-assistant Silver
candidates. Each candidate ran twice through the existing semantic extraction,
deterministic replay, and composed scorer path.

The evidence is complete and valid:

- candidates: 192/192;
- observations: 384/384;
- repeat variance: zero;
- safety: 384/384;
- product-complete candidates: 2/192;
- product-failed candidates: 190/192;
- report hash:
  `sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5`.

The two complete candidates are the medium and high variants of
`bernie_noise_seed_001`, a one-shot exact create instruction. Every other
candidate has at least one exact semantic, policy, or replay mismatch.

## What the score means

This is a robustness failure on the admitted synthetic distribution, not a
certification regression and not evidence about real-world receptionist
frequency. V10 remains sealed and unchanged. The result shows that the
currently certified bounded language contract does not generalize broadly to
the newly authored shorthand, fragmentation, slot order, and multi-turn
surfaces.

The raw downstream failure totals are mostly cascades from interpretation.
Using the first failing diagnostic boundary per candidate gives:

| Primary diagnostic category | Failed candidates |
|---|---:|
| Action extraction | 114 |
| Temporal/normalization | 68 |
| Entity semantics | 6 |
| Replay/integration only | 2 |
| Safety | 0 |

The medium and high variants perform almost identically: each has one pass and
95 failures. The problem is therefore not confined to the deliberately
heaviest noise.

## Important clusters

- All 32 schedule-explanation candidates primarily fail action extraction.
- All 24 clarification-form candidates primarily fail action extraction.
- Status change and resize shorthand frequently fail to identify the intended
  action; resize language is sometimes interpreted as create.
- Bounded phrases such as `by 5pm` and `3pm or later` are frequently reduced to
  exact or unspecified relations, producing temporal/normalization failures.
- Correction surfaces account for all six primary entity-semantic failures.
- Only two candidates reach a replay-only primary failure, so broad replay or
  policy repair is not supported by this baseline.

These clusters are diagnostic priorities, not remediation authority. A later
development sprint should reproduce a small representative slice before any
parser change and must distinguish language-authoring quality from a genuine
product requirement.

## Evidence integrity

The adapter cloned each named ordinary-development source scenario and
replaced only candidate identity, synthetic dialogue/evidence, and benign
language metadata. `deterministic_interpret` received only dialogue turns and
reference date. Expected fields were used only by the existing replay/scorer
oracle.

The JSON report contains every failing candidate's exact expected and observed
dimensions but no source utterances. It binds the accepted corpus, seed
manifest, ordinary development corpus, admission decision, and frozen source
commit.

A fresh Gemini review on exact source
`ec3d32dca17b583b7e7f7f05939e235b43e2ff3a` independently reproduced the
2/192 result, 384/384 safety, zero variance, hashes, and no-oracle-leakage
claim and returned `DECISION: pass`.

During initial discovery, one broad filename command emitted protected-path
filenames. No protected content, labels, hashes, modules, manifests, seals, or
reports were opened or used. The incident is metadata-only, contained, and
grants no future access authority.

## Boundary and next decision

No parser, policy, replay, product, API, database, UI, runtime, provider,
confirmation, deployment, release, or write surface changed. The synthetic
corpus remains development Silver and makes no real-world or Gold claim.

The baseline is complete. The next material choice is whether to authorize a
small ordinary-development diagnostic/remediation tranche, beginning with
action extraction and temporal operators, or to revise/expand the synthetic
language distribution first. No automatic repair follows from this report.

DECISION: baseline_complete
PRODUCT_COMPLETE: 2
PRODUCT_FAILED: 190
SAFETY_PASS: 384
VARIANCE: 0
PROTECTED_CONTENT_ACCESS: false
