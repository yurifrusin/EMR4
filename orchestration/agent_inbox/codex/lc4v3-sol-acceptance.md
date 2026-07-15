# LC4V3 Sol Acceptance

Date: 2026-07-15

Decision: `certification_fail`

Evidence procedure: `valid`

Parser remediation authority: `not_authorized`

## Frozen evidence identity

- Source commit: `c57a4d62dd1b633a0a1bb20f26b5bd0fd0a5d310`
- Evaluation: `lc4-holdout-v3-baseline-001`
- Evaluator: `lc4v3.aggregate_evaluator.v1`
- Manifest hash: `sha256:a128a77e9932710f2c979df1d0ab068832a55d976a44e923f13a56a8494f884f`
- Corpus hash: `sha256:c05ffbf9d513ed098216417bc3980abe284aa12079b6df4acd09d14bab88ec6d`
- Aggregate report hash: `sha256:cdbb5967ea0c5e32f7176425b04efdd6600aca7c51f88e241139da15301a8b73`
- Population: 24 groups, 288 scenarios, 72 trajectories, two repeats, 576 samples
- Coverage: 288 distinct cells
- Variance: zero variant scenarios and zero variant samples

The corpus and manifest were committed before sealing. The seal bound the
exact live source commit, the baseline ran once from the unconsumed seal, the
aggregate report was written before the consumed seal, and the post-run
aggregate-only checker passed without loading the corpus. No external model
session was active after actual content existed.

## Mechanical threshold decision

| Gate | Result | Required | Decision |
|---|---:|---:|---|
| Complete composed contract | 494/576 | at least 519/576 | fail |
| Intended action | 576/576 | at least 548/576 | pass |
| Action semantics | 550/576 | at least 548/576 | pass |
| Temporal relation | 576/576 | at least 548/576 | pass |
| Normalized values | 576/576 | at least 548/576 | pass |
| Entity semantics | 494/576 | at least 548/576 | fail |
| Clarification | 550/576 | at least 548/576 | pass |
| Downstream outcome | 550/576 | at least 548/576 | pass |
| Replay tool sequence | 496/576 | at least 548/576 | fail |
| Interpretation tools | 496/576 | at least 548/576 | fail |
| Authority | 550/576 | at least 548/576 | pass |
| Appointment deltas | 572/576 | at least 548/576 | pass |
| Audit deltas | 572/576 | at least 548/576 | pass |
| Safety | 576/576 | exactly 576/576 | pass |
| Interpretation failure layer | 82 | at most 57 | fail |
| Policy failure layer | 26 | at most 28 | pass |
| Integration failure layer | 80 | at most 28 | fail |
| Safety failure layer | 0 | exactly 0 | pass |
| Worst emitted slice | 0.0000 | at least 0.8000 | fail |
| Distinct coverage cells | 288 | at least 240 | pass |
| Repeat variance | 0/576 | zero | pass |

The failing worst slice is the aggregate `language_form=plain` slice at 0/82.
Every other language-form slice passed completely. That discontinuity is
strong evidence of a systematic authoring or representation defect rather
than general parser incapacity, but this is an aggregate inference only. The
sealed result exposes no case-level evidence and cannot justify inspecting,
repairing, relabelling, or rerunning v3.

## Authority decision

LC4V3 is a valid failed certification. It does not reopen deterministic parser
repair, prove a new parser gap, or authorize tuning from its outcomes. The
currently authorized development repair sequence remains complete: no
independently supported deterministic parser defect remains in ordinary
development evidence.

The post-consumption preservation gate passed 188/188 safe selected nodes:
56 content-blind framework/handover nodes and 132 ordinary composed-evaluator
nodes. The ordinary gate deselected only the two frozen historical
report-regeneration nodes named in the pre-content acceptance. The
aggregate-only checker also revalidated the report hash and schema without
loading the corpus.

Holdouts v1, v2, and v3 are now sealed. Do not open, enumerate, list, search,
import, run, regenerate, evaluate, hash-check, infer labels from, or tune
against their fixture, support, authoring, manifest, seal, receipt, or
case-level surfaces. Only committed aggregate evidence and closeouts remain
available for planning.

A later certification requires Yuri to authorize a genuinely fresh holdout
version or an explicit reviewed reuse policy. The recommended path is a new
content-blind authoring-quality tranche followed by a genuinely fresh v4; it
must not repair or reuse v3 cases. T3.1-T3.4 remain intact and blocked by
default. T3.5 providers, live calls, runtime wiring, deployment, and all write
authority remain deferred.

## Worker and recovery record

DeepSeek V4 Flash/high through Claude Code `--bare` produced the content-blind
candidate at `7392b951`; Sol rejected its fail-open validation and recovered
the framework without a correction loop. Gemini 3.5 Flash/medium independently
returned `DECISION: pass` on exact recovered framework head `170b44ab` before
any v3 content existed. Sol then froze the acceptance rule, closed external
sessions, authored and sealed the actual corpus alone, and retained sole
evaluation and acceptance authority.
