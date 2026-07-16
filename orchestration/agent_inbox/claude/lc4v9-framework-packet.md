# LC4V9 DeepSeek Flash Content-Blind Framework Packet

Status: `dispatched`
Date: 2026-07-16
Worker: DeepSeek V4 Flash/high via Claude Code `--bare`
Worktree: `C:\Users\sarashera\EMR4-worktrees\lc4v9-dw1`
Branch: `claude/lc4v9-content-blind-framework`
Source head: `f14f86a4b9a32f0083b10204bc8e4d4481a312fd`

## Objective

Implement and test one empty, content-blind LC4V9 certification framework.
There is no actual V9 corpus, evaluator, threshold file, manifest, seal, or
report. Do not create any of them. Use only opaque in-memory placeholder data
in tests. This is framework implementation, not planning or acceptance work.

Read only these named authority/source files:

- `AGENTS.md`;
- `orchestration/agent_inbox/codex/lc4v9-sol-contract.md`;
- `orchestration/agent_inbox/codex/lc4v9-one-shot-acceptance-rule.md`;
- `app/services/bernie/certification_decision_taxonomy.py`; and
- files you create under the owned surface below.

Do not use broad filesystem search, recursive listing, repository-wide grep,
or filename discovery. Do not inspect any earlier LC4V holdout path or content.

## Owned files

Create/edit only:

- `app/services/bernie/lc4v9_content_blind_framework.py`;
- `tests/test_bernie_lc4v9_content_blind_framework.py`; and
- `orchestration/agent_inbox/claude/lc4v9-deepseek-framework-candidate.md`.

No other file may change. Commit the candidate only on the assigned disposable
branch. Do not push and do not move `master` or `handoff/current`.

## Required behaviour

Implement a deterministic, dependency-light framework that:

1. rejects unknown or missing fields in fixture, scenario, Gold, threshold,
   manifest, seal, and report schemas;
2. validates the exact fixed 24/288/72/576 shape and coverage-cell uniqueness;
3. validates the fourteen scoring dimensions and `complete` conjunction;
4. represents policy behaviour and exact canonical 14-field policy projection
   as distinct dimensions;
5. validates Gold semantic outcome and canonical projection cross-field
   consistency before any evaluator callable can run;
6. imports and delegates final decision precedence to
   `classify_certification`;
7. verifies exact SHA-256 bindings for fixture, framework, evaluator, and
   thresholds, committed source ancestry/blobs, and loaded-evaluator source
   identity;
8. validates seal/attempt identity and uses exclusive durable marker creation
   before evaluator execution;
9. leaves the marker consumed on success, product failure, validation failure
   after marker creation, or exception, without cleanup or reuse; and
10. emits aggregate-only output and rejects per-case/oracle-bearing report
    fields.

Keep all I/O explicit through paths and injected callables so opaque temporary
tests can prove fail-closed behaviour. The framework must not contain real
receptionist utterances or inferred V9 expected values.

## Required tests

Use temporary directories, a temporary Git repository if needed, and opaque
placeholder scenarios. Cover at least:

- valid fixed-shape execution and product pass/fail taxonomy;
- every shape/count/coverage-cell rejection;
- unknown/missing schema field rejection;
- all canonical projection fields and tuple-to-array/null handling;
- contradictory Gold mutation, clarification, identity, temporal, authority,
  tool, delta, and simulated-write rejection before evaluator invocation;
- manifest hash, source commit, blob, evaluator path/source, seal, and attempt
  mismatch rejection;
- exclusive marker collision and marker persistence on every exit path;
- zero-variance and dimension-completeness enforcement; and
- aggregate-only report rejection of case IDs, utterances, Gold, per-case
  results, or other oracle content.

Run only the focused new test module plus the named ordinary taxonomy test if
one is imported directly. Repository pytest processes must remain serial.

## Forbidden surfaces

- all protected v1-v8 fixtures, evaluators, authoring/support modules,
  manifests, seals, receipts, tests, markers, and per-case evidence;
- actual V9 corpus text, evaluator, authoring module, thresholds, manifest,
  seal, marker, report, or one-shot execution;
- product parser, extractor, resolver, interpretation, replay, API, UI,
  database, deployment, provider, T3, historical-data, or write-authority code;
- `master`, `handoff/current`, origin refs, or GitHub publication.

## Durable candidate receipt

In the owned candidate receipt record:

- exact source head and final candidate commit;
- changed files;
- commands and exact test counts;
- any assumptions or unresolved risks;
- explicit confirmation that no forbidden path/content was accessed; and
- `DECISION: candidate_ready` or `DECISION: candidate_rejected`.

Self-certification is forbidden. GPT Sol will review and may reject or recover
the candidate under the recovery lease without a correction loop.
