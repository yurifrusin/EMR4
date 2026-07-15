# LC4V4D1 Sol Acceptance

Date: 2026-07-15

Decision: `diagnostic_valid`

Conductor, recovery, taxonomy, acceptance, and integration owner: GPT Sol.
Bounded worker candidate: DeepSeek V4 Flash/high through Claude Code `--bare`.
Independent veto reviewer: Gemini 3.5 Flash/high through a fresh Antigravity
project. DeepSeek Pro was not used.

## Exact evidence

- Frozen D1 contract commit: `191144f680ceb982d6c46739fa428f3f23298246`.
- Recovered source commit evaluated by the report:
  `be1f1c13811ff608906511611f38420eaa6994ef`.
- Exact recovered report head independently reviewed by Gemini:
  `5e1f0de4d49c9cdbcd7ec2b06d33b8e61d922e72`.
- Fixture hash:
  `sha256:a81de0b5371d4fcc425c23f0da9560e29827e3e85cc22847990ea83518863269`.
- Full report hash:
  `sha256:1527b99359dc76e831d7eabf49fff022781faf5d248c436bde6e022f30eff84d`.
- Candidate parser-gap selection hash:
  `sha256:1b254ae627e26b1b301b660628d90f39dce5e0364afc0cfcf4c4855fb6531f02`.

The 60 fresh, inspectable development probes produced 120 complete repeat
observations with zero variance:

| Classification | Count |
|---|---:|
| `authoring_invalid` | 0 |
| `parser_gap` | 23 |
| `policy_contract_gap` | 12 |
| `scorer_gap` | 0 |
| `planned_unavailable` | 0 |
| `supported_pass` | 25 |

Per family, entity is 12 parser / 8 policy / 10 pass; dialogue is 5 parser / 1
policy / 6 pass; safety is 6 parser / 3 policy / 3 pass; diary state is 6/6
pass. The case-level evidence remains intentionally inspectable because this is
ordinary development evidence, not a protected certification holdout.

## Worker failure and Sol recovery

DeepSeek's preserved candidate `43a67a86` classified all 60 probes as parser
gaps. Sol rejected that result because its surface validator did not prove the
semantic oracle, its policy defaults were generic and wrong, its safety pairs
were not actually safe/unsafe authority pairs, its classifier collapsed later
tool/policy/delta failures into parser gaps, its repeat comparison was partial,
and its report hash did not bind the complete result.

Under the recovery lease, Sol retained only useful authoring scaffolding and
independently replaced the evidence contract. The recovered implementation now
fails closed on exact population, entity lattice, single-field isolation,
dialogue turn structure, authority-clause pairs, identical diary surfaces,
lossless spans, mismatched diary proof, exact manifest readback, execution
exceptions, and complete normalized repeat fingerprints. Semantic and policy
oracles are authored before and independently of observation. Explicit diary
state joins are policy-contract gaps rather than utterance parser gaps, and
scorer gaps are reserved for scorer-only disagreement after component success.
The complete recovery record is
`orchestration/agent_inbox/codex/lc4v4d1-sol-recovery-amendment.md`.

## Verification

- Focused recovered D1 suite: 30/30 passed.
- Adjacent deterministic interpretation/replay/scorer preservation gate:
  182/182 selected nodes passed serially.
- Exactly two immutable historical report-equality nodes were deliberately
  deselected; their committed LC3 and LC4 artifacts were not regenerated.
- `git diff --check` passed.
- Gemini independently reproduced 30/30 focused tests, all three hashes, the
  23/12/25 split, and zero variance on exact recovered head `5e1f0de4`, then
  returned `DECISION: pass` in
  `orchestration/agent_inbox/antigravity/lc4v4d1-independent-review.md`.

## Meaning and authority decision

D1 is valid diagnostic evidence. It does not demonstrate poor overall progress:
the six diary-state probes all pass and 25/60 fresh probes are already complete.
It does demonstrate that the remaining weakness is real and concentrated:
explicit entity ambiguity/negation, omitted required identity, selected
correction and multi-turn reduction, action recognition, and a smaller set of
tool/refusal/state-join policy rules.

The 23-case parser selection is eligible to seed a separately frozen ordinary
development remediation contract because its surfaces and repeat mismatches are
inspectable and Gemini-confirmed. The 12 policy cases must not be treated as
parser training evidence. They should be handled in a later policy/state-join
tranche after semantic remediation is stable.

No remediation was performed or authorized inside D1. Holdouts v1-v4 remain
sealed. T3.1-T3.4 remain blocked by default; T3.5, providers, historical diary
expansion, routes/APIs, databases, UI, deployment, release, and all runtime
write authority remain deferred.
