# LC4R8 Sol Acceptance

Date: 2026-07-15

## Authority and provenance

GPT Sol remained Conductor, sprint planner, architecture/acceptance owner,
recovery owner, and protected integrator. DeepSeek V4 Flash/high ran through
Claude Code `--bare` as the bounded implementation/test worker. DeepSeek Pro
and Deep Code were not used. Gemini 3.5 Flash/medium ran through a fresh
Antigravity project as the independent veto reviewer.

Sol rejected worker commit `0378b8b5` before integration because it omitted
required baseline/safety/variance evidence, copied exit constants, lacked
frozen action hashes, did not exercise genuine input-order variants, and had
insufficient fail-closed verification. Worker revision `e646d40b` corrected
the substantive evidence defects and passed 84 focused tests.

Sol adopted that revision only as an untrusted candidate under the Ariadne
recovery lease. Independent review then found that malformed structures could
still raise, a directly drifted recomputed `report_hash` field could pass, and
the order test did not retain canonical full-artifact evidence. Sol owned the
bounded verifier/test amendment in `afdf8ecd`; the recovery is documented in
`lc4r8-sol-recovery-amendment.md`. It changes no taxonomy or committed JSON.

## Accepted result

The 53-record clarification decision surface reproduces selection hash
`9496e23c6f339603`. Every record has an upstream semantic-contract blocker;
zero are isolated clarification-policy choices. Frozen blocker counts are
3/6/20/24/0, the four action counts are 13/13/14/13, and record hash is
`baf4c66b1a7ee139`.

The 51-record replay/delta audit reproduces selection hash
`2e45f30f714568ef`. Frozen class counts are 11/11/28/1/0. Only the 11
`audit_change_type_vocabulary_only` cases are authorized for a later
generator-backed contract repair; zero genuine replay integration defects are
present. Replay record hash is `2fabb972ad0bc00b` and the combined record hash
is `fd0de59a2967ddf8`.

The development exit result is therefore:

- clarification policy decision-ready: 0;
- genuine replay integration defects: 0;
- generator-backed contract repair authorized: 11;
- upstream clarification contract blockers: 53;
- remaining replay contract-reconciliation blockers: 40; and
- status: `blocked_pending_generator_repair_and_contract_reconciliation`.

Semantic counts remain `880/814/628/101/300/782`, safety remains 1,152/1,152,
and variance remains zero over 2,304 samples. The aggregate report hash is
`sha256:cc262683c1c5528fb3d10f49ef55cae17b2896a2739f51c110374bbe7dfa7644`.

## Verification

Sol's recovered focused suite passed 88/88 tests. The LC4R8 CLI reported
`LC4R8 CHECK PASSED`, Python compilation succeeded, and diff hygiene was
clean.

Gemini independently reviewed exact recovered source head
`1824de50761f329e7c4a7dd485aa028f372a20c1`, reproduced 88/88 focused passes
and the CLI check, audited the protected boundaries, and returned
`DECISION: pass` in `lc4r8-antigravity-independent-review.md`.

The expanded single-process serial preservation gate covered the 186-node T2
aggregate, T3.1-T3.4, LC1-LC4R8, action grammar, all current provider-free
interpretation-harness readiness/isolation guards, and Ariadne preflight. Its
first 1,598-node run produced exactly one failure: the documented pre-existing
runtime-isolation baseline in which `app/config.py` intentionally names the
blocked runtime-gate JSON while an older guard rejects even that path string.
Earlier S10 review artifacts already record the same baseline, and LC4R8
changed neither file.

The clean rerun deselected only that known baseline plus the three historical
LC3, LC4, and LC4R2 exact-report equality nodes whose committed artifacts
intentionally freeze earlier evaluator states. It collected 1,597 selected
nodes and completed with 1,595 passes, one expected xfail, and one established
scenario-integrity skip. No historical report was regenerated.

## Boundaries and continuation

LC4R8 changes no generated fixture, generator, interpreter, core
audit/scorer/replay, scenario schema, provider/T3.5 adapter, route/API,
database, UI, deployment, historical diary, memory/RAG, confirmation, or write
authority. Protected holdout v1 was not enumerated, opened, imported, run,
regenerated, or tuned against. T3.1-T3.4 remain intact and blocked by default.

Before LC4R9, perform the user-requested bounded handover-maintenance tranche:
create a byte-identical dated archive of the current `AGENTS.md` with a Git
object/hash receipt, then compact the live handover into current authority,
baton, boundaries, active tracks, and indexed historical ledgers without
losing unique information. Add deterministic rehydration/source-preservation
checks. This documentation-only maintenance must not alter product authority.

After that maintenance, LC4R9 may implement only the frozen 11-case
generator-backed audit-vocabulary contract repair. It must change the source
generator/contract rather than edit generated fixtures in place, freeze the
exact delta, and preserve the remaining 53 clarification and 40 replay
reconciliation blockers. Holdout reuse/v2 and live-provider authority remain
separate user decision boundaries.

LC4R8 is accepted.
