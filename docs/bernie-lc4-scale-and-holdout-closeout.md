# Bernie LC4 Scale and Protected Holdout Closeout

Date: 2026-07-14
Status: complete

## Outcome

LC4 met its exact bounded contract:

- 120 semantic groups;
- 1,440 linguistic variants;
- 360 multi-turn trajectories;
- 96 development groups / 1,152 variants / 288 trajectories; and
- 24 protected-holdout groups / 288 variants / 72 trajectories.

The development partition is DeepSeek-generated Silver/pending evidence. The
holdout was authored by protected GPT Sol only after all DeepSeek and Gemini
work ended; it is synthetic Gold/adjudicated evidence with no provider-model
generator or write authority.

## Development baseline

The deterministic LC3 interpretation/replay/scoring path ran twice over all
1,152 development variants: 2,304 samples with zero repeat variance.

| Dimension | Passed | Failed |
|---|---:|---:|
| Complete sample | 0 | 2,304 |
| Intended action | 928 | 1,376 |
| Action semantics | 1,024 | 1,280 |
| Temporal relation | 954 | 1,350 |
| Normalized values | 142 | 2,162 |
| Entity semantics | 136 | 2,168 |
| Clarification requirement | 1,088 | 1,216 |
| Downstream outcome | 108 | 2,196 |
| Interpretation/replay tools | 486 | 1,818 |
| Authority | 1,088 | 1,216 |
| Appointment deltas | 432 | 1,872 |
| Audit deltas | 384 | 1,920 |
| Safety | 2,304 | 0 |

Failure-layer attribution is simultaneous: 2,282 interpretation, 2,196 policy,
2,244 integration, and zero safety attributions. The report retains 96
deterministically selected, repeat-deduplicated repair findings rather than
serializing all 2,304 samples.

The 1,152 pending candidates cover 444 candidate-only lattice cells. They do
not reduce the three Gold cells or the 152,061 adjudicated empty cells.

Development corpus hash:
`sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647`

Development report hash:
`sha256:d94f9481a6333af25645253a02517b5ac5b9ed7fc1b93901571751f60a1c325e`

## Independent pre-holdout veto

Gemini 3.5 Flash (High), through a fresh bound Antigravity worktree, returned
`DECISION: pass` before the real holdout existed. It reproduced 76 corpus tests,
94 evaluator tests, and both report checks. Its first prose response mistyped
the reviewed commit; two wrapper receipts bound the substantive review and the
provenance correction to exact clean before/after SHAs. The complete transparent
record is `docs/adversarial/lc4_pre_holdout_veto_review.md`.

## Protected holdout baseline

Sol sealed `lc4-holdout-v1` with manifest hash
`sha256:cd4a806e47f2a1ce802dcb88aa7eddefeae0f69f2a1bc6963d81245dd8e71f01`
and consumed evaluation ID `lc4-holdout-v1-baseline-001` exactly once.

The committed report exposes aggregates and slices only. It contains no
utterance, scenario/group/variant ID, expected label/outcome/tool/delta, source
span, normalized value, case finding, or per-case failure.

| Dimension | Passed | Failed |
|---|---:|---:|
| Complete sample | 0 | 576 |
| Intended action | 72 | 504 |
| Action semantics | 86 | 490 |
| Temporal relation | 312 | 264 |
| Normalized values | 0 | 576 |
| Entity semantics | 64 | 512 |
| Clarification requirement | 166 | 410 |
| Downstream outcome | 0 | 576 |
| Interpretation/replay tools | 158 | 418 |
| Authority | 118 | 458 |
| Appointment deltas | 88 | 488 |
| Audit deltas | 88 | 488 |
| Safety | 568 | 8 |

The eight safety failures come from safe negated completion/bypass wording that
the deterministic interpreter mishandles. They are retained as an honest
capability gap; no holdout case was rewritten after observing the baseline.
Failure-layer totals are 576 interpretation, 576 policy, 538 integration, and
eight safety attributions. Repeat variance is zero.

The holdout covers 264 distinct adjudicated cells, all new relative to the
three LC1 cells. Combined adjudicated coverage is 267/152,064, leaving 151,797
empty cells.

Holdout corpus hash:
`sha256:bf6a8c9255da7055b01b1e4abd7d3289b287f120e90b6ce8e94780d3458f8b84`

Aggregate report hash:
`sha256:17f7c3f8c894b06e47069a94236c8180e76d3eb667aaea0c95174de27e98d083`

Holdout v1 must not be re-evaluated, regenerated, or tuned against. Further
certification requires a new version or an explicit reviewed reuse policy.

## Acceptance evidence

The serial LC1-LC4 plus T1/T2/T3.1-T3.4 gate collected 682 tests and completed
with 681 passes and one expected xfail. The LC4-focused corpus/evaluator/holdout
gate completed 183 passes. Exact development, scaled-evaluation, and sealed
holdout checks pass; the T3 live gate still reports `decision: blocked`,
`external_calls_ready: false`, and `runtime_authority_ready: false`.

## Transport and recovery record

The tranche contract correctly specifies Claude Code `--bare` as the preferred
DeepSeek transport. DW2 nevertheless inherited an in-flight Deep Code lane from
stale transport wording. Yuri directed that it not be interrupted but that
future work use Claude Code. That bounded lane completed with a PTY receipt and
process cleanup; no later DeepSeek lane was opened. Future DeepSeek dispatch
must use Claude Code `--bare` unless an actual recorded failure activates the
Deep Code fallback.

Sol independently rejected two worker defects before integration: unbounded
case findings/weak report hashing, followed by optional identity credentials
and a shallow aggregate schema. The accepted implementation caps findings,
binds the complete report, requires all holdout credentials, validates nested
aggregate output, and keeps actual holdout support outside product modules.

## Next direction

LC4 does not justify T3.5. It shows that the deterministic semantic bridge
dominates model-shadow usefulness. The next tranche is LC4R: development-only
repair of lossless normalization, temporal/negation semantics, entity
resolution, clarification state, and interpretation/replay tool selection.
Provider/live/write gates remain closed.
