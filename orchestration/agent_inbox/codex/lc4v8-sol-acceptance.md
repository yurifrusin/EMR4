# LC4V8 Sol Acceptance

Date: 2026-07-16

Decision: `certification_fail_user_development_decision_required`

## Authority and provenance

Yuri authorized genuinely fresh LC4V8 after LC4V7D1 reached its clean exit.
DeepSeek V4 Flash/high through Claude Code `--bare` supplied only a
content-blind candidate at `2beeffe8`; Sol rejected it for conceptual
evidence-integrity fail-open behavior and recovered under the recorded lease
without a correction loop. The rejection, receipt, and every Sol amendment are
preserved in `lc4v8-sol-recovery-amendment.md`.

Sol's recovered framework passed 41 focused tests and two ordinary isolation
tests. Gemini 3.5 Flash/medium returned `DECISION: pass` in a fresh Antigravity
project on exact framework head `3c3a2662`. Before content, Sol additionally
bound the product-facing evaluator source; a second fresh Antigravity project
returned `DECISION: pass` on exact amended head
`b24f02934c509d5def819735cd83cbb9eb56832a`, reproducing 41 focused passes,
two isolation passes, and the one documented baseline deselection.

All external sessions then closed. Sol alone authored the actual corpus,
evaluator, thresholds, manifest, and seal. The exact corpus source commit is
`313e6247ea0851d12b925e8fc5b31315b2464654`; the immutable seal commit is
`5d465667ae9c0d91b4a1ad159610058c3c883920`. Holdouts v1-v7 remained sealed
and unavailable throughout.

## Sole attempt

Attempt `lc4v8-fresh-certification-001` created its exclusive marker before
evaluation and is permanently consumed. Exact evidence shape:

- 24 groups, 288 scenarios, and 576 two-repeat samples;
- 4 groups per implemented action and 12 scenarios per group;
- 48 scenarios / 96 samples per language form;
- 72 multi-turn and 216 one-turn scenarios;
- 288 distinct coverage cells; and
- zero validation errors, runtime exceptions, missing dimensions, case
  artifacts, oracle leaks, or repeat variance.

The valid aggregate result is:

| Dimension | Passed |
|---|---:|
| intended action | 576/576 |
| action semantics | 576/576 |
| temporal relation | 528/576 |
| normalized values | 528/576 |
| entity semantics | 576/576 |
| lossless source spans | 576/576 |
| extraction clarification | 576/576 |
| policy resolution | 0/576 |
| policy clarification | 576/576 |
| clarification composition | 576/576 |
| interpretation tool | 576/576 |
| replay | 576/576 |
| safety | 576/576 |

Complete is `0/576`. Interpretation failures, policy failures, and integration
failures are all zero. Every public group has complete `0/24`; every language
form has complete `0/96`. The final complete report hash is
`sha256:1b66929304a0a0e1cfecf31e85ab3dc85b891c7ddac73772f84c0815835c7ac6`.

## Acceptance interpretation

All evidence-procedure gates pass, so the result is not
`certification_invalid`. Product gates miss: complete, policy-resolution,
temporal-relation, normalized-value, every group, and every language-form
gate. Under the frozen generic taxonomy the only valid decision is
`certification_fail`.

The aggregate pattern proves a corpus-wide policy-resolution contract or
representation mismatch and a smaller temporal/normalization mismatch. It
does not identify case-level parser defects and supplies no repair authority.
In particular, the simultaneous 576/576 replay, safety, policy-clarification,
and clarification-composition results plus 0/576 policy resolution make a
systematic representation/Gold projection cause the first development
hypothesis, not evidence of broad parser regression. That statement is an
inference from public aggregates only.

V8 is sealed and consumed. Do not inspect, enumerate, search, import, run,
regenerate, hash-check, relabel, repair, rescore, or reuse its fixture,
evaluator, authoring module, manifest, seal, marker, tests, or per-case state.
Only this acceptance, the aggregate report, and aggregate closeout are
available for planning.

## Post-seal preservation

No V8 protected source or test was loaded after sealing. The explicit serial
ordinary-development gate passed 279/279 Bernie nodes. Exactly three nodes
were deselected: the two immutable LC4V4D3 committed-report regeneration/equality
nodes, whose historical artifacts are not rewritten under later source, and
the documented runtime-isolation baseline that rejects the intentionally
configured blocked-gate path in `app/config.py`. The compact live-handover gate
then passed 5/5 with `AGENTS.md` at 499 lines. `git diff --check` is required
again immediately before commit.

## Next authority boundary

Pause for Yuri's development decision. Recommended option: authorize a bounded
ordinary-development `LC4V8D1` using newly authored inspectable probes derived
only from the public aggregate categories. D1 should first test whether the
0/576 policy-resolution result is an authoring/projection mismatch, then
separately sample the 48 temporal/normalization misses. It must not derive
probes from sealed cases or grant a V8 rerun. Any later V9 certification is a
separate user decision after development exit.

T3.1-T3.4 remain intact and blocked. T3.5/provider calls, product/runtime
wiring, API/database/UI/deployment work, and all live/write authority remain
deferred.
