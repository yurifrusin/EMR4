# LC4V2 Sol Acceptance

## Decision

**DECISION: pass — procedure and evidence contract only**

**PRODUCT-READINESS RESULT: fail**

GPT Sol accepts LC4V2's fresh-corpus construction, content-blind review,
source freeze, one-shot aggregate evaluation, and sealing procedure. This is
not an acceptance of Bernie semantic readiness or authorization for T3.5.

## Accepted evidence

- frozen source commit:
  `f5af2fe5e7d7d6d96bb65299f832b0d6536e7b51`;
- manifest hash:
  `sha256:5555cfdde6a3b854d531630bfbb46678c403926847a04b176ae8e67319c44423`;
- shape: 24 groups, 288 variants, 72 multi-turn trajectories;
- evaluation: `lc4-holdout-v2-baseline-001`, two repeats, 576 samples;
- aggregate report hash:
  `sha256:61b01f256ce8ebc3ed91ff7754f2b4bc48d63eef79166f3be20ead6da6f1f122`;
- complete: 0/576;
- temporal relation: 576/576;
- intended action: 528/576;
- action semantics: 410/576;
- normalized value: 288/576;
- entity semantics: 0/576;
- clarification: 308/576;
- downstream/tool/authority dimensions: 410/576 each;
- appointment and audit deltas: 472/576 each;
- safety: 532/576;
- variance: zero across 576 samples; and
- aggregate coverage: 264 distinct cells.

The immediate aggregate schema, report-hash, source-commit, evaluation-ID, and
consumed-state check passed. The baseline command was invoked once only.

The final post-seal serial preservation gate collected 222 safe ordinary
development/framework nodes and completed with 220 passes, one expected xfail,
and one expected skip. It covered T1/T2, LC4R10, synthetic content-blind LC4V2
framework behavior, T3.1-T3.4, and handover integrity without loading either
protected holdout or the v2 authoring test. `git diff --check` passed.

## Worker and recovery provenance

DeepSeek V4 Flash/high through Claude Code `--bare` received only the
content-blind framework surface. Its self-certified candidate was rejected for
fabricated zero-failure output, incomplete production-count enforcement,
fail-open sealing, and a non-durable one-shot guard. The candidate and failure
were preserved. Because these were conceptual contract defects, Sol correctly
opened no Flash correction loop and replaced the framework under the recovery
lease.

Gemini 3.5 Flash/medium reviewed exact recovered framework head `82dfa640`
before actual content existed and returned `DECISION: pass`. It verified the
synthetic framework tests and adversarial fail-closed probes. All external
workers were closed before Sol-only content authoring began, and no external
worker saw actual v2 content or results.

## Interpretation

The aggregate baseline strongly supports the explicit temporal-relation
foundation: all 576 samples passed with zero repeat variance. It simultaneously
rejects product readiness. Every sample failed the complete composed contract,
every sample failed entity semantics, normalized values split 288/288, and 44
samples failed safety. The result cannot be remediated by inspecting or tuning
against v2; future work must use ordinary development evidence and fresh
synthetic development fixtures.

## Boundaries and next decision

Protected holdout v1 remained sealed throughout. Holdout v2 became sealed
immediately after consumption and now inherits the same no-read/no-rerun/
no-tuning rule. T3.1-T3.4 remain intact and blocked by default; T3.5 and all
live-provider, runtime, route/API, database, UI, deployment, release,
historical-trove, memory, confirmation, and write authority remain closed.

Sol recommends another aggregate-guided development-only semantic repair and
corpus-engineering tranche before any live-model comparison. Opening T3.5 or
authorizing any later certification holdout remains a documented user decision
boundary.
