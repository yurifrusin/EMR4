# LC4V5 Fresh Certification Holdout Contract

Date: 2026-07-16

User authorization: Yuri explicitly authorized a genuinely fresh holdout v5.

Decision before framework/content: `fresh_v5_content_blind_framework_authorized`

## Authority and sequence

1. GPT Sol owns plan, architecture, thresholds, acceptance, recovery,
   integration, actual corpus authorship, sealing, and the one permitted run.
2. DeepSeek V4 Flash/high through Claude Code `--bare` may implement only a
   content-blind framework and synthetic framework tests in a disposable
   worktree. It receives no actual v5 scenario content.
3. Gemini 3.5 Flash through a fresh Antigravity project must independently
   veto the exact recovered empty framework before content exists.
4. All external sessions close before Sol authors any v5 content.
5. Sol authors and freezes exactly 24 groups, 288 scenarios, 72 multi-turn
   trajectories, and 576 two-repeat samples; creates an unconsumed seal; and
   commits the protected source.
6. Sol runs the sealed production evaluation exactly once. The run emits only
   aggregate evidence, consumes the seal, and permanently seals v5.

DeepSeek Pro is forbidden. No external worker may certify the framework,
author or inspect content, consume a seal, run the production evaluator, or
integrate.

## Content-blind worker surface

Owned candidate files:

- `app/services/bernie/lc4v5_holdout_framework.py`
- `tests/test_bernie_lc4v5_holdout_framework.py`
- `orchestration/agent_inbox/claude/lc4v5-deepseek-framework-candidate.md`

The framework must provide strict schema validation, canonical hashing,
manifest/seal validation, exclusive one-shot state transitions, aggregate-only
report generation, threshold evaluation, tamper/malformed/missing-input
failure, and injectable synthetic tests. It may read the ordinary
`scenario_spec.py` and `composed_corpus_evaluator.py` contracts only. It must
not discover or inspect any earlier holdout path, support module, authoring
surface, test, manifest, seal, receipt, filename, or case evidence.

No real v5 fixture, authoring script, manifest, seal, receipt, report, group
label, utterance, expected value, or case ID may exist before Gemini passes the
framework.

## Fixed comparable shape

- 24 semantic groups;
- 12 scenarios per group;
- 288 unique scenarios and coverage cells;
- 72 multi-turn trajectories and 216 one-shot scenarios;
- two repeats per scenario;
- 576 complete typed samples;
- synthetic Gold/adjudicated provenance only;
- all six implemented action categories represented;
- deterministic, aggregate-only output with no per-case failures persisted.

The exact thresholds are frozen separately in
`lc4v5-one-shot-acceptance-rule.md` and cannot change after content exists.

## Closed boundaries

Holdouts v1-v4 remain sealed and unavailable. Do not open, enumerate, list,
search, import, run, regenerate, evaluate, hash-check, infer, or tune against
their fixtures, support/authoring modules, manifests, seals, receipts, tests,
filenames, or per-case evidence. V5 becomes subject to the same boundary at
source freeze and may be consumed once only.

T3.1-T3.4 remain blocked; T3.5/providers, external prompts, historical diary
material, runtime/default changes, routes, APIs, UI, database, deployment,
release, and all live/write authority remain deferred.
