# Bernie LC4V2 Fresh Holdout Closeout

Status: procedure accepted; product-readiness baseline failed; holdout v2
consumed and sealed on 2026-07-15.

## Scope and authority

Yuri authorized a genuinely fresh synthetic holdout v2 and one initial
aggregate baseline. GPT Sol retained sole content, seal, evaluation,
acceptance, and integration authority. DeepSeek V4 Flash/high through Claude
Code `--bare` worked only on a content-blind framework candidate, and Gemini
3.5 Flash reviewed only the recovered content-blind framework before actual v2
content existed. All external sessions were closed before Sol authored the
corpus. Neither external worker received actual v2 content.

Protected holdout v1 was not opened, enumerated, searched, imported, run,
regenerated, evaluated, hash-checked, inferred from, or reused.

## Framework and corpus freeze

The content-blind framework validates the fixed production shape, full
manifest reconstruction, source-commit binding, aggregate-only report schema,
one-shot state transition, deterministic repeats, failure layers, critical
slices, variance, and forbidden case-level fields. DeepSeek's first candidate
was rejected for conceptual fail-open behavior and preserved. Sol replaced it
under the recovery lease; no Flash correction loop was opened. Gemini returned
`DECISION: pass` on exact recovered framework head `82dfa640` before content
creation.

Sol then authored a new synthetic Gold/adjudicated corpus with exactly:

- 24 semantic groups;
- 288 variants;
- 72 multi-turn trajectories; and
- two deterministic repeats, producing 576 aggregate samples.

The corpus and manifest were frozen at source commit
`f5af2fe5e7d7d6d96bb65299f832b0d6536e7b51`. The manifest hash is
`sha256:5555cfdde6a3b854d531630bfbb46678c403926847a04b176ae8e67319c44423`.

## One-shot aggregate baseline

Evaluation `lc4-holdout-v2-baseline-001` was invoked exactly once. It produced
an aggregate-only report and a consumed seal with report hash
`sha256:61b01f256ce8ebc3ed91ff7754f2b4bc48d63eef79166f3be20ead6da6f1f122`.
The immediate contract-authorized aggregate validation passed. Holdout v2 then
became sealed and was not loaded again.

| Dimension | Passed | Failed |
|---|---:|---:|
| Complete composed contract | 0 | 576 |
| Intended action | 528 | 48 |
| Action semantics | 410 | 166 |
| Temporal relation | 576 | 0 |
| Normalized value | 288 | 288 |
| Entity semantics | 0 | 576 |
| Clarification | 308 | 268 |
| Downstream outcome | 410 | 166 |
| Tool sequence | 410 | 166 |
| Interpretation tools | 410 | 166 |
| Authority | 410 | 166 |
| Appointment deltas | 472 | 104 |
| Audit deltas | 472 | 104 |
| Safety | 532 | 44 |

Failure-layer totals were 576 interpretation, 166 policy, 166 integration,
and 44 safety attributions. All 576 temporal-relation samples passed. The
report covered 264 distinct cells. Repeat variance was zero across all 576
samples.

These are aggregate findings only. They do not disclose or authorize inference
about any individual case. The perfect temporal result is credible evidence
that the explicit temporal relation foundation generalized. The zero complete
and entity-semantic totals, half-pass normalized values, and 44 safety failures
show that the deterministic bridge is not credible enough for live T3.5 model
comparison. LC4V2 therefore passes its holdout-construction and one-shot
evaluation contract while failing product-readiness certification.

## Final preservation gate

After v2 became sealed, the final serial gate loaded only ordinary T1/T2
development scenarios, LC4R10 regressions, synthetic content-blind framework
tests, T3.1-T3.4 scaffolding, and handover integrity. It collected 222 nodes
and completed with 220 passes, one expected xfail, and one expected skip. It
did not load either protected holdout or the v2 authoring test. `git diff
--check` also passed.

## Closed boundaries and next decision

Holdout v2 now has the same no-read/no-rerun/no-tuning boundary as holdout v1.
Do not open, enumerate, list, search, import, run, regenerate, evaluate,
hash-check, infer from, or tune against its fixture, manifest, authoring,
pre-seal, consumed-seal, or per-case support surfaces. Only the committed
aggregate report and this aggregate closeout may guide future planning.

T3.1-T3.4 remain intact and blocked by default. T3.5 adapters, live-provider
calls, runtime wiring, prompts, raw-response persistence, provider-executed
tools, promotion claims, and write authority remain deferred. The recommended
next tranche is an aggregate-guided, development-only semantic repair and
corpus-engineering cycle focused on entity semantics, normalized values,
clarification, and safety, without accessing either sealed holdout. Any later
certification requires another explicitly authorized fresh holdout or reviewed
reuse policy. Live T3.5 execution remains a separate user decision boundary.
