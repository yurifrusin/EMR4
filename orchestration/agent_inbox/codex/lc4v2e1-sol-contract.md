# LC4V2E1 Sol Development Exit-Gap Contract

## Decision and scope

Yuri authorized continued ordinary work on 2026-07-15 after LC4V2R2. LC4V2E1
is a development-only exit-gap reassessment, not a parser-repair tranche and not
LC4V2R3. It determines whether the currently accepted development evidence
supports another repair or whether the next step has reached the separate
certification user-decision boundary.

Protected holdouts v1 and v2 remain sealed. This audit may not open, enumerate,
list, search, import, run, regenerate, evaluate, hash-check, infer from, or tune
against either protected fixture, support module, authoring surface, manifest,
seal, receipt, per-case report, or filename population. Only the exact ordinary
development and accepted R1/R2 artifacts named below are authorized inputs.

## Frozen inputs

At source commit `5b21db8de98fea29f5e34d939cb88563698f8a89`:

| Artifact | Required SHA-256 or authority value |
|---|---|
| `orchestration/agent_inbox/codex/lc4v2r1-sol-acceptance.md` | `7ae181e4c997915569ab721970899411a312fa64ae6b1e94ef80574635a37c4e` |
| `orchestration/agent_inbox/codex/lc4v2r2-sol-acceptance.md` | `4520dcb2f9083d7a9dd54d86ee291450b998ed9a82be3a737fa12c76431d1356` |
| `docs/bernie-lc4v2r1-entity-normalization-report.json` | file `1ec1f5e0e6c29cd8292015b30228d2d54b4ec0d827a6ca1cf45c6c538b290b1f`; canonical report `sha256:46570a2e3ab5d47fe4d74594544d4e92f1d68cc8d8a51d5db39a233f59d84c38` |
| `docs/bernie-lc4v2r2-safety-language-report.json` | file `d7eec5e71d1abfd03b1db08aed5d5496a8553d8d716901458cb66de175bf2029`; canonical report `sha256:6cec58fe319a070b2c0f6d2cf0d99f74dc0f4b98352b3268709da2abc400f750` |
| `docs/bernie-lc4r10-report.json` | file `72e202fc05f38db11c071f310d96c2f9444cb7b2428bf8b29d85f6f4aeca8a8f`; `all_assertions_passed: true`; corpus `sha256:af8f3276a50a2defcf4e4f65570a5dd4de0d252544ff6d695792d63e7e518195` |
| ordinary development manifest | file `fb86598333542431e4c53fa6da9adc052d0ca028cbe5016c909130a189411e1a`; same corpus hash |

R1 and R2 must each retain zero failed cases, empty selection hash
`e3b0c44298fc1c14`, all contracted assertions, and zero repeat variance.
Ordinary development must retain semantic counts `880/814/672/154/330/835`,
safety 1,152/1,152, and zero variance over 2,304 samples.

## Decision taxonomy

The audit may emit exactly one of:

- `r3_authorized`: at least one newly frozen development-only surface contains
  a deterministic, directly surface-supported parser failure with a non-empty
  failure selection and no unresolved product-policy choice;
- `no_r3_authorized`: every currently frozen repair surface has an empty
  failure selection, LC4R10 remains accepted, and no new independent surface
  evidence exists; or
- `reassessment_invalid`: an input, hash, schema, assertion, count, variance,
  or protected-boundary declaration fails closed.

The frozen input set contains no newly authored post-R2 failure surface.
Therefore, if every binding passes, the mechanically required decision is
`no_r3_authorized`. This is not a product-readiness or certification claim.

## Required output

Implement a deterministic report and tests that:

- read only the six exact authorized inputs above;
- bind file hashes and relevant internal authority values;
- report R1/R2 failure counts, selections, assertions, and variance;
- report the exact ordinary development counts, safety, variance, and corpus
  hash from the accepted R10 evidence;
- state `development_repair_exit_reached: true` only when the decision is
  `no_r3_authorized`;
- state `certification_status: unresolved_user_decision` and never infer product
  readiness;
- name the next gate as `fresh_holdout_or_reviewed_reuse_policy`;
- use an explicit `--write` and non-mutating exact `--check` mode;
- include a canonical report hash and zero nondeterministic inputs; and
- fail closed if any unexpected file, key, value, or protected reference enters
  the audit configuration.

## Allocation and boundaries

GPT Sol owns this evidence taxonomy and implementation. DeepSeek is not used
because cross-sprint exit classification is explicitly Sol work. Gemini 3.5
Flash through a fresh Antigravity worktree provides an independent exact-head
veto before acceptance. No external worker may alter the report or integrate.

Authorized implementation files:

- `scripts/bernie_lc4v2_exit_gap_reassessment.py`;
- `tests/test_bernie_lc4v2_exit_gap_reassessment.py`;
- `docs/bernie-lc4v2-exit-gap-report.json`; and
- `docs/bernie-lc4v2-development-exit-reassessment.md`.

T3.1-T3.4 remain intact and blocked by default. T3.5, providers, routes/API,
database, UI, deployment, runtime, historical diary, memory, confirmation,
release, and write authority remain closed. A fresh holdout or reuse policy is
a documented Yuri decision boundary and is not authorized by this contract.
